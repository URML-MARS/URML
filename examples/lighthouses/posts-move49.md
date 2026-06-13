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

# Move #49 post bodies: the swarm / multi-robot / alternative-framework wave

Seven targets, all GitHub Issues. Post under idoco2003. No license-ask
anywhere (state each repo's actual license, never ask; GPL/LGPL/EUPL-NC:
cross-citation only, no code reuse). AI-assisted-authoring disclosure up front.
Titles carry no em-dash. LSTS DUNE + Neptus are one post (on DUNE, referencing
Neptus). Three framings: language-to-language peer (Buzz/scafi/Protelis),
multi-agent runtime to URML fleet (SCRIMMAGE, LSTS), alternate non-ROS
substrate (OpenRTM-aist, RoboComp).

---

## RFC-0542: Buzz (anchor)

**Post to (Issue):** https://github.com/buzz-lang/Buzz/issues/new
**Title:** URML (open robot intent language): a per-robot validated-intent layer beside Buzz's swarm language (request for comment)

```
Hi Buzz maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. Buzz is also a language for robots, at a different layer -- it expresses collective swarm behavior that compiles down to per-robot execution. This is a language-to-language note, not a request to adopt anything.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

Where the two sit: Buzz expresses the swarm's collective behavior; URML declares each robot's validated intent and the fleet's roster + cross-robot constraints. One natural composition: a Buzz program coordinates the swarm, while the per-robot actions it issues are URML primitives validated against each robot's capability manifest before dispatch. URML adds the typed, statically-checkable per-robot gate; Buzz stays the swarm language. No manifest ask, just a conversation about where each layer sits.

Two real questions: (1) is "Buzz coordinates the swarm, URML validates the per-robot intent it issues" a sensible layering? (2) Does URML's fleet roster + cross-robot deconfliction overlap or complement Buzz's swarm primitives, and which boundary is worth exploring first?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0542-buzz-outreach.md

Thanks for Buzz; a purpose-built swarm language is exactly the kind of peer a per-robot intent layer wants to understand its boundary with.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0543: ScaFi

**Post to (Issue):** https://github.com/scafi/scafi/issues/new
**Title:** URML (open robot intent language): per-device validated intent beside ScaFi's aggregate computing (request for comment)

```
Hi ScaFi maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the device's declared capabilities and a safety envelope, then dispatched. ScaFi programs a collective of devices as a single field-based program (aggregate computing). URML is a language peer at the individual-device layer. This is a language-to-language note.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

Where the two sit: ScaFi expresses the aggregate behavior over a field of devices; URML declares each device's intent, validated against its capability manifest and a safety envelope, with a fleet roster across many (and cross-device deconfliction). One composition: the aggregate program decides the collective, and the per-device actions are URML primitives checked before dispatch. Two declarative styles -- aggregate over a field, and per-robot over capabilities -- meeting at a boundary worth naming.

Two real questions: (1) is "ScaFi expresses the aggregate behavior, URML validates the per-device intent" a sensible layering? (2) Does URML's fleet roster + deconfliction complement aggregate computing's field model, and which boundary is worth exploring first?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0543-scafi-outreach.md

Thanks for ScaFi; aggregate computing is a genuinely different and elegant take on the collective, and the seam with per-robot validated intent is the interesting part.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0544: Protelis

**Post to (Issue):** https://github.com/Protelis/Protelis/issues/new
**Title:** URML (open robot intent language): per-device validated intent beside Protelis field calculus (request for comment)

```
Hi Protelis maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the device's declared capabilities and a safety envelope, then dispatched. Protelis is a field-calculus language for aggregate programming of distributed systems. URML is a language peer at the individual-device layer. This is a language-to-language note (cross-citation only -- Protelis is GPL-3.0, so no shared code is implied).

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

Where the two sit: Protelis expresses computation over a field of devices; URML declares each device's intent validated against its capability manifest and a safety envelope, with a fleet roster across many. One composition: the field program decides the collective, the per-device actions are URML primitives checked before dispatch. Given the GPL-3.0 license this proposes no code reuse, only a conceptual boundary between two declarative languages.

Two real questions: (1) is "Protelis expresses the field computation, URML validates the per-device intent" a sensible layering? (2) Does URML's fleet roster + deconfliction complement field calculus's aggregate model, and which boundary is worth exploring first?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0544-protelis-outreach.md

Thanks for Protelis; field calculus is a clean formal foundation, and naming its boundary with per-robot validated intent seems worth doing.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0545: SCRIMMAGE

**Post to (Issue):** https://github.com/gtri/scrimmage/issues/new
**Title:** URML (open robot intent language): a validated multi-agent intent layer above a SCRIMMAGE scenario (request for comment)

```
Hi SCRIMMAGE maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. SCRIMMAGE simulates large heterogeneous multi-agent scenarios; URML is interesting at the multi-robot coordination layer above such a scenario.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: a SCRIMMAGE scenario of N agents maps onto a URML fleet roster -- each agent a member with its own capability manifest, the scenario's separation requirements expressed as cross-agent deconfliction. URML validates the multi-agent intent before it runs, then the scenario simulates it (or, for a real deployment, the substrate executes). URML does not simulate; it declares and statically checks the multi-agent intent.

Two real questions: (1) does a URML fleet roster + cross-agent deconfliction fit how SCRIMMAGE scenarios declare many heterogeneous agents? (2) Is a statically-validated multi-agent intent layer above a SCRIMMAGE scenario interesting, and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0545-scrimmage-outreach.md

Thanks for SCRIMMAGE; a simulator built for large heterogeneous fleets is exactly where fleet-level validated intent is easiest to try.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0546: LSTS toolchain (DUNE + Neptus)

**Post to (Issue):** https://github.com/LSTS/dune/issues/new
**Title:** URML (open robot intent language): validated intent for DUNE + Neptus fleet C2 (request for comment)

```
Hi LSTS maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the vehicle's declared capabilities and a safety envelope, then dispatched. The LSTS toolchain is a mature non-ROS stack for networked unmanned vehicles -- DUNE the onboard runtime, Neptus the fleet command-and-control. URML is interesting in two ways here.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment. (DUNE and Neptus are under a modified EUPL-1.1 with a non-commercial restriction; this proposes no code reuse, only a mapping / consumer relationship.)

The mapping, two seams: (1) DUNE is an onboard runtime in the same role URML's reference runtimes play -- the thing that executes a validated plan on a vehicle; URML validates intent against the vehicle's capabilities and a safety envelope, then dispatches to DUNE (URML stays substrate-neutral, DUNE is one substrate). (2) Neptus commands and monitors a fleet of networked vehicles; URML's fleet roster and cross-vehicle deconfliction are the static-validation complement -- declare the fleet and its constraints, validate the multi-vehicle intent, then drive it through Neptus.

Two real questions: (1) is DUNE a sensible non-ROS substrate for URML-validated intent to dispatch to? (2) Does URML's fleet roster + deconfliction complement Neptus's fleet C2, and which is the cleaner first seam -- DUNE (substrate) or Neptus (fleet)?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0546-lsts-outreach.md

Thanks for DUNE and Neptus; a real networked-UV stack with both an onboard runtime and fleet C2 is an unusually complete place to test substrate-neutral validated intent.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0547: OpenRTM-aist

**Post to (Issue):** https://github.com/OpenRTM/OpenRTM-aist/issues/new
**Title:** URML (open robot intent language): validated intent dispatched to RT-Middleware (request for comment)

```
Hi OpenRTM-aist maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. URML is substrate-neutral by design, and RT-Middleware -- an implementation of the OMG Robotic Technology Component (RTC) standard -- is exactly the kind of non-ROS substrate URML should dispatch validated intent to.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: URML validates an intent against the robot's declared capabilities and a safety envelope, then dispatches to whatever substrate the deployment uses; an RTC system is one such substrate -- URML produces the validated call, the RTC components execute it. And an RTC's declared data ports and service ports describe what a component exposes, which maps toward a URML capability manifest the validator can check against. URML is the typed intent + validation layer; OpenRTM-aist is the component runtime.

Two real questions: (1) is "URML validates intent, then dispatches to RT-Middleware (RTC) components" a sensible substrate mapping? (2) Could an RTC's declared ports inform a URML capability manifest, and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0547-openrtm-aist-outreach.md

Thanks for OpenRTM-aist; a standards-based non-ROS component middleware with this much history is a good proof that URML's substrate-neutrality is real and not just ROS-shaped.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0548: RoboComp

**Post to (Issue):** https://github.com/robocomp/robocomp/issues/new
**Title:** URML (open robot intent language): validated intent dispatched to RoboComp components (request for comment)

```
Hi RoboComp maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. URML is substrate-neutral, and RoboComp -- an open component framework for robot software -- is a non-ROS substrate URML can dispatch validated intent to. This is a cross-citation note (RoboComp is GPL-3.0, so no shared code is implied).

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: URML validates an intent against the robot's declared capabilities and a safety envelope, then dispatches; RoboComp's components execute it. RoboComp's component interface definitions describe what a component does, which maps toward a URML capability manifest the validator checks against. URML is the typed intent + validation layer; RoboComp is the component runtime. No code reuse proposed given the GPL-3.0 license.

Two real questions: (1) is "URML validates intent, then dispatches to RoboComp components" a sensible substrate mapping? (2) Could RoboComp component interfaces inform a URML capability manifest, and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0548-robocomp-outreach.md

Thanks for RoboComp; a long-running component framework outside the ROS world is exactly the kind of substrate that keeps an intent language honest about its neutrality.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```
