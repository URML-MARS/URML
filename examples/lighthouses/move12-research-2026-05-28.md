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

# Move-12 research — speech / translation / robot-command-library targets

**Research date**: 2026-05-28.
**Audience**: founder review before Move-12 RFCs draft.
**Method**: two general-purpose agents in parallel, one for STT/TTS, one for translation + robot-command-libraries. Each candidate verified via `gh repo view --json name,owner,licenseInfo,stargazerCount,pushedAt,isArchived,hasIssuesEnabled,hasDiscussionsEnabled,description,url`. Origin/domicile checked per URML's US-federal default policy (NDAA Section 889 excludes PRC-domiciled; URML treats Russia-domiciled as parallel exclude under EO 14071 / OFAC posture even though no published rule yet).
**Outcome**: 16 verified candidates (12 Tier A + 4 Tier B); 6 excluded with cause.

## Why this wave

URML's Layer-4 NL grammar declares multilingual structural slots (English content, Hebrew/Spanish/Japanese/Mandarin reserved) and Layer-2 primitives `listen` and `speak` with `input: speech | text`. None of the eleven prior outreach waves engaged the projects that produce the *inputs and substrates* for that layer:

- **STT / TTS engines** — what the `listen` and `speak` primitives delegate to.
- **Translation / multilingual NL** — what the Layer-4 multilingual reservation will compose with.
- **Robot command libraries / behavior-tree DSLs** — what URML's Layer-3 behavior composition would compile down to alongside the existing reference runtimes.

Move #12 fills that gap. Distinct from Move #11 (VLAs / robot foundation-models, RFCs 0138-0152, also currently un-posted): Move #11 is *upstream* of language infrastructure (a VLA emits actions), Move #12 is the language-infrastructure layer itself.

## Tier A (12) — vendor-direct / research-lab-direct, adapter-eligible

| Slug | Repo | License | Stars | Last push | Origin | Notes |
|---|---|---|---|---|---|---|
| `whisper` | [openai/whisper](https://github.com/openai/whisper) | MIT | 100.8k | 2026-04-15 | US | OpenAI reference STT; **Issues disabled — engage via Discussions only**. Pairs with Layer-2 `listen` (`input: speech`). |
| `faster-whisper` | [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper) | MIT | 23.2k | 2025-11-19 | FR (SYSTRAN) | CTranslate2-accelerated Whisper inference. Migrated from `guillaumekln/`. Issues + Discussions enabled. |
| `whisper-cpp` | [ggml-org/whisper.cpp](https://github.com/ggml-org/whisper.cpp) | MIT | 50.2k | 2026-05-28 | BG/individual (ggml-org) | Embedded C++ Whisper inference. **Migrated from `ggerganov/` to `ggml-org/`** — note the org rename. Ubiquitous on edge. |
| `openvoice` | [myshell-ai/OpenVoice](https://github.com/myshell-ai/OpenVoice) | MIT | 36.6k | 2025-04-19 | US (MyShell SF + MIT-the-institute co-author) | Zero-shot voice cloning. MyShell US-domiciled (Crunchbase, CB Insights, PitchBook concur); founders CN-heritage but corporate domicile passes US-federal default. |
| `opus-mt-train` | [Helsinki-NLP/OPUS-MT-train](https://github.com/Helsinki-NLP/OPUS-MT-train) | MIT | 403 | 2026-01-17 | FI (Univ. Helsinki) | Helsinki-NLP 300+ language-pair translation models. Directly addresses URML's Hebrew/Spanish/Japanese/Mandarin Layer-4 reservation. |
| `argos-translate` | [argosopentech/argos-translate](https://github.com/argosopentech/argos-translate) | MIT | 6.1k | 2026-04-25 | US (Ithaca, NY) | Offline on-device translation library. Federated-fleet friendly (no API dependency). |
| `marian-dev` | [marian-nmt/marian-dev](https://github.com/marian-nmt/marian-dev) | Other (MIT-style — verify LICENSE) | 287 | 2025-07-09 | UK/US (Edinburgh + MSR) | Marian NMT toolkit; the research backbone behind OPUS-MT. |
| `behaviortree-cpp` | [BehaviorTree/BehaviorTree.CPP](https://github.com/BehaviorTree/BehaviorTree.CPP) | MIT | 4.0k | 2026-05-22 | IT (Faconti) | URML Layer-3 candidate compilation target. ROS-relevant; the canonical C++ behavior-tree engine in robotics. |
| `py-trees` | [splintered-reality/py_trees](https://github.com/splintered-reality/py_trees) | Other (BSD-style — verify LICENSE) | 604 | 2026-05-22 | NZ/AU (Stonier; Yujin Robot lineage) | Python-side sibling to BehaviorTree.CPP; de-facto BT for ROS 2 Python nodes. |
| `moveit-task-constructor` | [moveit/moveit_task_constructor](https://github.com/moveit/moveit_task_constructor) | BSD-3 | 271 | 2026-04-23 | DE/US (MoveIt community) | URML pick / place / swap_tool primitives map naturally to MoveIt Task Constructor subtasks. |
| `skiros2` | [RobotLabLTH/SkiROS2](https://github.com/RobotLabLTH/SkiROS2) | Other (verify LICENSE) | 224 | 2025-06-09 | SE (Lund Univ., not Aalborg) | Knowledge + skills framework for ROS 2. **Note**: active repo is at Lund Univ. Robotics Lab (`RobotLabLTH/`), not the older Aalborg/RVMI fork — prior URML scratch notes had this wrong. |
| `langgraph` | [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | MIT | 33.2k | 2026-05-28 | US (LangChain Inc) | Agent-orchestration DSL; URML programs spawning delegated sub-agents. |

## Tier B (4) — friction notes; engageable with explicit caveat

| Slug | Repo | License | Stars | Last push | Origin | Friction |
|---|---|---|---|---|---|---|
| `porcupine` | [Picovoice/porcupine](https://github.com/Picovoice/porcupine) | Apache-2.0 SDK | 4.8k | 2026-05-28 | CA (Vancouver) | Commercial-SDK model (free tier + paid). Engagement may be tepid; the company sells the gated tiers. URML still engages — wake-word front-end pairs cleanly with Layer-1 RTOS substrates. |
| `piper1-gpl` | [OHF-Voice/piper1-gpl](https://github.com/OHF-Voice/piper1-gpl) | **GPL-3.0** | 4.2k | 2026-04-07 | US (Open Home Foundation, Piper successor) | Successor to archived `rhasspy/piper`. **GPL-3.0 = strong copyleft**; URML cannot statically link from Apache-2.0 reference runtimes. Engagement frames URML as a *neighboring* project that calls Piper via subprocess / IPC. Issues + Discussions enabled. |
| `fairseq` | [facebookresearch/fairseq](https://github.com/facebookresearch/fairseq) | MIT | 32.2k | 2025-09-30 | US (Meta) | **Archived 2025-09-30.** Code MIT-clean but no PRs merge. NLLB-200 model weights live here and are **CC-BY-NC 4.0** (non-commercial only). URML engages issues-only and flags the non-commercial weight licence in the RFC. |
| `libretranslate` | [LibreTranslate/LibreTranslate](https://github.com/LibreTranslate/LibreTranslate) | **AGPL-3.0** | 14.4k | 2026-05-26 | community (US-led) | AGPL-3.0 = network-copyleft. URML integration must stay at the REST-API boundary so AGPL does not contaminate URML core. Engagement frames URML-as-client-of-LibreTranslate-server, never URML-embeds-LibreTranslate. |

## Tier C — excluded with cause (recorded so the negative space is auditable)

| Slug | Repo | Cause |
|---|---|---|
| `vosk` | [alphacep/vosk-api](https://github.com/alphacep/vosk-api) | **Russia-domiciled** — Alphacephei is led by Nickolay V. Shmyrev (Astrakhan, Russia per GitHub profile + alphacephei.com + Tracxn). URML has no published Russia rule but the US-federal default (BIS Entity List risk, OFAC, EO 14071) and the NDAA-889-spirit caution that excludes PRC argue for a parallel exclude. **Founder-decision flag**: if Russia-domicile is acceptable, promote to Tier B. |
| `sherpa-onnx` | [k2-fsa/sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) | **PRC-domiciled (Xiaomi)** — k2-fsa / next-gen Kaldi is led by Daniel Povey (ex-Hopkins, chief voice scientist at Xiaomi AI Lab Beijing since 2019). Xiaomi has appeared on US restricted lists (DoD CCMC 2021, later settled) and remains PRC-domiciled. NDAA 889 default. |
| `f5-tts` | [SWivid/F5-TTS](https://github.com/SWivid/F5-TTS) | **PRC-domiciled** — README badges X-LANCE @ SJTU (Shanghai Jiao Tong University) + SII (Shanghai) + PCL (Pengcheng Lab Shenzhen). Authors at SJTU. NDAA 889. **Also**: pretrained weights are CC-BY-NC, independently disqualifying for URML's commercial-friendly posture. |
| `coqui-stt` | [coqui-ai/STT](https://github.com/coqui-ai/STT) | Coqui (Berlin) wound down; last push 2024-03-11. Dead upstream; engagement has nowhere to land. Active community forks exist but no single canonical successor — defer until one consolidates. |
| `coqui-tts` | [coqui-ai/TTS](https://github.com/coqui-ai/TTS) | Same Coqui shutdown; last push 2024-08-16. Same reasoning. |
| `festival` | [festvox/festival](https://github.com/festvox/festival) | Last push 2023-08-04; non-OSI custom license; legacy. Useful as a deterministic baseline reference *concept* but no live maintainer surface to engage. |

## Distribution across categories

| Move-12 category | Tier A | Tier B | Excluded |
|---|---|---|---|
| Speech-to-text / wake-word | 3 (whisper, faster-whisper, whisper.cpp) | 1 (porcupine) | 3 (vosk RU, sherpa-onnx PRC, coqui-stt dead) |
| Text-to-speech | 1 (openvoice) | 1 (piper1-gpl) | 3 (coqui-tts dead, festival dead, f5-tts PRC + CC-BY-NC) |
| Translation / multilingual NL | 3 (opus-mt-train, argos-translate, marian-dev) | 2 (fairseq archived + NLLB CC-BY-NC, libretranslate AGPL) | 0 |
| Robot command libraries / BT DSLs | 5 (behaviortree-cpp, py-trees, moveit-task-constructor, skiros2, langgraph) | 0 | 0 |
| **Total** | **12** | **4** | **6** |

## Reserved RFC range

RFCs **0153-0168** (16 numbers) reserved for Move #12 in `docs/rfcs/README.md` (Move #11 ends at RFC-0152 NUS-Octopi; Move #12 picks up at 0153).

## Open license-clarification asks (carry into per-RFC unresolved questions)

- `marian-nmt/marian-dev`: license listed as "Other" — request explicit OSI declaration.
- `splintered-reality/py_trees`: license listed as "Other" — verify LICENSE file is BSD-3 before quoting.
- `RobotLabLTH/SkiROS2`: license listed as "Other" — request explicit OSI declaration; ledger says BSD-3-historical but unverified at API level.
- `OHF-Voice/piper1-gpl`: GPL-3.0 confirmed; the ask is how the upstream feels about a non-GPL caller invoking via subprocess.
- `facebookresearch/fairseq`: code MIT confirmed; engagement-ask is what the *successor* surface for NLLB engagement is now the repo is archived.

## Founder-decision flags

- **Russia-domicile rule**: URML has not formally ruled. Vosk is the most technically attractive engageable Russia-domiciled candidate; default-exclude posture is conservative. If founder wants a published Russia rule, this is the surface to ask.
- **GPL-3.0 friction**: piper1-gpl is the only TTS Tier B that survives Coqui's shutdown. URML's Apache stance means engagement-via-IPC is the only clean shape. Confirm the framing before drafting RFC.

## Next steps

1. Founder review of this research file.
2. Setup PR ships: `outreach-move12.yaml` + README index update + this file.
3. Subsequent sessions: draft RFCs 0153-0168 one per session (Move-11 batch shape: ~5 RFCs per PR; 16 candidates = ~3-4 PRs).
4. Posting follows Move-10 / Move-11 pattern: founder review of bodies, then assistant posts via `gh` with explicit "go" authorization. Posting deferred until then.
