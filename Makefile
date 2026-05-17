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

.PHONY: help install install-dev demo demo-run test clean

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
