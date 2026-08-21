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

# Humanoid Examples

End-to-end humanoid programs. Each scenario ships as three companion files: the natural-language prompt (`*.en.txt`), the URML program (`*.urml.yaml`), and a self-contained capability manifest (`*.manifest.yaml`).

A humanoid is a biped ([RFC-0009](../../docs/rfcs/0009-legged-humanoid-mobility.md) `mobility.drive_type: biped`) with two arms ([RFC-0010](../../docs/rfcs/0010-whole-body-bimanual-manipulation.md) whole-body manipulation) and a declarable whole-body shape ([RFC-0384](../../docs/rfcs/0384-whole-body-capability-declaration.md): kinematic chains + static-stability limits). The programs use the core vocabulary plus the `bimanual` primitive under the `home` profile (profiles over forks), exactly as the biped conformance fixtures do, and validate/execute adapter-agnostically against the humanoid runtime's `DigitAdapter` and hermetically against the mock.

## Scenarios

- **`digit-patrol`** — the minimum-viable locomotion example. A navigation-only patrol on a `biped` manifest (Agility Digit, US origin; [RFC-0009](../../docs/rfcs/0009-legged-humanoid-mobility.md) `mobility.drive_type: biped`): walk to two staging points, then return to the dock. `dock` is a declared *location* (it has a pose), not a docking action.
- **`digit-tote-lift`** — the minimum-viable whole-body example ([RFC-0010](../../docs/rfcs/0010-whole-body-bimanual-manipulation.md) + [RFC-0384](../../docs/rfcs/0384-whole-body-capability-declaration.md)). On a two-arm Digit manifest (`manipulation.arm_count: 2` with a named `arms` list) that also declares its `whole_body` shape (2 legs, 2 arms bound to the arms list, torso; a center of mass within its support polygon; `can_carry_while_moving: true`), the robot detects a tote, lifts it with both arms in one `bimanual together` step, walks it to staging carrying it, and sets it down with both arms. The runtime decomposes each `bimanual` into a left-arm and a right-arm `send_manipulation_goal`, so the audit shows one detection and two arm-addressed goals per lift. The carry-to-staging step validates only because the manifest declares the platform can carry while moving.
- **`unitree-g1-retarget`** — validating a **retargeted whole-body motion** against the [RFC-0384](../../docs/rfcs/0384-whole-body-capability-declaration.md) envelope, as **software validation, not hardware proof**. A Unitree G1 manifest declares its whole-body shape (~29 DoF across 2 legs, 2 arms, torso) and its static-stability envelope (center of mass inside the support polygon). A motion retargeted onto the robot — reach and lift with both arms, carry to staging, place — validates against that envelope before any actuator moves. Every kinematic and stability value is **declared, not measured** (tagged `evidence: source: declared`, RFC-0631), and **nothing has run on a physical G1**. Flip the CoM outside the support polygon (the sibling `unitree_g1_wholebody_unstable` manifest / conformance fixture `biped/14`) and the same class of program is rejected with `capability.whole_body_unstable_com` — the static-stability filter. Two axes stay separate: Unitree is a PRC-origin vendor, so a real provenance block would be *denied* by the US-federal default policy; this manifest carries none, so Pass 5 is a no-op and the whole-body axis is checked on its own. This is not a compliance claim.

## Validate

```
urml validate digit-patrol.urml.yaml \
  -m digit-patrol.manifest.yaml --profile home

urml validate digit-tote-lift.urml.yaml \
  -m digit-tote-lift.manifest.yaml --profile home

urml validate unitree-g1-retarget.urml.yaml \
  -m unitree-g1-retarget.manifest.yaml --profile home
```

The Digit manifests carry US-compliant provenance, so the bundled default policy accepts them. The G1 manifest carries **no** provenance block (Unitree is PRC-origin; a real one would be policy-denied), so its policy pass is a no-op and no `--no-policy` is needed — the whole-body envelope check is the point. Pass `--no-policy` to skip Pass 5 on the Digit examples. To watch one run on the hermetic mock:

```
urml execute digit-tote-lift.urml.yaml \
  -m digit-tote-lift.manifest.yaml --profile home --no-policy
```

See the examples convention in [`/examples/README.md`](../README.md).
