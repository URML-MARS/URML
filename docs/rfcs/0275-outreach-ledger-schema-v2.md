---
rfc: 0275
title: Outreach ledger schema v2 — structured tier, country, sector, plus per-row comments and Claude directives
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-29
updated: 2026-05-30
supersedes: —
superseded-by: —
---

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

# RFC-0275: Outreach ledger schema v2 — structured tier, country, sector, plus per-row comments and Claude directives

## Summary

URML's outreach has scaled to 229 rows across 17 ledger files (Move-1 through Move-18). The current per-row schema buries tier (A / B / C), country of origin, and sector inside the free-text `notes` field, so aggregate queries are regex-over-prose and only Move-1 has a conformance test gating schema integrity. This RFC adds three structured analytical fields (`tier`, `country`, `sector`) and two interactive workspace lists (`comments`, `claude_directives`) to every row, defines a conformance gate for Move-2 through Move-18, and writes down the agent-directive convention that lets the maintainer leave per-row work for Claude in YAML and see it satisfied as a status change in the same commit. Backward compatibility is additive; pre-v1.0 spec; no primitive added; no Layer-1 through Layer-4 schema changed. This RFC is the open-core artifact that unblocks an interactive dashboard (SQLite mirror + Datasette browser) without forking the source of truth out of YAML.

## Motivation

Three concrete problems with the current ledger shape.

1. **The maintainer loses visibility as the wave count grows.** 229 rows across 17 ledger files cannot be scanned. The maintainer cannot answer "what percent of perception-sector Tier-A engagements landed an engaged response" without grepping prose. The recent Nav2 close (RFC-0275 is in the same week as the post-Nav2 outreach-format reform, AGENTS.md outreach-post-structure section) showed that the cost of being slow to see patterns is real: two prior maintainers bouncing off the same format was a pattern the maintainer wanted to see earlier than they did. Structured analytical fields are how that pattern gets cheap to query.

2. **There is no per-row workspace.** The maintainer scans the ledger and forms intent ("follow up on Bittle hero next week", "don't pursue Moteus further", "draft a round-2 reply on Marty when they respond") with no place to write it down on the row itself. The intent gets re-derived every time, or sits in chat history that decays. A `comments` list lets the maintainer leave a sticky note. A `claude_directives` list lets the maintainer leave work for Claude, with an explicit completion status so the audit trail of "founder asked, Claude did, commit X landed" lives in `git log`.

3. **The standard is the moat (CLAUDE.md §Strategic Posture), and outreach is how the moat gets adopted.** A maintainer who cannot answer "are we engaging Asia-Pacific robotics OEMs at any meaningful rate" cannot rebalance the next wave honestly. The structured fields make that question answerable in three SQL clicks instead of an afternoon of grep.

## Detailed design

### Five new required fields per row (Move-2 through Move-18; backfilled into Move-1 for uniformity, but Move-1's existing parity test remains the load-bearing gate)

```yaml
- slug: <unchanged>
  rfc: <unchanged>
  sent_at: <unchanged>
  posted_url: <unchanged>
  channel: <unchanged>
  contact: <unchanged>
  last_touch: <unchanged>
  response: <unchanged>
  next_action: <unchanged>
  notes: <unchanged>

  tier: A           # NEW. enum: A | B | C
  country: US       # NEW. ISO 3166-1 alpha-2, or the sentinel INTL for multi-national foundations.
  sector: robot-platform   # NEW. enum, see below.
  comments: []      # NEW. list of {date: YYYY-MM-DD, text: str}.
  claude_directives: []   # NEW. list of {date: YYYY-MM-DD, text: str, status: pending | done | skip}.
```

`tier`, `country`, and `sector` are required and validated. `comments` and `claude_directives` default to the empty list and are not required to be present, but the conformance test asserts that when present they match the schema.

### Sector enum

The first version of the enum is ~15 values, derived from the actual ledger content. The RFC review is the place to refine.

```yaml
sector:
  - robot-platform        # humanoid / legged / drone / mobile / arm; sub-shape stays in notes
  - component-vendor      # sensors, actuators, motor controllers
  - substrate-runtime     # ROS 2, PX4, Klipper, Marlin, LinuxCNC firmware
  - protocol-substrate    # MAVLink, DroneCAN, OPC UA, CRTP
  - middleware            # DDS, Zenoh, iceoryx
  - simulator             # Webots, Gazebo, Drake, MuJoCo
  - perception            # cameras, lidar, ToF, IMU, GNSS, tactile, sonar
  - ai-language           # STT, TTS, translation, foundation models, VLAs
  - framework-skill       # behavior trees, command libraries, skill catalogs
  - governance-body       # foundations, standards bodies, regulators
  - conceptual-peer       # Open Interpreter, Viam as peer not substrate
  - education-toolchain   # PROS, WPILib, PyBricks
  - medical               # dVRK, surgical
  - agriculture
  - delivery
```

The enum is closed at v0.1. Adding a new value is an RFC. The closed-enum discipline is what makes "are we engaging X sector at any meaningful rate" queryable without prose interpretation.

### Country field

ISO 3166-1 alpha-2 codes (`US`, `FR`, `DE`, `JP`, `NL`, `KR`, `CN`, etc.). Special sentinel `INTL` for multi-national foundations and standards bodies where a single country does not fit (Linux Foundation, Eclipse Foundation, ISO, IEEE, OPC Foundation, Dronecode Foundation). The conformance test validates the alpha-2 pattern or the literal `INTL`.

`country` is the origin / domicile of the maintainer org, not the country of any individual maintainer. The provenance audit work URML already does (US-federal default policy alignment per RFC-0003 and RFC-0004) is what populates this field; the structured field just makes the audit answerable in SQL.

### Comments list

```yaml
comments:
  - date: 2026-05-29
    text: Founder note: revisit after Q3, watch for upstream MAVSDK 3.0.
```

Append-only by convention. The Datasette write plugin (see Implementation note) does not expose edit or delete. If the maintainer ever needs to edit or remove a comment, they do it in YAML directly. The append-only discipline keeps `git log` honest about when each note was added.

### Claude directives list

```yaml
claude_directives:
  - date: 2026-05-29
    text: Draft a round-2 reply when ros-naoqi maintainer responds.
    status: pending
  - date: 2026-05-25
    text: Add the Bittle hero SVG to the README hero block.
    status: done
```

The `status` enum is `pending | done | skip`. When Claude touches a row that has pending directives, the convention is:

1. Read every `pending` directive on the row.
2. Either satisfy it (and set `status: done` in the same commit that lands the satisfying change), defer it (leave it `pending` and explain in the commit message), or push back (skip is only set by the maintainer, never by Claude).
3. The commit message references the directive verbatim so the audit trail of "founder asked, Claude did, commit X landed" is reconstructable from `git log` alone.

`skip` is the maintainer's "never mind, drop it" without losing the history. Claude never sets `skip`. Claude never deletes a directive entry. The full history of asked-and-satisfied / asked-and-skipped lives in the row forever.

### Spec changes

None. This RFC does not touch Layer-1, Layer-2, Layer-3, or Layer-4. It touches the outreach ledger schema, which lives outside the normative URML spec stack. The outreach ledgers are operational artifacts; this RFC is the first to write down a contract for them.

### Validator changes

None. The URML validator (`urml validate`) operates on URML programs and manifests, not on outreach ledgers. No change.

### Reference runtime changes

None. Reference runtimes consume URML programs and manifests. Outreach ledgers are not part of the runtime surface.

### Conformance suite changes

New test file `conformance/tests/test_outreach_ledger_schema_v2.py`. The new test is schema-only:

- Asserts every row in every Move-2-through-Move-18 ledger has `tier`, `country`, `sector` keys.
- Asserts `tier` is one of `{A, B, C}`.
- Asserts `country` matches the regex `^[A-Z]{2}$` OR is the literal `INTL`.
- Asserts `sector` is in the closed enum.
- Asserts that when `comments` is present it is a list of comment dicts, each with a `date` matching ISO 8601 date format and a non-empty body. The body is carried either as `text` (original shape) or as `summary` with an optional `author` (the richer `{date, author, summary}` shape used when a comment records who said what); exactly one non-empty body field is required.
- Asserts that when `claude_directives` is present it is a list of `{date, text, status}` dicts with `status ∈ {pending, done, skip}`.

The existing `conformance/tests/test_outreach_ledger.py` (Move-1 parity test) keeps its existing assertions. The two tests are complementary: Move-1 has parity-with-`demo.py::LIGHTHOUSES`, Move-2-through-18 has v2-schema enforcement.

## Backward compatibility

Pre-v1.0 spec. The five new fields are additive at the row level. No existing fields are removed or renamed. The free-text `notes` field stays as-is: structured fields are a lens for queries, not a replacement for the prose the maintainer writes when they want to.

Move-1 (`outreach.yaml`) is backfilled in the migration so its rows have the same shape as Move-2-through-18 rows, but Move-1's load-bearing test stays the existing parity test against `demo.py::LIGHTHOUSES`. The v2 schema test does not run against Move-1, so even if a future Move-1 row uses a sector value that is not yet in the enum, the build does not break. The cost is small; the benefit is that downstream tooling (the Datasette mirror in particular) can read every ledger with the same shape.

No external consumer of URML depends on the outreach ledger schema. The audit risk is internal-only.

## Drawbacks

1. **Enum-closing creates a "where does this fit" cost.** Sector and country are closed enums. The next outreach wave that includes, for example, a quantum-computing vendor or a maintainer org domiciled in a country not in URML's prior outreach footprint, has to either widen the enum (an RFC) or pick the closest fit. The friction is real. The mitigation: the enum is sized to current data, the RFC review is the right place to argue for additions, and the cost of a follow-up RFC is small compared to the cost of an unqueryable ledger.

2. **Migration risk on 229 rows across 17 files.** Regex-extraction from free-text `notes` is imperfect. The migration script ships with two output reports (extraction confidence per row, plus an uncertain-rows list for manual review). The conformance test catches anything the migration silently mis-extracted. But the maintainer still has to spot-check the migration output before the migration PR merges.

3. **Schema-evolution debt across waves drafted under the old shape.** Outreach RFCs 0023 through 0269 (the Outreach kind, per `docs/rfcs/README.md`) were drafted under the v1 schema. Their RFC bodies and post bodies do not reference the new fields. This RFC does not propose retroactively updating their prose; only the ledger gets the new fields. Future Outreach RFCs reference the new fields when relevant.

4. **The Datasette write plugin is a new operational surface.** It runs locally, writes back to YAML, and any bug in the plugin's atomic-rename or round-trip-YAML logic can silently corrupt a ledger file. The mitigation: the plugin uses `ruamel.yaml` for round-trip fidelity, writes via tempfile + atomic rename, and is tested with a round-trip test (parse → mutate → dump → reparse and assert equality). The plugin is also small (~150-200 lines Python). But "operational surface that writes to YAML" is a new failure mode this repo did not have before.

## Alternatives considered

1. **Stay free-text in `notes` and write a regex-based dashboard.** Rejected. The maintainer's complaint that visibility is degrading is the core motivation. Regex-over-prose is what is broken today. The whole point of structured fields is to make queries exact, not 80%-right.

2. **Add only `tier` and `country`; leave `sector` for a later RFC.** Rejected. Sector is the most-asked dimension in the maintainer's stated concern (numbers, sectors, success, blockers). Without sector the dashboard cannot answer the "by sector" pivot the maintainer wants.

3. **Move the ledger out of YAML into a SQLite-as-source-of-truth schema.** Rejected. YAML keeps the ledger reviewable in `git diff` and editable in any editor without tooling. SQLite-as-source would couple every reader to the schema and the tooling. The chosen design (YAML source of truth, SQLite as derived view, Datasette as the browser) keeps the YAML readable and adds the query surface as a regenerable side artifact.

4. **Use an external CRM (Salesforce, HubSpot, Pipedrive, Notion).** Rejected. External CRMs add an off-repo synchronization surface and a recurring cost. Phase 1 is solo-maintainer; the right answer is the smallest local tool that fixes the visibility problem.

5. **Use Excel or Google Sheets as the visibility layer.** Rejected. Drift between repo and sheet is the failure mode. Filters and pivots in Sheets are nice but the moment the maintainer forgets to refresh the sheet, the displayed numbers are wrong.

6. **Free-text `claude_directives` field (no structured per-directive status).** Rejected at the AskUserQuestion fork during plan design. The structured shape (per-directive date + status) is what makes the "what does Claude have pending right now" Datasette query trivial. The free-text alternative would force every check-in to re-read the field and infer state.

## Prior art

- [`conformance/tests/test_outreach_ledger.py`](../../conformance/tests/test_outreach_ledger.py). The existing Move-1 parity test that this RFC extends in shape (schema-assertion test) to Move-2-through-Move-18.
- [`tools/scripts/refresh_audit.py`](../../tools/scripts/refresh_audit.py). The existing read-only re-measurer pattern that `tools/scripts/refresh_outreach_db.py` mirrors. The discipline (regenerate on demand, no auto-edit of human-maintained files) carries over.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md). The precedent for writing down a contract that already exists implicitly. RFC-0014 wrote down what makes a runtime URML-compatible; this RFC writes down what an outreach ledger row contains.
- [RFC-0003 (US-federal alignment)](0003-us-alignment.md) and [RFC-0004 (compliance policy)](0004-compliance-policy.md). The source of the provenance / origin discipline that `country` operationalizes.
- `datasette-write-ui`, `datasette-edit-schema`, and `datasette-auth-passwords` plugins. None of them quite fit (they write to SQLite, not back to YAML), but they were considered as alternatives before choosing a custom plugin.

## Unresolved questions

1. **Sector enum size and split.** The proposed enum is ~15 values. Should `perception` be split into `perception-vision`, `perception-range`, `perception-inertial`, `perception-tactile` (finer grain, more queryable, more migration risk)? Should `robot-platform` be split into `robot-humanoid`, `robot-legged`, `robot-drone`, `robot-mobile`, `robot-arm` (same trade-off)? The RFC review is the right place to argue; the migration script can implement whichever the RFC settles on.

2. **Multi-country / multi-sector targets.** A few rows are arguably two sectors (a vendor that ships both a substrate runtime and the component hardware; a foundation that is also a standards body). The current proposal is "pick the dominant one and capture the secondary in `notes`". Is that enough, or does `sector` need to become a list?

3. **`country` for community-OSS targets without a clear domicile.** Some community OSS projects (Klipper, Marlin, LinuxCNC) have lead maintainers in one country but a globally distributed contributor base. The proposal is "use the lead maintainer's country". Is that the right anchor for the US-federal default-policy audit that `country` operationalizes? RFC-0003 / RFC-0004 owners weigh in.

4. **Backfill of Outreach RFC prose.** Should the Outreach RFCs (0023 through 0269 and onward) be retroactively edited to reference their structured `tier` / `country` / `sector` values? The current proposal is no, too much churn for too little benefit. The structured fields live in the ledger; the RFC prose already says what it says.

## Implementation note

This RFC lands as five PRs, in order. Each PR is small enough to review carefully; the migration PR is the largest.

1. **PR 1 (this PR): the RFC document itself.** No code change. The RFC merges first so the schema is the contract everything else is built against.

2. **PR 2: schema migration.** Add `tools/scripts/migrate_outreach_schema_v2.py`. Run it locally; commit the resulting changes to all 17 `examples/lighthouses/outreach*.yaml` files (229-row edits, mostly mechanical). Include `docs/launch/outreach-schema-migration-report.md` and `docs/launch/outreach-schema-migration-uncertain.md` as side artifacts so the maintainer can review extraction confidence. Do not yet add the conformance test; this PR is "add the fields, populate them, report on confidence" only.

3. **PR 3: conformance test.** Add `conformance/tests/test_outreach_ledger_schema_v2.py`. Verify it passes against the migrated tree from PR 2. This PR is the gate that prevents the new fields from rotting back into free-text drift.

4. **PR 4: read-only Datasette dashboard.** Add `tools/scripts/refresh_outreach_db.py`, `tools/outreach-datasette-metadata.yaml`, `tools/requirements-dev.txt` (adds `datasette` and `ruamel.yaml`), `Makefile` targets (`outreach-refresh`, `outreach-browse`), `.gitignore` entry for `tools/.outreach.db`. The Datasette UI is read-only at this stage.

5. **PR 5: Datasette write plugin.** Add `tools/datasette_plugins/outreach_edits.py`. Wire it into `make outreach-browse`. Add the round-trip-YAML write test. This is the PR that turns Datasette from a viewer into a workspace where the maintainer leaves comments and claude-directives.

PRs 2 through 5 stack on the merged RFC. They do not stack on each other; each is a standalone PR against `main`, so review can land them out of order if needed. The migration PR is the only one with a 229-file diff; the others are small.

## Self-review (Phase 0)

- [x] The Summary alone tells a reader what is being proposed.
- [x] The Motivation is grounded in a concrete use case (229 rows, post-Nav2 pattern visibility cost), not hypothetical needs.
- [x] The Detailed design names every affected file (17 ledger YAMLs, 1 conformance test, 0 spec docs, 0 reference runtimes).
- [x] At least one alternative is genuinely considered (six, including Excel / external CRM / SQLite-as-source / free-text directives).
- [x] Drawbacks are listed; at least one is a real downside (Datasette write plugin is a new operational surface that can corrupt a ledger if buggy).
- [x] Backward compatibility is honest (pre-v1.0, additive, no breakage; Move-1 backfilled but its own test stays).
- [x] This RFC adds no Layer-2 primitive. Substrate-neutrality acid test is not applicable.
- [x] The implementation note explains how this lands (5 stacked PRs, smallest-to-largest).
- [x] The author has re-read `CLAUDE.md` §What Claude Should Never Do and confirmed this proposal does not violate it. In particular: no cloud dependency, no commercial-in-repo, no vendor lock-in, no telemetry, no concentrated copyright (DCO sign-off is on every commit).
