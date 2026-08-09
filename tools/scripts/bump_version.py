"""Lockstep version bump for the twenty-package family.

The v0.2.0 and v0.3.0 alignments were hand-edited across 40+ files (all
pyprojects, all `_version.py` files, and every intra-repo `urml-*>=X` pin,
including the easy-to-miss optional-extra pin in conformance). This script
makes that mechanical and checkable.

Same posture as `refresh_audit.py`: stdlib only, deterministic, and `--check`
is read-only. `--apply` edits files in place and prints what it changed;
review with `git diff` before committing, per the repo's report-drift
discipline.

Usage:

    python tools/scripts/bump_version.py --check 0.4.0
    python tools/scripts/bump_version.py --apply 0.3.0 0.4.0

Rewritten surfaces, per package directory:

- `pyproject.toml`: the `[project]` `version = "..."` line, and every
  `urml-<name>>=OLD` dependency pin (non-URML pins are never touched).
- `src/<pkg>/_version.py`: the `__version__ = "..."` line, where present
  (18 of 20 packages; `mcp-server` and `model` version only in pyproject).
- `reference/validator/src/urml_validator/__init__.py`: the docstring
  `Stability: X.Y.Z.` line, a special case the release commits have
  historically updated.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# The twenty-package family, in the RELEASING.md publish order (tiers matter
# for PyPI first-publish, not for bumping; the list doubles as documentation).
PACKAGE_DIRS: tuple[str, ...] = (
    "reference/validator",
    "reference/llm-bridge",
    "reference/ros2-runtime",
    "reference/autosar-runtime",
    "reference/chrono-runtime",
    "reference/cobot-runtime",
    "reference/edu-runtime",
    "reference/embedded-runtime",
    "reference/humanoid-runtime",
    "reference/industrial-arm-runtime",
    "reference/isaac-runtime",
    "reference/legged-runtime",
    "reference/marine-runtime",
    "reference/mobile-runtime",
    "reference/mujoco-runtime",
    "reference/opcua-runtime",
    "reference/px4-runtime",
    "conformance",
    "reference/mcp-server",
    "reference/model",
)

_SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def _version_files(root: Path) -> list[Path]:
    """Every file that carries a literal package version."""
    files: list[Path] = []
    for pkg in PACKAGE_DIRS:
        pyproject = root / pkg / "pyproject.toml"
        if not pyproject.is_file():
            raise SystemExit(f"bump_version: missing {pyproject}; wrong --root?")
        files.append(pyproject)
        for version_py in sorted((root / pkg).glob("src/*/_version.py")):
            files.append(version_py)
    validator_init = root / "reference/validator/src/urml_validator/__init__.py"
    if validator_init.is_file():
        files.append(validator_init)
    return files


def _patterns(version: str) -> list[tuple[re.Pattern[str], str]]:
    """(pattern, replacement-template) pairs; {new} is filled at apply time."""
    v = re.escape(version)
    return [
        (re.compile(rf'^(version = "){v}(")$', re.MULTILINE), r"\g<1>{new}\g<2>"),
        # Both spellings exist in the tree: bare and `: str`-annotated.
        (re.compile(rf'^(__version__(?:: str)? = "){v}(")$', re.MULTILINE), r"\g<1>{new}\g<2>"),
        (re.compile(rf"(urml-[a-z0-9-]+>=){v}\b"), r"\g<1>{new}"),
        (re.compile(rf"(Stability: ){v}(\.)"), r"\g<1>{new}\g<2>"),
    ]


def check(root: Path, version: str) -> int:
    """Verify every version surface reads `version`. Exit 1 on drift."""
    drift = 0
    stale = re.compile(
        r'^version = "(?P<v>[\d.]+)"$'
        r'|^__version__(?:: str)? = "(?P<w>[\d.]+)"$'
        r"|urml-[a-z0-9-]+>=(?P<p>[\d.]+)"
        r"|Stability: (?P<s>[\d.]+)\.",
        re.MULTILINE,
    )
    for path in _version_files(root):
        text = path.read_text(encoding="utf-8")
        for match in stale.finditer(text):
            found = (
                match.group("v") or match.group("w") or match.group("p") or match.group("s")
            )
            if found != version:
                print(f"DRIFT {path.relative_to(root)}: {match.group(0).strip()}")
                drift += 1
    if drift:
        print(f"bump_version: {drift} surface(s) not at {version}.")
        return 1
    print(f"bump_version: all version surfaces at {version}.")
    return 0


def apply(root: Path, old: str, new: str) -> int:
    """Rewrite `old` to `new` on every version surface; print per-file counts."""
    total = 0
    for path in _version_files(root):
        text = path.read_text(encoding="utf-8")
        count = 0
        for pattern, template in _patterns(old):
            text, n = pattern.subn(template.replace("{new}", new), text)
            count += n
        if count:
            path.write_text(text, encoding="utf-8", newline="\n")
            print(f"{path.relative_to(root)}: {count} change(s)")
            total += count
    print(f"bump_version: {total} change(s) across the family.")
    if total == 0:
        print(f"bump_version: nothing at {old}; already bumped?")
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", metavar="VERSION", help="verify all surfaces read VERSION")
    group.add_argument(
        "--apply", nargs=2, metavar=("OLD", "NEW"), help="rewrite OLD to NEW everywhere"
    )
    args = parser.parse_args(argv)
    versions = [args.check] if args.check else list(args.apply)
    for version in versions:
        if not _SEMVER.match(version):
            parser.error(f"not a semver version: {version!r}")
    if args.check:
        return check(args.root, args.check)
    return apply(args.root, args.apply[0], args.apply[1])


if __name__ == "__main__":
    sys.exit(main())
