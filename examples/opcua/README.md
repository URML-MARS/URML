<p align="center">
  <a href="https://urml.dev"><img src="https://urml.dev/favicon.svg" alt="URML" width="72" height="72"></a>
</p>

# URML intent to OPC UA methods

A worked example of URML lowering a validated program onto OPC UA method calls
on a robotics cell. It came out of the OPC UA engagements:
[open62541#8077](https://github.com/open62541/open62541/issues/8077) (jpfr) and
[UA-.NETStandard#3827](https://github.com/OPCFoundation/UA-.NETStandard/issues/3827)
(marcschier, OPC Foundation).

jpfr framed the modeling: OPC UA is object-orientation over the network. The cell
is an object, each URML operation is one method called on it, and the typed args
are the method inputs. The grain is **one URML operation to one OPC UA method.**

`intent_to_methods.py` shows that grain end to end, with no live server:

1. **Validate** a pick-and-place program against the cell's manifest. Nothing is
   called until the validator proves it admissible.
2. **Lower** each operation to exactly one OPC UA method node, resolved through
   the deployment config in `opcua_adapter.yaml`. Node ids are deployment detail;
   the URML program and manifest never name them.
3. **Execute** the operations through the real `OpcUaAdapter`
   (`reference/opcua-runtime`) against an embedded fake ObjectsNode, and print the
   call log: N operations issue N method calls, one each.

```
python examples/opcua/intent_to_methods.py
```

The committed `method-mapping-report.txt` is the recorded output. It is
deterministic and byte-asserted in CI
(`reference/validator/tests/test_opcua_example.py`), so the example cannot drift
from the tool.

## Files

- `opcua-cell.manifest.yaml` — the cell's URML capability manifest (US provenance).
- `opcua_adapter.yaml` — deployment node mapping (which method node each operation calls).
- `intent_to_methods.py` — the generator.
- `method-mapping-report.txt` — the recorded, byte-asserted output.

The adapter, a conformance fixture, and the recorded spec gaps live under
`reference/opcua-runtime/`.
