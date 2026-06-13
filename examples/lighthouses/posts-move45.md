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

# Move #45 post bodies: the middleware / control / drivers wave

Nine targets, all GitHub Issues. Post under idoco2003. No license-ask anywhere
(state the license if relevant, e.g. KickCAT CeCILL-C; never ask). AI-assisted-
authoring disclosure up front. Titles carry no em-dash.

Shared thesis: unlike the platforms wave (URML above a whole robot), these are
things URML *composes with*: a controller or planner it hands a validated goal
to, a transport/fieldbus beneath Layer-1, or a Layer-3 interop peer. URML stays
the decide layer (typed, statically-validated intent against a capability
manifest + safety envelope); the target stays the do layer.

---

## RFC-0501: Robot Raconteur (anchor)

**Post to (Issue):** https://github.com/robotraconteur/robotraconteur/issues/new
**Title:** URML (open robot intent language): validated intent dispatched over Robot Raconteur (request for comment)

```
Hi Robot Raconteur community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: a person's intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. URML is a layer above a transport, and Robot Raconteur is exactly the kind of transport a validated intent could be dispatched over -- so the two compose rather than compete.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

Two seams: (1) validate, then transport -- URML does the decide-then-do (turns intent into a typed primitive and validates it against the capability manifest + envelope), and the validated call then needs to reach the device, which Robot Raconteur's augmented-object services carry cleanly. (2) manifest from advertised services -- a Robot Raconteur service advertises typed members, which map toward a URML capability manifest, so the validator can check a program only invokes what the service actually exposes.

Two real questions: (1) is URML-validated intent dispatched over Robot Raconteur a sensible composition (URML validates; RR transports)? (2) Could a service's advertised members inform a URML capability manifest -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0501-robotraconteur-outreach.md

Thanks for Robot Raconteur; a transport-agnostic, typed-member framework is a natural place to ask where a validated-intent layer sits.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0502: mc_rtc

**Post to (Issue):** https://github.com/jrl-umi3218/mc_rtc/issues/new
**Title:** URML (open robot intent language): a validated whole-body goal layer above mc_rtc (request for comment)

```
Hi mc_rtc community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. mc_rtc is a real-time whole-body QP + FSM controller, and URML is interesting one layer above it: it hands mc_rtc a validated goal, while mc_rtc stays the thing that realizes it in real time.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: the robot mc_rtc controls declares its kinematic structure and stability limits as a URML `whole_body` manifest, plus its manipulators; URML validates an intent against that before anything is commanded, then hands the goal to mc_rtc's QP/FSM. URML is the decide layer (typed intent, validated against capabilities + envelope); mc_rtc is the do layer.

Two real questions: (1) does a URML `whole_body` manifest fit how mc_rtc models a robot's structure and limits? (2) Is a validated-intent layer that hands goals to the QP/FSM interesting, or already covered by the FSM-state interface -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0502-mc-rtc-outreach.md

Thanks for mc_rtc; a real-time whole-body controller is exactly the do layer a validated-intent gate wants to sit above.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0503: bipedal-locomotion-framework

**Post to (Issue):** https://github.com/gbionics/bipedal-locomotion-framework/issues/new
**Title:** URML (open robot intent language): a validated locomotion-goal layer above the bipedal-locomotion-framework (request for comment)

```
Hi,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. Your bipedal-locomotion-framework provides the MPC and whole-body control that keeps a humanoid balanced and moving, and URML is interesting one layer above: a locomotion intent validated against the robot's declared structure and stability limits, then handed to your MPC/WBC.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: the humanoid's kinematic structure and stability limits (center-of-mass bounds, support polygon) map onto a URML `whole_body` declaration; URML validates a locomotion intent against that envelope before it reaches the controller. URML decides (typed, validated intent); the framework does (the locomotion control).

Two real questions: (1) does a URML `whole_body` manifest match how this framework models the humanoid? (2) Is a validated-intent layer that hands locomotion goals to the MPC/WBC interesting -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0503-bipedal-locomotion-framework-outreach.md

Thanks for the framework; the MPC-plus-whole-body-control layer is exactly where a validated locomotion intent would hand off.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0504: hpp-core (Humanoid Path Planner)

**Post to (Issue):** https://github.com/humanoid-path-planner/hpp-core/issues/new
**Title:** URML (open robot intent language): declare goal + constraints, consume the trajectory from hpp-core (request for comment)

```
Hi Humanoid Path Planner community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent. Its relationship to a motion planner is deliberately narrow: URML does not plan. It declares the goal and the constraints, validates them against the robot's capabilities and a safety envelope, hands them to the planner, and consumes the trajectory the planner returns. hpp-core is exactly such a planner.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: a URML program declares a goal and the constraints it must satisfy; the validator confirms they are within the robot's declared capabilities and envelope; hpp-core computes the path; URML consumes the resulting trajectory (the same shape as URML's plan/follow-trajectory split). The robot's reach, joint limits, and geometry feed both the URML manifest and the planning problem, so the validated goal and the planner's problem definition agree. URML never re-implements planning.

Two real questions: (1) does the declare-goal-plus-constraints / consume-trajectory split fit how a caller drives hpp-core? (2) Could a URML capability manifest be a useful, validatable source for the planning constraints -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0504-hpp-core-outreach.md

Thanks for HPP; a clean planning core is exactly what URML wants to declare a problem to and consume a trajectory from.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0505: ros2_ros_bt_py

**Post to (Issue):** https://github.com/fzi-forschungszentrum-informatik/ros2_ros_bt_py/issues/new
**Title:** URML (open robot intent language): a validated-intent layer beside ros2_ros_bt_py (request for comment)

```
Hi ros2_ros_bt_py community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent. Its Layer-3 behavior composition (sequence / parallel / branch) is a peer to a behavior tree, so URML and ros2_ros_bt_py compose in either direction rather than compete.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

Two directions: (1) lower URML composition onto a ros2_ros_bt_py tree; or (2) a BT leaf calls a single URML primitive that is validated against the robot's capability manifest and envelope before it executes. Either way URML adds the typed, statically-validated intent, and your runtime stays the executor. The same declared intent can be a URML program or driven from a tree, with the capability/envelope check applied once.

Two real questions: (1) is lowering URML composition to a tree the more natural direction, or is BT-leaf-dispatches-a-validated-URML-primitive cleaner? (2) Is a static capability/envelope check on the actions a tree dispatches useful to your users -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0505-ros2-ros-bt-py-outreach.md

Thanks for ros2_ros_bt_py; the web-GUI BT plus a clean node model is a natural place to ask where a validated-intent layer fits.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0506: libcyphal (Cyphal)

**Post to (Issue):** https://github.com/OpenCyphal-Garage/libcyphal/issues/new
**Title:** URML (open robot intent language): where a validated actuation command meets the Cyphal bus (request for comment)

```
Hi OpenCyphal community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. URML is a layer well above a wire protocol, and Cyphal is one of the low-level transports a validated actuation command ultimately rides. I wanted to describe that layering and ask whether it is the right altitude to engage.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The layering: URML's Layer-1 hardware abstraction sits above the bus. Once an actuation command has passed the capability/envelope check, it reaches an actuator node over a transport like Cyphal. URML does not replace the bus; it is the typed, statically-validated intent above it. Separately, Cyphal's registered, versioned DSDL types are a clean declarative source a URML capability manifest could reference for what a node actually exposes.

Two real questions: (1) is "URML validates intent, then dispatches to a Cyphal node" a sensible description of the layering? (2) Could Cyphal's typed DSDL interfaces inform a URML manifest for an actuator node -- and is the protocol the right altitude to engage, or is the integrator level the better seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0506-libcyphal-outreach.md

Thanks for Cyphal; the versioned, typed interface model is exactly the kind of declarative substrate a capability manifest likes to reference.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0507: KickCAT (EtherCAT)

**Post to (Issue):** https://github.com/leducp/KickCAT/issues/new
**Title:** URML (open robot intent language): where validated actuation meets the EtherCAT master (request for comment)

```
Hi KickCAT community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. EtherCAT is the fieldbus beneath the actuation layer in many industrial and legged systems, and KickCAT is an open master/slave stack for it. I wanted to describe how URML layers above that and ask whether it is the right altitude.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The layering: URML's actuation primitives are validated statically (pre-dispatch); the realized motion reaches the servo drives over EtherCAT, where KickCAT is the master doing the cyclic exchange. URML is the typed, pre-dispatch-validated intent; KickCAT is the deterministic transport to the drives. This mirrors URML's existing ros2_control hardware-abstraction mapping, one layer lower. (KickCAT is CeCILL-C; this proposes no code reuse, only a layering description.)

Two real questions: (1) is "URML validates actuation intent above, KickCAT carries it to the drives over EtherCAT" an accurate description? (2) Is a fieldbus master the right altitude to engage, or is the integrator / ros2_control layer the better seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0507-kickcat-outreach.md

Thanks for KickCAT; an open EtherCAT master is a clean reference point for where the validated-intent layer ends and the deterministic bus begins.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0508: Husarion UGV (husarion_ugv_ros)

**Post to (Issue):** https://github.com/husarion/husarion_ugv_ros/issues/new
**Title:** URML (open robot intent language): an English front door above the Husarion Panther / Lynx stack (request for comment)

```
Hi Husarion community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: "go to the loading bay" becomes a typed `move_to`, validated against the robot's declared mobility and the deployment's locations, then dispatched onto the existing ROS 2 stack. For a concrete UGV like Panther / Lynx, URML is interesting as the natural-language front door above your driver stack -- it adds a capability/envelope gate and a typed intent record, it does not replace your control.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: Panther / Lynx mobility (drive type, velocity limits) and the deployment's named locations and frames map onto a URML manifest; a `move_to(location)` is validated against it before dispatch. The URML-side next step would be a HusarionAdapter targeting the published ROS 2 packages, CI-gated, with hardware validation deferred -- the established URML adapter pattern.

Two real questions: (1) does mapping a Panther / Lynx UGV (mobility, velocity limits, locations) onto a URML manifest read right? (2) Is an English-to-validated-`move_to` front door above husarion_ugv_ros interesting -- and which is the cleaner first seam, the manifest mapping or a HusarionAdapter?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0508-husarion-ugv-outreach.md

Thanks for husarion_ugv_ros; a clean ROS 2 stack for a real UGV is a great fit for the English-front-door path.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0509: FCL (Flexible Collision Library)

**Post to (Issue):** https://github.com/flexible-collision-library/fcl/issues/new
**Title:** URML (open robot intent language): declared clearances above, FCL's geometric check below (request for comment)

```
Hi FCL community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent. It declares clearances and spatial constraints in a safety envelope; it does not compute geometry. FCL is exactly the kind of library a runtime uses downstream to check the constraints URML declares, so I wanted to describe that division of labor and ask whether it is the right altitude.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The division of labor: a URML safety envelope declares clearance volumes and spatial constraints (a lateral footprint, a vertical band; URML's cross-robot deconfliction model). When a runtime needs to verify a motion or a fleet separation against actual geometry, FCL's collision/distance queries are the computation behind that check. URML is the declarative, statically-auditable constraint; FCL is the geometric test. URML stays a declaration layer; the heavy query stays in a dedicated library.

Two real questions: (1) is "URML declares the clearance / spatial constraint, FCL is the geometric query that enforces it" an accurate and useful division of labor? (2) Is a collision library the right altitude to describe this, or is the seam better drawn at a planner / MoveIt-style layer that already wraps FCL?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0509-fcl-outreach.md

Thanks for FCL; it is the geometric-query layer beneath much of this ecosystem, which is exactly why the clearances-versus-check division is worth naming.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```
