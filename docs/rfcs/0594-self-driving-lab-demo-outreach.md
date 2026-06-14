---
rfc: 0594
title: Self-Driving Lab Demo integration — request for comment
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

# RFC-0594: Self-Driving Lab Demo integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the lab-automation wave (Move #54); the teaching corner.

## Summary

[`sparks-baird/self-driving-lab-demo`](https://github.com/sparks-baird/self-driving-lab-demo) (MIT) is an accessible reference and teaching framework for self-driving laboratories: low-cost closed-loop demos that optimize, then actuate, then measure. Because it is built to teach the autonomous-lab loop, it is a good place to make the validated-intent step explicit for learners. This RFC asks whether that is worthwhile.

## The relationship (URML beside the Self-Driving Lab Demo)

- **Making the validated step visible.** The demo runs a closed loop: choose the next experiment, run it on hardware, read the result. URML's angle is the "run it on hardware" step: declare the action as typed intent, validate it against the demo rig's declared capabilities and limits, then dispatch. For a learner, seeing why an out-of-range action is refused is exactly the kind of thing a teaching framework can make vivid.
- **A natural-language on-ramp.** URML's Layer 4 lets a demo start from a plain-language instruction and show how it becomes a checked, runnable action, which suits an educational setting.

## What is asked

1. Is a typed, validated intent step (the actuation checked against the rig's declared capabilities) a useful thing to make explicit in a teaching self-driving-lab loop?
2. Does showing the natural-language to validated-intent path add pedagogical value here?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's Layer-4 natural-language grammar, the capability manifest, the educational profile (RFC-0011), and the decide-then-do split (RFC-0002). Part of Move #54; the educational self-driving-lab target of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `sparks-baird/self-driving-lab-demo` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move54.yaml`.
