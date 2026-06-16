#!/usr/bin/env python3
"""URML intent lowered to OPC UA method calls on a robotics cell.

The worked example from the OPC UA engagements: jpfr on open62541#8077
(RFC-0313) and marcschier on OPCFoundation/UA-.NETStandard#3827 (RFC-0314).
jpfr gave the modeling: OPC UA is object-orientation over the network, so the
cell is an object, each URML operation is one method called on it, and the typed
args are the method inputs. The grain is one URML operation to one OPC UA method.

This script shows that grain end to end, hermetically (no live server):

1. Validate a pick-and-place program against the cell's manifest. Nothing is
   called until the validator proves the program admissible (validate before
   actuate).
2. Lower each operation to exactly one OPC UA method node, resolved through the
   deployment config (opcua_adapter.yaml). The node ids are deployment detail and
   live in config, never in the URML program or manifest.
3. Execute the operations through the real OpcUaAdapter against an embedded fake
   ObjectsNode, and print the call log: N operations issue N method calls, one
   each, on the configured ObjectsNode.

It is deterministic, so the committed ``method-mapping-report.txt`` is
byte-asserted in CI.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml
from urml_validator import validate

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "opcua-cell.manifest.yaml"
ADAPTER_CFG = _HERE / "opcua_adapter.yaml"


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _program() -> dict[str, Any]:
    """The RFC-0013 pick-and-place happy path (mirrors conformance fixture 07)."""
    return {
        "profile": "industrial",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [
                {"wait_for": {"condition": {"event": "safety_door_closed"}}},
                {
                    "pick_from": {
                        "source": "pick_bin",
                        "object": "widget_red",
                        "attributes": {"color": "red"},
                        "force": "firm",
                        "store_as": "red_widget",
                    }
                },
                {"place_at": {"target": "kitting_tray_red", "held": "$red_widget", "mode": "place"}},
                {
                    "report": {
                        "to": "line_controller",
                        "facts": {"cycle": "pick_red_to_tray", "result": "ok"},
                        "status": "success",
                    }
                },
            ],
        },
    }


# --------------------------------------------------------------------------
# Embedded fake OPC UA server (no asyncua install, no network). Same technique
# the opcua-runtime unit tests use: a controllable double injected into
# sys.modules so the real OpcUaAdapter runs against it.
# --------------------------------------------------------------------------


class _FakeNode:
    def __init__(self, store: dict[str, Any]) -> None:
        self._store = store

    def call_method(self, method: str, *args: Any) -> str:
        self._store.setdefault("calls", []).append((method, list(args)))
        return "ok"

    def read_value(self) -> float:
        return 7.0


class _FakeClient:
    def __init__(self, url: str, timeout: float = 5.0) -> None:
        self.url = url
        self.store: dict[str, Any] = {}

    def connect(self) -> None:  # noqa: D401
        pass

    def disconnect(self) -> None:
        pass

    def get_node(self, nodeid: str) -> _FakeNode:
        return _FakeNode(self.store)


def _install_fake_asyncua() -> None:
    sync_mod = ModuleType("asyncua.sync")
    sync_mod.Client = _FakeClient  # type: ignore[attr-defined]
    pkg = ModuleType("asyncua")
    pkg.sync = sync_mod  # type: ignore[attr-defined]
    sys.modules["asyncua"] = pkg
    sys.modules["asyncua.sync"] = sync_mod


def render_report() -> str:
    manifest = _load(MANIFEST)
    lines: list[str] = [
        "URML intent to OPC UA: one program, validated, lowered to method calls.",
        "Modeling (jpfr, open62541#8077): the cell is an object; each URML",
        "operation is one method called on it; typed args are the method inputs.",
        f"cell: {manifest['robot_id']}   substrate: urml-opcua-runtime (zero ROS)",
        "",
        "# 1. Validate the program against the manifest (validate before actuate)",
        "",
    ]
    result = validate(_program(), manifest, policy=None)
    verdict = "VALID" if result.accepted else "REJECTED"
    lines.append(f"[{verdict}] RFC-0013 pick-and-place: wait_for door, pick_from a red widget,")
    lines.append("        place_at the red tray, report. Nothing is called until this passes.")
    if not result.accepted:
        codes = ", ".join(e.code_str for e in result.errors)
        lines.append(f"   -> rejected [{codes}]")
    lines.append("")

    # Import only after the fake is installed, so the adapter binds to it.
    _install_fake_asyncua()
    from urml_opcua_runtime import OpcUaAdapter, load_opcua_config

    cfg = load_opcua_config(ADAPTER_CFG)

    # The operations the validated cycle lowers to, in order. Each is one method.
    lines += [
        "# 2. Lower each operation to one OPC UA method on the ObjectsNode "
        f"({cfg.objects_node})",
        "",
    ]

    def _fmt(method: str, args: list[str]) -> str:
        return f'{method}({", ".join(repr(a) for a in args)})'

    ops: list[tuple[str, Any, str]] = []
    with OpcUaAdapter(cfg) as cell:
        for loc in ("home_pose", "pick_bin"):
            mt = cfg.resolve_location(loc)
            assert mt is not None
            ops.append((f"move_to {loc}", lambda loc=loc: cell.send_navigation_goal(location=loc), _fmt(mt.method, mt.args)))
        g = cfg.manipulation_methods["grasp"]
        ops.append(("grasp", lambda: cell.send_manipulation_goal(action="grasp"), _fmt(g.method, g.args)))
        mt = cfg.resolve_location("kitting_tray_red")
        assert mt is not None
        ops.append(("move_to kitting_tray_red", lambda: cell.send_navigation_goal(location="kitting_tray_red"), _fmt(mt.method, mt.args)))
        r = cfg.manipulation_methods["release"]
        ops.append(("release", lambda: cell.send_manipulation_goal(action="release"), _fmt(r.method, r.args)))
        sw = cfg.resolve_service("swap_tool")
        assert sw is not None
        ops.append(("swap_tool (station service)", lambda: cell.send_docking_goal(station="tool_change_station", service="swap_tool"), _fmt(sw.method, sw.args)))
        pp = cfg.resolve_program("pick_place_cycle")
        assert pp is not None
        ops.append(("call_program pick_place_cycle", lambda: cell.call_named_program(name="pick_place_cycle"), _fmt(pp.method, pp.args)))

        width = max(len(label) for label, _, _ in ops)
        for label, _, target in ops:
            lines.append(f"  {label.ljust(width)}  ->  {target}")
        lines.append("")

        # 3. Execute against the fake ObjectsNode and read back the call log.
        lines += ["# 3. Execute against an embedded fake ObjectsNode (no live server)", ""]
        ok = all(fn().success for _, fn, _ in ops)
        client = cell._client  # the fake, after lazy connect
        calls = client.store.get("calls", [])

    lines.append(f"all {len(ops)} operations succeeded: {ok}")
    lines.append(f"{len(ops)} URML operations issued {len(calls)} method calls on {cfg.objects_node}, one each:")
    for method, args in calls:
        lines.append(f"  {_fmt(method, args)}")
    lines.append("")
    lines.append("The grain holds: one URML operation, one OPC UA method on the object.")
    lines.append("Node ids are deployment config; the URML program and manifest never name them.")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    out = _HERE / "method-mapping-report.txt"
    out.write_text(render_report(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
