"""urml_validator — static verification engine for the Universal Robot Language.

This package is the reference Python implementation of the URML validator.
It owns the schema definitions for Layer-1 (capability manifest), Layer-2
(intent primitives), and Layer-3 (behavior composition), plus the four-pass
validator that checks a URML program against a manifest and a safety envelope
before execution.

The schemas are the source of truth; JSON Schema is exported on demand for
non-Python consumers (the LLM bridge prompt contract, etc.).

Stability: 0.4.0. The schemas track the RFC-0002 vocabulary; the
five-pass validator and `urml` CLI are shipped, and the namespaced
error codes in `errors.py` are a stable public API.
"""

from urml_validator._version import __version__
from urml_validator.errors import ErrorCode, ValidationError, ValidationResult
from urml_validator.monitor import (
    CompiledProperty,
    Entity,
    OnlineMonitor,
    PropertyVerdict,
    Sample,
    Violation,
    compile_envelope_monitors,
    evaluate_trace,
)
from urml_validator.policy_engine import evaluate_policy
from urml_validator.schema_export import export_all_schemas, export_schema, write_schemas
from urml_validator.schemas.policy import Policy, PolicyRule
from urml_validator.schemas.program import URMLProgram
from urml_validator.schemas.roster import FleetRoster, RosterMember
from urml_validator.validator import DEFAULT_POLICY, validate, validate_fleet

__all__ = [
    "DEFAULT_POLICY",
    "CompiledProperty",
    "Entity",
    "ErrorCode",
    "FleetRoster",
    "OnlineMonitor",
    "Policy",
    "PolicyRule",
    "PropertyVerdict",
    "RosterMember",
    "Sample",
    "URMLProgram",
    "ValidationError",
    "ValidationResult",
    "Violation",
    "__version__",
    "compile_envelope_monitors",
    "evaluate_policy",
    "evaluate_trace",
    "export_all_schemas",
    "export_schema",
    "validate",
    "validate_fleet",
    "write_schemas",
]
