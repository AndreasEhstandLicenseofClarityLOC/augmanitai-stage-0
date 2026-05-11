#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 36 — Run pre-publish-gate against ALL 8632 existing pages.

Report which fail and why. Pages that fail must be fixed BEFORE we start the next wave.
"""
import json, io, sys
from pathlib import Path
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")
ATLAS = DEPLOY / "atlas"

sys.path.insert(0, str(DEPLOY))
from _pre_publish_gate import validate_page

slugs = sorted([d.name for d in ATLAS.iterdir() if d.is_dir()])
print(f"Sweeping {len(slugs)} pages through gate...")

results = {}
fail_counter = Counter()
n_pass = 0
for i, s in enumerate(slugs):
    if i and i % 1000 == 0: print(f"  ...{i}/{len(slugs)}")
    fp = ATLAS / s / "index.html"
    if not fp.exists(): continue
    html = fp.read_text(encoding="utf-8", errors="ignore")
    r = validate_page(html, slug=s)
    if r.passed:
        n_pass += 1
    else:
        results[s] = r.failures
        for f in r.failures:
            # Normalize to top-level category
            key = f.split(":")[0]
            fail_counter[key] += 1

print(f"\n=== GATE SWEEP RESULTS ===")
print(f"PASSED: {n_pass}/{len(slugs)} ({100*n_pass/len(slugs):.1f}%)")
print(f"FAILED: {len(results)}/{len(slugs)} ({100*len(results)/len(slugs):.1f}%)")

print(f"\nFailure breakdown (top categories):")
for cat, n in fail_counter.most_common():
    print(f"  {n:5d}  {cat}")

# Save full report
(DEPLOY / "_ITER36_GATE_SWEEP.json").write_text(
    json.dumps({"n_total": len(slugs), "n_pass": n_pass, "n_fail": len(results),
                "failure_categories": dict(fail_counter), "per_page": results},
               ensure_ascii=False, indent=2),
    encoding="utf-8"
)
print(f"\nSaved: _ITER36_GATE_SWEEP.json")
