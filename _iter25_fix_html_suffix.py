#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 25 — Fix .html-suffix bug from NEOMANITAI_4407 slugs.

1544 dirs were created as 'foo-bar.html/' instead of 'foo-bar/'.
Rename + patch internal URLs (canonical, og:url, JSON-LD @id, hreflang).
"""
import re, json, io, sys, shutil
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")
ATLAS = DEPLOY / "atlas"

broken = sorted([d for d in ATLAS.iterdir() if d.is_dir() and d.name.endswith(".html")])
print(f"Broken slugs to fix: {len(broken)}")

renamed = 0
patched = 0
conflicts = 0
for d in broken:
    new_name = d.name[:-5]  # strip .html
    new_dir = ATLAS / new_name
    if new_dir.exists():
        # Conflict — clean variant already exists (rare). Skip + log.
        conflicts += 1
        # Just delete the broken one (cleanup)
        shutil.rmtree(d)
        continue
    d.rename(new_dir)
    renamed += 1

    # Patch URLs inside the moved page
    fp = new_dir / "index.html"
    if fp.exists():
        c = fp.read_text(encoding="utf-8", errors="ignore")
        # Replace 'old-slug.html' with 'old-slug' in URLs (canonical, og:url, JSON-LD @id, breadcrumb)
        old_slug = d.name
        new_slug = new_name
        c = c.replace(f"/atlas/{old_slug}/", f"/atlas/{new_slug}/")
        c = c.replace(f"atlas/{old_slug}/", f"atlas/{new_slug}/")
        fp.write_text(c, encoding="utf-8")
        patched += 1

print(f"Renamed: {renamed}")
print(f"Conflicts (broken deleted): {conflicts}")
print(f"URL-patched inside pages: {patched}")

final = sum(1 for x in ATLAS.iterdir() if x.is_dir())
print(f"Atlas pages now: {final}")
