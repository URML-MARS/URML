<p align="center">
  <a href="https://urml.dev"><img src="https://urml.dev/favicon.svg" alt="URML" width="72" height="72"></a>
</p>

---

# Skill marketplace submissions (maintainer action)

Ready-to-push content for publishing [`urml-robot-intent/SKILL.md`](urml-robot-intent/SKILL.md) to the two main agent-skill venues. The in-repo `SKILL.md` is the single source; these entries point back to it. Drafted for the founder to push (the publish steps need the maintainer's GitHub/npm identity). Contact field everywhere: `greenvh@gmail.com`.

Security note: skills.sh / agentskill.sh run server-side static analysis across 12 threat categories (command injection, data exfiltration, credential harvesting, prompt injection, and so on). The URML skill bundles no scripts and only documents read-only `urml` CLI commands, so it should pass cleanly.

---

## Channel 1: skills.sh / `gh skill publish` (GitHub-indexed)

skills.sh (Vercel) and the `ags` / `npx skills` tool index `SKILL.md` files from public GitHub repos. The GitHub CLI has native support: `gh skill publish` validates a skill against the agentskills.io spec and checks repo security settings.

**Discovery path.** The skill lives at the conventional path `.github/skills/urml-robot-intent/SKILL.md`, so `gh skill publish` and the skills.sh / `ags` indexers discover it automatically. No relocation needed.

**Steps:**
1. From a checkout of `URML-MARS/URML`: `gh skill publish` (validates against the spec, reports repo-security recommendations).
2. Confirm it appears on skills.sh and is installable via `npx skills add urml-robot-intent`.

**Listing metadata:**
- **Name:** `urml-robot-intent`
- **One-liner:** Turn a plain-language goal for a physical robot into a validated robot program, checked against the robot's real capabilities and safety limits before any actuator moves.
- **Category:** Robotics / autonomy / safety
- **Tags:** robotics, robot-intent, validation, safety, autonomous-agents, ros2, px4, drone, manipulation, open-standard
- **Repo:** https://github.com/URML-MARS/URML
- **Homepage:** https://urml.dev
- **License:** Apache-2.0

---

## Channel 2: agentskills.io showcase

The open Agent Skills standard maintains a showcase/spec at [`agentskills/agentskills`](https://github.com/agentskills/agentskills). Submit URML by opening a PR (or following its `CONTRIBUTING.md`) adding URML to the showcase. The site lists entries with this shape:

```js
{
  name: "URML",
  description: "URML is an open Apache-2.0 language for robot intent. The urml-robot-intent skill turns a plain-language goal into a robot program validated against a robot's declared capabilities and safety envelope before any actuator moves. Provider-agnostic, runs offline.",
  url: "https://urml.dev",
  instructionsUrl: "https://github.com/URML-MARS/URML/blob/main/.github/skills/urml-robot-intent/SKILL.md",
  sourceCodeUrl: "https://github.com/URML-MARS/URML",
}
```

(Logo assets: the URML mark in `docs/assets/`. Light/dark variants exist if the showcase wants both.)

---

## After publishing

Track these listings like any other outreach: a row per venue with `sent_at` / `posted_url`, contact `greenvh@gmail.com`, `response: none` until there is real adoption signal. Do not cite install counts as engagement without corroboration. The skill must stay in lockstep with the `urml` CLI; if the CLI changes, regenerate the commands in `SKILL.md` before re-publishing.
