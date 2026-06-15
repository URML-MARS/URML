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

# Move #58 post bodies: the edge-AI / on-robot-inference wave

Five targets, all GitHub Issues. Post under idoco2003. No license-ask anywhere
(MIT/Apache stated; yolo_ros is GPL so cross-citation only). AI-assisted-
authoring disclosure up front. Titles carry no em-dash. embodied-agents + emos
are one post (on embodied-agents, referencing emos). Framing: URML consumes the
inference output (it does not run inference) and gates the action it informs;
for deployed/trained models, RFC-0383 (the artifact/policy declares its
envelope). Bodies are varied per target. This wave completes the third
candidate slate.

---

## RFC-0610: embodied-agents (and emos)

**Post to (Issue):** https://github.com/automatika-robotics/embodied-agents/issues/new
**Title:** URML (open robot intent language): a validated gate between a model's action and actuation (request for comment)

```
Hi Automatika maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an action becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. embodied-agents runs local LLM/VLM/VLA models on a robot and maps their output to ros2_control / MoveIt Servo actions, which is exactly the handoff URML is built to gate. This is a request for comment.

Nothing here asks the project to adopt, host, or maintain anything.

The seam: a local model is creative and occasionally wrong, and embodied-agents already turns its output into actuation. URML's candidate role is the typed gate in between -- the proposed action becomes a typed primitive, validated in five passes (argument typing, capability against a manifest, safety envelope, bindings, policy), and only an admissible action is dispatched. The model stays free to propose; the validator refuses what the robot cannot safely do. And because URML is a small, typed, runtime-neutral intent language, it is a natural thing for a VLA/VLM to emit as its action representation, which gets the capability and envelope check for free -- which is precisely the "model output to safe action" problem you are solving.

Two real questions: (1) is a typed, statically-validated gate between a model's proposed action and ros2_control / MoveIt Servo useful here, or does your action-mapping component already carry that safety reasoning? (2) Could a local VLA/VLM emit URML intent as its action representation?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0610-embodied-agents-outreach.md

Thanks for embodied-agents; running these models on-robot and mapping them to control is exactly where a validation gate between intent and actuation is most worth getting right.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0611: yolo_ros

**Post to (Issue):** https://github.com/mgonzs13/yolo_ros/issues/new
**Title:** URML (open robot intent language): consuming a yolo_ros detection as a fact an intent conditions on (request for comment)

```
Hi yolo_ros maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. URML does not do perception; it consumes the estimate. A detection from yolo_ros is exactly the kind of fact a URML intent conditions on and validates against before acting. This is a consume-the-estimate note (cross-citation only, since yolo_ros is GPL-3.0).

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The boundary: a typed URML intent ("pick up the detected mug", "approach the nearest person, keep this standoff") conditions on a detection and is validated against the robot's capabilities and a safety envelope before dispatch. yolo_ros stays the detector; URML stays out of perception entirely, and given the GPL-3.0 license this proposes no shared code, only a clean boundary. One nice alignment: the set of classes a yolo_ros node serves maps toward a URML manifest's object vocabulary, so an intent that references a class your stack does not provide can be caught early.

Two real questions: (1) is "yolo_ros produces the detection, URML consumes it as a fact an intent conditions on" a sensible boundary? (2) Do the served detection classes map cleanly toward a URML object vocabulary?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0611-yolo-ros-outreach.md

Thanks for yolo_ros; a well-maintained ROS 2 detection wrapper is exactly the kind of estimate source a validated intent layer wants to consume rather than reinvent.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0612: Kenning

**Post to (Issue):** https://github.com/antmicro/kenning/issues/new
**Title:** URML (open robot intent language): a validated action downstream of a Kenning-deployed model (request for comment)

```
Hi Kenning maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an action becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. Kenning deploys and optimizes edge-AI models with ROS 2 CV node support; URML is the layer above the model's output that turns a perception or policy result into a validated action. This is a request for comment.

Nothing here asks the project to adopt, host, or maintain anything.

Two seams. First: Kenning gets the model running efficiently on the device, and URML consumes its output (a detection, a policy decision) as a fact a typed intent conditions on, validated before dispatch; Kenning keeps the deployment and optimization, URML stays out of inference. Second, and more interesting: Kenning produces a deployed, optimized model artifact, and URML has a direction (LearnedPolicy) where such an artifact could carry the operating envelope it is valid within, so an intent that relies on it is checked against that envelope. For an edge deployment where the model is quantized or otherwise optimized, knowing the envelope it still holds for is genuinely useful.

Two real questions: (1) is a typed, validated action layer downstream of a Kenning-deployed model useful? (2) Could a deployed/optimized model artifact carry an operating envelope a URML intent is checked against?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0612-kenning-outreach.md

Thanks for Kenning; the deploy-and-optimize-for-edge step is exactly where the question of "what envelope does this optimized model still hold for" becomes concrete.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0613: hailo_tappas_ros2

**Post to (Issue):** https://github.com/kyrikakis/hailo_tappas_ros2/issues/new
**Title:** URML (open robot intent language): consuming NPU-accelerated detections as facts an intent conditions on (request for comment)

```
Hi,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. Your package runs on-edge inference on a Hailo NPU and publishes detections to ROS 2 topics, and URML is the layer that consumes those results as facts a validated intent conditions on. This is a consume-the-estimate note.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The boundary: the node publishes detections from the accelerator; a typed URML intent conditions on a detection and is validated against the robot's capabilities and a safety envelope before acting. The accelerated inference stays with your package; URML stays out of perception. If anything the clean separation matters more on an edge accelerator, where the inference is a fixed, optimized pipeline and the intent that uses it is the part that varies. The detection classes the node publishes also map toward a URML manifest's object vocabulary, so an intent referencing an unavailable class is caught early.

Two real questions: (1) is "the Hailo node produces the detection, URML consumes it as a fact an intent conditions on" a sensible boundary for an edge-accelerator perception pipeline? (2) Do the published detection classes map cleanly toward a URML object vocabulary?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0613-hailo-tappas-ros2-outreach.md

Thanks for the package; NPU-accelerated perception on a robot is exactly where a clean line between the estimate and the intent that uses it is worth drawing.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0614: OpenCV Zoo

**Post to (Issue):** https://github.com/opencv/opencv_zoo/issues/new
**Title:** URML (open robot intent language): consuming a zoo model's estimate on a robot (request for comment)

```
Hi OpenCV Zoo maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. opencv_zoo collects edge-deployable models for OpenCV DNN, and for the robotics subset of users, a zoo model's output is exactly the kind of perception fact a URML intent conditions on. This is a narrowly-scoped consume-the-estimate note about that robotics slice, not a claim on the whole project.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The boundary: for a robot running an opencv_zoo model on-device, the model's output (a detection, a pose, a segmentation) is a fact a typed URML intent conditions on, validated against the robot's capabilities and a safety envelope before dispatch. The zoo stays the model source and OpenCV DNN stays the runtime; URML stays out of perception. What a given zoo model outputs (its classes, keypoints) maps toward the perception side of a URML manifest, so an intent that needs an output the chosen model does not provide can be caught early.

Two real questions: (1) for robots using opencv_zoo models on-device, is "the zoo model produces the estimate, URML consumes it as a fact an intent conditions on" a sensible boundary? (2) Does a zoo model's output schema map cleanly toward the perception side of a URML manifest?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0614-opencv-zoo-outreach.md

Thanks for the zoo; edge-deployable models are exactly what a lot of robots run for perception, and a clean line to the intent that uses them seemed worth raising for that subset.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```
