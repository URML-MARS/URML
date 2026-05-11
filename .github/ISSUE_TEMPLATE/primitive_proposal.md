---
name: Primitive proposal
about: Propose adding (or significantly changing) a Layer-2 intent primitive. This is a one-way door — once shipped, removing a primitive breaks every downstream user. The bar is high; this template forces the proof of work up front.
title: "[primitive] "
labels: ["primitive-proposal", "rfc-candidate"]
assignees: []
---

<!--
This issue is the *pre-RFC* artifact. If the maintainer agrees the primitive belongs in the core vocabulary, the next step is an RFC in docs/rfcs/.

Before filing, please confirm:

1. The behavior cannot be reasonably composed from existing primitives. The Manifesto and CLAUDE.md both prefer composition over expansion.
2. The primitive belongs in the *core*, not in a profile. If it is specific to one domain (home / drone / industrial / agricultural / ...), propose it as a profile extension instead.
3. You have read MANIFESTO.md §Architecture and the relevant spec/layer-*/README.md (if drafted).
-->

## Proposed name

<!-- snake_case, English, verb or verb-phrase. Examples: move_to, grasp, hover, scan. Avoid overloaded English words ("run", "go", "do") and avoid name collisions with composition keywords (sequence, parallel, retry). -->

## One-sentence semantics

<!-- What the primitive instructs a robot to do, in plain English, in one sentence. If you cannot say it in one sentence, the primitive is doing too much. -->

## Signature (sketch)

```yaml
- proposed_primitive_name:
    required_arg: <type>     # what it means
    optional_arg: <type>     # what it means; default and units
    # ...
```

## Why this primitive belongs in Layer 2

<!-- Three or four sentences. The Manifesto's bar: "If a behavior can be composed from existing primitives, it should be." Show your composition attempt and why it fell short. -->

## Substrate-neutrality acid test

Per [`CLAUDE.md`](../../CLAUDE.md) and [`MANIFESTO.md`](../../MANIFESTO.md): every Layer-2 primitive must be cleanly implementable on a runtime with **zero** ROS dependencies. Sketch both implementations below.

### ROS 2 implementation sketch

<!-- Which ROS 2 packages, actions, or topics would implement this primitive? Be specific: Nav2 action `NavigateToPose`, MoveIt 2's `MoveGroup` action, etc. If you have to invent a new ROS interface, say so. -->

### PX4 / non-ROS implementation sketch

<!-- How would this primitive be implemented on PX4 (MAVLink commands, offboard mode setpoints) or on a runtime with NO ROS at all (e.g., a vendor SDK, an OPC UA Robotics endpoint, on-device microcontroller code)? If you cannot sketch a non-ROS implementation, the primitive may be leaking substrate assumptions and needs rework. -->

## Safety and envelope behavior

- What declared capabilities (Layer-1 manifest entries) must be present for this primitive to be valid?
- What safety-envelope checks must the validator perform before allowing execution?
- What is the runtime's required behavior if the safety envelope is violated mid-execution (abort vs. degrade vs. hand-off)?

## Alternative names considered

<!-- At least one. Naming is hard; alternatives let the maintainer see the design space you explored. -->

## Profile vs. core

- [ ] I believe this should be in the core (Layer 2). Justification:
- [ ] I believe this should be in a profile. Which one:

## Prior art

<!-- Behavior-tree libraries, PDDL operators, AUTOSAR services, robotics-paper formulations, vendor APIs, etc. URML almost never invents from scratch; pointers help the maintainer route this. -->

## Implementation commitment

- [ ] If accepted, I will draft the RFC.
- [ ] If accepted, I will write the reference implementation in at least one runtime.
- [ ] If accepted, I will write conformance tests and a runnable example.
- [ ] I am proposing this as a flag for the maintainer to consider; I am not committing to implement.
