---
rfc: 0515
title: Roboflow Inference integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-13
updated: 2026-06-13
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

# RFC-0515: Roboflow Inference integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the AI / robot-learning wave (Move #46).

## Summary

[`roboflow/inference`](https://github.com/roboflow/inference) (Apache-2.0 core, ~2.3k stars, active) turns any computer or edge device into a vision inference server (detection, segmentation, VLMs). On a robot, perception feeds action, and that is exactly the handoff URML gates: a detection result becomes a fact a typed intent is conditioned on, and the action that follows is validated against the robot's declared capabilities and a safety envelope before dispatch. This RFC asks whether describing that seam is useful.

## The mapping (URML beside Roboflow Inference)

- **Perception in, validated action out.** Roboflow Inference produces typed perception outputs (detections, masks). URML consumes a perception result as the condition for a typed primitive, then validates the resulting action against the manifest and envelope before it reaches the robot. URML is the perception-to-action gate; it does not do the inference.
- **Declared perception capability.** A deployment's perception (the classes / models a Roboflow Inference server serves) maps toward a URML manifest's perception declaration, so a program that conditions on "detect the mug" is checkable.

## What is asked

Request for comment from the Roboflow Inference maintainers:

1. Is "Roboflow Inference perceives, URML validates the action it conditions" a sensible description of the perception-to-action handoff on a robot?
2. Could a served model's classes inform a URML perception capability declaration?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's perception capability declarations, the decide-then-do split (RFC-0002), and the perception-vendor engagements (Move #10). Part of Move #46.

## Implementation note

Outreach only. The post is a GitHub Issue on `roboflow/inference` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (the core is Apache-2.0; some bundled model directories carry their own licenses, which this RFC does not touch). Tracked in `examples/lighthouses/outreach-move46.yaml`.
