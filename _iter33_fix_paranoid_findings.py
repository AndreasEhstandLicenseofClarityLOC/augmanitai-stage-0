#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 33 — Fix paranoid-audit findings.

Three fixes:
1. CANONICAL URL — replace augmanitai.com/<slug>.html → GitHub-Pages URL (6209 pages)
2. PHANTOM IDs — strip "Related to AUG-XXXX (Title), NEO-YYYY..." references
   for IDs not in our atlas (1848 pages affected)
3. DUPLICATE TITLES — keep shorter slug, delete "the-X" duplicates when "X" exists (878 groups)
"""
import re, json, shutil, io, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")
ATLAS = DEPLOY / "atlas"
BASE_URL = "https://andreasehstandlicenseofclarityloc.github.io/augmanitai-stage-0"


def fix_canonical(c, slug):
    """Replace augmanitai.com/<anything>.html with GitHub-Pages URL."""
    correct_canonical = f"{BASE_URL}/atlas/{slug}/"
    # canonical link
    c = re.sub(
        r'<link rel=["\']canonical["\'][^>]*href=["\'][^"\']*augmanitai\.com/[^"\']+["\'][^>]*>',
        f'<link rel="canonical" href="{correct_canonical}">',
        c
    )
    # og:url
    c = re.sub(
        r'(<meta property=["\']og:url["\'][^>]*content=["\'])[^"\']*augmanitai\.com/[^"\']+(["\'])',
        rf'\1{correct_canonical}\2',
        c
    )
    # alternate hreflangs (the V11.2 has many) — replace augmanitai.com/<slug>.html → canonical
    c = re.sub(
        r'(<link rel=["\']alternate["\'][^>]*hreflang=["\'][^"\']+["\'][^>]*href=["\'])[^"\']*augmanitai\.com/[^"\']+(["\'])',
        rf'\1{correct_canonical}\2',
        c
    )
    # andreasehstandlicenseofclarityloc.github.io/augmanitai-tools/X.html → /augmanitai-stage-0/atlas/X/
    c = re.sub(
        r'andreasehstandlicenseofclarityloc\.github\.io/augmanitai-tools/[^"\']+\.html',
        correct_canonical.replace("https://", ""),
        c
    )
    return c


def strip_phantom_ids(c, existing_ids):
    """Strip 'Related to AUG-XXXX (Title), NEO-YYYY (Title)' references for non-existent IDs."""
    # Pattern: "Related to AUG-NNNN (Title), AUG-MMMM (Title), and AUG-PPPP (Title)."
    # Strip the whole phrase if all referenced IDs are phantoms.
    def replacer(m):
        phrase = m.group(0)
        ids = re.findall(r"\b(AUG|NEO|PER|RPH|EDU|ROB)-(\d+)\b", phrase)
        if not ids:
            return phrase
        full_ids = [f"{a}-{b}" for a, b in ids]
        phantom = [i for i in full_ids if i not in existing_ids]
        if len(phantom) == len(full_ids):
            return ""  # all phantom → strip
        return phrase  # at least one is real, keep
    c = re.sub(
        r"\s*Related to (?:AUG|NEO|PER|RPH|EDU|ROB)-\d+\s*\([^)]*\)(?:,?\s*(?:and\s+)?(?:AUG|NEO|PER|RPH|EDU|ROB)-\d+\s*\([^)]*\))*\.?",
        replacer, c
    )
    return c


def collect_existing_ids():
    ids = set()
    for d in ATLAS.iterdir():
        if not d.is_dir(): continue
        fp = d / "index.html"
        if not fp.exists(): continue
        c = fp.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r'"termCode"\s*:\s*"([A-Z]+-\d+)"', c):
            ids.add(m.group(1))
    return ids


def main():
    print("Collecting existing term-IDs...")
    existing_ids = collect_existing_ids()
    print(f"  {len(existing_ids)} term-IDs in atlas")

    # === STEP A: Dedupe duplicate-title pairs ===
    print("\n=== STEP A: Dedupe duplicate titles ===")
    audit = json.load(open(DEPLOY / "_ITER32_PARANOID_AUDIT.json", encoding="utf-8"))
    dup_groups = audit["duplicate_titles"]
    to_delete = set()
    kept = 0
    for title, slugs_list in dup_groups.items():
        # Prefer shorter slug (no "the-" prefix). Among equally short, alphabetically first.
        slugs_sorted = sorted(slugs_list, key=lambda s: (s.startswith("the-"), len(s), s))
        keep = slugs_sorted[0]
        kept += 1
        for s in slugs_sorted[1:]:
            to_delete.add(s)
    print(f"  Kept: {kept} canonical slugs (most concise)")
    print(f"  To delete: {len(to_delete)} dup-slugs")

    n_deleted = 0
    for s in to_delete:
        d = ATLAS / s
        if d.exists() and d.is_dir():
            shutil.rmtree(d)
            n_deleted += 1
    print(f"  Deleted: {n_deleted}")

    # === STEP B: Fix canonical + strip phantom-IDs in remaining pages ===
    print("\n=== STEP B + C: Fix canonical + strip phantom-IDs ===")
    remaining = sorted([d.name for d in ATLAS.iterdir() if d.is_dir()])
    print(f"  Atlas remaining: {len(remaining)}")
    n_canonical_fixed = 0
    n_phantom_stripped = 0
    for s in remaining:
        fp = ATLAS / s / "index.html"
        if not fp.exists(): continue
        c = fp.read_text(encoding="utf-8", errors="ignore")
        orig = c
        c2 = fix_canonical(c, s)
        if c2 != c:
            n_canonical_fixed += 1
            c = c2
        c3 = strip_phantom_ids(c, existing_ids)
        if c3 != c:
            n_phantom_stripped += 1
            c = c3
        if c != orig:
            fp.write_text(c, encoding="utf-8")

    print(f"  canonical URLs fixed: {n_canonical_fixed}")
    print(f"  phantom-IDs stripped: {n_phantom_stripped}")

    final = sum(1 for x in ATLAS.iterdir() if x.is_dir())
    print(f"\n=== ATLAS FINAL: {final} pages ===")


if __name__ == "__main__":
    main()
