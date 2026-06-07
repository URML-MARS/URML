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

# Move #39 post bodies: the robot-description / interop-formats wave

Eight targets. Post under idoco2003 via the channel noted per row. No license-ask
(KDL is LGPL-2.1 — state, no change ask). AI-assisted-authoring disclosure up
front. At post time, query the one Discussion repo's real category id (Move #30
procedure). OSRF-adjacent repos (sdformat, urdfdom): courteous, format-design tone.

---

## RFC-0455: robot_descriptions.py

**Post to (Discussion):** https://github.com/robot-descriptions/robot_descriptions.py/discussions/new?category=ideas
**Title:** URML (open robot intent language): how should a capability + safety manifest relate to a robot description? — request for comment

```
Hi robot_descriptions.py community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. The manifest is a separate-but-adjacent artifact to a robot description: it declares what a robot is allowed and able to do (drive type, reach/DOF, payload, gripper, workspace bounds, safety envelope). Since your library already normalizes access to 185+ descriptions across URDF / MJCF / USD, you are the ideal people to ask how such a manifest should relate to — and where possible derive from — a robot description.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment, and genuinely a design question.

A robot description carries kinematics, joint limits, and geometry; a URML manifest carries capabilities and a safety envelope. Some manifest fields (reach, DOF, joint/speed limits) could be derived or cross-checked from the description; others (payload limits, graspable classes, no-go regions) are genuinely separate. URML's validator could consume a robot_descriptions.py entry to bootstrap or sanity-check a manifest, so the two do not drift. The clean split: the description says what the robot is; the manifest says what it is allowed and able to do.

Two real questions: (1) Which capability-manifest fields can be derived honestly from a URDF/MJCF/USD description, and which are genuinely separate? (2) Would a thin adapter from a robot_descriptions.py entry to a URML manifest skeleton be useful — and where should the line sit between robot description and robot capability + safety declaration?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0455-robot-descriptions-outreach.md

Thanks for robot_descriptions.py; a cross-format description aggregator is exactly the right vantage point for this question.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0456: SDFormat

**Post to (Issue):** https://github.com/gazebosim/sdformat/issues/new
**Title:** URML (open robot intent language): where should the boundary sit between SDFormat and a capability + safety manifest? — request for comment

```
Hi SDFormat maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. SDFormat describes a robot's structure; URML's manifest describes what a robot is allowed and able to do, plus a safety envelope. These are adjacent, and the boundary between them is a genuine design question I would value your view on.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

An SDFormat file carries links, joints, limits, sensors, and physics; a URML manifest carries capabilities (drive type, reach, payload, gripper, graspable classes) and a safety envelope. Some manifest fields could be derived or cross-checked from SDFormat; others (payload limits, graspable classes, the safety envelope) sit outside its scope. URML's validator could consume an SDFormat model to bootstrap or sanity-check a manifest rather than duplicating it. The split: SDFormat says what the robot and world are; the manifest says what the robot is allowed and able to do.

Two real questions: (1) Which URML capability-manifest fields map cleanly onto SDFormat elements, and which are genuinely outside SDFormat's scope? (2) Where should the boundary sit between robot description (SDFormat) and robot capability + safety declaration?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0456-sdformat-outreach.md

Thanks for SDFormat; a long-standing open robot-description format is the right place to think about where description ends and capability declaration begins.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0457: URDF tooling (urdfdom)

**Post to (Issue):** https://github.com/ros/urdfdom/issues/new
**Title:** URML (open robot intent language): how should a capability + safety manifest relate to URDF? — request for comment

```
Hi URDF tooling maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. URDF describes a robot's structure; URML's manifest describes what a robot is allowed and able to do, plus a safety envelope. I'm anchoring this on urdfdom and referencing the sibling tooling (urdfdom_headers, xacro, robot_state_publisher) rather than posting to each.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment, and a design question.

A URDF (parsed by urdfdom, generated via xacro) carries links, joints, limits, and geometry; a URML manifest carries capabilities and a safety envelope. Some manifest fields (reach, DOF, joint/speed limits) could be derived or cross-checked from URDF; others (payload limits, graspable classes, the safety envelope) are genuinely separate. URML's validator could consume a urdfdom-parsed model to bootstrap or sanity-check a manifest, keeping description and capability declaration from drifting. The split: URDF says what the robot is; the manifest says what it is allowed and able to do.

Two real questions: (1) Which URML capability-manifest fields can be derived honestly from URDF, and which are genuinely separate? (2) Would a thin adapter from a urdfdom-parsed model to a URML manifest skeleton be useful — and where should the boundary sit between URDF and capability + safety declaration?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0457-urdfdom-outreach.md

Thanks for the URDF tooling; the most widely-used robot-description format is the natural place for this question.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0458: iDynTree

**Post to (Issue):** https://github.com/gbionics/idyntree/issues/new
**Title:** URML (open robot intent language): which capability-manifest fields can be derived from a dynamics model? — request for comment

```
Hi iDynTree maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. The manifest declares capabilities (reach, DOF, payload, gripper, workspace bounds) and a safety envelope. Since iDynTree already computes kinematics and dynamics for floating-base robots from a URDF/SDF model, you are well placed to advise which of those manifest fields can be derived from a model and which must be declared separately.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

iDynTree computes kinematics/dynamics from a description; a URML manifest declares capabilities and a safety envelope. Some manifest fields could be derived from iDynTree's computed model (reachable workspace, joint/velocity limits); others (payload limits, graspable classes, the safety envelope) are separate. URML's validator could consume iDynTree-computed properties to bootstrap or sanity-check a manifest. The split: iDynTree says what the robot's physics are; the manifest says what it is allowed and able to do. This is especially relevant for floating-base and humanoid robots, where URML's whole-body work already lives.

Two real questions: (1) Which URML capability-manifest fields (reachable workspace, joint/velocity limits, payload) can be derived honestly from an iDynTree model, and which are genuinely separate? (2) Would a thin iDynTree → URML manifest-skeleton adapter be useful for floating-base / humanoid robots?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0458-idyntree-outreach.md

Thanks for iDynTree; a floating-base kinematics/dynamics library is exactly the right vantage point for the derive-vs-declare question.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0459: urdf-loaders (NASA JPL)

**Post to (Issue):** https://github.com/gkjohnson/urdf-loaders/issues/new
**Title:** URML (open robot intent language): visualizing a robot's declared capabilities + safety envelope alongside its URDF — request for comment

```
Hi urdf-loaders maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. Since urdf-loaders is the dominant way URDF robots are visualized on the web (THREE.js / Unity), it is a natural place to discuss showing a robot's declared capabilities and safety envelope alongside its visualized structure.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

urdf-loaders renders a URDF; a URML manifest declares capabilities and a safety envelope for that same robot. A viewer could surface the manifest's declared workspace, reach, and no-go regions over the rendered model. Some manifest fields (reach, DOF, joint limits) can be read directly from the loaded URDF; others (payload, graspable classes, the safety envelope) are declared separately. The split: the loaded URDF says what the robot looks like and is; the manifest says what it is allowed and able to do.

Two real questions: (1) Is visualizing a robot's declared capabilities / safety envelope alongside the URDF interesting for the web-robotics use case? (2) Which manifest fields can be read directly from the loaded URDF, and where should the boundary sit between visualized description and capability + safety declaration?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0459-urdf-loaders-outreach.md

Thanks for urdf-loaders; web URDF visualization is a great surface for making a robot's allowed envelope visible.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0460: yourdfpy

**Post to (Issue):** https://github.com/clemense/yourdfpy/issues/new
**Title:** URML (open robot intent language): a yourdfpy → capability-manifest adapter? — request for comment

```
Hi yourdfpy maintainer,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. URML's reference tooling is Python, so a clean permissive Python URDF parser like yourdfpy is the most natural building block for an adapter that derives or cross-checks URML capability-manifest fields against a URDF.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

yourdfpy parses a URDF in Python; a URML manifest declares capabilities and a safety envelope. A small adapter could read reach/DOF/joint limits from a yourdfpy model into a URML manifest skeleton, leaving payload, graspable classes, and the safety envelope to explicit declaration. URML's (Python) validator could use yourdfpy to keep a manifest consistent with the robot's URDF. The split: yourdfpy gives the URDF; the manifest gives capability + safety.

Two real questions: (1) Would a thin yourdfpy → URML manifest-skeleton adapter be useful, and what URDF fields map cleanly? (2) Which capability-manifest fields are genuinely outside URDF (payload, graspable classes, safety envelope), and where should the boundary sit?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0460-yourdfpy-outreach.md

Thanks for yourdfpy; a clean Python URDF parser is a great foundation for this kind of adapter.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0461: Orocos KDL

**Post to (Issue):** https://github.com/orocos/orocos_kinematics_dynamics/issues/new
**Title:** URML (open robot intent language): cross-checking a capability manifest against a KDL chain — request for comment

```
Hi Orocos KDL maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. Since KDL builds kinematic chains from URDF and computes FK/IK and joint limits, you are well placed to advise which URML capability-manifest fields (reach, joint limits, reachable workspace) are computable from a chain and which must be declared. (For clarity: KDL is LGPL-2.1; URML would interoperate above it and vendor none of its code — this is purely a design discussion, no license change requested.)

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

KDL builds chains from a URDF and computes FK/IK and joint limits; a URML manifest declares capabilities (reach, DOF, workspace bounds) and a safety envelope. Some manifest fields could be derived from a KDL chain; URML's validator could cross-check a manifest's declared workspace against KDL-computed reach. The split: KDL gives the kinematics; the manifest gives capability + safety.

Two real questions: (1) Which URML capability-manifest fields (reach, joint limits, reachable workspace) can be derived honestly from a KDL chain, and which are genuinely separate? (2) Would cross-checking a manifest's declared workspace against KDL-computed reach be useful, and where should the boundary sit?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0461-orocos-kdl-outreach.md

Thanks for KDL; a classic open kinematics library is a great reference point for the derive-vs-declare question.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0462: urchin

**Post to (Issue):** https://github.com/fishbotics/urchin/issues/new
**Title:** URML (open robot intent language): an urchin → capability-manifest adapter? — request for comment

```
Hi urchin maintainer,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. As the actively-maintained successor to urdfpy, urchin is a clean modern Python URDF library — a natural building block for an adapter that derives or cross-checks URML capability-manifest fields from a URDF.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

urchin parses a URDF and computes forward kinematics in Python; a URML manifest declares capabilities and a safety envelope. An adapter could read reach/DOF/joint limits from an urchin model into a URML manifest skeleton, leaving payload, graspable classes, and the safety envelope to explicit declaration. URML's (Python) validator could use urchin to keep a manifest consistent with the robot's URDF. The split: urchin gives the URDF + FK; the manifest gives capability + safety.

Two real questions: (1) Would a thin urchin → URML manifest-skeleton adapter be useful, and what URDF/FK fields map cleanly? (2) Which capability-manifest fields are genuinely outside URDF (payload, graspable classes, safety envelope), and where should the boundary sit?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0462-urchin-outreach.md

Thanks for urchin; keeping a clean URDF + FK Python library alive is a real service, and a great foundation for this kind of adapter.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```
