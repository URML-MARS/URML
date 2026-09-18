---
rfc: 0699
title: A `camera` selector for the `capture` primitive
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-09-18
updated: 2026-09-18
supersedes: —
superseded-by: —
---

<p align="center">
  <a href="https://urml.dev"><img src="https://urml.dev/favicon.svg" alt="URML" width="72" height="72"></a>
</p>

<p align="center">
  A small, opinionated, human-readable language for describing robot intent.
</p>

<p align="center">
  <a href="https://urml.dev"><b>urml.dev</b></a>
</p>

---

# RFC-0699: A `camera` selector for the `capture` primitive

**Kind: Spec.** This is a normative Layer-2 change: one optional field on the `capture` primitive and the static checks it enables. It is backward compatible. The implementation lands in the same PR for review and merges on maintainer acceptance.

## Summary

`capture` is the only URML perception primitive with no way to name its source. Its siblings `scan` and `measure` already carry an optional `sensor` field that the validator resolves against declared perception names; `capture` does not. On a robot with more than one camera, a program cannot say which camera to shoot with, and a targeted capture validates as long as *any* declared camera is movable. This RFC adds an optional `camera` field to `capture` that names a declared `perception.cameras` entry, and scopes capture's existing capability checks to that one camera.

## Motivation

The gap became concrete on the rai-opensource `spot_ros2` conversation ([Discussion #805](https://github.com/rai-opensource/spot_ros2/discussions/805)). A Boston Dynamics Spot with the Spot Arm declares five fixed body fisheyes (photo-only) and one movable hand camera (`hand_color`, photo and video). A program that means "photograph that valve" means the hand camera: a fixed fisheye cannot be pointed at a subject. Today `capture(media: photo, target: $valve)` on that robot validates, because the validator only asks whether *some* declared camera is movable, and `hand_color` is. A program that named the wrong camera, or meant a specific one, passes the static gate. This was carried into the Spot Arm manifest as an honest caveat.

The fix is small and already has a precedent in the vocabulary: `scan` and `measure` name a source with an optional `sensor` field. `capture`'s source is always a camera, so the field is named `camera` and resolves against `perception.cameras[].name`.

## Detailed design

All additions are optional. A `capture` step with no `camera` behaves exactly as before this RFC, so existing programs, fixtures, and examples are unaffected.

### 1. Layer-2 spec (`capture`)

`capture` gains one optional field:

```yaml
- capture:
    media: photo | video
    target: $name | <location | pose>   # optional; default: current view
    duration: <time>                    # required iff media == video
    attributes: {resolution?, format?, frame_rate?}   # optional
    camera: <name>                      # optional; names a declared perception.cameras entry
    store_as: <name>                    # required
```

When `camera` is set it MUST name a declared camera, and every capability check is scoped to that one camera: it must support the requested mode, and if `target` is set it must have `movable: true`. With no selector, at least one eligible declared camera must satisfy those conditions (the prior behavior). No manifest change is needed: cameras are already declared individually under `perception.cameras[].name` (each with `movable`, `supports_photo`, `supports_video`, per Layer-1 HAL and RFC-0682).

### 2. Schema

`CaptureArgs` gains `camera: Identifier | None = None`, mirroring `ScanArgs.sensor` and `MeasureArgs.sensor`. The field flows into the exported program schema through the existing generator; `extra="forbid"` continues to reject any other key.

### 3. Validator (Pass 2 capability check)

`_check_capture_caps` resolves a named `camera` against `perception.cameras`, following the shape of the `scan`/`measure` sensor checks:

- Undeclared camera → `capability.missing_camera` (field `camera`).
- Named camera that does not support the requested mode → `capability.video_unsupported` for video, else `capability.missing_camera`, scoped to that camera.
- `target` set and the named camera is fixed → `capability.fixed_camera_target`, even when a movable camera exists elsewhere on the robot.

No new error code is introduced; the existing `capability.*` codes are reused, as `scan` reuses `capability.missing_sensor`. Error-code strings are public API (the LLM bridge consumes them), so reuse rather than rename is deliberate.

### 4. Reference runtime

The `ROSAdapter` Protocol's `capture_media` gains `camera: str | None = None`, the way RFC-0586 added `grasp_type` to `send_manipulation_goal`. `scan`/`measure` already carry `sensor` on the same Protocol, so this is consistent with the existing shape. The ros2-runtime executor threads `args.camera` into the call; the `MockROSAdapter` records the selected camera in its audit log and media handle so hermetic fixtures can assert it flows through. Every adapter's `capture_media` accepts the new keyword; adapters that do not route by camera ignore it, exactly as they ignore other dispatch fields they cannot honor.

### 5. Conformance and examples

Three conformance fixtures under `conformance/fixtures/quadruped/` exercise the selector against the `spot_arm` manifest: a targeted capture on `hand_color` executes (positive), an undeclared camera is rejected, and a targeted capture on a fixed fisheye is rejected. A runnable worked example, `examples/spot-capture/`, shows the same three cases with a byte-asserted report, grounded in the #805 vocabulary.

## Alternatives considered

- **Name the field `source` or `sensor`.** `sensor` is what `scan`/`measure` use because they read cameras or sensors. `capture` only ever uses a camera, so `camera` is precise and resolves against exactly one manifest list. A generic `source` would blur that.
- **A new error code (`capability.camera_not_declared`).** Rejected to stay consistent with `scan`, which reuses `capability.missing_sensor`, and to avoid growing the public error-code surface.
- **Infer the camera from `target` geometry.** Out of altitude: URML declares and statically checks; it does not do frame math or camera selection by field of view. That belongs to the adapter.
- **Do nothing.** The any-eligible-camera behavior is a real hole on multi-camera robots and was already flagged as a caveat in-tree. A one-field addition closes it with no cost to single-camera robots.

## Prior art

`scan` (`ScanArgs.sensor`) and `measure` (`MeasureArgs.sensor`) already name a perception source and resolve it against the manifest. `ObjectDetector.sensor` (RFC-0615) binds an object class to a named camera. RFC-0682 declares cameras individually with a mount so they can be addressed by name. RFC-0586 set the precedent for adding an optional dispatch field to the frozen `ROSAdapter` Protocol (`grasp_type`).

## Implementation plan

Landed in this PR: the Layer-2 spec edit, the `CaptureArgs.camera` field, the validator check, the Protocol and adapter threading, validator unit tests, three conformance fixtures, and the `examples/spot-capture/` worked example with its guard test. The Spot Arm manifest caveat is updated to reflect the selector.

## Open questions

- Should a future revision let `camera` accept a list, for "any of these cameras"? Deferred; single-camera selection covers the motivating cases and keeps the check simple.
- Should `scan`/`measure` and `capture` converge on one source-selector name at v1.0? Noted for the v1.0 vocabulary review; not changed here to avoid a breaking rename.
