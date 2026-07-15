"""Mine gold (program, manifest) material out of the repository's fixtures (RFC-0666).

Two sources:

- `mine_fixture_programs()` — every validator-accepted single-robot case in
  the conformance suite. These are gold programs with no paired utterance;
  back-translation supplies one downstream.
- `mine_few_shot_pairs()` — the curated few-shot library from the LLM
  bridge. These already carry natural language and enter the dataset with
  `provenance: few_shot`.

Both yield `GoldExample`, the pre-synthesis shape: the program, the fully
resolved validation context (manifest, envelope, policy, profile), and the
registry names that let a dataset record stay reproducible by reference.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import yaml
from urml_conformance.fixtures import (
    ENVELOPE_REGISTRY,
    MANIFEST_REGISTRY,
    discover_fixtures,
    resolve_envelope,
    resolve_manifest,
    resolve_policy,
)
from urml_llm_bridge.few_shot import (
    drone_few_shots,
    educational_few_shots,
    home_few_shots,
    industrial_few_shots,
)

PolicyArg = dict[str, Any] | None | Literal["DEFAULT"]


@dataclass(frozen=True)
class GoldExample:
    """One gold program plus everything needed to re-validate it."""

    program: dict[str, Any]
    manifest: dict[str, Any]
    manifest_ref: str
    profile: str
    source: str
    envelope: dict[str, Any] | None = None
    envelope_ref: str | None = None
    policy: PolicyArg = "DEFAULT"
    nl: str | None = None


def _validator_manifests_dir() -> Path:
    """The validator's manifest fixture directory, located via the public registry."""
    return MANIFEST_REGISTRY["turtlebot4_home"].parent


def resolve_manifest_ref(name: str) -> dict[str, Any]:
    """Resolve a manifest name against the conformance registry, then the validator fixtures.

    The conformance `MANIFEST_REGISTRY` is the primary namespace. A few
    canonical manifests (the few-shot library's educational buggy) live in
    the validator's fixture directory without a registry entry; those
    resolve by file stem as a fallback.
    """
    if name in MANIFEST_REGISTRY:
        return resolve_manifest(name)
    candidate = _validator_manifests_dir() / f"{name}.yaml"
    if candidate.is_file():
        with candidate.open(encoding="utf-8") as fh:
            loaded = yaml.safe_load(fh)
        if not isinstance(loaded, dict):
            raise ValueError(f"manifest {name!r} did not parse as a mapping")
        return loaded
    raise KeyError(f"unknown manifest {name!r}: not in MANIFEST_REGISTRY and no validator fixture stem matches")


def resolve_envelope_ref(name: str | None) -> dict[str, Any] | None:
    """Resolve an envelope name against the conformance registry; None passes through."""
    if name is None:
        return None
    if name in ENVELOPE_REGISTRY:
        return resolve_envelope(name)
    raise KeyError(f"unknown envelope {name!r}; registered: {sorted(ENVELOPE_REGISTRY.keys())!r}")


def mine_fixture_programs(*, profiles: tuple[str, ...] = ()) -> list[GoldExample]:
    """Every validator-accepted single-robot conformance case as a GoldExample.

    Fleet cases (RFC-0286 rosters) are excluded in v1: they validate with
    `validate_fleet` and need a fleet-aware prompt shape (RFC-0666
    Unresolved questions). Pass `profiles` to keep only those profiles.
    """
    out: list[GoldExample] = []
    for case in discover_fixtures():
        if case.roster is not None or case.manifest is None:
            continue
        if not case.expected_validation.accepted:
            continue
        profile = case.profiles[0] if case.profiles else str(case.program.get("profile", "home"))
        if profiles and profile not in profiles:
            continue
        out.append(
            GoldExample(
                program=case.program,
                manifest=resolve_manifest(case.manifest),
                manifest_ref=case.manifest,
                profile=profile,
                source=case.name,
                envelope=resolve_envelope_ref(case.envelope),
                envelope_ref=case.envelope,
                policy=resolve_policy(case.policy),
            )
        )
    return out


# Profile -> (manifest name, envelope name). Mirrors the pairings that
# `test_few_shot_library.py` asserts every few-shot validates against.
# The fleet set is excluded for the same reason fleet fixtures are.
_FEW_SHOT_CONTEXT: dict[str, tuple[str, str | None]] = {
    "home": ("turtlebot4_home", "home_default"),
    "industrial": ("industrial_cell", None),
    "drone": ("drone_civilian", "drone_default"),
    "educational": ("educational_buggy", None),
}


def mine_few_shot_pairs(*, profiles: tuple[str, ...] = ()) -> list[GoldExample]:
    """The curated few-shot library as (utterance, program) GoldExamples."""
    factories = {
        "home": home_few_shots,
        "industrial": industrial_few_shots,
        "drone": drone_few_shots,
        "educational": educational_few_shots,
    }
    out: list[GoldExample] = []
    for profile, factory in factories.items():
        if profiles and profile not in profiles:
            continue
        manifest_ref, envelope_ref = _FEW_SHOT_CONTEXT[profile]
        manifest = resolve_manifest_ref(manifest_ref)
        envelope = resolve_envelope_ref(envelope_ref)
        for shot in factory():
            out.append(
                GoldExample(
                    program=shot.program,
                    manifest=manifest,
                    manifest_ref=manifest_ref,
                    profile=profile,
                    source=f"few_shot:{profile}",
                    envelope=envelope,
                    envelope_ref=envelope_ref,
                    nl=shot.user,
                )
            )
    return out
