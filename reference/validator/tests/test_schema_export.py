"""JSON Schema export tests.

Confirm the exporter produces valid Draft 2020-12 schemas, that the post-
processed `$schema` / `$id` / `$comment` fields are stable, and that the
generated schemas actually validate the canonical example.

`jsonschema` isn't a direct dependency of `urml-validator`, so these tests
do their structural validation manually (presence of `$schema`, `type:
object`, required-fields enumeration) rather than running the example
through a third-party validator. Validating the example *against the
emitted schema* with a separate JSON Schema implementation is a worthwhile
follow-up but lives outside this milestone.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from urml_validator import export_all_schemas, export_schema, write_schemas
from urml_validator.schema_export import SCHEMA_REGISTRY

REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLES_ROOT = REPO_ROOT / "examples"


# ---------------------------------------------------------------------------
# Registry coverage
# ---------------------------------------------------------------------------


def test_registry_lists_all_expected_artifacts() -> None:
    """The exporter knows about program, manifest, envelope, and policy."""
    assert set(SCHEMA_REGISTRY.keys()) == {"program", "manifest", "envelope", "policy"}


@pytest.mark.parametrize("name", sorted(SCHEMA_REGISTRY.keys()))
def test_each_schema_is_a_valid_object_schema(name: str) -> None:
    schema = export_schema(name)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"].endswith(f"urml-{name}.schema.json")
    assert schema["type"] == "object"
    # Properties must be declared (even if everything is optional).
    assert "properties" in schema


def test_program_schema_requires_profile_and_behavior() -> None:
    """RFC-0002's program shape has profile + behavior as required."""
    schema = export_schema("program")
    required = set(schema.get("required", []))
    assert "profile" in required
    assert "behavior" in required


def test_manifest_schema_requires_robot_id() -> None:
    schema = export_schema("manifest")
    required = set(schema.get("required", []))
    assert "robot_id" in required


def test_comment_block_is_machine_readable_json() -> None:
    """`$comment` carries a JSON-encoded provenance blob (artifact name, version)."""
    for name, schema in export_all_schemas().items():
        comment = schema["$comment"]
        decoded = json.loads(comment)
        assert decoded["artifact"] == name
        assert decoded["exported_by"] == "urml-validator"
        assert "version" in decoded


# ---------------------------------------------------------------------------
# write_schemas
# ---------------------------------------------------------------------------


def test_write_schemas_creates_all_files(tmp_path: Path) -> None:
    written = write_schemas(tmp_path)
    assert len(written) == len(SCHEMA_REGISTRY)
    expected = {tmp_path / f"urml-{name}.schema.json" for name in SCHEMA_REGISTRY}
    assert set(written) == expected
    for path in written:
        assert path.is_file()
        parsed = json.loads(path.read_text(encoding="utf-8"))
        assert parsed["$schema"] == "https://json-schema.org/draft/2020-12/schema"


def test_write_schemas_creates_missing_directory(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "missing" / "dir"
    write_schemas(target)
    assert target.is_dir()
    assert (target / "urml-program.schema.json").is_file()


def test_emitted_files_are_sorted_and_have_trailing_newline(tmp_path: Path) -> None:
    """Stable on-disk format so the LLM bridge can hash schema files for cache invalidation."""
    written = write_schemas(tmp_path)
    for path in written:
        text = path.read_text(encoding="utf-8")
        assert text.endswith("\n"), f"{path} missing trailing newline"
        parsed = json.loads(text)
        # sort_keys was applied — confirm by re-encoding and comparing.
        re_encoded = json.dumps(parsed, indent=2, sort_keys=True) + "\n"
        assert re_encoded == text


# ---------------------------------------------------------------------------
# Sanity: emitted schema mentions every primitive
# ---------------------------------------------------------------------------


def test_program_schema_mentions_every_primitive() -> None:
    """A regression guard: if a primitive is dropped from the discriminator union,
    the emitted schema's $defs won't reference it. This test catches that early.
    """
    schema_text = json.dumps(export_schema("program"))
    for verb in (
        "MoveToArgs",
        "DockArgs",
        "HoverArgs",
        "WaitArgs",
        "WaitForArgs",
        "GraspArgs",
        "ReleaseArgs",
        "DetectArgs",
        "ScanArgs",
        "MeasureArgs",
        "CaptureArgs",
        "ReportArgs",
    ):
        assert verb in schema_text, f"emitted program schema does not mention {verb}"


# ---------------------------------------------------------------------------
# RFC-0006: connectivity + link-loss reach the exported JSON Schema
# ---------------------------------------------------------------------------


def test_manifest_schema_includes_connectivity_models() -> None:
    """Regression guard: the abstract connectivity block and its nested models
    must appear in the emitted manifest schema's $defs. If `connectivity` is
    ever dropped from CapabilityManifest, this fails early."""
    schema_text = json.dumps(export_schema("manifest"))
    for token in ("Connectivity", "DeclaredLink", "LinkRole", "AssuranceClass"):
        assert token in schema_text, f"manifest schema does not mention {token}"


def test_envelope_schema_includes_link_loss_models() -> None:
    """Regression guard: the structured link-loss policy must be in the
    emitted envelope schema (it is no longer a free-form string)."""
    schema_text = json.dumps(export_schema("envelope"))
    for token in ("LinkLossRule", "LinkLossAction", "link_loss_policy"):
        assert token in schema_text, f"envelope schema does not mention {token}"


# ---------------------------------------------------------------------------
# Round-trip: the canonical example serializes back to schema-valid YAML
# (structural check only — full JSON Schema validation is a follow-up).
# ---------------------------------------------------------------------------


def test_red_mug_example_loads_as_dict() -> None:
    """A precondition for the bridge: the example file is a YAML object the
    LLM bridge can hand straight to the validator."""
    path = EXAMPLES_ROOT / "home" / "red-mug.urml.yaml"
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    assert isinstance(data, dict)
    assert "profile" in data
    assert "behavior" in data
