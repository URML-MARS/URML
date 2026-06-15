# Lowering a URML program to an AutoAPMS behavior tree

URML describes intent; a behavior tree executes it. This shows the bridge the
AutoAPMS maintainer proposed: validate a URML program, then lower it to a
behavior tree that the AutoAPMS execution layer can run.

It comes from the
[AutoAPMS engagement](https://github.com/AutoAPMS/auto-apms/issues/22), where
robin-mueller suggested an `auto_apms_urml` compatibility package implementing a
[build-handler](https://autoapms.github.io/auto-apms-guide/concept/common-resources#behavior-build-handlers)
plugin that validates and translates URML into AutoAPMS's behavior-tree
representation. This example is the validate-then-lower core of that idea.

```
URML program ──validate vs manifest──▶ admissible ──lower──▶ BehaviorTree.CPP XML ──▶ AutoAPMS execution
(sequence of primitives)                  │                  (Sequence + Action leaves)
                                          └─reject (undeclared location) ──▶ not lowered
```

URML's Layer-3 composition maps onto BT control nodes (a `sequence` becomes a
`<Sequence>`), and each primitive becomes an `<Action>` leaf the AutoAPMS
execution layer would implement (as an AutoAPMS skill or BT node). The key point
is order: the program is validated against the capability manifest first, so an
inadmissible intent never becomes an executable tree.

## What the example shows

[`lower_to_bt.py`](lower_to_bt.py) runs the programs in
[`programs.yaml`](programs.yaml) against [`delivery.manifest.yaml`](delivery.manifest.yaml):

| Program | Result |
|---|---|
| fetch_the_mug | LOWERED to a `<BehaviorTree>` (move_to / detect / grasp / move_to) |
| fetch_from_garage | REFUSED, `capability.missing_location`, not lowered |

The emitted tree is BehaviorTree.CPP v4 XML, the format AutoAPMS consumes. A real
`auto_apms_urml` build handler would wrap this: validate, lower, hand the tree to
the execution layer.

## Run it

```bash
python examples/behavior-tree/lower_to_bt.py
```

Validator-only, no AutoAPMS or ROS, deterministic. The committed
[`bt-report.txt`](bt-report.txt) is byte-asserted by
`reference/validator/tests/test_behavior_tree_example.py`.
