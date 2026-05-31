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

# Move #19 post bodies: education-community wave (Open Roberta / MakeCode / Snap!)

Copy-paste-ready bodies for the three Tier-A classroom-programming-environment targets. Tier-B partnership orgs (FIRST, REC Foundation, RoboCup Junior, Raspberry Pi Foundation / CoderDojo) are drafted separately in [`founder-actions-move19.md`](founder-actions-move19.md).

Bodies follow the [AGENTS.md](../../AGENTS.md) outreach-post-structure rules: concrete hook first, one or two real questions, light ask stated up front, full RFC linked as optional depth, under a two-minute read, zero em-dashes. The mandatory VIBE disclosure line goes last in every body.

All three repos have Issues enabled and Discussions disabled (verified 2026-05-31), so each post is a single Issue. Each post states the boundary against the device-SDK threads that already declined (PROS/VEX, Pybricks): this is the environment layer, not a device toolchain.

**Posting status:** all three posted live under `idoco2003` on 2026-05-31. Ledger `outreach-move19.yaml` carries the live URLs; `response` stays `none` until a maintainer replies.

**Routing summary**

| RFC | Target | Channel | Status | Live URL |
|---|---|---|---|---|
| 0287 | Open Roberta Lab | Issue on `OpenRoberta/openroberta-lab` | **Posted 2026-05-31** | https://github.com/OpenRoberta/openroberta-lab/issues/1747 |
| 0288 | Microsoft MakeCode | Issue on `microsoft/pxt` | **Posted 2026-05-31** | https://github.com/microsoft/pxt/issues/11340 |
| 0289 | Snap! (BJC) | Issue on `jmoenig/Snap` | **Posted 2026-05-31** | https://github.com/jmoenig/Snap/issues/3543 |

---

## RFC-0287: Open Roberta Lab

**Post to:** https://github.com/OpenRoberta/openroberta-lab/issues/new
**Title:** URML (open robot intent language): aligning a plain-language layer with Open Roberta's platforms

```
Hi Open Roberta team,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent. A student writes an English sentence, URML translates it to a primitive, validates it against the robot's declared capabilities, then dispatches. URML already drives LEGO SPIKE, micro:bit, and Thymio through its educational runtime, the same platforms Open Roberta programs with NEPO. So the two projects describe the same classroom hardware from different angles: you with blocks and a robot plugin, URML with a validated capability manifest plus a natural-language front door.

I am not proposing any change to Open Roberta, and nothing for you to maintain. This is a request for comment on whether the layers fit.

Two real questions. First, is a plain-English, validated-intent on-ramp that could feed into a NEPO-compatible target interesting to you, or does it overlap your roadmap? Second, could a URML capability manifest sensibly align with, or be derived from, an Open Roberta robot plugin's capability descriptor, and if so at what grain?

Full write-up if useful: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0287-open-roberta-outreach.md

Thanks for keeping classroom robotics open and vendor-neutral.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0288: Microsoft MakeCode

**Post to:** https://github.com/microsoft/pxt/issues/new
**Title:** URML (open robot intent language): an English front door alongside MakeCode for micro:bit

```
Hi MakeCode team,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent. A student writes an English sentence, URML translates it to a primitive, validates it against the device's declared capabilities, then dispatches. URML already ships a micro:bit capability fixture, so it describes the same device MakeCode's flagship editor targets. I have separately opened a thread with the micro:bit Foundation about the platform (RFC-0172); this thread is about the authoring environment, which is a different conversation.

Nothing here asks MakeCode to change or maintain anything. It is a request for comment on whether a plain-English, validated-intent on-ramp toward a MakeCode program is interesting, or out of scope.

One real question. URML's manifest needs to align with a device definition. Could it map onto a MakeCode target or board definition for the micro:bit-class subset, and what grain would be most useful from your side: just naming the target, or the board-level pin/peripheral detail?

Full write-up if useful: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0288-makecode-outreach.md

Thanks for how far MakeCode has lowered the bar for classroom programming.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0289: Snap! (BJC)

**Post to:** https://github.com/jmoenig/Snap/issues/new
**Title:** URML (open robot intent language): a teaching bridge from English to validated robot intent

```
Hi Snap! maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent. A student writes an English sentence, URML translates it to a primitive, validates it against the robot's declared capabilities, then dispatches, and it stops safely and explains itself when a request references something the robot has not been told about. That fail-closed behavior is a good thing to teach early, and a Snap!/BJC course feels like a natural place to teach the English-to-validated-intent loop.

Snap! is AGPL-3.0, so to be clear up front: I am not proposing to vendor any Snap! code, and nothing for you to maintain. The honest shape is a documented Snap-block to URML-primitive mapping kept on URML's Apache-2.0 side, plus a short BJC-compatible lesson. This is a request for comment.

Two real questions. Would a short lesson module showing the English-to-validated-intent loop be useful to point students at, or off-scope for the project? And is this repo the right channel, or should it go to the BJC curriculum team?

Full write-up if useful: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0289-snap-outreach.md

Thanks for Snap! and for the CS-education work around it.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```
