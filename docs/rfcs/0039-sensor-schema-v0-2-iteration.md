---
rfc: 0039
title: Sensor schema v0.2 iteration: point-cloud sensors, beam count, channels, time sync, rate ceiling
author: Ido Yahalomi (greenvh@gmail.com)
state: Implemented
created: 2026-05-22
updated: 2026-06-02
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

# RFC-0039: Sensor schema v0.2 iteration

## Summary

Extend the Layer-1 `Sensor` schema with five additive, backward-compatible fields to close concrete expressibility gaps for 3D lidars and other multi-channel sensors:

1. `point_cloud` added to `measurement_type` (literal union).
2. `beam_count: int | None` (lidar-SKU-fixed property).
3. `channels: list[str] | None` (the data channels a sensor publishes: `range`, `intensity`, `reflectivity`, `near_ir`, ...).
4. `time_sync_methods: list[str] | None` (capability list of supported timestamping methods: `ptp`, `nmea`, `ieee_1588`, `ntp`, ...).
5. `rate_hz_max: float | None` (declared sample-rate ceiling, capability not selector).

All five are **optional**, **additive**, and **declarative**. Existing manifests validate unchanged. The change is purely a schema iteration; no validator logic, no executor, no Protocol method is added.

The RFC also formalizes URML's posture on the capability-vs-configuration line: **the manifest declares what the hardware can do; the substrate driver picks what this deployment will do.** Field selectors (e.g. Ouster's `LidarMode` or `UDPLidarProfile`, ROS QoS, fleet-manager dispatch) live below URML, not in URML.

## Motivation

This RFC is the spec-side response to the Ouster maintainer feedback on [RFC-0032](0032-ouster-integration.md). On 2026-05-22 Samahu (`@Samahu`) replied to our request-for-comment issue (`ouster-lidar/ouster-sdk#711`) with substantive technical answers on all five expressibility gaps we raised. The conversation is captured verbatim in the outreach log (`C:\Users\Ido\.claude\plans\outreach\log.md`).

His specific guidance, by gap:

- **Units.** "If you want to preserve the original millimeter integer representation then [...] you have to include units as part of the schema." URML's `Sensor.units` field already exists as a free-form string; this RFC does not change its optionality but documents the obligation more clearly in the Layer-1 normative text.
- **Beam count.** "Each beam configuration is a different hardware. You can't change the beam count of a given sensor." Confirms beam count is hardware-SKU-fixed and belongs in the manifest.
- **Channels and frame rate.** "These can be configured using the LidarMode and UDPLidarProfile, include rate_hz." Confirms the architectural distinction: URML declares the *capability set* (the channels and rate ceiling the hardware supports), Ouster's SDK selects the active mode at runtime.
- **Time synchronization.** "Ouster sensors have support for 3 timestamps mode, it really depends whether the URML is set up as a configuration schema that the node would have to read and configure the sensor based on that." This is the most valuable pushback: it forces URML to take a stance. The stance taken here is *URML is a capability + intent schema, not a configuration schema*; the manifest declares supported methods, the substrate driver picks one.

The gaps are real: the shipped `ouster_3d_lidar_cell.yaml` fixture declares the lidar with `measurement_type: distance` and `units: m`, which is the closest the v0.1 schema gets to "this is a multi-channel 3D point-cloud sensor with a fixed beam count." That mapping is honest about what the v0.1 schema covers and what it does not. This RFC closes the gap for v0.2 deployments without breaking v0.1 ones.

## Detailed design

### Schema changes

`reference/validator/src/urml_validator/schemas/manifest.py`, the `Sensor` class:

```python
class Sensor(BaseModel):
    """A non-camera sensor declared in the manifest's perception block."""

    model_config = ConfigDict(extra="forbid")

    name: Identifier
    measurement_type: Literal[
        "distance",
        "temperature",
        "weight",
        "pressure",
        "humidity",
        "depth",
        "wind_speed",
        "current",
        "voltage",
        "speech",
        "point_cloud",       # v0.2 addition; for 3D lidars and similar multi-channel sensors.
        "custom",
    ]
    range_min: float | None = None
    range_max: float | None = None
    units: str | None = None

    # v0.2 additions (RFC-0039). All optional and additive; existing manifests
    # validate unchanged.
    beam_count: int | None = Field(
        default=None,
        ge=1,
        description="Vertical beam count for lidar-class sensors. SKU-fixed.",
    )
    channels: list[str] | None = Field(
        default=None,
        description=(
            "Data channels the sensor publishes; convention is the lowercase "
            "channel name (e.g. range, intensity, reflectivity, near_ir). "
            "Free-form list; no closed vocabulary in v0.2."
        ),
    )
    time_sync_methods: list[str] | None = Field(
        default=None,
        description=(
            "Capability list of supported timestamping methods (e.g. ptp, "
            "nmea, ieee_1588, ntp). URML declares the supported set; the "
            "substrate driver selects which one a deployment uses."
        ),
    )
    rate_hz_max: float | None = Field(
        default=None,
        gt=0,
        description=(
            "Declared sample-rate ceiling in Hz. The substrate driver may "
            "configure the sensor below this ceiling (e.g. Ouster LidarMode "
            "+ UDPLidarProfile selects an active rate within hardware limits)."
        ),
    )
```

### Layer-1 HAL spec changes

`spec/layer-1-hal/v0.1.0.md`, the `perception.sensors` subsection: add a paragraph documenting the new fields, including the capability-vs-configuration line:

> URML's Sensor block declares **what the sensor can do**, not what a deployment configures it to do. Fields like `beam_count`, `channels`, `time_sync_methods`, and `rate_hz_max` are capability declarations; runtime substrates (Ouster's `LidarMode` + `UDPLidarProfile`, ROS 2 driver parameters, vendor-specific configuration files) pick the active mode at deployment time. URML does not reach into substrate configuration; the manifest is the contract above the driver.

### Validator changes

None. The five additions are pydantic schema fields with built-in constraints (`ge=1` on `beam_count`, `gt=0` on `rate_hz_max`); pydantic validates them automatically. No Pass-2/Pass-3 helpers, no error codes, no envelope interaction.

A v0.3+ tightening RFC may add cross-field rules (e.g. "`measurement_type: point_cloud` SHOULD declare `channels`"), but v0.2 keeps the schema purely declarative.

### Reference runtime changes

None. The new fields are capability declarations; the runtime adapters do not dispatch on them. A future substrate-specific runtime (e.g. a hypothetical `ouster-lidar-runtime`) would read these fields to drive the substrate, but the existing ROS 2 / PX4 / mobile / industrial-arm runtimes are untouched.

### Conformance suite changes

`reference/validator/tests/fixtures/manifests/ouster_3d_lidar_cell.yaml` is updated to demonstrate the new fields on the Ouster lidar entry. The change is purely additive on a single sensor; all 97 existing conformance fixtures remain green, and the existing Ouster fixture's policy outcome (ACCEPTED under default policy) is unchanged.

No new fixtures are added in this RFC. A follow-up may add an explicit v0.2-features positive fixture once a downstream consumer (RFC-0020 Autoware substrate, or an AV runtime) demands them.

### LLM bridge changes

None. The bridge's prompt contract for the manifest's `perception.sensors` block becomes one literal Union value richer (`point_cloud`) and gains four optional fields. The bridge emits manifests, not configurations, so the capability-vs-configuration distinction does not affect its prompt.

## Backward compatibility

Purely additive. All five additions are optional with default `None`. Existing manifests under `reference/validator/tests/fixtures/manifests/`, all 97 conformance fixtures, the `bootstrap.py` demo loop, and every shipped example continue to validate without modification.

`measurement_type` gains one Literal value; this is additive at the union level. Programs that bind a sensor reference statically (e.g. `wait_for(condition.sensor_threshold: ...)`) keep working: the new value `point_cloud` is just one more permitted member of the Literal.

## Drawbacks

1. **Schema surface growth.** Five new field positions on a single class. The cost is real: every future schema iteration costs documentation, validation, and prompt-contract surface. The cost is justified by the genuine expressibility gap a single maintainer surfaced in 30 minutes of review; the next manufacturer review may surface more.
2. **`channels` is free-form.** No closed vocabulary in v0.2. A v0.3+ tightening could promote the common lidar set (`range`, `intensity`, `reflectivity`, `near_ir`) to a Literal, but doing so prematurely closes the door on multi-modal sensors (radar Doppler bins, sonar pings, hyperspectral lines) that may need their own channel names.
3. **`time_sync_methods` is free-form.** Same reason as `channels`; PTP, NMEA, IEEE 1588, NTP are the obvious values, but the field stays a free-form list pending downstream consumer needs.
4. **`rate_hz_max` could be mistaken for a setpoint.** The name carries `_max` to signal capability ceiling; the description carries the cross-reference to Ouster's `LidarMode` / `UDPLidarProfile` to make the line explicit. A reader who skims may still misread; the Layer-1 spec text is the load-bearing clarification.
5. **No corresponding tightening for camera-class sensors.** Cameras also have channel-count and rate-ceiling capabilities (RGB-D camera vs. mono vs. event camera). This RFC scopes to the `Sensor` class because that is where the Ouster gap surfaced; a parallel `Camera` iteration is a follow-up if and when a camera-vendor outreach surfaces it.

## Alternatives considered

- **`point_cloud` as a separate `Sensor` subclass via pydantic discriminated unions.** Rejected. The `Sensor` model is small and tight; adding a discriminator field plus per-type subclasses doubles the schema surface and breaks every existing tool that consumes `Sensor` as a single shape. The flat additive-fields approach matches the home / drone / industrial profile-extension pattern (RFC-0011/0012/0013): add capabilities, do not refactor.
- **A new top-level `lidars` block alongside `sensors` and `cameras`.** Rejected. 3D lidars are sensors with extra capabilities, not a separate sensing category that needs its own per-instance plumbing. Splitting forces every downstream consumer (validator, runtime, bridge) to merge `sensors + lidars` everywhere. Keeping the additions on `Sensor` keeps the manifest's perception block scannable.
- **Promote `units` to required.** Rejected. Every shipped manifest already populates `units` (the existing string field), so making it required is non-breaking in practice, but the v0.2 stance is to document the obligation in the Layer-1 spec text without bumping `Optional` to required. A v0.3 may tighten if any field-emitting tool starts omitting it.
- **Promote `time_sync_methods` to a per-deployment selector (single value, not list).** Rejected. That is the configuration-schema posture Samahu's question opened the door to; the RFC's stance is the opposite. The deployment driver picks one; the manifest declares the supported set.
- **Bundle this RFC with RFC-0020 (Autoware AV substrate).** Considered: the Autoware draft is the most likely downstream consumer of richer lidar manifest fields. Rejected for scoping reasons: RFC-0020 is itself Draft and is the substrate / profile that builds *on* a richer Sensor schema; landing the schema iteration first lets 0020 cite stable spec text.

## Prior art

- The `Sensor` model itself (RFC-0002 §Detailed Design and the shipped `schemas/manifest.py`).
- The home (`speak`/`listen`, PR #25), drone (`take_off`/`land`/`return_to_home`, PR #30), and industrial (`pick_from`/`place_at`/`swap_tool`, RFC-0013) profile-extension precedents established the **additive-on-existing-schema** pattern this RFC follows.
- Ouster's [`LidarMode`](https://github.com/ouster-lidar/ouster-sdk) and [`UDPLidarProfile`](https://github.com/ouster-lidar/ouster-sdk) are the substrate-side configuration handles this RFC explicitly does not duplicate.
- ROS 2 [`sensor_msgs/PointCloud2`](https://docs.ros2.org/latest/api/sensor_msgs/msg/PointCloud2.html) carries the same channel-set distinction (`fields[]`) and is the obvious target representation for `point_cloud`-typed Sensor entries; this RFC does not pin URML to PointCloud2 because the manifest is substrate-neutral.
- Velodyne's beam-count + rate variability (VLP-16, VLP-32C, VLS-128, ...) is the prior-art demonstration that `beam_count` is hardware-SKU-fixed across the industry, not just Ouster-specific.

## Unresolved questions

- Whether `channels` should accept a closed Literal vocabulary in v0.3 once a second vendor (e.g. Velodyne, Hesai-civilian, Innoviz) confirms the set.
- Whether a parallel `Camera` iteration (RGB-D channels, frame-rate ceiling, time-sync) lands on the same timeline. Tracked for a future RFC if a camera-vendor outreach surfaces the gap.
- Whether RFC-0020 (Autoware AV substrate) consumes `channels` and `time_sync_methods` in its Pass-3 envelope checks (e.g. "an AV substrate program SHOULD declare a `time_sync_methods` set including PTP"). Tracked under RFC-0020's unresolved-questions list.
- The Samahu RFC-0020 review ("Will try to take a look") may add Ouster-specific notes to the AV substrate work; this RFC does not block on it.

## Implementation note

One PR set, mirroring RFC-0013's precedent. Commit order:

1. This RFC at `Draft` plus the RFC-index row.
2. Pydantic schema additions to `schemas/manifest.py`.
3. Layer-1 HAL spec text update.
4. `ouster_3d_lidar_cell.yaml` fixture: demonstrate the new fields on the Ouster lidar entry.
5. RFC-0032 amendment: a `## Maintainer feedback (2026-05-22)` section quoting Samahu's reply verbatim with a link to this RFC.
6. Outreach log entry (private notes, not in repo).
7. Verification: `urml conformance run` stays at 97/97 (or grows by any new positive fixtures); the full unit-test suite remains green; `make demo` / `make demo-run` exit 0.
8. Flip this RFC `Draft → Open → Accepted → Implemented` per RFC-0001 process after the founder-triggered comment window.

## Self-review (Phase 0)

- [x] The Summary names the five additions and the architectural stance (capability vs configuration), so a reader gets the whole shape from the first paragraph.
- [x] The Motivation is grounded in a concrete artifact: Samahu's reply on `ouster-lidar/ouster-sdk#711`. The five gaps are not invented; they were elicited.
- [x] The Detailed Design names every affected file and explicitly identifies what is unchanged (validator logic, runtime executors, LLM bridge prompt shape).
- [x] At least one alternative is genuinely considered (point_cloud subclass, separate lidars block, units promoted to required, time_sync as selector).
- [x] Drawbacks are honest: schema surface growth, free-form `channels` and `time_sync_methods`, the `rate_hz_max` naming risk.
- [x] Backward compatibility: purely additive, all five new fields optional, one Literal-union extension, zero breaking changes across the 97 conformance fixtures and every shipped manifest.
- [x] The substrate-neutrality acid test is trivially satisfied because no adapter is touched.
- [x] The implementation note explains commit order, not just file list.
- [x] The author re-read CLAUDE.md §What Claude Should Never Do: this RFC does not couple the manifest to a specific substrate (Ouster's LidarMode is referenced as the configuration boundary, not as a required URML field), does not embed a vendor in the schema, adds no cloud dependency, and stays substrate-neutral.
