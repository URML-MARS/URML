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

# SPEC-GAPS — urml-cobot-runtime

Per the spec-gap protocol (RFC-0014): built strictly against the
frozen substrate Protocol. Needs the cobots surfaced are recorded
here; only the genuinely inexpressible become RFC Drafts for
maintainer decision — never a silent primitive/schema change.

## Genuinely inexpressible → RFC Draft filed

- **RFC-0017 — digital-I/O actuation.** Cobots fire end-effectors and
  signal PLCs by writing raw digital-output pins (UR `setStandardDigitalOut`,
  Franka FCI I/O, **Doosan DRFL DO, Techman TMflow `set_digital_output`,
  Kinova Kortex GPIO**). A raw DO write is not `grasp` (it may be a glue
  gun, a blow-off, a conveyor handshake), not `report`, and not a station
  service (so RFC-0013's `swap_tool`-rides-`send_docking_goal`
  precedent does not apply). No existing primitive composes it. Filed
  as RFC-0017 (Draft); until decided, the adapters do not expose raw
  I/O and `grasp`/`release` remain the only effector verbs. Track B's
  three new adapters (Doosan, Techman, Kinova) all surface the **same**
  gap as UR/Franka — cross-referenced here; **no new RFC**.

## Composable / watch-item (no RFC)

- **Force/impedance (item C).** `send_manipulation_goal` already
  carries scalar `force_n`, honoured at v0.1 fidelity (mirrors
  RFC-0013's "advisory in v0.1" stance for `place_at.height`). A full
  parametric stiffness/impedance matrix is finer than v0.1 needs;
  recorded as a **watch-item** for the maintainer to weigh later, not
  an RFC now.
- **Joint-space waypoints (item E).** Absorbed by config-side
  `CobotConfig.location_to_pose` (the px4 `location_to_pose` pattern):
  a named manifest location resolves to a 6/7-DoF vector in
  `cobot_adapter.yaml`. No URML surface change — documented, not a gap.

## Note

This is a NEW package, deliberately not a change to
`industrial-arm-runtime` (whose `Ur/FrankaAdapter` compose
`RclpyAdapter`, i.e. ROS 2 + MoveIt 2). Touching those would break the
zero-ROS acid test and the "don't modify existing adapters/Protocol"
rule; the ROS-free siblings live here, exactly as `marine-runtime` is
the ROS-free sibling of `ros2-runtime`.
