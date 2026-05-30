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

# AGENTS.md

> Operational handbook for AI assistants working in this repository (Claude Code, Cursor, Copilot Chat, Aider, any future agent that reads `AGENTS.md` by convention).
> Last updated: 2026-05-23

This file is the working-style companion to [`CLAUDE.md`](CLAUDE.md). `CLAUDE.md` says what URML is and the strategic and architectural rules. `AGENTS.md` says how to act inside the repo: writing style, chat style, outreach discipline, tactical workflow.

**Precedence.** If `AGENTS.md` and `CLAUDE.md` disagree, `CLAUDE.md` wins. If a Claude memory file disagrees with either of these checked-in files, the checked-in file wins. Memory is for state; the checked-in docs are for rules.

---

## Writing style

These rules apply to every artifact a human will see: READMEs, docs, RFC bodies, outreach posts, commit messages, issue replies, this file, [`CLAUDE.md`](CLAUDE.md). They were reinforced after the Hello Robot Stretch 4 outreach packet (2026-05-20: 12 em-dashes in the touch-message body, founder reply: "Too many em-dashes, looks fully machine generated, don't please").

- **No em-dashes** (`—`). Use commas, periods, or parentheses. Replace inline definitions (`X — Y`) with `X. Y.` or `X (Y)` or `X: Y` depending on context.
- **No hedging adverbs:** `importantly`, `notably`, `in essence`, `fundamentally`. Drop them. The sentence is fine without.
- **No throat-clearing transitions:** `furthermore`, `moreover`, `additionally`, `in particular`. Cut them. If you need a transition, start the next paragraph.
- **No empty intensifiers:** `robust`, `comprehensive`, `seamless`, `leverage`, `utilize`, `facilitate`. Use plain words. `use` not `leverage`, `before` not `prior to`, `about` not `regarding`, `help` not `facilitate`.
- **No bold-colon pattern** (`**Foo:** description`) when prose flows fine without it. Bold sentence leads (`**The foo is X.** Then the next thought.`) are fine.
- **No tricolons by default.** Use two items when two will do. Three only when the third earns its place.
- **No over-bulleted text** where short paragraphs work.
- **Short sentences are fine.** Slight informality is fine. Perfect parallelism is not the goal.

Outreach copy especially: write one paragraph at a time, read it aloud, rewrite if it sounds like a marketing email. The recipient is an engineer who clocks LLM copy in two seconds and adjusts trust accordingly.

## Outreach post structure

The Writing-style rules above cover word choice. These cover the shape of a cold outreach post (the Issue or Discussion body a maintainer reads first). They exist because of the Nav2 close: 2026-05-29, Steve Macenski (Nav2 lead maintainer) closed [`navigation2#6184`](https://github.com/ros-navigation/navigation2/issues/6184) saying he tried to answer but the wording was too obtuse to be worth his time. He bounced off the structure, not the topic. A maintainer who has to decode invented vocabulary and pick through seven questions stops reading.

- **Lead with one concrete example, not a description of one.** Show an English sentence, the URML primitive it becomes, and the target's actual call: `move_to(kitchen)` becomes a Nav2 `NavigateToPose` goal. The payload comes first, before any framing about what URML is.
- **One real question. Two at most, never a numbered dump.** If the RFC raises more, they stay in the RFC. The post asks the single highest-value question the maintainer is uniquely able to answer.
- **No invented compound-noun jargon in the post.** If a phrase only parses to someone who already knows URML (`dispatcher-class-only`, `the plugin-set degree of freedom`, `behavior-tree-composition novelty`), it does not belong in a cold post. Say it in plain words or cut it.
- **State up front that the ask is light.** "Apache-2.0, no spec change proposed, nothing for you to maintain." Maintainers triage by how much work you are about to create for them.
- **Link the full RFC as optional depth, never as required reading.** "Full write-up if useful: <link>." Assume the maintainer reads only the post body.
- **A maintainer should be able to read it and answer in under two minutes.** If reading it aloud takes longer than that, it is too long.

The mandatory VIBE disclosure line still goes last (see Outreach identity below), as one line, not a paragraph. The skeleton lives in the `posts-move*` files; the current canonical shape is in [`examples/lighthouses/posts-move17.md`](examples/lighthouses/posts-move17.md).

These rules apply to outreach RFC bodies too, not just the post. Steve called the RFC itself too long and machine-written. An outreach RFC gets the same read-aloud pass: concrete example early, plain language, real drawbacks, no jargon stacks.

## Chat style

The founder writes in very short prompts: `?`, `yes`, `So?`, `No, you do that`. They read outcomes, not narration. Match that energy.

- **Terse prompts get terse outcomes.** Report in a few lines. Lead with what is blocked on the founder. Skip commit-log dumps. Skip re-summaries of what you already showed.
- **Full delegation is expected** for multi-PR work, commits, RFC state changes, merges, RFC drafting, ledger updates. Do not ask permission for steps already delegated.
- **AskUserQuestion only for genuine forks** (which library, which approach, which trade-off the founder owns). Not for "ready?" or "any feedback?" or "should I proceed?". Those are ExitPlanMode or just acting.
- **Thoroughness lives in artifacts, not in chat.** RFCs, specs, and docs get the full treatment. Chat replies stay tight.
- **Disagree directly.** "I think this is wrong because..." beats "you might want to consider...". The founder welcomes disagreement and reads hedging as noise.

### Exception: protected actions need explicit OK

The chat-style autonomy stops at protected actions. Each of these needs a specific, per-action authorization from the founder, not terse delegation:

- Force-push to any branch.
- `--admin` merge to `main` (bypassing branch protection).
- Repo-settings change (branch protection, default branch, merge methods, secrets, webhooks).
- History rewriting (`git rebase -i` against shared branches, `git reset --hard` on shared branches).
- Skipping commit hooks (`--no-verify`, `--no-gpg-sign`).

Prepare the exact commands and hand them over. Do not run them yourself.

## Outreach identity

- **Contact email in any third-party-facing URML artifact: `greenvh@gmail.com`.** Not `ido@jacob-ai.com` (that is the Claude account address; the founder's outbound URML identity is `greenvh@gmail.com`). Use `greenvh@gmail.com` in RFC author fields, packet contact lines, signature blocks, message bodies.
- Git author for commits stays `Ido Yahalomi <greenvh@gmail.com>`.
- **Every outreach post (issue, discussion, message body) ends with a one-paragraph authoring-disclosure line** linking to [`VIBE.md`](VIBE.md). Template: *"AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request."* The disclosure is not optional, and it is not apologetic. Origin: 2026-05-26 OVOS RFC-0107 wontfix close (JarbasAl flagged URML's outreach as AI-generated); URML's response was to disclose openly, not to retreat. See [`docs/rfcs/0107-openvoiceos-outreach.md`](docs/rfcs/0107-openvoiceos-outreach.md).

## Outreach verification (no blind posts)

Before drafting any outreach RFC, issue, or message body:

1. **Open the target's actual repo or API surface.** Verify the class names, file paths, and module imports you cite. If you say `lerobot.common.policies.Policy`, that path must resolve to the named class in the repo's current `main`. Research-agent summaries and search-result snippets are a starting point, not a citation.
2. **Verify the contribution surface exists.** Many open-source projects have Discussions disabled, even when they look like they would not. Check the repo's tabs (Issues, Discussions, PRs) and the `CONTRIBUTING.md`. If you route the post to a surface that 404s, you do not get a second chance.
3. **Verify the named maintainer's current handle and role** from the actual repo (commits, CODEOWNERS, the org's people page), not from a press release summary.
4. **Cite a real precedent** if one exists. A similar plugin, a similar integration, a relevant doc page. Anchoring the proposal in something the maintainers already accepted dramatically improves response rate.

Founder feedback on this rule, 2026-05-23: "no blind anymore, we should be professionals". The first LeRobot draft (RFC-0040, v1) had to be rewritten after a verification pass found: wrong module path, wrong base class, wrong surface (Discussions are disabled), wrong maintainer attribution. Do not repeat that.

## Outreach ledger discipline

Two ledgers live under [`examples/lighthouses/`](examples/lighthouses/):

- `outreach.yaml`: Move #1 (RFCs 0023 through 0038, robot OEMs and component vendors). Parity-locked to `examples/lighthouses/demo.py::LIGHTHOUSES` by `conformance/tests/test_outreach_ledger.py`. Adding a row anywhere needs both updated, or the test fails.
- `outreach-move2.yaml`: Move #2 onward (RFC 0040+, AI / ML layer plus substrate follow-ons). Mirroring schema, no parity test (different audience, not every target has an in-repo manifest).

**Schema (both files):** `slug | rfc | sent_at | channel | contact | last_touch | response | next_action | notes`.

**Response enum:** `none | acked | engaged | declined | wontfix`. Default state for fresh outreach is `none` with `last_touch == sent_at`. Do not massage state to look more engaged than reality. If the only contact in 14 days is silence, `response` stays `none`.

**Update protocol.** When outreach state changes (a maintainer replies, a deadline passes, a nudge goes out), edit the ledger first. Bump `last_touch`. Set `response` from the enum. Write the next concrete step into `next_action`. Keep notes factual.

**Drafting a new outreach RFC.** Number it from the next free slot. Set the `Kind` column in [`docs/rfcs/README.md`](docs/rfcs/README.md) to `Outreach`. Include the explicit sentence "No spec change is proposed here" in the body. Add the ledger row in the same change (Move #1 also updates `demo.py::LIGHTHOUSES`; Move #2+ does not).

## Merge workflow specifics

The CLAUDE.md rule is "merge commit, never squash". This is the operational detail.

- `main` is branch-protected. The repo allows merge and squash, disallows rebase merge, deletes branches on merge.
- Solo-maintainer reality: the founder cannot approve their own PR, so landing requires `gh pr merge <n> --merge --admin`. AI assistants prepare the PR; the founder runs the merge command (or gives an explicit per-action OK).
- **Always pass `-R URML-MARS/URML`** to `gh pr merge`. `gh` resolves the repo from the current working directory by default and that is fragile.
- **Always `git fetch origin` and branch from `origin/main`**, not from stale local `main`. Origin advances between sessions because PRs land outside this chat. Branching from stale local `main` risks a 3-way merge that silently clobbers edits to files origin also changed.
- **After merge, verify the edit landed on `origin/main`** before claiming the work shipped. On Windows the Bash tool mangles `git show origin/main:path` (colon plus backslash); use `git ls-tree -r origin/main -- path` and then read the blob, or use PowerShell.
- **Never `--no-verify` or `--no-gpg-sign`.** If a hook fails, fix the underlying issue. DCO sign-off (`-s`) is mandatory on every commit.

## Audit discipline

`make audit` (= `python tools/scripts/refresh_audit.py`) is a read-only re-measurer:

- It runs every package's pytest in a subprocess, counts conformance fixtures from disk, and prints a paste-ready markdown block plus a diff against the current audit table.
- **It does not auto-edit any file.** The maintainer reads, sanity-checks the diff, and transcribes to `docs/launch/claims-audit.md` and the README front-page cell in lockstep.
- Mark unmeasurable rows (missing optional extras on the host) as `n/a` and carry forward the prior number with an explicit caveat. **Never fabricate 0.**
- Quirk: do not pass `-q` to the subprocess pytest. This venv's config suppresses the `N passed in Xs` summary banner under `-q`, which breaks the parser. The script already handles this; do not "fix" it back.

Report drift, do not silently rewrite. The human review step is the point.

## Hero and demo discipline

The README hero SVG (`docs/assets/sentence-to-motion.svg`) is generated by `tools/scripts/gen_demo_svg.py`. Pure Python stdlib, deterministic, regenerates byte-identical, any-OS including Windows.

- **Not asciinema, not vhs, not termtosvg, not ffmpeg, not Node.** If asked to "use a real recorder," push back: pure Python is the on-ethos choice and matches the MockROSAdapter and bootstrap hermetic posture (zero external runtime dependency). The older `docs/demos/record-*.sh` (asciinema) scripts are a different, manual, non-committed precedent. Do not conflate.
- **`reference/validator/tests/test_demo_svg.py` is the guard.** It asserts the committed SVG equals generator output (stale asset means red CI) and that every line the hero shows is emitted verbatim by a live hermetic `translate -> validate -> execute` run. The hero cannot drift from or lie about the tool.
- **Open residual risk:** GitHub's animation of a CSS-`@keyframes` SVG embedded as an `<img>` is the standard svg-term technique but has not been visually confirmed from CI. The founder eyeballs the rendered README on the branch. Documented fallback if static: a committed GIF from the same transcript (generator and test stay source of truth). Do not claim it animates until someone has actually looked.

## What lives where

| Concern | Source of truth |
|---|---|
| What URML is, the architecture, strategic posture, never-do list | [`CLAUDE.md`](CLAUDE.md) |
| Working-style and tactical AI-assistant rules | This file |
| Per-target outreach state (sent, replies, next steps) | [`examples/lighthouses/outreach.yaml`](examples/lighthouses/outreach.yaml) and [`examples/lighthouses/outreach-move2.yaml`](examples/lighthouses/outreach-move2.yaml) |
| RFC decision history (Spec and Outreach kinds) | [`docs/rfcs/`](docs/rfcs/) |
| The project's constitution | [`MANIFESTO.md`](MANIFESTO.md) |
| Permanent Apache-2.0 commitments | [`CORE_COMMITMENT.md`](CORE_COMMITMENT.md) |
| Governance and decision process | [`GOVERNANCE.md`](GOVERNANCE.md) |
| How to contribute (Phase 1, open) | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| Re-measured test and fixture counts | `make audit`, then transcribed to `docs/launch/claims-audit.md` and the README |

Memory (the Claude auto-memory under each session's project dir) is for **state** (what is currently in flight, who replied when, what the founder asked yesterday) and for **point-in-time observations**. Rules belong in this file or in `CLAUDE.md`. If you find yourself writing a memory that captures a rule, write the rule into one of these files instead and link the file from the memory.

---

*This file is checked into version control. Substantive changes to it require an RFC.*
