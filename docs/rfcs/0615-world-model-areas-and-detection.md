---
rfc: 0615
title: World-model declarations — named areas (rooms) and object-detection responsibility
author: Ido Yahalomi (greenvh@gmail.com)
state: Implemented
created: 2026-06-15
updated: 2026-06-15
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

# RFC-0615: World-model declarations — named areas (rooms) and object-detection responsibility

## Summary

URML's manifest declares point locations and a flat object vocabulary, but it
cannot say what *rooms* a robot knows, nor *which sensor* detects which object
class. This RFC adds two optional, declaration-only fields: `declared_areas`
(named regions a primitive may target by name) and `perception.object_detection`
(which declared sensor is responsible for which declared object class). It is
*not* a primitive and *not* a world model. URML declares the finite set the robot
is configured for; it does not enumerate objects, model attributes, map regions,
or perform detection.

**State: Implemented** (2026-06-15). Ships the two schema fields, the
`_location_declared` extension (a primitive may target an area), three Pass-2
coherence checks, unit tests, and a worked example. Additive: a manifest without
these fields validates unchanged.

## Motivation

Surfaced by an engagement. On
[linorobot/linorobot2#223](https://github.com/linorobot/linorobot2/issues/223),
PaulBouchier relayed a Dallas Personal Robotics Group review. The recurring,
multi-reviewer note (HR): "there seems to be some missing parts, such as how to
define objects, rooms, etc. ... It does not define how objects will be detected."

URML already had two of the pieces: `object_vocabulary` plus
`capability.missing_object_class` reject `detect(object)` for an undeclared
class, and `declared_locations` plus `capability.missing_location` reject a
`move_to` to an unknown place. What was missing: rooms as first-class named
regions (a location is a point, not an area you can be *in*), and the link from
an object class to the sensor that detects it.

The same review carried a sharp warning (KV, Paul): if URML tries to model every
object and constraint, it replicates what a VLA already knows and becomes an
impossible expert system. That warning shapes the scope below.

## Detailed design

Two optional, additive fields.

```
declared_areas:                          # RFC-0615
  - name: kitchen
    frame: map
    polygon: [ {x: 2, y: 0}, {x: 5, y: 0}, {x: 5, y: 3}, {x: 2, y: 3} ]

perception:
  object_vocabulary: [mug, cup]
  object_detection:                      # RFC-0615
    - { object_class: mug, sensor: head_rgb }
```

`extra: forbid` as everywhere in Layer 1.

**Areas.** A named 2-D region (a polygon of at least three `{x, y}` vertices in a
declared frame). `_location_declared` is extended so a primitive that targets a
place (`move_to`, `pick_from`, ...) resolves the name against `declared_locations`
*and* `declared_areas`. So `move_to: { location: kitchen }` works when `kitchen`
is a room.

**Object-detection responsibility.** A list of `{ object_class, sensor }`
declaring which declared camera or sensor detects which declared object class. It
answers "how is this object found" at the capability level (which sensor is
responsible), not the algorithm level.

### Scope (the deliberate boundary)

URML declares the **finite set this robot is configured for**: the rooms it
knows, the object classes it can recognize, and the sensor responsible for each.
It does **not**: enumerate every object, model attributes (colour, size), map or
survey the regions, or perform detection. A model proposes "fetch the mug from
the kitchen"; URML checks the mug is a class this robot can detect and the
kitchen is a room it knows, then dispatches. That membership check is the whole
job, and it is what keeps URML from becoming the "know everything" layer the
linorobot reviewers warned against.

### Spec changes

- **Layer 1**: add `Area` + `declared_areas` (§2.2) and `ObjectDetector` +
  `perception.object_detection` (§2.6). No Layer 2/3/4 change; no new primitive.

### Validator changes

- `_location_declared` resolves area names too, so a primitive may target a room.
- Three Pass-2 coherence checks: an area's `frame` must be declared
  (`capability.area_frame_undeclared`); an `object_detection` entry's
  `object_class` must be in `object_vocabulary`
  (`capability.detector_unknown_object_class`); its `sensor` must be a declared
  camera or sensor (`capability.detector_unknown_sensor`).

### Reference runtime changes

None required.

## Alternatives considered

**Model objects richly (attributes, instances).** Rejected: that is the expert
system the reviewers warned about, and it replicates the VLA. URML declares the
vocabulary boundary, not a world database.

**Areas as point locations with a radius.** Rejected: rooms are not circles; a
polygon matches how floor plans and nav stacks describe rooms, and reuses the
existing `OddRegion` / `Point2` shape (RFC-0020).

**A new `enter_area` primitive.** Rejected: `move_to` already expresses "go
there"; an area is just another kind of place it can target. No new primitive.

## Implementation plan

1. `Area` + `declared_areas`, `ObjectDetector` + `perception.object_detection`
   (`schemas/manifest.py`). Done.
2. `_location_declared` extension + `_check_world_model` + three error codes
   (`validator.py`, `errors.py`). Done.
3. Unit tests (`test_world_model_rfc0615.py`). Done.
4. Worked example (`examples/world-model/`), byte-asserted. Done.
5. Layer-1 HAL §2.2 / §2.6 spec update. Done.

## Open questions

- A future rule could check that a primitive targeting a room is geometrically
  consistent with the room polygon (e.g. a declared dwell point lies inside it).
  Deferred; v0.1 checks declaration coherence only.
- Detection confidence / multiple sensors per class are out of scope until a
  consuming runtime needs them.
