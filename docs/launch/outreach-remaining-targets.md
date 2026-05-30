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

# Outreach: the rest (un-sent targets outside Move #17)

Re-verification on 2026-05-30 of every target that was researched but never posted, **excluding Move #17** (governance / foundation-home; tracked separately). Of ~229 ledger rows across Moves #1–18, 200 were posted. This document accounts for the nine that were not, outside Move #17, and records the disposition decided 2026-05-30.

The goal of the re-check was simple: some targets were deferred at posting time because no engageable surface was found. Surfaces change. Two of them now have one.

## Disposition table

| Target | RFC | Move | Ledger | Disposition (2026-05-30) |
|---|---|---|---|---|
| wageningen-fre → `github.com/FieldRobotEvent` | 0099 | #7 | [outreach-move7.yaml](../../examples/lighthouses/outreach-move7.yaml) | **SENT** — surface recovered |
| fairseq → `facebookresearch/seamless_communication` | 0167 | #12 | [outreach-move12.yaml](../../examples/lighthouses/outreach-move12.yaml) | **SENT** — retargeted to successor |
| klipper (`Klipper3d/klipper`) | 0227 | #18 | [outreach-move18.yaml](../../examples/lighthouses/outreach-move18.yaml) | **SENT** |
| wpilib (`wpilibsuite/allwpilib`) | 0228 | #18 | [outreach-move18.yaml](../../examples/lighthouses/outreach-move18.yaml) | **SENT** |
| openbci-brainflow (`brainflow-dev/brainflow`) | 0230 | #18 | [outreach-move18.yaml](../../examples/lighthouses/outreach-move18.yaml) | **SENT** |
| crazyflie (`bitcraze/crazyflie-lib-python`) | 0229 | #18 | [outreach-move18.yaml](../../examples/lighthouses/outreach-move18.yaml) | **HELD** — see below |
| inivation-event | 0126 | #10 | [outreach-move10.yaml](../../examples/lighthouses/outreach-move10.yaml) | **DEFERRED** — no surface |
| bear-robotics-servi | 0102 | #8 | [outreach-move8.yaml](../../examples/lighthouses/outreach-move8.yaml) | **DEFERRED** — no surface |
| serve-robotics-model-optimizer | 0195 | #15 | [outreach-move15.yaml](../../examples/lighthouses/outreach-move15.yaml) | **DEFERRED** — no surface |

## Sent (5)

These five had a postable GitHub surface as of 2026-05-30 and went out under the maintainer's GitHub identity.

- **wageningen-fre (RFC-0099).** The original ledger note said "NO verified GitHub org or Issue surface; community channel is Discord." The 2026-05-30 re-check found `github.com/FieldRobotEvent` does exist, with Issues enabled on several repos (`competition_environment`, `virtual_maize_field`, `example_ws`). The May surface check missed it. Posted to the org's competition-environment surface, with the Discord acknowledged.
- **fairseq (RFC-0167).** The original blocker was that `facebookresearch/fairseq` is archived (read-only since 2025-09-30), so `gh issue create` is refused there. The RFC's own engagement question was "what is the successor surface for NLLB engagement now?" `facebookresearch/seamless_communication` is live (Issues + Discussions, not archived) and was already named in the RFC as the candidate successor. Posted there, framed as the successor-surface question. The non-commercial-weights caveat (NLLB / Seamless model weights are CC-BY-NC 4.0) is stated in the body; the ask is framed around the multilingual NL layer, not the weights.
- **klipper (RFC-0227), wpilib (RFC-0228), openbci-brainflow (RFC-0230).** Move #18 batch-1 frame-break targets. RFCs were complete and on `main`; the only gap was a post-body file, now written in [posts-move18.md](../../examples/lighthouses/posts-move18.md). All three repos are live with Issues enabled.

**Venue note.** Klipper (Discourse/Discord) and WPILib (Chief Delphi) both prefer a forum over GitHub Issues for cross-project discussion. Each post acknowledges the forum and asks the maintainers which venue they prefer, so a redirect-to-forum is an expected, acceptable outcome (a soft no on venue, not on substance), recorded truthfully if it happens.

## Held (1)

- **crazyflie (RFC-0229).** Targets `bitcraze/crazyflie-lib-python`. Move #13 RFC-0181 already posted an Issue to the sister repo `bitcraze/crazyflie-firmware` (same vendor, Bitcraze AB), and that thread has not yet had a response. Posting a second Issue to the same vendor while the first is unanswered risks reading as spam. Held until RFC-0181 gets any response, at which point RFC-0229 can be posted to `crazyflie-lib-python` with an explicit RFC-0181 cross-reference.

## Deferred — no engageable GitHub surface (3)

Re-verified 2026-05-30; all three still lack a postable surface. Kept on the ledger with refreshed notes for the audit trail.

- **inivation-event (RFC-0126).** Development is GitLab-native (`gitlab.com/inivation/dv/`). The `github.com/inivation` org is five repos, all utility forks with Issues disabled. URML's outreach pipeline is GitHub-based. A GitLab-side post is a possible future motion if the GitHub default is relaxed.
- **bear-robotics-servi (RFC-0102).** The `github.com/bearrobotics` org is infrastructure forks with no customer-facing Issues surface; the Bear Cloud API portal has no contact form. No engageable surface located.
- **serve-robotics-model-optimizer (RFC-0195).** All public `serve-robotics` repos are forks with Issues disabled. No vendor-original engagement surface exists.

## Out of scope here

**Move #17** (governance / foundation-home): 13 founder-action drafts (OSRA, JDF, IEEE, NIST, ASTM, CEN-CENELEC, DIN, AFNOR, BSI, OECD + IIA/euRobotics/ADRA), 4 federal docket-watch rows, and 15 Tier-B deferred bodies. These are email / membership / formal-submission channels, not assistant-postable GitHub surfaces, and are tracked in [founder-actions-move17.md](../../examples/lighthouses/founder-actions-move17.md) and [outreach-move17.yaml](../../examples/lighthouses/outreach-move17.yaml).
