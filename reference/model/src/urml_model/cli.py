"""urml-model — synthesize, export, and evaluate the URML-native model dataset (RFC-0666).

Three subcommands:

- ``urml-model synthesize --out data.jsonl`` mines the repo's gold assets
  (conformance fixtures + few-shot library), back-translates fixture
  programs with the deterministic template renderer, filters everything
  through the validator oracle, and writes the dataset. Hermetic: no
  network, no LLM.
- ``urml-model export --in data.jsonl --out sft.jsonl --fmt chatml`` writes
  training files (chatml / completions / dpo).
- ``urml-model eval`` scores any local or canned model against a profile's
  utterance set with the conformance scorer and writes the ResultRow YAML.
  The LLM back-translation path (dataset diversity at scale) is a library
  call, not a CLI flag: it needs an operator-configured provider and spend.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from urml_model.backtranslate import TemplateBackTranslator
from urml_model.dataset import Dataset
from urml_model.export import export_dpo, export_sft
from urml_model.mining import mine_few_shot_pairs, mine_fixture_programs, resolve_manifest_ref
from urml_model.synthesize import synthesize


def _cmd_synthesize(args: argparse.Namespace) -> int:
    profiles = tuple(args.profile or ())
    gold = []
    if not args.no_fixtures:
        gold.extend(mine_fixture_programs(profiles=profiles))
    if not args.no_few_shots:
        gold.extend(mine_few_shot_pairs(profiles=profiles))
    dataset, report = synthesize(gold, TemplateBackTranslator(), per_program=args.per_program)
    count = dataset.write_jsonl(Path(args.out))
    print(report.summary())
    print(f"wrote {count} record(s) to {args.out}")
    return 0


def _cmd_export(args: argparse.Namespace) -> int:
    dataset = Dataset.read_jsonl(Path(args.infile))
    out = Path(args.out)
    if args.fmt == "dpo":
        count = export_dpo(dataset, out)
    else:
        count = export_sft(dataset, out, fmt=args.fmt)
    print(f"wrote {count} {args.fmt} example(s) to {out}")
    return 0


def _build_eval_provider(args: argparse.Namespace) -> Any:
    if args.backend == "echo":
        if not args.echo_responses:
            raise SystemExit("--backend echo requires --echo-responses (JSON map of utterance -> emission)")
        with Path(args.echo_responses).open(encoding="utf-8") as fh:
            responses = json.load(fh)
        if not isinstance(responses, dict):
            raise SystemExit("--echo-responses must contain a JSON object")
        from urml_llm_bridge.providers.echo import EchoProvider

        return EchoProvider(responses={str(k): str(v) for k, v in responses.items()})
    if args.backend == "ollama":
        from urml_llm_bridge.providers.ollama import OllamaProvider

        return OllamaProvider(model=args.model)
    from urml_llm_bridge.providers.llama_cpp import LlamaCppProvider

    return LlamaCppProvider(model_label=args.model)


def _cmd_eval(args: argparse.Namespace) -> int:
    from urml_conformance.llm_bridge.loader import load_utterances
    from urml_conformance.llm_bridge.scorer import score

    utterances = load_utterances(Path(args.utterances_root), profile=args.profile, language=args.language)
    manifest = resolve_manifest_ref(utterances.manifest)
    recorded_at = args.recorded_at or datetime.now(UTC).isoformat(timespec="seconds")
    row = score(
        provider=_build_eval_provider(args),
        utterances=utterances,
        manifest=manifest,
        backend=args.backend,
        model_id=args.model,
        recorded_at=recorded_at,
        max_revisions=args.max_revisions,
    )
    payload = dataclasses.asdict(row)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        yaml.safe_dump(payload, fh, sort_keys=True)
    print(
        f"{row.model_id} on {row.profile}: structural {row.structural_pass_rate}, "
        f"semantic {row.semantic_pass_rate}, revisions {row.revision_attempts_mean}"
    )
    print(f"wrote {out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="urml-model", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_syn = sub.add_parser("synthesize", help="mine + back-translate + oracle-filter into a dataset JSONL")
    p_syn.add_argument("--out", required=True, help="output dataset JSONL path")
    p_syn.add_argument("--profile", action="append", help="restrict to a profile (repeatable)")
    p_syn.add_argument("--per-program", type=int, default=1, help="utterances per fixture program")
    p_syn.add_argument("--no-fixtures", action="store_true", help="skip conformance-fixture mining")
    p_syn.add_argument("--no-few-shots", action="store_true", help="skip the few-shot library")
    p_syn.set_defaults(func=_cmd_synthesize)

    p_exp = sub.add_parser("export", help="write SFT/DPO training files from a dataset JSONL")
    p_exp.add_argument("--in", dest="infile", required=True, help="input dataset JSONL")
    p_exp.add_argument("--out", required=True, help="output path")
    p_exp.add_argument("--fmt", choices=("chatml", "completions", "dpo"), default="chatml")
    p_exp.set_defaults(func=_cmd_export)

    p_eval = sub.add_parser("eval", help="score a model against an utterance set (conformance scorer)")
    p_eval.add_argument("--utterances-root", required=True, help="root dir holding <profile>/utterances-<lang>.yaml")
    p_eval.add_argument("--profile", required=True)
    p_eval.add_argument("--language", default="en")
    p_eval.add_argument("--backend", choices=("echo", "ollama", "llama_cpp"), required=True)
    p_eval.add_argument("--model", required=True, help="model id label for the result row")
    p_eval.add_argument("--out", required=True, help="output ResultRow YAML path")
    p_eval.add_argument("--max-revisions", type=int, default=3)
    p_eval.add_argument("--recorded-at", help="ISO timestamp for the row (defaults to now, UTC)")
    p_eval.add_argument("--echo-responses", help="echo backend: JSON file mapping utterance -> emission")
    p_eval.set_defaults(func=_cmd_eval)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result: int = args.func(args)
    return result


if __name__ == "__main__":
    sys.exit(main())
