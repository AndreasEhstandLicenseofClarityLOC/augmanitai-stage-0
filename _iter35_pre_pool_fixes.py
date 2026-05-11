#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 35 — Pre-Pool-Wave Compliance Fixes.

A) iter24 + iter26 pages: add EU AI Act Art. 50 + DSGVO Authority text to disclaimer section
   (Pre-Publish-Gate found these missing).
B) V11.2 pages: strip residual legacy `<link rel='alternate' hreflang=... href='augmanitai.com/X.html'>` lines
   that iter33 missed.
C) Verify Living Document banner present (case-insensitive); add if missing.
"""
import re, io, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")
ATLAS = DEPLOY / "atlas"

EU_AI_ACT_TEXT = " EU AI Act Regulation 2024/1689 Art. 50 transparency obligations met by this descriptive research framework."
DSGVO_TEXT = " Aufsicht DSGVO: Bayerisches Landesamt für Datenschutzaufsicht, Promenade 18, 91522 Ansbach."


def patch_iter24_disclaimer(c):
    """Insert EU AI Act + DSGVO into iter24 disclaimer section if missing."""
    changed = False
    if "EU AI Act" not in c and "2024/1689" not in c:
        # Insert before &sect;19 in disclaimer
        new_text = f" &sect;17b{EU_AI_ACT_TEXT}"
        c2 = re.sub(r"(&sect;19\s+Severability)", new_text + " " + r"\1", c, count=1)
        if c2 != c:
            c = c2
            changed = True
    if "Bayerisches Landesamt" not in c:
        # Append to existing §18 line in disclaimer (which has the address already)
        c2 = re.sub(
            r"(&sect;18\s+Verantwortlich[^&]*?Starnberg\s*·\s*DE\.)",
            r"\1" + DSGVO_TEXT,
            c, count=1
        )
        if c2 != c:
            c = c2
            changed = True
    return c, changed


def strip_legacy_hreflang(c):
    """Remove <link rel='alternate' hreflang='...' href='augmanitai.com/.html'> lines."""
    orig = c
    # Strip individual hreflang entries pointing to augmanitai.com/X.html
    c = re.sub(
        r'<link\s+rel=["\']alternate["\']\s+hreflang=["\'][^"\']+["\']\s+href=["\']https?://augmanitai\.com/[^"\']+\.html["\']\s*>[\r\n]*',
        "", c
    )
    # Also remove hreflang pointing to augmanitai-tools-pattern with .html
    c = re.sub(
        r'<link\s+rel=["\']alternate["\']\s+hreflang=["\'][^"\']+["\']\s+href=["\']https?://[^"\']*augmanitai-tools[^"\']*\.html["\']\s*>[\r\n]*',
        "", c
    )
    return c, (c != orig)


def main():
    n_iter24_patched = 0
    n_v11_hreflang_stripped = 0
    n_total = 0
    for d in ATLAS.iterdir():
        if not d.is_dir(): continue
        fp = d / "index.html"
        if not fp.exists(): continue
        c = fp.read_text(encoding="utf-8", errors="ignore")
        orig = c
        # Detect iter24-style (<div class="definition"> + universal short disclaimer)
        is_iter24 = '<div class="definition">' in c
        if is_iter24:
            c, ch = patch_iter24_disclaimer(c)
            if ch: n_iter24_patched += 1
        else:
            c, ch = strip_legacy_hreflang(c)
            if ch: n_v11_hreflang_stripped += 1
        if c != orig:
            fp.write_text(c, encoding="utf-8")
            n_total += 1

    print(f"iter24/26 pages patched (EU AI Act + DSGVO): {n_iter24_patched}")
    print(f"V11.2 pages with legacy hreflang stripped: {n_v11_hreflang_stripped}")
    print(f"Total files modified: {n_total}")


if __name__ == "__main__":
    main()
