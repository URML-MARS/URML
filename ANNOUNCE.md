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

# URML — a verification layer between language models and robots

**An LLM can propose a robot action. URML statically refuses the unsafe ones
before a single actuator moves — and hands back a structured error precise
enough for the model to correct itself.**

That sentence is the whole project. Everything below is how it's real.

## The problem

"Let an LLM drive the robot" is one prompt-injection or one confident
hallucination away from a machine doing something dangerous. The usual answer —
"add guardrails in the prompt" — is not a safety boundary; it's a suggestion.

## What URML is

A small, opinionated, human-readable language for robot **intent**, plus a
five-pass static validator that sits *above* the substrate (ROS 2, PX4,
vendor SDKs) and *below* the language model. The model proposes; the validator
verifies against the robot's declared capabilities, the active safety envelope,
and a deployment compliance policy. Only a program that passes all five passes
is allowed to reach an actuator. Proposal and verification are separated, and
the verifier is not optional.

URML is a **specification** plus **reference implementations**, Apache-2.0
forever for the core (see `CORE_COMMITMENT.md`). It is not a robot operating
system; it targets the ones that exist.

## Why it's credible, not vapor

- **Five-pass validator** — argument typing → capability → safety envelope
  (incl. geofence, 3D altitude bands, people-occupancy zones) → variable +
  cross-primitive type analysis → compliance policy. 188 tests.
- **Two real reference runtimes** — `RclpyAdapter` (ROS 2, via `rclpy`/Nav2)
  and `PX4Adapter` (MAVLink, no ROS dependency), plus a `CompositeAdapter`
  that runs one program across a PX4 flight controller + a ROS 2 companion.
- **End-to-end verified** — a conformance fixture drives a *simulated
  TurtleBot 4* through Nav2 via the real adapter, green on three independent
  CI runs. Not "should work" — reproduced.
- **Compliance is enforced, not documented** — the bundled default policy
  encodes US-federal procurement rules (NDAA §889/FY26, FCC Covered List, EO
  14307, ASRA); a covered-foreign-country component is rejected *at validation
  time*. Override is one flag for other jurisdictions.
- **473 tests across five packages**, all green. Every front-page claim is
  mapped to a file and a passing run in [`docs/launch/claims-audit.md`](docs/launch/claims-audit.md).

## See it in 90 seconds

- **The safety story:** [`docs/demos/safety-rejection.md`](docs/demos/safety-rejection.md)
  — an LLM-shaped drone program that would fly over a spectator area; URML
  refuses it pre-flight, returns the machine-readable error, the re-routed
  program passes. Every command's output is pasted verbatim.
- **The compliance story:** [`docs/demos/compliance-walkthrough.md`](docs/demos/compliance-walkthrough.md)
  — the same program, three manifests, the covered-component rejection, the override.

## Try it

```bash
git clone https://github.com/URML-MARS/URML.git && cd URML
python bootstrap.py
make demo            # → Validation passed
```

One command, any OS, fully reversible. The full case is in
[`MANIFESTO.md`](MANIFESTO.md); the design history is the numbered RFCs in
[`docs/rfcs/`](docs/rfcs/).

## What this is not

Passing the validator is a static guarantee about *declared* capabilities and
the *declared* envelope — not a substitute for real flight authorization,
airspace deconfliction, or counsel review. URML refuses programs that violate
the declared envelope; it cannot verify the declared envelope matches the
world. That boundary is the deployer's, and we say so on every demo.
