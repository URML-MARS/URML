"""RFC-0667: evaluation semantics + a reference monitor for monitorable properties.

RFC-0382 gave the envelope a declarative temporal-logic core and a parser
(`urml_validator.monitorable`) and drew a boundary: URML does not run the
monitor. This module extends that boundary honestly. The *semantics* of the
core over finite timed traces become normative (this file is the executable
form; the spec text states the same rules in prose), and URML ships a
reference evaluator so a runtime can enforce an envelope without adopting an
external RV backend. Third-party backends (RTAMT, Reelay, Copilot,
MoonLight) remain first-class through `compile_to_stl`; using this evaluator
is optional.

Three surfaces:

- `evaluate_trace(node, trace)` — offline, exact: the completed-trace
  verdict of a property at trace start.
- `OnlineMonitor` — three-valued (`satisfied` / `violated` / `pending`)
  verdicts over a growing prefix, with `finalize()` collapsing pending
  verdicts under completed-trace semantics.
- `compile_envelope_monitors(envelope)` — every declared monitorable
  property plus the envelope's static numeric caps (max_velocity and
  friends) derived into implicit `always` properties, so one evaluator
  covers both.

## Trace model

A trace is a finite sequence of `Sample`s with strictly increasing
timestamps. A sample carries the ego robot's signal values plus the
`Entity` set the spatial (STREL) operators quantify over: each entity has a
distance from ego (meters) and its own signal map.

## Semantics (normative)

Boolean satisfaction of a property is judged at the first sample. Signals
are piecewise-constant: quantifiers range over the observed samples, and a
bounded operator's window `[a, b]` is measured in the trace's time unit
(seconds) relative to the sample under evaluation.

Completed traces (`evaluate_trace`): quantifiers range over observed
samples only. `eventually` (and the witness of `until`) requires an actual
observed witness: a bounded window that extends past the end of the trace
does not excuse a missing witness (strong semantics for existential
operators). `always` holds when no observed sample in the window violates
it (a truncated window cannot manufacture a violation).

Growing prefixes (`OnlineMonitor`): verdicts are three-valued in the
LTL3 style, computed by dual-mode evaluation. A property is `satisfied`
when even the pessimistic reading of the unobserved future cannot break it,
`violated` when even the optimistic reading cannot save it, `pending`
otherwise. Negation swaps the modes. A non-pending online verdict never
changes and always agrees with the completed-trace verdict.

Spatial operators (`somewhere` / `everywhere` / `surround`, dialect
`stl_strel`): evaluated per sample over the entity set. `somewhere[a,b] p`
holds when some entity at distance within `[a, b]` satisfies `p` with
signal lookups resolving against the entity's signals first, then ego's.
`everywhere[a,b] p` requires every such entity to satisfy `p` (vacuously
true when none). `p surround[a,b] q` is the simplified annulus form: ego
satisfies `p` and every entity in the `[a, b]` annulus satisfies `q` (the
full STREL reach/escape formulation is a declared follow-on). Temporal
operators inside a spatial operand are rejected: entity identity across
samples is not modeled in v1.

Missing signals are an error (`MonitorSignalError`), never silently false:
a safety monitor that shrugs at absent data is not a safety monitor. The
validator's static pass already checks that referenced signals resolve
against the manifest; the runtime must actually deliver them.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from itertools import pairwise
from typing import Any, Literal

from urml_validator.monitorable import (
    Binary,
    BoolOp,
    Compare,
    Const,
    Node,
    Not,
    Signal,
    Temporal,
    parse_property,
)

__all__ = [
    "CompiledProperty",
    "Entity",
    "MonitorError",
    "MonitorSemanticsError",
    "MonitorSignalError",
    "OnlineMonitor",
    "PropertyVerdict",
    "Sample",
    "Violation",
    "compile_envelope_monitors",
    "evaluate_trace",
]


class MonitorError(ValueError):
    """Base class for monitor evaluation errors."""


class MonitorSignalError(MonitorError):
    """A property referenced a signal the sample does not carry."""


class MonitorSemanticsError(MonitorError):
    """The property uses a construct the v1 semantics do not define."""


# ---------------------------------------------------------------------------
# Trace model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Entity:
    """One spatial entity in a sample: a distance from ego plus its own signals."""

    entity_id: str
    distance: float
    signals: Mapping[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class Sample:
    """One timestamped observation of the ego signals and the entity set."""

    t: float
    signals: Mapping[str, float] = field(default_factory=dict)
    entities: tuple[Entity, ...] = ()


def _check_trace(trace: Sequence[Sample]) -> None:
    if not trace:
        raise MonitorError("cannot evaluate an empty trace")
    for prev, cur in pairwise(trace):
        if cur.t <= prev.t:
            raise MonitorError(f"trace timestamps must strictly increase ({prev.t} then {cur.t})")


# ---------------------------------------------------------------------------
# Signal resolution
# ---------------------------------------------------------------------------


def _lookup(sample: Sample, name: str, entity: Entity | None) -> float:
    if entity is not None and name in entity.signals:
        return float(entity.signals[name])
    if name in sample.signals:
        return float(sample.signals[name])
    scope = f"entity {entity.entity_id!r} or ego" if entity is not None else "ego"
    raise MonitorSignalError(f"signal {name!r} is not present in the {scope} sample at t={sample.t}")


def _term_value(sample: Sample, term: str | float, entity: Entity | None) -> float:
    if isinstance(term, str):
        return _lookup(sample, term, entity)
    return float(term)


_COMPARE_OPS: dict[str, Callable[[float, float], bool]] = {
    "<=": lambda a, b: a <= b,
    ">=": lambda a, b: a >= b,
    "==": lambda a, b: a == b,
    "<": lambda a, b: a < b,
    ">": lambda a, b: a > b,
}


def _contains_temporal(node: Node) -> bool:
    if isinstance(node, Temporal) and node.op in ("always", "eventually"):
        return True
    if isinstance(node, Binary) and node.op == "until":
        return True
    if isinstance(node, Not):
        return _contains_temporal(node.operand)
    if isinstance(node, Temporal):
        return _contains_temporal(node.operand)
    if isinstance(node, (BoolOp, Binary)):
        return _contains_temporal(node.left) or _contains_temporal(node.right)
    return False


# ---------------------------------------------------------------------------
# Dual-mode evaluation
#
# `optimistic=True` reads the unobserved future as favorably as possible for
# the property; `optimistic=False` as unfavorably. `complete=True` means the
# trace is finished and there is no future to speculate about (completed-
# trace semantics). Negation flips the mode; `complete` is mode-independent.
# ---------------------------------------------------------------------------


def _in_window(t: float, origin: float, bound: tuple[float, float] | None) -> bool:
    if bound is None:
        return True
    return origin + bound[0] <= t <= origin + bound[1]


def _window_fully_observed(trace: Sequence[Sample], origin: float, bound: tuple[float, float] | None) -> bool:
    if bound is None:
        return False  # an unbounded window always extends past any finite prefix
    return trace[-1].t >= origin + bound[1]


def _eval(
    node: Node,
    trace: Sequence[Sample],
    i: int,
    *,
    optimistic: bool,
    complete: bool,
    entity: Entity | None,
) -> bool:
    sample = trace[i]

    if isinstance(node, Const):
        return node.value
    if isinstance(node, Signal):
        return _lookup(sample, node.name, entity) != 0.0
    if isinstance(node, Compare):
        left = _term_value(sample, node.left, entity)
        right = _term_value(sample, node.right, entity)
        return _COMPARE_OPS[node.op](left, right)
    if isinstance(node, Not):
        return not _eval(node.operand, trace, i, optimistic=not optimistic, complete=complete, entity=entity)
    if isinstance(node, BoolOp):
        if node.op == "and":
            return _eval(node.left, trace, i, optimistic=optimistic, complete=complete, entity=entity) and _eval(
                node.right, trace, i, optimistic=optimistic, complete=complete, entity=entity
            )
        if node.op == "or":
            return _eval(node.left, trace, i, optimistic=optimistic, complete=complete, entity=entity) or _eval(
                node.right, trace, i, optimistic=optimistic, complete=complete, entity=entity
            )
        # implies == (not left) or right; the antecedent evaluates in the flipped mode.
        return not _eval(
            node.left, trace, i, optimistic=not optimistic, complete=complete, entity=entity
        ) or _eval(node.right, trace, i, optimistic=optimistic, complete=complete, entity=entity)

    if isinstance(node, Temporal):
        if node.op in ("somewhere", "everywhere"):
            return _eval_spatial_quantifier(node, trace, i, optimistic=optimistic, complete=complete)
        origin = sample.t
        if node.op == "always":
            for j in range(i, len(trace)):
                if not _in_window(trace[j].t, origin, node.bound):
                    if node.bound is not None and trace[j].t > origin + node.bound[1]:
                        break
                    continue
                if not _eval(node.operand, trace, j, optimistic=optimistic, complete=complete, entity=entity):
                    return False
            if complete or _window_fully_observed(trace, origin, node.bound):
                return True
            return optimistic
        if node.op == "eventually":
            for j in range(i, len(trace)):
                if not _in_window(trace[j].t, origin, node.bound):
                    if node.bound is not None and trace[j].t > origin + node.bound[1]:
                        break
                    continue
                if _eval(node.operand, trace, j, optimistic=optimistic, complete=complete, entity=entity):
                    return True
            if complete or _window_fully_observed(trace, origin, node.bound):
                return False
            return optimistic
        raise MonitorSemanticsError(f"unknown temporal operator {node.op!r}")

    if isinstance(node, Binary):
        if node.op == "surround":
            return _eval_surround(node, trace, i, optimistic=optimistic, complete=complete)
        # until: a witness of the right side inside the window, with the left
        # side holding at every sample from i up to (not including) the witness.
        origin = sample.t
        for j in range(i, len(trace)):
            past_window = node.bound is not None and trace[j].t > origin + node.bound[1]
            if past_window:
                break
            if _in_window(trace[j].t, origin, node.bound) and _eval(
                node.right, trace, j, optimistic=optimistic, complete=complete, entity=entity
            ):
                return True
            if not _eval(node.left, trace, j, optimistic=optimistic, complete=complete, entity=entity):
                return False
        if complete or _window_fully_observed(trace, origin, node.bound):
            return False
        return optimistic

    raise MonitorSemanticsError(f"unknown node type {type(node).__name__}")


def _entities_in_band(sample: Sample, bound: tuple[float, float] | None) -> Iterable[Entity]:
    for entity in sample.entities:
        if bound is None or bound[0] <= entity.distance <= bound[1]:
            yield entity


def _eval_spatial_quantifier(
    node: Temporal,
    trace: Sequence[Sample],
    i: int,
    *,
    optimistic: bool,
    complete: bool,
) -> bool:
    if _contains_temporal(node.operand):
        raise MonitorSemanticsError(
            f"temporal operators inside {node.op!r} are not defined in v1 "
            "(entity identity across samples is not modeled)"
        )
    matches = [
        _eval(node.operand, trace, i, optimistic=optimistic, complete=complete, entity=entity)
        for entity in _entities_in_band(trace[i], node.bound)
    ]
    if node.op == "somewhere":
        return any(matches)
    return all(matches)  # everywhere: vacuously true with no entity in band


def _eval_surround(
    node: Binary,
    trace: Sequence[Sample],
    i: int,
    *,
    optimistic: bool,
    complete: bool,
) -> bool:
    if _contains_temporal(node.left) or _contains_temporal(node.right):
        raise MonitorSemanticsError(
            "temporal operators inside 'surround' are not defined in v1 "
            "(entity identity across samples is not modeled)"
        )
    ego_ok = _eval(node.left, trace, i, optimistic=optimistic, complete=complete, entity=None)
    if not ego_ok:
        return False
    return all(
        _eval(node.right, trace, i, optimistic=optimistic, complete=complete, entity=entity)
        for entity in _entities_in_band(trace[i], node.bound)
    )


def evaluate_trace(node: Node, trace: Sequence[Sample]) -> bool:
    """The completed-trace verdict of a property, judged at the first sample."""
    _check_trace(trace)
    return _eval(node, trace, 0, optimistic=False, complete=True, entity=None)


# ---------------------------------------------------------------------------
# Envelope compilation
# ---------------------------------------------------------------------------

Severity = Literal["info", "warning", "critical"]

#: envelope numeric cap -> the runtime signal it constrains (RFC-0382 built-ins).
_STATIC_CAP_SIGNALS: dict[str, str] = {
    "max_velocity": "speed",
    "max_altitude": "altitude",
    "max_payload": "payload",
    "max_grip_force_n": "grip_force",
}


@dataclass(frozen=True)
class CompiledProperty:
    """One monitor-ready property: parsed AST plus its enforcement metadata."""

    name: str
    severity: Severity
    node: Node
    expression: str
    source: Literal["declared", "derived"]


def compile_envelope_monitors(envelope: Mapping[str, Any] | None) -> list[CompiledProperty]:
    """Compile an envelope's monitorable properties plus its static caps.

    Declared `monitorable_properties` parse with their stated dialect;
    `dialect: custom` entries are skipped (URML cannot evaluate a grammar it
    does not define — a custom expression belongs to an external backend).
    Static numeric caps derive into implicit `always` properties at
    `critical` severity: they are hard limits the validator already enforces
    statically, and the monitor's job is to keep them true in motion.
    """
    if envelope is None:
        return []
    compiled: list[CompiledProperty] = []
    for cap, signal in _STATIC_CAP_SIGNALS.items():
        limit = envelope.get(cap)
        if limit is None:
            continue
        expression = f"always ({signal} <= {float(limit):g})"
        compiled.append(
            CompiledProperty(
                name=f"envelope.{cap}",
                severity="critical",
                node=parse_property(expression, dialect="stl"),
                expression=expression,
                source="derived",
            )
        )
    for raw in envelope.get("monitorable_properties", []) or []:
        dialect = raw.get("dialect", "stl")
        if dialect == "custom":
            continue
        expression = raw["expression"]
        compiled.append(
            CompiledProperty(
                name=str(raw["name"]),
                severity=raw.get("severity", "warning"),
                node=parse_property(expression, dialect=dialect),
                expression=expression,
                source="declared",
            )
        )
    return compiled


# ---------------------------------------------------------------------------
# Online monitor
# ---------------------------------------------------------------------------

VerdictState = Literal["satisfied", "violated", "pending"]


@dataclass(frozen=True)
class PropertyVerdict:
    """The current three-valued verdict of one property."""

    name: str
    severity: Severity
    state: VerdictState
    at_time: float | None = None


@dataclass(frozen=True)
class Violation:
    """A property that reached the `violated` verdict."""

    name: str
    severity: Severity
    expression: str
    at_time: float


class OnlineMonitor:
    """Three-valued monitoring of compiled properties over a growing prefix.

    The reference implementation re-evaluates each still-pending property on
    the full prefix after every sample: correctness over performance, and
    the per-sample cost is bounded by trace length times property size.
    Incremental monitoring is exactly what the RFC-0382 backend ecosystem
    (RTAMT, Reelay) exists for; this class is the semantics, not the
    fastest implementation of them.

    A non-pending verdict is final: once a property is `satisfied` or
    `violated` no future sample changes it, and `finalize()` only collapses
    the still-pending verdicts under completed-trace semantics.
    """

    def __init__(self, properties: Sequence[CompiledProperty]) -> None:
        self._properties = list(properties)
        self._trace: list[Sample] = []
        self._states: dict[str, PropertyVerdict] = {
            p.name: PropertyVerdict(name=p.name, severity=p.severity, state="pending") for p in self._properties
        }
        self._finalized = False

    @property
    def trace(self) -> tuple[Sample, ...]:
        return tuple(self._trace)

    def observe(self, sample: Sample) -> tuple[PropertyVerdict, ...]:
        """Append a sample and return the refreshed verdict for every property."""
        if self._finalized:
            raise MonitorError("cannot observe after finalize()")
        if self._trace and sample.t <= self._trace[-1].t:
            raise MonitorError(
                f"sample timestamps must strictly increase ({self._trace[-1].t} then {sample.t})"
            )
        self._trace.append(sample)
        for prop in self._properties:
            if self._states[prop.name].state != "pending":
                continue
            pessimistic = _eval(prop.node, self._trace, 0, optimistic=False, complete=False, entity=None)
            if pessimistic:
                self._states[prop.name] = PropertyVerdict(
                    name=prop.name, severity=prop.severity, state="satisfied", at_time=sample.t
                )
                continue
            optimistic = _eval(prop.node, self._trace, 0, optimistic=True, complete=False, entity=None)
            if not optimistic:
                self._states[prop.name] = PropertyVerdict(
                    name=prop.name, severity=prop.severity, state="violated", at_time=sample.t
                )
        return self.verdicts()

    def finalize(self) -> tuple[PropertyVerdict, ...]:
        """Collapse pending verdicts under completed-trace semantics."""
        if not self._trace:
            raise MonitorError("cannot finalize an empty trace")
        if not self._finalized:
            self._finalized = True
            for prop in self._properties:
                if self._states[prop.name].state != "pending":
                    continue
                verdict = evaluate_trace(prop.node, self._trace)
                self._states[prop.name] = PropertyVerdict(
                    name=prop.name,
                    severity=prop.severity,
                    state="satisfied" if verdict else "violated",
                    at_time=self._trace[-1].t,
                )
        return self.verdicts()

    def verdicts(self) -> tuple[PropertyVerdict, ...]:
        return tuple(self._states[p.name] for p in self._properties)

    def violations(self) -> list[Violation]:
        """Every property currently in the `violated` state."""
        by_name = {p.name: p for p in self._properties}
        return [
            Violation(
                name=v.name,
                severity=v.severity,
                expression=by_name[v.name].expression,
                at_time=v.at_time if v.at_time is not None else (self._trace[-1].t if self._trace else 0.0),
            )
            for v in self._states.values()
            if v.state == "violated"
        ]
