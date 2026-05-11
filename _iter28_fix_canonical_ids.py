#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 28 — CRITICAL FIX: replace wrong ORCID and Wikidata-IDs across all pages.

Wrong IDs (used by iter21-26):
- ORCID 0000-0003-3171-4159
- Wikidata Q133970938 (Andy)
- Wikidata Q134193001 (AUGMANITAI)

Correct IDs (per TRADE_SECRET_NOTE.md + PERMANITAI_LAUNCH/COINAGES):
- ORCID 0009-0006-3773-7796
- Wikidata Q138634675 (Andy)
- Wikidata Q138522830 (AUGMANITAI)
"""
import re, io, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")

REPLACEMENTS = [
    ("0000-0003-3171-4159", "0009-0006-3773-7796"),
    ("Q133970938", "Q138634675"),
    ("Q134193001", "Q138522830"),
]


def patch_file(fp):
    try:
        c = fp.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return 0
    orig = c
    n_changes = 0
    for old, new in REPLACEMENTS:
        if old in c:
            n_changes += c.count(old)
            c = c.replace(old, new)
    if c != orig:
        fp.write_text(c, encoding="utf-8")
        return n_changes
    return 0


def main():
    total_files = 0
    total_changes = 0
    # All html
    for fp in DEPLOY.rglob("*.html"):
        n = patch_file(fp)
        if n:
            total_files += 1
            total_changes += n
    # ai.txt / llms.txt / robots.txt / sitemap.xml
    for special in ["ai.txt", "llms.txt", "robots.txt", "sitemap.xml"]:
        fp = DEPLOY / special
        if fp.exists():
            n = patch_file(fp)
            if n:
                total_files += 1
                total_changes += n
                print(f"  Patched: {special} ({n} replacements)")

    print(f"\n=== FIXED {total_changes} bad IDs across {total_files} files ===")

    # Verify nothing left
    leftover = 0
    for fp in DEPLOY.rglob("*.html"):
        c = fp.read_text(encoding="utf-8", errors="ignore")
        for old, _ in REPLACEMENTS:
            if old in c:
                leftover += c.count(old)
    print(f"Leftover wrong IDs (should be 0): {leftover}")


if __name__ == "__main__":
    main()
