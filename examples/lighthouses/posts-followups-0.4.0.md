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

# v0.4.0 follow-up posts

Drafts for the surfaces that earned a "this shipped" note. Rewritten
2026-08-10 to claim only what is true today: 0.4.0 is cut and merged on
`main`, and the PyPI publish has not run yet, so no draft says "on PyPI"
or gives a `pip install` line. When the family goes live on the index
(`pip index versions urml-validator` shows 0.4.0), swap the from-source
lines for the pip lines before posting anything not yet posted. Founder
reviews every draft; the Discussion #497 note is founder-voiced and
founder-posted.

Ledger discipline on posting: edit `outreach-move12.yaml` first (bump
`last_touch`, quoted-string dates in `comments[]`), run the full
`conformance/tests/test_outreach_ledger_schema_v2.py`, then refresh the
DB mirror (`python tools/scripts/refresh_outreach_db.py`, dashboard
stopped).

---

## 1. Discussion #497 (slowrunner) — founder-voiced, founder-posted

Thread: https://github.com/URML-MARS/URML/discussions/497 (closed, not
locked; a new comment works). Keep it short and personal; he prefers human
replies. No footer.

> Quick update you earned: native Ollama support just landed on `main`, and this thread drove part of it.
>
> ```bash
> git pull && python bootstrap.py
> urml translate "Bring me the red mug." --manifest manifest.yaml --provider ollama --model "qwen3.5:9b"
> ```
>
> No more `OPENAI_BASE_URL`, no more model tag standing in for `OPENAI_API_KEY`. Your old recipe keeps working, but the flags now say what they mean. Your `OLLAMA_CONTEXT_LENGTH` guidance still applies word for word; that part of the HOWTO is not superseded. It is all in the 0.4.0 release cut, which reaches PyPI next; until then the source checkout above is the way to run it.
>
> One more thing that fits your all-local setup: `urml translate --audio request.wav` now transcribes with a local whisper-server before translating. One spoken sentence to motion, fully offline.
>
> Thanks again for this thread. It is exactly the kind of field report that turns into flags.

## 2. whisper.cpp Discussion #3836 (RFC-0155) — follow-up with a shipped artifact

Thread: https://github.com/ggml-org/whisper.cpp/discussions/3836 (open,
0 comments since 2026-05-28). The new fact: URML now ships a
whisper-server adapter. Describe what shipped, not the RFC's old
subprocess/pybind sketch.

> Follow-up with a shipped artifact rather than a proposal.
>
> Since posting this, URML shipped a whisper.cpp adapter (RFC-0670, merged on `main` in the 0.4.0 cut): `urml translate --audio request.wav` sends the audio to a running `whisper-server` `/inference` endpoint (multipart, `response_format: json`, optional `language` hint) and feeds the transcript into a validate-before-actuate pipeline, so the resulting robot program is statically checked against a capability manifest before anything moves. whisper-server is the default speech backend. Adapter source: https://github.com/URML-MARS/URML/blob/main/reference/llm-bridge/src/urml_llm_bridge/speech/whisper_cpp.py
>
> It differs from the sketch in my original post: instead of a subprocess wrapper around the binary, the adapter speaks HTTP to whisper-server, which keeps the model resident between requests and needs no Python on the inference host.
>
> One question: is there anything about the `/inference` request or response contract we should not rely on (fields likely to change, or a different endpoint you would consider the stable one)?
>
> AI-assisted prose, maintainer-reviewed before posting (see VIBE.md). Human-only correspondence available on request.
>
> Ido Yahalomi (URML maintainer, urml.dev, greenvh@gmail.com)

## 3. Optional twins — post only if the founder wants the loop closed

**openai/whisper Discussion #2783** (0 comments since 2026-05-28):

> Closing the loop on this proposal: URML shipped speech input (RFC-0670, on `main` in the 0.4.0 cut). Whisper models serve it two ways today: whisper.cpp's `whisper-server` as the default on-device backend, and any OpenAI-compatible transcription endpoint via `--speech-provider openai --speech-base-url`. No ask here; the original manifest-mapping questions above still stand if they ever become interesting.
>
> AI-assisted prose, maintainer-reviewed before posting (see VIBE.md). Human-only correspondence available on request.

**SYSTRAN/faster-whisper Discussion #1446** (0 comments since 2026-05-28):

> Closing the loop on this proposal: URML shipped speech input (RFC-0670, on `main` in the 0.4.0 cut). A faster-whisper deployment exposing an OpenAI-compatible transcription endpoint is reachable today with `--speech-provider openai --speech-base-url http://host:port/v1`, no API key required for a local server. No ask here; the realtime-latency manifest questions above still stand if they ever become interesting.
>
> AI-assisted prose, maintainer-reviewed before posting (see VIBE.md). Human-only correspondence available on request.

## 4. Seamless #578 — no post (recommendation)

Our 2026-06-12 comment already told the maintainer the permissive path
"is turning into the next piece", and RFC-0304 shipped the day after. A
third consecutive no-ask message from us, to a maintainer who asked for
human-only correspondence, spends goodwill without adding information.
If the founder wants one anyway: founder-written, human-only, no footer,
one sentence ("the permissive-alternative mechanism you steered us
toward shipped as RFC-0304 and is in the 0.4.0 cut").
