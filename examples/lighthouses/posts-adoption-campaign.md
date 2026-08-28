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

# Adoption-campaign drafts (founder-action)

## 1. slowrunner: first registry/directory entry (founder-voiced, founder-posted)

Channel: email or a comment on Discussion #497, founder's choice. He prefers
human replies; keep it personal, no footer. Why this matters strategically:
the runtime registry's third-party section is empty, and the standing public
commitment to a Tier-1 OEM advances "in the same wave that admits the first
third-party runtime." His entry is that wave, and it is also simply true:
he earned it. Do not name the OEM to him or anyone; the invite stands on its
own merits.

> Hey, an invitation rather than an ask.
>
> URML is opening its adopter and runtime registry, and I want the first entry to be real rather than corporate: you and Lyrical-Dave. You were the first person outside the project to run a validated URML program on hardware, you caught the FLU-to-RFD frame bug on a real robot and fixed it upstream, and your Ollama HOWTO literally changed the CLI (native `--provider ollama` is on main now, no dummy key; your context-length guidance still applies word for word).
>
> Concretely, if you are up for it: a short self-reported row in `docs/compatible-runtimes.md` for the GoPiGo3 runtime you validated (RFC-0014 self-reported tier, you credited as its hardware validator and field maintainer), and, if you like, an adopter entry on urml.dev with Dave's picture. It is one PR against a template (`docs/registry/SUBMISSION.md`); I can prepare the whole thing for your review, or you drive it, whichever is more fun.
>
> No deadline, no obligation, and if you would rather stay an uncredited legend, that is fine too.

On acceptance: help him land the PR (or prepare it for his review), then the
registry's first third-party entry exists; the OEM listing wave (Kawasaki row
on the commitments page) advances in that same wave, per the written promise.

## 2. Kawasaki listing back-post (queued behind entry #1)

Only after the first third-party registry entry is merged. One short comment
on Kawasaki-Robotics/khi_ros2#9 (closed resolved, warm): the listing condition
recorded in RFC-0029 and the commitments page has been met, the
`KawasakiAdapter` row is now live in `docs/compatible-runtimes.md` at the
self-reported tier, link to the row. No ask. Then the Mitsubishi follow-up on
melfa_ros2_driver discussion #25: the conformance-listing wave hunterzhongME
deferred on is now real, his Q4 answer welcome whenever.

## 3. Zivid report-back (after RFC-0682 merges)

**Public, on zivid/zivid-ros#163** (posted under idoco2003, VIBE line, no ask):

> Closing the loop on the schema questions from May: RFC-0682 (https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0682-3d-camera-declaration.md) is on main. It follows the guidance from the email exchange rather than inventing shapes: a 3D camera declares its primary product as a color point cloud with per-point attributes (xyz, rgba, snr, normals), accuracy is never a scalar (the manifest points at the per-model datasheet instead), acquisition modes stay the camera's business, and `pick_from` gained no vision-source field. The one open item that was ours to decide, hand-eye calibration, is a `mount` declaration (eye-in-hand or eye-to-hand against a declared frame, with an opaque reference to the calibration artifact). The Zivid Two cell manifest in the repo demonstrates every field. No ask; corrections welcome.
>
> AI-assisted prose, maintainer-reviewed before posting (see VIBE.md). Human-only correspondence available on request.

**Email to Espen Holmbakken** (founder-voiced, founder-sent from greenvh@gmail.com; he chose email as the substantive channel):

> Subject: URML follow-up: the 3D-camera schema, built the way you suggested
>
> Hi Espen,
>
> A short report-back on the exchange from May. You steered us away from recommending schema shapes and toward Zivid's authoritative documentation, and that turned out to be the right instruction. RFC-0682 is now on URML's main branch: a camera declares its primary product as a color point cloud with per-point attributes (xyz, rgba, snr, normals), accuracy is deliberately not a scalar (the manifest carries a pointer to the per-model datasheet, exactly the trueness/precision/working-distance point you made), acquisition modes stay the camera's business, and we dropped the pick_from vision-source idea as you suggested.
>
> The one question you left with us, hand-eye calibration, became a small `mount` declaration: eye-in-hand or eye-to-hand against a declared frame, with an opaque reference to the calibration artifact and the geometry riding the frame transforms we already had. No calibration file format invented.
>
> The Zivid Two cell manifest in the repo demonstrates every field: https://github.com/URML-MARS/URML/blob/main/reference/validator/tests/fixtures/manifests/zivid_two_cell.yaml
>
> Nothing to ask. If any of it misrepresents how Zivid thinks about these fields, I would rather fix it than leave it wrong.
>
> Thanks again,
> Ido

## 4. Model Hardware Standard: every submission, post, and email (adoption campaign)

Gate: the harness PR is merged and the blog post is live before anything below goes out. Founder-voiced channels are first person, no AI footer. GitHub posts carry the VIBE line. No public post names any other engaged org. Record each send in `outreach-move71.yaml` and on the commitments page.

Links every draft uses:
- Harness: https://github.com/URML-MARS/URML/tree/main/examples/physical-ai-safety-eval
- Positioning: https://github.com/URML-MARS/URML/blob/main/docs/integrations/model-hardware-standard.md
- Blog: https://urml.dev/blog/mhs-and-urml/
- RFC-0683: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0683-model-hardware-standard-outreach.md

### 4.1 Research-preview application (founder submits at modelhardwarestandard.com)

> Organization: URML (urml.dev), an Apache-2.0 open specification for robot intent, stewarded by MARS.
>
> What we build: an intent language and a five-pass static validator that checks a whole robot program against a capability manifest and a deployment safety envelope before any actuator moves, with runtime envelope enforcement, a simulation rehearsal gate, a conformance suite, and evidence tags on every capability claim. Reference runtimes ship for ROS 2, PX4, OPC UA, and vendor SDKs, including Universal Robots and Doosan. An MCP server exposes the validator to agents with no path to an actuator that skips it.
>
> Why MHS: MHS answers what a device is and what it refuses per call. URML answers whether the whole program is admissible on that device in this deployment before the first call, and lets a site cap a device below its vendor limits. We would like to build, under Apache 2.0 and during the preview: an importer that reads an MHS reference file into a capability manifest (we ship the same for URDF), an adapter that dispatches validated URML programs through MHS read/write, and conformance fixtures for MHS-driven devices, starting with the two partners we already support.
>
> What exists today: a hermetic safety-evaluation harness for agents operating physical equipment, built against a lab cell shaped like the assay in your announcement, reporting refusals with machine-readable reasons, envelope verdicts over rehearsed traces, and the evidence class of every limit relied on: https://github.com/URML-MARS/URML/tree/main/examples/physical-ai-safety-eval
>
> Contact: Ido Yahalomi, greenvh@gmail.com. No ask beyond access to the specification.

### 4.2 URML GitHub Discussions announcement (Announcements; I post under idoco2003)

> **URML and the Model Hardware Standard: where we sit, and an evaluation harness for the gate Anthropic named**
>
> Anthropic opened a research preview of the Model Hardware Standard this week: a standardized driver (read/write primitives), discovery, and a per-device reference file of what it measures, adjusts, and refuses. It is model-agnostic and will be open-sourced after "safety evaluations and best practices for AI systems that operate physical equipment" exist.
>
> Where URML sits: above it. MHS says what a device is and what it refuses per call; URML checks the whole program against the manifest and the deployment envelope before the first call, and lets a site cap a device below its vendor's limits. Positioning and a mapping table: <positioning link>. Blog: <blog link>.
>
> What we built for the gate: a hermetic safety-evaluation harness, a corpus of agent intents against a lab cell shaped like the assay in Anthropic's post, with refusals in machine-readable codes, envelope-monitor verdicts over rehearsed traces, and the evidence class of every limit relied on. <harness link>. RFC-0683 records what waits for the open spec (an importer, an adapter): <RFC link>.
>
> We have not seen the specification and claim no compatibility with it. Corrections and counter-arguments welcome here.
>
> AI-assisted prose, maintainer-reviewed before posting (see VIBE.md). Human-only correspondence available on request.

### 4.3 LinkedIn post (founder profile; image: the refusal matrix from the report)

> Anthropic just previewed the Model Hardware Standard: a common driver so AI agents can find and operate lab and factory equipment, with each device carrying its own safety limits. Universal Robots, Doosan, Danaher, Tecan and top labs are in.
>
> I have spent the last months building the layer above that: URML, an open language where an agent's whole plan is checked against the robot's declared capabilities and the site's safety envelope before the first command goes out. A per-call limit catches the fifth action of a bad plan. A program check refuses the plan. And a lab gets to be stricter than the vendor.
>
> Anthropic said the standard opens once safety evaluations exist. So we built one: a harness that judges agent intents against an assay cell like the one in their post and reports exactly why each unsafe one is refused. Open source, runs offline in seconds.
>
> Post: <blog link>. Harness: <harness link>.

### 4.3b LinkedIn article (founder profile; the blog in first person, published a few days after the post)

> **Title:** The driver and the language: where URML sits next to Anthropic's Model Hardware Standard
>
> Anthropic opened a research preview of the Model Hardware Standard this week. In their words it is a standardized driver, a small set of primitives like read and write that any device can understand, plus discovery over the network and a reference file per device describing what it can measure, what can be adjusted, and what safety limits it will enforce. It is model-agnostic, reachable through MCP, a command line, or code, and it will be open-sourced after Anthropic and its partners build safety evaluations for AI systems that operate physical equipment. Universal Robots and Doosan are launch partners, next to lab-automation vendors and several of the best labs in the world.
>
> I have spent the last months building URML, an open language for robot intent. So the obvious question landed on my desk the same day: what is URML for, if MHS exists?
>
> **Two different questions**
>
> MHS answers: how does an agent find this device, what can it do, and what will it refuse when asked? Those are per-device, per-call questions, and putting the answers in a file the vendor writes is exactly right.
>
> URML answers a different one: is this whole program admissible on this hardware, in this deployment, before the first call goes out? A URML program is checked in five passes against the robot's capability manifest and a deployment envelope. A per-call limit at the device catches the fifth action of a bad plan. A program check refuses the plan.
>
> The second difference matters more in practice than it sounds. A device's limits are not a deployment's limits. A vendor says the arm may move at 1 m/s. A lab says that in this room, next to these people, it moves at 0.3. MHS puts the device's limits in the device file, which is where they belong. URML keeps the deployment's limits in a separate envelope, and the validator applies the stricter of the two. One artifact cannot express that a site owner is more conservative than a vendor. Two can.
>
> **Where URML sits**
>
> URML's manifesto has said since the first commit that its hardware layer extends existing description standards rather than reinventing them. MHS is another such standard, and I treat it the way I treat URDF: a source the capability manifest derives from, and a substrate the validated program dispatches to. URML already ships adapters for two of the MHS partners and an OPC UA runtime whose intent-to-node mapping is the closest existing cousin of intent-to-read/write.
>
> So this is not a contest. MHS is the driver. URML is the language above it, with the check in between.
>
> **The gate Anthropic named, and what I built for it**
>
> Anthropic said the standard opens after safety evaluations exist. That is what URML has been building toward: static validation, envelope enforcement at runtime, a rehearsal gate that rolls a program out in simulation before real execution, a conformance suite, and evidence tags on every capability claim.
>
> This week I packaged that into an evaluation harness. It takes a corpus of agent intents against a lab cell shaped like the assay in Anthropic's own post (a liquid handler, a robotic arm, a plate reader) and a deployment envelope, and reports which intents are refused and why, in machine-readable codes: a grasp above the gripper's force, a move to a location the cell never declared, a measurement on an instrument that is not there, a flight command on an arm. For every accepted program it reports the envelope-monitor verdict over the rehearsed trace. It measures whether an agent's intent is admissible on declared hardware under a declared envelope. It does not measure physics, and the README says so in its first paragraph.
>
> It runs offline, with no model and no device, in a few seconds. Apache 2.0, like everything else in the project.
>
> **What I am not claiming**
>
> I have not seen the MHS specification. Nothing in URML claims compatibility with it, and nothing in the manifest schema has been bent toward a format I have not read. When the standard is open, two pieces follow: an importer that reads a reference file into a manifest, and an adapter that dispatches URML programs through MHS read and write, so every MHS device becomes a URML target through one adapter. Until then there is a scaffold with a placeholder transport, labeled as such.
>
> I applied to the research preview. If you are one of the partners, or you run a lab about to hand an agent a pipetting robot, the harness is the thing to try first.
>
> Harness: https://github.com/URML-MARS/URML/tree/main/examples/physical-ai-safety-eval
> Where URML sits, with the mapping table: https://github.com/URML-MARS/URML/blob/main/docs/integrations/model-hardware-standard.md
> Original post: https://urml.dev/blog/mhs-and-urml/

### 4.4 Show HN (founder posts; title + first comment)

Title: `Show HN: URML, a safety-evaluation harness for AI agents operating lab and factory hardware`
URL: the harness README (not the blog).

First comment:
> Author here. Anthropic previewed a hardware standard (MHS) this week and said it opens once safety evaluations for AI operating physical equipment exist. This is one. It takes a corpus of agent intents against a lab-cell manifest (liquid handler, plate arm, plate reader) and a deployment envelope, validates each whole program, and reports refusals with machine-readable codes, the envelope-monitor verdict over a rehearsed trace for every accepted one, and the evidence class of every limit a refusal relied on.
>
> What it does not do: physics. It judges declared limits and intent coherence; the evidence tag says how much to trust each declaration. Honest status: URML has one external adopter running it on a real robot (a GoPiGo3), and we have not seen the MHS spec, so nothing here claims compatibility. Apache 2.0, runs offline in a few seconds. Happy to take the hard questions.

### 4.5 ROS Discourse (General; founder posts)

> **Where does an intent-validation layer sit relative to Anthropic's Model Hardware Standard and to ROS 2?**
>
> Anthropic previewed MHS this week: a driver standard (read/write, discovery, a per-device reference file with enforced limits), model-agnostic, MCP-reachable, open-sourced after safety evaluations. I maintain URML, an open intent language whose programs are validated whole against a capability manifest and a deployment envelope before dispatch, with a ROS 2 reference runtime among others.
>
> My read of the layering: MHS is a Layer-0 driver and description standard, like URDF/SDF are description standards, and an intent layer derives its manifest from those and dispatches through them. The positioning doc and a mapping table are here: <positioning link>. The one question I would value this community's view on: which ROS 2 device-description conventions (URDF joint limits, ros2_control interfaces, sensor_msgs field names) should a reference-file-to-manifest mapping respect so that an MHS device and a ROS 2 device describe their limits the same way? Not asking anyone to adopt anything.

### 4.6 Anthropic developer community (Discord/forum channel for MHS or physical AI; founder posts)

> Built the evaluation harness the MHS post described as the gate: a corpus of agent intents against a lab cell like the assay in the announcement, validated whole before dispatch, refusals with machine-readable reasons, envelope verdicts over rehearsed traces, evidence class per limit. Open source, hermetic, runs in seconds: <harness link>. We applied to the preview; happy to build the reference-file importer and an adapter against the real spec.

### 4.7 Warm email: Universal Robots (urrsk; founder sends from greenvh@gmail.com)

> Subject: URML update: your MHS partnership, and where our UR adapter now sits
>
> Hi, a short no-ask update since you reviewed URML's UR mapping back in May. UR is a named partner in Anthropic's Model Hardware Standard preview. URML's posture is to sit above MHS: the UR adapter keeps dispatching through RTDE, and when the MHS spec is open it gains MHS as a second transport, while the validator keeps checking the whole program against the manifest and the site envelope before the first call. Your earlier points (generation-agnostic RTDE, no hardcoded clock rates, the manifest stating which clock is authoritative) all carried into RFC-0015/0016 and still hold. Positioning: <positioning link>. If any of it misreads UR's view of MHS, I would rather fix it than leave it wrong.

### 4.8 Warm email: OPC Foundation (marcschier; founder sends)

> Subject: MHS and the OPC UA Robotics CS, a question only you can answer well
>
> Hi Marc, following our thread on the Robotics CS libraries. Anthropic's Model Hardware Standard puts a per-device reference file (measures, adjustable, enforced limits) and read/write primitives at the driver layer. URML intends to map both an MHS reference file and the Robotics CS into the same capability manifest and dispatch through either. The question: how do you see MHS relating to the Robotics CS and the control-API standardization you mentioned, overlap, layering, or neither? No ask beyond your read. Positioning doc: <positioning link>.

### 4.9 Zivid (Espen): one paragraph added to the RFC-0682 email already drafted in section 3

> One more thing since I wrote the above: Anthropic's Model Hardware Standard preview puts a per-device reference file at the driver layer. A 3D camera is exactly that kind of device, and the point-cloud and mount fields we just shipped are the ones such a file would carry. When the spec is open, URML will read those files into manifests the way we read URDF.

### 4.10 Press follow-up (founder emails the Bloomberg and CNBC reporters; after HN)

> Subject: The open-source validation layer above Anthropic's MHS
>
> You covered Anthropic's Model Hardware Standard this week. One angle you may find useful: Anthropic said the standard opens once safety evaluations for AI operating physical equipment exist. An open-source project, URML, shipped exactly that harness today: an agent's whole plan checked against the equipment's declared limits and the site's stricter envelope before the first command, with machine-readable reasons for every refusal. It sits above MHS rather than competing with it. Blog: <blog link>. Harness: <harness link>. Happy to answer questions or give a quote. Ido Yahalomi, maintainer.

### 4.11 X (optional)

> Anthropic's MHS tells an agent what a device is and what it refuses per call. URML checks the whole plan before the first call, and lets the lab be stricter than the vendor. We built the safety-eval harness their preview says it needs: <blog link>

### 4.12 ROSCon UK abstract, one added sentence (docs/launch/roscon-uk-2026-lightning.md)

> The demo now includes the validator refusing an out-of-limit action against a device manifest shaped like Anthropic's Model Hardware Standard reference file.

### 4.13 AWS Strands Agents integration (contribution-first, week 2, founder OK before posting)

Build a `urml_validate` tool for Strands agents (github.com/strands-agents), open a PR or issue upstream with the harness as the worked example. Ledger row on send.

### 4.14 LeRobot #3655 (optional, founder decides)

> Since this proposal: an evaluation harness for agents on physical equipment now exists (<harness link>); the BYOP wrapper proposed here would be judged by it. No ask.

