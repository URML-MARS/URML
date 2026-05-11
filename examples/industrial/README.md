# Industrial Examples

**Status:** Reserved. Populated when the industrial-profile Layer-2 vocabulary is drafted (Phase 3 per [`MANIFESTO.md`](../../MANIFESTO.md) §Roadmap Snapshot).

The industrial profile scenarios from the Manifesto (the "line reconfiguration" — *"same as before, but pick red instead of blue, and slow down by twenty percent"*) require Layer-2 primitive signatures (`pick_from`, `place_at`, constrained `move_to`, profile-specific `grasp` force-ceiling defaults) that do not yet exist. Examples will land here once those signatures stabilize.

When this directory is populated, expect at least:

- `line-reconfiguration.urml.yaml` + `line-reconfiguration.en.txt` — the manifesto's pick-and-place re-color + slow-down scenario, exercising natural-language re-parameterization against a stored prior program.
- `simple-pick-and-place.urml.yaml` + `simple-pick-and-place.en.txt` — a minimum-viable industrial example for first-time integrators.

Both will validate against an industrial-profile capability manifest (in [`/spec/profiles/industrial/`](../../spec/profiles/industrial/) when drafted) and against the cell-perimeter, safety-door-interlock, and force-ceiling safety envelope defaults.

See the examples convention in [`/examples/README.md`](../README.md).
