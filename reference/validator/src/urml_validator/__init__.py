"""urml_validator — static verification engine for the Universal Robot Language.

This package is the reference Python implementation of the URML validator.
It owns the schema definitions for Layer-1 (capability manifest), Layer-2
(intent primitives), and Layer-3 (behavior composition), plus the four-pass
validator that checks a URML program against a manifest and a safety envelope
before execution.

The schemas are the source of truth; JSON Schema is exported on demand for
non-Python consumers (the LLM bridge prompt contract, etc.).

Stability: 0.1.0a0 — pre-alpha. The schemas track the RFC-0002 vocabulary;
the four-pass validator lands in a follow-up release.
"""

from urml_validator._version import __version__
from urml_validator.errors import ErrorCode, ValidationError, ValidationResult
from urml_validator.schema_export import export_all_schemas, export_schema, write_schemas
from urml_validator.schemas.program import URMLProgram
from urml_validator.validator import validate

__all__ = [
    "ErrorCode",
    "URMLProgram",
    "ValidationError",
    "ValidationResult",
    "__version__",
    "export_all_schemas",
    "export_schema",
    "validate",
    "write_schemas",
]
