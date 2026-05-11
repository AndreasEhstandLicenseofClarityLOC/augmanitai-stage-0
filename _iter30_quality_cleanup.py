#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 30 — QUALITY CLEANUP based on iter27 audit.

Deletes:
- 1695 trailing-N variants (adu-010..100 etc.)  → Pipeline-IDs, not real terms
- 168 stub-pattern pages                          → generator-template-boilerplate
- 359 def_too_short pages                         → bond-a/edge-b/ethics-q-style fragments
"""
import json, shutil, io, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")
ATLAS = DEPLOY / "atlas"

audit = json.load(open(DEPLOY / "_ITER27_QUALITY_DEEP_AUDIT.json", encoding="utf-8"))

to_delete = set()

for slug, r in audit["results"].items():
    if "variant" in r and "trailing" in str(r["variant"]):
        to_delete.add(slug)
    if r.get("stub") in (
        "stub_may_describe", "stub_users_generic", "stub_phenomenon_catalogued",
        "stub_emerged_observation", "stub_identifies_unfolds", "stub_low_uniqueness"
    ):
        to_delete.add(slug)
    if "quality" in r and "def_too_short" in r["quality"]:
        to_delete.add(slug)

# Manually add the def_len=0 ones (network, termmap)
to_delete |= {"network", "termmap"}

print(f"Total slugs to delete: {len(to_delete)}")

n_del = 0
for s in to_delete:
    d = ATLAS / s
    if d.exists() and d.is_dir():
        shutil.rmtree(d)
        n_del += 1

print(f"Deleted: {n_del}")
final = sum(1 for x in ATLAS.iterdir() if x.is_dir())
print(f"Atlas pages now: {final}")

# Save manifest
import datetime
(DEPLOY / "_ITER30_CLEANUP_MANIFEST.json").write_text(
    json.dumps({
        "date": datetime.date.today().isoformat(),
        "deleted_count": n_del,
        "deleted_slugs": sorted(to_delete),
        "atlas_before": 11732,
        "atlas_after": final,
        "categories": {
            "trailing-N variants": sum(1 for s, r in audit["results"].items() if "variant" in r and "trailing" in str(r["variant"])),
            "stubs": sum(1 for s, r in audit["results"].items() if r.get("stub") in ("stub_may_describe", "stub_users_generic", "stub_phenomenon_catalogued", "stub_emerged_observation", "stub_identifies_unfolds", "stub_low_uniqueness")),
            "def_too_short": sum(1 for s, r in audit["results"].items() if "quality" in r and "def_too_short" in r["quality"]),
        }
    }, ensure_ascii=False, indent=2),
    encoding="utf-8"
)
print("Saved: _ITER30_CLEANUP_MANIFEST.json")
