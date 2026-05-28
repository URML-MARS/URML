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

# Move #9 post bodies

Copy-paste-ready Discussion / Issue / Contact-form bodies for the Move #9 NASA-robotics outreach. Wave shape: three Tier A vendor-style targets identified via a verified 2026-05-27 shortlist — `nasa-jpl/rosa` (NL-driven ROS agent), `nasa/fprime` (flight-software framework with ROS 2 bridge), `nasa/astrobee` (ISS free-flyer). Sequencing: lead with ROSA alone, let it land before F Prime + Astrobee bodies are drafted.

Ledger state lives in [`outreach-move9.yaml`](outreach-move9.yaml). After posting, set `posted_url`, update `last_touch`, and update `next_action`.

Voice: founder posts under his GitHub identity. Each post opens with "Hi <team>" and addresses the maintainers directly.

**Confidentiality discipline.** Per the outreach-confidentiality rule, public post bodies do NOT name or link to previously engaged URML maintainers as social proof. URML's own shipped artifacts (`reference/llm-bridge/`, `reference/ros2-runtime/`, `reference/isaac-runtime/`, RFCs in `docs/rfcs/`) are fine to cite. Aggregate counts ("nine outreach waves across URML's outreach") are fine. Naming the specific orgs that responded is not.

**Authoring disclosure.** Per [`AGENTS.md`](../../AGENTS.md) line 67 + [`VIBE.md`](../../VIBE.md), every Move #9 post ends with the one-paragraph authoring-disclosure line. Origin: 2026-05-26 OVOS RFC-0107 wontfix close; URML's response is to disclose openly, not to retreat. The disclosure paragraph is reproduced verbatim at the bottom of each post body below.

---

## RFC-0108: NASA-JPL ROSA

**Post to:** https://github.com/nasa-jpl/rosa/discussions/new?category=ideas (Discussions surface; CONTRIBUTING.md names Discussions as the preferred design-discussion channel)

**Title:**

```
Proposal: URML (substrate-neutral robot intent) as a Langchain tool inside ROSA — a typed pre-flight safety check between NL and ROS publish
```

**Body:**

```markdown
Hi @RobRoyce and the ROSA team,

Proposing a Langchain tool that ROSA's agent could register alongside its existing ROS tools, emitting validated URML programs in place of raw `rospy` / `rclpy` calls. [URML](https://urml.dev) (Universal Robot Language, Apache-2.0) is an open spec for substrate-neutral robot intent: a typed primitive vocabulary (`move_to`, `grasp`, `release`, `measure`, `wait_for`, ...) plus a Layer-1 capability manifest and a validator that rejects, before any actuator publishes, any program a manifest cannot honor.

Of every repo URML has surveyed across its outreach, **ROSA's natural-language-to-ROS-tool-call loop is the closest single-repo semantic overlap with URML's reason for existing.** ROSA owns the LLM, the prompt orchestration, the tool registration, and the ROS execution path. URML owns the typed primitive vocabulary, the manifest, and the validator. Plugged together: ROSA's planner emits a URML program via one new tool, URML's validator gates it against the active manifest, the program either executes (via URML's substrate adapter, ROSA's own ROS layer, or both) or returns a typed reason ("manifest declares `gripper: none`") that ROSA's planner can re-plan against. Natural-language interaction plus static safety before publish; neither side gives up its strengths.

This is **proposal-only**, posted as URML's first Move #9 outreach (the NASA-robotics wave, URML's first dedicated NASA engagement). No bridge code in URML's repo yet; the bridge ships engagement-driven, on the precedent set by URML's [Robotical Marty engagement (RFC-0073)](https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0073-robotical-marty-outreach.md). The Langchain tool shape, the URML-vs-ROSA execution-path choice, the manifest-seed pattern, and the alignment with NASA's SLIM framework are observable design points worth your input before any code lands.

Full RFC, with the proposed tool sketch, the URML / ROSA role split, the manifest-seed pattern, and all alternatives considered:
https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0108-nasa-jpl-rosa-outreach.md

Seven questions worth `nasa-jpl/rosa` maintainer input on:

1. **Bridge home.** Should the URML bridge live as (a) an example folder inside `nasa-jpl/rosa`, (b) a separately-maintained `nasa-jpl/rosa-urml-bridge` repo under the same org, or (c) external in `URML-MARS/URML` only? URML's default assumption is (c) until invited otherwise.
2. **Execution path.** Should the bridge return execution to ROSA's existing tool layer (URML as pre-flight check only), or hand off to URML's substrate adapter (URML as execution layer)?
3. **LLM reuse.** Should the bridge reuse ROSA's `llm` parameter for the NL-to-URML translation step (one LLM, two completions per request), or hold a separate LLM handle URML provides?
4. **Manifest seeding.** Does ROSA's planner benefit from URML's compact manifest-seed pattern (50–200 tokens summarizing supported primitives), or is the LLM better served by reading a full URML manifest as plain context like documentation?
5. **IsaacSim extension alignment.** ROSA's IsaacSim extension is flagged as coming soon. Is there a near-term timeline where URML's `reference/isaac-runtime/` could compose with that extension as the URML-side simulation target?
6. **NASA SLIM / governance constraints.** Are there documentation, governance, or process constraints from NASA's SLIM framework (or JPL-specific) that should shape how URML contributes to or cross-cites ROSA?
7. **Conformance lane.** Would the ROSA team consider a README or Wiki link to URML once a working bridge ships, basic tests pass, and an example agent (TurtleSim or similar) demonstrates the loop?

Happy to discuss any of these here, or via a different surface if you'd prefer.

URML is in Phase 1 (open, solo-maintainer); no commercial program. URML will want maintainer and governance participation eventually, not today. Today the ask is the technical critique above.

Thanks for the work that made `nasa-jpl/rosa` available in the first place; it is a real anchor in a field that has not had many.

Ido Yahalomi (URML maintainer, [urml.dev](https://urml.dev), greenvh@gmail.com)

---

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```
