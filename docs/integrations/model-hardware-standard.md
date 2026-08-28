<p align="center">
  <a href="https://urml.dev"><img src="https://urml.dev/favicon.svg" alt="URML" width="72" height="72"></a>
</p>

<p align="center">
  A small, opinionated, human-readable language for describing robot intent.
</p>

<p align="center">
  <a href="https://urml.dev"><b>urml.dev</b></a>
</p>

---

# URML and the Model Hardware Standard

Anthropic opened a research preview of the [Model Hardware Standard](https://www.anthropic.com/news/model-hardware-standard-research-preview) (MHS) on 2026-08-27. This page states where URML sits relative to it, what maps onto what, and what waits until the standard is open. Everything here is drawn from Anthropic's own announcement; URML has not seen the specification and claims no compatibility with it.

## What MHS is, in Anthropic's words

A standardized driver: "software that translates between a computer's operating system and a hardware device", built on "a simple set of primitives, commands like read (for example, get temperature) or write (for example, set temperature), that any hardware device can understand". Devices are discoverable "in a standard format, so that devices and agents can find each other and communicate across networks". Each device carries a reference file "with information about a device's general characteristics, such as what it can measure, what can be adjusted, and what safety limits will be enforced". It is model-agnostic and reachable through MCP, a command line, or code. Anthropic will open-source it after building "safety evaluations and best practices for AI systems that operate physical equipment". Preview partners include Universal Robots, Doosan Robotics, AWS, Automata, Danaher, Tecan, QIAGEN, Genentech, HHMI Janelia, the University of Washington, Carnegie Mellon, and QuEra.

## Where URML sits

```
   natural language / an agent's goal
                 |
   Layer 4  NL grammar + LLM bridge        URML
   Layer 3  behavior composition           URML
   Layer 2  intent primitives              URML     <- one program, validated whole
   Layer 1  capability manifest + envelope URML     <- derives from device descriptions
   ------------------------------------------------------------------------
   Layer 0  substrate: ROS 2, PX4, OPC UA, vendor SDKs, and now MHS drivers
             (device description, discovery, read/write, per-call limits)
```

URML's Manifesto has said since day one that Layer 1 "extends existing standards (URDF, SDF); we do not reinvent robot description". MHS is another description and driver standard at Layer 0, and URML treats it the same way it treats URDF: as a source the capability manifest derives from, and as a substrate the validated program dispatches to. URML already ships adapters for two of the MHS preview partners (Universal Robots and Doosan, in `reference/cobot-runtime/`) and an OPC UA runtime whose intent-to-node mapping is the closest existing analogue of intent-to-read/write.

The one-line version: **MHS tells the agent what a device is and what it will refuse per call. URML checks the whole program against the manifest and the deployment envelope before the first call.**

## What each side has that the other does not

MHS, as announced, has: a driver contract, network discovery, a device-authored reference file, per-call limit enforcement at the device, and a distribution channel through the vendors themselves.

URML has, shipped and tested:

- **Whole-program static validation** before dispatch: five passes over an entire program (argument typing, capability, safety envelope, bindings and cross-primitive types, compliance policy). A per-call limit catches the fifth action; a program check refuses the plan.
- **The self-declaration / deployment-envelope split.** A device's own limits (what MHS's reference file carries) and a deployment's limits (what a site owner imposes) are separate artifacts; the validator conjoins them, strictest wins. A lab may cap an arm below what its vendor allows.
- **Runtime enforcement** as a second, independent check ([RFC-0667](../rfcs/0667-envelope-enforcement.md) shield) and a **rehearsal gate** that rolls the validated program out in simulation before real execution ([RFC-0668](../rfcs/0668-rehearsal-gate.md)).
- **A conformance suite** and a normative runtime contract ([RFC-0014](../rfcs/0014-substrate-conformance.md)), so "this runtime is URML-compatible" is a test result, not a claim.
- **Evidence traceability** on every capability claim ([RFC-0631](../rfcs/0631-evidence-traceability.md)): declared, derived, or verified.
- **Provider neutrality and offline execution.** MHS claims model-agnosticism too, so this is a shared value, not a differentiator. The differentiator is the validator.

## Mapping the announced reference-file concepts onto the manifest

Only the three concepts Anthropic's post names are mapped; the columns will be filled with real field names when the specification is public.

| MHS reference file (as announced) | URML capability manifest | URML deployment envelope |
|---|---|---|
| "what it can measure" | `perception.sensors[]` (`measurement_type`, `range_min/max`, `units`, RFC-0039 capability fields), `perception.cameras[]` (RFC-0682) | not applicable |
| "what can be adjusted" | `mobility` (`max_velocity`, `max_payload`, ...), `manipulation.grippers[]` (`force_min_n/force_max_n`, `accepted_classes`), `manipulation.arms[]`, `outputs.named_endpoints`, `programs` (RFC-0015) | not applicable |
| "what safety limits will be enforced" | the same mechanical ceilings, tagged with `evidence` (RFC-0631) | `max_velocity`, `max_grip_force_n`, `max_payload`, geofences, people-occupancy zones, monitorable temporal properties (RFC-0382/0667) |
| read/write primitives | not a manifest concern | not applicable; a URML *adapter* lowers Layer-2 primitives onto them (see below) |

The split in the third row is the point: MHS puts the device's own limits in the device file, which is exactly right for a device; URML adds the deployment's limits on top and validates against the stricter of the two.

## The evaluation harness

Anthropic's stated gate before open-sourcing MHS is "safety evaluations and best practices for AI systems operating physical equipment". URML's contribution to that gate is [`examples/physical-ai-safety-eval/`](../../examples/physical-ai-safety-eval/): a hermetic harness that takes a corpus of agent intents against a lab-cell manifest shaped like the assay in Anthropic's post (a liquid handler, a robotic arm, a plate reader), validates each one, and reports the refusal matrix with machine-readable reasons, the envelope-monitor verdict over the rehearsed trace of every accepted program, and the evidence class of every capability the refusals relied on. It measures whether an agent's intent is admissible on declared hardware under a declared envelope. It does not measure physics, and it says so.

## What waits for the open specification

- A reference-file importer (`mhs-to-manifest`), the same shape as the shipped [`examples/urdf-to-manifest/`](../../examples/urdf-to-manifest/).
- A real `MhsAdapter` runtime (RFC-0014 conformance) lowering URML primitives onto MHS read/write. The harness ships a labeled scaffold with an injectable transport; its wire format is a placeholder.
- Conformance fixtures for MHS-driven devices, starting with the two partners URML already has adapters for.
- Any manifest schema change. None is proposed against an unpublished schema.

Tracked in [RFC-0683](../rfcs/0683-model-hardware-standard-outreach.md).
