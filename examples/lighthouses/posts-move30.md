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

# Move #30 post bodies: outreach to what we built for

Two targets, each backed by a shipped (Implemented) spec artifact. Post as a
GitHub **Discussion** (RFC-style intro) under idoco2003 once authorized. No
license-ask (both repos are Apache-2.0). AI-assisted-authoring disclosure up
front.

---

## RFC-0386: Autoware

**Post to:** https://github.com/autowarefoundation/autoware/discussions/new?category=ideas
**Title:** URML (open robot intent language): a validated intent layer above Autoware — request for comment

```
Hi Autoware community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: a person writes an English sentence, URML turns it into a typed primitive, validates it against the robot's declared capabilities and a safety envelope, then dispatches to whatever runs below. Autoware is named in URML's manifesto as a target, and URML's research-grade autonomous-vehicle profile was designed against Autoware's operational model, which is why I am writing.

Nothing here asks Autoware to adopt, host, or maintain anything. This is a request for comment, and genuinely a design question.

URML sits one layer above Autoware as a substrate-neutral, validated intent vocabulary. The mapping I shipped (urml.dev, RFC-0020):

- plan_path(from, to, along) is a compute verb that binds a planned trajectory; it maps onto the planning pipeline (mission -> behavior -> motion). It does not actuate.
- follow_trajectory(route, speed_envelope) is the only verb that actuates; it maps onto the control stack (pure_pursuit / MPC). The validator checks the trajectory's speed against the declared ODD cap, and that follow_trajectory consumes a plan_path-produced trajectory, before anything dispatches.
- A manifest av block declares the HD map (format-neutral; Lanelet2 is yours), the ODD, and the Minimum-Risk Maneuver.

URML is explicitly research-grade for AV (production_safety_certified: false). It does not certify autonomous-vehicle safety and makes no SOTIF / R157 claim; the value is an honest, validated, human-readable intent layer with a validate-before-actuate guarantee.

Three real questions: (1) Is the plan_path -> planning, follow_trajectory -> control mapping faithful to Autoware's architecture, or does it mis-model the mission/behavior/motion split? (2) What should a URML av manifest declare to honestly describe an Autoware deployment's ODD beyond a speed cap and regions? (3) Where is the right seam for a URML -> Autoware adapter: the trajectory ROS 2 interface, or higher?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0386-autoware-outreach.md

Thanks for Autoware; an open, production-aimed AV stack is exactly the kind of substrate a neutral intent layer should be able to sit above honestly.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0387: Eclipse S-CORE

**Post to:** https://github.com/eclipse-score/score/discussions/new?category=ideas
**Title:** URML (open robot intent language): a validated intent layer above S-CORE, and an ara::com binding — request for comment

```
Hi Eclipse S-CORE community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches to the substrate below. S-CORE is the open, service-oriented, AUTOSAR-Adaptive-aligned SDV core URML's AUTOSAR work targets, so let me be upfront about the layer: URML sits above S-CORE as a typed, validated intent vocabulary, not as a competing platform.

Nothing here asks S-CORE to adopt, host, or maintain anything. This is a request for comment.

The mapping I shipped (urml.dev, RFC-0019):

- A declared program can carry an ara::com binding (a service / instance / method id triple). call_program(name, args) is the verb; the validator checks the binding is complete and the args match the declared signature before dispatch. URML adds no AUTOSAR-specific primitive: service-method invocation rides the existing call_program, which is the substrate-neutral discipline URML holds itself to.
- A deployment's cyclic Execution-Management timing maps onto URML's realtime block (RFC-0016): MinimumCycleTime -> cyclic_period_ms, WatchdogTimeout -> watchdog_ms. URML never claims to enforce hard real-time; the field is a descriptive, internally-checked declaration.

Two real questions: (1) Is call_program plus an ara::com id triple the right granularity to name an S-CORE service method from an outside intent layer, or is a different handle more natural in your model? (2) Does mapping Execution-Management timing onto a descriptive realtime block (period + watchdog, no enforcement claim) read as honest from your side?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0387-eclipse-score-outreach.md

Thanks for S-CORE; an open, safety-minded SDV core built in the open is a genuinely good thing for the field.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```
