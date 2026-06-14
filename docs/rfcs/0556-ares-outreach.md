---
rfc: 0556
title: ARES (robot-data ingest) integration — request for comment
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

# RFC-0556: ARES (robot-data ingest) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the robot-data sub-cluster of the HRI / conversational / robot-data wave (Move #50).

## Summary

[`jacobphillips99/ares`](https://github.com/jacobphillips99/ares) (Apache-2.0) is a platform for ingesting, annotating, and analyzing robot-episode data. URML is the closest *intent* peer to that work: its validated-intent audit records are a structured annotation layer over robot episodes, capturing what was instructed and whether it was admissible. This RFC asks whether the mapping is useful.

## The mapping (URML beside ARES)

- **Structured intent annotation.** ARES ingests and annotates robot episodes. URML's audit trail is a typed record of the intent behind each episode plus the validation verdict (admissible, rejected, why). As an annotation layer it turns "what the robot did" into "what it was asked to do and whether that was allowed", which is the harder half to recover after the fact.
- **Queryable by intent.** Because the records are typed and tied to a capability manifest + safety envelope, episodes become queryable by intent and by rejection reason, not just by raw signal.

## What is asked

Request for comment from the ARES maintainer:

1. Is a typed validated-intent record a useful structured annotation layer over ingested robot episodes?
2. Does intent-and-verdict annotation fit how ARES models episode metadata?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's execution audit trail, the five-pass validator, and the audit-trail-as-data-source framing (Move #40). Part of Move #50; the closest robot-data intent peer in the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `jacobphillips99/ares` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move50.yaml`.
