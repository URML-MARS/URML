<p align="center">
  <a href="https://urml.dev"><img src="https://urml.dev/favicon.svg" alt="URML" width="72" height="72"></a>
</p>

---

# skills/

URML packaged as an [Agent Skill](https://agentskills.io) (the open `SKILL.md`
standard, originally from Anthropic, now supported across Claude Code, Codex,
Cursor, Gemini CLI, VS Code, and many other agents). A skill is a folder with a
`SKILL.md`: frontmatter (`name`, `description`) plus markdown instructions an
agent loads on demand.

This is the agent-adoption side of [RFC-0640](../docs/rfcs/0640-moltbook.md)'s
strategy: rather than only telling agents about URML, publish URML as a
capability any compatible agent can install.

## What is here

- [`urml-robot-intent/SKILL.md`](urml-robot-intent/SKILL.md): the skill. Turn a
  natural-language goal for a physical robot into a validated URML program before
  any actuator moves. Self-contained, provider-agnostic, with the hermetic
  offline commands.
- [`urml-robot-intent/references/`](urml-robot-intent/references/): a pointer to
  the canonical in-repo guide, kept as a link (not a copy) so the skill cannot
  drift from the runtime.

The skill content is a condensed view of
[`docs/integrations/urml-for-ai-agents.md`](../docs/integrations/urml-for-ai-agents.md);
that doc stays the canonical source.

## Publishing

The `SKILL.md` is the artifact. To distribute it where agents discover skills:

- **skills.sh** (Vercel, npm-style): publish so agents can `npx skills add urml-robot-intent`.
- **agentskills.io showcase**: submit URML to the open-standard client/skill showcase.
- **Direct install**: any skills-compatible agent can load the folder from a
  checkout or a raw GitHub URL.

Publishing to a marketplace is a maintainer action (it needs the relevant account
and, for skills.sh, an npm-style publish). The in-repo skill is the single source;
marketplace entries point back to it. Use `greenvh@gmail.com` for any contact field.

## Discipline

- Keep the skill in lockstep with the reference runtime. Every command in
  `SKILL.md` must run against the current `urml` CLI (the same no-dangling-example
  rule as the rest of the repo).
- Apache-2.0, provider-agnostic, no telemetry. The skill is part of the open core
  story, not a commercial surface.
