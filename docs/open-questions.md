# Open Questions

The working list of decisions that are still open. Extends [`MANIFESTO.md`](../MANIFESTO.md) Appendix B. Items move out of this file when an RFC resolves them — the RFC stays as the historical record; the entry here is deleted (the file should always reflect the *current* set of open questions, not the cumulative one).

If you have an opinion or pointers to prior art on any of these, see [`CONTRIBUTING.md`](../CONTRIBUTING.md) §Ways to Engage Today for how to reach the maintainer.

---

## From the Manifesto

These are the six questions Appendix B of the Manifesto explicitly flags. Status as of Phase 0:

### 1. Final name

URML is provisional. Alternatives include CRL (Common Robot Language), RIDL (Robot Intent Description Language), OpenIntent, RoboLingua.

- **Status:** unresolved.
- **Constraints:** must be available as a trademark in at least the US and EU; should be pronounceable in the target audience's working languages; should not pre-decide governance jurisdiction.
- **Plan:** decide before Phase 1 launch, so the public launch ships under the chosen name.

### 2. Serialization

YAML for human readability, JSON-LD for tooling, or both.

- **Status:** **leaning** — both supported, YAML canonical.
- **Open detail:** if both, how does the spec define equivalence between the YAML and JSON-LD encodings of the same program? A small canonicalization rule, or a round-trip tool?
- **Plan:** decide in the layer-3 RFC that defines the surface syntax.

### 3. Versioning scheme

Semver applied per spec layer and profile, or a date-based scheme (URML 2026-Q3) at the project level.

- **Status:** **leaning** — per-artifact semver.
- **Rationale:** spec layers evolve at different paces; the LLM-bridge prompt contract is more volatile than the Layer-1 HAL. Per-artifact semver lets each be stable when it's stable.
- **Plan:** decide in the meta-RFC that defines the release process (post-RFC-0001).

### 4. LLM prompt contract location

In the main spec or in a separate companion document.

- **Status:** **leaning** — separate companion document under `/spec/layer-4-nl-grammar`, referenced from the main spec.
- **Rationale:** the prompt contract will iterate faster than the spec it serves. Decoupling keeps the spec stable.

### 5. First demo robot

TurtleBot 4 (cheapest, widest community), a simulated platform only, or both.

- **Status:** unresolved.
- **Constraints:** the Phase 2 flagship demo must travel virally (Manifesto §Strategic Posture: "demos that travel virally"); a simulated demo is reproducible but less compelling; a physical demo is compelling but harder to reproduce.
- **Lean:** both — the canonical demo runs in simulation (so anyone can re-run it) and a single physical TurtleBot 4 recording ships as a hero video.

### 6. Hebrew localization in v0.1

The author works in Hebrew; the manifesto names Spanish, Japanese, Mandarin as additional v0.1 targets *structurally* (file layout reserves the slots), with English-only as the actual v0.1 content coverage.

- **Status:** **decided** — English-only NL fixtures in v0.1; `/examples/<profile>/scenario.<lang>.txt` reserves `he`, `es`, `ja`, `zh` as sibling files. CLAUDE.md will be updated to reflect actual coverage as fixtures land.

---

## Additional questions surfaced since the Manifesto

### A. RFC numbering across the eventual entity split

The Manifesto anticipates a future split into a non-profit foundation (owning the standard) and a for-profit company (selling adjacent products). Do RFC numbers carry across that boundary, or does the foundation re-base?

- **Status:** unresolved.
- **Lean:** carry across. Re-basing would lose the decision trail that justifies the foundation's existence.

### B. Trademark holding during Phase 0

The Manifesto and [`CLAUDE.md`](../CLAUDE.md) §Strategic Posture say trademarks are filed in the founder's name initially and assignable. What is the actual filing date, jurisdiction order, and assignment template?

- **Status:** unresolved; pre-RFC.
- **Plan:** treat as a Phase 0 deliverable; flag if it slips into Phase 1.

### C. Conformance suite versus runtime tests

Do runtime tests live in `/reference/<runtime>/tests/` *as well as* in `/conformance/`? If yes, what is the boundary?

- **Status:** unresolved.
- **Lean:** `/conformance/` contains spec-level tests that pass on *any* URML-compatible runtime. `/reference/<runtime>/tests/` contains runtime-internal tests (white-box, integration with the substrate, regression). A bug in the validator's parser is a `/reference/validator/tests/` issue; a bug in *which programs the validator accepts* is a `/conformance/` issue.

### D. CHANGELOG granularity

Top-level `CHANGELOG.md` records project-level milestones; each versioned spec layer and reference runtime will eventually have its own. How are the per-artifact changelogs tied to the top-level?

- **Status:** unresolved.
- **Plan:** decide alongside the per-artifact semver decision (Question 3 above).

### E. Multilingual NL fixture naming

The current convention (`scenario.urml.yaml` paired with `scenario.<lang>.txt`) puts everything in one directory. Does that scale to ten languages with twenty scenarios? Or do we move to `nl/<lang>/scenario.txt` parallel trees once the multilingual fixtures actually land?

- **Status:** deferred; not a problem until the second language ships.

---

## How to add to this list

Open an issue with the `open-question` label, or include a question in any RFC you file. Discuss in the issue; promote to this file once the question has at least one concrete constraint and a directional lean.
