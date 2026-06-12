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

# Move #40 post bodies: the developer-tooling / observability wave

Six targets. Post under idoco2003 via the channel noted per row (Discussion or
Issue). No license-ask (all permissive). AI-assisted-authoring disclosure up
front. At post time, query each Discussion repo's real category id (Move #30
procedure) for the four Discussion targets.

---

## RFC-0463: Lichtblick

**Post to (Discussion):** https://github.com/lichtblick-suite/lichtblick/discussions/new?category=ideas
**Title:** URML (open robot intent language): visualizing a validated-intent audit stream in Lichtblick — request for comment

```
Hi Lichtblick community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: a person writes a sentence, URML turns it into a typed primitive, validates it against the robot's declared capabilities and a safety envelope, then dispatches. I'm not writing about a substrate — I'm writing because URML produces a structured audit record on every step, and Lichtblick is exactly the kind of tool that could make it legible: the intent, which of the five validator passes ran and their verdicts, and the substrate calls that followed.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

A URML runtime emits one audit event per step: the typed intent, the validation verdict (and the failing pass + error code when a request is refused), and the dispatched calls. That is a clean time-series + event stream a Lichtblick data-source plugin could ingest, so a panel could show "intent -> validated -> dispatched" right next to the pose and sensor panels — the why-it-did-that beside the what-it-did. A refused intent (out-of-capability, out-of-envelope) becomes a first-class, explained event. This is the same shape as URML's engagement with NASA's Open MCT: URML's audit/envelope state as a telemetry source, not a substrate claim.

Two real questions: (1) Is URML's validated-intent audit stream a useful data source / panel for Lichtblick? (2) What is the cleanest seam — a custom data-source plugin, an MCAP recording, or a live foxglove-protocol stream — and what fields would a "validated intent" panel want (intent, pass/verdict, substrate call, timing)?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0463-lichtblick-outreach.md

Thanks for Lichtblick; an open, actively-developed robotics viz platform is exactly where this kind of integration should be designed with input.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0464: Rerun

**Post to (Discussion):** https://github.com/rerun-io/rerun/discussions/new?category=ideas
**Title:** URML (open robot intent language): logging a validated-intent stream to a Rerun timeline — request for comment

```
Hi Rerun community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. I'm writing because URML produces a structured, timestamped audit record on every step, and Rerun's time-aligned multimodal model looks like a natural home for it next to the poses, images, and point clouds you already log.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

A URML runtime logs one entity per step: the typed intent, the validation verdict (and the failing pass + error code when refused), and the dispatched substrate calls. "What was intended, whether it was allowed, what was sent" sits cleanly on a Rerun timeline beside sensor data, and a refused intent (out-of-capability, out-of-envelope) becomes a first-class timeline event — making validate-before-actuate legible in replay.

Two real questions: (1) Is URML's validated-intent audit stream a useful thing to log to a Rerun timeline? (2) What's the idiomatic Rerun shape for "intent + verdict + dispatch" events (a custom archetype, scalars + text, a structured log) — and is there interest in a small reference logger that emits URML audit records as Rerun entities?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0464-rerun-outreach.md

Thanks for Rerun; a fast multimodal timeline is a great place to make validated intent visible alongside everything else a robot logs.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0465: PlotJuggler

**Post to (Discussion):** https://github.com/PlotJuggler/PlotJuggler/discussions/new?category=ideas
**Title:** URML (open robot intent language): plotting validated-intent / envelope-margin series in PlotJuggler — request for comment

```
Hi PlotJuggler community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. I'm writing because that validation produces timestamped numbers PlotJuggler is built to plot: per-step verdicts, dispatch timing, and — the interesting one — envelope margins, how close each command ran to its declared limit.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

A URML runtime can expose timestamped series a PlotJuggler streaming plugin consumes: per-step validation verdict (accepted/refused), the failing pass when refused, dispatch latency, and envelope margins (commanded vs. declared max velocity, grip force, altitude). Plotting "how close each command ran to its declared envelope" turns validate-before-actuate into a quantitative, reviewable trace.

Two real questions: (1) Is URML's validated-intent / envelope-margin stream a useful streaming source for PlotJuggler? (2) Is a custom streaming plugin the right seam, or is replaying a recorded log (CSV / MCAP) the cleaner first step — and what scalar/event shape would a "validated intent" series want?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0465-plotjuggler-outreach.md

Thanks for PlotJuggler; a fast, plugin-friendly time-series tool is the natural place to make envelope margins reviewable.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0466: MCAP

**Post to (Discussion):** https://github.com/foxglove/mcap/discussions/new?category=ideas
**Title:** URML (open robot intent language): recording a validated-intent audit trail as an MCAP channel — request for comment

```
Hi MCAP community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. I'm writing because URML produces a structured audit record on every step, and recording it as a first-class MCAP channel would make it replayable, diffable, and visualizable in any MCAP-aware tool — rather than tied to one viewer.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

A URML runtime writes one MCAP channel of audit messages: per step, the typed intent, the validator verdict (failing pass + error code when refused), and the dispatched substrate calls, each with a log time. Because MCAP is serialization-agnostic, the audit schema can be JSON Schema (the same program/manifest schemas URML already exports) or protobuf — no new format invented. A recorded .mcap then opens directly in Lichtblick or any MCAP reader, so the validated-intent stream is portable across the whole ecosystem. (The Foxglove SDK is the natural live-streaming complement; this is about MCAP as the on-disk format.)

Two real questions: (1) Is recording URML's validated-intent audit trail as a dedicated MCAP channel the right pattern (schema-encoded messages on their own channel)? (2) Should the audit schema be advertised as JSON Schema or protobuf for best cross-tool support, and are there conventions for an "intent + verdict" channel that would make it idiomatic for MCAP readers?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0466-mcap-outreach.md

Thanks for MCAP; a serialization-agnostic open logging format is exactly the right place to make a validated-intent trail portable.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0467: rosboard

**Post to (Issue):** https://github.com/dheera/rosboard/issues/new
**Title:** URML (open robot intent language): a glanceable validated-intent tile for rosboard — request for comment

```
Hi rosboard community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. I'm writing because rosboard is the lowest-friction way to watch a robot from a phone or laptop, and URML's validated-intent stream (intent -> verdict -> dispatch) is exactly the kind of human-legible signal a glanceable dashboard wants.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

A URML runtime publishes its audit records on a topic; rosboard could render them as a live panel: the current intent, whether it validated, and what was dispatched — readable at a glance next to the usual topic tiles. A refused intent (out-of-capability or out-of-envelope) becomes a visible, explained event rather than a silent non-action.

Two real questions: (1) Is a "validated intent" panel (intent / verdict / dispatch) a useful addition to rosboard's topic tiles? (2) Is publishing audit records on a ROS topic the right seam, or a dedicated rosboard data type — and what would a glanceable validated-intent tile most want to show?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0467-rosboard-outreach.md

Thanks for rosboard; a no-install web dashboard is a great place to surface why a robot did (or didn't) act.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0468: rviz_visual_tools

**Post to (Issue):** https://github.com/PickNikRobotics/rviz_visual_tools/issues/new
**Title:** URML (open robot intent language): drawing validated intent + envelope with rviz_visual_tools — request for comment

```
Hi rviz_visual_tools / PickNik community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. I'm writing because a validated intent and its declared safety envelope are spatial — a target pose, a workspace bound, a geofence, a no-go region, a planned trajectory — and rviz_visual_tools is the standard way to render exactly those as markers next to the robot.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

A URML runtime could use rviz_visual_tools to draw what it just validated: the target pose of a move_to, the declared workspace bounds, a geofence polygon, the planned trajectory of a plan_path — the spatial side of the audit trail. A refused intent could be drawn distinctly (the out-of-envelope pose in red), making validate-before-actuate visible in the same RViz scene as the robot. (We also engaged PickNik's abb_ros2 in the arm-driver wave; this is a separate, visualization-side thought.)

Two real questions: (1) Is drawing a validated intent's target/envelope (pose, workspace bound, geofence, trajectory) a natural use of rviz_visual_tools? (2) Are the existing marker primitives sufficient, or would a small "intent/envelope" helper layer be worth it, and any conventions for distinguishing accepted vs. refused intent visually?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0468-rviz-visual-tools-outreach.md

Thanks for rviz_visual_tools; a clean marker API is the natural place to make a robot's intended-and-allowed envelope visible.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```
