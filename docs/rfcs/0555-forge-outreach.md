---
rfc: 0555
title: Forge (robot-data converter) integration — request for comment
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

# RFC-0555: Forge (robot-data converter) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the robot-data sub-cluster of the HRI / conversational / robot-data wave (Move #50).

## Summary

[`arpitg1304/forge`](https://github.com/arpitg1304/forge) (MIT) converts between robot-learning data formats (RLDS, LeRobot, rosbag and friends). URML is interesting as an *annotation* source for these datasets: its validated-intent audit records say, in typed form, what the robot was instructed to do and whether it was admissible, which is exactly the kind of label robot-learning datasets are usually missing. This RFC asks whether that mapping is useful.

## The mapping (URML beside Forge)

- **Intent labels for episodes.** A robot-learning episode (in RLDS, LeRobot, or a rosbag) records what happened. URML's audit trail records the typed intent that drove it and the validation verdict. Aligning the two gives episodes a structured intent label without hand-annotation. Forge already moves between formats; URML intent records could ride along as an annotation channel.
- **A small, stable schema.** URML intent is a small typed vocabulary, so the annotation is compact and consistent across robots and substrates.

## What is asked

Request for comment from the Forge maintainer:

1. Is a typed validated-intent record a useful annotation channel when converting robot-learning datasets?
2. Does aligning intent records to RLDS/LeRobot/rosbag episodes fit Forge's model?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's execution audit trail, the small typed primitive vocabulary (RFC-0002), and the audit-trail-as-data-source framing (Move #40). Part of Move #50; sibling to ReductStore (RFC-0554) and ARES (RFC-0556).

## Implementation note

Outreach only. The post is a GitHub Issue on `arpitg1304/forge` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move50.yaml`.
