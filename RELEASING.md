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

# Releasing URML packages

> The twenty reference packages are published to PyPI from this repository.
> This is the canonical, deliberate process. Publishing is **irreversible**
> (a PyPI version can never be re-uploaded, only yanked; names are claimed
> permanently) and **outward-facing**, so it is a founder-gated action —
> never automatic on push.

## The twenty packages and their dependency order

PyPI resolves dependencies from the index at install time, so a package
must be on the index **before** anything that depends on it. Publish in
this dependency order (tiers; within a tier the order is free):

1. `urml-validator` — no internal deps.
2. `urml-llm-bridge`, `urml-ros2-runtime` — each needs `urml-validator`.
3. The platform runtimes — `urml-autosar-runtime`, `urml-chrono-runtime`,
   `urml-cobot-runtime`, `urml-edu-runtime`, `urml-embedded-runtime`,
   `urml-humanoid-runtime`, `urml-industrial-arm-runtime`,
   `urml-isaac-runtime`, `urml-legged-runtime`, `urml-marine-runtime`,
   `urml-mobile-runtime`, `urml-mujoco-runtime`, `urml-opcua-runtime`,
   `urml-px4-runtime` — each needs `urml-validator` + `urml-ros2-runtime`.
4. `urml-conformance` (needs validator + ros2-runtime + llm-bridge extra),
   `urml-mcp-server` (needs validator + llm-bridge + ros2-runtime).
5. `urml-model` — needs `urml-validator`, `urml-llm-bridge`, `urml-conformance`.

**First-publish note for 0.4.0.** Only `urml-validator` and
`urml-llm-bridge` are on PyPI today (both at `0.1.0`; the 0.2.0 and 0.3.0
lockstep alignments were never uploaded); the other **eighteen** names are
**first-ever** publishes, so their names are not yet claimed. Each new name
needs a **pending** Trusted Publisher configured on (Test)PyPI before its
first upload (see "Automated path"). Because eighteen names are new, use
the explicitly-ordered `twine upload` sequence below, not the bulk workflow
upload, for the 0.4.0 release.

## Version coherence

**Decided:** all twenty packages are aligned to a single version for a clean
public debut (easier for adopters to reason about "I have URML 0.4.0" than
mixed pre-releases). The bump is applied in lockstep — every `version =`,
every `_version.py` `__version__`, and every inter-package pin. It is
scripted: `python tools/scripts/bump_version.py --apply OLD NEW` rewrites
every surface, and `--check VERSION` verifies uniformity (run it before
building). Pins track the current minor so installing any one package pulls
the matching build of its dependencies:

| Package | Version | Pins |
|---|---|---|
| urml-validator | `0.4.0` | — |
| urml-llm-bridge | `0.4.0` | `urml-validator>=0.4.0` |
| urml-ros2-runtime | `0.4.0` | `urml-validator>=0.4.0` |
| the 13 platform runtimes + urml-px4-runtime | `0.4.0` | `urml-validator>=0.4.0`, `urml-ros2-runtime>=0.4.0` |
| urml-conformance | `0.4.0` | `urml-validator>=0.4.0`, `urml-ros2-runtime>=0.4.0`, `urml-llm-bridge>=0.4.0` (extra) |
| urml-mcp-server | `0.4.0` | `urml-validator>=0.4.0`, `urml-llm-bridge>=0.4.0`, `urml-ros2-runtime>=0.4.0` |
| urml-model | `0.4.0` | `urml-validator>=0.4.0`, `urml-llm-bridge>=0.4.0`, `urml-conformance>=0.4.0` |

These resolve correctly for a publish in the dependency order above. Future
releases bump in lockstep too — keep the twenty uniform.

## The discipline (why this is gated)

Per the project's standing posture (defer public commitments until they
are real): **the README / Tutorial 1 install instructions are not flipped
to `pip install urml-...` until the packages are actually live on PyPI.**
That README change is part of the release commit itself, made *after*
the upload succeeds and a fresh-venv install from the real index is
verified — never before. Packaging-ready ≠ published.

## TestPyPI first, always

Every release goes to TestPyPI and is verified from there before it
touches real PyPI. TestPyPI is the rehearsal: it catches metadata,
dependency-order, and data-file bugs without burning a permanent real
version number.

## Step by step

```bash
# 0. Clean tree on main, all suites green. Decide versions (see above).

# The full publish order (tiers; see the table above). Reused by build,
# TestPyPI upload, and real-PyPI upload so all three stay in lockstep.
PKGS="reference/validator \
      reference/llm-bridge reference/ros2-runtime \
      reference/autosar-runtime reference/chrono-runtime reference/cobot-runtime \
      reference/edu-runtime reference/embedded-runtime reference/humanoid-runtime \
      reference/industrial-arm-runtime reference/isaac-runtime reference/legged-runtime \
      reference/marine-runtime reference/mobile-runtime reference/mujoco-runtime \
      reference/opcua-runtime reference/px4-runtime \
      conformance reference/mcp-server \
      reference/model"

# 1. Build all twenty (artifacts land in each package's dist/, gitignored).
for p in $PKGS; do python -m build --outdir "$p/dist" "$p"; done

# 2. Static metadata check — must all PASS before any upload.
python -m twine check reference/*/dist/* conformance/dist/*

# 3. Upload to TestPyPI in dependency order. Requires a TestPyPI token
#    or a configured Trusted Publisher (see .github/workflows/release.yml).
for p in $PKGS; do python -m twine upload --repository testpypi "$p"/dist/*; done

# 4. Verify from TestPyPI in a clean venv, OUTSIDE the repo (so bundled
#    data — validator policies, conformance fixtures — must come from the
#    package, not the source tree):
python -m venv /tmp/rel-verify && cd /tmp
/tmp/rel-verify/bin/pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  urml-validator urml-llm-bridge urml-ros2-runtime \
  urml-autosar-runtime urml-chrono-runtime urml-cobot-runtime \
  urml-edu-runtime urml-embedded-runtime urml-humanoid-runtime \
  urml-industrial-arm-runtime urml-isaac-runtime urml-legged-runtime \
  urml-marine-runtime urml-mobile-runtime urml-mujoco-runtime \
  urml-opcua-runtime urml-px4-runtime \
  urml-conformance urml-mcp-server urml-model
/tmp/rel-verify/bin/urml --version
/tmp/rel-verify/bin/urml-mcp --help    # MCP server console script resolves
/tmp/rel-verify/bin/python -c "from urml_conformance import discover_fixtures; \
  assert len(discover_fixtures()) >= 20; print('fixtures shipped OK')"

# 5. ONLY if step 4 is clean: upload to real PyPI, same order ($PKGS).
#    This is the irreversible step. Founder runs it deliberately.
for p in $PKGS; do python -m twine upload "$p"/dist/*; done

# 6. AFTER the upload is verified: flip README + docs/tutorials/01 install
#    instructions to the published reality, tag the release
#    (`git tag v0.4.0 && git push --tags`), and cut the GitHub release
#    with the CHANGELOG section as notes.

# 7. Register the MCP server manifest with the official MCP registry
#    (separate from PyPI; needs the package live from step 5 first):
#    see reference/mcp-server/SUBMISSIONS.md for the mcp-publisher steps.
```

## Automated path

`.github/workflows/release.yml` does steps 1–3 (build, check, TestPyPI)
on `workflow_dispatch`. Real-PyPI publish is a separate gated input
behind a protected GitHub Environment so it cannot fire without explicit
approval. **Both paths require Trusted Publisher configuration on
(Test)PyPI per package — that is a one-time founder setup on the PyPI
side (Account → Publishing → add `URML-MARS/URML` + workflow), and
cannot be done from this repository.** Until that is configured, use the
manual `twine upload` path above with an API token.

## Rollback

A bad release is **yanked**, never deleted (`pip` already-pinned installs
keep working; new installs skip it). Fix forward with a new patch
version. There is no "unpublish."
