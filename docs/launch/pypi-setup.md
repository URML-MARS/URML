# PyPI setup — the founder-only prerequisites (WS6 0b/0c)

These steps **cannot be done from this repository or by automation** — they
are account-side actions on (test.)pypi.org and in repo Settings, under the
founder's identity. Everything else in the release (build, `twine check`,
TestPyPI rehearsal, clean-venv verify) is automatable and prepared; the
irreversible real publish is gated behind a GitHub Environment approval.

This is the turn-key checklist. Values are exact and match
`.github/workflows/release.yml` — entering anything different breaks the
publish.

## The five packages

`urml-validator` · `urml-llm-bridge` · `urml-ros2-runtime` ·
`urml-px4-runtime` · `urml-conformance` (all `0.1.0`, aligned).

## 0b — Accounts

1. Create / sign in to a **PyPI** account (https://pypi.org) and a
   **TestPyPI** account (https://test.pypi.org) — they are separate.
2. (Recommended) enable 2FA on both.

## 0c — Trusted Publisher (OIDC, no tokens in the repo)

For a **first** publish the projects don't exist on the index yet, so use
PyPI's **pending publisher** flow (it creates the project on first upload):

On **test.pypi.org** *and* **pypi.org**, for **each of the five package
names**: Account → *Publishing* → *Add a pending publisher* →

| Field | Value |
|---|---|
| PyPI Project Name | (the package name, e.g. `urml-validator`) |
| Owner | `URML-MARS` |
| Repository name | `URML` |
| Workflow name | `release.yml` |
| Environment name | `pypi-release` for pypi.org; **leave blank** for test.pypi.org |

That's 5 entries on TestPyPI + 5 on PyPI = 10 pending publishers.

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

Done and verified on `release/version-align` (this branch / its PR):

- All five aligned to `0.1.0` (version + `_version.py` + inter-package
  pins, lockstep). Suites green: validator 188 / llm-bridge 77 /
  ros2-runtime 114(+4 gated) / px4-runtime 54 / conformance 40.
- `python -m build` for all five → clean `*-0.1.0` sdists + wheels.
- `python -m twine check dist/*` → **all 10 artifacts PASSED**.

Remaining, in order (RELEASING.md is authoritative):

1. **TestPyPI rehearsal** — run the `release` workflow (Actions →
   *release* → Run workflow → target `testpypi`). Safe; repeatable.
2. **Clean-venv verify outside the repo** (RELEASING.md step 4):
   `pip install --index-url https://test.pypi.org/simple/
   --extra-index-url https://pypi.org/simple/ urml-validator
   urml-llm-bridge urml-ros2-runtime urml-px4-runtime urml-conformance`
   in `/tmp`; `urml --version` → `urml-validator 0.1.0`;
   `python -c "from urml_conformance import discover_fixtures;
   assert len(discover_fixtures())>=20"`. **Gate — do not proceed unless
   clean.**
3. **First real publish** — because the projects are new to the index,
   dependency order matters. Use the **manual ordered `twine upload`**
   sequence in RELEASING.md §Step-by-step (validator → llm-bridge →
   ros2-runtime → conformance → px4-runtime), *not* the workflow's bulk
   path (the workflow is the steady-state path; its own header says so).
   This is **6e — irreversible — you run it.**
4. **Release commit (6f)** — only after a fresh *real*-PyPI install
   verifies: flip README + Tutorial 1 install blocks to `pip install`,
   update CHANGELOG, `git tag v0.1.0 && git push --tags`. (I prepare
   this commit; it lands with your go.)
5. **Announce (6g)** — publish `ANNOUNCE.md`; the WS4 Phase-0→1
   governance flip rides here.

I never run steps 3 or 5. I hand a verified-green state and the exact
commands; the irreversible trigger is yours.
