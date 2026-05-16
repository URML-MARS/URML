# Releasing URML packages

> The five reference packages are published to PyPI from this repository.
> This is the canonical, deliberate process. Publishing is **irreversible**
> (a PyPI version can never be re-uploaded, only yanked; names are claimed
> permanently) and **outward-facing**, so it is a founder-gated action —
> never automatic on push.

## The five packages and their dependency order

PyPI resolves dependencies from the index at install time, so a package
must be on the index **before** anything that depends on it. Publish in
this order:

1. `urml-validator` — no internal deps.
2. `urml-llm-bridge` — needs `urml-validator`.
3. `urml-ros2-runtime` — needs `urml-validator`.
4. `urml-conformance` — needs `urml-validator`, `urml-ros2-runtime`.
5. `urml-px4-runtime` — needs `urml-validator`, `urml-ros2-runtime`.

(2 can publish any time after 1; 4 and 5 any time after 3.)

## Version coherence

**Decided:** all five packages are aligned to a single `0.1.0` for a
clean public debut (easier for adopters to reason about "I have URML
0.1.0" than mixed `a0`/`a1` pre-releases). The bump was applied in
lockstep — every `version =`, every `_version.py` `__version__`, and
every inter-package pin:

| Package | Version | Pins |
|---|---|---|
| urml-validator | `0.1.0` | — |
| urml-llm-bridge | `0.1.0` | `urml-validator>=0.1.0` |
| urml-ros2-runtime | `0.1.0` | `urml-validator>=0.1.0` |
| urml-conformance | `0.1.0` | `urml-validator>=0.1.0`, `urml-ros2-runtime>=0.1.0` |
| urml-px4-runtime | `0.1.0` | `urml-validator>=0.1.0`, `urml-ros2-runtime>=0.1.0` |

These resolve correctly for a first publish in the dependency order
above. Future releases bump in lockstep too — keep the five uniform.

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

# 1. Build all five (artifacts land in each package's dist/, gitignored).
for p in reference/validator reference/llm-bridge reference/ros2-runtime \
         reference/px4-runtime conformance; do
  python -m build --outdir "$p/dist" "$p"
done

# 2. Static metadata check — must all PASS before any upload.
python -m twine check reference/*/dist/* conformance/dist/*

# 3. Upload to TestPyPI in dependency order. Requires a TestPyPI token
#    or a configured Trusted Publisher (see .github/workflows/release.yml).
python -m twine upload --repository testpypi reference/validator/dist/*
python -m twine upload --repository testpypi reference/llm-bridge/dist/*
python -m twine upload --repository testpypi reference/ros2-runtime/dist/*
python -m twine upload --repository testpypi conformance/dist/*
python -m twine upload --repository testpypi reference/px4-runtime/dist/*

# 4. Verify from TestPyPI in a clean venv, OUTSIDE the repo (so bundled
#    data — validator policies, conformance fixtures — must come from the
#    package, not the source tree):
python -m venv /tmp/rel-verify && cd /tmp
/tmp/rel-verify/bin/pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  urml-validator urml-llm-bridge urml-ros2-runtime \
  urml-px4-runtime urml-conformance
/tmp/rel-verify/bin/urml --version
/tmp/rel-verify/bin/python -c "from urml_conformance import discover_fixtures; \
  assert len(discover_fixtures()) >= 20; print('fixtures shipped OK')"

# 5. ONLY if step 4 is clean: upload to real PyPI, same order.
#    This is the irreversible step. Founder runs it deliberately.
python -m twine upload reference/validator/dist/*
# ... remaining four, in order ...

# 6. In the SAME release commit: flip README + docs/tutorials/01 install
#    instructions to `pip install urml-validator urml-llm-bridge`, tag
#    the release (`git tag v0.1.0 && git push --tags`), update the
#    CHANGELOG.
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
