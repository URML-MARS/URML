"""RFC-0382: the small temporal-logic core for envelope monitorable properties.

URML does not adopt a full STL/STREL grammar. It defines a small, closed core
that the Move #28 runtime-verification backends share, parses a property into
an AST, collects the signals the property references (so the validator can
resolve them against the manifest), and compiles the non-spatial core to STL
notation for an online monitor.

Grammar (precedence, loosest to tightest):

    expr      := implies
    implies   := or_   ('implies' or_)*          # right-associative
    or_       := and_  ('or' and_)*
    and_      := binary ('and' binary)*
    binary    := unary  (('until' | 'surround') opt_bound unary)*
    unary     := 'not' unary
               | ('always' | 'eventually' | 'somewhere' | 'everywhere') opt_bound unary
               | primary
    primary   := '(' expr ')' | atom
    atom      := term OP term            # comparison
               | signal                  # bare boolean signal (event / sensor truthiness)
               | 'true' | 'false'
    term      := number | signal
    opt_bound := ('[' number ',' number ']')?

``somewhere`` / ``everywhere`` / ``surround`` are spatial (STREL), accepted only
under dialect ``stl_strel``. ``compile_to_stl`` rejects them; STREL/Copilot
compilation is a documented follow-on.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

__all__ = [
    "Binary",
    "BoolOp",
    "Compare",
    "Const",
    "MonitorableParseError",
    "Node",
    "Not",
    "Signal",
    "Temporal",
    "compile_to_stl",
    "parse_property",
    "referenced_signals",
    "referenced_signals_custom",
]

_COMPARISONS = ("<=", ">=", "==", "<", ">")
_PREFIX_TEMPORAL = ("always", "eventually", "somewhere", "everywhere")
_INFIX_BINARY = ("until", "surround")
_SPATIAL = ("somewhere", "everywhere", "surround")
_KEYWORDS = frozenset(
    (
        "always", "eventually", "until", "not", "and", "or",
        "implies", "somewhere", "everywhere", "surround", "true", "false",
    )
)


class MonitorableParseError(ValueError):
    """Raised when a monitorable-property expression is malformed."""


# ---------------------------------------------------------------------------
# AST
# ---------------------------------------------------------------------------


class Node:
    """Base class for the property AST."""


@dataclass(frozen=True)
class Const(Node):
    value: bool


@dataclass(frozen=True)
class Signal(Node):
    name: str


@dataclass(frozen=True)
class Compare(Node):
    left: str | float
    op: str
    right: str | float


@dataclass(frozen=True)
class Not(Node):
    operand: Node


@dataclass(frozen=True)
class BoolOp(Node):
    op: str  # 'and' | 'or' | 'implies'
    left: Node
    right: Node


@dataclass(frozen=True)
class Temporal(Node):
    op: str  # 'always' | 'eventually' | 'somewhere' | 'everywhere'
    operand: Node
    bound: tuple[float, float] | None


@dataclass(frozen=True)
class Binary(Node):
    op: str  # 'until' | 'surround'
    left: Node
    right: Node
    bound: tuple[float, float] | None


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

_TOKEN_RE = re.compile(
    r"""
    \s*(?:
      (?P<number>-?\d+(?:\.\d+)?)
    | (?P<op><=|>=|==|<|>)
    | (?P<lparen>\()
    | (?P<rparen>\))
    | (?P<lbrack>\[)
    | (?P<rbrack>\])
    | (?P<comma>,)
    | (?P<ident>[A-Za-z_][A-Za-z0-9_]*)
    )
    """,
    re.VERBOSE,
)


@dataclass(frozen=True)
class _Tok:
    kind: str
    value: str


def _tokenize(text: str) -> list[_Tok]:
    toks: list[_Tok] = []
    pos = 0
    while pos < len(text):
        if text[pos].isspace():
            pos += 1
            continue
        m = _TOKEN_RE.match(text, pos)
        if not m or m.start() == m.end():
            raise MonitorableParseError(f"unexpected character at offset {pos}: {text[pos]!r}")
        kind = m.lastgroup
        assert kind is not None
        toks.append(_Tok(kind, m.group(kind)))
        pos = m.end()
    toks.append(_Tok("eof", ""))
    return toks


# ---------------------------------------------------------------------------
# Recursive-descent parser
# ---------------------------------------------------------------------------


class _Parser:
    def __init__(self, toks: list[_Tok], allow_spatial: bool) -> None:
        self._toks = toks
        self._i = 0
        self._allow_spatial = allow_spatial

    def _peek(self) -> _Tok:
        return self._toks[self._i]

    def _is_kw(self, *names: str) -> bool:
        t = self._peek()
        return t.kind == "ident" and t.value in names

    def _advance(self) -> _Tok:
        t = self._toks[self._i]
        self._i += 1
        return t

    def _expect(self, kind: str) -> _Tok:
        t = self._peek()
        if t.kind != kind:
            raise MonitorableParseError(f"expected {kind}, got {t.kind!r} ({t.value!r})")
        return self._advance()

    def parse(self) -> Node:
        node = self._implies()
        if self._peek().kind != "eof":
            t = self._peek()
            raise MonitorableParseError(f"unexpected trailing token: {t.kind!r} ({t.value!r})")
        return node

    def _implies(self) -> Node:
        left = self._or()
        if self._is_kw("implies"):
            self._advance()
            right = self._implies()  # right-associative
            return BoolOp("implies", left, right)
        return left

    def _or(self) -> Node:
        left = self._and()
        while self._is_kw("or"):
            self._advance()
            left = BoolOp("or", left, self._and())
        return left

    def _and(self) -> Node:
        left = self._binary()
        while self._is_kw("and"):
            self._advance()
            left = BoolOp("and", left, self._binary())
        return left

    def _binary(self) -> Node:
        left = self._unary()
        while self._is_kw(*_INFIX_BINARY):
            op = self._advance().value
            if op == "surround" and not self._allow_spatial:
                raise MonitorableParseError("'surround' is a spatial operator; use dialect 'stl_strel'")
            bound = self._opt_bound()
            right = self._unary()
            left = Binary(op, left, right, bound)
        return left

    def _unary(self) -> Node:
        if self._is_kw("not"):
            self._advance()
            return Not(self._unary())
        if self._is_kw(*_PREFIX_TEMPORAL):
            op = self._advance().value
            if op in _SPATIAL and not self._allow_spatial:
                raise MonitorableParseError(f"'{op}' is a spatial operator; use dialect 'stl_strel'")
            bound = self._opt_bound()
            return Temporal(op, self._unary(), bound)
        return self._primary()

    def _opt_bound(self) -> tuple[float, float] | None:
        if self._peek().kind != "lbrack":
            return None
        self._advance()
        a = float(self._expect("number").value)
        self._expect("comma")
        b = float(self._expect("number").value)
        self._expect("rbrack")
        if b < a:
            raise MonitorableParseError(f"bound upper {b} is below lower {a}")
        return (a, b)

    def _primary(self) -> Node:
        t = self._peek()
        if t.kind == "lparen":
            self._advance()
            node = self._implies()
            self._expect("rparen")
            return node
        return self._atom()

    def _atom(self) -> Node:
        if self._is_kw("true"):
            self._advance()
            return Const(True)
        if self._is_kw("false"):
            self._advance()
            return Const(False)
        left = self._term(boolean_ok=True)
        if self._peek().kind == "op":
            op = self._advance().value
            right = self._term(boolean_ok=False)
            return Compare(left, op, right)
        # bare term: must be a signal (boolean atom), not a lone number
        if isinstance(left, float):
            raise MonitorableParseError("a bare number is not a boolean atom; compare it to a signal")
        return Signal(left)

    def _term(self, *, boolean_ok: bool) -> str | float:
        t = self._peek()
        if t.kind == "number":
            self._advance()
            return float(t.value)
        if t.kind == "ident":
            if t.value in _KEYWORDS:
                raise MonitorableParseError(f"unexpected keyword {t.value!r} where a signal or number was expected")
            self._advance()
            return t.value
        raise MonitorableParseError(f"expected a signal or number, got {t.kind!r} ({t.value!r})")


def parse_property(expression: str, *, dialect: str) -> Node:
    """Parse a property expression into an AST. Raises MonitorableParseError.

    ``dialect`` is ``stl`` (temporal core only) or ``stl_strel`` (adds the
    spatial operators). ``custom`` is not parsed here (see
    :func:`referenced_signals_custom`).
    """
    if not expression or not expression.strip():
        raise MonitorableParseError("empty expression")
    allow_spatial = dialect == "stl_strel"
    return _Parser(_tokenize(expression), allow_spatial=allow_spatial).parse()


# ---------------------------------------------------------------------------
# Signal extraction + STL compilation
# ---------------------------------------------------------------------------


def referenced_signals(node: Node) -> set[str]:
    """Collect every signal identifier the property references."""
    out: set[str] = set()
    _collect(node, out)
    return out


def _collect(node: Node, out: set[str]) -> None:
    if isinstance(node, Signal):
        out.add(node.name)
    elif isinstance(node, Compare):
        if isinstance(node.left, str):
            out.add(node.left)
        if isinstance(node.right, str):
            out.add(node.right)
    elif isinstance(node, Not):
        _collect(node.operand, out)
    elif isinstance(node, Temporal):
        _collect(node.operand, out)
    elif isinstance(node, (BoolOp, Binary)):
        _collect(node.left, out)
        _collect(node.right, out)
    # Const contributes no signal.


def referenced_signals_custom(expression: str) -> set[str]:
    """Best-effort signal extraction for ``dialect: custom`` (no grammar).

    Pulls identifier-shaped tokens that are not keywords; this is enough for
    the validator to resolve signals on a custom expression it does not parse.
    """
    idents = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expression))
    return {i for i in idents if i not in _KEYWORDS}


_STL_BOOL = {"and": "&", "or": "|", "implies": "->"}


def _bound_str(bound: tuple[float, float] | None) -> str:
    if bound is None:
        return ""
    a, b = bound
    return f"[{a:g}, {b:g}]"


def compile_to_stl(node: Node) -> str:
    """Compile the non-spatial core to STL notation (RTAMT / Reelay dialect).

    Raises NotImplementedError on spatial (STREL) operators; STREL and Copilot
    compilation are documented follow-ons in RFC-0382.
    """
    if isinstance(node, Const):
        return "true" if node.value else "false"
    if isinstance(node, Signal):
        return node.name
    if isinstance(node, Compare):
        left = node.left if isinstance(node.left, str) else f"{node.left:g}"
        right = node.right if isinstance(node.right, str) else f"{node.right:g}"
        return f"({left} {node.op} {right})"
    if isinstance(node, Not):
        return f"!{compile_to_stl(node.operand)}"
    if isinstance(node, BoolOp):
        return f"({compile_to_stl(node.left)} {_STL_BOOL[node.op]} {compile_to_stl(node.right)})"
    if isinstance(node, Temporal):
        if node.op == "always":
            return f"G{_bound_str(node.bound)} {compile_to_stl(node.operand)}"
        if node.op == "eventually":
            return f"F{_bound_str(node.bound)} {compile_to_stl(node.operand)}"
        raise NotImplementedError(f"spatial operator {node.op!r} has no STL form (STREL is a follow-on)")
    if isinstance(node, Binary):
        if node.op == "until":
            return f"({compile_to_stl(node.left)} U{_bound_str(node.bound)} {compile_to_stl(node.right)})"
        raise NotImplementedError("spatial operator 'surround' has no STL form (STREL is a follow-on)")
    raise NotImplementedError(f"unknown node type {type(node).__name__}")
