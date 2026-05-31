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

# Move #19 founder actions: education-community orgs (Tier B, not GitHub-routable)

The Tier-A Move #19 targets (Open Roberta, MakeCode, Snap!) are GitHub-routable and drafted in [`posts-move19.md`](posts-move19.md). The orgs below are partnership / email / forum contacts, not GitHub maintainers. They follow the Move #17 sub-wave-B precedent: drafted here for the founder to send under his own identity, ledgered only once shaped and sent.

Two standing constraints apply to every contact below:

- **No support promise.** URML is early and solo-maintained. Do not commit a response SLA, a help-desk, or a "we will support your classroom" guarantee. That is deferred until measured (CLAUDE.md, public-commitments rule). Offer interest and material, not a service level.
- **No cross-thread name-dropping.** Do not name specific engaged maintainers or orgs from other threads as social proof. Aggregate framing ("URML has opened conversations across the classroom-robotics ecosystem") is fine; specific identification is not.

The pitch is constant: URML is an open, Apache-2.0 plain-language layer for robot intent, with an educational profile, runnable classroom examples, and a 30-minute no-API-key lesson ([Tutorial 5](../../docs/tutorials/05-teaching-urml.md)). The ask is a conversation about whether URML fits the org's program, curriculum, or competition, not a sale and not a commitment.

---

## 1. FIRST (FRC / FTC / FLL)

**Who.** FIRST is the largest school robotics program in the US (FIRST Robotics Competition, FIRST Tech Challenge, FIRST LEGO League). The WPILib software library is already a separate URML thread (RFC-0228); this is the *organization*, not the codebase.

**Channel.** FIRST's partnerships / education contact form, or a known education-team email if the founder has one. Not a GitHub issue.

**Ask.** Whether an English-to-validated-intent layer is interesting as a teaching aid or an accessibility on-ramp for new teams, and who the right person to talk to is. Keep it to one paragraph plus the Tutorial 5 link.

**Boundary to state.** This is the curriculum/program layer; the WPILib software conversation (RFC-0228) is separate.

---

## 2. REC Foundation (VEX competition + curriculum)

**Who.** The Robotics Education and Competition Foundation runs the VEX competition ecosystem and a large classroom curriculum. This is explicitly distinct from the PROS/VEX device toolchain (RFC-0236), which declined: REC is the competition and curriculum org, not the device SDK.

**Channel.** REC Foundation education / partnerships contact. Not GitHub.

**Ask.** Whether a plain-language intent layer fits anywhere in their classroom curriculum or accessibility goals. State up front that this is not a re-pitch of the VEX device toolchain.

---

## 3. RoboCup Junior

**Who.** The school-age division of RoboCup, international, community-run, with regional leagues. The audience is teachers and student teams.

**Channel.** RoboCup Junior community / regional-committee contact, or a relevant mailing list / forum. International org, so a ticket-bot autoreply counts as `acked`, not `engaged`, when ledgered.

**Ask.** Whether URML's English-to-intent loop and the educational profile's fail-safe defaults are useful for an introductory league or workshop. Offer the lesson material.

---

## 4. Raspberry Pi Foundation / CoderDojo

**Who.** The education arm and the CoderDojo network. Distinct from the Raspberry Pi Pico SDK thread (RFC-0175), which is the device-firmware layer; this is the teaching/community layer.

**Channel.** Foundation education-team contact or the CoderDojo community channel. Not GitHub.

**Ask.** Whether a no-install, offline, no-API-key robot-intent lesson fits a Dojo session or the Foundation's learning resources. The offline, zero-telemetry posture is the selling point for a youth-education context.

---

## Optional, lower priority

- **Technovation** and **CSTA (Computer Science Teachers Association)** are warm-list candidates if the four above gain traction. Same pitch, same constraints. Hold until there is at least one engaged education-org thread to learn from.

---

## Sequencing

Low-friction first. RoboCup Junior and CoderDojo are community-shaped and forgiving of an early-project pitch. FIRST and REC Foundation are larger and slower; approach them once the Tier-A GitHub threads have any signal to reference (in aggregate, per the confidentiality rule). Ledger each in `outreach-move19.yaml` only when a message actually goes out, with `channel: email` (or `in_person`) and `response: none`.
