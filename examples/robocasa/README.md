# URML as an eval lens over RoboCasa instructions

On [robocasa/robocasa#200](https://github.com/robocasa/robocasa/issues/200) the
maintainer made a sharp point: RoboCasa learns policies end to end in sim and
defines tasks by the environment plus a success checker, so there is no actuation
gate to refuse a request. A validated intent layer is more relevant to a
deployment stack. **But** an explicit capability + safety envelope is a useful
**eval lens**, for flagging out-of-distribution or out-of-capability instructions.

That is what this example shows, with no new URML machinery.

- [`robocasa-kitchen.manifest.yaml`](robocasa-kitchen.manifest.yaml) is built
  from the spec the maintainer gave: a Franka Panda 7-DOF arm on an Omron mobile
  base, a parallel-jaw gripper, kitchen-scene reachability, and the graspable
  object vocabulary.
- [`eval_lens.py`](eval_lens.py) lowers each benchmark instruction to URML intent
  and validates it against the manifest. An in-capability instruction passes; one
  that names an object or place outside the scene (**out-of-distribution**), or
  exceeds a declared capability like gripper force or an absent flight modality
  (**out-of-capability**), is flagged before any policy runs.

```
  [PASS]  Pick up the mug from the counter and put it in the sink
  [PASS]  Drive to the stove
  [FLAG]  Grasp the anvil on the counter           [out-of-distribution]
  [FLAG]  Go to the rooftop                         [out-of-distribution]
  [FLAG]  Pick up the mug, squeezing it with 200 N  [out-of-capability]
  [FLAG]  Fly up to the top shelf                   [out-of-capability]
```

Nothing is actuated; the lens is static and offline. Run it:

```sh
python examples/robocasa/eval_lens.py
```

The output is deterministic and byte-asserted in
[`eval-report.txt`](eval-report.txt) by
`reference/validator/tests/test_robocasa_example.py`.
