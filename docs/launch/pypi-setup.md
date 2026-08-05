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

# PyPI setup — the founder-only prerequisites (WS6 0b/0c)

These steps **cannot be done from this repository or by automation** — they
are account-side actions on (test.)pypi.org and in repo Settings, under the
founder's identity. Everything else in the release (build, `twine check`,
TestPyPI rehearsal, clean-venv verify) is automatable and prepared; the
irreversible real publish is gated behind a GitHub Environment approval.

This is the turn-key checklist. Values are exact and match
`.github/workflows/release.yml` — entering anything different breaks the
publish.

## The twenty packages

The family grew past the original five; `release.yml` now builds and
publishes all of these, aligned at `0.3.0` in lockstep:

`urml-validator` · `urml-llm-bridge` · `urml-ros2-runtime` ·
`urml-px4-runtime` · `urml-conformance` · `urml-mcp-server` ·
`urml-model` · `urml-autosar-runtime` · `urml-chrono-runtime` ·
`urml-cobot-runtime` · `urml-edu-runtime` · `urml-embedded-runtime` ·
`urml-humanoid-runtime` · `urml-industrial-arm-runtime` ·
`urml-isaac-runtime` · `urml-legged-runtime` · `urml-marine-runtime` ·
`urml-mobile-runtime` · `urml-mujoco-runtime` · `urml-opcua-runtime`

(The exact list and its build order live in
[`release.yml`](../../.github/workflows/release.yml); if the two ever
disagree, the workflow wins.)

## 0b — Accounts

1. Create / sign in to a **PyPI** account (https://pypi.org) and a
   **TestPyPI** account (https://test.pypi.org) — they are separate.
2. (Recommended) enable 2FA on both.

## 0c — Trusted Publisher (OIDC, no tokens in the repo)

For a **first** publish the projects don't exist on the index yet, so use
PyPI's **pending publisher** flow (it creates the project on first upload):

On **test.pypi.org** *and* **pypi.org**, for **each of the twenty package
names**: Account → *Publishing* → *Add a pending publisher* →

| Field | Value |
|---|---|
| PyPI Project Name | (the package name, e.g. `urml-validator`) |
| Owner | `URML-MARS` |
| Repository name | `URML` |
| Workflow name | `release.yml` |
| Environment name | `pypi-release` for pypi.org; **leave blank** for test.pypi.org |

That's 20 entries on TestPyPI + 20 on PyPI = 40 pending publishers. It
is tedious; it is also one-time, and it keeps every long-lived API token
out of the repository. A pending publisher for a package that was
already published once (e.g. `urml-validator` at 0.1.0) is instead added
on the existing project's *Publishing* settings page.

Then in the GitHub repo → Settings → *Environments*, create two:

- **`testpypi-release`** — no protection needed.
- **`pypi-release`** — add a *required reviewer* (yourself). This is the
  human gate on the irreversible step: the `release` workflow's `pypi`
  target cannot run until it's approved here.

*Alternative (if you'd rather not use Trusted Publishing):* skip 0c, create
an API token on each index, and use the manual ordered `twine upload` path
in [`RELEASING.md`](../../RELEASING.md) §Step by step instead of the
workflow. Decide one; don't half-configure both.

## After 0b/0c — what's already done vs. what you fire

Done and verified on `release/v0.3.0` (this branch / its PR):

- All twenty aligned to `0.3.0` (version + `_version.py` + inter-package
  pins, lockstep). Core suites green post-bump.
- `python -m build` for all twenty → clean `*-0.3.0` sdists + wheels.
- `python -m twine check dist/*` → all 40 artifacts PASSED.

Remaining, in order (RELEASING.md is authoritative):

1. **Pending publishers** (0c above) for any package name not yet
   registered on the index — for the 0.3.0 family that is 19 new names
   plus the existing `urml-validator` project.
2. **TestPyPI rehearsal** — run the `release` workflow (Actions →
   *release* → Run workflow → target `testpypi`). Safe; repeatable.
3. **Clean-venv verify outside the repo**: in a temp dir,
   `pip install --index-url https://test.pypi.org/simple/
   --extra-index-url https://pypi.org/simple/ urml-validator
   urml-llm-bridge urml-ros2-runtime urml-conformance`;
   `urml --version` → `urml-validator 0.3.0`; then
   `urml run "Bring me the red mug from the kitchen." ...` per the
   README hero to prove the wheel path end to end. **Gate — do not
   proceed unless clean.**
4. **Real publish** — run the workflow with target `pypi` and approve
   the `pypi-release` environment gate. Irreversible — you run it.
5. **Tag** — after the publish verifies:
   `git tag v0.3.0 && git push origin v0.3.0`.
6. **Announce** — a short release note; the trained-model story
   (RFC-0666) gets its own post once measured numbers exist.

The irreversible triggers (4, 6) are yours; everything before them is
prepared and repeatable.
