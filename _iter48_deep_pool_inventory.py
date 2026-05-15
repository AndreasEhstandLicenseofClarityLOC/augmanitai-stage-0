#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 48 — DEEP POOL INVENTORY across whole Claude/ workspace.

Find every JSON/CSV/MD that contains term-like records, count what's quality+gate-eligible
and not yet online in atlas/.
"""
import json, re, io, sys
from pathlib import Path
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude")
DEPLOY = ROOT / "_AKTIV/_FIRST_NETWORK_BUILD/_DEPLOY_STAGE_0_50TERMS"
ATLAS = DEPLOY / "atlas"

existing = {d.name for d in ATLAS.iterdir() if d.is_dir()}
print(f"Atlas online: {len(existing)}")

def slugify(s):
    s = s.lower().strip()
    if s.endswith(".html"): s = s[:-5]
    s = re.sub(r"[^a-z0-9-]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s

STUB = re.compile(r"May describe|^Users .{1,30} (collectively|generally|typically)|^The phenomenon catalogued as|^A domain-specific term|^A framework term for|The measurable .{1,40} between AI-augmented|covering the theory and practice of", re.IGNORECASE)
HARD_BLOCK = re.compile(r"\b(suicide|kill|rape|abuse|porn|child|minor|nazi|terror|exploit)\b", re.IGNORECASE)
THEME = re.compile(r"funeral|bestatter|undertaker|mortuary|cemeter|mind-upload|consciousness-upload|digital-immortality|insurance-underwrit|premium-deni|tibet|taiwan independ|hong kong|xinjiang|tiananmen|falun|genocid|massacre|self-harm|self-injur|abortion|pornograph|methylphenidat|ritalin|gabapentin|topiramat|fluoxetin|white genocide|great replacement|racial purity|pedophil|weapon\s+system|kill\s+chain|combat\s+AI|warfare|clinical\s+advice|treatment\s+protocol|prescription|legal\s+advice|litigation\s+strategy", re.IGNORECASE)


def quality(en, defn):
    if not en or not defn: return False
    if len(defn) < 80: return False
    if STUB.search(defn): return False
    if HARD_BLOCK.search(en + " " + defn): return False
    if THEME.search(en + " " + defn): return False
    return True


# Search dirs (everything under Claude root, but skip atlas/ itself and worker_outputs)
SKIP_DIRS = {"atlas", "_worker_outputs", ".git", "node_modules", "__pycache__"}
SEARCH_ROOTS = [ROOT / "01_AUGMANITAI_KERN", ROOT / "02_NEOMANITAI", ROOT / "03_AKADEMISCH",
                ROOT / "04_PRODUKTE", ROOT / "12_ARCHIV"]


def extract_records(d):
    """Yield (english_name, definition_en) tuples from dict/list."""
    if isinstance(d, dict):
        # Try standard keys
        en = d.get("english_name") or d.get("name") or d.get("en") or d.get("term") or d.get("title")
        defs = d.get("definitions") or d.get("definition") or d.get("def_en") or d.get("def") or d.get("description")
        if isinstance(defs, dict):
            defn = defs.get("en") or defs.get("english") or ""
        elif isinstance(defs, str):
            defn = defs
        else:
            defn = ""
        if en and defn:
            yield (en, defn)
        # Recurse on container keys
        for key in ("terms", "entries", "items", "data", "records", "glossary", "concepts", "results"):
            if key in d and isinstance(d[key], list):
                for it in d[key]:
                    yield from extract_records(it)
    elif isinstance(d, list):
        for it in d[:5000]:  # cap
            yield from extract_records(it)


total_seen = 0
new_quality = []
seen_slugs = set()
files_scanned = 0
big_pools = []

for root in SEARCH_ROOTS:
    if not root.exists(): continue
    for fp in root.rglob("*.json"):
        # Skip large dirs we know are template-stub generators
        if any(s in str(fp) for s in ["NEOMANITAI_400", "NEOMANITAI_OUTPUT_V", "V5_ENRICHMENTS"]):
            continue  # already inventoried
        sz = fp.stat().st_size
        if sz < 5000 or sz > 100_000_000: continue
        try:
            d = json.load(open(fp, encoding="utf-8"))
        except: continue
        files_scanned += 1
        count_local = 0
        for en, defn in extract_records(d):
            total_seen += 1
            count_local += 1
            slug = slugify(en)
            if not slug or slug in existing or slug in seen_slugs: continue
            if not quality(en, defn): continue
            seen_slugs.add(slug)
            new_quality.append({"slug": slug, "en": en, "def_en": defn, "source": str(fp.relative_to(ROOT))})
        if count_local > 100:
            big_pools.append((count_local, str(fp.relative_to(ROOT))))

print(f"\nFiles scanned: {files_scanned}")
print(f"Term records seen: {total_seen}")
print(f"NEW quality-passing (not yet online): {len(new_quality)}")
print(f"\nTop 15 big pools (>100 terms):")
big_pools.sort(reverse=True)
for n, p in big_pools[:15]:
    print(f"  {n:6d}  {p}")

# Source histogram of new_quality
from collections import Counter
src_counts = Counter(c["source"].split("\\")[0] for c in new_quality)
print(f"\nNEW candidates by top-level dir:")
for d, c in src_counts.most_common():
    print(f"  {c:5d}  {d}")

# Save the pool for next wave
import json as J
(DEPLOY / "_ITER48_DEEP_POOL.json").write_text(
    J.dumps({"total_seen": total_seen, "new_quality_count": len(new_quality),
             "files_scanned": files_scanned,
             "candidates": new_quality},
            ensure_ascii=False, indent=2),
    encoding="utf-8"
)
print(f"\nSaved: _ITER48_DEEP_POOL.json")
