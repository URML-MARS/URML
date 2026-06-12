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

# Move #43 post bodies: the reinforcement-learning / policy-training wave

Six targets. Three GitHub Issues (stable-baselines3, mushroom-rl, ray/RLlib) and
three GitHub Discussions in the Ideas category (cleanrl, skrl, torchrl). Post
under idoco2003. No license-ask (all permissive: MIT / Apache-2.0).
AI-assisted-authoring disclosure up front. For the Discussion targets, query the
category id at post time (skrl also has a Sim2Real category, the natural
alternative to Ideas).

The shared thesis (RFC-0383 LearnedPolicy + RFC-0002 decide-then-do): a policy
trained in your framework is deployed on a robot; URML carries its training
envelope (obs/action spaces + domain bounds) as a typed declaration and validates
each proposed action against the robot's declared capabilities + a safety envelope
before dispatch. The policy decides; URML does.

---

## RFC-0485: Stable-Baselines3 (anchor)

**Post to (Issue):** https://github.com/DLR-RM/stable-baselines3/issues/new
**Title:** URML (open robot intent language): declaring a trained policy's deployment envelope (request for comment)

```
Hi Stable-Baselines3 community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent is turned into a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. A trained SB3 policy is a function from an observation space to an action space, trained inside a specific domain, and URML is interesting to that policy at the moment it's deployed on a robot, in a way that doesn't compete with SB3.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML has a "LearnedPolicy" declaration: a manifest can say "this capability is served by a learned policy trained within these bounds." Two seams for SB3: (1) envelope export -- a trained policy already knows its observation_space / action_space (Gymnasium Box/Discrete), and a VecNormalize wrapper knows the obs/return statistics it saw; those are exactly the bounds a URML deployment envelope wants, emitted as a small artifact next to the saved model. (2) validated deployment -- with the envelope declared, URML sits between the SB3 policy and the robot and checks each proposed action against the robot's declared capabilities + the active safety envelope before dispatch; the policy decides, URML is the typed gate that does.

Two real questions: (1) Does exporting a trained policy's spaces (and VecNormalize bounds) as a declared deployment envelope make sense as an optional artifact? (2) Is a validated-intent gate between an SB3 policy and a real robot interesting, or already covered by something you'd recommend -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0485-stable-baselines3-outreach.md

Thanks for SB3; it's the reference RL library for a huge number of people, which is exactly why the deployment-envelope question is worth asking here first.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0486: CleanRL

**Post to (Discussion, Ideas category):** https://github.com/vwxyzjn/cleanrl/discussions/new?category=ideas
**Title:** URML (open robot intent language): a single-file example for declaring a trained policy's deployment envelope (request for comment)

```
Hi CleanRL community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. CleanRL's single-file clarity is exactly why it's an interesting place to ask URML's question: when a policy trained by a single-file PPO/SAC is deployed on a robot, what declares the bounds it was trained inside, and what checks a deployment stays within them?

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML has a "LearnedPolicy" declaration for exactly this. Two seams: (1) a single-file envelope example -- a CleanRL script knows its single_observation_space / single_action_space and the domain it trained in; a few lines emitting a URML deployment envelope (obs/action ranges + training-domain bounds) next to the saved weights would be a clean, copy-pasteable reference for "how do I declare what my policy was trained for." (2) validated deployment -- URML then sits between the trained policy and the robot, checking each proposed action against declared capabilities + the safety envelope before dispatch.

Two real questions: (1) Would a single-file example that emits a URML deployment envelope alongside a trained policy be a useful reference for the deployment side? (2) Is the validated-deployment gate interesting, or out of scope for a single-file-algorithms project -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0486-cleanrl-outreach.md

Thanks for CleanRL; the single-file philosophy is the reason this would make such a clean worked example.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0487: skrl

**Post to (Discussion, Ideas category; Sim2Real is the natural alternative):** https://github.com/Toni-SM/skrl/discussions/new?category=ideas
**Title:** URML (open robot intent language): a typed sim2real deployment envelope for trained policies (request for comment)

```
Hi skrl community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. skrl's Isaac Lab / sim2real focus (you even keep a dedicated Sim2Real discussion category) is exactly where URML's question lives: a policy trained in a simulated domain has bounds it must not be trusted outside of on the real robot.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML has a "LearnedPolicy" declaration built for this. Two seams: (1) the sim2real envelope -- a skrl policy trained in Isaac Lab knows its observation/action spaces and the simulated domain it saw; declaring that as a URML deployment envelope makes the sim-to-real boundary a typed, checkable artifact rather than an implicit assumption, so the validator can refuse to dispatch the policy outside the domain it trained for. (2) validated deployment -- URML sits between the trained policy and the real robot, checking each proposed action against declared capabilities + the safety envelope before dispatch; on a sim2real deployment, that gate is where an out-of-distribution action gets caught before it reaches hardware.

Two real questions: (1) For a sim2real deployment, is a declared envelope (the simulated training domain a policy must stay within on the real robot) a useful typed artifact to emit alongside a trained skrl agent? (2) Is the validated-deployment gate interesting for the real-robot side of sim2real -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0487-skrl-outreach.md

Thanks for skrl; the explicit sim2real framing is what makes this a natural fit.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0488: TorchRL

**Post to (Discussion, Ideas category):** https://github.com/pytorch/rl/discussions/new?category=ideas
**Title:** URML (open robot intent language): mapping TensorSpec to a deployment envelope (request for comment)

```
Hi TorchRL community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. TorchRL's primitive-first design and its TensorSpec types (which describe observation/action specs precisely) are a natural match for URML's typed view of the world.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML has a "LearnedPolicy" declaration: a manifest can say "this capability is served by a learned policy trained within these bounds." Two seams: (1) spec to envelope -- a TorchRL policy carries TensorSpec observation/action specs (bounds, shapes, dtypes), which map almost directly onto a URML deployment envelope (obs/action ranges + training-domain bounds); the export is a thin adapter from TensorSpec to the URML declaration. (2) validated deployment -- URML then sits between the trained policy and the robot, checking each proposed action against declared capabilities + the safety envelope before dispatch.

Two real questions: (1) Does mapping a policy's TensorSpec specs onto a declared deployment envelope make sense as an optional export? (2) Is the validated-deployment gate interesting for the robot-deployment side of TorchRL -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0488-torchrl-outreach.md

Thanks for TorchRL; the primitive-first stance is part of why the mapping feels clean.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0489: MushroomRL

**Post to (Issue):** https://github.com/MushroomRL/mushroom-rl/issues/new
**Title:** URML (open robot intent language): MDPInfo as a trained-policy deployment envelope (request for comment)

```
Hi MushroomRL community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. MushroomRL's clean MDPInfo names the observation and action spaces of every environment, which is exactly the structure URML's deployment question needs.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML has a "LearnedPolicy" declaration: a manifest can say "this capability is served by a learned policy trained within these bounds." Two seams: (1) MDPInfo to envelope -- an agent's MDPInfo declares the observation/action spaces it trained against; emitting those (plus the training-domain bounds) as a URML deployment envelope makes "what was this policy trained for" a typed, checkable artifact rather than tacit knowledge. (2) validated deployment -- URML then sits between the trained policy and the robot, checking each proposed action against declared capabilities + the safety envelope before dispatch.

Two real questions: (1) Does exporting an agent's MDPInfo spaces (plus training-domain bounds) as a declared deployment envelope make sense as an optional artifact? (2) Is the validated-deployment gate interesting, or already covered elsewhere -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0489-mushroom-rl-outreach.md

Thanks for MushroomRL; the explicit MDPInfo structure is what makes this mapping straightforward.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0490: Ray RLlib

**Post to (Issue, scoped to RLlib):** https://github.com/ray-project/ray/issues/new
**Title:** URML (open robot intent language): a validated deployment envelope for RLlib policies (request for comment)

```
Hi RLlib community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. This is scoped to RLlib and its deployment story, not to Ray's distributed-compute core. An RLlib-trained policy is deployed to act on a system, and URML's question is the same one this applies everywhere: what declares the bounds the policy was trained inside, and what validates that a deployment stays within them?

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML has a "LearnedPolicy" declaration for exactly this. Two seams: (1) policy to envelope -- an RLlib Policy knows its observation/action spaces and the environment domain it trained against; emitting those as a URML deployment envelope (obs/action ranges + training-domain bounds) makes the deployment boundary a typed, checkable artifact. (2) validated deployment -- when an RLlib policy is served to control a robot, URML sits between the policy and the hardware, checking each proposed action against declared capabilities + the safety envelope before dispatch; this complements a serving layer, it doesn't replace it.

Two real questions: (1) Does exporting an RLlib policy's spaces (plus training-domain bounds) as a declared deployment envelope make sense? (2) For an RLlib policy serving a robot, is a validated-intent gate interesting, or already addressed by a pattern you'd recommend -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0490-ray-rllib-outreach.md

Thanks for RLlib. To be clear, the ask is scoped to RLlib, not Ray core.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```
