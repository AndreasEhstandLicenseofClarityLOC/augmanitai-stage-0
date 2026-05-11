#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 43 — Apply Gate v4 extension to all 17056 live pages.

Flag and delete pages that fail:
- Children mentions
- Violence (physical/psychological)
- Instruction patterns (how to / step-by-step / imperative)
- Du-Ansprache (second-person addressing in body)
- Readability too low (Flesch < 20)
"""
import re, json, shutil, io, sys, importlib.util
from pathlib import Path
from collections import defaultdict, Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")
ATLAS = DEPLOY / "atlas"

# Load extension module (no dataclass, safe to exec-import)
spec = importlib.util.spec_from_file_location("_gate_v4", str(DEPLOY / "_pre_publish_gate_v4_extension.py"))
_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_mod)
validate_extension = _mod.validate_extension


def extract_definition(html):
    m = re.search(r"<h2[^>]*>(?:<span[^>]*>[^<]*</span>)?\s*Definition\s*</h2>\s*<p>([^<]+)</p>", html, re.DOTALL)
    if m: return m.group(1)
    m = re.search(r'<div class=["\']definition["\']>([^<]+)</div>', html, re.DOTALL)
    if m: return m.group(1)
    m = re.search(r'<meta name=["\']description["\'] content=["\']([^"\']+)["\']', html)
    if m: return m.group(1)
    return ""


def main():
    slugs = sorted([d.name for d in ATLAS.iterdir() if d.is_dir()])
    print(f"Gate v4 sweep on {len(slugs)} pages...")

    flagged = {}
    counters = Counter()
    for i, s in enumerate(slugs):
        if i and i % 2000 == 0: print(f"  ...{i}/{len(slugs)}")
        fp = ATLAS / s / "index.html"
        if not fp.exists(): continue
        html = fp.read_text(encoding="utf-8", errors="ignore")
        defn = extract_definition(html)
        fails = validate_extension(html, slug=s, definition=defn)
        if fails:
            flagged[s] = fails
            for f in fails:
                counters[f.split(":")[0]] += 1

    n = len(slugs)
    print(f"\n=== GATE v4 SWEEP ===")
    print(f"Total flagged: {len(flagged)} ({100*len(flagged)/n:.1f}%)")
    for k, c in counters.most_common(): print(f"  {c:5d}  {k}")

    # Save report
    (DEPLOY / "_ITER43_GATE_V4_REPORT.json").write_text(
        json.dumps({"n_total": n, "n_flagged": len(flagged),
                    "counters": dict(counters), "flagged": flagged},
                   ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"\nSaved: _ITER43_GATE_V4_REPORT.json")

    # AUTO-DELETE all flagged
    print(f"\nDeleting {len(flagged)} flagged pages...")
    n_del = 0
    for s in flagged:
        d = ATLAS / s
        if d.exists():
            shutil.rmtree(d)
            n_del += 1
    print(f"Deleted: {n_del}")
    final = sum(1 for d in ATLAS.iterdir() if d.is_dir())
    print(f"Atlas final: {final}")


if __name__ == "__main__":
    main()
