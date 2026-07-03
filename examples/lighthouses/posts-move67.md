# Move #67 posts — newest VLA / robot-LLM residue (4 clean)

Posted under idoco2003 on 2026-07-03. VIBE.md disclosure up front, no license-ask, em-dash-free titles.
RFC-0655 microsoft/VITRA (#41), RFC-0656 RobotControlStack (#316), RFC-0657 daniekpo/verigraph (#2), RFC-0658 airo-ugent/airo-mono (#204).

Context: a focused search of the newest (2026-04+) VLA/robot-model releases, deduped against ~636 prior contacts, with strict origin scrutiny (the search agent mislabeled several PRC repos as US). 4 clean US/allied; the larger remaining volume is PRC open-weight academic (RFC-0003 deferred).

---

## 1. microsoft/VITRA  (RFC-0655)  -> issue #41

**Title:** URML: validating a human-video-pretrained action against the target robot's envelope

(Body: see the ledger comment / RFC-0655. VLA pretrained on human-activity video; what a human demonstrated is not automatically admissible on the target robot; validate the emitted action against the declared envelope.)

## 2. RobotControlStack/robot-control-stack  (RFC-0656)  -> issue #316

**Title:** URML: a capability check at the sim-to-real deploy boundary

(Body: see RFC-0656. Sim-to-real deploy is exactly the validate-before-actuate boundary; validate the policy's commanded action against the real arm's envelope before deployment dispatches it. AGPL-3.0 stated as cross-reference, no code reuse.)

## 3. daniekpo/verigraph  (RFC-0657)  -> issue #2

**Title:** URML: scene verification and capability admissibility as two gates on the same action

(Body: see RFC-0657. Closest conceptual sibling: VeriGraph verifies against the scene (semantic), URML verifies against the robot (capability); the two compose as independent gates. A peer conversation.)

## 4. airo-ugent/airo-mono  (RFC-0658)  -> issue #204

**Title:** URML: a capability check one layer above the manipulation commands

(Body: see RFC-0658. Honest weakest fit: airo-mono is a manipulation library, not a model; URML's value is narrower than for an autonomy layer. Same admissibility check, applied above the library.)

The full verbatim bodies were posted from the scratchpad drafts m67_1..m67_4.md.
