# `examples/lighthouses/` — Move #1 lighthouse demo runner

This directory ships one demo runner for URML's **Move #1 lighthouse
program** — the 16 Tier-1 vendor mapping RFCs filed against the
ROS-Industrial and zero-ROS substrate vendors URML targets. Each RFC
(0023–0038) is framed as a *request for comment from `<vendor>`
maintainers* on URML's primitive-to-vendor mapping.

The demo runner exercises any single vendor's conformance fixture
hermetically against `MockROSAdapter` — no ROS, no hardware, no
network. It's the smallest possible end-to-end proof of URML's
substrate-neutral Protocol against a named vendor's manifest.

## The 16 lighthouse vendors

| Tier | RFCs | Vendors |
|---|---|---|
| **Arms** (ROS-Industrial driver lineage) | 0023–0030 | Yaskawa, Universal Robots, KUKA, Stäubli, Mitsubishi MELFA, FANUC, Kawasaki, Denso |
| **Parts** (declared in manifest, not driven) | 0031–0036 | SCHUNK, Ouster, SICK, Festo, Zivid, Hokuyo |
| **Simulator / Foundation** (proposal-only) | 0037 | OSRF / Gazebo Sim |
| **Institutional umbrella** | 0038 | ROS-Industrial Consortium |

## Quick start

```bash
# Set PYTHONPATH so the validator + conformance + runtime packages resolve.
# Windows PowerShell:
$env:PYTHONPATH = "reference/validator/src;reference/ros2-runtime/src;conformance/src"
# Linux / macOS:
export PYTHONPATH=reference/validator/src:reference/ros2-runtime/src:conformance/src

# List the 16 lighthouse vendors:
python examples/lighthouses/demo.py --list

# Run the conformance fixture for any vendor:
python examples/lighthouses/demo.py --vendor yaskawa
python examples/lighthouses/demo.py --vendor ur
python examples/lighthouses/demo.py --vendor ouster
```

For vendors whose RFC is proposal-only (OSRF / Gazebo Sim) or
institutional (ROS-Industrial Consortium), the runner prints an
honest "no adapter shipping; RFC-NNNN proposes one" notice rather
than a fake demo.

## What the demo proves

Each run loads the named vendor's conformance fixture from
`conformance/fixtures/industrial/`, resolves the vendor's brand-named
manifest from the `MANIFEST_REGISTRY`, runs URML's validator + executor
through `ConformanceRunner` against `MockROSAdapter`, and prints the
audit trace. A passing run means:

1. The vendor's manifest schema-validates clean.
2. The validator's five passes (typing → capability → safety envelope
   → bindings → compliance policy) accept the manifest under the
   bundled US-federal default policy (RFC-0004) — every lighthouse
   vendor is allied-origin and not on the denylist.
3. The substrate-neutral Protocol survives the vendor's manifest —
   the same `MockROSAdapter` that exercises the in-tree conformance
   suite drives this fixture identically.

## What the demo does *not* prove

- It does not exercise the vendor's real driver / SDK. The gated
  CI workflows (`industrial-arm-integration.yml`, `cobot-integration.yml`,
  etc.) do that with a sourced ROS 2 environment.
- It does not certify the vendor as URML-compatible. URML's
  conformance-listing path is per [RFC-0014](../../docs/rfcs/0014-substrate-conformance.md)
  and is opt-in by the vendor.
- It does not commit URML to any partnership with the vendor. The
  RFC is a request for comment; partnership is a separate, later
  conversation.

## The outreach ledger (`outreach.yaml`)

`outreach.yaml` is the project's per-vendor record of what was sent, to
whom, when, and what came back. It is the listening side of the Move #1
program — without it, "did anyone respond?" lives in the maintainer's
head, not in the repo. One row per vendor; schema documented in the file
header. The `slug` set is asserted equal to `demo.py::LIGHTHOUSES` by
[`conformance/tests/test_outreach_ledger.py`](../../conformance/tests/test_outreach_ledger.py)
so the two cannot drift.

`response` enum: `none | acked | engaged | declined | wontfix`. Default
state for every freshly-sent vendor is `none`, with `last_touch == sent_at`.
**Do not massage these to look more engaged than reality.** When a
maintainer takes any action on a vendor (a nudge, a follow-up, a reply
arriving), bump `last_touch`, set `response` to the matching enum value,
and write the next concrete step into `next_action`. Notes hold facts,
not feelings.

The list view (`python examples/lighthouses/demo.py --list`) will print
the response status alongside the vendor when the ledger is present.

## See also

- The per-vendor mapping RFCs: [`docs/rfcs/0023-yaskawa-motoros2-integration.md`](../../docs/rfcs/0023-yaskawa-motoros2-integration.md) through [`0038-ros-industrial-consortium.md`](../../docs/rfcs/0038-ros-industrial-consortium.md).
- [RFC-0014](../../docs/rfcs/0014-substrate-conformance.md) — what makes a runtime URML-compatible (the normative substrate-conformance contract).
- [RFC-0007](../../docs/rfcs/0007-manufacturer-go-to-market.md) — the manufacturer go-to-market wedge underlying the lighthouse program.
- [URML's conformance suite](../../conformance/) — the broader test surface this demo is a subset of.
