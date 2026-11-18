#!/usr/bin/env python3
"""Keep the shared files of skills/tournament-en identical to skills/tournament.

SKILL.md and references/ are written per language; scripts/, assets/ and tests/
are shared. Usage:
    python3 tools/sync_en.py          # copy shared files into tournament-en
    python3 tools/sync_en.py --check  # exit 1 if the copies differ
"""

import filecmp
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, DST = ROOT / "skills" / "tournament", ROOT / "skills" / "tournament-en"
SHARED = ("scripts", "assets", "tests")


def files(base):
    return sorted(
        p.relative_to(base)
        for d in SHARED
        for p in (base / d).rglob("*")
        if p.is_file() and not any(part.startswith(".") or part == "__pycache__" for part in p.parts)
    )


def main():
    check = "--check" in sys.argv
    diff = [
        r
        for r in files(SRC)
        if not (DST / r).exists() or not filecmp.cmp(SRC / r, DST / r, shallow=False)
    ]
    extra = [r for r in files(DST) if not (SRC / r).exists()]
    if check:
        for r in diff + extra:
            print("differs:", r)
        return 1 if diff or extra else 0
    for r in diff:
        (DST / r).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SRC / r, DST / r)
        print("synced:", r)
    for r in extra:
        (DST / r).unlink()
        print("removed:", r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
