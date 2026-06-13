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

# Move #46 post bodies: the AI / robot-learning wave

Eight targets, all GitHub Issues. Post under idoco2003. No license-ask anywhere
(roboflow core is Apache-2.0; do not ask). AI-assisted-authoring disclosure up
front. Titles carry no em-dash.

Shared thesis (RFC-0383 LearnedPolicy + RFC-0002 decide-then-do): a trained
policy, or the benchmark/eval it was measured in, declares the capability
envelope it was trained/evaluated in; URML carries that and validates each
proposed action against the robot's declared capabilities + a safety envelope
before dispatch. The policy decides; URML is the typed gate that does.

---

## RFC-0510: RoboHive (anchor)

**Post to (Issue):** https://github.com/vikashplus/robohive/issues/new
**Title:** URML (open robot intent language): a deployment envelope + validated-intent gate for RoboHive policies (request for comment)

```
Hi RoboHive community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. RoboHive is a unified framework for robot learning, and URML is interesting at the deployment boundary: a policy trained in RoboHive carries observation/action spaces and a training domain, and URML has a "LearnedPolicy" declaration that lets a policy publish those bounds so a deployment is validated against the domain it was actually trained for.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

Two seams: (1) envelope export -- a RoboHive env defines the obs/action spaces and the domain a policy trains against; emitting those as a URML deployment envelope makes "what was this policy trained for" a typed, checkable artifact next to the weights. (2) validated deployment -- URML then sits between the trained policy and the robot, checking each proposed action against the robot's declared capabilities + the safety envelope before dispatch. The policy decides; URML is the typed gate.

Two real questions: (1) does exporting a trained policy's spaces + training-domain bounds as a declared deployment envelope make sense as an optional artifact? (2) Is a validated-intent gate between a RoboHive policy and a real robot interesting -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0510-robohive-outreach.md

Thanks for RoboHive; a unified learning framework is a natural place to ask where a deployment envelope and a validation gate fit.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0511: SimplerEnv

**Post to (Issue):** https://github.com/simpler-env/SimplerEnv/issues/new
**Title:** URML (open robot intent language): a policy's eval setup as a deployment envelope (request for comment)

```
Hi SimplerEnv community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. SimplerEnv reproduces real-robot manipulation policy evals in sim, and the embodiment and task a policy is scored in is exactly the envelope a deployment should be validated against.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: the embodiment, observation/action spaces, and task distribution a policy is scored in under SimplerEnv map onto a URML "LearnedPolicy" deployment envelope. A deployment can then be validated against the setup the policy's numbers were actually obtained in -- and URML checks each proposed action against the robot's declared capabilities + the safety envelope before dispatch, so an out-of-eval-distribution action is caught before it reaches hardware.

Two real questions: (1) does declaring a policy's evaluation setup (embodiment + obs/action spaces + task distribution) as a URML deployment envelope make sense? (2) Is a validated-intent gate that checks a deployment matches the eval setup interesting -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0511-simplerenv-outreach.md

Thanks for SimplerEnv; tying deployment validity back to the eval setup is exactly the gap a declared envelope closes.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0512: CALVIN

**Post to (Issue):** https://github.com/mees/calvin/issues/new
**Title:** URML (open robot intent language): typed intent on the language seam + a learned-task envelope for CALVIN (request for comment)

```
Hi CALVIN community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: a language instruction becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. CALVIN sits squarely on URML's main seam -- language in, robot action out -- so the two are unusually aligned.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

Two seams: (1) typed intent on the language seam -- CALVIN evaluates language-conditioned policies, and URML is a typed, validatable representation of exactly that language-to-intent step; a long-horizon CALVIN task can be expressed as a URML composition of typed primitives, each checkable against the manifest. (2) learned-task envelope -- a CALVIN-trained policy carries the obs/action spaces and the task distribution it learned, and URML's "LearnedPolicy" declaration lets it publish those bounds so a deployment is validated against the domain it was trained for.

Two real questions: (1) is a typed, validatable representation of the language-to-intent step useful alongside a language-conditioned benchmark? (2) Does declaring a trained policy's learned task envelope as a URML LearnedPolicy make sense -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0512-calvin-outreach.md

Thanks for CALVIN; language-conditioned long-horizon manipulation is the exact path URML is built around.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0513: RoboEval

**Post to (Issue):** https://github.com/Robo-Eval/RoboEval/issues/new
**Title:** URML (open robot intent language): per-skill bimanual diagnostics as declared capabilities (request for comment)

```
Hi RoboEval community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. RoboEval is a structured bimanual-manipulation benchmark with per-skill diagnostics, and the skills you measure map onto declared capability stages a deployment can be bounded against.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: RoboEval's per-skill, bimanual structure lines up with URML's manipulation model -- a two-arm task declares its arms (manipulation.arms) and uses a bimanual primitive. The skill a policy is measured on is the capability a deployment declares it can do. And a policy scored on RoboEval can carry, via URML's "LearnedPolicy" declaration, the obs/action spaces and task distribution it was scored in, so a deployment is validated against that envelope.

Two real questions: (1) do RoboEval's per-skill, bimanual diagnostics map cleanly onto URML's declared capabilities (manipulation.arms + a bimanual primitive)? (2) Is declaring a scored policy's evaluation envelope as a URML LearnedPolicy useful -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0513-roboeval-outreach.md

Thanks for RoboEval; structured per-skill bimanual diagnostics are a clean match for declared capability stages.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0514: robo-gym

**Post to (Issue):** https://github.com/jr-robotics/robo-gym/issues/new
**Title:** URML (open robot intent language): an env-to-envelope + sim-to-real gate for robo-gym (request for comment)

```
Hi robo-gym community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. robo-gym does distributed deep RL on real and simulated robots (with real UR and MiR envs), and URML is interesting right at that sim-to-real boundary.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

Two seams: (1) env to envelope -- a robo-gym environment defines the obs/action spaces and the (real or simulated) domain a policy trains against; emitting those as a URML "LearnedPolicy" envelope makes the training domain a typed, checkable artifact. (2) validated deployment -- URML's gate sits at the sim-to-real boundary, checking each proposed action against the robot's declared capabilities + the safety envelope before dispatch, so an out-of-distribution action is caught before it reaches a UR or MiR.

Two real questions: (1) does exporting a robo-gym env's spaces + domain bounds as a URML deployment envelope make sense for the real-robot side? (2) Is a validated-intent gate at the sim-to-real boundary interesting -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0514-robo-gym-outreach.md

Thanks for robo-gym; explicit real-hardware envs make the deployment boundary unusually concrete.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0515: Roboflow Inference

**Post to (Issue):** https://github.com/roboflow/inference/issues/new
**Title:** URML (open robot intent language): the perception-to-action handoff above Roboflow Inference (request for comment)

```
Hi Roboflow Inference community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. Roboflow Inference turns any device into a vision inference server, and on a robot perception feeds action -- which is exactly the handoff URML gates.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: Roboflow Inference produces typed perception outputs (detections, masks). URML consumes a perception result as the condition for a typed primitive, then validates the resulting action against the manifest and safety envelope before it reaches the robot. URML is the perception-to-action gate; it does not do the inference. Separately, a served model's classes map toward a URML perception capability declaration, so a program that conditions on "detect the mug" is checkable.

Two real questions: (1) is "Roboflow Inference perceives, URML validates the action it conditions" a sensible description of the perception-to-action handoff on a robot? (2) Could a served model's classes inform a URML perception capability declaration -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0515-roboflow-inference-outreach.md

Thanks for Inference; edge perception feeding action is exactly where a validated handoff matters on a robot.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0516: ExecuTorch

**Post to (Issue):** https://github.com/pytorch/executorch/issues/new
**Title:** URML (open robot intent language): a validated-action gate above on-device policy inference (request for comment)

```
Hi ExecuTorch community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. ExecuTorch runs PyTorch models on-device, including the edge compute a robot carries to run a learned policy, and URML is interesting one layer above the inference runtime.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The layering: a policy deployed to a robot's edge compute runs under ExecuTorch; the action it produces is then checked by URML against the robot's declared capabilities + the active safety envelope before dispatch. ExecuTorch is the runtime that computes the action; URML is the typed gate that decides whether to dispatch it. The model ExecuTorch runs has the obs/action spaces and training domain a URML "LearnedPolicy" declaration records, so the on-device policy carries the bounds the gate enforces.

Two real questions: (1) is "ExecuTorch runs the policy on-device, URML validates the action before dispatch" a sensible description of the layering for a robot? (2) Is a LearnedPolicy envelope traveling with an on-device model useful for the robotics-deployment case -- and is an inference runtime the right altitude to engage?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0516-executorch-outreach.md

Thanks for ExecuTorch; on-device policy inference is exactly the do layer a validated-action gate wants to sit above.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0517: openrlbenchmark

**Post to (Issue):** https://github.com/openrlbenchmark/openrlbenchmark/issues/new
**Title:** URML (open robot intent language): from tracked RL run metadata to a deployment envelope (request for comment)

```
Hi openrlbenchmark community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent. It is a layer removed from RL experiment tracking, but it shares your premise: a policy should be described by the conditions it was trained and evaluated under. URML's "LearnedPolicy" declaration captures exactly those conditions for the deployment side, and several of the libraries you track (stable-baselines3, CleanRL and others) are ones we have engaged separately.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The connection: openrlbenchmark records the environments, configurations, and results of RL runs. The same metadata that makes a run comparable (the env, the spaces, the domain) is what a URML deployment envelope carries to the deployment, so a policy is validated against the conditions it was trained and measured under. Both projects insist a policy is only meaningful relative to a declared setup -- you make that explicit for comparison, URML makes it explicit for safe deployment.

Two real questions: (1) is there a useful path from the run metadata you track to a URML deployment envelope? (2) Is the shared "a policy is defined by its declared training/eval setup" framing worth a cross-reference for users who go from benchmark to deployment?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0517-openrlbenchmark-outreach.md

Thanks for openrlbenchmark; the discipline of describing a policy by its declared setup is exactly the one a deployment envelope depends on.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```
