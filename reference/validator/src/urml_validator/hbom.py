"""Structured HBOM parsing for Pass 5 (RFC-0005).

The v0.1 manifest records a Hardware Bill of Materials *by reference*:
``format``, ``uri``, and a ``sha256`` integrity hash, but never the parsed
contents. That lets a policy gate on the manifest's *declared* provenance
facts (vendor, country, role) but not on the *parsed* HBOM (for example,
"no critical component contains a chip from a covered foreign country, even
one hidden behind an integrator's own part number"). RFC-0005 closes that
gap with an opt-in, content-aware sub-pass.

This module is the parser half: it resolves a component's ``hbom_ref`` to a
local file, verifies the declared SHA-256, and reads the CycloneDX document
into a flat list of :class:`HBOMComponent` records. The policy engine
(``policy_engine``) is the evaluator half.

Design notes:

- **Dependency-free on purpose.** A CycloneDX document is JSON. We read the
  small, stable subset the content predicates need (component name, supplier
  and manufacturer name and country, and the full pedigree tree) with the
  standard library, rather than taking a runtime dependency on
  ``cyclonedx-python-lib``. This matches URML's hermetic posture (the
  MockROSAdapter, the pure-Python demo hero): the validator installs and runs
  the same on any OS with zero extra wheels, and an air-gapped federal
  deployment needs no wheelhouse for the parser. Strict, full-schema
  CycloneDX validation against the library is a documented follow-up
  (RFC-0005 Phase D), not a prerequisite for the content predicates.
- **The pedigree is walked.** ``pedigree.ancestors``, ``pedigree.descendants``,
  ``pedigree.variants``, and nested ``components`` are all flattened, so a
  country/vendor predicate catches a covered part at any depth (NDAA §889
  vendor-of-vendor).
- **No network.** A remote ``uri`` is reported unreachable rather than
  fetched; the validator does not phone home (RFC-0005 unresolved Q1, the
  conservative default).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from urml_validator.errors import ErrorCode

# Schemes we treat as remote (not fetched in v0.2). A bare local path or an
# explicit file:// uri is local; anything with a network scheme is remote.
_REMOTE_SCHEMES = frozenset({"http", "https", "ftp", "ftps", "s3", "gs"})


@dataclass(frozen=True)
class HBOMComponent:
    """One node in a parsed HBOM, flattened out of the pedigree tree.

    ``country`` and ``vendor`` are best-effort: CycloneDX lets a component
    name a supplier, a manufacturer, both, or neither. We resolve in that
    order and keep ``None`` when nothing is declared (an unknown-origin part
    is not the same as a clean one, and predicates treat ``None`` as
    "not in the deny-list").
    """

    name: str
    vendor: str | None = None
    country: str | None = None
    #: How deep in the pedigree this node sits (0 = a top-level component).
    pedigree_depth: int = 0


class HBOMError(Exception):
    """A recoverable HBOM-resolution failure, carrying the policy error code.

    The engine turns this into a ``ValidationError`` (an error for parse
    failures, a warning for unreachable uris) rather than letting it abort
    the whole validation run.
    """

    def __init__(self, code: ErrorCode, detail: dict) -> None:
        super().__init__(detail.get("reason", code.value))
        self.code = code
        self.detail = detail


# ---------------------------------------------------------------------------
# Resolution: ref -> bytes -> parsed components
# ---------------------------------------------------------------------------


def resolve_and_parse(
    hbom_ref: object,
    base_dir: Path | None,
) -> list[HBOMComponent]:
    """Resolve a manifest ``HBOMRef`` to a flat list of HBOM components.

    Args:
        hbom_ref: The component's ``hbom_ref`` (an ``HBOMRef`` model with
            ``format`` / ``uri`` / ``sha256``).
        base_dir: Directory a relative ``uri`` is resolved against — normally
            the manifest file's own directory. ``None`` means relative uris
            cannot be resolved (a programmatic caller that passed manifests as
            in-memory dicts); a relative uri then reports unreachable.

    Returns:
        The flattened component list (pedigree included).

    Raises:
        HBOMError: With ``POLICY_HBOM_URI_UNREACHABLE`` (remote uri, missing
            base_dir, or absent file) or ``POLICY_HBOM_PARSE_FAILED`` (hash
            mismatch, malformed JSON, or unsupported format).
    """
    uri: str = getattr(hbom_ref, "uri", "")
    fmt: str = getattr(hbom_ref, "format", "")
    declared_sha: str | None = getattr(hbom_ref, "sha256", None)

    path = _resolve_local_path(uri, base_dir)

    data = path.read_bytes()
    if declared_sha:
        actual_sha = hashlib.sha256(data).hexdigest()
        if actual_sha.lower() != declared_sha.lower():
            raise HBOMError(
                ErrorCode.POLICY_HBOM_PARSE_FAILED,
                {
                    "reason": "hash_mismatch",
                    "hash_mismatch": True,
                    "uri": uri,
                    "declared_sha256": declared_sha,
                    "actual_sha256": actual_sha,
                },
            )

    try:
        doc = json.loads(data.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise HBOMError(
            ErrorCode.POLICY_HBOM_PARSE_FAILED,
            {"reason": "malformed_json", "uri": uri, "error": str(exc)},
        ) from exc

    if fmt.startswith("cyclonedx"):
        return parse_cyclonedx(doc)
    raise HBOMError(
        ErrorCode.POLICY_HBOM_PARSE_FAILED,
        {
            "reason": "unsupported_format",
            "uri": uri,
            "format": fmt,
            "supported": ["cyclonedx-*"],
        },
    )


def _resolve_local_path(uri: str, base_dir: Path | None) -> Path:
    """Map a uri to a readable local Path or raise an unreachable HBOMError."""
    parsed = urlparse(uri)
    if parsed.scheme in _REMOTE_SCHEMES:
        raise HBOMError(
            ErrorCode.POLICY_HBOM_URI_UNREACHABLE,
            {"reason": "remote_uri_not_fetched", "uri": uri, "scheme": parsed.scheme},
        )

    raw = parsed.path if parsed.scheme == "file" else uri
    candidate = Path(raw)
    if not candidate.is_absolute():
        if base_dir is None:
            raise HBOMError(
                ErrorCode.POLICY_HBOM_URI_UNREACHABLE,
                {"reason": "no_base_dir_for_relative_uri", "uri": uri},
            )
        candidate = (base_dir / raw).resolve()

    if not candidate.is_file():
        raise HBOMError(
            ErrorCode.POLICY_HBOM_URI_UNREACHABLE,
            {"reason": "file_not_found", "uri": uri, "resolved": str(candidate)},
        )
    return candidate


# ---------------------------------------------------------------------------
# CycloneDX subset parsing
# ---------------------------------------------------------------------------


def parse_cyclonedx(doc: dict) -> list[HBOMComponent]:
    """Flatten a CycloneDX JSON document into HBOMComponent records.

    Walks ``components[]`` plus each component's ``pedigree`` (ancestors,
    descendants, variants) and nested ``components``. Order is a stable
    depth-first pre-order so the engine reports a deterministic "first
    offending component".
    """
    out: list[HBOMComponent] = []
    seen: set[int] = set()
    for raw in doc.get("components", []) or []:
        _walk_component(raw, depth=0, out=out, seen=seen)
    return out


def _walk_component(raw: dict, *, depth: int, out: list, seen: set) -> None:
    if not isinstance(raw, dict):
        return
    # Guard against a pedigree that references itself into a cycle.
    marker = id(raw)
    if marker in seen:
        return
    seen.add(marker)

    out.append(
        HBOMComponent(
            name=str(raw.get("name", "<unnamed>")),
            vendor=_resolve_vendor(raw),
            country=_resolve_country(raw),
            pedigree_depth=depth,
        )
    )

    for child in raw.get("components", []) or []:
        _walk_component(child, depth=depth, out=out, seen=seen)

    pedigree = raw.get("pedigree")
    if isinstance(pedigree, dict):
        for chain in ("ancestors", "descendants", "variants"):
            for node in pedigree.get(chain, []) or []:
                _walk_component(node, depth=depth + 1, out=out, seen=seen)


def _resolve_vendor(raw: dict) -> str | None:
    """Supplier name, then manufacturer name, then publisher/author."""
    for key in ("supplier", "manufacturer"):
        entity = raw.get(key)
        if isinstance(entity, dict):
            name = entity.get("name")
            if isinstance(name, str) and name:
                return name
    for key in ("publisher", "author"):
        val = raw.get(key)
        if isinstance(val, str) and val:
            return val
    return None


def _resolve_country(raw: dict) -> str | None:
    """Supplier address country, then manufacturer address country."""
    for key in ("supplier", "manufacturer"):
        entity = raw.get(key)
        if not isinstance(entity, dict):
            continue
        address = entity.get("address")
        if isinstance(address, dict):
            country = address.get("country")
            if isinstance(country, str) and country:
                return country
    return None
