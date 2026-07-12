"""Oracle-filtered dataset synthesis (RFC-0666).

`synthesize()` turns mined `GoldExample`s into `DatasetRecord`s:

1. Utterances: a few-shot example brings its own; a fixture program gets
   back-translated.
2. The oracle: every program is re-validated against its manifest,
   envelope, profile, and policy at synthesis time. Rejected programs are
   dropped and reported, never silently.
3. Dedup: records collapse on (utterance, canonical program JSON).

The oracle call is not optional and not cached across schema versions: a
dataset is only as trustworthy as the validator that filtered it.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from urml_validator import validate

from urml_model.backtranslate import BackTranslator, TemplateBackTranslator
from urml_model.dataset import Dataset, DatasetRecord, Provenance, ValidatorVerdict
from urml_model.mining import GoldExample


@dataclass
class SynthesisReport:
    """What synthesize() kept and what it dropped, with reasons."""

    kept: int = 0
    deduplicated: int = 0
    dropped_rejected: list[tuple[str, list[str]]] = field(default_factory=list)
    dropped_no_utterance: list[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [f"kept {self.kept} record(s); {self.deduplicated} duplicate(s) collapsed"]
        if self.dropped_rejected:
            lines.append(f"dropped {len(self.dropped_rejected)} validator-rejected program(s):")
            lines.extend(f"  {source}: {codes}" for source, codes in self.dropped_rejected)
        if self.dropped_no_utterance:
            lines.append(
                f"dropped {len(self.dropped_no_utterance)} program(s) the translator "
                f"produced no utterance for: {self.dropped_no_utterance}"
            )
        return "\n".join(lines)


def synthesize(
    gold: list[GoldExample],
    translator: BackTranslator | None = None,
    *,
    per_program: int = 1,
    language: str = "en",
) -> tuple[Dataset, SynthesisReport]:
    """Produce an oracle-filtered dataset from mined gold examples."""
    translator = translator if translator is not None else TemplateBackTranslator()
    dataset = Dataset()
    report = SynthesisReport()
    seen: set[tuple[str, str]] = set()

    for example in gold:
        verdict = validate(
            example.program,
            example.manifest,
            example.envelope,
            profiles=(example.profile,),
            policy=example.policy,
        )
        if not verdict.accepted:
            report.dropped_rejected.append((example.source, verdict.codes()))
            continue

        if example.nl is not None:
            utterances = [example.nl]
            provenance: Provenance = "few_shot"
        else:
            utterances = translator.to_utterances(
                example.program, example.manifest, language=language, n=per_program
            )
            provenance = (
                "fixture_backtranslation"
                if isinstance(translator, TemplateBackTranslator)
                else "llm_backtranslation"
            )
            if not utterances:
                report.dropped_no_utterance.append(example.source)
                continue

        for utterance in utterances:
            record = DatasetRecord(
                nl=utterance,
                program=example.program,
                manifest_ref=example.manifest_ref,
                profile=example.profile,
                language=language,
                provenance=provenance,
                validator_verdict=ValidatorVerdict(accepted=True),
                envelope_ref=example.envelope_ref,
            )
            key = record.dedup_key()
            if key in seen:
                report.deduplicated += 1
                continue
            seen.add(key)
            dataset.records.append(record)
            report.kept += 1

    return dataset, report
