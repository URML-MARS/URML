"""The rulebook pass (RFC-0702, Draft).

A rulebook states what law or an organization allows a robot to do. This
module judges a program against the rulebooks that apply to it. The
normative text is ``spec/layer-1-hal/rulebook.md``; the file format is
``schemas/rulebook.py``.

Position: the pass runs after the safety-envelope pass (Pass 3) and before
the variable-binding pass (Pass 4), whenever Pass 1 succeeds. It does not
depend on the compliance policy: ``policy=None`` and ``--no-policy`` never
skip it.

Loading: the bundled rulebooks (``urml_validator/rulebooks/*.yaml``, sorted by
file name, unless ``default_rulebooks=False``), then the caller's rulebooks in
order. A file that breaks the format, or repeats a loaded ``rulebook_id``, is
reported as ``rule.rulebook_invalid`` and not applied.

Judging: rulebooks in load order, rules in document order, steps in
execution order, one issue per (rule, step, zone or value). Rules only
restrict. The only narrowing is a deployment rulebook's declaration or its
recorded exception, and an exception turns a covered violation into a
warning with the same code.

Zone rules fail closed: a rule that must judge a step against a zone it
resolved, and cannot place the step, refuses it with ``rule.place_unknown``.

A program passing a rulebook is not a legal compliance determination. The
pass checks the statically checkable subset of the rules a rulebook encodes;
obligations are listed in the report and never checked.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from collections.abc import Sequence as SequenceABC
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from functools import lru_cache
from importlib import resources
from typing import Any, Literal

import yaml
from pydantic import ValidationError as PydanticValidationError

from urml_validator.errors import ErrorCode, RulebookReport, ValidationError
from urml_validator.schemas.common import Speed
from urml_validator.schemas.composition import Barrier, Branch, OnMember, Parallel, Retry, Step
from urml_validator.schemas.composition import Sequence as SequenceNode
from urml_validator.schemas.envelope import SafetyEnvelope
from urml_validator.schemas.manifest import CapabilityManifest, Frame
from urml_validator.schemas.primitives import GraspArgs
from urml_validator.schemas.program import URMLProgram
from urml_validator.schemas.rulebook import Cite, Condition, Issuer, Rule, RuleException, Rulebook
from urml_validator.transforms import transform_point_between
from urml_validator.validator import _AERIAL_DRIVE_TYPES, _resolve_force, _segments_intersect

#: The package the bundled rulebooks ship in, as package data.
BUNDLED_PACKAGE = "urml_validator.rulebooks"

#: Codes whose fix is in the deployment, not the program.
_FIX_DEPLOYMENT = frozenset({ErrorCode.RULE_DECLARATION_MISSING, ErrorCode.RULE_RULEBOOK_INVALID})

_UNITS: dict[str, str] = {"altitude_agl_m": "m", "speed_m_per_s": "m/s", "grip_force_n": "N"}

#: Steps that end at a place the validator cannot see.
_RELATIVE = frozenset({"drive", "turn", "follow_trajectory", "call_program"})

#: Steps that change the robot's place (they have a target, or move relatively).
_MOVING = frozenset(
    {
        "move_to",
        "pick_from",
        "place_at",
        "dock",
        "swap_tool",
        "return_to_home",
        "scan",
        *_RELATIVE,
    }
)

#: The flight steps that decide whether an aircraft is airborne at the start.
_FLIGHT_STEPS = frozenset(
    {"take_off", "move_to", "hover", "scan", "land", "return_to_home", "follow_trajectory"}
)

#: Named-place altitudes the cap judges (land.at and swap_tool.at are not judged).
_ALTITUDE_PLACE_STEPS = frozenset({"move_to", "hover", "pick_from", "place_at", "dock"})

_NOT_KNOWN = "the robot's place is not known at this step"


# ---------------------------------------------------------------------------
# Public result
# ---------------------------------------------------------------------------


@dataclass
class RulebookPassResult:
    """What the rulebook pass adds to a validation result."""

    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)
    reports: list[RulebookReport] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _Source:
    """One rulebook as loaded: the parsed model, or the problems that stopped it."""

    label: str
    bundled: bool
    book: Rulebook | None
    problems: tuple[str, ...] = ()
    raw_id: str | None = None


def _loc(parts: tuple[int | str, ...]) -> str:
    text = ""
    for part in parts:
        if isinstance(part, int):
            text += f"[{part}]"
        else:
            text += ("." if text else "") + str(part)
    return text


def _problems(exc: PydanticValidationError) -> tuple[str, ...]:
    out: list[str] = []
    for err in exc.errors():
        msg = str(err.get("msg", "invalid"))
        if msg.startswith("Value error, "):
            msg = msg[len("Value error, ") :]
        loc = _loc(tuple(err.get("loc", ())))
        entry = f"{loc}: {msg}" if loc else msg
        if entry not in out:
            out.append(entry)
    return tuple(out)


def _parse(data: object, *, label: str | None, bundled: bool) -> _Source:
    """Validate one rulebook; never raises."""
    if isinstance(data, Rulebook):
        return _Source(label or data.rulebook_id, bundled, data, (), data.rulebook_id)
    raw_id = None
    if isinstance(data, Mapping) and isinstance(data.get("rulebook_id"), str):
        raw_id = str(data["rulebook_id"])
    name = label or raw_id or "rulebook"
    if not isinstance(data, Mapping):
        return _Source(name, bundled, None, ("a rulebook is a YAML mapping",), raw_id)
    try:
        book = Rulebook.model_validate(dict(data))
    except PydanticValidationError as exc:
        return _Source(name, bundled, None, _problems(exc), raw_id)
    return _Source(name, bundled, book, (), book.rulebook_id)


@lru_cache(maxsize=1)
def _bundled_sources() -> tuple[_Source, ...]:
    """The bundled rulebooks, sorted by file name, parsed once per process."""
    root = resources.files(BUNDLED_PACKAGE)
    names = sorted(entry.name for entry in root.iterdir() if entry.name.endswith(".yaml"))
    out: list[_Source] = []
    for name in names:
        try:
            data = yaml.safe_load(root.joinpath(name).read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            out.append(_Source(name, True, None, (f"YAML parse error: {exc}",)))
            continue
        out.append(_parse(data, label=name, bundled=True))
    return tuple(out)


def bundled_rulebooks() -> list[Rulebook]:
    """The bundled rulebooks that parse, in load order."""
    return [src.book for src in _bundled_sources() if src.book is not None]


# ---------------------------------------------------------------------------
# Places, targets and zones
# ---------------------------------------------------------------------------


@dataclass(frozen=True, eq=False)
class _Robot:
    """The robot that executes a step: its manifest, envelope and frame graph."""

    key: str | None
    manifest: CapabilityManifest
    envelope: SafetyEnvelope | None
    frames: Mapping[str, Frame]

    @property
    def aircraft(self) -> bool:
        mobility = self.manifest.mobility
        return mobility is not None and mobility.drive_type in _AERIAL_DRIVE_TYPES


@dataclass(frozen=True)
class _Place:
    """A resolved place: a point (location, station, pose) or an area.

    ``frame`` is None for a scan polygon or bounding box, which has no frame
    of its own and is read in the zone's frame. ``label`` is how messages name
    the place and does not take part in equality.
    """

    kind: Literal["point", "area"]
    frame: str | None
    vertices: tuple[tuple[float, float], ...]
    z: float | None = None
    label: str = field(default="", compare=False)


@dataclass(frozen=True)
class _Target:
    """A place a step sends the robot to.

    ``place`` is None for a ``$reference`` (``ref``) or a name that does not
    resolve; ``named`` marks a declared place (not a pose or a scan area).
    """

    field: str
    label: str
    place: _Place | None
    named: bool = False
    ref: bool = False

    @property
    def unknown_reason(self) -> str:
        if self.ref:
            return f"its target {self.label} is a runtime binding"
        return f"its target {self.label} does not name a declared place"


@dataclass(frozen=True)
class _StepInfo:
    path: tuple[str, ...]
    step: Step
    robot: _Robot
    place_before: _Place | None
    targets: tuple[_Target, ...]


@dataclass(frozen=True)
class _Zone:
    name: str
    frame: str
    polygon: tuple[tuple[float, float], ...]
    source: str
    allow_override: bool = False


@dataclass(frozen=True)
class _Value:
    """One value a cap rule judges."""

    what: str
    field: str
    amount: float
    path_suffix: tuple[str, ...] = ()
    named_place: bool = False


def _named_place(name: str, manifest: CapabilityManifest) -> _Place | None:
    """A declared location, else a declared area (a location wins, as in Pass 2)."""
    for loc in manifest.declared_locations:
        if loc.name == name:
            z = float(loc.pose.z) if loc.pose.z is not None else None
            return _Place(
                "point", loc.frame, ((float(loc.pose.x), float(loc.pose.y)),), z,
                f"declared location {name!r}",
            )
    for area in manifest.declared_areas:
        if area.name == name:
            vertices = tuple((float(p.x), float(p.y)) for p in area.polygon)
            return _Place("area", area.frame, vertices, None, f"declared area {name!r}")
    return None


def _station(name: str, manifest: CapabilityManifest) -> _Place | None:
    for station in manifest.docking_stations:
        if station.name == name:
            z = float(station.pose.z) if station.pose.z is not None else None
            return _Place(
                "point", station.frame, ((float(station.pose.x), float(station.pose.y)),), z,
                f"docking station {name!r}",
            )
    return None


def _named_target(primitive: str, field_name: str, name: str, manifest: CapabilityManifest) -> _Target:
    return _Target(field_name, f"{primitive}.{field_name} {name!r}", _named_place(name, manifest), named=True)


def _scan_target(args: Any, manifest: CapabilityManifest) -> _Target:
    area = args.area
    if area.named_region is not None:
        region = area.named_region
        place = next(
            (
                _Place(
                    "area", a.frame, tuple((float(p.x), float(p.y)) for p in a.polygon), None,
                    f"declared area {region!r}",
                )
                for a in manifest.declared_areas
                if a.name == region
            ),
            None,
        )
        return _Target("area", f"scan.area.named_region {region!r}", place, named=True)
    if area.bounding_box is not None:
        box = area.bounding_box
        if all(key in box for key in ("min_x", "max_x", "min_y", "max_y")):
            corners = (
                (float(box["min_x"]), float(box["min_y"])),
                (float(box["max_x"]), float(box["min_y"])),
                (float(box["max_x"]), float(box["max_y"])),
                (float(box["min_x"]), float(box["max_y"])),
            )
            return _Target("area", "scan.area.bounding_box", _Place("area", None, corners, None, "the scan area"))
        return _Target("area", "scan.area.bounding_box", None)
    points = tuple((float(p.x), float(p.y)) for p in (area.polygon or []))
    if not points:
        return _Target("area", "scan.area.polygon", None)
    return _Target("area", "scan.area.polygon", _Place("area", None, points, None, "the scan area"))


def _targets(step: Step, robot: _Robot) -> tuple[_Target, ...]:
    """The places a step sends the robot to (spec, *Targets*)."""
    name = step.primitive_name
    args = getattr(step, name)
    manifest = robot.manifest
    if name == "move_to":
        if args.pose is not None and args.frame is not None:
            x, y = float(args.pose.x), float(args.pose.y)
            z = float(args.pose.z) if args.pose.z is not None else None
            where = f"({x:g}, {y:g}) in frame {args.frame!r}"
            place = _Place("point", args.frame, ((x, y),), z, f"pose {where}")
            return (_Target("pose", f"move_to.pose {where}", place),)
        if args.location is not None:
            return (_named_target("move_to", "location", args.location, manifest),)
        return ()
    if name == "pick_from":
        return (_named_target("pick_from", "source", args.source, manifest),)
    if name == "place_at":
        return (_named_target("place_at", "target", args.target, manifest),)
    if name == "dock":
        station = args.at
        if station is None and manifest.docking_stations:
            station = manifest.docking_stations[0].name
        if station is None:
            return (_Target("at", "dock.at (no station declared)", None),)
        return (_Target("at", f"dock.at {station!r}", _station(station, manifest), named=True),)
    if name == "swap_tool":
        return (_Target("at", f"swap_tool.at {args.at!r}", _station(args.at, manifest), named=True),)
    if name == "hover" and args.over is not None:
        if args.over.startswith("$"):
            return (_Target("over", f"hover.over {args.over}", None, ref=True),)
        return (_named_target("hover", "over", args.over, manifest),)
    if name == "land" and args.at is not None:
        return (_named_target("land", "at", args.at, manifest),)
    if name == "return_to_home":
        home = next((loc for loc in manifest.declared_locations if loc.name == "home"), None)
        home_place: _Place | None = None
        if home is not None:
            home_z = float(home.pose.z) if home.pose.z is not None else None
            home_place = _Place(
                "point", home.frame, ((float(home.pose.x), float(home.pose.y)),), home_z,
                "declared location 'home'",
            )
        return (_Target("home", "return_to_home 'home'", home_place, named=True),)
    if name == "scan":
        return (_scan_target(args, manifest),)
    return ()


def _moves(step: Step) -> bool:
    """Whether a step changes the robot's current place."""
    name = step.primitive_name
    if name in _MOVING:
        return True
    args = getattr(step, name)
    return (name == "hover" and args.over is not None) or (name == "land" and args.at is not None)


def _place_after(step: Step, targets: tuple[_Target, ...], before: _Place | None) -> _Place | None:
    """The current place after a step (spec, *Where a step happens*)."""
    if step.primitive_name in _RELATIVE:
        return None
    if not _moves(step):
        return before
    if len(targets) == 1 and targets[0].place is not None:
        return targets[0].place
    return None


def _resolve_zone(name: str, robot: _Robot) -> _Zone | None:
    """Declared areas, then people-occupancy zones, then geofences (spec, *Zones*)."""
    for area in robot.manifest.declared_areas:
        if area.name == name:
            return _Zone(name, area.frame, tuple((float(p.x), float(p.y)) for p in area.polygon), "declared area")
    envelope = robot.envelope
    if envelope is not None:
        for zone in envelope.people_occupancy_zones:
            if zone.name == name:
                return _Zone(
                    name, zone.frame, tuple((float(x), float(y)) for x, y in zone.vertices),
                    "people-occupancy zone", zone.allow_override,
                )
        for fence in envelope.geofences:
            if fence.name == name:
                return _Zone(name, fence.frame, tuple((float(x), float(y)) for x, y in fence.vertices), "geofence")
    return None


def _on_segment(p: tuple[float, float], a: tuple[float, float], b: tuple[float, float]) -> bool:
    eps = 1e-9
    cross = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
    if abs(cross) > eps * max(1.0, abs(b[0] - a[0]) + abs(b[1] - a[1])):
        return False
    return (
        min(a[0], b[0]) - eps <= p[0] <= max(a[0], b[0]) + eps
        and min(a[1], b[1]) - eps <= p[1] <= max(a[1], b[1]) + eps
    )


def _point_in_zone(p: tuple[float, float], polygon: tuple[tuple[float, float], ...]) -> bool:
    """Point in polygon; the boundary counts as inside."""
    n = len(polygon)
    for i in range(n):
        if _on_segment(p, polygon[i], polygon[(i + 1) % n]):
            return True
    x, y = p
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def _share_point(a: tuple[tuple[float, float], ...], b: tuple[tuple[float, float], ...]) -> bool:
    """True when two polygons (closed sets) share any point."""
    if any(_point_in_zone(p, b) for p in a) or any(_point_in_zone(p, a) for p in b):
        return True
    for i in range(len(a)):
        p1, p2 = a[i], a[(i + 1) % len(a)]
        for j in range(len(b)):
            if _segments_intersect(p1, p2, b[j], b[(j + 1) % len(b)]):
                return True
    return False


def _place_in_zone(place: _Place, zone: _Zone, frames: Mapping[str, Frame]) -> bool | None:
    """Whether a place lies in (a point) or overlaps (an area) a zone.

    None when the place cannot be expressed in the zone's frame (RFC-0290).
    """
    vertices = place.vertices
    if place.frame is not None and place.frame != zone.frame:
        moved: list[tuple[float, float]] = []
        z = place.z if place.z is not None else 0.0
        for x, y in vertices:
            resolved = transform_point_between((x, y, z), place.frame, zone.frame, frames)
            if resolved is None:
                return None
            moved.append((resolved[0], resolved[1]))
        vertices = tuple(moved)
    if place.kind == "point":
        return _point_in_zone(vertices[0], zone.polygon)
    return _share_point(vertices, zone.polygon)


def _uses(step: Step) -> list[tuple[str, str | None]]:
    """Every primitive a step uses, directly first, then through composition."""
    name = step.primitive_name
    args = getattr(step, name)
    own_name: str | None = None
    if name in ("call_program", "gesture"):
        own_name = args.name
    elif name == "set_output":
        own_name = args.output
    out: list[tuple[str, str | None]] = [(name, own_name)]
    if name == "pick_from":
        out += [("move_to", None), ("detect", None), ("grasp", None)]
    elif name == "place_at":
        out += [("move_to", None), ("release", None)]
    elif name == "bimanual":
        for side in (args.left, args.right):
            out.append(("grasp" if isinstance(side, GraspArgs) else "release", None))
    elif name == "scan" and args.media in ("photo", "video"):
        out.append(("capture", None))
    elif name == "listen" and args.prompt:
        out.append(("speak", None))
    return out


def _speed_value(speed: Any, max_velocity: float | None, label: str) -> _Value | None:
    if speed is None:
        return None
    if isinstance(speed, Speed):
        if speed.units == "fraction":
            if max_velocity is None:
                return None  # Pass 2 refuses a fraction with no mobility block
            fraction = float(speed.value)
            return _Value(
                f"{label} (fraction {_fmt(fraction)} of the manifest maximum {_fmt(max_velocity)} m/s)",
                "speed",
                fraction * max_velocity,
            )
        return _Value(label, "speed", float(speed.value))
    return _Value(label, "speed", float(speed))


def _cap_values(info: _StepInfo, quantity: str) -> list[_Value]:
    """The values of one step a cap on `quantity` judges (spec, *cap*)."""
    step = info.step
    name = step.primitive_name
    args = getattr(step, name)
    out: list[_Value] = []
    if quantity == "altitude_agl_m":
        if name == "take_off":
            out.append(_Value("take_off.altitude", "altitude", float(args.altitude)))
        elif name in ("return_to_home", "scan") and args.altitude is not None:
            out.append(_Value(f"{name}.altitude", "altitude", float(args.altitude)))
        elif name == "move_to" and args.pose is not None and args.pose.z is not None:
            out.append(_Value("move_to.pose.z", "pose.z", float(args.pose.z)))
        if name in _ALTITUDE_PLACE_STEPS:
            for target in info.targets:
                place = target.place
                if target.named and place is not None and place.kind == "point" and place.z is not None:
                    out.append(_Value(f"{target.label} altitude", target.field, place.z, named_place=True))
    elif quantity == "speed_m_per_s":
        mobility = info.robot.manifest.mobility
        max_velocity = mobility.max_velocity if mobility is not None else None
        value: _Value | None = None
        if name in ("move_to", "drive"):
            value = _speed_value(args.speed, max_velocity, f"{name}.speed")
        elif name == "return_to_home" and args.speed is not None:
            value = _Value("return_to_home.speed", "speed", float(args.speed))
        elif name == "follow_trajectory":
            envelope = args.speed_envelope
            if envelope is not None and envelope.max_velocity_mps is not None:
                value = _Value(
                    "follow_trajectory.speed_envelope.max_velocity_mps",
                    "speed_envelope",
                    float(envelope.max_velocity_mps),
                )
        if value is not None:
            out.append(value)
    elif quantity == "grip_force_n":
        if name in ("grasp", "pick_from"):
            force = _resolve_force(args.force)
            if force is not None:
                out.append(_Value(f"{name}.force", "force", force))
        elif name == "bimanual":
            for side in ("left", "right"):
                sub = getattr(args, side)
                if isinstance(sub, GraspArgs):
                    force = _resolve_force(sub.force)
                    if force is not None:
                        out.append(_Value(f"bimanual.{side}.force", "force", force, (side,)))
    return out


# ---------------------------------------------------------------------------
# Small formatting helpers
# ---------------------------------------------------------------------------


def _fmt(value: object) -> str:
    """A value as a message shows it: YAML booleans, short floats."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return f"{value:.10g}"
    return str(value)


def _same(a: object, b: object) -> bool:
    """Type-strict equality for declaration values: a boolean is not an integer."""
    return type(a) is type(b) and a == b


def _phrase(title: str) -> str:
    """A rule title as the middle of a sentence."""
    text = title.strip().rstrip(".")
    if len(text) > 1 and text[0].isupper() and text[1].islower():
        return text[0].lower() + text[1:]
    return text


def _cite_dict(cite: Cite | None) -> dict[str, str | None] | None:
    return None if cite is None else {"text": cite.text, "url": cite.url}


def _issuer_dict(issuer: Issuer) -> dict[str, str | None]:
    return {"kind": issuer.kind, "name": issuer.name, "jurisdiction": issuer.jurisdiction}


def _plural(count: int, word: str) -> str:
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


def _report(book: Rulebook, *, bundled: bool, applied: bool, reason: str | None) -> RulebookReport:
    deployment = book.issuer.kind == "deployment"
    return RulebookReport(
        rulebook_id=book.rulebook_id,
        title=book.title,
        issuer=_issuer_dict(book.issuer),
        source_status=book.source_status,
        effective=book.effective,
        reviewed=book.reviewed,
        bundled=bundled,
        applied=applied,
        reason=reason,
        obligations=(
            [
                {"id": o.id, "title": o.title, "text": o.text, "cite": _cite_dict(o.cite)}
                for o in book.obligations
            ]
            if applied
            else []
        ),
        declarations=dict(book.declarations or {}) if deployment else None,
        exceptions=(
            [
                {"rule": e.rule, "basis": e.basis, "limit": e.limit, "expires": e.expires}
                for e in book.exceptions or []
            ]
            if deployment
            else None
        ),
    )


# ---------------------------------------------------------------------------
# The pass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _Exception:
    """An exception that passed the set checks, with its deployment rulebook."""

    deployment_id: str
    exception: RuleException


class _RulebookPass:
    def __init__(
        self,
        program: URMLProgram,
        robots: Mapping[str | None, _Robot],
        *,
        fleet: bool,
        sole_member: str | None,
        profiles: SequenceABC[str],
        as_of: date,
    ) -> None:
        self.program = program
        self.robots = robots
        self.fleet = fleet
        self.sole_member = sole_member
        self.as_of = as_of
        active = [*program.profiles, *profiles]
        self.profiles = list(dict.fromkeys(active))
        self.drive_types = {
            r.manifest.mobility.drive_type for r in robots.values() if r.manifest.mobility is not None
        }
        self.result = RulebookPassResult()
        self.declarations: dict[str, str | int | bool] = {}
        self.deployments: list[Rulebook] = []
        self.exceptions: dict[tuple[str, str], _Exception] = {}
        self._seen: set[tuple[object, ...]] = set()
        self._infos: list[_StepInfo] | None = None
        self._air: tuple[int, frozenset[str]] | None = None

    # ----- entry point -----

    def run(self, rulebooks: SequenceABC[Mapping[str, Any] | Rulebook], default_rulebooks: bool) -> RulebookPassResult:
        bundled = list(_bundled_sources())
        caller = [
            _parse(data, label=None if isinstance(data, Rulebook) else self._caller_label(data, i), bundled=False)
            for i, data in enumerate(rulebooks)
        ]
        loaded = self._load([*bundled, *caller] if default_rulebooks else caller)
        self._deployment_data(loaded)

        applied: list[Rulebook] = []
        for src in loaded:
            book = src.book
            assert book is not None
            if book.issuer.kind == "deployment":
                self.result.reports.append(_report(book, bundled=src.bundled, applied=True, reason=None))
                continue
            if not self._in_scope(book):
                continue
            switch = self._holding(book.applies_to.unless_declared if book.applies_to else None)
            reason = None if switch is None else self._switch_reason(switch)
            self.result.reports.append(_report(book, bundled=src.bundled, applied=switch is None, reason=reason))
            if switch is None:
                applied.append(book)

        if not default_rulebooks:
            loaded_ids = {src.book.rulebook_id for src in loaded if src.book is not None}
            for src in bundled:
                if src.book is not None and src.book.rulebook_id not in loaded_ids and self._in_scope(src.book):
                    self._defaults_disabled(src.book)

        for book in applied:
            for rule in book.rules:
                judge = getattr(self, f"_judge_{rule.kind}")
                judge(book, rule)
        return self.result

    @staticmethod
    def _caller_label(data: object, index: int) -> str:
        if isinstance(data, Mapping) and isinstance(data.get("rulebook_id"), str):
            return str(data["rulebook_id"])
        return f"rulebooks[{index}]"

    # ----- loading and the set checks -----

    def _load(self, sources: list[_Source]) -> list[_Source]:
        loaded: list[_Source] = []
        for src in sources:
            if src.book is None:
                problems = list(src.problems)
                self._invalid(
                    rulebook_id=src.raw_id,
                    issuer=None,
                    source=src.label,
                    problems=problems,
                    message=(
                        f"rulebook {src.label} does not follow the rulebook format and was not "
                        f"applied: {'; '.join(problems)}."
                    ),
                )
                continue
            book = src.book
            if any(done.book is not None and done.book.rulebook_id == book.rulebook_id for done in loaded):
                self._invalid(
                    rulebook_id=book.rulebook_id,
                    issuer=book.issuer,
                    source=src.label,
                    problems=[f"rulebook_id {book.rulebook_id} is already loaded"],
                    message=(
                        f"rulebook {book.rulebook_id} is loaded twice; the later copy was not "
                        "applied. To replace a bundled rulebook, switch the bundled rulebooks "
                        "off and load your own copy."
                    ),
                )
                continue
            loaded.append(src)
        return loaded

    def _deployment_data(self, loaded: list[_Source]) -> None:
        """Merge declarations and check exceptions across the deployment rulebooks."""
        self.deployments = [
            src.book for src in loaded if src.book is not None and src.book.issuer.kind == "deployment"
        ]
        declared_by: dict[str, str] = {}
        conflicted: set[str] = set()
        for book in self.deployments:
            for key, value in (book.declarations or {}).items():
                if key in conflicted:
                    continue
                if key not in self.declarations:
                    self.declarations[key] = value
                    declared_by[key] = book.rulebook_id
                elif not _same(self.declarations[key], value):
                    first = self.declarations.pop(key)
                    conflicted.add(key)
                    problem = (
                        f"deployment rulebooks {declared_by[key]} and {book.rulebook_id} declare "
                        f"{key} with different values ({_fmt(first)} and {_fmt(value)}); "
                        "neither value is used"
                    )
                    self._invalid(
                        rulebook_id=book.rulebook_id,
                        issuer=book.issuer,
                        source=book.rulebook_id,
                        problems=[problem],
                        message=f"{problem}.",
                    )

        books = {src.book.rulebook_id: src.book for src in loaded if src.book is not None}
        found: dict[tuple[str, str], list[_Exception]] = {}
        for book in self.deployments:
            for exc in book.exceptions or []:
                target = books.get(exc.rulebook_id)
                if target is None:
                    continue  # the rulebook is not loaded: the exception is inert
                mismatch = self._exception_problem(target, exc)
                if mismatch is not None:
                    self._invalid(
                        rulebook_id=book.rulebook_id,
                        issuer=book.issuer,
                        source=book.rulebook_id,
                        problems=[mismatch],
                        message=f"deployment rulebook {book.rulebook_id}: {mismatch}.",
                    )
                    continue
                found.setdefault((exc.rulebook_id, exc.rule_id), []).append(_Exception(book.rulebook_id, exc))
        for rule_key, entries in found.items():
            if len(entries) == 1:
                self.exceptions[rule_key] = entries[0]
                continue
            owners = ", ".join(entry.deployment_id for entry in entries)
            problem = (
                f"{len(entries)} exceptions name {rule_key[0]}/{rule_key[1]} (in {owners}); a rule has at "
                "most one exception, so none of them is used"
            )
            last = next(b for b in self.deployments if b.rulebook_id == entries[-1].deployment_id)
            self._invalid(
                rulebook_id=last.rulebook_id,
                issuer=last.issuer,
                source=last.rulebook_id,
                problems=[problem],
                message=f"{problem}.",
            )

    @staticmethod
    def _exception_problem(target: Rulebook, exc: RuleException) -> str | None:
        rule = target.rule(exc.rule_id)
        if rule is None:
            return f"the exception names {exc.rule}, but rulebook {exc.rulebook_id} has no rule {exc.rule_id}"
        if not rule.exceptable:
            return f"the exception names {exc.rule}, which is not exceptable"
        if rule.cap is not None:
            if exc.limit is None:
                unit = _UNITS[rule.cap.quantity]
                return f"the exception to {exc.rule}, a cap rule, states no limit (in {unit})"
        elif rule.max_concurrent_aircraft is not None:
            if exc.limit is None:
                return f"the exception to {exc.rule} states no limit (a number of aircraft)"
            if not isinstance(exc.limit, int) or exc.limit < 1:
                return f"the exception to {exc.rule} states limit {_fmt(exc.limit)}; it is an integer of 1 or more"
        elif exc.limit is not None:
            return (
                f"the exception to {exc.rule} states a limit, which only cap and "
                "max_concurrent_aircraft exceptions take"
            )
        return None

    # ----- applicability -----

    def _in_scope(self, book: Rulebook) -> bool:
        applies = book.applies_to
        if applies is None or (applies.profiles is None and applies.drive_types is None):
            return True
        if applies.profiles is not None and any(p in self.profiles for p in applies.profiles):
            return True
        return applies.drive_types is not None and any(d in self.drive_types for d in applies.drive_types)

    def _holding(self, conditions: list[Condition] | None) -> Condition | None:
        """The first condition the merged declarations satisfy, or None."""
        for condition in conditions or []:
            if condition.key in self.declarations and any(
                _same(self.declarations[condition.key], allowed) for allowed in condition.allowed
            ):
                return condition
        return None

    def _switch_reason(self, condition: Condition) -> str:
        value = self.declarations[condition.key]
        text = f"switched off: the deployment declares {condition.key}: {_fmt(value)}"
        if condition.cite is not None:
            text += f" ({condition.cite.text})"
        return text

    # ----- issues -----

    def _emit(
        self,
        code: ErrorCode,
        *,
        error: bool,
        book: Rulebook,
        rule: Rule | None,
        message: str,
        suggestion: str | None = None,
        info: _StepInfo | None = None,
        path_suffix: tuple[str, ...] = (),
        field_name: str | None = None,
        extra: Mapping[str, Any] | None = None,
        exception: dict[str, Any] | None = None,
        robot: _Robot | None = None,
        dedupe: tuple[object, ...] | None = None,
    ) -> None:
        if dedupe is not None:
            if dedupe in self._seen:
                return
            self._seen.add(dedupe)
        detail: dict[str, Any] = {"rulebook_id": book.rulebook_id}
        if rule is not None:
            detail["rule_id"] = rule.id
        detail["rule_kind"] = rule.kind if rule is not None else None
        detail["cite"] = _cite_dict(rule.cite) if rule is not None else None
        detail["issuer"] = _issuer_dict(book.issuer)
        detail["exception"] = exception
        detail["remediation_hint"] = "fix_deployment" if code in _FIX_DEPLOYMENT else "revise_program"
        detail.update(extra or {})
        who = info.robot if info is not None else robot
        if self.fleet and who is not None and who.key is not None:
            detail["member"] = who.key
        issue = ValidationError(
            code=code,
            severity="error" if error else "warning",
            primitive=info.step.primitive_name if info is not None else None,
            path=[*info.path, *path_suffix] if info is not None else ["<rulebook>", book.rulebook_id],
            field=field_name,
            message=message,
            suggestion=suggestion,
            detail=detail,
        )
        (self.result.errors if error else self.result.warnings).append(issue)

    def _invalid(
        self,
        *,
        rulebook_id: str | None,
        issuer: Issuer | None,
        source: str,
        problems: list[str],
        message: str,
    ) -> None:
        self.result.errors.append(
            ValidationError(
                code=ErrorCode.RULE_RULEBOOK_INVALID,
                severity="error",
                primitive=None,
                path=["<rulebook>", rulebook_id or source],
                field=None,
                message=message,
                suggestion="Fix the rulebook file; editing the program cannot resolve this.",
                detail={
                    "rulebook_id": rulebook_id,
                    "rule_kind": None,
                    "cite": None,
                    "issuer": _issuer_dict(issuer) if issuer is not None else None,
                    "exception": None,
                    "remediation_hint": "fix_deployment",
                    "source": source,
                    "problems": problems,
                },
            )
        )

    def _defaults_disabled(self, book: Rulebook) -> None:
        self.result.warnings.append(
            ValidationError(
                code=ErrorCode.RULE_DEFAULTS_DISABLED,
                severity="warning",
                primitive=None,
                path=["<rulebook>", book.rulebook_id],
                field=None,
                message=(
                    f"{book.title}: the bundled rulebook {book.rulebook_id} would apply to this "
                    "program, and the bundled rulebooks are switched off. Its rules were not checked."
                ),
                suggestion=None,
                detail={
                    "rulebook_id": book.rulebook_id,
                    "rule_kind": None,
                    "cite": None,
                    "issuer": _issuer_dict(book.issuer),
                    "exception": None,
                    "remediation_hint": "revise_program",
                },
            )
        )

    def _exception_for(
        self, book: Rulebook, rule: Rule, value: float | None
    ) -> tuple[bool, dict[str, Any] | None, RuleException | None]:
        """(covered, detail.exception, the exception) for one violation."""
        found = self.exceptions.get((book.rulebook_id, rule.id))
        if found is None:
            return False, None, None
        exc = found.exception
        expired = exc.expires is not None and date.fromisoformat(exc.expires) < self.as_of
        exceeds = value is not None and exc.limit is not None and value > exc.limit
        detail = {
            "rulebook_id": found.deployment_id,
            "basis": exc.basis,
            "limit": exc.limit,
            "expires": exc.expires,
            "expired": expired,
            "exceeds_limit": exceeds,
        }
        return not expired and not exceeds, detail, exc

    @staticmethod
    def _allowed_by(exc: RuleException, unit: str | None = None) -> str:
        terms: list[str] = []
        if exc.limit is not None:
            terms.append(f"limit {_fmt(exc.limit)}{' ' + unit if unit else ''}")
        if exc.expires is not None:
            terms.append(f"expires {exc.expires}")
        tail = f" ({', '.join(terms)})" if terms else ""
        return f"allowed by exception: {exc.basis.strip()}{tail}"

    @staticmethod
    def _not_covered(exc: RuleException, detail: dict[str, Any], unit: str | None = None) -> str:
        if detail["expired"]:
            return f" The exception ({exc.basis.strip()}) expired on {exc.expires}."
        limit = f"{_fmt(exc.limit)}{' ' + unit if unit else ''}"
        return f" The value is above the exception's limit of {limit} ({exc.basis.strip()})."

    @staticmethod
    def _head(book: Rulebook, rule: Rule) -> str:
        source = rule.cite.text if rule.cite is not None else f"{book.rulebook_id}/{rule.id}"
        return f"{source}: {_phrase(rule.title)}."

    def _violation(
        self,
        code: ErrorCode,
        *,
        book: Rulebook,
        rule: Rule,
        body: str,
        suggestion: str | None,
        info: _StepInfo | None = None,
        path_suffix: tuple[str, ...] = (),
        field_name: str | None = None,
        extra: Mapping[str, Any] | None = None,
        value: float | None = None,
        unit: str | None = None,
        limit_text: str | None = None,
        dedupe: tuple[object, ...] | None = None,
        error: bool = True,
    ) -> None:
        """Emit a rule violation, downgraded to a warning when an exception covers it.

        ``body`` is the sentence after the rule's citation and title; for a
        value rule it names the value, and ``limit_text`` names the limit.
        """
        covered, exc_detail, exc = self._exception_for(book, rule, value)
        text = f"{self._head(book, rule)} {body}"
        if exc is not None and exc_detail is not None and covered:
            # A covered violation keeps its code, becomes a warning, and names the basis.
            text += f"; {self._allowed_by(exc, unit)}."
            suggestion = None
            error = False
        else:
            text += f"; {limit_text}." if limit_text is not None else "."
            if exc is not None and exc_detail is not None:
                text += self._not_covered(exc, exc_detail, unit)
        self._emit(
            code,
            error=error,
            book=book,
            rule=rule,
            message=text,
            suggestion=suggestion,
            info=info,
            path_suffix=path_suffix,
            field_name=field_name,
            extra=extra,
            exception=exc_detail,
            dedupe=dedupe,
        )

    def _place_unknown(
        self,
        book: Rulebook,
        rule: Rule,
        info: _StepInfo,
        reason: str,
        *,
        field_name: str | None = None,
        zone: _Zone | None = None,
    ) -> None:
        suggestion = (
            "Move to a declared place before this step."
            if reason == _NOT_KNOWN
            else "Name a declared place the rule can judge."
        )
        extra: dict[str, Any] = {"reason": reason}
        if zone is not None:
            extra["zone"] = zone.name
        self._emit(
            ErrorCode.RULE_PLACE_UNKNOWN,
            error=True,
            book=book,
            rule=rule,
            message=(
                f"{self._head(book, rule)} The rule cannot place this "
                f"{info.step.primitive_name} step: {reason}. Zone rules fail closed."
            ),
            suggestion=suggestion,
            info=info,
            field_name=field_name,
            extra=extra,
            dedupe=(book.rulebook_id, rule.id, "place_unknown", info.path, zone.name if zone else None),
        )

    # ----- the program walk -----

    def _robot_for(self, member: str | None) -> _Robot | None:
        if not self.fleet:
            return self.robots.get(None)
        key = member if member is not None else self.sole_member
        return self.robots.get(key) if key is not None else None

    @property
    def infos(self) -> list[_StepInfo]:
        """Every step in execution order, with its robot, targets and current place."""
        if self._infos is None:
            self._infos = []
            self._walk(self.program.behavior, {}, None, ("behavior",))
        return self._infos

    def _walk(
        self,
        node: object,
        state: dict[str | None, _Place | None],
        member: str | None,
        path: tuple[str, ...],
    ) -> dict[str | None, _Place | None]:
        if isinstance(node, Step):
            robot = self._robot_for(member)
            if robot is None:
                return state  # an unaddressed fleet step: the fleet pass reports it
            targets = _targets(node, robot)
            before = state.get(robot.key)
            assert self._infos is not None
            self._infos.append(_StepInfo(path, node, robot, before, targets))
            after = dict(state)
            after[robot.key] = _place_after(node, targets, before)
            return after
        if isinstance(node, SequenceNode):
            for idx, sub in enumerate(node.steps):
                state = self._walk(sub, state, member, (*path, "steps", str(idx)))
            return state
        if isinstance(node, Branch):
            ends = [self._walk(node.if_true, state, member, (*path, "if_true"))]
            if node.if_false is not None:
                ends.append(self._walk(node.if_false, state, member, (*path, "if_false")))
            else:
                ends.append(state)  # a missing if_false arm leaves the place unchanged
            return _merge(ends)
        if isinstance(node, Parallel):
            movers = [self._moved(arm, member) for arm in node.branches]
            ends = []
            for idx, arm in enumerate(node.branches):
                start = dict(state)
                for other, moved in enumerate(movers):
                    if other != idx:
                        for key in moved:
                            start[key] = None
                ends.append(self._walk(arm, start, member, (*path, "branches", str(idx))))
            return _merge(ends)
        if isinstance(node, Retry):
            start = dict(state)
            for key in self._moved(node.behavior, member):
                start[key] = None  # a second attempt starts wherever the first stopped
            return self._walk(node.behavior, start, member, (*path, "behavior"))
        if isinstance(node, OnMember):
            scoped = node.member if self.fleet else member
            return self._walk(node.body, state, scoped, (*path, "body"))
        return state  # Barrier: no step, no place change

    def _moved(self, node: object, member: str | None) -> set[str | None]:
        """The robots whose place a subtree changes."""
        out: set[str | None] = set()

        def visit(n: object, m: str | None) -> None:
            if isinstance(n, Step):
                robot = self._robot_for(m)
                if robot is not None and _moves(n):
                    out.add(robot.key)
            elif isinstance(n, SequenceNode):
                for sub in n.steps:
                    visit(sub, m)
            elif isinstance(n, Branch):
                visit(n.if_true, m)
                if n.if_false is not None:
                    visit(n.if_false, m)
            elif isinstance(n, Parallel):
                for sub in n.branches:
                    visit(sub, m)
            elif isinstance(n, Retry):
                visit(n.behavior, m)
            elif isinstance(n, OnMember):
                visit(n.body, n.member if self.fleet else m)

        visit(node, member)
        return out

    def _program_robots(self) -> list[_Robot]:
        """The robots that execute steps, in order of first appearance."""
        if not self.fleet:
            robot = self.robots.get(None)
            return [robot] if robot is not None else []
        seen: list[_Robot] = []
        for info in self.infos:
            if info.robot not in seen:
                seen.append(info.robot)
        return seen

    def _rule_zones(self, book: Rulebook, rule: Rule, names: list[str]) -> dict[str | None, list[_Zone]]:
        """Resolve a rule's zones per robot, warning once per rule, zone and robot."""
        out: dict[str | None, list[_Zone]] = {}
        for robot in self._program_robots():
            resolved: list[_Zone] = []
            for name in names:
                zone = _resolve_zone(name, robot)
                if zone is not None:
                    resolved.append(zone)
                    continue
                who = f" (member {robot.key!r})" if self.fleet and robot.key is not None else ""
                self._emit(
                    ErrorCode.RULE_ZONE_UNDECLARED,
                    error=False,
                    book=book,
                    rule=rule,
                    message=(
                        f"{self._head(book, rule)} The rule names zone {name!r}, which no declared "
                        f"area or envelope zone declares{who}, so the rule cannot judge it."
                    ),
                    suggestion=f"Declare {name!r} in the manifest's declared_areas or in the envelope.",
                    extra={"zone": name},
                    robot=robot,
                    dedupe=(book.rulebook_id, rule.id, "zone_undeclared", name, robot.key),
                )
            out[robot.key] = resolved
        return out

    # ----- rule kinds -----

    def _judge_cap(self, book: Rulebook, rule: Rule) -> None:
        body = rule.cap
        assert body is not None
        unit = _UNITS[body.quantity]
        for info in self.infos:
            for value in _cap_values(info, body.quantity):
                if value.amount <= body.max:
                    continue
                found = self.exceptions.get((book.rulebook_id, rule.id))
                limit = body.max
                if found is not None and found.exception.limit is not None:
                    expired = found.exception.expires is not None and (
                        date.fromisoformat(found.exception.expires) < self.as_of
                    )
                    if not expired:
                        limit = max(limit, float(found.exception.limit))
                if value.named_place:
                    suggestion = f"Name a place at or below {_fmt(limit)} {unit}."
                else:
                    suggestion = f"Use a value at or below {_fmt(limit)} {unit}."
                self._violation(
                    ErrorCode.RULE_CAP_EXCEEDED,
                    book=book,
                    rule=rule,
                    body=f"{value.what} is {_fmt(value.amount)} {unit}",
                    limit_text=f"the limit is {_fmt(body.max)} {unit}",
                    suggestion=suggestion,
                    info=info,
                    path_suffix=value.path_suffix,
                    field_name=value.field,
                    extra={"quantity": body.quantity, "value": value.amount, "limit": body.max},
                    value=value.amount,
                    unit=unit,
                )

    def _judge_forbid_primitive(self, book: Rulebook, rule: Rule) -> None:
        body = rule.forbid_primitive
        assert body is not None
        zones_by_robot = self._rule_zones(book, rule, body.in_zones) if body.in_zones is not None else None
        for info in self.infos:
            match = next(
                (
                    (primitive, name)
                    for primitive, name in _uses(info.step)
                    if primitive in body.primitives
                    and (body.names is None or name in body.names)
                    and (body.except_names is None or name not in body.except_names)
                ),
                None,
            )
            if match is None:
                continue
            primitive, name = match
            own = info.step.primitive_name
            extra: dict[str, Any] = {"primitive": primitive}
            if own != primitive:
                extra["used_by"] = own
            if name is not None:
                extra["name"] = name
            # `use` names the forbidden use; `why` says why the rule refuses it.
            if name is not None:
                use = f"{own} {name!r}"
                if body.names is not None:
                    why = f"is on the rule's forbidden list ({', '.join(body.names)})"
                    suggestion = f"Do not use {own} {name!r}."
                elif body.except_names is not None:
                    why = f"is not on the rule's allowed list ({', '.join(body.except_names)})"
                    suggestion = f"Use only a {own} on the allowed list: {', '.join(body.except_names)}."
                else:
                    why = "is forbidden by the rule"
                    suggestion = f"Reach the goal without {primitive}."
            elif own == primitive:
                use = f"The step uses {primitive}"
                why = "which the rule forbids"
                suggestion = f"Reach the goal without {primitive}."
            else:
                use = f"{own} counts as a use of {primitive}"
                why = "which the rule forbids"
                suggestion = f"Reach the goal without {primitive}; the rule also covers {own}."
            if zones_by_robot is None:
                comma = ", " if why.startswith("which") else " "
                self._violation(
                    ErrorCode.RULE_PRIMITIVE_FORBIDDEN,
                    book=book,
                    rule=rule,
                    body=f"{use}{comma}{why}",
                    suggestion=suggestion,
                    info=info,
                    extra=extra,
                    dedupe=(book.rulebook_id, rule.id, "primitive", info.path, None),
                )
                continue
            zones = zones_by_robot.get(info.robot.key, [])
            if not zones:
                continue
            places, reasons = self._happens_at(info)
            for place in places:
                for zone in zones:
                    inside = _place_in_zone(place, zone, info.robot.frames)
                    if inside is None:
                        self._place_unknown(
                            book, rule, info,
                            f"{place.label} cannot be expressed in the frame {zone.frame!r} of zone {zone.name!r}",
                            zone=zone,
                        )
                    elif inside:
                        where = f"in zone {zone.name!r} ({zone.source})"
                        self._violation(
                            ErrorCode.RULE_PRIMITIVE_FORBIDDEN,
                            book=book,
                            rule=rule,
                            body=f"{use} {where}" if name is None else f"{use} runs {where}",
                            suggestion=f"Do not use {primitive} in {zone.name!r}; move out of the zone first.",
                            info=info,
                            extra={**extra, "zone": zone.name},
                            dedupe=(book.rulebook_id, rule.id, "primitive", info.path, zone.name),
                        )
            for reason in reasons:
                self._place_unknown(book, rule, info, reason)

    def _happens_at(self, info: _StepInfo) -> tuple[list[_Place], list[str]]:
        """Where a step happens, for a zone-scoped forbid_primitive rule."""
        places: list[_Place] = []
        reasons: list[str] = []
        if info.targets:
            for target in info.targets:
                if target.place is None:
                    reasons.append(target.unknown_reason)
                else:
                    places.append(target.place)
            return places, reasons
        if info.place_before is None:
            reasons.append(_NOT_KNOWN)
        else:
            places.append(info.place_before)
        if info.step.primitive_name == "capture":
            aimed = info.step.capture.target if info.step.capture is not None else None
            if aimed is not None and not aimed.startswith("$"):
                named = _named_place(aimed, info.robot.manifest)
                if named is not None:
                    places.append(named)
        return places, reasons

    def _judge_forbid_zone_entry(self, book: Rulebook, rule: Rule) -> None:
        body = rule.forbid_zone_entry
        assert body is not None
        zones_by_robot = self._rule_zones(book, rule, body.zones)
        for info in self.infos:
            zones = zones_by_robot.get(info.robot.key, [])
            if zones:
                self._judge_targets(
                    ErrorCode.RULE_ZONE_FORBIDDEN, book, rule, info, zones,
                    describe=lambda target, zone: f"{target.label} is in zone {zone.name!r} ({zone.source})",
                    suggest=lambda zone: f"Choose a target outside {zone.name!r}.",
                )

    def _judge_forbid_over_people(self, book: Rulebook, rule: Rule) -> None:
        body = rule.forbid_over_people
        assert body is not None
        if self._holding(body.unless_declared) is not None:
            return  # a declaration satisfies the rule
        for info in self.infos:
            robot = info.robot
            if not robot.aircraft or robot.envelope is None:
                continue
            zones = [
                _Zone(
                    z.name, z.frame, tuple((float(x), float(y)) for x, y in z.vertices),
                    "people-occupancy zone", z.allow_override,
                )
                for z in robot.envelope.people_occupancy_zones
            ]
            if not zones:
                continue

            def describe(target: _Target, zone: _Zone) -> str:
                text = f"{target.label} is over the people-occupancy zone {zone.name!r}"
                if zone.allow_override:
                    text += (
                        ". The envelope marks the zone allow_override: true, which accepts a "
                        "physical risk and does not change this rule"
                    )
                return text

            self._judge_targets(
                ErrorCode.RULE_OVER_PEOPLE, book, rule, info, zones,
                describe=describe,
                suggest=lambda zone: f"Choose a target outside the people-occupancy zone {zone.name!r}.",
            )

    def _judge_targets(
        self,
        code: ErrorCode,
        book: Rulebook,
        rule: Rule,
        info: _StepInfo,
        zones: list[_Zone],
        *,
        describe: Callable[[_Target, _Zone], str],
        suggest: Callable[[_Zone], str],
    ) -> None:
        """Judge every target of a step against zones (zone entry and over people)."""
        for target in info.targets:
            if target.place is None:
                self._place_unknown(book, rule, info, target.unknown_reason, field_name=target.field)
                continue
            for zone in zones:
                inside = _place_in_zone(target.place, zone, info.robot.frames)
                if inside is None:
                    self._place_unknown(
                        book, rule, info,
                        f"{target.label} cannot be expressed in the frame {zone.frame!r} of zone {zone.name!r}",
                        field_name=target.field,
                        zone=zone,
                    )
                elif inside:
                    self._violation(
                        code,
                        book=book,
                        rule=rule,
                        body=describe(target, zone),
                        suggestion=suggest(zone),
                        info=info,
                        field_name=target.field,
                        extra={"zone": zone.name, "target": target.label},
                        dedupe=(book.rulebook_id, rule.id, str(code), info.path, zone.name),
                    )

    def _judge_require_declared(self, book: Rulebook, rule: Rule) -> None:
        body = rule.require_declared
        assert body is not None
        present = body.key in self.declarations
        value = self.declarations.get(body.key)
        if present and (body.allowed is None or any(_same(value, a) for a in body.allowed)):
            return
        allowed = f" (allowed: {', '.join(_fmt(a) for a in body.allowed)})" if body.allowed else ""
        if not self.deployments:
            text = (
                f"No deployment rulebook is loaded, so nothing declares {body.key}; "
                f"a deployment rulebook must declare it{allowed}"
            )
        elif not present:
            text = f"The deployment declares no {body.key}{allowed}"
        else:
            text = f"The deployment declares {body.key}: {_fmt(value)}, which is not an allowed value{allowed}"
        self._violation(
            ErrorCode.RULE_DECLARATION_MISSING,
            book=book,
            rule=rule,
            body=text,
            suggestion=f"Declare {body.key} in the deployment rulebook.",
            extra={
                "key": body.key,
                "declared_value": value if present else None,
                "allowed_values": list(body.allowed) if body.allowed is not None else None,
            },
            error=bool(self.deployments),
        )

    def _judge_max_concurrent_aircraft(self, book: Rulebook, rule: Rule) -> None:
        if not self.fleet:
            return  # a single-robot validation has at most one aircraft
        body = rule.max_concurrent_aircraft
        assert body is not None
        count, aircraft = self._airborne_peak()
        pilots: int | None = None
        if body.max is not None:
            limit = body.max
            limit_text = f"the limit is {limit}"
        else:
            assert body.max_per_remote_pilot is not None
            pilots = self._remote_pilots()
            limit = body.max_per_remote_pilot * pilots
            limit_text = (
                f"the limit is {limit} ({body.max_per_remote_pilot} per remote pilot in command, "
                f"{_plural(pilots, 'remote pilot')} in command)"
            )
        if count <= limit:
            return
        self._violation(
            ErrorCode.RULE_CONCURRENCY_EXCEEDED,
            book=book,
            rule=rule,
            body=f"The program can have {count} aircraft airborne at once ({', '.join(sorted(aircraft))})",
            limit_text=limit_text,
            suggestion="Land each aircraft before the next one takes off.",
            extra={
                "count": count,
                "limit": limit,
                "aircraft": sorted(aircraft),
                "remote_pilots_in_command": pilots,
            },
            value=float(count),
            dedupe=(book.rulebook_id, rule.id, "concurrency"),
        )

    def _remote_pilots(self) -> int:
        value = self.declarations.get("remote_pilots_in_command")
        if isinstance(value, int) and not isinstance(value, bool) and value >= 1:
            return value
        return 1

    def _airborne_peak(self) -> tuple[int, frozenset[str]]:
        """The most aircraft airborne at once, and which (spec, *max_concurrent_aircraft*)."""
        if self._air is None:
            aircraft = {key for key, robot in self.robots.items() if key is not None and robot.aircraft}
            first: dict[str, str] = {}
            for info in self.infos:
                key = info.robot.key
                name = info.step.primitive_name
                if key in aircraft and key is not None and key not in first and name in _FLIGHT_STEPS:
                    first[key] = name
            initial = frozenset(key for key, name in first.items() if name != "take_off")
            _, peak, peak_set, _ = self._air_walk(self.program.behavior, initial, None)
            self._air = (peak, peak_set)
        return self._air

    def _air_walk(
        self, node: object, airborne: frozenset[str], member: str | None
    ) -> tuple[frozenset[str], int, frozenset[str], frozenset[str]]:
        """(end state, peak count, peak set, members airborne at any point)."""
        if isinstance(node, Step):
            robot = self._robot_for(member)
            if robot is None or robot.key is None or not robot.aircraft:
                return airborne, len(airborne), airborne, airborne
            name = node.primitive_name
            if name == "take_off":
                during = after = airborne | {robot.key}
            elif name in ("land", "return_to_home"):
                during, after = airborne, airborne - {robot.key}
            else:
                during = after = airborne
            return after, len(during), during, during
        if isinstance(node, SequenceNode):
            state, peak, peak_set, ever = airborne, len(airborne), airborne, airborne
            for sub in node.steps:
                state, p, s, v = self._air_walk(sub, state, member)
                if p > peak:
                    peak, peak_set = p, s
                ever = ever | v
            return state, peak, peak_set, ever
        if isinstance(node, Branch):
            first = self._air_walk(node.if_true, airborne, member)
            second = (
                self._air_walk(node.if_false, airborne, member)
                if node.if_false is not None
                else (airborne, len(airborne), airborne, airborne)
            )
            best = first if first[1] >= second[1] else second
            return first[0] | second[0], best[1], best[2], first[3] | second[3]
        if isinstance(node, Parallel):
            arms = [self._air_walk(arm, airborne, member) for arm in node.branches]
            together = airborne.union(*(arm[3] for arm in arms))
            end = frozenset().union(*(arm[0] for arm in arms))
            return end, len(together), together, together
        if isinstance(node, Retry):
            end, peak, peak_set, ever = self._air_walk(node.behavior, airborne, member)
            return airborne | end, peak, peak_set, ever
        if isinstance(node, OnMember):
            return self._air_walk(node.body, airborne, node.member if self.fleet else member)
        return airborne, len(airborne), airborne, airborne  # Barrier


def _merge(states: list[dict[str | None, _Place | None]]) -> dict[str | None, _Place | None]:
    """The arms' common end place per robot, or unknown when they differ."""
    keys: set[str | None] = set()
    for state in states:
        keys.update(state)
    merged: dict[str | None, _Place | None] = {}
    for key in keys:
        values = [state.get(key) for state in states]
        first = values[0]
        merged[key] = first if first is not None and all(v == first for v in values) else None
    return merged


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def run_rulebook_pass(
    program: URMLProgram,
    robots: Mapping[str | None, tuple[CapabilityManifest, SafetyEnvelope | None]],
    *,
    fleet: bool,
    sole_member: str | None = None,
    profiles: SequenceABC[str] = (),
    rulebooks: SequenceABC[Mapping[str, Any] | Rulebook] = (),
    default_rulebooks: bool = True,
    as_of: date | None = None,
) -> RulebookPassResult:
    """Judge a program against the rulebooks that apply to it.

    Args:
        program: The validated program (Pass 1 succeeded).
        robots: ``{None: (manifest, envelope)}`` for a single-robot validation,
            ``{member: (manifest, envelope)}`` for a fleet.
        fleet: True under ``validate_fleet``: steps are attributed through
            ``on:`` nodes and ``max_concurrent_aircraft`` is judged.
        sole_member: The member an unaddressed step belongs to in a fleet of one.
        profiles: The caller's profiles; the program's own profiles are added.
        rulebooks: The caller's rulebooks, as parsed YAML mappings or models.
        default_rulebooks: False switches off the bundled rulebooks only.
        as_of: The validation date for exception expiry; None is today in UTC.
    """
    table = {
        key: _Robot(key, manifest, envelope, {f.name: f for f in manifest.frames})
        for key, (manifest, envelope) in robots.items()
    }
    today = as_of if as_of is not None else datetime.now(UTC).date()
    judge = _RulebookPass(
        program, table, fleet=fleet, sole_member=sole_member, profiles=profiles, as_of=today
    )
    return judge.run(rulebooks, default_rulebooks)


__all__ = ["BUNDLED_PACKAGE", "RulebookPassResult", "bundled_rulebooks", "run_rulebook_pass"]
