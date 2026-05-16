"""System-prompt construction for the bridge.

The bridge assembles the LLM's system prompt from:

  1. A short instruction about URML.
  2. The robot's declared capabilities (manifest summary).
  3. The active safety envelope (if any).
  4. The active profile(s).
  5. The JSON Schema the emitted program must satisfy (from urml_validator).
  6. Few-shot examples.
  7. On revision: the previous emission plus the validator's structured errors.

The system prompt is treated as opaque text by `LLMProvider`; the provider
adapter is free to translate it (e.g., Anthropic accepts a `system`
parameter directly; some adapters may need to inline it as the first
turn of a conversation).
"""

from __future__ import annotations

import json
from typing import Any

from urml_llm_bridge.few_shot import FewShot

# A small, deliberately-stable header. Providers will sometimes prepend or
# wrap; treating this as a stable string makes prompt-cache hit rates
# predictable.
_INSTRUCTION_HEADER = """\
You are a robot-intent translator. Your job is to convert a user's
natural-language request into a URML program — a small, structured
description of what the robot should do.

You MUST emit a single JSON object that conforms to the URML program
schema attached below. Do NOT wrap the JSON in Markdown code fences.
Do NOT include commentary or explanation outside the JSON.

Use only the primitives, locations, frames, object classes, sensors,
and docking-station services declared in the manifest below. If the
user's request requires something the manifest does not declare,
emit a `report` step with `status: failure` and a `facts.reason`
explaining what is missing — do not fabricate undeclared capabilities.

Respect the safety envelope, if one is provided.
"""


def build_system_prompt(
    *,
    schema: dict[str, Any],
    manifest: dict[str, Any],
    envelope: dict[str, Any] | None = None,
    profiles: tuple[str, ...] = (),
    few_shots: list[FewShot] | None = None,
    revision_context: str | None = None,
) -> str:
    """Assemble the full system prompt as a single string.

    Args:
        schema:           JSON Schema for URMLProgram (from urml_validator.export_schema('program')).
        manifest:         The robot's capability manifest (raw dict form).
        envelope:         Optional active safety envelope.
        profiles:         Profile names this request targets. Currently informational.
        few_shots:        Examples to include in the prompt. Empty list = no examples.
        revision_context: When set, appended at the end with the prior emission and
                          the validator's structured errors. Used during the revision loop.
    """
    parts: list[str] = [_INSTRUCTION_HEADER]
    parts.append(f"Active profile(s): {', '.join(profiles) if profiles else '(none declared)'}")
    parts.append("")

    parts.append("=== Robot capability manifest ===")
    parts.append(_summarise_manifest(manifest))
    parts.append("")

    if envelope:
        parts.append("=== Active safety envelope ===")
        parts.append(_summarise_envelope(envelope))
        parts.append("")

    if few_shots:
        parts.append("=== Examples ===")
        for idx, ex in enumerate(few_shots, start=1):
            parts.append(f"--- Example {idx} ---")
            if ex.note:
                parts.append(f"# {ex.note}")
            parts.append(f"User request: {ex.user}")
            parts.append("Emitted URML:")
            parts.append(json.dumps(ex.program, indent=2))
            parts.append("")

    parts.append("=== URML program JSON Schema ===")
    parts.append(json.dumps(schema, indent=2, sort_keys=True))
    parts.append("")

    if revision_context:
        parts.append("=== Revision required ===")
        parts.append(revision_context)
        parts.append("")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Compact summaries
# ---------------------------------------------------------------------------


def _summarise_manifest(manifest: dict[str, Any]) -> str:
    """Render the manifest as a compact, prompt-friendly summary.

    The raw manifest contains fields the LLM does not need (build metadata,
    free-form descriptions). Trimming them keeps the prompt short and
    increases the chance of a cache hit on identical-manifest calls.
    """
    lines: list[str] = []
    lines.append(f"Robot ID: {manifest.get('robot_id', '<unknown>')}")
    if manifest.get("description"):
        lines.append(f"Description: {manifest['description']}")

    frames = manifest.get("frames") or []
    if frames:
        names = [f["name"] for f in frames]
        lines.append(f"Frames: {', '.join(names)}")

    declared_locations = manifest.get("declared_locations") or []
    if declared_locations:
        names = [loc["name"] for loc in declared_locations]
        lines.append(f"Declared locations: {', '.join(names)}")

    if manifest.get("declared_events"):
        lines.append(f"Declared events: {', '.join(manifest['declared_events'])}")

    mob = manifest.get("mobility")
    if mob:
        bits = [f"drive={mob.get('drive_type')}", f"max_velocity={mob.get('max_velocity')} m/s"]
        if mob.get("station_keeping"):
            bits.append("station_keeping=true")
        if mob.get("service_ceiling") is not None:
            bits.append(f"service_ceiling={mob['service_ceiling']} m")
        lines.append("Mobility: " + ", ".join(bits))

    manip = manifest.get("manipulation")
    if manip:
        grippers = [
            f"{g['name']}({g['kind']}, {g['force_min_n']}-{g['force_max_n']} N)"
            for g in manip.get("grippers") or []
        ]
        if grippers:
            lines.append("Grippers: " + ", ".join(grippers))
        if manip.get("reachable_workspace_m") is not None:
            lines.append(f"Reachable workspace: {manip['reachable_workspace_m']} m")

    perc = manifest.get("perception")
    if perc:
        if perc.get("cameras"):
            cams = []
            for c in perc["cameras"]:
                modes = []
                if c.get("supports_photo"):
                    modes.append("photo")
                if c.get("supports_video"):
                    modes.append("video")
                if c.get("supports_stream"):
                    modes.append("stream")
                tag = "movable" if c.get("movable") else "fixed"
                cams.append(f"{c['name']}({tag}, {'/'.join(modes)})")
            lines.append("Cameras: " + ", ".join(cams))
        if perc.get("sensors"):
            sensors = [f"{s['name']}({s['measurement_type']})" for s in perc["sensors"]]
            lines.append("Sensors: " + ", ".join(sensors))
        if perc.get("object_vocabulary"):
            lines.append("Object vocabulary: " + ", ".join(perc["object_vocabulary"]))

    if manifest.get("docking_stations"):
        stations = [
            f"{s['name']}({'+'.join(s.get('services') or [])})"
            for s in manifest["docking_stations"]
        ]
        lines.append("Docking stations: " + ", ".join(stations))

    outputs = manifest.get("outputs") or {}
    if outputs.get("named_endpoints"):
        lines.append("Output endpoints: " + ", ".join(outputs["named_endpoints"]))

    connectivity = manifest.get("connectivity") or {}
    links = connectivity.get("links") or []
    if links:
        bits = []
        for link in links:
            tags = []
            if link.get("required_for_operation"):
                tags.append("required")
            if link.get("autonomous_when_lost"):
                tags.append("autonomous-on-loss")
            tags.append(link.get("assurance_class", "best_effort"))
            bits.append(f"{link.get('role')}({', '.join(tags)})")
        lines.append("Connectivity links: " + ", ".join(bits))

    return "\n".join(lines)


def _summarise_envelope(envelope: dict[str, Any]) -> str:
    """Render the envelope as a compact summary."""
    lines: list[str] = []
    if envelope.get("deployment_id"):
        lines.append(f"Deployment: {envelope['deployment_id']}")
    if envelope.get("description"):
        lines.append(f"Description: {envelope['description']}")
    caps: list[str] = []
    for key in ("max_velocity", "max_altitude", "max_payload", "max_grip_force_n"):
        if envelope.get(key) is not None:
            caps.append(f"{key}={envelope[key]}")
    if caps:
        lines.append("Caps: " + ", ".join(caps))
    if envelope.get("geofences"):
        lines.append(f"Geofences: {len(envelope['geofences'])} polygon(s) declared")
    if envelope.get("people_occupancy_zones"):
        lines.append(f"People-occupancy zones: {len(envelope['people_occupancy_zones'])} declared")
    if envelope.get("weather"):
        w = envelope["weather"]
        bits = [f"{k}={v}" for k, v in w.items() if v is not None]
        if bits:
            lines.append("Weather thresholds: " + ", ".join(bits))
    rules = envelope.get("link_loss_policy") or []
    if rules:
        summary = []
        for r in rules:
            label = f"{r.get('role')}->{r.get('action')}"
            if r.get("max_outage_seconds") is not None:
                label += f" (<= {r['max_outage_seconds']}s)"
            summary.append(label)
        lines.append("Link-loss policy: " + ", ".join(summary))
    return "\n".join(lines) if lines else "(empty envelope)"


def render_revision_context(
    *,
    prior_emission: str,
    error_payload: list[dict[str, Any]],
) -> str:
    """Render the revision-loop context the bridge appends on each retry."""
    lines = [
        "Your previous emission was rejected by the URML validator. "
        "Inspect the structured errors below and emit a CORRECTED program.",
        "",
        "Previous emission:",
        prior_emission,
        "",
        "Validator errors (machine-readable):",
        json.dumps(error_payload, indent=2),
    ]
    return "\n".join(lines)
