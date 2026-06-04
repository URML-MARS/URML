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

# Move #29 post bodies: open humanoid / legged robots (round 2)

Copy-paste-ready bodies for the 9 Tier-A targets. PRC-domiciled hardware-vendor
stacks (Unitree, RobotEra) are deferred with cause in
[`outreach-move29.yaml`](outreach-move29.yaml), not posted.

Shared framing, in every body: URML describes intent and declares a platform's
capability, but its `mobility.drive_type` enum has no legged / bipedal /
quadruped class and no whole-body shape, so these are partly a genuine design
conversation about what a humanoid / legged capability declaration should
contain. URML composes above the platform (intent + validated capability -> the
locomotion stack -> joints); the locomotion controller (learned policy or MPC) is
the substrate. The bodies are honest that URML can only describe a humanoid
coarsely today.

**No body contains a license-clarification ask** (per the 2026-06-03 guidance).

Bodies follow the [AGENTS.md](../../AGENTS.md) rules: concrete hook, "nothing for
you to maintain" up front, one or two real questions, RFC linked as optional
depth, under a two-minute read, zero em-dashes. VIBE disclosure line last.

All 9 repos have Issues enabled (verified 2026-06-04), so each is a single Issue.

**Posting status:** DRAFTED, not yet posted. Post under `idoco2003` only after
RFCs 0372-0380 land on `main`. Then fill `sent_at` / `posted_url` per row and
refresh `outreach.db`.

**Routing summary**

| RFC | Target | Channel | Status |
|---|---|---|---|
| 0372 | ToddlerBot | Issue on `hshi74/toddlerbot` | Drafted (post after merge) |
| 0373 | Open Duck Mini | Issue on `apirrone/Open_Duck_Mini` | Drafted (post after merge) |
| 0374 | K-Scale (ksim) | Issue on `kscalelabs/ksim` | Drafted (post after merge) |
| 0375 | PAL TALOS | Issue on `pal-robotics/talos_robot` | Drafted (post after merge) |
| 0376 | legged_gym | Issue on `leggedrobotics/legged_gym` | Drafted (post after merge) |
| 0377 | rsl_rl | Issue on `leggedrobotics/rsl_rl` | Drafted (post after merge) |
| 0378 | DIAL-MPC | Issue on `LeCAR-Lab/dial-mpc` | Drafted (post after merge) |
| 0379 | legged_control | Issue on `qiayuanl/legged_control` | Drafted (post after merge) |
| 0380 | rl_games | Issue on `Denys88/rl_games` | Drafted (post after merge) |

---

## RFC-0372: ToddlerBot

**Post to:** https://github.com/hshi74/toddlerbot/issues/new
**Title:** URML (open robot intent language): what should a bipedal-humanoid capability declaration contain? request for comment

```
Hi ToddlerBot maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent. A person writes an English sentence, URML turns it into a typed primitive, validates it against the robot's declared capabilities and a safety envelope, then dispatches. ToddlerBot is exactly the kind of accessible open humanoid I want URML to describe well, and it has exposed a real gap, which is why I am writing.

Nothing here asks ToddlerBot to change or maintain anything. This is a request for comment, and genuinely a design question.

URML's capability manifest describes mobility with a fixed set of drive types (wheeled, tracked, multirotor, and so on). A bipedal humanoid with arms fits none of them, and URML has no whole-body shape yet. So: what should a minimal but honest bipedal-humanoid capability declaration contain, from the perspective of someone who built one? A legged mobility class, whole-body kinematic structure, balance or stability constraints, the split between locomotion and manipulation? And where should the boundary sit between a URML intent (go to the kitchen, pick that up) and ToddlerBot's own policy stack?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0372-toddlerbot-outreach.md

Thanks for making a real humanoid something a lab or a person can actually build.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0373: Open Duck Mini

**Post to:** https://github.com/apirrone/Open_Duck_Mini/issues/new
**Title:** URML (open robot intent language): declaring a small biped whose walk is a learned policy, request for comment

```
Hi Open Duck Mini maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an English sentence becomes a typed primitive, validated against a robot's declared capabilities and a safety envelope, then dispatched. Open Duck Mini is a lovely small open biped, and it sits right on a question URML needs to answer well.

Nothing here asks Open Duck Mini to change or maintain anything. This is a request for comment.

Two real questions. First, the walk is a learned policy, so where is the line between what URML declares as capability (the platform can locomote, within these limits) and what the policy owns (how it steps)? URML would bound a navigation-level intent and let the policy realize it, but I want to get that division right rather than assume it. Second, URML has no legged mobility class today (its drive types are all wheeled or flying); what would a small-biped capability declaration most need to carry to be useful rather than decorative?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0373-open-duck-mini-outreach.md

Thanks for Open Duck Mini; an open BDX-style biped people can actually build is a real contribution.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0374: K-Scale Labs

**Post to:** https://github.com/kscalelabs/ksim/issues/new
**Title:** URML (open robot intent language): where would a validated-intent layer sit in the K-Scale stack? request for comment

```
Hi K-Scale team,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an English sentence becomes a typed primitive, validated against a robot's declared capabilities and a safety envelope, then dispatched. You are building a fully open humanoid stack, ksim for training and kos for the onboard runtime, which is a rare and useful thing to be able to reason about end to end.

Nothing here asks K-Scale to change or maintain anything. This is a request for comment.

Two real questions. First, where would a validated-intent layer naturally sit relative to kos as the runtime: above it, handing kos validated, in-capability commands? Second, could a URML capability manifest align with, or be derived from, a K-Scale robot definition, so the declaration and the real robot cannot drift? Underlying both: URML has no legged or whole-body capability class yet, and a humanoid stack like yours is exactly where I would want to design that with input rather than guess. ksim or kos, whichever is the right surface for this, point me.

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0374-kscale-outreach.md

Thanks for building the humanoid stack in the open; very few are.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0375: PAL Robotics TALOS

**Post to:** https://github.com/pal-robotics/talos_robot/issues/new
**Title:** URML (open robot intent language): declaring a full-size humanoid (TALOS), request for comment

```
Hi PAL Robotics team,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an English sentence becomes a typed primitive, validated against a robot's declared capabilities and a safety envelope, then dispatched. I reached out earlier about TIAGo (a wheeled mobile manipulator); TALOS is the legged, full-size sibling, and it raises a capability-declaration question at OEM scale that I would value your read on.

Nothing here asks PAL to change or maintain anything. This is a request for comment.

URML composes above a robot's ROS stack: it validates an in-capability, in-envelope request, then dispatches to the controllers. For TALOS that runs into a gap: URML's mobility model has no legged class and no whole-body (legs plus arms, balance) shape. Two real questions. First, what should a URML manifest declare for a full-size torque-controlled humanoid so a request can be validated honestly (legged mobility, whole-body limits, balance constraints)? Second, where should the boundary sit between a URML intent and PAL's whole-body controller, so URML stays the intent layer and does not duplicate control?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0375-pal-talos-outreach.md

Thanks for keeping TALOS's stack open; a full-size humanoid you can actually program against is rare.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0376: legged_gym

**Post to:** https://github.com/leggedrobotics/legged_gym/issues/new
**Title:** URML (open robot intent language): bounding a legged_gym-trained locomotion policy, request for comment

```
Hi legged_gym maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. legged_gym is where a remarkable number of quadruped and humanoid walk policies are trained, and a trained policy is exactly the kind of thing URML would treat as a locomotion substrate: URML declares the platform's capability and bounds a navigation-level intent the policy must satisfy, while the policy owns the gait.

Nothing here asks legged_gym to change or maintain anything. This is a request for comment.

Two real questions. First, what is the right URML granularity above a velocity-tracking locomotion policy: navigation-level commands (go to X, walk at velocity V, turn), or something finer? Second, URML has no legged mobility class today; for a platform whose locomotion is a legged_gym-trained policy, what should the manifest declare as capability versus leave to the policy? I am reaching the rsl_rl maintainers separately about the library underneath.

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0376-legged-gym-outreach.md

Thanks for legged_gym; it is the on-ramp for a huge amount of legged-locomotion work.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0377: rsl_rl

**Post to:** https://github.com/leggedrobotics/rsl_rl/issues/new
**Title:** URML (open robot intent language): could a trained policy export the limits it was trained under? request for comment

```
Hi rsl_rl maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. rsl_rl is the RL library underneath legged_gym and Isaac Lab legged training, which puts it a layer below where URML normally talks, so let me be upfront about the boundary: URML talks to the trained policy or the platform, not to the trainer.

Nothing here asks rsl_rl to change or maintain anything. This is a request for comment on one specific idea.

A policy trained with rsl_rl was trained under assumptions: command ranges, velocity and torque limits, terrain. Those are exactly what URML's capability manifest and safety envelope try to declare on the outside. So the real question: would it be sensible and feasible for a trained policy to carry, or export, the capability and limits it was trained under, so a URML manifest can stay consistent with what the policy will actually do safely, rather than a human restating it and drifting? And where, if anywhere, is the natural place for that metadata to live?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0377-rsl-rl-outreach.md

Thanks for rsl_rl; fast, clean on-policy RL for legged robots is load-bearing for the field.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0378: DIAL-MPC

**Post to:** https://github.com/LeCAR-Lab/dial-mpc/issues/new
**Title:** URML (open robot intent language): a validated intent into a DIAL-MPC task, request for comment

```
Hi DIAL-MPC maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. DIAL-MPC is interesting to URML precisely because it is training-free: a real-time legged whole-body controller, a clean contrast to the learned-policy stacks. URML would declare the platform's capability and a task-level intent; DIAL-MPC realizes the whole-body motion; URML validates the request is admissible first.

Nothing here asks DIAL-MPC to change or maintain anything. This is a request for comment.

Two real questions. First, what is the cleanest boundary for "URML intent plus capability -> a DIAL-MPC task or cost", and how would URML's declared limits become constraints the controller respects? Second, from your point of view, does a training-free MPC change what URML should declare compared to a learned policy (no training-time assumptions to carry, but tuning and cost structure instead)? For context, I am also reaching OCS2 about general switched-system MPC and legged_gym about the learned-policy side.

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0378-dial-mpc-outreach.md

Thanks for DIAL-MPC; training-free real-time whole-body control is a genuinely refreshing direction.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0379: legged_control

**Post to:** https://github.com/qiayuanl/legged_control/issues/new
**Title:** URML (open robot intent language): a navigation intent into an MPC+WBC legged stack, request for comment

```
Hi legged_control maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. legged_control is a complete MPC plus whole-body-control stack for quadrupeds and humanoids, built on OCS2, which makes it a natural locomotion substrate for a URML-governed legged robot: URML declares capability and a navigation-level intent, legged_control realizes it, URML validates admissibility first.

Nothing here asks legged_control to change or maintain anything. This is a request for comment.

Two real questions. First, what is the cleanest boundary for "URML navigation intent plus capability -> the MPC+WBC stack", and how should URML's declared limits map onto the controller's constraints? Second, since you build on OCS2 (which I engaged separately), where would you draw the line for a URML integration: at legged_control's higher-level interface, or lower? URML has no legged mobility class yet, and a complete stack like yours is a good place to figure out what the manifest should carry.

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0379-legged-control-outreach.md

Thanks for legged_control; a complete, readable MPC+WBC stack lowered the barrier for a lot of people.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0380: rl_games

**Post to:** https://github.com/Denys88/rl_games/issues/new
**Title:** URML (open robot intent language): could a trained policy carry its capability envelope? a boundary check

```
Hi rl_games maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. rl_games trains a great many of the Isaac-based locomotion and manipulation policies that end up being the controller a robot actually runs, which puts it below the layer URML talks to. So let me be honest about the boundary: URML talks to the trained policy or the platform, not to the trainer.

Nothing here asks rl_games to change or maintain anything. This is a boundary check plus one real question.

The question is the same one I am asking rsl_rl: a policy trained with rl_games was trained under command ranges and limits that are exactly what URML's capability manifest and safety envelope try to declare from the outside. Would it be feasible for a trained policy (or its config) to carry those assumptions in a readable form, so a URML manifest can stay consistent with what the policy will actually do, instead of a human transcribing and drifting? I am genuinely unsure where that metadata best lives, and you have the clearest view of the training side.

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0380-rl-games-outreach.md

Thanks for rl_games; the throughput it unlocked changed what is trainable.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## Correction comments (2026-06-04)

The "URML has no legged / bipedal / quadruped class" framing above is **false**:
`biped` and `quadruped` have been in `mobility.drive_type` since RFC-0009
(Implemented 2026-05-19). The error came from reading a drifted Layer-1 spec
doc (reconciled in the RFC-0010 build). The whole-body manipulation half of the
queued work then shipped as RFC-0010 (Implemented 2026-06-04).

**Post the correction below to the 6 threads that carried the claim**, AFTER
RFC-0010 (PR #308) lands on `main` so the RFC-0010 reference is live:

- RFC-0372 ToddlerBot — https://github.com/hshi74/toddlerbot/issues/19
- RFC-0373 Open Duck Mini — https://github.com/apirrone/Open_Duck_Mini/issues/47
- RFC-0374 K-Scale Labs — https://github.com/kscalelabs/ksim/issues/539
- RFC-0375 PAL TALOS — https://github.com/pal-robotics/talos_robot/issues/9
- RFC-0376 legged_gym — https://github.com/leggedrobotics/legged_gym/issues/98
- RFC-0379 legged_control — https://github.com/qiayuanl/legged_control/issues/85

**No correction needed** (these posts never made the false claim; they ask
about the policy/MPC boundary): RFC-0377 rsl_rl, RFC-0378 DIAL-MPC,
RFC-0380 rl_games.

Reusable comment text:

```
A correction to my message above, in the interest of accuracy.

I overstated the gap. URML does have legged mobility classes today: `mobility.drive_type` includes `biped` and `quadruped` (shipped in RFC-0009). So "no legged mobility class" was wrong, and I apologize for the inaccuracy.

The whole-body piece I described as queued has since landed too: RFC-0010 adds two-arm / bimanual manipulation (an `arm` selector on grasp/release and a `bimanual` primitive).

What remains genuinely open, and what I would still value your view on, is the richer whole-body capability shape: whole-body kinematic structure and balance / stability constraints in the manifest, and where the boundary should sit between a URML intent and your locomotion / control stack. That question stands.

Ido Yahalomi (URML, greenvh@gmail.com)
```
