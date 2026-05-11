#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 18 — VERSIONS DEDUPE.

Andy-Direktive: "viele terme versioniert in verschiedenen versionen das geht auch nicht.
dass die eigene felder haben das muss ja immer ein aktueller sein."

Removes auto-generated template-variant duplicates:
- *-variant-N (N>=2) — 781 pages
- trust-var-NN (1-25) — 25 pages
- Other generic stubs that are template-replicated

Logic per base-name:
1. If "base" (no suffix) exists → KEEP base, DELETE all variant-N, version-N, trust-var-N siblings
2. If "base-variant-1" or "base-1" exists → KEEP that as canonical
3. If only variant-2..N exist (no base) → KEEP variant-2 as canonical (oldest variant)
4. Always DELETE: trust-var-NN, *-variant-N where N>1
"""
import os, re, shutil, io, sys
from collections import defaultdict
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")
ATLAS = DEPLOY / "atlas"

all_slugs = sorted([d.name for d in ATLAS.iterdir() if d.is_dir()])
print(f"Total atlas pages: {len(all_slugs)}")

# Identify all variants
to_delete = set()
keep_canonical = {}  # base → canonical slug to keep

# Pattern 1: *-variant-N (N>=2)
variant_groups = defaultdict(list)
for s in all_slugs:
    m = re.match(r"^(.+?)-variant-(\d+)$", s)
    if m:
        base = m.group(1)
        n = int(m.group(2))
        variant_groups[base].append((n, s))

# For each variant group: keep base if exists, else keep variant-1 if exists, else variant-2
for base, vs in variant_groups.items():
    vs.sort()  # by variant number
    if base in set(all_slugs):
        # base exists → delete all variants
        for n, s in vs:
            to_delete.add(s)
        keep_canonical[base] = base
    else:
        # base doesn't exist → keep variant-1 if exists, else variant-2 (lowest)
        canonical = vs[0][1]
        keep_canonical[base] = canonical
        for n, s in vs[1:]:
            to_delete.add(s)
print(f"variant-N pattern groups: {len(variant_groups)}")
print(f"  → to delete: {sum(len(v) for v in variant_groups.values()) - sum(1 for b in variant_groups if b in set(all_slugs)) - sum(1 for b in variant_groups if b not in set(all_slugs))}")

# Pattern 2: trust-var-N — ALL DELETE (stubs)
trust_var = [s for s in all_slugs if re.match(r"^trust-var-\d+$", s)]
for s in trust_var:
    to_delete.add(s)
print(f"trust-var-N stubs: {len(trust_var)} → all deleted")

# Pattern 3: *-version-N (rare)
version_groups = defaultdict(list)
for s in all_slugs:
    m = re.match(r"^(.+?)-version-(\d+)$", s)
    if m:
        version_groups[m.group(1)].append((int(m.group(2)), s))
for base, vs in version_groups.items():
    vs.sort()
    if base in set(all_slugs):
        for n, s in vs: to_delete.add(s)
    else:
        # keep lowest version
        for n, s in vs[1:]: to_delete.add(s)
print(f"version-N groups: {len(version_groups)}")

# Pattern 4: trailing -N where same base has multiple variants AND base also exists
# (already mostly captured by variant-N pattern, but check trailing -2, -3, -4 numerics)
trailing_groups = defaultdict(list)
for s in all_slugs:
    m = re.match(r"^(.+?)-(\d+)$", s)
    if m:
        # but skip stuff that's already in to_delete
        if s not in to_delete:
            trailing_groups[m.group(1)].append((int(m.group(2)), s))
# Only delete if base exists
for base, vs in trailing_groups.items():
    if base in set(all_slugs) and len(vs) >= 1:
        # Skip if base is just generic "foo" and vs is ["foo-1"] — keep foo-1
        for n, s in vs:
            if n >= 2:  # foo-2, foo-3 → delete (base wins)
                to_delete.add(s)
print(f"Trailing -N where base exists: candidates considered")

# Stub detection: pages with very short definition + generic "May describe" pattern
stub_count = 0
import re as _re
for s in all_slugs:
    if s in to_delete: continue
    fp = ATLAS / s / "index.html"
    if not fp.exists(): continue
    c = fp.read_text(encoding="utf-8", errors="ignore")
    # Look for stub pattern: "May describe aspect of X experience"
    if _re.search(r"May describe (an? )?aspect of \w+ experience", c, _re.IGNORECASE):
        to_delete.add(s); stub_count += 1
print(f"Stub-pattern 'May describe aspect of X': {stub_count}")

# Final delete
print(f"\n=== TOTAL TO DELETE: {len(to_delete)} ===")
remaining = len(all_slugs) - len(to_delete)
print(f"=== REMAINING ATLAS PAGES: {remaining} ===")

# Sample what stays for top variant-groups
print(f"\n=== Sample: what stays after dedupe ===")
for base in ["absence-feeling", "achievement-warming", "trust-var", "bloom", "echo"]:
    stays = [s for s in all_slugs if s.startswith(base) and s not in to_delete]
    goes = [s for s in all_slugs if s.startswith(base) and s in to_delete]
    print(f"  {base}: stays={stays}, deleted={len(goes)}")

# Execute deletion
import shutil
print(f"\n=== EXECUTING DELETION ===")
n_deleted = 0
for s in to_delete:
    fp = ATLAS / s
    if fp.exists() and fp.is_dir():
        shutil.rmtree(fp)
        n_deleted += 1
print(f"Deleted {n_deleted} atlas folders")

# Verify
final_count = sum(1 for d in ATLAS.iterdir() if d.is_dir())
print(f"Atlas pages NOW: {final_count}")

# Save manifest
import json, datetime
manifest = {
    "iteration": 18,
    "date": datetime.date.today().isoformat(),
    "before_count": len(all_slugs),
    "after_count": final_count,
    "deleted_count": n_deleted,
    "deletion_reasons": {
        "variant-N (N>=2)": sum(1 for s in to_delete if "-variant-" in s),
        "trust-var-N": len([s for s in to_delete if re.match(r"^trust-var-\d+$", s)]),
        "stub-pattern": stub_count,
        "trailing-N (base exists)": sum(1 for s in to_delete if re.match(r".+-\d+$", s) and "-variant-" not in s and not re.match(r"^trust-var-\d+$", s)),
    },
    "deleted_slugs_sample": sorted(to_delete)[:50],
}
(DEPLOY / "_ITER18_DEDUPE_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nManifest: _ITER18_DEDUPE_MANIFEST.json")
