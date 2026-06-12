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

# Move #22 research: the communication layer

Move #22 targets the communication surfaces URML has not yet engaged. A coverage check first ruled out what is already done, so this wave does not duplicate prior moves:

- **DDS / transport spine** is Move #16 (Fast DDS, Cyclone DDS, Zenoh, iceoryx, MAVLink, DroneCAN, ROS 2 core).
- **Fleet interop** is Move #21 (VDA5050, InOrbit / MassRobotics, openTCS) and Move #2 (Open-RMF).
- **Agent comms** is RFC-0048 (Anthropic MCP + Agent Skills).
- **Speech / dialogue** is largely Move #12 (Whisper family, Piper / piper1-gpl, Porcupine, openVoice). Vosk and Silero were **deliberately excluded** there as Russia-domiciled under URML's US-alignment posture; that exclusion stands and is not revisited here.

What remains uncovered sits in four slices. The pitch is constant: URML composes **above** each communication surface as the plain-language intent layer; it never embeds into or forks the transport. Surfaces verified 2026-06-01 via the GitHub API.

## Slice 1 — Web / teleop / visualization bridges

How operators, browsers, and UIs talk to a robot. The cleanest gap, and a natural fit for URML's English-to-intent front door.

| Repo | License | Stars | Issues | Archived | Notes |
|---|---|---|---|---|---|
| `RobotWebTools/rosbridge_suite` | BSD-3 | ~1.2k | yes (+Disc) | no | Lead. The canonical websocket bridge; URML intent rides over it. |
| `RobotWebTools/webrtc_ros` | Other (clarify) | ~183 | yes | no | Teleop streams over WebRTC; last push 2024-07 (staleness noted). |

Dropped: `foxglove/ws-protocol`, `foxglove/studio` (archived / relicensed-closed), `RobotWebTools/ros2-web-bridge` (archived 2022), `web_video_server` (video transport, not intent; cross-cite only).

## Slice 2 — Alternative transports / messaging

Pub/sub and message-passing beyond the Move #16 DDS spine.

| Repo | License | Stars | Issues | Archived | Notes |
|---|---|---|---|---|---|
| `micro-ROS/micro_ros_setup` | Apache-2.0 | ~494 | yes (+Disc) | no | Lead. Extends the DDS spine to MCUs; cross-cites eProsima `Micro-XRCE-DDS` (already engaged via Fast DDS, Move #16). |
| `eclipse-ecal/ecal` | Apache-2.0 | ~1k | yes (+Disc) | no | Automotive/robotics pub-sub; clean license. |
| `lcm-proj/lcm` | LGPL-2.1 | ~1.2k | yes | no | Robotics-native message passing; IPC-boundary integration (no vendoring). |
| `eclipse-mosquitto/mosquitto` | EPL/EDL | ~10.9k | yes | no | MQTT broker; pairs with VDA5050-over-MQTT (RFC-0297). |
| `emqx/emqx` | **BSL** (friction) | ~16k | yes (+Disc) | no | MQTT broker; CN-domiciled (EMQ). BSL stated honestly; client-boundary only. |

## Slice 3 — Industrial / OPC UA

On-manifesto: "OPC UA Robotics" is a named URML substrate, not yet engaged.

| Repo | License | Stars | Issues | Archived | Notes |
|---|---|---|---|---|---|
| `open62541/open62541` | MPL-2.0 | ~3.1k | yes | no | Lead engineering target; the open C OPC UA stack. |
| `OPCFoundation/UA-.NETStandard` | MIT | ~2.3k | yes (+Disc) | no | The OPC Foundation reference stack; highest standards-body leverage. |
| `eclipse-milo/milo` | EPL-2.0 | ~1.4k | yes (+Disc) | no | Java OPC UA; Eclipse, like Cyclone/iceoryx. |
| `FreeOpcUa/opcua-asyncio` | LGPL-3.0 | ~1.4k | yes (+Disc) | no | Python OPC UA; matches URML's tooling language. |

`node-opcua/node-opcua` (MIT) held as optional breadth, not in this batch.

## Slice 4 — Human-robot dialogue (only the net-new remainder)

Move #12 covered STT/TTS/wake-word; only two surfaces are genuinely new.

| Repo | License | Stars | Issues | Archived | Notes |
|---|---|---|---|---|---|
| `dscripka/openWakeWord` | Apache-2.0 | ~2.3k | yes (+Disc) | no | Open wake-word engine; the open alternative to Porcupine (RFC-0165, commercial-SDK friction). |
| `RasaHQ/rasa` | Apache-2.0 | ~21k | yes | no | Dialogue-management framework; a layer above Move #12's STT/TTS. |

Excluded / do-not-repitch: Whisper family, Piper/piper1-gpl, Porcupine, openVoice (Move #12); Vosk, Silero, Coqui (Russia-domiciled / dead upstream).

## Wave shape

Full wave: 13 Outreach RFCs (0306-0318), all `response: none` until posted. License frictions (EMQX BSL, LCM/opcua-asyncio LGPL, milo/mosquitto EPL) are stated in-RFC and resolved by the same client/IPC-boundary integration shape URML uses everywhere: URML maps intent to the surface's public interface and never vendors copyleft code.
