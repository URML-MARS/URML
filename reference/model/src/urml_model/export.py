"""Export a dataset in the formats fine-tuning frameworks consume (RFC-0666).

Two families:

- `export_sft()` — supervised fine-tuning examples from the accepted
  records. The `chatml` format rebuilds the bridge's real system prompt for
  each record's manifest so the model trains on exactly the prompt shape
  the bridge hands it at inference time. The `completions` format is the
  bare (utterance, program) pair for frameworks that template their own
  prompts.
- `export_dpo()` — (prompt, chosen, rejected) preference triples from the
  rejection_repair records.

Assistant targets are compact JSON: that is what the bridge parses back.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from urml_llm_bridge.few_shot import few_shots_for
from urml_llm_bridge.prompt import build_system_prompt
from urml_validator import export_schema

from urml_model.dataset import Dataset
from urml_model.mining import resolve_envelope_ref, resolve_manifest_ref

SftFormat = Literal["chatml", "completions"]


def _compact(program: dict[str, Any]) -> str:
    return json.dumps(program, sort_keys=True, separators=(",", ":"))


def _system_prompt_for(manifest_ref: str, envelope_ref: str | None, profile: str) -> str:
    manifest = resolve_manifest_ref(manifest_ref)
    envelope = resolve_envelope_ref(envelope_ref)
    return build_system_prompt(
        schema=export_schema("program"),
        manifest=manifest,
        envelope=envelope,
        profiles=(profile,),
        few_shots=few_shots_for((profile,)),
    )


def export_sft(dataset: Dataset, path: Path, *, fmt: SftFormat = "chatml") -> int:
    """Write accepted records as SFT examples; returns the example count.

    System prompts are cached per (manifest_ref, envelope_ref, profile) so
    exporting a large dataset does not rebuild identical prompts per line.
    """
    prompt_cache: dict[tuple[str, str | None, str], str] = {}
    count = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for record in dataset.accepted():
            if fmt == "chatml":
                key = (record.manifest_ref, record.envelope_ref, record.profile)
                if key not in prompt_cache:
                    prompt_cache[key] = _system_prompt_for(*key)
                payload: dict[str, Any] = {
                    "messages": [
                        {"role": "system", "content": prompt_cache[key]},
                        {"role": "user", "content": record.nl},
                        {"role": "assistant", "content": _compact(record.program)},
                    ]
                }
            else:
                payload = {"prompt": record.nl, "completion": _compact(record.program)}
            fh.write(json.dumps(payload, sort_keys=True))
            fh.write("\n")
            count += 1
    return count


def export_dpo(dataset: Dataset, path: Path) -> int:
    """Write rejection_repair records as DPO preference triples; returns the count."""
    prompt_cache: dict[tuple[str, str | None, str], str] = {}
    count = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for record in dataset.repairs():
            if record.repair is None:
                continue
            key = (record.manifest_ref, record.envelope_ref, record.profile)
            if key not in prompt_cache:
                prompt_cache[key] = _system_prompt_for(*key)
            payload = {
                "system": prompt_cache[key],
                "prompt": record.nl,
                "chosen": _compact(record.repair),
                "rejected": _compact(record.program),
                "rejected_error_codes": record.validator_verdict.error_codes,
            }
            fh.write(json.dumps(payload, sort_keys=True))
            fh.write("\n")
            count += 1
    return count
