# Drone Examples

**Status:** Reserved. Populated when the drone-profile Layer-2 vocabulary is drafted (Phase 2 per [`MANIFESTO.md`](../../MANIFESTO.md) §Roadmap Snapshot).

The drone profile scenarios from the Manifesto (the "citizen inspector" roof inspection) are evocative prose, not authored URML — turning them into valid programs requires Layer-2 primitive signatures (`take_off`, `hover`, `scan`, `return_to_home`, `land`) that do not yet exist. Adding example files here before those signatures stabilize would mean either inventing speculative signatures or shipping examples that won't validate. Neither is useful.

When this directory is populated, expect at least:

- `roof-inspection.urml.yaml` + `roof-inspection.en.txt` — the manifesto's "citizen inspector" scenario.
- `area-scan.urml.yaml` + `area-scan.en.txt` — a serpentine area scan with declared overlap.

Both will validate against the canonical drone-profile capability manifest (in [`/spec/profiles/drone/`](../../spec/profiles/drone/) when drafted) and against the safety envelope defaults named there (altitude cap, geofence, weather thresholds, people-occupancy zones).

See the examples convention in [`/examples/README.md`](../README.md).
