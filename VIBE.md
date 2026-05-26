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

# How URML is authored

**URML is the invention of Ido Yahalomi** ([greenvh@gmail.com](mailto:greenvh@gmail.com)): the language, the layered architecture, the primitive vocabulary, the substrate-neutral framing, the open-core / closed-surround strategy. One human, one design.

The authoring of the spec text, the four reference runtimes, the validator, the conformance suite, and the outreach RFC log is **AI-assisted (vibe-coded)**: drafted with Claude (Anthropic) under the maintainer's direction and review. This is not hidden, not a transitional state, not something a future contributor reorganization will reverse.

URML's stance:

- The invention is human. The keyboarding is shared.
- A solo-maintainer Apache-2.0 project that ships a multi-layer spec, four runtimes, a conformance suite, and ~100 outreach RFCs in a single phase does not exist at this pace without AI assistance. URML chose to exist.
- Every technical claim in the repo is measured by `make audit` against real test runs, real fixture counts, real conformance results. AI prose does not get to bypass the audit.
- Every external-facing post (issues, discussions, RFCs) is read by the maintainer before it ships. AI drafts; the maintainer approves.
- Specs, schemas, and primitive definitions are checked-in artifacts whose correctness is enforced by tests and conformance fixtures, not by the eloquence of the prose around them.

Reviewers who prefer human-only correspondence are welcome to say so. URML will not contest the preference, and will route around the channel. URML will not pretend the prose was hand-typed.

License of the work product is unchanged: Apache 2.0, no CLA, DCO sign-off on every commit. AI-assisted authorship does not affect the legal posture of the contributions.

— Ido Yahalomi
