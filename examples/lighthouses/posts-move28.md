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

# Move #28 post bodies: safety / runtime verification

Copy-paste-ready bodies for the 10 Tier-A targets. Deferred / folded rows
(py-metric-temporal-logic + stlpy under the RV cluster, Breach, safety-gymnasium
under OmniSafe) are recorded in [`outreach-move28.yaml`](outreach-move28.yaml),
not posted.

Shared framing, in every body: URML does STATIC validation of intent against a
capability manifest and a safety envelope before dispatch; these tools operate at
the complementary point (runtime monitoring, scenario testing, falsification, or
safe control / learning). URML composes WITH them; it does not replace them.
Bodies are written precisely for a formal-methods / verification audience and
take care not to overclaim.

**No body contains a license-clarification ask** (per the 2026-06-03 guidance).

Bodies follow the [AGENTS.md](../../AGENTS.md) rules: concrete hook, "nothing for
you to maintain" up front, one or two real questions, RFC linked as optional
depth, under a two-minute read, zero em-dashes. VIBE disclosure line last.

All 10 repos have Issues enabled (verified 2026-06-04), so each is a single Issue.

**Posting status:** DRAFTED, not yet posted. Post under `idoco2003` only after
RFCs 0362-0371 land on `main`. Then fill `sent_at` / `posted_url` per row and
refresh `outreach.db`.

**Routing summary**

| RFC | Target | Channel | Status |
|---|---|---|---|
| 0362 | RTAMT | Issue on `nickovic/rtamt` | Drafted (post after merge) |
| 0363 | Reelay | Issue on `doganulus/reelay` | Drafted (post after merge) |
| 0364 | Copilot | Issue on `Copilot-Language/copilot` | Drafted (post after merge) |
| 0365 | Ogma | Issue on `nasa/ogma` | Drafted (post after merge) |
| 0366 | Scenic | Issue on `BerkeleyLearnVerify/Scenic` | Drafted (post after merge) |
| 0367 | VerifAI | Issue on `BerkeleyLearnVerify/VerifAI` | Drafted (post after merge) |
| 0368 | safe-control-gym | Issue on `learnsyslab/safe-control-gym` | Drafted (post after merge) |
| 0369 | OmniSafe | Issue on `PKU-Alignment/omnisafe` | Drafted (post after merge) |
| 0370 | esmini | Issue on `esmini/esmini` | Drafted (post after merge) |
| 0371 | MoonLight | Issue on `MoonLightSuite/moonlight` | Drafted (post after merge) |

---

## RFC-0362: RTAMT

**Post to:** https://github.com/nickovic/rtamt/issues/new
**Title:** URML (open robot intent language): a safety envelope as STL properties RTAMT could monitor, request for comment

```
Hi RTAMT maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent. It validates a request statically against a capability manifest and a safety envelope, then dispatches. The envelope is the part this issue is about: today it is a set of declared limits (geofence, occupancy, velocity and altitude bounds, link-loss rules) that URML checks before anything moves. What it is not yet is a set of monitorable temporal-logic properties, and RTAMT is the obvious vocabulary for that.

Nothing here asks RTAMT to change or maintain anything. This is a request for comment on a clean division of labor.

URML is static and pre-dispatch: it rejects an inadmissible request before execution. A runtime monitor is the complement: it catches a violation of an envelope property during execution. So two real questions. First, is it sound to express a URML safety-envelope property (a geofence held over time, a velocity bound) as an STL formula that RTAMT monitors, and are there envelope shapes that resist a clean STL encoding? Second, what signal interface does an online RTAMT monitor expect, so URML could emit the right traces from a running program?

Full write-up, with the envelope-to-STL mapping: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0362-rtamt-outreach.md

Thanks for RTAMT; an approachable open STL monitor is exactly the missing piece for a lot of us.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0363: Reelay

**Post to:** https://github.com/doganulus/reelay/issues/new
**Title:** URML (open robot intent language): an on-robot envelope monitor via Reelay, request for comment

```
Hi Reelay maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request statically against a capability manifest and a safety envelope, then dispatches. The envelope is a set of declared safety properties URML checks before motion. Reelay is interesting to URML because it builds efficient runtime monitors from temporal-logic specifications, header-only C++, which is the kind of thing that can actually run on a robot alongside the validated program.

Nothing here asks Reelay to change or maintain anything. This is a request for comment.

The division: URML rejects inadmissible intent before dispatch; a Reelay monitor enforces an envelope property at runtime. Two real questions. First, do URML envelope properties (bounds and timing conditions held over execution) map naturally onto Reelay's past-time MTL, or do some need future-time operators that change the deployment story? Second, what is the cleanest boundary for "URML declares the property and emits the signals, Reelay compiles and runs the monitor" on an embedded target?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0363-reelay-outreach.md

Thanks for Reelay; efficient header-only monitors are rarer than the need for them.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0364: Copilot

**Post to:** https://github.com/Copilot-Language/copilot/issues/new
**Title:** URML (open robot intent language): generating a hard-real-time envelope monitor with Copilot, request for comment

```
Hi Copilot maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request statically against a capability manifest and a safety envelope, then dispatches. The envelope is a declared set of safety properties. Copilot is interesting to URML for the strongest possible version of the runtime half: it generates provably hard-real-time C monitors from stream specifications, the kind used in aerospace.

Nothing here asks Copilot to change or maintain anything. This is a request for comment.

The picture: URML is static and pre-dispatch; a Copilot-generated monitor runs alongside the program as a hard-real-time guard on the same properties. Two real questions. First, can a URML safety-envelope property be expressed as a Copilot stream specification cleanly, and which envelope shapes are awkward? Second, for the hard-real-time guarantee to mean something end to end, what would URML need to declare about its signal sources and timing? I am also reaching Ogma separately, since it generates Copilot monitors from requirements.

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0364-copilot-rv-outreach.md

Thanks for Copilot; deployable, verifiable runtime monitoring is a real contribution.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0365: Ogma

**Post to:** https://github.com/nasa/ogma/issues/new
**Title:** URML (open robot intent language): a safety envelope as an Ogma requirement input, request for comment

```
Hi Ogma maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request statically against a capability manifest and a safety envelope, then dispatches. Ogma is the closest existing tool I have found to what URML's envelope wants downstream: it turns formal requirements into runtime-monitoring applications, generates Copilot monitors, and already integrates with frameworks including ROS, which URML targets too.

Nothing here asks Ogma to change or maintain anything. This is a request for comment, and an exciting one from URML's side.

The shape: a URML safety envelope is a declared set of properties; Ogma is a path from declared requirements to a generated, framework-integrated monitor. Two real questions. First, what input does Ogma expect (FRET-style structured requirements, a specification file), and could a URML envelope be lowered to that form? Second, given Ogma's ROS integration, how should a generated monitor's verdict feed back into a URML-governed system, so a runtime violation becomes a first-class signal rather than a side channel?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0365-ogma-outreach.md

Thanks for Ogma; closing the gap from requirements to deployed monitors is exactly the hard part.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0366: Scenic

**Post to:** https://github.com/BerkeleyLearnVerify/Scenic/issues/new
**Title:** URML (open robot intent language): pairing an intent spec with a Scenic scenario spec, request for comment

```
Hi Scenic maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an English sentence becomes a typed primitive, validated against a robot's declared capabilities and a safety envelope, then dispatched. I am reaching out because Scenic and URML are both specification languages, on complementary axes, and that feels worth exploring out loud.

URML specifies what the robot is meant to do and what it can do. Scenic specifies the world it is placed in. Put together, they describe both halves of a test: a URML behavior as the agent under test, a Scenic scenario as the environment that exercises it. To be clear, this is a peer-and-compose idea, not URML trying to sit above Scenic.

Two real questions. First, could a URML behavior serve as the ego/agent specification a Scenic scenario drives, and where would the interface naturally sit? Second, a Scenic scenario makes assumptions about the agent (its dynamics, its sensors); could those stay consistent with a URML capability manifest rather than being restated, so the two specs cannot drift?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0366-scenic-outreach.md

Thanks for Scenic; a readable probabilistic scenario language raised the bar for how we talk about test environments.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0367: VerifAI

**Post to:** https://github.com/BerkeleyLearnVerify/VerifAI/issues/new
**Title:** URML (open robot intent language): falsifying a declared safety envelope with VerifAI, request for comment

```
Hi VerifAI maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request statically against a capability manifest and a safety envelope, then dispatches. The envelope is a declared, structured set of safety properties, which is exactly the kind of thing a falsification loop wants as its specification.

Nothing here asks VerifAI to change or maintain anything. This is a request for comment.

The pairing: URML declares the properties and provides a validated system-under-test; VerifAI searches for scenarios (often via Scenic, which I am also reaching) that falsify those properties; a counterexample feeds back as a tightened envelope or a corrected capability. Two real questions. First, is a URML safety-envelope property usable as a VerifAI specification or monitor as-is, or does it need a transformation? Second, what would a URML-governed system need to expose to act as a VerifAI system-under-test, and what should a falsifying counterexample map back to in URML terms (an envelope change, a capability correction)?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0367-verifai-outreach.md

Thanks for VerifAI; a usable falsification toolkit for systems with learned components is sorely needed.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0368: safe-control-gym

**Post to:** https://github.com/learnsyslab/safe-control-gym/issues/new
**Title:** URML (open robot intent language): intent-level limits as control-level constraints, request for comment

```
Hi safe-control-gym maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request statically against a capability manifest and a safety envelope, then dispatches. The envelope declares limits at the intent level (bounds, geofences, occupancy). safe-control-gym is where limits like those become control-theoretic constraints and a controller is actually evaluated for honoring them, which is the level below where URML sits.

Nothing here asks safe-control-gym to change or maintain anything. This is a request for comment on whether the two levels line up.

Two real questions. First, does a URML safety-envelope constraint set map cleanly onto safe-control-gym's constraint specification (state and input constraints, CBF formulations), or is the intent-level declaration too coarse to be useful at the control level? Second, could a benchmarked controller's constraint-satisfaction record sensibly inform a URML capability or envelope (this controller honors these limits, so declare them safe to rely on)?

Full write-up, with the constraint mapping: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0368-safe-control-gym-outreach.md

Thanks for safe-control-gym; a shared benchmark for safe control and safe RL is exactly what the field needed.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0369: OmniSafe

**Post to:** https://github.com/PKU-Alignment/omnisafe/issues/new
**Title:** URML (open robot intent language): bounding a safe-RL policy with a declared envelope, request for comment

```
Hi OmniSafe maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request statically against a capability manifest and a safety envelope, then dispatches. A safety envelope is, in effect, a constraint declaration, which is what brings me to OmniSafe: a policy trained under explicit safety constraints is a learned controller, and URML is well placed to declare and statically bound what such a policy is allowed to attempt.

Nothing here asks OmniSafe to change or maintain anything. This is a request for comment, and I will be upfront that a learned policy as a URML substrate is newer ground for us.

Two real questions. First, does a URML safety-envelope constraint correspond to a constrained-MDP cost or constraint in a way that is meaningful, or are the two notions of constraint too different (declared and static vs learned and statistical)? Second, where is the clean boundary between URML's static, pre-dispatch bound and a trained policy's learned constraint-satisfaction, so the two reinforce rather than duplicate each other? For context, I am tracking safety-gymnasium as the environment side of the same conversation.

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0369-omnisafe-outreach.md

Thanks for OmniSafe; a serious infrastructural framework for safe RL is a real service to the field.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0370: esmini

**Post to:** https://github.com/esmini/esmini/issues/new
**Title:** URML (open robot intent language): a URML-governed agent under an OpenSCENARIO run, request for comment

```
Hi esmini maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request statically against a capability manifest and a safety envelope, then dispatches. esmini is interesting to URML as a standards-based test harness: a URML-governed system could be the controlled entity exercised by an ASAM OpenSCENARIO scenario, giving a portable, standard way to check that URML's static validation and the resulting behavior hold up in defined situations.

Nothing here asks esmini to change or maintain anything. This is a request for comment.

Two real questions. First, what is the cleanest way to wire a URML-governed agent as a controlled entity in an OpenSCENARIO run (an external controller interface, a co-simulation boundary)? Second, OpenSCENARIO's entity and action model is fairly driving-centric; does URML's mobility and perception capability declaration line up with it, or is the scope mismatch large enough that only a subset is meaningful? I am separately exploring Scenic as the probabilistic-scenario-language counterpart to the OpenSCENARIO standard.

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0370-esmini-outreach.md

Thanks for esmini; a lightweight, genuinely usable OpenSCENARIO player is a gift to anyone testing autonomy.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0371: MoonLight

**Post to:** https://github.com/MoonLightSuite/moonlight/issues/new
**Title:** URML (open robot intent language): a spatial-temporal envelope as a STREL property, request for comment

```
Hi MoonLight maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request statically against a capability manifest and a safety envelope, then dispatches. Some of the most important envelope properties are inherently spatial and temporal at once: a geofence held over time, a minimum separation distance maintained across a fleet of robots. That is exactly what STREL and MoonLight are built to monitor, which is why I am writing.

Nothing here asks MoonLight to change or maintain anything. This is a request for comment.

The division: URML declares the spatial-and-temporal envelope and validates intent before dispatch; a MoonLight monitor enforces the property at runtime. Two real questions. First, do URML envelope properties (a geofence, an occupancy region, a cross-robot separation) map onto STREL's reach and escape operators, or are some shapes hard to express? Second, for the multi-robot case (URML has a fleet deconfliction notion built on operational volumes), what spatial-graph and signal interface would a MoonLight monitor expect so the separation property could be checked over a live fleet?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0371-moonlight-outreach.md

Thanks for MoonLight; spatio-temporal monitoring is underserved and you are one of the few clean open tools for it.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```
