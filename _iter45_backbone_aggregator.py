#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 45 — Aggregate all backbone variants + V10_BUILD_PROGRESS to find new terms.

62 backbone variants × ~5000 terms + 50 V10 build_progress files. Most overlap with
LATEST backbone (already mined). Goal: dedupe across all + filter for new terms only.
"""
import json, re, io, sys, importlib.util
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude")
DEPLOY = ROOT / "_AKTIV/_FIRST_NETWORK_BUILD/_DEPLOY_STAGE_0_50TERMS"
ATLAS = DEPLOY / "atlas"

spec = importlib.util.spec_from_file_location("_g4", str(DEPLOY / "_pre_publish_gate_v4_extension.py"))
_v4 = importlib.util.module_from_spec(spec); spec.loader.exec_module(_v4)
validate_extension = _v4.validate_extension

spec2 = importlib.util.spec_from_file_location("_gb", str(DEPLOY / "_pre_publish_gate.py"))
_base = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(_base)
validate_page = _base.validate_page


def _import_build_page():
    src = (DEPLOY / "_iter37_gate_filtered_generator.py").read_text(encoding="utf-8")
    src_lines = []
    skip = False
    for line in src.splitlines(keepends=True):
        if "sys.stdout = io.TextIOWrapper" in line: continue
        if line.startswith('if __name__ == "__main__":'):
            skip = True; continue
        if skip: continue
        src_lines.append(line)
    ns = {"__name__": "_g37_inline", "__file__": str(DEPLOY / "_iter37_gate_filtered_generator.py"),
          "validate_page": validate_page}
    exec(compile("".join(src_lines), str(DEPLOY / "_iter37_gate_filtered_generator.py"), "exec"), ns)
    return ns["build_page"]


_build_page = _import_build_page()


def clean_slug(s):
    s = s.lower().strip()
    if s.endswith(".html"): s = s[:-5]
    s = re.sub(r"[^a-z0-9-]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


STUB = re.compile(r"May describe|^Users .{1,30} (collectively|generally|typically)|^The phenomenon catalogued as|^A domain-specific term|^A framework term for|The measurable .{1,40} between AI-augmented|covering the theory and practice of", re.IGNORECASE)
THEME = re.compile(
    r"funeral|bestatter|undertaker|mortuary|cemeter|mind-upload|consciousness-upload|"
    r"digital-immortality|insurance-underwrit|premium-deni|tibet|taiwan independ|"
    r"hong kong|xinjiang|tiananmen|falun|genocid|massacre|self-harm|self-injur|"
    r"abortion|pornograph|methylphenidat|ritalin|gabapentin|topiramat|fluoxetin|"
    r"white genocide|great replacement|racial purity|pedophil|"
    r"weapon\s+system|kill\s+chain|combat\s+AI|warfare|clinical\s+advice|"
    r"treatment\s+protocol|prescription|legal\s+advice|litigation\s+strategy",
    re.IGNORECASE
)

def quality(en, defn):
    if not en or not defn: return False
    if len(defn) < 100: return False
    if STUB.search(defn): return False
    if re.search(r"\b(suicide|kill|rape|abuse|porn|child|minor|nazi|terror|exploit)\b", en+defn, re.IGNORECASE): return False
    if THEME.search(en + " " + defn): return False
    return True


def harvest_all():
    existing = {d.name for d in ATLAS.iterdir() if d.is_dir()}
    seen_slugs = set()
    candidates = []
    sources = [
        *sorted(Path(ROOT / "01_AUGMANITAI_KERN").glob("augmanitai_taxonomy_backbone*.json")),
        *sorted(Path(ROOT / "01_AUGMANITAI_KERN/V10_BUILD_PROGRESS").glob("**/*.json")),
    ]
    print(f"Scanning {len(sources)} backbone-variant files...")
    n_files_read = 0
    for fp in sources:
        try:
            d = json.load(open(fp, encoding="utf-8"))
        except: continue
        if not isinstance(d, dict): continue
        terms = d.get("terms", [])
        if not isinstance(terms, list): continue
        n_files_read += 1
        for t in terms:
            eng = t.get("english_name", "")
            if not eng: continue
            slug = clean_slug(eng)
            if not slug or slug in existing or slug in seen_slugs: continue
            seen_slugs.add(slug)
            defs = t.get("definitions", {})
            defn = defs.get("en", "") if isinstance(defs, dict) else ""
            if not quality(eng, defn): continue
            meta = t.get("meta", {})
            if isinstance(meta, dict) and meta.get("risk_level") in ("RISK4", "RISK5"): continue
            candidates.append({
                "id": t.get("canonical_id", ""), "slug": slug, "en": eng, "def_en": defn,
                "category": t.get("domain", "AUGMANITAI_CORE"),
            })
    print(f"Files read: {n_files_read}")
    print(f"Unique new candidates after quality: {len(candidates)}")
    return candidates


def main():
    cands = harvest_all()
    if not cands:
        print("Pool exhausted — no new candidates."); return
    LIMIT = 8000
    if len(cands) > LIMIT:
        cands = cands[:LIMIT]
        print(f"Limit {LIMIT}")

    atlas_snap = {d.name for d in ATLAS.iterdir() if d.is_dir()}
    by_cat = defaultdict(list)
    for c in cands: by_cat[c["category"]].append(c)

    n_pass = 0
    n_fail = 0
    fail_breakdown = Counter()
    for c in cands:
        ext_fails = validate_extension("<body>" + c["def_en"] + "</body>", definition=c["def_en"])
        if ext_fails:
            n_fail += 1
            for f in ext_fails: fail_breakdown[f.split(":")[0]] += 1
            continue
        sibs = [s for s in by_cat[c["category"]] if s["slug"] != c["slug"]][:6]
        page_html = _build_page(c["id"], c["slug"], c["en"], c["def_en"], c["category"], sibs)
        base_r = validate_page(page_html, slug=c["slug"], definition=c["def_en"], atlas_slug_snapshot=atlas_snap)
        ext_r = validate_extension(page_html, slug=c["slug"], definition=c["def_en"])
        if base_r.passed and not ext_r:
            d = ATLAS / c["slug"]
            d.mkdir(exist_ok=True)
            (d / "index.html").write_text(page_html, encoding="utf-8")
            atlas_snap.add(c["slug"])
            n_pass += 1
            if n_pass % 500 == 0: print(f"  ...{n_pass}")
        else:
            n_fail += 1
            for f in base_r.failures: fail_breakdown[f.split(":")[0]] += 1
            for f in ext_r: fail_breakdown[f.split(":")[0]] += 1

    print(f"\nPASS: {n_pass}  FAIL: {n_fail}")
    for k, v in fail_breakdown.most_common(): print(f"  {v:5d}  {k}")
    print(f"\nAtlas: {sum(1 for d in ATLAS.iterdir() if d.is_dir())}")


if __name__ == "__main__":
    main()
