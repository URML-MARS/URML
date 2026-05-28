#!/usr/bin/env python3
"""URML-provided validation script for real Marty v1 / v2 hardware.

Origin: round-4 follow-up on https://github.com/robotical/martypy/issues/52.
NikTheGeek1 (Robotical contributor) offered to run a URML-provided
validation script against real Marty hardware and share the output. URML
owns this script and the RoboticalMartyAdapter; Robotical runs the
script and shares the JSON.

Per Nik's round-4 instructions:
- self-contained (only depends on `martypy` + Python standard library)
- prints commands BEFORE running them
- movement is opt-in via explicit flags; default run is sensor-only
- no walking / kicking; movement options are limited to `eyes('normal')`
  and `stand_straight()`, which were the round-4 maintainer examples
- closes the connection cleanly in a `finally` block

Round-5 corrections (NikTheGeek1, robotical/martypy#52, 2026-05-28):
- ``martypy`` does NOT expose ``get_accelerometer_x() / _y() / _z()``
  methods; axis reads use ``get_accelerometer("x")``, ``("y")``, ``("z")``.
- The first ``get_power_status()`` after reconnect can return an empty
  / zero snapshot; a rerun returns valid data. The script now retries
  once if the first read is empty.

The script exercises the URML-documented `martypy.Marty` API surface
(skill methods + sensor getters from the round-3 authoritative list) so
the captured JSON answers: do the names URML's adapter dispatches
against still resolve to callable attributes on real Marty hardware,
and do they return the shapes URML's payload-handling expects.

Usage:

  # Sensor-only, WiFi (Marty v2):
  python marty_validate.py --method wifi --host 192.168.1.12

  # Sensor-only, USB (Marty v2 default per maintainer guidance):
  python marty_validate.py --method usb

  # Sensor-only, socket (Marty v1):
  python marty_validate.py --method socket --host 192.168.1.12

  # With the two opt-in safe visible commands:
  python marty_validate.py --method wifi --host 192.168.1.12 \\
      --with-eyes --with-stand-straight

  # Show the plan and exit without connecting (extra-cautious review):
  python marty_validate.py --method wifi --host 192.168.1.12 --plan-only

Output:
  - stderr: a human-readable plan, followed by `RUN: ...` lines logged
    before each call.
  - stdout: a single JSON object structured like the round-3 trace on
    robotical/martypy#52 so URML can capture it verbatim.

Exit codes:
  0  ran to completion (including connect failures captured in JSON)
  1  martypy not installed
  2  bad arguments (missing host for wifi/socket)
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
from typing import Any, Callable


def announce(label: str, call_str: str) -> None:
    """Log a planned call to stderr before invoking it."""
    print(f"  RUN [{label}]: {call_str}", file=sys.stderr, flush=True)


def safe_call(label: str, call_str: str, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> dict[str, Any]:
    """Invoke `fn(*args, **kwargs)` and return a JSON-friendly result envelope."""
    announce(label, call_str)
    try:
        value = fn(*args, **kwargs)
    except Exception as exc:  # noqa: BLE001 - validation script captures everything for the report
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    return {"ok": True, "type": type(value).__name__, "value": _jsonable(value)}


def _jsonable(v: Any) -> Any:
    """Best-effort coerce arbitrary martypy return shapes to JSON-friendly values."""
    if v is None or isinstance(v, (bool, int, float, str)):
        return v
    if isinstance(v, (list, tuple)):
        return [_jsonable(x) for x in v]
    if isinstance(v, dict):
        return {str(k): _jsonable(x) for k, x in v.items()}
    return repr(v)


def _is_empty_power(value: Any) -> bool:
    """Detect an empty / zero post-reconnect power_status snapshot.

    Per the robotical/martypy#52 round-4 trace (2026-05-28): the first call
    to ``get_power_status()`` immediately after reconnect may return either
    an empty dict or one whose battery percentage / capacity fields are
    zero / missing. A rerun returns valid data. The retry is a one-shot
    inside this script; no sleep loop.
    """
    if not value:
        return True
    if isinstance(value, dict):
        pct = value.get("battRemainCapacityPercent")
        cap = value.get("battRemainCapacityMAH")
        if pct in (None, 0) and cap in (None, 0):
            return True
    return False


def build_plan(args: argparse.Namespace) -> list[str]:
    """Return the human-readable plan that prints before any call runs."""
    if args.method == "usb":
        connect = "martypy.Marty('usb', blocking=False)"
    else:
        connect = f"martypy.Marty({args.method!r}, {args.host!r}, blocking=False)"
    plan = [
        f"Connect: {connect}",
        "Probe: getattr(marty, 'get_system_info' | 'get_version_info' | 'get_software_version')()",
        "Read:   marty.get_battery_remaining()",
        "Read:   marty.get_power_status()           # retried once if first read is empty (round-4 trace finding)",
        "Read:   marty.get_accelerometer()           # no-axis form returns list per round-3 trace",
        "Read:   marty.get_accelerometer('x'), ('y'), ('z')  # axis form per round-4 maintainer correction",
        "Read:   marty.get_robot_status()",
        "Read:   marty.get_distance_sensor()",
    ]
    if args.with_eyes:
        plan.append("Move:   marty.eyes('normal')               # opt-in via --with-eyes")
    if args.with_stand_straight:
        plan.append("Move:   marty.stand_straight()             # opt-in via --with-stand-straight")
    if not (args.with_eyes or args.with_stand_straight):
        plan.append("Move:   (none: no --with-eyes / --with-stand-straight flag set)")
    plan.append("Close:  marty.close() (fallback: marty.disconnect())")
    return plan


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="URML round-4 validation script for real Marty v1 / v2 hardware.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--method", choices=["usb", "wifi", "socket"], required=True,
        help="martypy.Marty connection method. v2: 'usb' or 'wifi'. v1: 'socket'.",
    )
    parser.add_argument(
        "--host", default=None,
        help="Host / IP for the wifi or socket method. Ignored for usb.",
    )
    parser.add_argument(
        "--with-eyes", action="store_true",
        help="Run marty.eyes('normal') after the sensor reads. Off by default.",
    )
    parser.add_argument(
        "--with-stand-straight", action="store_true",
        help="Run marty.stand_straight() after the sensor reads. Off by default.",
    )
    parser.add_argument(
        "--plan-only", action="store_true",
        help="Print the plan and exit without importing or connecting to martypy.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    plan = build_plan(args)
    print("# URML round-4 validation script. Execution plan:", file=sys.stderr)
    for step in plan:
        print(f"  - {step}", file=sys.stderr)
    print("", file=sys.stderr)

    if args.plan_only:
        print("# --plan-only set; exiting without connecting.", file=sys.stderr)
        print(json.dumps({"plan_only": True, "plan": plan}, indent=2))
        return 0

    if args.method in ("wifi", "socket") and args.host is None:
        print(json.dumps(
            {"connection": {"ok": False, "error": f"--host required for method={args.method!r}"}},
            indent=2,
        ))
        return 2

    print("# Executing now:", file=sys.stderr)

    try:
        import martypy  # type: ignore[import-not-found]
    except ImportError as exc:
        print(json.dumps(
            {"connection": {"ok": False, "error": f"martypy not installed: {exc}"}},
            indent=2,
        ))
        return 1

    result: dict[str, Any] = {
        "script_version": "round-5",
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "martypy_version": getattr(martypy, "__version__", "unknown"),
        "connection": {"method": args.method, "host": args.host},
    }

    connect_args: list[Any] = [args.method]
    if args.method in ("wifi", "socket"):
        connect_args.append(args.host)

    connect_str = f"martypy.Marty({', '.join(repr(a) for a in connect_args)}, blocking=False)"
    announce("connect", connect_str)
    try:
        marty = martypy.Marty(*connect_args, blocking=False)
    except Exception as exc:  # noqa: BLE001
        result["connection"]["ok"] = False
        result["connection"]["error"] = f"{type(exc).__name__}: {exc}"
        print(json.dumps(result, indent=2, default=str))
        return 0
    result["connection"]["ok"] = True

    try:
        system_info: dict[str, Any] = {}
        for name in ("get_system_info", "get_version_info", "get_software_version"):
            getter = getattr(marty, name, None)
            if callable(getter):
                system_info[name] = safe_call("system", f"marty.{name}()", getter)
        result["system"] = system_info

        result["get_battery_remaining"] = safe_call(
            "battery", "marty.get_battery_remaining()", marty.get_battery_remaining,
        )
        # Retry once if the first power-status read is empty: NikTheGeek1
        # observed on robotical/martypy#52 (2026-05-28) that the first
        # get_power_status() right after reconnect can return an empty / zero
        # snapshot, with a rerun producing valid data. Single retry, no sleep
        # loop, so the script stays predictable.
        power = safe_call("power", "marty.get_power_status()", marty.get_power_status)
        if power.get("ok") and (not power.get("value") or _is_empty_power(power.get("value"))):
            announce("power-retry", "marty.get_power_status()  # first read empty; retrying once")
            power = safe_call("power", "marty.get_power_status()", marty.get_power_status)
            power["retried_once"] = True
        result["get_power_status"] = power
        result["get_accelerometer"] = safe_call(
            "accel-noaxis", "marty.get_accelerometer()", marty.get_accelerometer,
        )
        # Per round-4 maintainer correction (robotical/martypy#52, 2026-05-28):
        # martypy does NOT expose get_accelerometer_x/y/z() methods. Axis reads
        # use the no-axis getter with an axis argument: get_accelerometer("x").
        for axis in ("x", "y", "z"):
            result[f"get_accelerometer_{axis}"] = safe_call(
                f"accel-{axis}",
                f"marty.get_accelerometer({axis!r})",
                marty.get_accelerometer,
                axis,
            )
        result["get_robot_status"] = safe_call(
            "status", "marty.get_robot_status()", marty.get_robot_status,
        )
        result["get_distance_sensor"] = safe_call(
            "distance", "marty.get_distance_sensor()", marty.get_distance_sensor,
        )

        if args.with_eyes:
            result["eyes_normal"] = safe_call(
                "movement", "marty.eyes('normal')", marty.eyes, "normal",
            )
        if args.with_stand_straight:
            result["stand_straight"] = safe_call(
                "movement", "marty.stand_straight()", marty.stand_straight,
            )

    finally:
        close = getattr(marty, "close", None) or getattr(marty, "disconnect", None)
        if callable(close):
            announce("close", f"marty.{close.__name__}()")
            try:
                close()
                result["close"] = {"ok": True, "method": close.__name__}
            except Exception as exc:  # noqa: BLE001
                result["close"] = {"ok": False, "method": close.__name__, "error": f"{type(exc).__name__}: {exc}"}
        else:
            result["close"] = {"ok": False, "error": "neither marty.close() nor marty.disconnect() present"}

    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
