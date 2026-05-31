#!/usr/bin/env python3
"""One-shot migration: add tier, country, sector, comments, claude_directives to every outreach ledger row.

Implements RFC-0275 (outreach ledger schema v2). Reads every
examples/lighthouses/outreach*.yaml, regex-extracts tier and country from
the free-text notes field, infers sector from the wave plus keywords in
notes, and writes the new structured fields in place. Comments and
Claude-directives default to empty lists.

Two output reports for founder review:
    docs/launch/outreach-schema-migration-report.md
        Every row's extraction outcome with confidence (high/medium/low).
    docs/launch/outreach-schema-migration-uncertain.md
        Subset: rows where any field was extracted with low confidence
        and the founder should manually review.

Usage:
    python tools/scripts/migrate_outreach_schema_v2.py --dry-run
    python tools/scripts/migrate_outreach_schema_v2.py

In --dry-run mode the YAML files are NOT modified; only the reports are
written. In real mode the YAML files are rewritten in place using
ruamel.yaml round-trip mode so existing formatting and comments are
preserved (so `git diff` shows only the actual schema additions, not
formatting churn).

Per RFC-0275 the script is one-shot. After the migration PR lands, this
script is preserved for archival reference but should not be re-run.
"""

from __future__ import annotations

import argparse
import io
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Optional

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from ruamel.yaml.scalarstring import LiteralScalarString


REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_DIR = REPO_ROOT / "examples" / "lighthouses"
REPORT_DIR = REPO_ROOT / "docs" / "launch"

VALID_SECTORS = {
    "robot-platform",
    "component-vendor",
    "substrate-runtime",
    "protocol-substrate",
    "middleware",
    "simulator",
    "perception",
    "ai-language",
    "framework-skill",
    "governance-body",
    "conceptual-peer",
    "education-toolchain",
    "medical",
    "agriculture",
    "delivery",
}


WAVE_DEFAULT_SECTOR = {
    "outreach.yaml": "robot-platform",
    "outreach-move2.yaml": "ai-language",
    "outreach-move3.yaml": "robot-platform",
    "outreach-move4.yaml": "robot-platform",
    "outreach-move5.yaml": "robot-platform",
    "outreach-move6.yaml": "robot-platform",
    "outreach-move7.yaml": "agriculture",
    "outreach-move8.yaml": "robot-platform",
    "outreach-move9.yaml": "robot-platform",
    "outreach-move10.yaml": "perception",
    "outreach-move11.yaml": "ai-language",
    "outreach-move12.yaml": "ai-language",
    "outreach-move13.yaml": "robot-platform",
    "outreach-move14.yaml": "robot-platform",
    "outreach-move15.yaml": "robot-platform",
    "outreach-move16.yaml": "substrate-runtime",
    "outreach-move17.yaml": "governance-body",
    "outreach-move18.yaml": "substrate-runtime",
}


# Waves where the header asserts every row is one tier (so missing explicit
# "Tier X" notation in row notes still gets the right answer).
WAVE_DEFAULT_TIER = {
    "outreach-move17.yaml": "A",  # header: "22 Tier A rows in this ledger"
}


COUNTRY_PATTERNS = [
    ("INTL", [
        r"\bLinux Foundation\b",
        r"\bEclipse Foundation\b",
        r"\bDronecode Foundation\b",
        r"\bOpen Robotics Foundation\b",
        r"\bOPC Foundation\b",
        r"\bOpenSSF\b",
        r"\bDroneCAN community\b",
        r"\bROS-Industrial\b",
        r"\bIEEE\b",
        r"\bISO\b",
        r"\bASTM\b",
        r"\bCEN-CENELEC\b",
        r"\bOECD\b",
        r"\bNIST\b",
        r"\bMulti-vendor governance\b",
        r"\bmulti-vendor, governance-neutral\b",
    ]),
    ("US", [r"\bOrigin US\b", r"\bOrigin\s+US\b", r"\bUS-domiciled\b", r"\bUS-based\b",
            r"\bUS\s+lead\b", r"\bUnited States\b", r"\bUSA\b",
            r"\bSanta Clara CA\b", r"\bPittsburgh\b", r"\bSan Francisco\b",
            r"\bBoston\b", r"\bMassachusetts\b", r"\bNew York\b",
            r"\bPurdue\b", r"\bStanford\b", r"\bMIT\b", r"\bCarnegie\b",
            r"\bWPI\b", r"\bIthaca NY\b", r"\bMIT\s+lead"]),
    ("FR", [r"\bOrigin FR\b", r"\bFrance\b", r"\bParis\b", r"\bBordeaux\b",
            r"\bSYSTRAN\b", r"\bPollen Robotics\b", r"\bINRIA\b"]),
    ("DE", [r"\bOrigin DE\b", r"\bGermany\b", r"\bBerlin\b", r"\bMunich\b",
            r"\bBavaria\b"]),
    ("JP", [r"\bOrigin JP\b", r"\bJapan\b", r"\bTokyo\b", r"\bToyota Research\b",
            r"\bKawasaki Heavy\b"]),
    ("CN", [r"\bOrigin CN\b", r"\bChina\b", r"\bShenzhen\b", r"\bBeijing\b",
            r"\bPRC\b", r"\bcountry_of_origin:\s*CN\b"]),
    ("KR", [r"\bOrigin KR\b", r"\bKorea\b", r"\bSeoul\b"]),
    ("UK", [r"\bOrigin UK\b", r"\bUnited Kingdom\b", r"\bBritain\b",
            r"\bEdinburgh\b", r"\bLondon\b", r"\bCambridge UK\b"]),
    ("NL", [r"\bOrigin NL\b", r"\bNetherlands\b", r"\bAmsterdam\b",
            r"\bDelft\b", r"\bEindhoven\b"]),
    ("SE", [r"\bOrigin SE\b", r"\bSweden\b", r"\bBitcraze AB, Malmo\b",
            r"\bStockholm\b", r"\bLund\b"]),
    ("CH", [r"\bOrigin CH\b", r"\bSwitzerland\b", r"\bEPFL\b", r"\bZurich\b",
            r"\bGeneva\b"]),
    ("IT", [r"\bOrigin IT\b", r"\bItaly\b", r"\bGenoa\b", r"\bFaconti\b",
            r"\bIIT\b", r"\bMilan\b"]),
    ("AT", [r"\bOrigin AT\b", r"\bAustria\b", r"\bPremst.tten\b",
            r"\bVienna\b"]),
    ("FI", [r"\bOrigin FI\b", r"\bFinland\b", r"\bHelsinki\b"]),
    ("BG", [r"\bOrigin BG\b", r"\bBulgaria\b"]),
    ("AU", [r"\bOrigin AU\b", r"\bAustralia\b", r"\bUNSW\b", r"\bSydney\b",
            r"\bMelbourne\b"]),
    ("CA", [r"\bOrigin CA\b", r"\bCanada\b", r"\bVancouver\b", r"\bMontreal\b",
            r"\bToronto\b"]),
    ("BE", [r"\bOrigin BE\b", r"\bBelgium\b", r"\bBrussels\b"]),
    ("IL", [r"\bOrigin IL\b", r"\bIsrael\b", r"\bTel Aviv\b"]),
    ("EE", [r"\bOrigin EE\b", r"\bEstonia\b", r"\bTallinn\b"]),
    ("HU", [r"\bOrigin HU\b", r"\bHungary\b", r"\bBudapest\b",
            r"\bEmlid Tech Kft\b"]),
    ("NZ", [r"\bOrigin NZ\b", r"\bNew Zealand\b", r"\bStonier\b"]),
    ("ES", [r"\bOrigin ES\b", r"\bSpain\b", r"\beProsima\b"]),
    ("DK", [r"\bOrigin DK\b", r"\bDenmark\b"]),
    ("NO", [r"\bOrigin NO\b", r"\bNorway\b", r"\bZivid\b"]),
    ("CZ", [r"\bOrigin CZ\b", r"\bCzech\b", r"\bPrague\b"]),
    ("RO", [r"\bOrigin RO\b", r"\bRomania\b"]),
    ("SI", [r"\bOrigin SI\b", r"\bSlovenia\b"]),
    ("LT", [r"\bOrigin LT\b", r"\bLithuania\b"]),
    ("SG", [r"\bOrigin SG\b", r"\bSingapore\b", r"\bNUS\b",
            r"\bNational University of Singapore\b"]),
    ("IN", [r"\bOrigin IN\b", r"\bIndia\b", r"\bBangalore\b", r"\bMumbai\b"]),
    ("TW", [r"\bOrigin TW\b", r"\bTaiwan\b"]),
    ("PT", [r"\bOrigin PT\b", r"\bPortugal\b"]),
    ("GR", [r"\bOrigin GR\b", r"\bGreece\b"]),
    ("PL", [r"\bOrigin PL\b", r"\bPoland\b", r"\bWarsaw\b"]),
    ("UA", [r"\bOrigin UA\b", r"\bUkraine\b"]),
    ("BR", [r"\bOrigin BR\b", r"\bBrazil\b"]),
    ("MX", [r"\bOrigin MX\b", r"\bMexico\b"]),
]


# Ordered most-specific to least-specific. First match wins. Broad substrate
# / robot-platform patterns are LAST so they don't overshadow specific
# behavior-tree / conceptual-peer / education / medical etc. matches.
SECTOR_KEYWORDS = [
    ("medical", [
        r"\bdVRK\b", r"\bsurgical\b", r"\bmedical robot\b",
        r"\bmedical-robot\b", r"\bsurgery\b", r"\bsurgical robot\b",
    ]),
    ("delivery", [
        r"\bsidewalk delivery\b", r"\bsidewalk-delivery\b",
        r"\bdelivery robot\b", r"\bdelivery-robot\b",
        r"\bsidewalk-delivery class\b", r"\bStarship Technologies\b",
    ]),
    ("agriculture", [
        r"\bagriculture\b", r"\bagri-tech\b", r"\bagricultural\b",
        r"\bfarming robot\b", r"\bagri robot\b",
    ]),
    ("education-toolchain", [
        r"\bPROS\b", r"\bWPILib\b", r"\bPyBricks\b", r"\bVEX V5\b",
        r"\bVEX-V5\b", r"\bFRC\b", r"\bFIRST Robotics\b",
        r"\bChief Delphi\b", r"\beducation-toolchain\b",
        r"\beducation-on-ramp\b", r"\bLEGO SPIKE\b",
        r"\bEducational toolchain\b",
    ]),
    ("conceptual-peer", [
        r"\bOpen Interpreter\b", r"\bopen-interpreter\b",
        r"\bViam\b", r"\bviam-rdk\b", r"\bconceptual peer\b",
        r"\bconceptual-peer\b", r"\bpeer-citation\b",
    ]),
    ("framework-skill", [
        r"\bbehavior tree\b", r"\bbehavior-tree\b", r"\bBehaviorTree\b",
        r"\bpy_trees\b", r"\bSkiROS\b", r"\bskill-library\b",
        r"\bskill library\b", r"\bskill framework\b",
        r"\bcommand library\b", r"\bcommand-library\b", r"\bcommand DSL\b",
        r"\bskill catalog\b", r"\bskill-catalog\b",
        r"\bLangGraph\b", r"\bagent orchestration\b",
    ]),
    ("governance-body", [
        r"\bgovernance body\b", r"\bgovernance-body\b",
        r"\bfoundation home\b", r"\bfoundation-home\b",
        r"\bstandards body\b", r"\bstandards-body\b",
        r"\bELISA\b", r"\bSLSA\b", r"\bScorecard\b",
        r"\bOPC Foundation\b", r"\bASTM F45\b", r"\bIEEE 1872\b",
        r"\bNIST\b", r"\bCEN-CENELEC\b", r"\bOECD\b",
        r"\bClass\s+[123]\s*/\s*Sub-wave\b",
    ]),
    ("simulator", [
        r"\bWebots\b", r"\bGazebo\b", r"\bMuJoCo Playground\b", r"\bMuJoCo\b",
        r"\bDrake\b", r"\bIsaac Sim\b", r"\bsim-substrate\b",
        r"\bsim substrate\b", r"\brobot simulator\b",
    ]),
    ("middleware", [
        r"\bCyclone DDS\b", r"\bFast DDS\b", r"\beProsima Fast DDS\b",
        r"\bZenoh\b", r"\biceoryx\b", r"\bDDS\b",
        r"\bzero-copy IPC\b", r"\bpub-sub overlay\b",
    ]),
    ("protocol-substrate", [
        r"\bMAVLink\b", r"\bDroneCAN\b", r"\blibcanard\b", r"\bOPC UA\b",
        r"\bCRTP\b", r"\bMAVSDK\b", r"\bprotocol substrate\b",
        r"\bprotocol-class\b",
    ]),
    ("perception", [
        r"\bdepth camera\b", r"\blidar\b", r"\bLiDAR\b", r"\bToF\b",
        r"\btime-of-flight\b", r"\bperception\b", r"\bIMU\b", r"\bGNSS\b",
        r"\bRTK\b", r"\btactile\b", r"\bsonar\b", r"\bunderwater sonar\b",
        r"\bevent camera\b", r"\bspectral\b", r"\bhyperspectral\b",
        r"\bRealSense\b", r"\bZED\b", r"\bMultiSense\b", r"\bMira\b",
        r"\bTMF\b", r"\bcamera SDK\b", r"\bstereo\b", r"\bRGB-D\b",
    ]),
    ("ai-language", [
        r"\bVLA\b", r"\bvision-language-action\b", r"\bfoundation model\b",
        r"\bDiffusion Policy\b", r"\bdiffusion policy\b", r"\bopenvla\b",
        r"\bOpenVLA\b", r"\bOcto\b", r"\bWhisper\b", r"\bSTT\b", r"\bTTS\b",
        r"\btranslation\b", r"\bMarian\b", r"\bOPUS-MT\b", r"\bArgos\b",
        r"\bLibreTranslate\b", r"\bopenvoice\b", r"\bOpenVoice\b",
        r"\bPiper\b", r"\bPorcupine\b", r"\bsmolagents\b",
        r"\bGemini Robotics\b", r"\bOpenMind\b",
        r"\bAI2-THOR\b", r"\bTheia\b", r"\bVLFM\b", r"\bPSI\b",
        r"\bCogACT\b", r"\bOctopi\b", r"\bAutoDistill\b",
        r"\bspeech-IO\b", r"\bspeech IO\b", r"\bBCI intent\b",
        r"\bBrainFlow\b", r"\bOpenBCI\b",
    ]),
    ("substrate-runtime", [
        r"\bROS 2\b", r"\bROS-?2\b", r"\bROS 2 core\b", r"\bNav2\b",
        r"\bMoveIt\b", r"\bMoveIt 2\b", r"\bMoveIt Task Constructor\b",
        r"\bPX4\b", r"\bArduPilot\b", r"\bKlipper\b", r"\bMarlin\b",
        r"\bLinuxCNC\b", r"\bOctoPrint\b", r"\bG-code\b",
        r"\bautopilot stack\b", r"\bsubstrate-runtime\b",
        r"\bsubstrate runtime\b", r"\bsubstrate spine\b",
        r"\bautopilot substrate\b", r"\bROS-Industrial\b",
    ]),
    ("component-vendor", [
        r"\bcomponent vendor\b", r"\bcomponent-vendor\b",
        r"\bservo\b", r"\bmotor controller\b", r"\bESC\b",
        r"\bmoteus\b", r"\bactuator vendor\b",
    ]),
    ("robot-platform", [
        r"\brobot platform\b", r"\brobot-platform\b", r"\bhumanoid\b",
        r"\bquadruped\b", r"\bbiped\b", r"\bmobile robot\b",
        r"\bmobile-base\b", r"\bnano-drone\b", r"\bnano drone\b",
        r"\bbittle\b", r"\bBittle\b", r"\bNAO\b", r"\bPepper\b",
        r"\bPoppy\b", r"\bReachy\b", r"\bCrazyflie\b",
    ]),
]


# Per-slug sector overrides for rows where keyword detection is unreliable.
# Source: explicit RFC framing or domain knowledge. Trumps SECTOR_KEYWORDS.
SLUG_SECTOR_OVERRIDES = {
    "klipper": "substrate-runtime",
    "wpilib": "education-toolchain",
    "crazyflie": "robot-platform",
    "openbci-brainflow": "ai-language",
    "marlin": "substrate-runtime",
    "octoprint": "substrate-runtime",
    "linuxcnc": "substrate-runtime",
    "webots": "simulator",
    "pybricks": "education-toolchain",
    "pros-vex": "education-toolchain",
    "naoqi-driver": "robot-platform",
    "pepper-dcm-robot": "robot-platform",
    "poppy-humanoid": "robot-platform",
    "reachy": "robot-platform",
    "open-interpreter": "conceptual-peer",
    "viam-rdk": "conceptual-peer",
    "behaviortree-cpp": "framework-skill",
    "py-trees": "framework-skill",
    "moveit-task-constructor": "framework-skill",
    "skiros2": "framework-skill",
    "langgraph": "framework-skill",
    "jhu-dvrk-saw-intuitive-research-kit": "medical",
    "robotology-icub-main": "robot-platform",  # humanoid research platform
    "robotology-yarp": "framework-skill",
    "starship-bag-rdr": "delivery",
    "serve-robotics-model-optimizer": "delivery",
    "mjbots-moteus": "component-vendor",
    "moteus-mjbots": "component-vendor",
    "moteus": "component-vendor",
}


def extract_tier(notes: str, slug: str = "", wave: str = "") -> tuple[str, str]:
    """Return (tier, confidence) where tier in {A, B, C} and confidence in {high, medium, low}."""
    if not notes:
        if wave in WAVE_DEFAULT_TIER:
            return (WAVE_DEFAULT_TIER[wave], "medium")
        return ("A", "low")
    m = re.search(r"\bTier\s+([ABC])\b", notes)
    if m:
        return (m.group(1), "high")
    # Tier C inferred from exclusion language
    if re.search(r"\bexcluded with cause\b", notes, re.IGNORECASE):
        return ("C", "medium")
    if re.search(r"\bTier C\b", notes):
        return ("C", "high")
    # Wave-asserted tier (e.g., Move-17 is all Tier A per header)
    if wave in WAVE_DEFAULT_TIER:
        return (WAVE_DEFAULT_TIER[wave], "medium")
    # Default to A when nothing matches, but flag low confidence
    return ("A", "low")


def extract_country(notes: str, slug: str = "") -> tuple[str, str]:
    """Return (country_code, confidence)."""
    if not notes:
        return ("US", "low")
    for code, patterns in COUNTRY_PATTERNS:
        for pat in patterns:
            if re.search(pat, notes):
                # Prefer high confidence for explicit `Origin XX` patterns
                conf = "high" if "Origin" in pat else "medium"
                return (code, conf)
    return ("US", "low")


def extract_sector(notes: str, slug: str, wave: str) -> tuple[str, str]:
    """Return (sector, confidence)."""
    # Per-slug overrides win first.
    if slug in SLUG_SECTOR_OVERRIDES:
        return (SLUG_SECTOR_OVERRIDES[slug], "high")
    haystack = f"{notes} {slug}"
    for sector, patterns in SECTOR_KEYWORDS:
        for pat in patterns:
            if re.search(pat, haystack):
                return (sector, "high")
    # Fall back to wave default
    default = WAVE_DEFAULT_SECTOR.get(wave, "robot-platform")
    return (default, "medium" if default else "low")


def add_v2_fields(row: CommentedMap, slug: str, wave_file: str) -> dict:
    """Mutate row in place. Return extraction report dict."""
    notes = row.get("notes", "") or ""
    tier, tier_conf = extract_tier(notes, slug, wave_file)
    country, country_conf = extract_country(notes, slug)
    sector, sector_conf = extract_sector(notes, slug, wave_file)

    # Insert structured fields BEFORE notes (visible position) if notes exists,
    # otherwise append to the end.
    insert_after_key = "response"
    keys = list(row.keys())
    target_idx = keys.index(insert_after_key) + 1 if insert_after_key in keys else len(keys)

    new_fields = [
        ("tier", tier),
        ("country", country),
        ("sector", sector),
        ("comments", CommentedSeq()),
        ("claude_directives", CommentedSeq()),
    ]
    # Only add fields that aren't already present (idempotent re-run safety).
    for key, value in new_fields:
        if key not in row:
            row.insert(target_idx, key, value)
            target_idx += 1

    return {
        "slug": slug,
        "wave": wave_file,
        "tier": tier,
        "tier_conf": tier_conf,
        "country": country,
        "country_conf": country_conf,
        "sector": sector,
        "sector_conf": sector_conf,
        "low_conf": [k for (k, v) in [
            ("tier", tier_conf), ("country", country_conf), ("sector", sector_conf),
        ] if v == "low"],
    }


def process_ledger(path: Path, yaml_io: YAML, dry_run: bool) -> list[dict]:
    raw = path.read_text(encoding="utf-8")
    data = yaml_io.load(raw)
    if not isinstance(data, CommentedSeq):
        # Some ledger files have a top-level list; others may have a wrapper.
        # All current outreach*.yaml files are bare lists.
        print(f"warn: {path.name} is not a list", file=sys.stderr)
        return []
    extractions = []
    for row in data:
        if not isinstance(row, CommentedMap):
            continue
        slug = row.get("slug", "")
        ext = add_v2_fields(row, slug, path.name)
        extractions.append(ext)
    if not dry_run:
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            yaml_io.dump(data, f)
    return extractions


def write_reports(all_extractions: list[dict]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / "outreach-schema-migration-report.md"
    uncertain_path = REPORT_DIR / "outreach-schema-migration-uncertain.md"

    total = len(all_extractions)
    by_tier = Counter(e["tier"] for e in all_extractions)
    by_country = Counter(e["country"] for e in all_extractions)
    by_sector = Counter(e["sector"] for e in all_extractions)
    uncertain = [e for e in all_extractions if e["low_conf"]]

    lines = [
        "# Outreach schema v2 migration report",
        "",
        f"Generated by `tools/scripts/migrate_outreach_schema_v2.py`. Mechanically",
        f"extracted from each ledger row's `notes` field per RFC-0275.",
        "",
        f"**Total rows processed:** {total}",
        f"**Rows with at least one low-confidence extraction:** {len(uncertain)}",
        "",
        "## Tier distribution",
        "",
        "| Tier | Count |",
        "|---|---|",
    ]
    for tier in sorted(by_tier):
        lines.append(f"| {tier} | {by_tier[tier]} |")

    lines += ["", "## Country distribution (top 15)", "", "| Country | Count |", "|---|---|"]
    for c, n in by_country.most_common(15):
        lines.append(f"| {c} | {n} |")

    lines += ["", "## Sector distribution", "", "| Sector | Count |", "|---|---|"]
    for s in sorted(VALID_SECTORS):
        lines.append(f"| {s} | {by_sector.get(s, 0)} |")

    lines += [
        "",
        "## Per-row extraction (sample of first 50 rows)",
        "",
        "| Wave | Slug | Tier | Country | Sector | Low-conf fields |",
        "|---|---|---|---|---|---|",
    ]
    for e in all_extractions[:50]:
        low = ", ".join(e["low_conf"]) if e["low_conf"] else ""
        lines.append(f"| {e['wave']} | `{e['slug']}` | {e['tier']} | {e['country']} | {e['sector']} | {low} |")

    lines += [
        "",
        f"(Showing 50 of {total} rows. Full extraction in the YAML files.)",
        "",
        "## Idempotency",
        "",
        "Re-running this script is safe. Rows that already have `tier`,",
        "`country`, `sector`, `comments`, or `claude_directives` are not",
        "overwritten; only missing keys are added. After a hand-fix of an",
        "uncertain row, the next migration run preserves the hand-fix.",
        "",
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")

    # Uncertain report
    u_lines = [
        "# Outreach schema v2 migration: rows needing manual review",
        "",
        "Generated by `tools/scripts/migrate_outreach_schema_v2.py`. Each row",
        "below had at least one field where regex extraction fell back to a",
        "low-confidence default. The maintainer is asked to review each row's",
        "`notes` field, decide the correct value, and edit the YAML directly.",
        "",
        f"**Total uncertain rows:** {len(uncertain)} of {total}",
        "",
        "| Wave | Slug | Tier | Country | Sector | Low-conf |",
        "|---|---|---|---|---|---|",
    ]
    for e in uncertain:
        low = ", ".join(e["low_conf"])
        u_lines.append(
            f"| {e['wave']} | `{e['slug']}` | {e['tier']} (`{e['tier_conf']}`) | "
            f"{e['country']} (`{e['country_conf']}`) | {e['sector']} (`{e['sector_conf']}`) | {low} |"
        )
    u_lines += [
        "",
        "## How to fix",
        "",
        "1. Open the row's YAML file (under `examples/lighthouses/`).",
        "2. Find the slug.",
        "3. Edit `tier`, `country`, or `sector` directly to the correct value.",
        "4. The schema-v2 conformance test (PR 3) gates the result. Run",
        "   `python -m pytest conformance/tests/test_outreach_ledger_schema_v2.py`",
        "   locally to verify.",
        "",
    ]
    uncertain_path.write_text("\n".join(u_lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="Do not modify YAML files; only emit reports.")
    args = ap.parse_args()

    yaml_io = YAML(typ="rt")
    yaml_io.preserve_quotes = True
    yaml_io.width = 4096  # long single-line strings stay on one line
    # Match existing ledger convention: `- slug: foo` at column 0, with mapping
    # keys at column 2. ruamel calls this sequence=2, offset=0.
    yaml_io.indent(mapping=2, sequence=2, offset=0)

    ledger_paths = sorted(LEDGER_DIR.glob("outreach*.yaml"))
    if not ledger_paths:
        print(f"error: no outreach*.yaml files under {LEDGER_DIR}", file=sys.stderr)
        return 1

    all_extractions: list[dict] = []
    for path in ledger_paths:
        ext = process_ledger(path, yaml_io, args.dry_run)
        all_extractions.extend(ext)
        print(f"{path.name}: {len(ext)} rows", file=sys.stderr)

    write_reports(all_extractions)

    print(f"\nTotal: {len(all_extractions)} rows across {len(ledger_paths)} files", file=sys.stderr)
    print(f"Report: {REPORT_DIR / 'outreach-schema-migration-report.md'}", file=sys.stderr)
    print(f"Uncertain: {REPORT_DIR / 'outreach-schema-migration-uncertain.md'}", file=sys.stderr)
    if args.dry_run:
        print("DRY RUN: YAML files NOT modified.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
