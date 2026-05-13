# Home Profile

**Status:** Draft (v0.1)
**Targets:** URML v0.1
**Created:** 2026-05-13

The first URML profile to ship: indoor service robots operating in spaces shared with people, driven by natural language from non-expert users. Constrains and extends the [twelve core primitives](../../../docs/rfcs/0002-initial-primitive-vocabulary.md) for the household setting, defines a default safety envelope appropriate to unsupervised human-shared space, and binds the profile's compliance posture to the [bundled US-federal policy](../../../docs/rfcs/0004-compliance-policy.md).

## Application domain

Indoor service robots operating in spaces shared with people: kitchens, living rooms, offices, small clinics. The defining shape of the home profile is *natural-language input from a non-expert end user, executed by a robot that has to navigate human-occupied space gracefully*.

## In scope

- **Fetch-and-carry tasks.** "Bring me the red mug from the kitchen." The canonical home example (see [`/examples/home/red-mug.urml.yaml`](../../../examples/home/red-mug.urml.yaml) and the companion manifest [`/examples/home/red-mug.manifest.yaml`](../../../examples/home/red-mug.manifest.yaml)).
- **Navigation in human-occupied space.** The runtime is expected to honor proxemics, give right-of-way to people, and slow near unexpected motion. URML expresses the *intent*; the runtime's Layer-0 implementation handles the social-navigation specifics.
- **Charging-station docking.** The core `dock` primitive applied to the declared `charging_dock` station.
- **Voice- or text-driven natural-language flows.** The home profile is one of the first profiles where Layer-4 (the LLM bridge) is exercised end-to-end with a non-expert in the loop. The profile adds `speak` and `listen` to make conversational hand-offs first-class.
- **Multi-step household errands.** Composable through Layer-3 `sequence`, `branch`, and error handling.

## Out of scope

- **Outdoor navigation.** Home robots that move between indoor and outdoor environments are common; their outdoor behavior is covered by other profiles (drone for aerial, vehicle for ground), not by the home profile.
- **Manipulation requiring industrial-grade safety** (force ceilings beyond gentle-grasp categories). That is the industrial profile.
- **Continuous monitoring or surveillance.** Out of scope; URML's design principles prohibit collecting user data without explicit opt-in.

## Profile-required Layer-1 manifest fields

A home-profile-conformant capability manifest **must** declare:

- **`mobility`** with `drive_type` in (`differential`, `omnidirectional`, `ackermann`, `tracked`, `manipulator_base`). A stationary home robot omits mobility but cannot use the canonical fetch-and-carry programs.
- **`manipulation.grippers`** — at least one gripper. The default `kind` is `servo_electric`; pneumatic grippers are permitted but the profile's force ceilings are tightened (see *Layer-2 primitives this profile constrains*).
- **`perception.cameras`** — at least one camera. Speech is profile-extended (see `listen`); a camera-only manifest is permitted but `listen(condition.input: speech)` becomes unusable.
- **`perception.object_vocabulary`** — the closed set of object classes the manifest commits to. The LLM bridge inlines this verbatim; objects outside the vocabulary are rejected at `detect` validation.
- **`declared_locations`** — at minimum `user` (or whatever named recipient the deployment uses) and a `charging_dock`. Fetch-and-carry programs target the user location for `release(mode: hand_to_user)`.
- **`docking_stations`** with a station declaring `services: [park, charge]` for the charging dock.

A home-profile manifest **should** declare:

- **`provenance:`** per [RFC-0004](../../../docs/rfcs/0004-compliance-policy.md). Home deployments inside the US can claim NDAA/FY26 compliance only if every critical component's provenance is declared and validated against the bundled default policy. Manifests without provenance still validate; they just do not gain the compliance posture.

A home-profile manifest **must not** declare:

- **`mobility.service_ceiling`** with a non-trivial value. Aerial flight is the drone profile, not home.

## Default safety envelope

A home robot operates in **shared, unsupervised space with non-expert end users**. The default safety envelope tightens the manifest's declared limits:

```yaml
# Default home-profile envelope shape. Deployments tighten or extend; they
# do not weaken. The validator rejects envelopes that relax these defaults
# without an explicit override flag (deferred to a follow-up RFC).
envelope_version: "0.1"
deployment_id: <free-form>
description: <free-form>

# Numeric caps. Strictest-wins against the manifest's declared maxima.
max_velocity: 0.5                  # m/s; human-walking-pace default
max_grip_force_n: 3.0              # N; the gentle-grasp ceiling

# Spatial constraints.
people_occupancy_zones: []         # list of named zones or polygons.
                                   # default-empty means no restricted zones;
                                   # deployments add bathrooms / children's rooms here.
geofences: []                      # optional polygons; deployment-supplied if the
                                   # robot's mapped area is bounded.

# Behavioural defaults.
link_loss_policy: halt_and_report  # halt motion and `report status: failure` to caller.
emergency_stop_event: emergency_stop  # must match a declared event on the manifest.
```

A reference envelope ships at [`reference/validator/tests/fixtures/envelopes/home_default.yaml`](../../../reference/validator/tests/fixtures/envelopes/home_default.yaml). Deployments are expected to start from it and tighten.

### Mandatory invariants

These are non-negotiable for the home profile and the validator enforces them:

- **No motion in a declared people-occupancy zone** without an explicit manifest override.
- **`grasp.force` is at or below `max_grip_force_n`** (default 3.0 N) — a *gentle*-class ceiling chosen so inadvertent contact with a person yields.
- **A program must declare `emergency_stop` handling** through a top-level `on_error` or an explicit `wait_for(condition.event: emergency_stop)` — programs lacking either are rejected. (v0.1: enforcement of this invariant is best-effort; a follow-up RFC tightens.)

## Layer-2 primitives this profile adds

[RFC-0002 §Detailed Design](../../../docs/rfcs/0002-initial-primitive-vocabulary.md) authorizes per-profile primitive additions. The home profile adds two: `speak` and `listen`. Both pass the substrate-neutrality acid test sketched per primitive below.

### `speak`

Emit a spoken utterance to the user via the robot's declared speech-output channel. Conversational acknowledgement and confirmation.

**Signature:**

```yaml
- speak:
    utterance: <string>          # required; what to say
    locale: <BCP-47>             # optional; defaults to the manifest's declared primary_locale
    style: notice | warning | conversational  # optional; default: conversational
    interrupt: true | false      # optional; default: false. If true, the runtime
                                 # cancels any in-progress utterance before speaking.
```

**Semantics.** The robot pronounces `utterance` through its declared speech-output channel. `style` is advisory to the runtime's voice rendering (e.g., notice = neutral; warning = louder/firmer); the substrate decides. `interrupt: true` is for safety messages; the default `false` queues behind any in-progress utterance to keep conversational flow predictable.

**Capability requirements (Layer 1):** `manifest.outputs.named_endpoints` declares `speech` (the canonical name for a speech-output channel). A manifest without `speech` declared rejects programs using `speak`.

**Safety-envelope checks:** none beyond capability declaration. (Future: deployment-declared do-not-disturb hours that block non-`interrupt: true` utterances. Deferred.)

**Variable bindings:** `speak` does not produce a result.

**ROS-2 implementation sketch:** publish on a configured topic with a `std_msgs/String` or vendor-specific TTS message; for production, route through a TTS node (e.g., `audio_common`).

**Non-ROS implementation sketch:** OPC UA — `Speech.Utter()` method on the audio service. Vendor SDK — vendor TTS API. PX4 — not applicable; drones operate outside human conversational range.

### `listen`

Block until the user provides spoken input (or until a declared timeout). Conversational hand-off and ambiguity resolution.

**Signature:**

```yaml
- listen:
    prompt: <string>             # optional; an utterance to speak before listening
    locale: <BCP-47>             # optional; defaults to manifest's primary_locale
    timeout: <duration>          # optional; default per deployment, capped by envelope
    expected: free_form | confirmation | choice  # optional; default: free_form
    choices: [<string>, ...]     # required iff expected == "choice"
    store_as: <name>             # required if the result is referenced later
```

**Semantics.** The robot listens on its declared speech-input channel. If `prompt` is set, the robot first speaks it (equivalent to `speak(prompt) + listen()` but the validator treats the pair atomically). The bound result is `{transcription: str, confidence: float, choice_index: int | null}`. For `expected: choice`, the runtime maps the transcription to the closest `choices` entry; for `confirmation`, the runtime extracts a yes/no judgment.

**Capability requirements (Layer 1):** `manifest.perception.sensors` declares a sensor with `measurement_type: speech` (the canonical name; a microphone declared as a perception sensor is the most common shape). A manifest without speech-input declared rejects programs using `listen`.

**Safety-envelope checks:** the `timeout` does not exceed the envelope's `max_listen_duration` (deferred field; v0.1 enforces only the timeout being declared finite).

**Variable bindings:** the `store_as` name resolves to `{transcription, confidence, choice_index}` (`choice_index` is `null` for `free_form` and `confirmation`; an integer index into `choices` for `expected: choice`).

**ROS-2 implementation sketch:** subscription to a configured speech-recognition topic (e.g., a ROS 2 STT node publishing `audio_common_msgs/AudioData` then transcribed to `std_msgs/String`); the URML adapter buffers, applies the `expected` mode, and returns.

**Non-ROS implementation sketch:** OPC UA — `Speech.Listen(timeout)` method on the audio service. Vendor SDK — vendor STT API.

## Layer-2 primitives this profile constrains

The home profile narrows several core primitives' default behavior:

### `grasp`

- **Force ceiling:** `grasp.force` defaults to `gentle` (1.5 N nominal) and rejects values above the envelope's `max_grip_force_n` (default 3.0 N). A program that declares `grasp(force: 25)` against a home-profile envelope fails Pass 3 (envelope) with `envelope.force_exceeded`.
- **Accepted classes:** the home profile's typical gripper declares `accepted_classes: [mug, cup, small_object]`. Programs that `grasp(target: $obj)` where `$obj.class` is outside the gripper's declared list fail Pass 2 (capability) with `capability.missing_gripper`.

### `release`

- **`mode: hand_to_user`** is the home-profile preferred release semantics. The runtime presents the object at the declared `user` location and waits for the user to take it before opening the gripper. Timeout for the wait is profile-declared (default 30s).
- **`mode: drop`** is permitted but the height ceiling is 5 cm — high enough to release, low enough to avoid breaking the dropped item.

### `move_to`

- **Location resolution:** named locations resolve against the manifest's `declared_locations`. The validator rejects unnamed coordinates within the declared mapped area unless the program specifies a `frame` matching a declared frame.
- **Velocity:** the strictest-wins rule applies normally; the home envelope's 0.5 m/s default is typically tighter than a robot's declared maximum.

### `wait`

- **In-program `wait` is permitted at any position.** Unlike the drone profile, the home profile does not prohibit `wait` mid-program; robots in human-shared space sometimes need to passively wait without active station-keeping.

### `report`

- **`to: user`** routes through the speech-output channel if declared; otherwise through the manifest's default output. The LLM bridge translates `report.facts` to natural-language utterances when the destination is `user`.

## Layer-4 (LLM bridge) integration

The home profile is the first profile where the LLM bridge is exercised in production. Specific expectations:

- The bridge's [`home_few_shots`](../../../reference/llm-bridge/src/urml_llm_bridge/few_shot.py) ship with the bridge package; they are loaded automatically when `profiles=("home",)` is passed to `Bridge`.
- The bridge inlines `manifest.perception.object_vocabulary` into the system prompt verbatim. The LLM is constrained to emit `detect(object: ...)` only with declared classes; out-of-vocabulary detections produce `capability.missing_object_class` and trigger the revision loop.
- Programs that name `user` as a location are expected to behave correctly — the home profile reserves `user` as the conventional recipient.

## Compliance policy alignment

Home deployments inside the United States routinely fall under federal procurement scope when sold to municipalities, school districts, or military family programs. The bundled default policy (RFC-0004) applies to home-profile manifests the same way it applies to industrial or drone: provenance is opt-in at the manifest level; once declared, the default policy enforces NDAA-style restrictions.

For home robots specifically, the policy considerations the profile flags:

- **Camera modules** are most commonly the regulatorily-sensitive critical component on home robots (consumer drone vendors and consumer camera vendors overlap with FCC-Covered-List entries). Manifests declaring camera modules with `vendor: dji` or similar will reject under the default policy with `policy.vendor_denied`.
- **Microphones** are typically non-critical for procurement rules but may be regulated by other frames (privacy, data-export). v0.1 does not encode privacy rules; future RFC.
- **Drive controllers** are typically critical; substitutes with declared US/JP/KR origin are widely available.

Deployments outside the US should override the default with their own jurisdiction-appropriate policy. The reference home envelope at [`reference/validator/tests/fixtures/envelopes/home_default.yaml`](../../../reference/validator/tests/fixtures/envelopes/home_default.yaml) is jurisdictionally neutral; the regulatory frame attaches via the policy file, not the envelope.

## Conformance points

The conformance suite at [`/conformance/fixtures/home/`](../../../conformance/fixtures/home/) exercises this profile:

| Fixture | What it tests |
|---|---|
| `01_red_mug_positive.yaml` | Canonical end-to-end fetch-and-carry; happy path. |
| `02_red_mug_nav_failure.yaml` | Runtime nav failure surfaces as program failure with `path_blocked`. |
| `03_missing_location_rejected.yaml` | Validator rejects `move_to` to an undeclared location (Pass 2). |
| `04_branch_on_color.yaml` | Layer-3 `branch` composition with home-profile primitives. |
| `05_retry_until_confidence.yaml` | Layer-3 `retry` composition. |
| `06_parallel_first_to_succeed.yaml` | Layer-3 `parallel` composition. |
| `07_policy_country_denied.yaml` | Bundled default policy rejects a CN-origin critical component (Pass 5). |
| `08_policy_none_accepts_otherwise_denied.yaml` | `--no-policy` escape hatch accepts the same manifest. |
| `09_policy_vendor_denylist.yaml` | Bundled default policy rejects an FCC-Covered-List vendor (Pass 5). |

Additional fixtures this spec will require when the profile reaches **Implemented** state (deferred to follow-up PRs):

- `10_speak_listen_conversation.yaml` — a multi-turn conversation using the new `speak`/`listen` primitives.
- `11_emergency_stop_handling.yaml` — a program that declares `emergency_stop` handling correctly is accepted; a program that omits it is rejected (when the invariant tightens).
- `12_force_ceiling_envelope.yaml` — `grasp(force: 25)` rejected against the home envelope.

## Related documents

- [`/docs/architecture.md`](../../../docs/architecture.md) §Profiles.
- [`/spec/layer-1-hal/`](../../layer-1-hal/) — capability manifest reference, including the provenance block.
- [`/spec/layer-2-primitives/`](../../layer-2-primitives/) — the core twelve.
- [`/docs/rfcs/0002-initial-primitive-vocabulary.md`](../../../docs/rfcs/0002-initial-primitive-vocabulary.md) — primitive vocabulary, including the §Profile-extensibility clause authorizing `speak`/`listen`.
- [`/docs/rfcs/0004-compliance-policy.md`](../../../docs/rfcs/0004-compliance-policy.md) — compliance policy mechanism.
- [`/examples/home/`](../../../examples/home/) — the runnable example pair for this profile.
- [`/conformance/fixtures/home/`](../../../conformance/fixtures/home/) — conformance fixtures.
- [`MANIFESTO.md`](../../../MANIFESTO.md) §Motivating Scenarios — *Home: the multilingual grandparent*.
