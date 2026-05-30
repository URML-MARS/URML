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

# Move #18 post bodies — frame-break wave (batch 1)

Copy-paste-ready Issue bodies for the Move #18 outreach. **Wave shape**: four reframes that step outside the robot-vendor mental model (RFCs 0227-0230), verified 2026-05-29. Ledger: [`outreach-move18.yaml`](outreach-move18.yaml).

**Posted 2026-05-30: three of four.** Klipper (0227), WPILib (0228), and OpenBCI/BrainFlow (0230) went out. **Crazyflie (0229) is held** — Move #13 RFC-0181 already posted an unanswered Issue to the sister repo `bitcraze/crazyflie-firmware`; a second Issue to the same vendor before the first is answered risks reading as spam. RFC-0229 posts to `crazyflie-lib-python` once RFC-0181 gets a response, with an explicit cross-reference.

Voice: maintainer posts under his GitHub identity. Each opens "Hi <team>" and addresses the maintainers directly.

**Confidentiality discipline.** Per the outreach-confidentiality rule, post bodies do not name or link previously engaged URML maintainers as social proof. URML's own RFCs in `docs/rfcs/` and aggregate counts are fine.

**Authoring disclosure (reused verbatim at the bottom of every post body):**

```
*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

**Venue note.** Klipper (Discourse/Discord) and WPILib (Chief Delphi) prefer a forum over GitHub Issues for cross-project discussion. Each body acknowledges the forum and asks the maintainers which venue they prefer; a redirect-to-forum is an expected, acceptable outcome.

---

## RFC-0227: Klipper
**Post to:** https://github.com/Klipper3d/klipper/issues/new (Issues enabled)

**Title:** URML (substrate-neutral robot intent language) — RFC requesting feedback on a Klipper motion-substrate mapping

**Body:**

Hi Klipper team,

URML (urml.dev) is a small, opinionated, human-readable language for describing robot intent — Apache-2.0, substrate-neutral by design. It sits above runtime substrates and compiles a sentence about what a machine should do into a validated, runnable program. Most of our prior outreach engaged robot vendors. This one is deliberately different: a 3D printer or CNC gantry is a motion platform, G-code is a motion substrate, and Klipper is one of the largest active open-source motion-control communities anywhere. If a motion mapping lands cleanly on Klipper, which has zero ROS dependency and is not a robot OEM, that is a real test of the substrate-neutral claim.

This is a **proposal-only** RFC. No spec change, no ask for your code, nothing to merge. Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0227-klipper-outreach.md

URML would integrate at the G-code / IPC boundary (emit G-code that Klipper consumes over a process or Moonraker boundary), with no Klipper code vendored — keeping URML's Apache-2.0 stance clean against Klipper's GPL-3.0. The mapping covers motion intent only: extruder temperature, material feed, and heater control are process control, not motion, and stay outside URML's scope. That makes a Klipper mapping a partial mapping by design, and we want to know whether motion-only is coherent or omits too much to be useful.

A few questions for the maintainers (full list in the RFC):

1. **Kinematics declaration.** URML's mobility enum has no `cartesian` / `corexy` / `delta` today. Should a URML manifest declare kinematics mirroring `printer.cfg`, or reference the Klipper config directly rather than restate it?
2. **Integration boundary.** For an external intent layer, is G-code emission or the Moonraker API the cleaner boundary?
3. **Work-envelope and limits.** Cross-reference `printer.cfg` position / velocity / acceleration limits, or restate them in the manifest?
4. **Scope.** Is a motion-only mapping (no thermal / material process) useful in practice for Klipper?
5. **Venue.** We know Klipper reserves GitHub Issues for bug reports under templates and routes discussion to Discourse / Discord. If this RFC belongs on the forum rather than here, just say so and we will move it — that answer is useful on its own.
6. **Anything else.**

Happy to scope down, deepen, or shelve as fits. Thanks for the years of work on a genuinely excellent motion stack.

Ido Yahalomi (URML maintainer, urml.dev, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

## RFC-0228: WPILib
**Post to:** https://github.com/wpilibsuite/allwpilib/issues/new (Issues enabled)

**Title:** URML (substrate-neutral robot intent language) — RFC requesting feedback on a WPILib capability-manifest mapping

**Body:**

Hi WPILib team,

URML (urml.dev) is a small, opinionated, human-readable language for describing robot intent — Apache-2.0, substrate-neutral by design. It compiles a sentence about what a robot should do into a validated, runnable program above whatever substrate runs below. WPILib is the surface where tens of thousands of FRC students program a real robot every season, and the mental model people learn first tends to be the one they carry forward. That makes WPILib a strategic mapping target, not a niche one.

This is a **proposal-only** RFC. BSD-3-Clause composes cleanly with URML's Apache-2.0, so there is no license friction and nothing to merge on your side. Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0228-wpilib-outreach.md

The mapping surfaces one real gap honestly: differential (tank) and mecanum map onto URML's existing mobility vocabulary, but **swerve does not**, and swerve is now the dominant competitive drivetrain. That is a concrete, well-bounded extension we would want shaped by your input rather than guessed, following the same path URML used to add `quadruped` / `biped`.

A few questions for the maintainers (full list in the RFC):

1. **Swerve.** What does a swerve declaration need to capture at the capability level (module count, independent steering) without overreaching into per-module geometry?
2. **Integration boundary.** Is the cleaner boundary generating a command-based skeleton, or driving the robot over an existing WPILib interface (network table / command path)?
3. **CAN motor controllers.** Should a URML manifest declare the CAN motor-controller inventory (vendor, count), or treat it as below the manifest line?
4. **Language target.** WPILib ships Java, C++, and Python. Which is the natural target for a generated adapter or skeleton?
5. **Venue.** We know Chief Delphi is the FRC community's home for design discussion. If this RFC belongs there rather than on a GitHub Issue, tell us and we will move it.
6. **Anything else.**

Happy to scope down, deepen, or shelve. Thanks for the library that has taught a generation of roboticists.

Ido Yahalomi (URML maintainer, urml.dev, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

## RFC-0230: OpenBCI / BrainFlow
**Post to:** https://github.com/brainflow-dev/brainflow/issues/new (Issues enabled)

**Title:** URML (robot intent language) — RFC on a BrainFlow intent-input bridge (alternative to natural-language intent)

**Body:**

Hi BrainFlow team (and OpenBCI, cross-referenced),

URML (urml.dev) is a small, opinionated, human-readable language for describing robot intent — Apache-2.0. Its job is to turn an intent into verified, safe robot motion: it validates intent against a capability manifest and a safety envelope before anything executes. Natural language is URML's usual source of intent. This RFC asks about a different source: a brain-computer-interface intent signal, delivered through BrainFlow from OpenBCI hardware, feeding URML's behavior layer for users who cannot use the language path.

This is a **proposal-only** RFC, and the most exploratory thing we have posted. It is honest that this is an **input-bridge, not a runtime adapter**: URML does not decode EEG and does not classify neural signals — that stays in your pipeline. The bridge is narrow:

```
OpenBCI board -> BrainFlow stream -> (user's classifier) -> discrete intent label -> URML behavior trigger -> validate -> execute
```

URML consumes a discrete intent label and runs its normal validate-then-execute path. It is the non-verbal analog of how speech-to-text feeds a text layer: the recognizer produces a token, URML does the rest. MIT composes cleanly with Apache-2.0, so there is no license boundary and nothing to merge. Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0230-openbci-brainflow-outreach.md

A few questions for the maintainers (full list in the RFC):

1. **Bridge boundary.** Is "BrainFlow stream plus the user's classifier emits a discrete intent label, URML consumes the label" the right boundary, or would you expect URML to engage a different layer?
2. **Intent-label contract.** Is there a conventional shape for classified-intent events in BrainFlow-based projects that URML should map to, rather than inventing one?
3. **Confidence gating.** A classifier emits a confidence. Should URML require a per-intent confidence threshold before a behavior fires? This is the safety-relevant question.
4. **Two-party scope.** Should we engage BrainFlow (the SDK) and OpenBCI (the hardware) separately, or is one the right entry point?
5. **Anything else** — including whether the assistive-robotics framing matches how your users actually drive robots.

Happy to scope down or shelve. If a maintainer prefers Slack, the OpenBCI forum, or human-only correspondence, that is welcome and we will route to it. Thanks for the vendor-neutral biosignal SDK that makes a question like this even askable.

Ido Yahalomi (URML maintainer, urml.dev, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

## RFC-0229: Crazyflie — HELD (not posted)

Targets `bitcraze/crazyflie-lib-python`. Held 2026-05-30 to avoid a same-vendor double-post: Move #13 RFC-0181 already opened an Issue on `bitcraze/crazyflie-firmware` that has not yet had a response. When RFC-0181 gets any reply, post RFC-0229 to `crazyflie-lib-python` with an explicit cross-reference to the firmware thread so Bitcraze sees them as one coordinated conversation, not two unsolicited Issues. Draft body lives in [`docs/rfcs/0229-crazyflie-outreach.md`](../../docs/rfcs/0229-crazyflie-outreach.md).

---

## Operational notes

- **Sequencing.** Posted OpenBCI/BrainFlow and the two forum-preferring targets (Klipper, WPILib) with an explicit venue question, so a forum redirect is a clean outcome rather than a rejection.
- **Cadence.** Frame-break targets are community-driven; 4-6 week first-touch windows. Klipper and WPILib have seasonal / event rhythms (WPILib especially, on the FRC calendar).
- **Crazyflie gate.** Do not post RFC-0229 until RFC-0181 (firmware, Move #13) shows a response. Re-check that thread before sending.
- **Confidentiality.** No other engaged URML maintainer or org is named in any post body above. URML's own RFCs and aggregate counts are fine; specific responder identities are not.
