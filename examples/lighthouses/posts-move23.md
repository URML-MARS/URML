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

# Move #23 post bodies: ros2_control / actuation-control stack

Copy-paste-ready bodies for the three Tier-A targets. Sibling `ros-controls`
repos (ros2_controllers, gz_ros2_control, control_toolbox, realtime_tools,
control_msgs, kinematics_interface) and the fieldbus master libs (SOEM,
CANopenNode) are folded into these threads, not posted separately, to avoid
carpet-bombing one org. The EtherCAT Technology Group is deferred (no GitHub
surface). See [`outreach-move23.yaml`](outreach-move23.yaml) for the full set.

Bodies follow the [AGENTS.md](../../AGENTS.md) outreach-post-structure rules:
concrete hook first, "nothing for you to maintain" up front, one or two real
questions, full RFC linked as optional depth, under a two-minute read, zero
em-dashes. The audience is a control-framework maintainer, so the bodies speak
in `hardware_interface` / `command_interface` / `controller_manager` terms. The
mandatory VIBE disclosure line goes last in every body.

All three repos have Issues enabled (verified 2026-06-02). `ros2_control` and
`ros2_canopen` have Discussions disabled, so each is a single Issue;
`ethercat_driver_ros2` has both, so an Issue or a Discussion is fine.

**Posting status:** DRAFTED, not yet posted. Post under `idoco2003` only after
RFCs 0319-0321 land on `main`. Then fill `sent_at` / `posted_url` and add a
posted comment per row in `outreach-move23.yaml`, and refresh `outreach.db`.

**Routing summary**

| RFC | Target | Channel | Status |
|---|---|---|---|
| 0319 | ros2_control (framework anchor) | Issue on `ros-controls/ros2_control` | Drafted (post after merge) |
| 0320 | ethercat_driver_ros2 | Issue/Discussion on `ICube-Robotics/ethercat_driver_ros2` | Drafted (post after merge) |
| 0321 | ros2_canopen | Issue on `ros-industrial/ros2_canopen` | Drafted (post after merge) |

---

## RFC-0319: ros2_control (framework anchor)

**Post to:** https://github.com/ros-controls/ros2_control/issues/new
**Title:** URML (open robot intent language): mapping a validated-intent layer onto ros2_control, request for comment

```
Hi ros2_control maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent. A person (or an LLM) writes an English sentence, URML translates it to a typed primitive, statically validates it against the robot's declared capability manifest and the active safety envelope, then dispatches. It composes above ros2_control: URML intent -> validated primitive -> a controller_manager-managed controller -> command interfaces -> hardware. ros2_control is the cleanest substrate fit URML has found, because your hardware_interface / controller split mirrors URML's Layer-1 (capability) / Layer-2 (primitive) split almost one to one.

Nothing here asks ros2_control to change or maintain anything. This is a request for comment on whether the layers fit, and where the boundary should sit.

The interesting part for URML is that we validate before any command interface is claimed, which is one layer up and earlier than resource_manager's runtime arbitration. So two real questions:

1. Interface granularity. URML's capability manifest today declares capability blocks (a manipulation block, a mobility block), not the position/velocity/effort command and state interfaces a <ros2_control> tag enumerates per joint. Should URML's manifest declare interfaces at that grain to mirror the description, or stay coarse and let the adapter resolve interfaces from the URDF?

2. Primitive to controller binding. URML maps a primitive (move_to, grasp) to an outcome, not to a named controller. Is "URML primitive -> controller_manager activate + a joint_trajectory_controller goal" the right adapter boundary, and would it help for the manifest to declare which controllers a deployment exposes?

A bonus question if you have patience for it: is gz_ros2_control (or mock_components) the right vehicle for a hermetic demo, validated intent -> controller -> simulated hardware, with no real robot in the loop? That is the shape our example fixtures prefer.

This thread is also the home for the ros-controls family in general (ros2_controllers, control_toolbox, realtime_tools, control_msgs, kinematics_interface); I did not want to open five Issues at one org. If any of those deserves its own thread, point me and I will move it.

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0319-ros2-control-outreach.md

One small thing: the GitHub API did not surface an SPDX license id for the repo at our verification time. Is it Apache-2.0?

Thanks for ros2_control. It is the piece of the ROS 2 stack that made this mapping feel natural rather than forced.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0320: ethercat_driver_ros2

**Post to:** https://github.com/ICube-Robotics/ethercat_driver_ros2/issues/new
**Title:** URML (open robot intent language): EtherCAT fieldbus mapping under ros2_control, request for comment

```
Hi ICube-Robotics team,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. I have opened a parallel thread with ros2_control about the framework mapping (RFC-0319). This one is specifically about the fieldbus beneath it. Because ethercat_driver_ros2 presents a ros2_control SystemInterface, URML's primitive -> controller -> command interface path carries straight through to your EtherCAT command interfaces; the added concern is what the bus exposes.

Nothing here asks the project to change or maintain anything. It is a request for comment, and partly a boundary check I would value your read on.

URML deliberately does not model bus wiring. EtherCAT topology, slave addresses, PDO/SDO mapping, distributed-clock sync, all of that stays in your driver config, which URML treats as Layer 0 (we draw the same line for network transports). So:

1. Is "URML primitive -> controller -> ethercat_driver_ros2 command interface" the right boundary, with the slave and PDO mapping left entirely in the driver config? Does anything about EtherCAT break that clean separation?

2. For CiA-402 drives, should URML's manifest ever surface the operation mode (profile position vs cyclic synchronous position), or is that firmly substrate configuration in your view?

The honest reason EtherCAT matters to URML: it is the hardest, most real-time-sensitive end of the substrate spectrum, so a clean mapping here is the strongest evidence our abstraction is not accidentally ROS-shaped. I am tracking SOEM as the master library underneath; this thread covers it unless you would rather route the master-lib layer separately.

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0320-ethercat-driver-ros2-outreach.md

One small thing: the GitHub API did not surface an SPDX license id at our verification time. Is the driver Apache-2.0?

Thanks for keeping an open EtherCAT hardware interface alive for ros2_control.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0321: ros2_canopen

**Post to:** https://github.com/ros-industrial/ros2_canopen/issues/new
**Title:** URML (open robot intent language): CANopen device-profile mapping under ros2_control, request for comment

```
Hi ros2_canopen maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. I have a parallel thread open with ros2_control about the framework mapping (RFC-0319) and one with the EtherCAT driver (RFC-0320). This one is the CANopen counterpart. To be clear about scope: this is specifically about the ros2_canopen device-profile mapping, not a re-pitch of the ROS-Industrial consortium (I touched that separately in RFC-0038, cross-linked below).

Because ros2_canopen presents a ros2_control SystemInterface, URML's primitive -> controller -> command interface path carries through to your CANopen command interfaces. The CiA-402 object dictionary, node IDs, EDS files, PDO mapping, and NMT state stay in the driver config, which URML treats as Layer 0.

Nothing here asks the project to change or maintain anything. Two real questions:

1. Is "URML primitive -> controller -> ros2_canopen command interface" the right boundary, with the object dictionary and node addressing left in the driver config?

2. For a deployment that could run either CANopen or EtherCAT, is there a preference for how URML should present that choice, a fieldbus-class hint in the manifest, or no manifest distinction at all? (I am asking the EtherCAT driver folks the mirror of this in RFC-0320.)

With EtherCAT and CANopen both mapped under one ros2_control framing, URML gets a two-buses-one-abstraction data point, which is exactly the kind of evidence our substrate-neutrality claim needs. I am tracking CANopenNode as the protocol stack underneath; this thread covers it unless you would rather route that layer separately.

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0321-ros2-canopen-outreach.md

One small thing: the GitHub API did not surface an SPDX license id at our verification time. Is ros2_canopen Apache-2.0?

Thanks for bringing CANopen drives cleanly into ros2_control.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```
