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

# Move #18 post bodies: frame-break wave (Klipper / WPILib / Crazyflie / BrainFlow / motion + sim / education / humanoids / conceptual peers)

Copy-paste-ready bodies for the 15 Move #18 engageable targets (Pepper RFC-0238 is a Tier C exclusion stub, no body).

Bodies follow the [AGENTS.md](../../AGENTS.md) outreach-post-structure rules added after the Nav2 close (2026-05-29, SteveMacenski closed [navigation2#6184](https://github.com/ros-navigation/navigation2/issues/6184) as too dense to read): concrete hook first, one or two real questions, light ask stated up front, full RFC linked as optional depth, under a two-minute read, zero em-dashes.

**Posting status (this session, 2026-05-29).** GitHub-routable targets are posted live in this PR. Forum / Discord targets stay drafted here for founder posting under his account.

**Routing summary**

| RFC | Target | Status | Live URL |
|---|---|---|---|
| 0227 | Klipper | Draft (Klipper Discourse, founder-post) | — |
| 0228 | WPILib | Draft (Chief Delphi forum, founder-post) | — |
| 0229 | Crazyflie | Draft (Bitcraze Discourse, founder-post) | — |
| 0230 | BrainFlow | **Posted 2026-05-29** | https://github.com/brainflow-dev/brainflow/issues/838 |
| 0231 | Marlin | **Posted 2026-05-29** | https://github.com/MarlinFirmware/Marlin/issues/28450 |
| 0232 | OctoPrint | Draft (OctoPrint Discourse, GH Discussions disabled, founder-post) | — |
| 0233 | LinuxCNC | **Posted 2026-05-29** (secondary touch; forum is primary) | https://github.com/LinuxCNC/linuxcnc/issues/4071 |
| 0234 | Webots | **BLOCKED** (createDiscussion FORBIDDEN for idoco2003; founder posts under their account) | — |
| 0235 | PyBricks | **Posted 2026-05-29** (pybricks/support, the maintainer-recommended Q&A repo) | https://github.com/pybricks/support/issues/2713 |
| 0236 | PROS-VEX | **Posted 2026-05-29** | https://github.com/purduesigbots/pros/issues/789 |
| 0237 | NAOqi-driver | **Posted 2026-05-29** (stale-substrate framing acknowledged) | https://github.com/ros-naoqi/naoqi_driver/issues/171 |
| 0238 | Pepper | No post (Tier C exclusion-with-cause stub) | — |
| 0239 | Poppy | Draft (founder-call hold; 4.5-yr stale upstream) | — |
| 0240 | Reachy | **Posted 2026-05-29** | https://github.com/pollen-robotics/reachy2-sdk/issues/561 |
| 0241 | Open Interpreter | **Posted 2026-05-29** | https://github.com/openinterpreter/open-interpreter/issues/1771 |
| 0242 | Viam | Draft (Viam Discord, founder-post; Issues disabled on rdk) | — |

**This session, 2026-05-29:** 8 GitHub Issues posted live (BrainFlow, Marlin, LinuxCNC, PyBricks, PROS, NAOqi, Reachy, Open Interpreter). 1 Discussion attempt blocked (Webots: createDiscussion FORBIDDEN). 6 forum / Discord / hold targets stay drafted for founder posting under his own account.

**Note on ledger state.** The Move-18 ledger row updates for the 8 live posts were attempted in this session but reverted by a parallel-session writer that has the wave in flux (a different batch organization is in progress). The live posts and their URLs are authoritative; the founder reconciles ledger state with the parallel session.

The mandatory VIBE disclosure line goes last in every body. See [AGENTS.md](../../AGENTS.md) outreach-identity section.

---

## RFC-0230: BrainFlow / OpenBCI

**Post to:** https://github.com/brainflow-dev/brainflow/issues/new
**Title:** URML (open robot intent language): a manifest field for BrainFlow biosignals

```
Hi BrainFlow maintainers,

URML (urml.dev) is a small open language for describing robot intent. A user writes an English instruction; URML translates it to a primitive, validates it against the robot's declared capabilities, then dispatches. One thing URML wants to declare in that manifest is a non-language intent source: a brain-computer-interface signal coming in over BrainFlow, gated by a confidence threshold, that triggers a URML behavior. Apache-2.0 on URML's side, no spec change to BrainFlow proposed, nothing for you to maintain.

One real question. URML's manifest needs a single field that says "this deployment can accept BCI intent over BrainFlow." What grain is most useful from your side: just naming BrainFlow as the substrate, or naming the board class (Cyton, Ganglion, OpenBCI EEG-Cap, etc.), or going to the per-channel level with impedance and filter state? URML defaults to the substrate level for v0.1 and treats per-channel as a future extension, but we want to anchor that decision on what you'd recommend.

Full write-up if useful: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0230-openbci-brainflow-outreach.md

Thanks for keeping BrainFlow vendor-neutral and open.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0231: Marlin

**Post to:** https://github.com/MarlinFirmware/Marlin/issues/new
**Title:** URML (open robot intent language): declaring a Marlin-driven printer in a robot capability manifest

```
Hi Marlin maintainers,

URML (urml.dev) is a small open language for describing robot intent. On a 3D printer, a user writes "print the calibration cube at 0.2 mm"; URML translates that to a `run_print_job` primitive, checks the declared work envelope and material limits, then streams G-code to Marlin over serial. On URML's side it is Apache-2.0, no change to Marlin proposed, nothing for you to maintain.

One real question. URML's capability manifest wants to say "this printer is Marlin-driven, with these motion limits and homing strategy." From your end, is there a canonical Configuration.h-derived field set that you'd point a third party at (build-time defines exposed at runtime via M-code, or something similar), or do you treat the manifest as outside the firmware's scope and expect hosts like OctoPrint or Klipper to carry it? URML would rather pull from a source you consider authoritative than hand-roll a list.

Full write-up if useful: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0231-marlin-outreach.md

Thanks for keeping Marlin the readable reference.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0233: LinuxCNC

**Post to:** https://github.com/LinuxCNC/linuxcnc/issues/new (secondary touch; LinuxCNC forum is the primary maintainer hub)
**Title:** URML (open robot intent language): the canonical descriptor for a LinuxCNC-driven machine in a robot manifest

```
Hi LinuxCNC maintainers,

URML (urml.dev) is a small open language for describing robot intent. On a CNC machine, a user writes "mill this pocket to 5 mm depth"; URML translates that to a machining primitive, checks the declared work envelope and tooling against the machine's manifest, then streams G-code or HAL commands to LinuxCNC. Apache-2.0 on URML's side, no change to LinuxCNC proposed, nothing for you to maintain. The forum is acknowledged as the primary maintainer hub; this Issue is a secondary touch in case GitHub is more convenient.

One real question. URML's manifest wants a single descriptor that says "this is a LinuxCNC-driven 3-axis mill / 4-axis lathe / 6-axis robot arm" with its work envelope and tool changer presence. From the LinuxCNC side, is the canonical source the INI file's [TRAJ] / [EMC] / [KINS] sections, the HAL netlist itself, or a separate machine-config descriptor that maintainers consider authoritative? URML would rather point at what LinuxCNC considers the right source than synthesize one.

Full write-up if useful: https://github.com/URML-MARS/URML/blob/rfc/move18-batches-2to4-complete/docs/rfcs/0233-linuxcnc-outreach.md

Thanks for the breadth of what LinuxCNC drives.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0234: Webots

**Post to:** https://github.com/cyberbotics/webots/discussions/new (Q&A category)
**Title:** URML (open robot intent language): the canonical name for a Webots robot model in a third-party manifest

```
Hi Webots maintainers and community,

URML (urml.dev) is a small open language for describing robot intent. A user writes "patrol two waypoints, then dock"; URML translates that to `move_to` and `dock` primitives, validates against the robot's manifest, then dispatches. When the deployment is a Webots scene rather than physical hardware, URML wants its manifest to say "this is a Webots scene running on Pioneer 3-AT" or "NAO H25" or "Mavic 2 Pro." Apache-2.0 on URML's side, no change to Webots proposed.

One real question. When a third-party tool wants to name a Webots robot model in a manifest, is there a canonical identifier you would point at (the PROTO file name, a URL into webots.cloud, a hash of the proto contents, or something else)? URML's v0.1 default is to use the PROTO name plus version, but we want to anchor on what the Webots side considers stable.

Full write-up if useful: https://github.com/URML-MARS/URML/blob/rfc/move18-batches-2to4-complete/docs/rfcs/0234-webots-outreach.md

Thanks for keeping the simulator both free and open.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0235: PyBricks

**Post to:** https://github.com/pybricks/support/issues/new (Issues are disabled on pybricks-micropython; support is the maintainer-recommended Q&A repo)
**Title:** URML (open robot intent language): a license-clarity question on pybricks-micropython, plus the right Q&A channel

```
Hi PyBricks maintainers,

URML (urml.dev) is a small open language for describing robot intent. A user writes "drive forward 30 cm, then beep"; URML translates that to `move_to` and `play_sound` primitives, validates against the hub's manifest, then dispatches. URML's edu-runtime already ships a LEGO SPIKE Prime adapter, and the natural next step is to declare PyBricks specifically as a substrate the manifest can target. Apache-2.0 on URML's side, no change to PyBricks proposed, nothing for you to maintain.

Two short questions, both light. First: the pybricks-micropython repo currently shows "Other" as its license; could you confirm the OSI license, or point at the LICENSE file that should be authoritative? URML's downstream packaging depends on knowing whether this is MIT, BSD, or something else. Second: is pybricks/support the right place to keep that conversation, or do you prefer the forum at pybricks.com for design-shape questions like this?

Full write-up if useful: https://github.com/URML-MARS/URML/blob/rfc/move18-batches-2to4-complete/docs/rfcs/0235-pybricks-outreach.md

Thanks for keeping Pybricks the cleanest path off the LEGO default firmware.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0236: PROS / VEX V5

**Post to:** https://github.com/purduesigbots/pros/issues/new
**Title:** URML (open robot intent language): how to declare PROS vs VEXcode on V5 in a manifest

```
Hi PROS maintainers,

URML (urml.dev) is a small open language for describing robot intent. A VRC team writes "score four red balls in the high goal, then park"; URML translates that to autonomous-routine primitives, validates against the V5 brain's manifest, then dispatches to the team's compiled C++. URML already has a VEX V5 adapter in its edu-runtime, but the manifest does not yet declare which toolchain the team chose (PROS, VEXcode, Robot-Mesh), and that choice changes the engagement surface meaningfully. Apache-2.0 on URML's side, no change to PROS proposed, nothing for you to maintain.

Two short questions, both for the PROS side. First: the repo currently shows "Other" as the license; could you confirm the OSI license or point at LICENSE.md? Second: from the PROS side, is there a manifest-field shape you'd recommend for declaring "this team is on PROS" (the PROS version, the kernel build, the project template), or is the toolchain choice just opaque from URML's perspective and we should default to "PROS, unspecified version"?

Full write-up if useful: https://github.com/URML-MARS/URML/blob/rfc/move18-batches-2to4-complete/docs/rfcs/0236-pros-vex-outreach.md

Thanks for keeping the open V5 toolchain alive at Purdue.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0237: NAOqi-driver

**Post to:** https://github.com/ros-naoqi/naoqi_driver/issues/new
**Title:** URML (open robot intent language): is ros-naoqi still the canonical NAOqi engagement point in 2026?

```
Hi ros-naoqi maintainers,

URML (urml.dev) is a small open language for describing robot intent. A user writes "walk to the demo spot, wave, then sit"; URML translates that to `move_to`, a gesture primitive, and a posture primitive, validates against the robot's manifest, then dispatches. For NAO and Pepper that dispatch goes through naoqi_driver over libqi. URML's manifest wants to declare "this is a NAOqi-bridged robot" at the bridge layer rather than per-robot, which gives one engagement covering both NAO and Pepper. Apache-2.0 on URML's side, no change to naoqi_driver proposed.

One real question, asked with the cadence slowdown in mind. The repo's last commit is from September 2024. Is ros-naoqi still the canonical engagement point for NAOqi-based deployments in 2026, or has community support migrated somewhere else that URML should anchor on instead? URML would rather point its manifest at the surface that is actually maintained.

Full write-up if useful: https://github.com/URML-MARS/URML/blob/rfc/move18-batches-2to4-complete/docs/rfcs/0237-naoqi-driver-outreach.md

Thanks for keeping the NAOqi bridge alive at all.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0240: Reachy 2

**Post to:** https://github.com/pollen-robotics/reachy2-sdk/issues/new
**Title:** URML (open robot intent language): Reachy 2 SDK or ROS 2 as the URML adapter layer?

```
Hi Pollen Robotics team,

URML (urml.dev) is a small open language for describing robot intent. A user writes "hand me the red mug"; URML translates that to `pick_from` and `move_to` primitives, validates against Reachy's bimanual + mobile-base capability manifest, then dispatches. The question for URML's adapter target is whether to compose against reachy2-sdk directly or to drop one layer down and compose against the underlying ROS 2 stack (URML already has a ROS 2 reference runtime). Apache-2.0 on URML's side, commercial-OSS hybrid acknowledged.

One real question. From your side, which layer is the cleaner long-term integration target for a third-party intent compiler: the Python SDK at reachy2-sdk (stable, vendor-blessed API, easier ergonomics) or the ROS 2 nodes underneath (more general, more substrate-neutral)? URML's default for Reachy 2 is to target the SDK and call this out as a deliberate higher-level choice, but if you would rather see third parties anchor on ROS 2 we want to know before shipping.

Full write-up if useful: https://github.com/URML-MARS/URML/blob/rfc/move18-batches-2to4-complete/docs/rfcs/0240-reachy-outreach.md

Thanks for keeping Reachy 2 open-source-first.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0241: Open Interpreter

**Post to:** https://github.com/OpenInterpreter/open-interpreter/issues/new
**Title:** URML (open robot intent language): peer-citation and an interoperability question for Open Interpreter

```
Hi Open Interpreter maintainers,

URML (urml.dev) is a small open language for describing robot intent. A user writes "stack the red cube on the blue platform"; URML translates that to `pick_from` and `place_at` primitives, validates against the robot's manifest, then dispatches to a substrate. The shape is the same one Open Interpreter uses for general computer control (user writes "resize all images in this folder to 800 px"; the agent generates shell or Python and runs it). Different action surfaces, same NL-to-action loop. Apache-2.0 on URML's side, no change to Open Interpreter proposed.

Two short questions. First: would you welcome a peer-citation footnote in URML's docs that points at Open Interpreter as the general-purpose-computer analog of URML's robot-intent specialization, and is a reciprocal mention something the project would consider? Second, more speculative: is there an interoperability shape worth exploring, where URML emits computer-control intents (file moves, container ops) that Open Interpreter executes for the non-robot half of a deployment?

Full write-up if useful: https://github.com/URML-MARS/URML/blob/rfc/move18-batches-2to4-complete/docs/rfcs/0241-open-interpreter-outreach.md

Thanks for setting the bar on local-first natural-language tooling.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## Forum-routable and Discord-routable drafts (founder posts)

These bodies stay drafted here for the founder to post under his account on the maintainer-preferred channel. Each one is in the same post-Nav2 reformed shape.

### RFC-0227 Klipper (Klipper Discourse forum)

**Title:** URML (open robot intent language): declaring a Klipper-driven motion platform in a robot manifest

```
Hi Klipper community,

URML (urml.dev) is a small open language for describing robot intent. A user writes "print the calibration cube at 0.2 mm"; URML translates that to a `run_print_job` primitive, validates the work envelope and material limits against the manifest, then streams G-code to Klipper over the Moonraker API. On URML's side it is Apache-2.0, no spec change to Klipper proposed, nothing for you to maintain.

One real question. URML's manifest wants to declare "this is a Klipper-driven Cartesian / CoreXY / Delta platform with these motion limits and this kinematic." From the Klipper side, is the canonical source the printer.cfg the user already maintains, the host's reported limits over Moonraker, or a higher-level descriptor you would recommend for third-party tooling to anchor on?

Full write-up if useful: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0227-klipper-outreach.md

Thanks for keeping the host-plus-MCU architecture both fast and readable.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

### RFC-0228 WPILib (Chief Delphi forum)

**Title:** URML (open robot intent language): declaring a WPILib / FRC robot in a capability manifest

```
Hi WPILib and FRC community,

URML (urml.dev) is a small open language for describing robot intent. An FRC team writes an English plan ("auto: drive forward, score on the speaker, return for a teleop handoff"); URML translates that into autonomous-routine primitives, validates against the robot's manifest (drivetrain class, motor controllers, subsystems), then dispatches into the team's WPILib-built code on the roboRIO. On URML's side it is Apache-2.0, no change to WPILib proposed, nothing for the project to maintain.

One real question. URML's manifest wants a single descriptor that says "this is an FRC robot with this drivetrain class (tank / mecanum / swerve), these motor controllers, and these named subsystems." From the WPILib side, is there a config or annotation pattern in the existing template projects that third-party tooling should anchor on, or is the manifest just out of scope from the library's perspective?

Full write-up if useful: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0228-wpilib-outreach.md

Thanks for being the on-ramp that gets the next generation of roboticists building.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

### RFC-0229 Crazyflie (Bitcraze Discourse forum)

**Title:** URML (open robot intent language): declaring a Crazyflie deployment in a robot capability manifest

```
Hi Bitcraze maintainers and community,

URML (urml.dev) is a small open language for describing robot intent. A user writes "take off, fly the figure-eight, then land at the start"; URML translates that to multirotor primitives, validates against the Crazyflie's manifest (deck stack, battery, positioning setup), then dispatches through cflib over CRTP. On URML's side it is Apache-2.0, no change to Crazyflie proposed, nothing for you to maintain.

One real question. URML's manifest wants to declare "this is a Crazyflie with these decks attached and this positioning setup (Lighthouse, Loco, motion-capture, none)." From the Bitcraze side, is there a canonical place where deck and positioning configuration is already enumerated (a TOML in the firmware repo, the cfclient settings, the cflib API itself), or is this manifest concept outside the existing model and we should pick a reasonable default?

Full write-up if useful: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0229-crazyflie-outreach.md

Thanks for keeping a 27 g research drone real.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

### RFC-0232 OctoPrint (OctoPrint Discourse forum; Discussions disabled on GitHub)

**Title:** URML (open robot intent language): a manifest field for an OctoPrint-hosted 3D printer

```
Hi OctoPrint maintainers and community,

URML (urml.dev) is a small open language for describing robot intent. A user writes "print this STL at 0.2 mm, pause at layer 5 for a magnet insert"; URML translates that into a host-side print-job intent, validates against the printer's manifest, then dispatches through the OctoPrint REST API. URML reaches OctoPrint over the REST boundary deliberately so the AGPL-3.0 stays clean on both sides. Apache-2.0 on URML's side, no change to OctoPrint proposed, nothing for you to maintain.

One real question. URML's manifest wants to declare "this is an OctoPrint-hosted printer with these plugins installed and this firmware underneath (Marlin / Klipper / RepRap)." From the OctoPrint side, is there a settings shape the API already exposes that third-party tooling should mirror, or is this declaration outside the existing model?

Full write-up if useful: https://github.com/URML-MARS/URML/blob/rfc/move18-batches-2to4-complete/docs/rfcs/0232-octoprint-outreach.md

Thanks for keeping the snappy web interface snappy.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

### RFC-0239 Poppy (founder-call hold; 4.5-yr stale upstream)

Drafted but held per the post-Nav2 fit-honest rule. The upstream repo last saw a commit 4.5 years ago; cold-posting carries a high abandonment-signal risk. Founder decides whether to post or hold.

**Title:** URML (open robot intent language): is poppy-project still maintained, and what is the canonical Python entry point?

```
Hi Poppy project maintainers and community,

URML (urml.dev) is a small open language for describing robot intent. A user writes "raise both arms, then nod"; URML translates that to gesture primitives, validates against the humanoid's manifest, then dispatches to the Dynamixel servos via a Python control library. On URML's side it is Apache-2.0, no change to Poppy proposed.

Two short questions, asked with respect for the project's reduced cadence. First: is the project still under active maintenance, and if so where (this repo, poppy-software, somewhere else)? Second: if a third party wants to write an adapter today, which Python entry point is the canonical one (pypot, poppy-creature, poppy-humanoid as a meta-package, or something newer)? The README's library list is several years old and URML would rather anchor on what is current than guess.

Full write-up if useful: https://github.com/URML-MARS/URML/blob/rfc/move18-batches-2to4-complete/docs/rfcs/0239-poppy-humanoid-outreach.md

Thanks for the 3D-printable humanoid being a thing in the world at all.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

### RFC-0242 Viam (Viam Discord; Issues disabled on rdk)

**Title:** URML (open robot intent language): the interoperability seam between URML and Viam RDK

```
Hi Viam team,

URML (urml.dev) is a small open language for describing robot intent. A user writes "patrol two waypoints, then dock"; URML translates that to `move_to` and `dock` primitives, validates against the robot's capability manifest, then dispatches. Viam composes adapters over hardware; URML composes intent over substrates. The two systems overlap meaningfully at the resource-API layer with different design points (Viam = cloud-coupled, URML = local-validate-then-dispatch). On URML's side it is Apache-2.0, AGPL-3.0 boundary acknowledged for any code-level interaction.

One real question. From Viam's side, where do you see the cleanest interoperability seam: at the resource-API level (URML's manifest declares Viam-managed resources and validates against Viam's component model), at the intent level (URML emits high-level intent that Viam dispatches into its modular components), or just mutual-citation in each project's docs? URML's default is mutual-citation for v0.1 with the resource-API seam as a later exploration.

Full write-up if useful: https://github.com/URML-MARS/URML/blob/rfc/move18-batches-2to4-complete/docs/rfcs/0242-viam-rdk-outreach.md

Thanks for keeping the modular framework an open conversation.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```
