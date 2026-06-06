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

# Move #33 post bodies: the agriculture / farm-robotics wave

Eight targets. Post under idoco2003 via the channel noted per row (Discussion or
Issue). No license-ask (state the license). AI-assisted-authoring disclosure up
front. At post time, query the repo's real Discussion category id (Move #30
procedure) for the two Discussion targets.

---

## RFC-0404: FarmBot

**Post to (Issue — Discussions off; Forum is the alternative):** https://github.com/FarmBot/farmbot_os/issues/new
**Title:** URML (open robot intent language): a validated intent layer above FarmBot — request for comment

```
Hi FarmBot community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: a person writes an English sentence, URML turns it into a typed primitive, validates it against the robot's declared capabilities and a safety envelope, then dispatches. FarmBot is the most accessible open farm robot there is, with a clean sequence + REST/MQTT command API, which makes it a natural fit for a validated natural-language layer.

Nothing here asks FarmBot to adopt, host, or maintain anything. This is a request for comment, and genuinely a design question.

URML is not ROS-bound; it dispatches to whatever a substrate exposes. FarmBot exposes named sequences over a REST/MQTT API, so URML binds to that the same way it binds AUTOSAR service methods: a FarmBot sequence is declared in the URML manifest as a program, and call_program(name, args) invokes it after validation. "Water the tomatoes in bed 3" becomes a typed primitive, validated against the declared bed geometry / tool set / plant vocabulary, and only then dispatched. Validate-before-actuate refuses an undeclared tool or an out-of-bounds coordinate before a motor moves.

Two real questions: (1) Is binding FarmBot sequences via call_program (sequence name + typed args) the right granularity to drive FarmBot from an outside intent layer, or is the Web App REST/MQTT API a better seam? (2) What should a URML capability manifest declare to describe a FarmBot honestly — bed/work-area geometry, mounted tools (seeder, waterer, weeder, sensor), plant/crop vocabulary, coordinate bounds?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0404-farmbot-outreach.md

Thanks for FarmBot; an open-source CNC farming robot is one of the best on-ramps in robotics.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0405: farm-ng Amiga

**Post to (Discussion):** https://github.com/farm-ng/amiga-dev-kit/discussions/new?category=ideas
**Title:** URML (open robot intent language): a validated intent layer above the Amiga — request for comment

```
Hi farm-ng community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. The Amiga is a rugged, commercial-but-open ag rover with gRPC and ROS bridges — exactly the kind of mobile platform a validated natural-language layer should sit above.

Nothing here asks farm-ng to adopt, host, or maintain anything. This is a request for comment.

A URML drive / navigation intent ("drive the east row at 1 m/s and record") lowers onto the Amiga's ROS bridge — which meets URML's ROS 2 runtime directly — or the gRPC surface as a binding target. Validate-before-actuate refuses a request outside the declared speed, area, or implement envelope before the rover moves, which matters on a heavy outdoor platform.

Two real questions: (1) Is the ROS bridge or the gRPC surface the better seam for an external validated-intent layer above the Amiga? (2) What should a URML capability manifest declare to describe an Amiga-class ag rover honestly — drive type, speed/turn limits, implement interfaces, GNSS/positioning, field-boundary / geofence constraints?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0405-farm-ng-outreach.md

Thanks for the Amiga and the open dev kit; an open developer surface on a real ag platform is a great thing for the field.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0406: CropCraft (Romea)

**Post to (Issue — Discussions off):** https://github.com/Romea/cropcraft/issues/new
**Title:** URML (open robot intent language): driving a field robot in a CropCraft world from validated intent — request for comment

```
Hi Romea / CropCraft maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches to the substrate below. CropCraft is interesting to URML as a procedural crop-field world generator for robotics simulation — a place a URML-validated command can drive a field robot before any hardware.

Nothing here asks CropCraft to adopt, host, or maintain anything. This is a request for comment.

A URML field-robot program (drive rows, detect, measure, report) runs against a CropCraft-generated world through the ROS 2 surface URML's runtime already targets. URML's optional validation block records the simulation-fidelity context a deployment was checked in, which CropCraft's procedural fields and ground-truth sensors make concrete; the sim-first posture matches URML's own.

Two real questions: (1) Is a validated natural-language intent layer above CropCraft interesting as a demonstration / teaching surface for field-robot scenarios? (2) What should a URML manifest declare to describe a field-robot deployment honestly — drive type, row/area geometry, implement set, crop vocabulary, GNSS — and is the broader Romea middleware a natural integration point?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0406-cropcraft-outreach.md

Thanks for CropCraft; a permissive, procedural crop-field generator is a real asset for ag-robotics simulation.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0407: OpenWeedLocator

**Post to (Discussion):** https://github.com/geezacoleman/OpenWeedLocator/discussions/new?category=ideas
**Title:** URML (open robot intent language): a validated detect-then-spray layer above OpenWeedLocator — request for comment

```
Hi OpenWeedLocator community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. OWL is interesting to URML because its detect-then-spray loop is exactly the decide-then-do split URML's primitives are built around.

Nothing here asks OWL to adopt, host, or maintain anything. This is a request for comment.

In URML, a detect step binds a target and an actuation step consumes it — the same pattern as detect -> grasp, here detect -> spray. Validate-before-actuate is the safety point that matters for a sprayer: a spray action outside the declared application envelope (a no-spray zone, a rate cap, an undeclared nozzle) is refused before a relay fires. A URML manifest would declare what OWL can sense and actuate, making "spray the weeds but not within 1 m of the crop row" a validatable intent.

Two real questions: (1) Is a validated intent layer above OWL's detect-then-spray loop interesting, or does the existing configuration already cover that need? (2) What should a URML manifest declare to describe a spot-sprayer honestly — detection classes, nozzle/relay configuration, application-rate limits, no-spray exclusion zones?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0407-openweedlocator-outreach.md

Thanks for OWL; a low-cost open weed-detection-and-spray device is a genuinely useful contribution.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0408: Agri-OpenCore / L-CAS

**Post to (Issue):** https://github.com/LCAS/aoc_tomato_farm/issues/new
**Title:** URML (open robot intent language): a validated intent layer above the Agri-OpenCore stack — request for comment

```
Hi L-CAS / Agri-OpenCore maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. The Agri-OpenCore stack — the tomato-glasshouse digital twin here, plus the lab's GNSS drivers, crop-monitoring, and mobile-manipulator work — is the most active academic agri-robotics ecosystem I have found, and a natural place for a validated intent layer.

Nothing here asks L-CAS to adopt, host, or maintain anything. This is a request for comment.

URML's ROS 2 runtime targets the aoc_tomato_farm digital twin and the lab's robots directly; "inspect row 4 and report ripe tomatoes" lowers onto the ROS 2 surface. URML's optional validation block records the simulation-fidelity context the glasshouse twin makes concrete, and the lab's mobile-manipulator work is where URML's manipulation primitives would exercise harvesting intent. Validate-before-actuate refuses an out-of-capability request before dispatch across a heterogeneous fleet.

Two real questions: (1) Is a validated natural-language intent layer above the Agri-OpenCore stack interesting for the lab's glasshouse / field robotics? (2) What should a URML capability manifest declare to describe a glasshouse or field agri-robot honestly — drive type, row/bench geometry, crop vocabulary, manipulator reach for harvesting, GNSS?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0408-agri-opencore-lcas-outreach.md

Thanks for Agri-OpenCore; an open, active academic agri-robotics ecosystem is exactly where this kind of layer should be designed with input rather than guessed.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0409: FarmBot-ROS2 (AURA / Maynooth)

**Post to (Issue):** https://github.com/farmbot-ros/interfaces/issues/new
**Title:** URML (open robot intent language): aligning a validated intent layer with FarmBot-ROS2 — request for comment

```
Hi FarmBot-ROS2 (AURA / Maynooth) maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches over ROS 2. Your modular ROS 2 re-implementation of FarmBot control is a pure ROS 2 agricultural stack URML's runtime can target directly — and I want to check where a validated-intent layer aligns with your interfaces.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML's ROS 2 runtime meets farmbot-ros on its action/service surface; "seed bed 2 and water it" lowers onto the cartograph / taskforce modules. The shared interfaces package is the natural place to align URML's typed intent with your message contracts — URML prefers to target the standard interfaces rather than invent parallel ones (the same way it targets Nav2 and ros2_control). Validate-before-actuate refuses an undeclared tool or out-of-bounds coordinate before dispatch.

Two real questions: (1) Does URML's typed intent map cleanly onto the interfaces message contracts, and where should it target them rather than a generic ROS surface? (2) What should a URML capability manifest declare to describe a FarmBot-class gantry in ROS 2 — bed geometry, tool set, plant vocabulary, coordinate bounds?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0409-farmbot-ros2-outreach.md

Thanks for FarmBot-ROS2; a clean modular ROS 2 take on FarmBot control is great to see.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0410: PRBonn AgriBot

**Post to (Issue — Discussions off):** https://github.com/PRBonn/agribot/issues/new
**Title:** URML (open robot intent language): a validated intent layer above an AgriBot field robot — request for comment

```
Hi PRBonn AgriBot maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. AgriBot is a credible academic field robot from a lab whose crop/weed perception and agricultural mapping are exactly the kind of perception substrate a validated intent layer composes with, which is why I am writing.

Nothing here asks PRBonn to adopt, host, or maintain anything. This is a request for comment, and a design question.

URML's ROS 2 runtime targets the AgriBot's ROS surface; "survey the field and record" lowers onto its navigation + data-recording interface. Your crop/weed perception is the kind of detect source URML consumes: a detection binds a target a downstream action consumes (decide-then-do). Validate-before-actuate refuses an out-of-capability request before dispatch.

Two real questions: (1) What should a URML capability manifest declare to describe an agricultural field robot honestly — drive type, row/field geometry, sensor suite, GNSS/positioning? (2) Where is the cleanest seam — URML above the navigation/recording interface, or composing with the lab's perception/mapping outputs as detect sources?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0410-prbonn-agribot-outreach.md

Thanks for AgriBot and the lab's ag-perception work; it is some of the most credible research in the area.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0411: smart_diffbot (Saxion)

**Post to (Issue):** https://github.com/SaxionMechatronics/smart_diffbot/issues/new
**Title:** URML (open robot intent language): a validated intent layer above smart_diffbot — request for comment

```
Hi smart_diffbot maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. smart_diffbot is a clean ROS 2 differential-drive robot with Nav2-based outdoor GNSS navigation — a tidy fit for URML's Nav2-targeting runtime, and a common agricultural / field-robot shape.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML's move_to lowers onto smart_diffbot's Nav2 navigation (Nav2 is already a URML substrate), so "drive to this GNSS waypoint and report" maps cleanly. Validate-before-actuate refuses a request outside the declared speed / area envelope before the rover moves. The outdoor-GNSS shape is a useful, minimal manifest case.

Two real questions: (1) Is URML's move_to-onto-Nav2 mapping the right seam for an outdoor GNSS rover? (2) What should a URML manifest declare to describe an outdoor GNSS diff-drive robot honestly — drive type, speed limits, GNSS frame, geofence / field boundaries?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0411-smart-diffbot-outreach.md

Thanks for smart_diffbot; a clean open ROS 2 + Nav2 outdoor GNSS rover is a nice, approachable platform.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```
