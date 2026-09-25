<p align="center">
  <a href="https://urml.dev"><img src="https://urml.dev/favicon.svg" alt="URML" width="72" height="72"></a>
</p>

# URML model benchmark (`urml bench`)

This directory is a **benchmark, not a conformance test**. Conformance
(`conformance/`) decides whether a runtime is URML-compatible; this benchmark
measures how well a given language model translates natural-language requests
into URML that survives the validator. A model can score poorly here and the
runtime it feeds can still be fully conformant.

## What one run measures

`urml bench` sends every utterance in a corpus through the same bridge loop
`urml translate` uses (same prompt contract, same JSON repair, same revision
budget) against one capability manifest, and classifies where each request
lands:

| Outcome | Meaning |
|---|---|
| `accepted` | The validator accepted a program that does real work. |
| `honest_refusal` | The validator accepted a program whose root behavior is only `report(status: failure)`: the model declined the request. |
| `invalid_emission` | The revision budget ran out without an accepted program. |
| `provider_error` | The provider raised, or emitted something that is not JSON even after conservative repair. |
| `policy_block` | Only `policy.*` errors remained; revision cannot fix hardware provenance (RFC-0004). |

Each corpus row also declares `expected: accept | refuse` — what a good model
should do with that request on that manifest. The run reports a separate
`expected_match` rate so an honest refusal of a doable request is visible as a
miss, never binned with invalid output.

Two honesty rules worth knowing before quoting numbers:

- **Refusal means report-only at the root.** A program that moves the robot
  and then reports failure did real work and counts as `accepted`. (The
  RFC-0021 conformance scorer matches a failure report anywhere in the tree;
  the two numbers are not comparable.)
- **The benchmark measures admissibility, not physics.** An `accepted`
  program is one the validator admits against the declared manifest and
  envelope. Whether it would accomplish the user's goal on a real robot is
  out of scope.

`revision_attempts_mean` averages the revision count over rows where the
bridge returned a program (accepted or refusal); failed rows have no
comparable number and are excluded.

## Running it

```bash
pip install urml-validator "urml-llm-bridge[ollama]"

urml bench \
  --corpus bench/corpora/home-en.yaml \
  --manifest reference/validator/tests/fixtures/manifests/turtlebot4_home.yaml \
  --provider ollama --model qwen3.5:9b \
  --no-policy
```

The run prints a per-utterance report plus a markdown table row, and writes a
machine-readable YAML row to `bench/results/<date>/<row_id>.yaml`. One
invocation measures one (provider, model) pair; compare models by running once
per model and aggregating:

```bash
urml bench --render bench/results/2026-09-25/
```

A hermetic run with no model at all (useful for CI and for validating a new
corpus) uses the echo provider with a canned script:

```bash
urml bench --corpus bench/corpora/home-en.yaml -m <manifest> \
  --provider echo --echo-script my-script.yaml --no-policy
```

where the script is a YAML map of utterance-substring to canned JSON response.

## Corpus format

```yaml
corpus_id: home-en        # defaults to the file stem
profile: home             # profile passed to the validator (overridable with -p)
language: en
manifest: turtlebot4_home # advisory; --manifest decides what is actually used
utterances:
  - id: red_mug           # stable key; never re-key rows
    text: "Bring me the red mug from the kitchen."
    expected: accept      # accept | refuse
```

The legacy conformance spelling `expected_kind: positive | report_failure`
(RFC-0021 fixtures under `conformance/llm-bridge/fixtures/`) is accepted as an
alias, so those sets run unchanged.

## Publishing results

Commit row YAMLs under `bench/results/<date>/` with the model, backend, and
hardware noted (`--notes`, `--tag`). Numbers published anywhere (README, blog,
posts) must come from committed rows, per the project's claims-audit
discipline: report what was measured, on which corpus, on which date.
