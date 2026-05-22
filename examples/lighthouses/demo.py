"""Move #1 lighthouse demo runner — one entry point, 16 Tier-1 vendors.

Each Tier-1 vendor in the URML Move #1 lighthouse program (RFCs
0023–0038) ships an in-repo warm-touch artifact:

  * A brand-named manifest fixture in
    ``reference/validator/tests/fixtures/manifests/<vendor>_cell.yaml``
    (or its parts-vendor equivalent).
  * A positive conformance fixture in
    ``conformance/fixtures/industrial/<NN>_<vendor>_cell_positive.yaml``
    (or its parts-vendor equivalent).
  * An adapter (for arms) or a manifest declaration (for parts), all
    against the frozen substrate-neutral ``ROSAdapter`` Protocol.

This script lets a reader pick any single lighthouse vendor, run that
vendor's conformance fixture **hermetically** against ``MockROSAdapter``,
and see the audit trace. No ROS, no hardware, no network.

Usage::

    PYTHONPATH=reference/validator/src;reference/ros2-runtime/src;conformance/src \\
        python examples/lighthouses/demo.py --vendor yaskawa
    python examples/lighthouses/demo.py --vendor ouster
    python examples/lighthouses/demo.py --list

For vendors with no shipping adapter today (OSRF/Gazebo Sim, ROS-
Industrial Consortium), the demo prints the honest "no adapter
shipping; RFC-NNNN proposes one" notice rather than a fake demo.

See ``docs/rfcs/0023-..-integration.md`` through ``0038-..-consortium.md``
for the per-vendor mapping RFCs.
"""

from __future__ import annotations

import argparse
import sys

# (rfc_number, vendor_display, conformance_fixture_or_None, kind, rfc_slug)
# kind in {"arm", "part", "proposal", "institutional"}
LIGHTHOUSES: dict[str, tuple[int, str, str | None, str, str]] = {
    "yaskawa": (23, "Yaskawa / MotoROS2", "industrial/yaskawa_cell_positive", "arm", "yaskawa-motoros2-integration"),
    "ur": (24, "Universal Robots (dual-adapter substrate-neutrality proof)", "industrial/ur_cell_positive", "arm", "universal-robots-integration"),
    "kuka": (25, "KUKA (via kroshu/kuka_drivers)", "industrial/kuka_cell_positive", "arm", "kuka-integration"),
    "staubli": (26, "Staubli (via ros-industrial)", "industrial/staubli_cell_positive", "arm", "staubli-integration"),
    "mitsubishi": (27, "Mitsubishi MELFA", "industrial/mitsubishi_cell_positive", "arm", "mitsubishi-melfa-integration"),
    "fanuc": (28, "FANUC", "industrial/fanuc_cell_positive", "arm", "fanuc-integration"),
    "kawasaki": (29, "Kawasaki", "industrial/kawasaki_cell_positive", "arm", "kawasaki-integration"),
    "denso": (30, "Denso", "industrial/denso_cell_positive", "arm", "denso-integration"),
    "schunk": (31, "SCHUNK", "industrial/schunk_gripper_positive", "part", "schunk-integration"),
    "ouster": (32, "Ouster", "industrial/ouster_3d_lidar_cell_positive", "part", "ouster-integration"),
    "sick": (33, "SICK", "industrial/sick_safety_lidar_positive", "part", "sick-integration"),
    "festo": (34, "Festo", "industrial/festo_dhep_cell_positive", "part", "festo-integration"),
    "zivid": (35, "Zivid", "industrial/zivid_two_cell_positive", "part", "zivid-integration"),
    "hokuyo": (36, "Hokuyo", "industrial/hokuyo_lidar_cell_positive", "part", "hokuyo-integration"),
    "osrf": (37, "OSRF / Gazebo Sim", None, "proposal", "osrf-gazebo-integration"),
    "ros-industrial": (38, "ROS-Industrial Consortium", None, "institutional", "ros-industrial-consortium"),
}


def _list() -> None:
    """Print the 16 lighthouse vendors + their RFC + adapter status."""
    print("Move #1 lighthouse - 16 Tier-1 vendors (RFCs 0023-0038):")
    print()
    print(f"  {'Vendor':24} {'RFC':6} {'Kind':14} {'Shipping artifact?'}")
    print(f"  {'-' * 70}")
    for slug, (rfc, display, fixture, kind, _rfc_slug) in LIGHTHOUSES.items():
        artifact = "yes" if fixture else "no - proposal-only"
        print(f"  {slug:24} 00{rfc:02}   {kind:14} {artifact}")
    print()
    print("Run `python examples/lighthouses/demo.py --vendor <slug>` to exercise")
    print("the conformance fixture for any vendor whose artifact is shipping.")


def _run(slug: str) -> int:
    """Run the conformance fixture for the named lighthouse vendor."""
    if slug not in LIGHTHOUSES:
        print(f"unknown vendor: {slug}")
        print("use --list to see the 16 lighthouse vendors.")
        return 2

    rfc, display, fixture, kind, rfc_slug = LIGHTHOUSES[slug]
    rfc_path = f"docs/rfcs/00{rfc:02}-{rfc_slug}.md"

    print(f"----------------------------------------------------------------")
    print(f"Lighthouse vendor: {display}")
    print(f"RFC:               {rfc_path}")
    print(f"Kind:              {kind}")
    print(f"----------------------------------------------------------------")
    print()

    if fixture is None:
        # OSRF or ROS-Industrial Consortium — proposal / institutional RFCs.
        print(f"No shipping adapter for this lighthouse vendor today.")
        print()
        if kind == "proposal":
            print(f"RFC-00{rfc} proposes a future `urml-gazebo-runtime` adapter.")
            print(f"Build follows in a later session contingent on OSRF / Open")
            print(f"Robotics feedback. See the RFC for the proposed mapping.")
        else:
            print(f"RFC-00{rfc} is the institutional umbrella RFC closing the")
            print(f"Move #1 lighthouse program. Engagement is at the consortium")
            print(f"level (rosindustrial.org), not on a single GitHub repo.")
        return 0

    # Run the named conformance fixture against MockROSAdapter, hermetically.
    try:
        from urml_conformance import ConformanceRunner
        from urml_conformance.fixtures import discover_fixtures
    except ImportError as exc:
        print(f"could not import urml_conformance: {exc}", file=sys.stderr)
        print()
        print("Did you set PYTHONPATH? Try:")
        print("  $env:PYTHONPATH = \"reference/validator/src;reference/ros2-runtime/src;conformance/src\"")
        return 2

    cases = [c for c in discover_fixtures() if c.name == fixture]
    if not cases:
        print(f"fixture not found by name: {fixture!r}", file=sys.stderr)
        return 2
    runner = ConformanceRunner(cases=cases)
    report = runner.run()

    print(report.render())
    print()
    if report.all_passed:
        print(f"[PASS] {display} - fixture passed hermetically against MockROSAdapter.")
        print(f"       The substrate-neutral Protocol survives this vendor's manifest.")
        return 0
    else:
        print(f"[FAIL] {display} - fixture failed. See above.")
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Move #1 lighthouse demo runner — exercises the conformance "
        "fixture for any of the 16 Tier-1 vendors in URML's Move #1 lighthouse "
        "program (RFCs 0023–0038)."
    )
    parser.add_argument("--vendor", help="Vendor slug (use --list to see all 16).")
    parser.add_argument("--list", action="store_true", help="List the 16 lighthouse vendors.")
    args = parser.parse_args()

    if args.list:
        _list()
        return 0
    if not args.vendor:
        parser.print_help()
        return 2
    return _run(args.vendor)


if __name__ == "__main__":
    sys.exit(main())
