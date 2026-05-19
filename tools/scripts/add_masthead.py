#!/usr/bin/env python3
"""Insert (or remove) the shared URML masthead at the top of every tracked Markdown file.

The masthead is a centered HTML banner: the urml.dev brand mark, the canonical
one-liner, and a link to the site. It is applied to every git-tracked ``*.md``
file *except* GitHub form templates under ``.github/`` (those start with YAML
frontmatter or are issue/PR forms, and an HTML block above the frontmatter
breaks GitHub's template parsing).

Behavior:

* Idempotent. A file already containing ``SENTINEL`` is left untouched, so the
  script is safe to re-run and a partial run can be resumed.
* Frontmatter-aware. If a file begins with a ``---`` YAML frontmatter block the
  banner is inserted *after* the closing ``---``; otherwise it goes at the top.
* ``README.md`` is special-cased: it already carries a standalone tagline line
  identical to the banner's, so that one line is removed to avoid duplication.

Usage::

    python tools/scripts/add_masthead.py            # insert
    python tools/scripts/add_masthead.py --remove   # revert (delete the block)
    python tools/scripts/add_masthead.py --check     # report, change nothing

Run from anywhere; the repo root is derived from ``git``.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SENTINEL = "urml.dev/favicon.svg"

BANNER = """\
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

"""

# The standalone tagline line in README.md that the banner makes redundant.
README_DUP = (
    "A small, opinionated, human-readable language "
    "for describing robot **intent**.\n\n"
)


def repo_root() -> Path:
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(out.stdout.strip())


def tracked_markdown(root: Path) -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "*.md", "*.MD"],
        capture_output=True,
        text=True,
        check=True,
        cwd=root,
    )
    rels = [line for line in out.stdout.splitlines() if line]
    # Exclude GitHub form templates; everything else is in scope.
    return [root / r for r in rels if not r.startswith(".github/")]


def frontmatter_end(text: str) -> int:
    """Return the index just past the closing ``---`` of a YAML frontmatter
    block, or 0 if the file has no frontmatter."""
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return 0
    # Find the closing fence: a line that is exactly '---' after the first.
    lines = text.splitlines(keepends=True)
    for i in range(1, len(lines)):
        if lines[i].rstrip("\r\n") == "---":
            return len("".join(lines[: i + 1]))
    return 0  # Unterminated frontmatter: treat as no frontmatter.


def with_masthead(rel: str, text: str) -> str:
    # Only the top-level README carries the redundant standalone tagline;
    # nested README.md files (docs/, spec/, ...) must not be touched here.
    if rel == "README.md":
        if README_DUP not in text:
            raise SystemExit(
                "README.md: expected duplicate tagline line not found; "
                "aborting so nothing is silently skipped."
            )
        text = text.replace(README_DUP, "", 1)

    cut = frontmatter_end(text)
    if cut == 0:
        return BANNER + text
    head, rest = text[:cut], text[cut:]
    rest = rest.lstrip("\n")
    return head + "\n" + BANNER + rest


def without_masthead(text: str) -> str:
    idx = text.find(BANNER)
    if idx == -1:
        return text
    return text[:idx] + text[idx + len(BANNER) :]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remove", action="store_true", help="revert the masthead")
    parser.add_argument(
        "--check", action="store_true", help="report only, write nothing"
    )
    args = parser.parse_args()

    root = repo_root()
    files = tracked_markdown(root)
    changed: list[str] = []
    skipped = 0

    for path in files:
        rel = path.relative_to(root).as_posix()
        original = path.read_text(encoding="utf-8")
        has = SENTINEL in original

        if args.remove:
            if not has:
                skipped += 1
                continue
            updated = without_masthead(original)
        else:
            if has:
                skipped += 1
                continue
            updated = with_masthead(rel, original)

        if updated == original:
            skipped += 1
            continue

        changed.append(rel)
        if not args.check:
            # newline="" keeps LF as written; utf-8 has no BOM.
            path.write_text(updated, encoding="utf-8", newline="")

    verb = "would change" if args.check else ("reverted" if args.remove else "updated")
    print(f"{verb}: {len(changed)} file(s); skipped (already correct): {skipped}")
    for rel in changed:
        print(f"  {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
