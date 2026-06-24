# URML on Isaac Sim: a USD-derived manifest, validated, then driven (RFC-0631)

The worked example NVIDIA Isaac asked for on
[isaac-sim/IsaacSim#649](https://github.com/isaac-sim/IsaacSim/issues/649): not a
conceptual mapping, but the real flow that earns a conformance listing.

The three concerns, kept separate exactly as the reviewer described them:

1. **USD as structural evidence.** [`isaac-arm.manifest.yaml`](isaac-arm.manifest.yaml)
   was derived from a USD asset. Every capability claim carries an RFC-0631
   `evidence` tag tracing it to the USD prim it came from
   (`/World/arm/base/ArticulationRoot`, `/World/arm/joints/JointStateSensor`), so
   a reviewer can tell a derived contract from a hand-typed one.
2. **The capability manifest as the validation contract.** The program is
   validated against the manifest before anything actuates, and again under an
   opt-in evidence policy that requires `derived` evidence for the mobility and
   sensor claims. Because the manifest is USD-derived, it clears that
   listing-grade gate.
3. **A backend-neutral adapter for dispatch.** The validated program is executed
   through the real `IsaacAdapter`, hermetically: a fake `isaacsim` module is
   injected (no wheel, no GPU, no engine), the same technique
   [`examples/opcua/`](../opcua/) uses for `asyncua`. Each `move_to` lowers to one
   control-vector write on the model plus a physics step. No ROS in the path.

Run it:

```sh
python examples/isaac/usd_to_motion.py
```

The output is deterministic and byte-asserted in
[`motion-report.txt`](motion-report.txt) by
`reference/validator/tests/test_isaac_example.py`.

Per the reviewer, URML is **not** listed as supported on a conceptual mapping.
This example is the honest path: a USD-derived manifest with traceable evidence,
a working Isaac Sim adapter run, and validate-before-actuate over both. The
adapter surface is backend-neutral by construction (Action Graph / OmniGraph is
not where URML integrates); cuMotion / PINK is the controller-interface seam the
consume-trajectory primitives target.
