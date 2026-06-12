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

# Move #22 post bodies: communication-layer wave

Copy-paste-ready bodies for the 13 Move #22 targets across four slices (web/teleop bridges, alt transports, OPC UA, dialogue). Bodies follow the [AGENTS.md](../../AGENTS.md) outreach-post-structure rules: concrete hook first, one or two real questions, light ask up front, full RFC linked as optional depth, under a two-minute read, zero em-dashes. The VIBE disclosure line goes last in every body.

Every body frames URML as composing **above** the communication surface, never embedding it. License frictions (EMQX BSL, LCM/opcua-asyncio LGPL) are stated up front in those bodies.

**Posting status:** all DRAFT. Founder posts under `idoco2003` after the RFCs land on `main` (so the write-up links resolve); then record `posted_url` + flip `last_touch` in `outreach-move22.yaml`.

**Routing summary**

| RFC | Target | Repo | Channel |
|---|---|---|---|
| 0306 | rosbridge_suite | RobotWebTools/rosbridge_suite | Issue / Ideas Discussion |
| 0307 | webrtc_ros | RobotWebTools/webrtc_ros | Issue (license ask) |
| 0308 | micro-ROS | micro-ROS/micro_ros_setup | Issue / Ideas Discussion |
| 0309 | eCAL | eclipse-ecal/ecal | Issue / Discussion |
| 0310 | LCM | lcm-proj/lcm | Issue (LGPL boundary) |
| 0311 | Mosquitto | eclipse-mosquitto/mosquitto | Issue |
| 0312 | EMQX | emqx/emqx | Issue / Discussion (BSL note) |
| 0313 | open62541 | open62541/open62541 | Issue |
| 0314 | UA-.NETStandard | OPCFoundation/UA-.NETStandard | Issue / Discussion |
| 0315 | Eclipse Milo | eclipse-milo/milo | Issue / Discussion |
| 0316 | opcua-asyncio | FreeOpcUa/opcua-asyncio | Issue / Discussion (LGPL) |
| 0317 | openWakeWord | dscripka/openWakeWord | Issue / Ideas Discussion |
| 0318 | Rasa | RasaHQ/rasa | Issue |

The disclosure line, used verbatim at the end of every body below:

> *AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

## RFC-0306: rosbridge_suite

**Post to:** https://github.com/RobotWebTools/rosbridge_suite/issues/new
**Title:** URML (open robot intent language): a validated producer of rosbridge messages

```
Hi RobotWebTools team,

URML (urml.dev) is a small open language (Apache-2.0) for robot intent. A user writes an English sentence, URML turns it into a primitive, validates it against the robot's declared capabilities, and only then dispatches it. The most common way a browser reaches a ROS robot is rosbridge over a websocket, so URML's natural output is exactly a rosbridge publish / call_service message. Nothing for you to change or maintain; this is a request for comment on the producer relationship.

One real question: would deriving a URML capability manifest from a rosbridge advertised-type list be useful, and at what grain (topics/services, or full types)? URML validates before anything moves, which feels like the right property for a web-facing bridge.

Full write-up if useful: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0306-rosbridge-suite-outreach.md

Thanks for keeping the robot web stack open.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0307: webrtc_ros

**Post to:** https://github.com/RobotWebTools/webrtc_ros/issues/new
**Title:** URML (open robot intent language): validated intent on the WebRTC data channel + a license question

```
Hi RobotWebTools team,

URML (urml.dev) is a small open language (Apache-2.0) for robot intent: English in, a validated primitive out, dispatched only after it is checked against the robot's real capabilities. For teleoperation over webrtc_ros, the interesting surface is the data channel: a validated URML command can ride it alongside the video, so a remote operator on a laggy link cannot send something the robot cannot safely do.

Two things. First, a practical question: webrtc_ros shows license "other" on GitHub, so could you confirm the license? I want to describe the integration boundary correctly. Second, is a validated-intent data-channel producer for teleop interesting, or out of scope?

Full write-up if useful: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0307-webrtc-ros-outreach.md

Thanks for the open WebRTC teleop work.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0308: micro-ROS

**Post to:** https://github.com/micro-ROS/micro_ros_setup/issues/new
**Title:** URML (open robot intent language): a plain-language layer down to the MCU tier

```
Hi micro-ROS team,

URML (urml.dev) is a small open language (Apache-2.0) for robot intent: an English sentence becomes a validated primitive that is checked against the robot's capabilities before dispatch. URML already has a micro-class robot story (a micro:bit-class manifest and a conservative educational profile); micro-ROS is the substrate that would actually carry that intent onto a real MCU agent. It also extends the same engagement we have at the full DDS layer (Fast DDS, Cyclone DDS) one tier down.

One real question: what grain should a URML manifest use to declare the MCU-tier substrate, just naming micro-ROS, or the agent topology and micro-XRCE-DDS transport?

Full write-up if useful: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0308-micro-ros-outreach.md

Thanks for bringing ROS 2 to microcontrollers.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0309: eCAL

**Post to:** https://github.com/eclipse-ecal/ecal/issues/new
**Title:** URML (open robot intent language): validated intent published on eCAL

```
Hi eCAL team,

URML (urml.dev) is a small open language (Apache-2.0) for robot intent: English in, a validated primitive out, dispatched only after a capability check. URML is substrate-neutral, so eCAL is a first-class transport for it, not a special case: a validated URML intent publishes on an eCAL topic exactly as it would on DDS. Apache-2.0 on both sides, nothing for you to maintain.

One real question: what grain is most useful for a URML manifest to declare eCAL as the deployment transport, and could it align with the eCAL monitoring/registry view of topics and types?

Full write-up if useful: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0309-ecal-outreach.md

Thanks for the open pub/sub work.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0310: LCM

**Post to:** https://github.com/lcm-proj/lcm/issues/new
**Title:** URML (open robot intent language): validated intent on an LCM channel

```
Hi LCM maintainers,

URML (urml.dev) is a small open language (Apache-2.0) for robot intent: English in, a validated primitive out, dispatched after a capability check. URML is transport-neutral, and LCM is a clean example beyond DDS: a validated URML intent serializes onto an LCM channel. To be clear up front, LCM is LGPL-2.1, so any URML use stays at the library boundary; URML never vendors LCM into its tree.

One real question: what grain should a URML manifest use to declare LCM as the transport (channel namespace, type package)?

Full write-up if useful: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0310-lcm-outreach.md

Thanks for keeping LCM going.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0311: Mosquitto

**Post to:** https://github.com/eclipse-mosquitto/mosquitto/issues/new
**Title:** URML (open robot intent language): an MQTT-client producer of validated intent

```
Hi Mosquitto team,

URML (urml.dev) is a small open language (Apache-2.0) for robot intent: English in, a validated primitive out, dispatched after a capability check. A lot of fleet robotics moves over MQTT, and URML already emits VDA5050 orders over an MQTT broker in its warehouse work; this is just making the broker layer explicit. URML is an ordinary MQTT client above Mosquitto, nothing to change on your side.

One real question: what grain should a URML manifest use to declare an MQTT deployment, just topic namespace and QoS, or also retained / last-will details?

Full write-up if useful: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0311-mosquitto-outreach.md

Thanks for the reference open broker.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0312: EMQX

**Post to:** https://github.com/emqx/emqx/issues/new
**Title:** URML (open robot intent language): an MQTT-client producer for clustered deployments

```
Hi EMQX team,

URML (urml.dev) is a small open language (Apache-2.0) for robot intent: English in, a validated primitive out, dispatched after a capability check. When an MQTT fleet deployment needs clustering and scale, EMQX is the broker; URML's relationship is the same as with any broker: a validated intent published as an MQTT message, broker untouched. To be transparent, I note that EMQX's platform is under a Business Source License and the integration is strictly an at-arms-length MQTT client, so it never embeds or redistributes EMQX.

One real question: what grain should a URML manifest use to declare a clustered MQTT deployment (cluster endpoint, topic namespace, QoS)?

Full write-up if useful: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0312-emqx-outreach.md

Thanks for the high-scale open broker.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0313: open62541

**Post to:** https://github.com/open62541/open62541/issues/new
**Title:** URML (open robot intent language): mapping validated intent onto OPC UA

```
Hi open62541 team,

URML (urml.dev) is a small open language (Apache-2.0) for robot intent: English in, a validated primitive out, dispatched after a capability check. OPC UA is named as a target substrate in URML's design, and open62541 is the cleanest open stack to map onto: a validated URML intent becomes an OPC UA method call or variable write against a server's address space. MPL-2.0 on your side composes fine with URML's Apache-2.0. This is URML's first OPC UA engagement and a request for comment.

One real question: what grain should a URML manifest use to map onto an address space, importing a nodeset, or a declared method/variable subset?

Full write-up if useful: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0313-open62541-outreach.md

Thanks for the open OPC UA stack.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0314: UA-.NETStandard (OPC Foundation)

**Post to:** https://github.com/OPCFoundation/UA-.NETStandard/issues/new
**Title:** URML (open robot intent language): a mapping to the OPC UA Robotics companion spec

```
Hi OPC Foundation maintainers,

URML (urml.dev) is a small open language (Apache-2.0) for robot intent: English in, a validated primitive out, dispatched after a capability check. URML's design names OPC UA Robotics as a target substrate, and the most useful conversation is with the body that stewards that companion spec. URML would map validated intent onto OPC UA services; it does not embed or redistribute the reference stack, keeping the relationship at the protocol boundary.

Two questions: is the OPC UA Robotics companion nodeset the right thing for a URML manifest to target, and is the GitHub repo the right channel or should this go to a working group?

Full write-up if useful: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0314-ua-dotnet-standard-outreach.md

Thanks for the OPC UA reference work.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0315: Eclipse Milo

**Post to:** https://github.com/eclipse-milo/milo/issues/new
**Title:** URML (open robot intent language): OPC UA mapping for the JVM

```
Hi Eclipse Milo team,

URML (urml.dev) is a small open language (Apache-2.0) for robot intent: English in, a validated primitive out, dispatched after a capability check. URML is engaging OPC UA across implementations so the mapping is validated where integrators actually work; Milo is the JVM stack. A validated URML intent maps onto an OPC UA method call or write through a Milo client. Nothing for you to maintain; a request for comment.

One real question: what grain should a URML manifest use to map onto an address space via Milo (nodeset import, method/variable subset)?

Full write-up if useful: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0315-eclipse-milo-outreach.md

Thanks for the open Java OPC UA stack.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0316: opcua-asyncio (FreeOpcUa)

**Post to:** https://github.com/FreeOpcUa/opcua-asyncio/issues/new
**Title:** URML (open robot intent language): a Python OPC UA prototype path

```
Hi FreeOpcUa maintainers,

URML (urml.dev) is a small open language (Apache-2.0) for robot intent: English in, a validated primitive out, dispatched after a capability check. URML's validator and tooling are Python, so opcua-asyncio is the most direct path from URML to a real OPC UA server: a validated intent becomes an async OPC UA call_method / write. LGPL-3.0 means any URML adapter uses opcua-asyncio at the library boundary and does not vendor it.

One real question: would a URML OPC UA adapter prototype built on opcua-asyncio be welcome to reference, and what grain should the manifest mapping use?

Full write-up if useful: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0316-opcua-asyncio-outreach.md

Thanks for the actively maintained Python OPC UA stack.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0317: openWakeWord

**Post to:** https://github.com/dscripka/openWakeWord/issues/new
**Title:** URML (open robot intent language): wake-word as the front gate of spoken intent

```
Hi openWakeWord maintainers,

URML (urml.dev) is a small open language (Apache-2.0) for robot intent: an English sentence becomes a validated primitive, checked against the robot's capabilities before dispatch. A wake word is the always-on front gate of that spoken loop, and openWakeWord fits URML's offline, no-account, no-API-key posture far better than a commercial SDK (URML's classroom lesson runs fully on-device). A detection event would simply gate when URML starts capturing an instruction.

One real question: what grain should a URML manifest use to declare a wake-word front gate, model id plus a confidence threshold, or more?

Full write-up if useful: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0317-openwakeword-outreach.md

Thanks for the open wake-word work.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0318: Rasa

**Post to:** https://github.com/RasaHQ/rasa/issues/new
**Title:** URML (open robot intent language): a custom-action target for safe robot dispatch

```
Hi Rasa team,

URML (urml.dev) is a small open language (Apache-2.0) for robot intent. It is not a dialogue manager and does not overlap Rasa; it is the opposite end of the pipe. Rasa decides what the user wants across a conversation; URML takes a decided action, validates it against the robot's real capabilities, and dispatches it safely. A Rasa custom action that emits a validated URML program lets Rasa own the conversation and URML own the safe robot dispatch, and a URML validation failure becomes a clean Rasa fallback ("I can't do that here, because ...").

One real question: does that division (Rasa owns dialogue state, URML owns validated robot dispatch) match how you would expect robotics users to wire Rasa to a robot?

Full write-up if useful: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0318-rasa-outreach.md

Thanks for the open dialogue framework.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```
