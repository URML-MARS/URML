# Declaring a robot's world model: rooms and objects

A robot's manifest can now say what rooms it knows and what objects it can
recognize, so an intent that names a room or object the robot was never declared
to know is refused before it acts. This is RFC-0615, and it came from the
linorobot2 / Dallas Personal Robotics Group review, where the recurring note was
"how to define objects, rooms... it doesn't define how objects will be detected."

The important constraint: this is declaration, not a world model. URML declares
the finite set this specific robot is configured for. It does not enumerate every
object, model attributes like colour or size, map the rooms, or perform
detection. A model proposes "fetch the mug from the kitchen"; URML only checks
that the mug is a class this robot can detect and the kitchen is a room it knows.
That is the whole job, and it is what keeps it from turning into the impossible
"know everything" layer the reviewers warned about.

## What's declared

In [`home.manifest.yaml`](home.manifest.yaml):

- `declared_areas`: named rooms or zones, each a polygon in a declared frame. A
  primitive can target an area by name (`move_to: { location: kitchen }`) just as
  it targets a point location. An area's frame must be a declared frame.
- `perception.object_detection`: which declared sensor detects which declared
  object class. The class must be in `object_vocabulary`, and the sensor must be
  a declared camera or sensor. It declares responsibility, not the algorithm.

The membership checks that make this useful already existed (`object_vocabulary`
plus `capability.missing_object_class`, `declared_locations` plus
`capability.missing_location`); RFC-0615 adds rooms and the detector link.

## What the example shows

[`check_world_model.py`](check_world_model.py) validates the intents in
[`intents.yaml`](intents.yaml):

| Intent | Result |
|---|---|
| fetch_mug_from_kitchen | ACCEPT (kitchen is a room, mug is detectable) |
| go_to_living_room | ACCEPT (living_room is a room) |
| go_to_garage | REFUSE, `capability.missing_location` (no such room) |
| fetch_a_banana | REFUSE, `capability.missing_object_class` (not in vocabulary) |

## Run it

```bash
python examples/world-model/check_world_model.py
```

Validator-only, deterministic. The committed
[`world-model-report.txt`](world-model-report.txt) is byte-asserted by
`reference/validator/tests/test_world_model_example.py`.
