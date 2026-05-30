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

# Move #12 post bodies — speech / translation / robot-command-library

Copy-paste-ready Issue / Discussion bodies for the Move #12 outreach. **Wave shape**: 16 engageable targets across the projects that produce the inputs and substrates for URML's Layer-4 NL grammar (STT, TTS, translation) and the libraries URML's Layer-3 behavior composition would compile down to (behavior-tree / skill-catalog DSLs). 12 Tier A vendor-direct / research-lab-direct + 4 Tier B with explicit friction notes (commercial-SDK, GPL, archived + CC-BY-NC, AGPL). Verified 2026-05-28. RFC numbers 0153-0168.

Ledger state: [`outreach-move12.yaml`](outreach-move12.yaml). Full research audit: [`move12-research-2026-05-28.md`](move12-research-2026-05-28.md).

Voice: founder posts under his GitHub identity. Each post opens with "Hi <team>" and addresses the maintainers directly.

**Confidentiality discipline.** Per the outreach-confidentiality rule, public post bodies do NOT name or link to previously engaged URML maintainers as social proof. URML's own shipped artifacts and RFCs in `docs/rfcs/` are fine to cite. Aggregate counts ("twelve outreach waves to date") are fine. Naming the specific orgs that responded is not.

**Authoring disclosure.** Per [`AGENTS.md`](../../AGENTS.md) + [`VIBE.md`](../../VIBE.md), every Move #12 post ends with the shortened authoring-disclosure line.

**Disclosure paragraph (reused verbatim at the bottom of every post body):**

```
*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

**Schema-extension flags.** Move #12 surfaces multiple v0.1 schema gaps that should be opened as Spec RFCs in parallel (not bundled into the per-target outreach RFCs):

- **STT-engine-class declaration** (Whisper RFC-0153, faster-whisper RFC-0154, whisper.cpp RFC-0155).
- **STT-inference-runtime declaration** (faster-whisper RFC-0154, whisper.cpp RFC-0155).
- **Runtime-dependency-profile declaration** (whisper.cpp RFC-0155 surfaces it for STT; Marian RFC-0159 reuses it for translation; symmetric across speech-IO and translation).
- **TTS-engine-class declaration** (OpenVoice RFC-0156, piper1-gpl RFC-0166).
- **Translation-engine-class declaration** (OPUS-MT RFC-0157, Argos RFC-0158, Marian RFC-0159, NLLB RFC-0167, LibreTranslate RFC-0168).
- **Translation-runtime declaration** (Marian RFC-0159, LibreTranslate RFC-0168).
- **Model-license declaration + commercial-use validator gate** (NLLB RFC-0167; generalizes beyond translation).
- **Network-endpoint runtime declaration** (LibreTranslate RFC-0168).
- **Substrate license-boundary declaration** (LibreTranslate RFC-0168 surfaces `agpl_network_boundary`; piper1-gpl RFC-0166 surfaces `gpl_subprocess`; unified Spec RFC covers both shapes).
- **Secret-reference declaration** (LibreTranslate RFC-0168; generalizes for any manifest field pointing at a secret store).
- **Behavior-tree-runtime declaration** (BehaviorTree.CPP RFC-0160, py_trees RFC-0161; different language tags).
- **Manipulation-substrate declaration + URML-primitive-to-MTC-stage mapping** (MoveIt Task Constructor RFC-0162).
- **Skill-framework declaration + knowledge-graph substrate declaration + skill-grounding-mode declaration** (SkiROS2 RFC-0163).
- **Orchestration-framework declaration + execution-model enumeration** (LangGraph RFC-0164; shares Spec RFC with prior smolagents RFC-0143 + Gemini SDK RFC-0145).
- **Wake-word substrate declaration + substrate license-tier declaration + wake-word-to-STT handoff declaration** (Porcupine RFC-0165).

Each is a separate Spec RFC; URML's outreach RFCs ship with the v0.1 `custom` controller_class / sensor_class escape-hatch and reference the queued Spec RFC.

---

## Tier A — 12 vendor-direct / research-lab-direct targets

### RFC-0153: OpenAI Whisper

**Post to:** https://github.com/openai/whisper/discussions/new (Show-and-tell category)

**Title:**

```
Proposal: URML (substrate-neutral robot intent) manifest declaration for Whisper as the multilingual `listen` substrate
```

**Body:**

```markdown
Hi @openai/whisper team,

Proposing a URML v0.1 capability-manifest mapping for Whisper over `openai/whisper`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: a typed primitive vocabulary plus a Layer-1 capability manifest and a validator that gates programs against the manifest before any actuator publishes.

Whisper is the reference multilingual STT. URML's Layer-2 `listen` primitive consumes Whisper transcripts as the input to URML's natural-language bridge; URML's Layer-4 reserves multilingual slots (English content; Hebrew, Spanish, Japanese, Mandarin reserved in v0.1) that Whisper's 99-language coverage maps onto directly. Engaging through Discussions since Issues are disabled on this repo.

**This is proposal-only**, the first RFC of URML's Move #12 outreach (16 RFCs covering speech / translation / robot-command-library substrates for URML's NL layer).

Full RFC with manifest mapping, three alternatives, and the inference-runtime fragmentation discussion: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0153-whisper-outreach.md

Questions worth maintainer input on:

1. **Engagement channel.** Discussions Q&A or Show-and-tell? URML's post is a design-discussion request, not a bug report.
2. **STT-engine-class declaration shape.** URML needs to distinguish the Whisper *family* from the inference *runtime* (`openai-reference` vs. CTranslate2 vs. ggml). Does the OpenAI team have a preferred convention?
3. **Multilingual labelling.** Whisper auto-detects source language; URML's manifest declares an explicit `stt_languages` list for static validation. Is the explicit list a useful downstream signal, or is auto-detect the canonical default?
4. **Decode-mode boundary.** Whisper's built-in `translate` mode overlaps URML's separate translation-engine layer. Is one of these modes the canonical URML default, or should the manifest support both?
5. **Cadence expectation.** Is `openai/whisper` actively monitoring Discussions, or has the active community moved to faster-whisper / whisper.cpp?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0154: SYSTRAN faster-whisper

**Post to:** https://github.com/SYSTRAN/faster-whisper/discussions/new (Ideas category)

**Title:**

```
Proposal: URML (substrate-neutral robot intent) manifest declaration for faster-whisper as the realtime `listen` substrate
```

**Body:**

```markdown
Hi @SYSTRAN/faster-whisper team,

Proposing a URML v0.1 capability-manifest mapping for faster-whisper over `SYSTRAN/faster-whisper`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: typed primitive vocabulary + capability manifest + static validator.

faster-whisper is the CTranslate2-accelerated Whisper inference engine that closes the realtime-latency gap for URML's Layer-2 `listen` primitive on resource-constrained robots. URML's manifest declares the Whisper family (shared with the reference Whisper and whisper.cpp) plus the inference runtime (`ctranslate2` here); the quantization-level and latency-class fields are CTranslate2-specific knobs URML's manifest needs to model.

**This is proposal-only**, part of URML's Move #12 outreach (16 RFCs covering speech / translation / robot-command-library substrates for URML's NL layer).

Full RFC with manifest mapping, three alternatives, and the runtime-fragmentation design discussion: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0154-faster-whisper-outreach.md

Questions worth maintainer input on:

1. **STT-inference-runtime declaration.** Would faster-whisper benefit from URML's manifest declaring the runtime explicitly (e.g., a README badge "URML manifest declares `stt_inference_runtime: ctranslate2`"), or is this internal detail?
2. **Realtime-class declaration.** Does the faster-whisper team have a benchmarking convention for declaring "realtime on platform X" that URML's `stt_realtime_class` field could reference?
3. **Quantization declaration.** Is `int8 / float16 / float32` the right granularity, or should URML's manifest list specific CTranslate2 quantization presets (`int8`, `int8_float16`, `int8_bfloat16`, …)?
4. **Adapter home.** URML's `reference/speech-bridge/`, contributed example in `SYSTRAN/faster-whisper/examples/`, or external bridge repo?
5. **Org migration handling.** Is `SYSTRAN/faster-whisper` the URL going forward, or do historical references to `guillaumekln/faster-whisper` still need to coexist?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0155: ggml-org whisper.cpp

**Post to:** https://github.com/ggml-org/whisper.cpp/discussions/new (Ideas category)

**Title:**

```
Proposal: URML (substrate-neutral robot intent) manifest declaration for whisper.cpp as the embedded `listen` substrate
```

**Body:**

```markdown
Hi @ggml-org/whisper.cpp team,

Proposing a URML v0.1 capability-manifest mapping for whisper.cpp over `ggml-org/whisper.cpp`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: typed primitive vocabulary + capability manifest + static validator.

whisper.cpp is the embedded substrate that closes URML's Layer-2 `listen` primitive on Layer-1 robots without Python — PX4 / NuttX, vendor RTOSes, microcontroller-class boards. URML's manifest needs a runtime-dependency-profile field (no_python / libc_only / rtos) that whisper.cpp's deployment profile is the canonical example of; the field generalizes to other embedded substrates URML will engage.

**This is proposal-only**, part of URML's Move #12 outreach (16 RFCs covering speech / translation / robot-command-library substrates for URML's NL layer).

Full RFC with manifest mapping, three alternatives, and the no-Python deployment design discussion: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0155-whisper-cpp-outreach.md

Questions worth maintainer input on:

1. **STT-inference-runtime declaration.** Would whisper.cpp benefit from URML's manifest declaring the runtime explicitly (`stt_inference_runtime: ggml`), or is this internal detail?
2. **Runtime-dependency-profile declaration.** Does the whisper.cpp team have a convention for documenting "this build requires libc only, no Python, no CUDA"? URML's `stt_runtime_dependency_profile` field would reflect that.
3. **ggml-quantization declaration.** Is the q4_0 / q4_1 / q5_0 / q8_0 / f16 / f32 enumeration the right granularity, or should it be a free-form ggml-quant-string?
4. **Adapter home.** URML-side adapter calling whisper.cpp via subprocess in `reference/speech-bridge/`, contributed example in `whisper.cpp/examples/`, or external bridge repo?
5. **Org-migration handling.** Is `ggml-org/whisper.cpp` the URL going forward, or should historical `ggerganov/whisper.cpp` references still be honored in URML's documentation?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0156: MyShell OpenVoice

**Post to:** https://github.com/myshell-ai/OpenVoice/discussions/new (Ideas category)

**Title:**

```
Proposal: URML (substrate-neutral robot intent) manifest declaration for OpenVoice as the `speak` substrate (URML's first TTS engagement)
```

**Body:**

```markdown
Hi @myshell-ai/OpenVoice team,

Proposing a URML v0.1 capability-manifest mapping for OpenVoice over `myshell-ai/OpenVoice`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: typed primitive vocabulary + capability manifest + static validator.

This is URML's first TTS RFC. URML's Layer-2 `speak` primitive renders text output to audio; the zero-shot voice-cloning angle is the OpenVoice contribution URML wants to declare — a single reference clip lets a robot fleet share one consistent voice identity across deployments, and the cross-lingual capability pairs directly with URML's Layer-4 multilingual structural-slot reservation.

**This is proposal-only**, part of URML's Move #12 outreach (16 RFCs covering speech / translation / robot-command-library substrates for URML's NL layer).

Full RFC with manifest mapping, three alternatives, and the voice-clone-reference design discussion: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0156-openvoice-outreach.md

Questions worth maintainer input on:

1. **TTS-engine-class declaration shape.** Does the OpenVoice team have a preferred convention for declaring "OpenVoice is the TTS engine" in a downstream manifest, or is this internal detail?
2. **Voice-clone-reference declaration.** Is a manifest field that names the reference voice clip URI useful (for downstream consent / audit), or does it introduce a privacy footprint the project would rather not have associated with it?
3. **Voice-style enumeration.** Is the preset set stable enough for URML's manifest to declare an enum, or is it evolving fast enough that a free-form string is the right shape?
4. **Multilingual coverage.** OpenVoice supports cross-lingual cloning. What is the canonical set of synthesis languages URML's manifest should list (README authoritative)?
5. **Adapter home.** URML-side adapter in URML's `reference/speech-bridge/`, contributed example in `OpenVoice/examples/`, or external bridge repo?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0157: Helsinki-NLP OPUS-MT

**Post to:** https://github.com/Helsinki-NLP/OPUS-MT-train/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) manifest declaration for OPUS-MT as the multilingual translation substrate
```

**Body:**

```markdown
Hi @Helsinki-NLP team,

Proposing a URML v0.1 capability-manifest mapping for OPUS-MT over `Helsinki-NLP/OPUS-MT-train`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: typed primitive vocabulary + capability manifest + static validator.

This is URML's first translation RFC. URML's Layer-4 reserves multilingual structural slots (English content; Hebrew, Spanish, Japanese, Mandarin reserved in v0.1) — OPUS-MT's 300+ language-pair coverage maps onto every slot URML has reserved, with one MIT-clean toolkit and license. The per-pair model architecture is the right granularity for URML's manifest to declare which pairs a deployment supports.

**This is proposal-only**, part of URML's Move #12 outreach (16 RFCs covering speech / translation / robot-command-library substrates for URML's NL layer).

Full RFC with manifest mapping, three alternatives, and the HuggingFace-URI scheme discussion: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0157-opus-mt-train-outreach.md

Questions worth maintainer input on:

1. **Translation-engine-class declaration shape.** Is `opus_mt` + per-pair model URI the right granularity for URML's manifest, or does the OPUS-MT team prefer a different convention?
2. **Per-pair vs. multilingual models.** OPUS-MT publishes per-pair models predominantly. Is the per-pair list the right abstraction, or is a multilingual one-model-many-pairs direction worth declaring?
3. **HuggingFace-URI scheme.** Is `huggingface://Helsinki-NLP/opus-mt-{src}-{tgt}` the right URI shape for pointing at a specific model, or does the team have a preferred URI / path?
4. **Marian-runtime coupling.** Is Marian the canonical OPUS-MT inference runtime URML should declare, or are alternatives (CTranslate2, custom) the rising default?
5. **License coverage.** Per-pair model weights on HuggingFace appear CC0 / Apache-2.0; the OPUS-MT-train code is MIT. Is this distinction stable across all pairs?
6. **Adapter home.** URML-side adapter in URML's `reference/translation-bridge/`, contributed example in `OPUS-MT-train/examples/`, or external bridge repo?
7. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0158: Argos Translate

**Post to:** https://github.com/argosopentech/argos-translate/discussions/new (Ideas category)

**Title:**

```
Proposal: URML (substrate-neutral robot intent) manifest declaration for Argos Translate as the offline-on-device translation substrate
```

**Body:**

```markdown
Hi @argosopentech team,

Proposing a URML v0.1 capability-manifest mapping for Argos Translate over `argosopentech/argos-translate`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: typed primitive vocabulary + capability manifest + static validator.

URML's reference runtimes execute fully offline once validated (no cloud dependency at runtime). The Layer-4 translation path needs an in-process MIT-clean substrate that preserves that invariant; Argos is the only credible Tier A option. URML's manifest declares Argos as the runtime, OPUS-MT as the upstream model source (separately engaged), and the pair-install class (bundled / on-demand / user-install) as the deployment-shape signal.

**This is proposal-only**, part of URML's Move #12 outreach (16 RFCs covering speech / translation / robot-command-library substrates for URML's NL layer).

Full RFC with manifest mapping, three alternatives, and the no-cloud invariant discussion: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0158-argos-translate-outreach.md

Questions worth maintainer input on:

1. **Translation-engine-class declaration shape.** Is `argos_translate` + per-pair list the right granularity for URML's manifest, or does the team prefer a different naming?
2. **Pair-install-class declaration.** Is `bundled \| on_demand \| user_install` the right enumeration, or does the model-install lifecycle have other modes?
3. **Offline / no-cloud declaration.** Is an explicit `translation_offline: true` manifest field useful as a downstream signal, or unnecessary (since Argos is inherently offline)?
4. **Composition with OPUS-MT.** Is OPUS-MT the canonical upstream Argos should declare, or are alternatives (custom-trained, NLLB-derived) common enough to enumerate?
5. **Adapter home.** URML's `reference/translation-bridge/`, contributed example in `argos-translate/examples/`, or external bridge repo?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0159: Marian-NMT

**Post to:** https://github.com/marian-nmt/marian-dev/discussions/new (Ideas category)

**Title:**

```
Proposal: URML (substrate-neutral robot intent) manifest declaration for Marian-NMT as the C++ translation runtime — plus license-clarification ask
```

**Body:**

```markdown
Hi @marian-nmt team,

Proposing a URML v0.1 capability-manifest mapping for Marian-NMT over `marian-nmt/marian-dev`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: typed primitive vocabulary + capability manifest + static validator.

Marian is the research-backbone inference runtime beneath URML's Move #12 translation cluster: OPUS-MT trains and publishes against Marian; Argos Translate embeds Marian inference. Engaging the upstream toolkit closes the loop on URML's translation-runtime declaration. The C++ deployment path symmetric to URML's embedded STT engagements (whisper.cpp) is the runtime-side mirror.

One housekeeping ask: GitHub reports `licenseInfo: Other` on the repo. URML's adapter cannot ship until the OSI classification is confirmed.

**This is proposal-only**, part of URML's Move #12 outreach (16 RFCs covering speech / translation / robot-command-library substrates for URML's NL layer).

Full RFC with manifest mapping, four alternatives, and the runtime-side declaration discussion: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0159-marian-dev-outreach.md

Questions worth maintainer input on:

1. **License clarification.** What is the explicit OSI license URML should cite? (MIT? Modified-MIT? Some Edinburgh-specific clause?)
2. **Translation-runtime declaration shape.** Is `marian` the right slug, or should URML distinguish the `marian` release branch from `marian-dev`?
3. **Runtime-dependency-profile.** URML's manifest will declare `translation_runtime_dependency_profile: no_python` for the C++ path. Does the team have a convention for declaring the deployment-substrate constraint?
4. **Quantization declaration.** Is `int8 / float16 / float32` the right granularity, or are there project-specific levels?
5. **Adapter home.** URML-side adapter in URML's `reference/translation-bridge/`, contributed example in `marian-dev/examples/`, or external bridge repo?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0160: BehaviorTree.CPP

**Post to:** https://github.com/BehaviorTree/BehaviorTree.CPP/discussions/new (Ideas category)

**Title:**

```
Proposal: URML (substrate-neutral robot intent) Layer-3 → BehaviorTree.CPP as a typed-intent compilation target
```

**Body:**

```markdown
Hi @BehaviorTree team,

Proposing a URML v0.1 capability-manifest mapping for BehaviorTree.CPP over `BehaviorTree/BehaviorTree.CPP`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: typed primitive vocabulary + Layer-3 behavior composition + capability manifest + static validator.

This is URML's first robot-command-library RFC. URML's Layer-3 (behavior composition) needs a substrate to compile down to; BehaviorTree.CPP is the dominant C++ choice in ROS 2 and standalone robotics, and the architectural mapping is direct — URML primitives become custom `TreeNode` subclasses, Layer-3 composition becomes BT XML. The "URML the typed-intent language → BT the executable graph → Groot the visualizer" pipeline gives URML programs the BT tooling ecosystem for free.

**This is proposal-only**, part of URML's Move #12 outreach (16 RFCs covering speech / translation / robot-command-library substrates for URML's NL layer).

Full RFC with manifest mapping, four alternatives, and the BT-XML schema-versioning discussion: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0160-behaviortree-cpp-outreach.md

Questions worth maintainer input on:

1. **Behavior-tree-runtime declaration shape.** Is `behaviortree_cpp` the right slug for URML's manifest, or do you prefer a different convention?
2. **BT XML schema version.** Which schema version (3.x vs. 4.x) should URML's v0.1 compilation target? Is there a forward-looking version you'd recommend pinning to?
3. **Custom-node registry declaration.** URML compilation produces custom BT nodes (one per URML primitive). Is the manifest's enumerated registry the right shape?
4. **Groot 2 boundary.** URML's manifest declares the BehaviorTree.CPP runtime, not Groot 2 (separate concern, different license). Should URML's documentation explicitly distinguish the open-source runtime from the commercial-tier editor?
5. **Adapter home.** URML-side compiler in `reference/bt-bridge/`, contributed example in `BehaviorTree.CPP/examples/`, or external bridge repo?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0161: py_trees

**Post to:** https://github.com/splintered-reality/py_trees/discussions/new (Ideas category)

**Title:**

```
Proposal: URML (substrate-neutral robot intent) Layer-3 → py_trees as the Python-side compilation target — plus license-clarification ask
```

**Body:**

```markdown
Hi @splintered-reality team,

Proposing a URML v0.1 capability-manifest mapping for py_trees over `splintered-reality/py_trees`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: typed primitive vocabulary + Layer-3 behavior composition + capability manifest + static validator.

py_trees is the Python-side counterpart to URML's C++ behavior-tree engagement. Where BehaviorTree.CPP targets C++ deployments and Nav2-style production stacks, py_trees targets ROS 2 Python nodes — a different deployment profile URML's Python-first reference runtimes reach for first. Mapping is direct: URML primitives become `py_trees.behaviour.Behaviour` subclasses, Layer-3 composition becomes a py_trees module.

One housekeeping ask: GitHub reports `licenseInfo: Other` on the repo. URML's adapter cannot ship until the OSI classification is confirmed.

**This is proposal-only**, part of URML's Move #12 outreach (16 RFCs covering speech / translation / robot-command-library substrates for URML's NL layer).

Full RFC with manifest mapping, three alternatives, and the two-language-coverage discussion: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0161-py-trees-outreach.md

Questions worth maintainer input on:

1. **License clarification.** What is the explicit OSI license URML should cite? (BSD-2-Clause? BSD-3-Clause? Some project-specific BSD variant?)
2. **Behavior-tree-runtime declaration shape.** Is `py_trees` the right slug for URML's manifest, or do you prefer a different convention?
3. **`Behaviour` subclass registry declaration.** URML compilation produces custom `Behaviour` subclasses (one per URML primitive). Is the enumerated registry the right manifest shape?
4. **ROS 2 integration tier.** Is `py_trees_ros \| standalone` the right granularity, or are there additional tiers (`py_trees_ros_interfaces`, custom-ROS-wrapper) worth enumerating?
5. **Adapter home.** URML-side compiler in `reference/bt-bridge/`, contributed example in `py_trees/examples/`, or external bridge repo?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0162: MoveIt Task Constructor

**Post to:** https://github.com/moveit/moveit_task_constructor/discussions/new (Ideas category)

**Title:**

```
Proposal: URML (substrate-neutral robot intent) industrial primitives → MoveIt Task Constructor stage decomposition
```

**Body:**

```markdown
Hi @moveit team,

Proposing a URML v0.1 capability-manifest mapping for MoveIt Task Constructor over `moveit/moveit_task_constructor`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: typed primitive vocabulary + capability manifest + static validator. URML's industrial profile ships `pick_from`, `place_at`, and `swap_tool` primitives; MTC is the natural runtime for executing them.

This is URML's first industrial-manipulation-substrate RFC. The mapping is concrete: `pick_from(object, source)` decomposes into `GeneratePose(grasp) → Connect(approach) → PickPlace::pick → Connect(retreat)`; `place_at` is the mirror; `swap_tool` is a `Connect` + `PickPlace::release` + tool-change-message + `Connect` + `PickPlace::pick` sequence. URML's manifest declares the MoveGroup, the active solver pipeline, the planning-scene source, and the URML-primitive → MTC-stage mapping table.

**This is proposal-only**, part of URML's Move #12 outreach (16 RFCs covering speech / translation / robot-command-library substrates for URML's NL layer).

Full RFC with manifest mapping, four alternatives, and the concrete primitive-to-stage decomposition table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0162-moveit-task-constructor-outreach.md

Questions worth maintainer input on:

1. **Manipulation-substrate declaration shape.** Is `moveit_task_constructor` the right slug for URML's manifest, or do you prefer a different convention?
2. **Primitive-to-stage mapping.** Is the proposed `pick_from → GeneratePose / Connect / PickPlace::pick / Connect` decomposition correct, or are there standard MTC patterns URML should follow instead?
3. **Planning-scene source enum.** Is `ros_topic \| static_yaml` the right granularity, or are there additional sources (database-backed, runtime-constructed) common in production?
4. **Solver-pipeline declaration.** Is a high-level selector (`Pipeline, RRTConnect, CHOMP, ...`) sufficient, or do you recommend a finer-grained manifest field?
5. **Adapter home.** URML's `reference/industrial-arm-runtime/`, contributed example in `moveit_task_constructor/examples/`, or external bridge repo?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0163: SkiROS2

**Post to:** https://github.com/RobotLabLTH/SkiROS2/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) Layer-2 / Layer-3 → SkiROS skill semantics with knowledge-graph substrate declaration — plus license-clarification ask
```

**Body:**

```markdown
Hi @RobotLabLTH team,

Proposing a URML v0.1 capability-manifest mapping for SkiROS2 over `RobotLabLTH/SkiROS2`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: typed primitive vocabulary + capability manifest + static validator.

SkiROS is structurally distinctive among URML's Move #12 robot-command-library engagements: where the behavior-tree engagements provide execution semantics, SkiROS adds a knowledge-graph substrate (world model) that grounds skill parameters against scene state. URML's primitive vocabulary maps cleanly onto SkiROS skill classes; the knowledge-graph substrate surfaces a novel URML manifest concern (skill-grounding-mode declaration) URML is queueing as a Spec RFC.

Two housekeeping notes: (1) GitHub reports `licenseInfo: Other` on the repo — URML's adapter cannot ship until OSI classification is confirmed. (2) URML's internal notes had this project at Aalborg / RVMI historically; engaging the active `RobotLabLTH/SkiROS2` (Lund University Robotics Lab / Department of Automatic Control) as the canonical upstream.

**This is proposal-only**, part of URML's Move #12 outreach (16 RFCs covering speech / translation / robot-command-library substrates for URML's NL layer).

Full RFC with manifest mapping, four alternatives, and the knowledge-graph-substrate design discussion: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0163-skiros2-outreach.md

Questions worth maintainer input on:

1. **License clarification.** What is the explicit OSI license URML should cite? Historical SkiROS shipped BSD-3-Clause; is that current?
2. **Repo-location confirmation.** Is `RobotLabLTH/SkiROS2` the canonical upstream for URML to engage going forward (vs. historical Aalborg / RVMI lineage)?
3. **Knowledge-graph substrate declaration.** URML proposes adding a `knowledge_graph_substrate` manifest field. Is this a useful abstraction for SkiROS-class deployments, or should the knowledge graph stay SkiROS-internal?
4. **Skill-grounding-mode declaration.** Is `world_model \| runtime_query \| hybrid` the right enumeration, or do you see other modes worth declaring?
5. **World-model seed path.** Is a static YAML seed the canonical convention, or do deployments commonly use other seed sources?
6. **Adapter home.** URML's `reference/skill-bridge/`, contributed example in `SkiROS2/examples/`, or external bridge repo?
7. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0164: LangChain LangGraph

**Post to:** https://github.com/langchain-ai/langgraph/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) manifest declaration for LangGraph as an agent-orchestration substrate
```

**Body:**

```markdown
Hi @langchain-ai team,

Proposing a URML v0.1 capability-manifest mapping for LangGraph over `langchain-ai/langgraph`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: typed primitive vocabulary + capability manifest + static validator.

LangGraph is one of two distinct agent-execution patterns URML's manifest needs to declare: **state-graph-agent** (LangGraph) vs. **code-generation-agent** (parallel URML engagement covers the latter). URML programs spawn LangGraph sub-graphs for delegated multi-step planning under uncertainty (target moved, environment changed, tool failed). URML's framing here is light-touch — URML is one node type registerable in a `StateGraph`, alongside many others.

**This is proposal-only**, part of URML's Move #12 outreach (16 RFCs covering speech / translation / robot-command-library substrates for URML's NL layer).

Full RFC with manifest mapping, five alternatives, and the execution-model enumeration discussion: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0164-langgraph-outreach.md

Questions worth maintainer input on:

1. **Orchestration-framework declaration shape.** Is `langgraph` the right slug for URML's manifest, or do you prefer a specific naming convention?
2. **Typed-state-class declaration.** Is the import-path field the right shape for declaring URML's `State` reference, or is a different mechanism preferable?
3. **Execution-model enumeration.** Is `state_graph \| code_generation \| function_calling` the right tri-state, or do you see this differently?
4. **Checkpoint-backend declaration.** Is `memory \| sqlite \| postgres \| custom` the right granularity?
5. **Node-vs-graph hosting.** URML can register as either a single LangGraph node or a sub-graph. Which framing matches LangChain's preferred extension pattern?
6. **Adapter home.** URML's `reference/orchestration-bridge/`, contributed example in `langgraph/examples/`, or external bridge repo?
7. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## Tier B — 4 friction-note targets

### RFC-0165: Picovoice Porcupine

**Post to:** https://github.com/Picovoice/porcupine/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) manifest declaration for Porcupine as the wake-word front-end to robot speech-input loops
```

**Body:**

```markdown
Hi @Picovoice team,

Proposing a URML v0.1 capability-manifest mapping for Porcupine over `Picovoice/porcupine`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: typed primitive vocabulary + capability manifest + static validator.

Porcupine closes a real gap in URML's speech-input story: full STT engines are too power-hungry to keep continuously active on resource-constrained robots, so an always-on wake-word detector is the missing piece. URML's manifest declares Porcupine as the wake-word substrate, the active keyword set, the license tier (personal / commercial — operator's decision, not URML's), and the STT engine the wake handoff activates.

**This is proposal-only**, part of URML's Move #12 outreach (16 RFCs covering speech / translation / robot-command-library substrates for URML's NL layer). Framing as open-source-tier composition; commercial-tier deployment inherits Picovoice's commercial-license obligations directly.

Full RFC with manifest mapping, three alternatives, and the license-tier expression discussion: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0165-porcupine-outreach.md

Questions worth maintainer input on:

1. **Wake-word substrate declaration shape.** Is `porcupine` the right slug for URML's manifest, or do you prefer a different convention?
2. **License-tier declaration.** Is `personal \| commercial` the right enumeration, or are there additional tiers (research, education, enterprise) URML should enumerate?
3. **Wake-word-to-STT handoff declaration.** Is the handoff field useful as a downstream signal, or unnecessary?
4. **Custom-keyword authoring.** Does Picovoice have a preferred convention for declaring custom keywords in a downstream manifest (file path? URI? Console handle)?
5. **Engagement cadence.** Is `Picovoice/porcupine` actively monitored for non-customer design-discussion Issues, or is a different surface preferred?
6. **Adapter home.** URML's `reference/speech-bridge/`, contributed example in `porcupine/examples/`, or external bridge repo?
7. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0166: OHF-Voice piper1-gpl

**Post to:** https://github.com/OHF-Voice/piper1-gpl/discussions/new (Ideas category)

**Title:**

```
Proposal: URML (substrate-neutral robot intent) manifest declaration for Piper as the IPC-bounded `speak` substrate
```

**Body:**

```markdown
Hi @OHF-Voice team,

Proposing a URML v0.1 capability-manifest mapping for Piper over `OHF-Voice/piper1-gpl`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: typed primitive vocabulary + capability manifest + static validator.

Piper is the surviving open neural-TTS substrate after the Coqui shutdown and is the active successor to the archived `rhasspy/piper`. URML's integration shape with Piper is explicitly **IPC-only**: URML's reference adapter is a subprocess caller of the `piper` CLI, never an importer of the Python module. This preserves URML's Apache-2.0 license posture across the GPL-3.0 boundary.

**This is proposal-only**, part of URML's Move #12 outreach (16 RFCs covering speech / translation / robot-command-library substrates for URML's NL layer).

Full RFC with manifest mapping, five alternatives, and the IPC-boundary discussion: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0166-piper1-gpl-outreach.md

Questions worth maintainer input on:

1. **IPC-boundary framing.** Is "URML is a subprocess caller of the `piper` CLI, never embedding the Python module" the framing OHF-Voice would endorse, or is there language the project prefers for downstream integrations?
2. **TTS-engine declaration shape.** Is `piper` (with `tts_runtime: piper1_gpl` distinguishing the active repo) the right slug for URML's manifest, or do you have a preferred convention?
3. **License-boundary declaration.** Is `tts_license_boundary: gpl_subprocess` the right way to declare the GPL constraint? Useful as a downstream signal, or unnecessary friction?
4. **Voice-model declaration.** Is the voice-model slug (e.g., `en_US-lessac-medium`) the canonical identifier for downstream-manifest declarations?
5. **Subprocess invocation mode.** Is the `piper` CLI the canonical invocation surface, or are there preferred alternatives (Wyoming protocol via wyoming-piper, HTTP server, gRPC) for production?
6. **Adapter home.** URML-side subprocess wrapper in `reference/speech-bridge/`, contributed example in `piper1-gpl/examples/`, or external bridge repo?
7. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0167: Meta fairseq / NLLB-200

**Post to:** https://github.com/facebookresearch/fairseq/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) manifest declaration for NLLB-200 — and successor-surface question now that fairseq is archived
```

**Body:**

```markdown
Hi @facebookresearch team,

Proposing a URML v0.1 capability-manifest mapping for NLLB-200 over `facebookresearch/fairseq` (where the NLLB-200 model card lives). [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: typed primitive vocabulary + capability manifest + static validator.

NLLB-200's 200-language coverage is unmatched in open translation today; URML wants to declare it as an alternate substrate (the v0.1 default is OPUS-MT for license cleanness). Two friction points URML's RFC documents explicitly: the upstream repo is archived (PRs do not merge), and the NLLB-200 model weights are CC-BY-NC 4.0 — URML's reference adapter would carry the non-commercial flag, never bundle the weights.

URML's primary ask here is the **successor-surface question**: with `facebookresearch/fairseq` archived 2025-09-30, where should downstream projects engage on NLLB-200 going forward? `seamless_communication`? `large_concept_model`? HuggingFace community? Direct contact?

**This is proposal-only**, part of URML's Move #12 outreach (16 RFCs covering speech / translation / robot-command-library substrates for URML's NL layer).

Full RFC with manifest mapping, four alternatives, and the model-license declaration design: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0167-fairseq-outreach.md

Questions worth maintainer input on:

1. **Successor surface.** Where should downstream projects engage on NLLB-200 now that `facebookresearch/fairseq` is archived?
2. **Model-license-declaration shape.** URML's manifest will declare `translation_model_license: cc_by_nc_4_0`. Is this the right level of granularity, or does Meta have a finer-grained license-classification convention?
3. **Commercial-use boundary.** Is there a path for commercial use of NLLB-200 weights (e.g., enterprise license), or is non-commercial the canonical and only path?
4. **Engagement channel.** Given fairseq is archived, where would Meta prefer URML's outreach Issue to land?
5. **Conformance listing.** Even with archived-upstream, would Meta consider a README link in the successor-surface repo to URML's compatible-runtimes registry once a working adapter ships?
6. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

### RFC-0168: LibreTranslate

**Post to:** https://github.com/LibreTranslate/LibreTranslate/issues/new

**Title:**

```
Proposal: URML (substrate-neutral robot intent) manifest declaration for LibreTranslate as a REST-boundary translation substrate
```

**Body:**

```markdown
Hi @LibreTranslate team,

Proposing a URML v0.1 capability-manifest mapping for LibreTranslate over `LibreTranslate/LibreTranslate`. [URML](https://urml.dev) (Apache-2.0) is a substrate-neutral spec for robot intent: typed primitive vocabulary + capability manifest + static validator.

LibreTranslate is interesting to URML because of the deployment shape: operators self-host a translation server inside their own network, URML acts as a REST client. The integration is **strictly REST-boundary-only** — URML's reference adapter never embeds or links LibreTranslate's source. This preserves URML's Apache-2.0 license posture across the AGPL-3.0 boundary and matches URML's no-cloud invariant (the server is on-prem, not public cloud).

**This is proposal-only**, part of URML's Move #12 outreach (16 RFCs covering speech / translation / robot-command-library substrates for URML's NL layer).

Full RFC with manifest mapping, four alternatives, and the AGPL-network-boundary design: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0168-libretranslate-outreach.md

Questions worth maintainer input on:

1. **REST-boundary framing.** Is "URML is an HTTP client of a self-hosted LibreTranslate server, never embedding the source" the framing LibreTranslate would endorse, or is there language the project prefers for downstream integrations?
2. **API key declaration.** Is `translation_endpoint_api_key` with a secret-store reference the right shape, or do you have a preferred convention?
3. **License-boundary declaration.** Is `translation_endpoint_license_constraint: agpl_network_boundary` the right way to declare "this substrate is AGPL but I'm calling it across a network boundary"? Useful as a downstream signal, or unnecessary friction?
4. **Pair availability discovery.** LibreTranslate's `/languages` endpoint enumerates supported pairs at runtime. Should URML's manifest declare the static list, or discover-on-startup?
5. **Self-host vs. public.libretranslate.com.** Is the public hosted instance a supported runtime for URML to declare, or strictly an example?
6. **Adapter home.** URML-side REST-client adapter in `reference/translation-bridge/`, contributed example in `LibreTranslate/examples/`, or external bridge repo?
7. **Anything else.**

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## Posting checklist

Order of posts (operator can batch by channel type for efficiency):

**Discussions (Ideas-category-preferred) — 8 posts:**
1. RFC-0153 (openai/whisper — Show-and-tell)
2. RFC-0154 (SYSTRAN/faster-whisper)
3. RFC-0155 (ggml-org/whisper.cpp)
4. RFC-0156 (myshell-ai/OpenVoice)
5. RFC-0158 (argosopentech/argos-translate)
6. RFC-0159 (marian-nmt/marian-dev)
7. RFC-0160 (BehaviorTree/BehaviorTree.CPP)
8. RFC-0161 (splintered-reality/py_trees)
9. RFC-0162 (moveit/moveit_task_constructor)
10. RFC-0166 (OHF-Voice/piper1-gpl)

**Issues — 6 posts:**
11. RFC-0157 (Helsinki-NLP/OPUS-MT-train)
12. RFC-0163 (RobotLabLTH/SkiROS2)
13. RFC-0164 (langchain-ai/langgraph)
14. RFC-0165 (Picovoice/porcupine)
15. RFC-0167 (facebookresearch/fairseq)
16. RFC-0168 (LibreTranslate/LibreTranslate)

After posting each: update the corresponding ledger row in [`outreach-move12.yaml`](outreach-move12.yaml) with the posted URL, set `sent_at` to the post date, set `channel` from `deferred` to `issue` or `discussion`, set `last_touch` to match `sent_at`. Per [`AGENTS.md`](../../AGENTS.md), do not modify `response` until the maintainer actually responds.

---

## RFC-0167 addendum (2026-05-30): retargeted to the successor surface, posted

RFC-0167 was deferred at posting time 2026-05-28 because `facebookresearch/fairseq` is archived (read-only since 2025-09-30) and `gh issue create` is refused there. The RFC's own engagement question was "what is the successor surface for NLLB engagement now?" — and `facebookresearch/seamless_communication` (named in the RFC as the candidate successor) is live, with Issues and Discussions enabled. Posted to [seamless_communication#578](https://github.com/facebookresearch/seamless_communication/issues/578), framed as the successor-surface question. The non-commercial-weights caveat (NLLB / Seamless model weights are CC-BY-NC 4.0) is stated plainly; the ask is framed around the multilingual NL layer, not the weights.

**Posted to:** https://github.com/facebookresearch/seamless_communication/issues/578

**Title:** URML (robot intent language) — NLLB successor-surface question + a manifest-level model-license note

**Body:**

Hi Seamless / NLLB team,

URML (urml.dev) is a small, opinionated, human-readable language for describing robot intent — Apache-2.0. Its natural-language layer is multilingual by design, and NLLB-200's 200-language breadth is unmatched in open translation, so URML wants to document NLLB as a declarable translation substrate in its capability manifest. Two honest frictions prompted this RFC, and the second is really a question for you.

This is **proposal-only** — no spec change, nothing to merge. Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0167-fairseq-outreach.md

First friction: the original NLLB home, `facebookresearch/fairseq`, is archived, so an Issue cannot be opened there. This repo is the closest active Meta surface I could find for multilingual-communication work, which is why the question lands here. Second friction, and the load-bearing one: the NLLB / Seamless model **weights are CC-BY-NC 4.0** (non-commercial), while the code is permissive. URML's manifest would declare that constraint explicitly (a `translation_model_license: cc_by_nc_4_0` field, validator-enforced so a commercial deployment that pairs with NLLB weights fails at static-check time). I am not asking you to relicense anything — I am asking whether URML is modelling the boundary the way you would want it modelled.

Questions for the maintainers (full list in the RFC):

1. **Successor surface.** With `fairseq` archived, where should a downstream project engage on NLLB-200 going forward — here, the HuggingFace model community, or somewhere else?
2. **Model-license declaration.** URML would record `translation_model_license: cc_by_nc_4_0` at the manifest level. Is that the right granularity, or do you have a finer-grained convention?
3. **Commercial-use boundary.** Is non-commercial the canonical and only path for the weights, or is there an enterprise-license route a manifest should be able to point at?
4. **Engagement channel.** Is a public Issue the right shape here, or would you prefer this elsewhere?
5. **Anything else.**

Happy to scope down or shelve. Thanks for keeping 200 languages in scope when most of the field keeps 10.

Ido Yahalomi (URML maintainer, urml.dev, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
