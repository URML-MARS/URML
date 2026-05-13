"""JSON Schema export.

Two top-level artifacts the rest of the URML toolchain consumes:

- **`urml-program.schema.json`** — what a URML program looks like. Goes into
  the LLM bridge's system prompt as the structured-output contract.
- **`urml-manifest.schema.json`** — what a robot's capability manifest looks
  like. Used by robot makers to validate their manifests and by the LLM
  bridge to inject the active robot's capabilities into the prompt.

Pydantic v2's `model_json_schema()` does the heavy lifting; this module's
job is to (a) post-process the output for two minor presentational fixes
the LLM bridge prefers, and (b) provide a stable Python API and CLI for
writing the schemas to disk.

The schemas are emitted at **JSON Schema Draft 2020-12** — the dialect
pydantic v2 produces by default and the dialect the Anthropic and OpenAI
structured-output features both target.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from urml_validator._version import __version__
from urml_validator.schemas.envelope import SafetyEnvelope
from urml_validator.schemas.manifest import CapabilityManifest
from urml_validator.schemas.policy import Policy
from urml_validator.schemas.program import URMLProgram

#: The named schemas this module knows how to export.
SCHEMA_REGISTRY: dict[str, type[BaseModel]] = {
    "program": URMLProgram,
    "manifest": CapabilityManifest,
    "envelope": SafetyEnvelope,
    "policy": Policy,
}


def export_schema(name: str) -> dict[str, Any]:
    """Return the JSON Schema for a single named artifact as a Python dict.

    Args:
        name: One of "program", "manifest", "envelope".

    Returns:
        A Draft 2020-12 JSON Schema document.

    Raises:
        KeyError: If `name` is not in SCHEMA_REGISTRY.
    """
    model = SCHEMA_REGISTRY[name]
    raw = model.model_json_schema(mode="serialization")
    return _post_process(raw, name=name)


def export_all_schemas() -> dict[str, dict[str, Any]]:
    """Return every registered schema as a dict keyed by artifact name."""
    return {name: export_schema(name) for name in SCHEMA_REGISTRY}


def write_schemas(output_dir: Path) -> list[Path]:
    """Write all registered schemas to `output_dir` as `urml-<name>.schema.json`.

    Creates `output_dir` if it doesn't exist.

    Returns:
        The list of paths written, in registry order.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, schema in export_all_schemas().items():
        path = output_dir / f"urml-{name}.schema.json"
        path.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append(path)
    return written


# ---------------------------------------------------------------------------
# Post-processing
# ---------------------------------------------------------------------------


_TARGET_DIALECT = "https://json-schema.org/draft/2020-12/schema"


def _post_process(schema: dict[str, Any], *, name: str) -> dict[str, Any]:
    """Apply small, additive fixups the URML LLM bridge prefers.

    Currently:

    - Pin `$schema` to JSON Schema Draft 2020-12 so downstream tools know
      exactly which dialect to validate against.
    - Set a stable `$id` per artifact so multiple schemas can be loaded
      side-by-side in one validator session without collisions.
    - Stamp a `urml.exported_by` and `urml.version` block under `$comment`
      so consumers can detect schema-version drift without parsing strings.
    """
    fixed = dict(schema)  # shallow copy; we only touch top-level keys
    fixed["$schema"] = _TARGET_DIALECT
    fixed["$id"] = f"https://urml.org/schemas/v0.1/urml-{name}.schema.json"
    fixed["$comment"] = json.dumps(
        {"exported_by": "urml-validator", "version": __version__, "artifact": name},
        sort_keys=True,
    )
    return fixed
