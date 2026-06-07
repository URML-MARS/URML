---
rfc: 0459
title: urdf-loaders (NASA JPL) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-07
updated: 2026-06-07
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

# RFC-0459: urdf-loaders (NASA JPL) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's capability-manifest model and its relationship to robot-description formats.

## Summary

[`gkjohnson/urdf-loaders`](https://github.com/gkjohnson/urdf-loaders) (Apache-2.0, ~792 stars, active; NASA JPL / Caltech) provides URDF loaders for THREE.js and Unity — the dominant way URDF robots are visualized on the web. A web-facing URDF consumer is a natural place to discuss showing a robot's *capabilities and safety envelope* alongside its visualized structure, and to ask how a capability manifest should relate to the loaded URDF. This RFC asks that.

## The mapping (URML manifest alongside a loaded URDF)

URML's manifest sits alongside the visualized robot description:

- urdf-loaders renders a URDF in the browser / Unity; a URML manifest declares capabilities and a safety envelope for that same robot. A viewer could surface the manifest's declared workspace, reach, and no-go regions over the rendered model.
- Some manifest fields (reach, DOF, joint limits) could be read directly from the loaded URDF; others (payload, graspable classes, safety envelope) are declared separately.
- The split: the loaded URDF says what the robot *looks like and is*; the URML manifest says what it is *allowed and able to do*.

## What is asked

Request for comment from the urdf-loaders maintainers:

1. Is visualizing a robot's declared capabilities / safety envelope alongside the URDF interesting for the web-robotics use case?
2. Which manifest fields can be read directly from the loaded URDF, and which need separate declaration?
3. Where should the boundary sit between visualized description and capability + safety declaration?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability-manifest model (Layer-1 HAL); the robot-description anchor (RFC-0455). urdf-loaders is the web-visualization vertex of the robot-description wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `gkjohnson/urdf-loaders` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move39.yaml`.
