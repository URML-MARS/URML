---
rfc: 0606
title: PyElastica (and gym-softrobot) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-14
updated: 2026-06-14
supersedes: —
superseded-by: —
---

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

# RFC-0606: PyElastica (and gym-softrobot) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the soft-robotics / assistive wave (Move #57). One RFC for PyElastica and the gym-softrobot RL environment built on it.

## Summary

[`GazzolaLab/PyElastica`](https://github.com/GazzolaLab/PyElastica) (MIT, UIUC) is a Cosserat-rod simulation framework for slender, soft, and muscular structures, and [`skim0119/gym-softrobot`](https://github.com/skim0119/gym-softrobot) (MIT) wraps it as reinforcement-learning environments for soft-robot control. URML relates to both at the intent layer: it does not simulate and it does not train, but it can declare the control goal and operating envelope, and (for the learned-policy case) check a policy against the envelope it was trained for before that policy is trusted to drive. This RFC asks whether the mapping is useful.

## The relationship (URML beside PyElastica / gym-softrobot)

- **Simulation and training below, declared intent above.** PyElastica simulates the soft structure; gym-softrobot trains a control policy on it. URML's contribution, if any, is a typed declaration of the control goal plus the admissible envelope, sitting above either. URML does not simulate; it declares and checks.
- **A policy that declares its envelope.** gym-softrobot produces trained policies, and URML's LearnedPolicy direction (RFC-0383) is the idea that a trained policy declares the operating envelope it was trained for, so an intent can be validated against it before the policy is deployed on a real soft robot rather than in sim. That is the more interesting of the two seams.

## What is asked

1. Is a typed declaration of a soft-robot control goal + envelope useful above PyElastica / gym-softrobot, or is that already implicit in the environment definition?
2. Could a gym-softrobot-trained policy declare a training/operating envelope a URML intent is checked against (RFC-0383)?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's decide-then-do split (RFC-0002), the LearnedPolicy envelope (RFC-0383), and the safety-envelope validation. Part of Move #57; the soft-robot simulation + RL target of the wave.

## Implementation note

Outreach only. The post is a single GitHub Issue on `GazzolaLab/PyElastica` (referencing gym-softrobot) under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move57.yaml`.
