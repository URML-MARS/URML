# URML — repo-root convenience targets.
#
# Phase 0: the reference packages are NOT on PyPI. Onboarding is a local
# editable install into a project-local venv, driven by bootstrap.py.
# This Makefile is a thin ergonomic wrapper; everything it does, you can
# do with `python bootstrap.py` directly (the no-make path, documented in
# the README for Windows users who don't have make).
#
# Nothing here is public or irreversible: `make clean` removes the venv
# and every trace.

.PHONY: help install install-dev demo demo-run demo-record kawasaki-demo-record architecture-record audit outreach-refresh outreach-browse outreach-schema-migrate test clean

VENV   := .venv
PYBIN  := $(VENV)/bin
URML   := $(PYBIN)/urml
PYTEST := $(PYBIN)/python -m pytest

help:
	@echo "URML — local development targets"
	@echo ""
	@echo "  make install      Create .venv and install all 5 packages editable (no PyPI)."
	@echo "  make install-dev  Same, plus each package's [dev] extra (pytest/ruff/mypy)."
	@echo "  make demo         Validate the canonical red-mug example end-to-end."
	@echo "  make demo-run     Sentence -> URML -> validate -> execute (hermetic, no creds)."
	@echo "  make demo-record  Regenerate the README hero SVG (deterministic, any OS)."
	@echo "  make architecture-record  Regenerate the homepage architecture-stack SVG."
	@echo "  make audit        Re-measure every suite + fixture count; print a paste-ready"
	@echo "                    block for docs/launch/claims-audit.md (does not auto-edit)."
	@echo "  make outreach-refresh   Regenerate tools/outreach.db from every"
	@echo "                          examples/lighthouses/outreach*.yaml. See RFC-0275."
	@echo "  make outreach-browse    Launch Datasette on http://localhost:8001 with the"
	@echo "                          read-only outreach mirror + canned queries."
	@echo "  make outreach-schema-migrate"
	@echo "                          One-shot: add the schema-v2 fields (tier, country,"
	@echo "                          sector, comments, claude_directives) to every row."
	@echo "                          Run once during rollout; idempotent."
	@echo "  make test         Run every package's test suite (each in its own process)."
	@echo "  make clean        Remove .venv (full, reversible teardown)."
	@echo ""
	@echo "  No make? Run: python bootstrap.py   (then see its printed next steps)"

install:
	python3 bootstrap.py

install-dev:
	python3 bootstrap.py --dev

demo:
	$(URML) validate examples/home/red-mug.urml.yaml \
	    --manifest examples/home/red-mug.manifest.yaml --profile home

# The flagship demo: one English sentence becomes a validated URML
# program becomes an executed step-by-step trace. Hermetic — the `echo`
# provider replays a committed canned completion (no API key, no network)
# and the `mock` adapter moves nothing. Proves the whole language
# pipeline, reproducible by anyone. Full walkthrough + the honest
# "this is a mock" framing: docs/demos/sentence-to-motion.md.
# Generated program lands in $(VENV) so `make clean` removes it.
demo-run:
	$(URML) translate "Bring me the red mug from the kitchen." \
	    --manifest examples/home/red-mug.manifest.yaml --profile home \
	    --provider echo \
	    --echo-response-file examples/home/red-mug.echo-response.json \
	    --out $(VENV)/redmug.generated.yaml
	$(URML) validate $(VENV)/redmug.generated.yaml \
	    --manifest examples/home/red-mug.manifest.yaml --profile home --no-policy
	$(URML) execute $(VENV)/redmug.generated.yaml \
	    --manifest examples/home/red-mug.manifest.yaml --profile home --no-policy

# Regenerate the README hero (docs/assets/sentence-to-motion.svg): the
# committed, CSS-animated terminal SVG of the demo-run loop. Pure Python,
# no asciinema/ffmpeg/node — deterministic and any-OS (unlike the
# asciinema docs/demos/record-*.sh scripts). The committed asset is the
# deliverable; CI (test_demo_svg.py) asserts it is in sync and that every
# line it shows is real `urml` output.
demo-record:
	$(PYBIN)/python tools/scripts/gen_demo_svg.py

# Regenerate the Kawasaki `call_program` hero SVG
# (docs/assets/kawasaki-as-program-to-motion.svg): the RFC-0015 demo,
# same discipline as demo-record. CI (test_kawasaki_demo_svg.py) asserts
# the committed asset matches the generator and that every line is real
# `urml` output.
kawasaki-demo-record:
	$(PYBIN)/python tools/scripts/gen_kawasaki_demo_svg.py

# Regenerate the homepage architecture diagram
# (docs/assets/architecture-stack.svg): committed, deterministic SVG of
# the five-layer stack with the validator gate on the left and the
# domain-profiles pill on the right. Same discipline as demo-record:
# pure stdlib, any-OS. CI (test_architecture_svg.py) asserts the
# committed asset matches the generator and that every layer label
# traces back to docs/architecture.md.
architecture-record:
	$(PYBIN)/python tools/scripts/gen_architecture_svg.py

# Re-measure the claims-audit. Runs every package's pytest, counts the
# conformance fixtures from disk, and prints a paste-ready markdown
# block + a diff vs the current audit table. Does NOT auto-edit any
# file — the maintainer reviews and transcribes. Matches the project's
# "report drift, don't silently rewrite" discipline.
audit:
	$(PYBIN)/python tools/scripts/refresh_audit.py

# Outreach dashboard (RFC-0275). Source of truth: outreach*.yaml.
# The SQLite mirror is derived and gitignored. Datasette is a dev dep;
# `pip install -r tools/requirements-dev.txt` if not already present.
outreach-refresh:
	$(PYBIN)/python tools/scripts/refresh_outreach_db.py

outreach-browse: outreach-refresh
	$(PYBIN)/datasette serve tools/outreach.db \
	    --metadata tools/outreach-datasette-metadata.yaml \
	    --port 8001

outreach-schema-migrate:
	$(PYBIN)/python tools/scripts/migrate_outreach_schema_v2.py

# Each suite runs in its own pytest process: the packages have
# same-named test modules, so a single combined invocation collides on
# collection. Separate processes sidestep that entirely.
test:
	$(PYTEST) reference/validator/tests -q
	$(PYTEST) reference/llm-bridge/tests -q
	$(PYTEST) reference/ros2-runtime/tests -q
	$(PYTEST) reference/px4-runtime/tests -q
	$(PYTEST) conformance/tests -q

clean:
	rm -rf $(VENV)
