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

# Move #53 post bodies: the motor-control / RTOS substrate wave

Ten targets, all GitHub Issues. Post under idoco2003. No license-ask anywhere
(state each repo's actual license, never ask; GPL/LGPL/non-standard: no code
reuse). AI-assisted-authoring disclosure up front. Titles carry no em-dash.
This lane is altitude-sensitive: the RTOS bodies are deliberately honest that
URML sits well above an OS, and the wave leads with integrator firmware where
the altitude is clean. Bodies are varied per target (different openings,
question counts, ordering), not a single skeleton. This wave completes the
2026-06-13 second candidate slate.

---

## RFC-0576: Betaflight (anchor)

**Post to (Issue):** https://github.com/betaflight/betaflight/issues/new
**Title:** URML (open robot intent language): a validated intent layer above flight-controller firmware (request for comment)

```
Hi Betaflight maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent. The idea is narrow: take an intent, check it against what the craft can actually do and the bounds it is allowed to operate within, and only then send it on to whatever flies the aircraft. Betaflight is the firmware that flies it, and this is a request for comment about that boundary (cross-citation only, since Betaflight is GPL-3.0).

To be clear about what URML is not: it does not fly the aircraft, does not touch stabilization, and is not a layer Betaflight needs in order to work. It sits above the firmware. What it adds is a typed, checkable statement of a flight intent plus its operating bounds (geometry, speed, the conditions under which a maneuver is permitted), validated against the craft's declared capabilities before anything is dispatched.

So two honest questions for people who live in this firmware: does that validation belong above the firmware at all, or does the relevant safety reasoning already sit in Betaflight and the configurator where it can see the real state? And if a craft's operating envelope were written down separately, would it line up with how Betaflight already describes a craft's limits, or would the two drift apart?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0576-betaflight-outreach.md

Thanks for Betaflight; it flies an enormous fleet, which is exactly why I wanted to ask the people who know its limits best.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0577: INAV

**Post to (Issue):** https://github.com/iNavFlight/inav/issues/new
**Title:** URML (open robot intent language): a declared, validated mission intent above INAV (request for comment)

```
Hi INAV maintainers,

INAV is navigation-first, which is what brought me here rather than to a stabilization-focused firmware. A waypoint mission with a geofence, altitude bounds, and a return-to-home condition is, in language terms, a goal plus constraints. That is exactly the shape URML (urml.dev, a small Apache-2.0 robot-intent language) is built to declare and check. This is a request for comment (cross-citation only, since INAV is GPL-3.0).

The mapping is direct: URML declares the mission as intent plus bounds, validates it against the craft's declared capabilities and a safety envelope, then hands it to INAV to fly. INAV keeps full ownership of navigation and control; URML is the checkable statement of what the mission is and whether the craft may do it. The geofence and failsafe conditions INAV already enforces are, in URML terms, a safety envelope, so an inadmissible mission could be rejected before upload rather than discovered in the air.

Two questions: does a declared, validated mission intent fit how INAV missions are actually defined and uploaded? And do INAV's existing geofence and failsafe bounds correspond closely enough to a written-down safety envelope that a shared representation would be worth anything?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0577-inav-outreach.md

Thanks for INAV; autonomous missions are where a declared, checkable intent earns its keep, and INAV is the clearest place in this firmware family to ask.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0578: FluidNC

**Post to (Issue):** https://github.com/bdring/FluidNC/issues/new
**Title:** URML (open robot intent language): a validated job-intent layer above FluidNC (request for comment)

```
Hi FluidNC maintainers,

A motion job has hard limits baked into the machine: axis travel, feed and acceleration ceilings, the work envelope. URML (urml.dev, a small Apache-2.0 robot-intent language) is built around exactly that kind of check: declare the job as intent plus its bounds, validate it against what the machine can actually do, and only then dispatch. FluidNC is the firmware that drives the motion. This is a request for comment.

URML does not generate steps and does not move the machine. It sits above FluidNC as a typed, checkable statement of a job and the envelope it must stay inside, validated against the machine's declared capabilities before anything runs. FluidNC's per-machine configuration (axes, limits) is already close in spirit to that capability description, which is what made me think the two might line up.

Two questions: is a validated job-intent layer useful above FluidNC, or is the machine config plus FluidNC's own checks already where that reasoning belongs? And does FluidNC's machine configuration map onto an external capability description closely enough to be worth sharing rather than duplicating?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0578-fluidnc-outreach.md

Thanks for FluidNC; a clean ESP32 motion firmware with explicit machine limits is a natural place to test whether a job-level intent check pulls its weight.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0579: Tock OS

**Post to (Issue):** https://github.com/tock/tock/issues/new
**Title:** URML (open robot intent language): lining up a capability manifest with Tock's capability model (request for comment)

```
Hi Tock maintainers,

The reason I am writing to Tock specifically, and not to RTOS projects in general, is capabilities. Tock bounds what each component may do at the OS level; URML (urml.dev, a small Apache-2.0 robot-intent language) bounds what an intent may do by checking it against a declared capability manifest at the language level. Two projects, two layers, the same instinct that capability is the right unit for "what is permitted." This is a request for comment about whether those two notions usefully line up.

Here is the concrete thought. A minimal URML executor (we have a constrained-target execution shape, RFC-0018) running as a Tock process would have its allowed actions bounded twice: once statically by the manifest, before anything runs, and once at runtime by Tock's grants. That might be a genuinely useful belt-and-suspenders, or the two notions of "capability" might not correspond closely enough to be worth aligning. I would rather ask the people who designed Tock's model than guess.

I will keep the honest caveat visible: URML sits well above an OS, so this is a narrow seam, not a grand integration.

Two questions: does a language-level capability manifest meaningfully correspond to Tock's OS-level capabilities, or are they different enough animals that lining them up buys nothing? And is a small, statically-validated intent executor a sensible shape for a Tock app at all?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0579-tock-outreach.md

Thanks for Tock; the capability model is genuinely interesting, and the overlap with a capability-checked intent layer felt worth thinking through with you.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0580: FreeRTOS

**Post to (Issue):** https://github.com/FreeRTOS/FreeRTOS/issues/new
**Title:** URML (open robot intent language): a minimal pre-validated executor as a FreeRTOS task (request for comment)

```
Hi FreeRTOS maintainers,

Let me lead with the altitude, because it matters: URML (urml.dev, a small Apache-2.0 robot-intent language) sits far above an RTOS. It is not a competitor to FreeRTOS, not a layer FreeRTOS needs, and most of what it does (validating an intent against a robot's capabilities and a safety envelope) happens off the microcontroller, ahead of time. So this is a deliberately narrow request for comment.

The one place the two actually touch is execution. After validation, what reaches a constrained target is an already-checked plan, run by a small executor. URML has a minimal MCU execution shape for this (RFC-0018), and FreeRTOS is the obvious substrate such an executor would live on. The honest question is whether that executor sits naturally as a FreeRTOS task and uses FreeRTOS primitives well, not whether FreeRTOS should know anything about URML. It should not, and would not need to.

Two questions, both about the device side: for a constrained target, is a small pre-validated intent executor a sensible thing to run as a FreeRTOS task, and are there primitives or patterns you would point it toward? And is "validate off the MCU, execute a checked plan on it" a reasonable discipline for keeping an intent layer honest about RTOS constraints?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0580-freertos-outreach.md

Thanks for FreeRTOS; it is the substrate half the embedded world runs on, so it is the right place to sanity-check whether the execution shape is realistic.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0581: Apache NuttX

**Post to (Issue):** https://github.com/apache/nuttx/issues/new
**Title:** URML (open robot intent language): a POSIX-friendly executor host, with a concrete PX4 path (request for comment)

```
Hi NuttX maintainers,

Same honest framing as I would give any RTOS: URML (urml.dev, a small Apache-2.0 robot-intent language) lives well above the OS, and validation mostly happens off the microcontroller. What brings me to NuttX in particular is two things: the POSIX-compatible API, and the fact that PX4 runs on NuttX while URML already maps onto PX4 as a substrate. So there is an existing, concrete path here rather than a hypothetical.

The seam is execution. A minimal URML executor (RFC-0018, our constrained-target shape) runs an already-validated plan, and NuttX's POSIX-like surface is a friendly host for one. Because the PX4-on-NuttX stack is real and URML already targets PX4, the most sensible first look is probably right there rather than in the abstract.

Two questions: does NuttX's POSIX compatibility make it a natural host for a small pre-validated intent executor on constrained targets? And given the existing PX4-on-NuttX path, is that the right concrete place to examine this, rather than a generic NuttX integration?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0581-nuttx-outreach.md

Thanks for NuttX; the POSIX discipline is exactly what makes hosting a small executor tractable, and the PX4 connection makes it more than theoretical.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0582: RIOT OS

**Post to (Issue):** https://github.com/RIOT-OS/RIOT/issues/new
**Title:** URML (open robot intent language): networked actuator nodes as members of a validated fleet (request for comment)

```
Hi RIOT maintainers,

RIOT's strength is low-power networked nodes, and that suggests a slightly different angle than the other RTOS notes I am writing. URML (urml.dev, a small Apache-2.0 robot-intent language) gets interesting exactly where a networked node is also a small actuator in a larger system. This is a request for comment, cross-citation only since RIOT is LGPL-2.1.

Two layers to the seam. On a single node that drives an actuator, a minimal URML executor (RFC-0018) can run a pre-validated intent. Across many such nodes, URML's multi-robot roster and cross-node constraints (RFC-0286, RFC-0291) give a way to declare and validate intent for the whole networked set, not just one device. URML targets RIOT as a substrate; it does not ask RIOT to depend on or know about it, and proposes no shared code.

Two questions: for a RIOT node acting as a networked actuator, is a small pre-validated intent executor a sensible component? And does the idea of addressing a set of networked nodes as a validated fleet map onto how RIOT deployments are actually structured?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0582-riot-outreach.md

Thanks for RIOT; the networked-node focus is what made the fleet angle feel like the honest one to lead with here.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0583: Contiki-NG

**Post to (Issue):** https://github.com/contiki-ng/contiki-ng/issues/new
**Title:** URML (open robot intent language): an honest note about a thin seam with a sensing-first OS (request for comment)

```
Hi Contiki-NG maintainers,

I want to be upfront: this is the most exploratory note in a small batch I am sending to embedded OS projects, and the seam with Contiki-NG is genuinely thin. Contiki-NG's center of gravity is low-power sensing and networking, and URML (urml.dev, a small Apache-2.0 robot-intent language) is about validated actuation intent. Those do not overlap much, and I would rather say so than pretend otherwise.

Where they do touch is narrow. If a Contiki-NG node also actuates, a minimal URML executor (RFC-0018) could run a pre-validated intent on it, and that node could be one member of a URML-addressed fleet. But the more natural connection probably runs the other way: Contiki-NG sensor data is exactly the kind of fact a URML intent elsewhere conditions on. URML consumes such facts; it does not produce them.

So, genuinely asking rather than pitching: in deployments where a Contiki-NG node actuates and does not only sense, is a small pre-validated intent executor a sensible component? Or is the sensor-data-as-an-input-fact framing the only connection that actually makes sense for a sensing-first OS?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0583-contiki-ng-outreach.md

Thanks for Contiki-NG; even if the answer is "the seam is too thin to bother," that is useful for me to hear from the people who know the platform.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0584: Embassy

**Post to (Issue):** https://github.com/embassy-rs/embassy/issues/new
**Title:** URML (open robot intent language): a minimal pre-validated executor built on Embassy (request for comment)

```
Hi Embassy maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent, and its longer-running infrastructure leans toward Rust on purpose. On the device side, the piece that would touch Embassy is a minimal executor for constrained targets (RFC-0018): it runs an already-validated plan, asynchronously, close to the hardware. That is squarely the kind of thing Embassy is built to make pleasant. This is a request for comment.

The pairing feels natural for two reasons. First, the executor wants an ergonomic async embedded foundation, and Embassy is one of the best of those. Second, URML leans on types for its guarantees and Rust enforces a lot of that for free, so a Rust-side executor and URML's typed intent model fit together rather than fighting.

Two questions, both practical: is a small, pre-validated intent executor (async, constrained targets) a sensible thing to build on Embassy? And are there Embassy patterns you would steer it toward, particularly around timing and peripheral access?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0584-embassy-outreach.md

Thanks for Embassy; modern async embedded Rust is exactly the foundation a small typed executor wants to stand on.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0585: RTIC

**Post to (Issue):** https://github.com/rtic-rs/rtic/issues/new
**Title:** URML (open robot intent language): mapping declared cyclic timing onto an RTIC task set (request for comment)

```
Hi RTIC maintainers,

RTIC's predictable, priority-based scheduling is the specific thing that brought me here. URML (urml.dev, a small Apache-2.0 robot-intent language) recently grew a real-time timing block (RFC-0016) that lets a manifest declare cyclic timing and a watchdog as part of what a robot requires. A declared timing requirement is only as good as the substrate that can honor it, and RTIC is exactly the kind of substrate where such a claim could be checked rather than hoped for. This is a request for comment.

The seam is concrete. URML says, in effect, "this intent needs a 10 ms cycle with this watchdog." RTIC actually schedules tasks with timing you can reason about. The question is whether URML's declared timing can map onto an RTIC task set so that the timing claim becomes checkable against what RTIC guarantees, rather than a number in a manifest that nothing verifies. A minimal URML executor (RFC-0018) that carries timing requirements is a natural fit for that model.

Two questions: can declared cyclic-timing requirements map onto an RTIC task set in a way that makes the claim checkable? And is a small, pre-validated intent executor with timing requirements a sensible thing to express in RTIC?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0585-rtic-outreach.md

Thanks for RTIC; predictable real-time scheduling is what turns a declared timing requirement from a wish into something you can check, which is why I wanted your read.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```
