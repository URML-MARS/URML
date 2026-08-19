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

# ROSCon UK 2026 lightning talk (draft for founder submission)

- **Event**: ROSCon UK 2026, Edinburgh, 21-23 October 2026 (https://roscon.org.uk/2026/)
- **Submission**: lightning talks via EasyChair (https://easychair.org/cfp/rosconuk2026), deadline **14 October 2026, 23:59 BST**. Founder submits and presents.
- **Format**: 3 minutes. Live demo on a laptop; robot motion shown on the hermetic mock trace (honest and projector-friendly) with hardware as a stretch goal.

## Title

One spoken sentence, one validated program, zero cloud

## Abstract (~150 words, paste into EasyChair)

URML (urml.dev) is an Apache-2.0 intent language that sits above ROS 2 and other substrates. A language model turns a plain sentence into a small YAML program, and a five-pass validator checks that program against the robot's declared capability manifest and safety envelope before anything actuates. A 250 N grasp on a 100 N gripper is refused on paper, not attempted on hardware.

In three minutes, live on one laptop with no cloud anywhere: speak a sentence into a microphone, watch whisper.cpp transcribe it and a local LLM emit URML, watch the validator reject an over-limit variant with a machine-readable reason, then watch the accepted program execute as a step-by-step trace. The interesting part is not the LLM. It is the boundary: models may be wrong, declarations are checkable, and nothing moves without passing the check. Everything shown is open source and reproducible from the repository.

## Demo run-of-show (3:00)

1. 0:00-0:20. One slide: the layer picture (sentence above, ROS 2 below, validator between).
2. 0:20-1:00. `urml translate --audio` with a live-recorded sentence; whisper-server transcript echoes on screen; local LLM (Ollama) emits the program.
3. 1:00-1:50. The money moment: the "drive at full speed" variant is refused (envelope cap, named error code); the corrected sentence validates.
4. 1:50-2:40. `urml run` executes the accepted program on the hermetic mock; the audit trail scrolls. One sentence on the rehearsal gate.
5. 2:40-3:00. Close: Apache 2.0, conformance suite, urml.dev. QR code.

Fallback discipline: every live step has a pre-recorded terminal capture on the
same slide deck; the demo gods get no vote. All output shown must be real
`urml` output (hero-SVG discipline applies to slides too).
