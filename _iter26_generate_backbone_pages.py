#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 26 — Generate atlas pages from latest AUG Backbone (981 quality terms).

Same template + Ehstand-anchors as iter24, but uses pre-filtered _ITER26_BACKBONE_POOL.json.
"""
import json, re, io, sys, html
from pathlib import Path
from datetime import datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")
ATLAS = DEPLOY / "atlas"
POOL = DEPLOY / "_ITER26_BACKBONE_POOL.json"

# Import build_page from iter24
sys.path.insert(0, str(DEPLOY))
from _iter24_generate_pool_pages import build_page

def main():
    pool = json.load(open(POOL, encoding="utf-8"))
    print(f"Pool size: {len(pool)}")
    existing = {d.name for d in ATLAS.iterdir() if d.is_dir()}
    to_create = [t for t in pool if t["slug"] not in existing]
    print(f"To create (after de-dupe vs online): {len(to_create)}")

    from collections import defaultdict
    by_cat = defaultdict(list)
    for t in to_create:
        by_cat[t["category"]].append(t)

    created = 0
    for t in to_create:
        sibs = [s for s in by_cat[t["category"]] if s["slug"] != t["slug"]][:6]
        page = build_page(t, sibs)
        d = ATLAS / t["slug"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(page, encoding="utf-8")
        created += 1
        if created % 300 == 0:
            print(f"  ...generated {created}")
    print(f"\n=== Created: {created} ===")
    final = sum(1 for d in ATLAS.iterdir() if d.is_dir())
    print(f"Atlas total now: {final}")

if __name__ == "__main__":
    main()
