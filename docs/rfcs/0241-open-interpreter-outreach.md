---
rfc: 0241
title: Open Interpreter conceptual-peer integration, request for comment from OpenInterpreter maintainers
author: Ido Yahalomi (greenvh@gmail.com)
created: 2026-05-29
updated: 2026-05-29
state: Draft
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

# RFC-0241: Open Interpreter conceptual-peer integration, request for comment from OpenInterpreter maintainers

## Summary

URML is a small open language for robot intent. Open Interpreter is a natural-language interface for general computer control. The two projects sit on the same English-sentence-to-action niche but on different action surfaces: Open Interpreter dispatches into the shell and Python on the host, URML dispatches into validated robot primitives on a substrate like ROS 2 or PX4. This RFC frames the relationship as a conceptual peer, not a substrate URML composes onto, and asks one light question about mutual citation and a possible interoperability seam. No spec change proposed, nothing for you to maintain.

## Concrete example

An English sentence handed to Open Interpreter:

> Resize all images in this folder to 800px wide.

becomes a short shell-and-Python plan that runs locally (`ls`, then `PIL.Image.thumbnail`, then save back to disk).

The same English-sentence-to-action shape handed to URML:

> Stack the cube on the platform.

becomes a URML program:

```yaml
program:
  - pick_from: { object: cube }
  - place_at:  { surface: platform }
```

which is validated against a manifest before any motion command leaves the host. Same niche (English in, deterministic action out), different action surfaces (computer vs robot).

## Why URML on this target

This is a conceptual peer engagement, not a substrate composition. URML does not run inside Open Interpreter and Open Interpreter does not run inside URML. The two projects are working the same problem from opposite sides of the action surface, and there is value in saying so plainly to readers of either repo. The ask is light: a peer-citation footnote in URML's docs pointing to Open Interpreter, and a question about whether the maintainers would consider a reciprocal mention. AGPL on Open Interpreter's side means any deeper integration stays at the REST or IPC boundary, never inside the binary.

## Capability-manifest mapping

This is a peer-citation declaration shape, not a full adapter mapping. URML's docs and registry would carry a "conceptual peers" section that names Open Interpreter with the framing below.

| URML peer-citation field | Open Interpreter value |
| ------------------------ | ---------------------- |
| `peer.name`              | Open Interpreter       |
| `peer.repo`              | `OpenInterpreter/open-interpreter` |
| `peer.surface`           | general computer control (shell, Python) |
| `peer.relationship`      | natural-language-to-action peer on a different action surface |
| `peer.interop_boundary`  | REST or IPC only (AGPL-3.0 on peer side) |

## Drawbacks

- AGPL-3.0 on Open Interpreter means any code-level integration stays at the REST or IPC boundary; URML cannot embed Open Interpreter as a library.
- The "conceptual peer" framing is novel for URML's RFC catalog; readers expecting a substrate-composition story may find the shape unusual.
- Maintainer interest in a reciprocal citation is unknown; the engagement may end at a one-way URML footnote.

## Unresolved questions

Would the Open Interpreter maintainers welcome a peer-citation footnote in URML's docs and consider a reciprocal mention, and is there an interoperability shape worth exploring (for example, URML emitting computer-control intents that Open Interpreter executes over a documented boundary)?

## How to respond

Best channel is a single GitHub Issue on `OpenInterpreter/open-interpreter` (Issues are enabled, 63.7k stars, last commit 2026-05-17, not archived). Use the `question` label if available, and frame the issue as a conceptual-peer note rather than a feature request. Ledger row and full thread tracked at [`examples/lighthouses/outreach-move18.yaml`](../../examples/lighthouses/outreach-move18.yaml).

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (AGPL-3.0, 63.7k stars, Issues enabled, last commit 2026-05-17, isArchived: false).
- [x] Conceptual-peer framing explicit; not pitched as substrate composition.
- [x] No spec change proposed; AGPL-3.0 boundary acknowledged (REST or IPC only).
- [x] Ledger row drafted in `outreach-move18.yaml`; AI-assisted authoring disclosed (see [`VIBE.md`](../../VIBE.md)).
- [x] Post-Nav2 structure applied: concrete example first, 1-2 questions, no compound-noun jargon, under-2-min read aloud, zero em-dashes.
