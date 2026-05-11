#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 29 — CRITICAL TRADE-SECRET FIX: remove "Inhaber Leomanitai UG" from all pages.

Per TRADE_SECRET_NOTE.md Section 1.C:
"Leomanitai (UG / Plattform / Geschaeftsmodell) ↔ Andy-Verbindung: Beamten-Nebentaetigkeits-Risiko
 + GF-Trennung. Leona ist GF, Andy ist nicht Inhaber. Verbindung Andy↔Leomanitai NIRGENDS aussen
 sichtbar machen."

Replacements:
- "Inhaber Leomanitai UG" → removed (EUIPO number stays as public registry reference)
- "Leomanitai UG" in any other context → removed
- ", Inhaber ..." cleanup
"""
import re, io, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")

# Patterns to scrub
REGEX_PATTERNS = [
    # ", Inhaber Leomanitai UG)" → ")"
    (re.compile(r",\s*Inhaber\s+Leomanitai\s+UG\s*\)"), ")"),
    # "(EUIPO 019206780, Inhaber Leomanitai UG)" → "(EUIPO 019206780)"
    (re.compile(r"\(EUIPO\s+019206780,\s*Inhaber\s+Leomanitai\s+UG\)"), "(EUIPO 019206780)"),
    # "Inhaber Leomanitai UG" anywhere
    (re.compile(r"\s*Inhaber\s+Leomanitai\s+UG"), ""),
    # Fallback: bare "Leomanitai UG" anywhere
    (re.compile(r"\s*Leomanitai\s+UG"), ""),
    # Cleanup dangling double-comma or comma-paren
    (re.compile(r",\s*\)"), ")"),
    (re.compile(r",\s*,"), ","),
]


def patch_file(fp):
    try:
        c = fp.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return 0
    orig = c
    for pat, rep in REGEX_PATTERNS:
        c = pat.sub(rep, c)
    if c != orig:
        fp.write_text(c, encoding="utf-8")
        return 1
    return 0


def main():
    n = 0
    for fp in DEPLOY.rglob("*.html"):
        if patch_file(fp): n += 1
    for special in ["ai.txt", "llms.txt", "robots.txt"]:
        fp = DEPLOY / special
        if fp.exists() and patch_file(fp): n += 1
    print(f"Patched files: {n}")

    # Verify
    leftover = 0
    for fp in DEPLOY.rglob("*.html"):
        c = fp.read_text(encoding="utf-8", errors="ignore")
        if "Leomanitai" in c:
            leftover += 1
    print(f"Leftover 'Leomanitai' mentions in HTML: {leftover}")


if __name__ == "__main__":
    main()
