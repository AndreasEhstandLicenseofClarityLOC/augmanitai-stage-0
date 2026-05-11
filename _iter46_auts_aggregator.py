#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scan AUTS_V2_WIP + remaining backbone variants for new terms."""
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
    lines = []
    skip = False
    for ln in src.splitlines(keepends=True):
        if "sys.stdout = io.TextIOWrapper" in ln: continue
        if ln.startswith('if __name__ == "__main__":'): skip = True; continue
        if skip: continue
        lines.append(ln)
    ns = {"__name__":"_inl","__file__":str(DEPLOY / "_iter37_gate_filtered_generator.py"),"validate_page":validate_page}
    exec(compile("".join(lines), str(DEPLOY / "_iter37_gate_filtered_generator.py"),"exec"), ns)
    return ns["build_page"]
_build_page = _import_build_page()

def clean_slug(s):
    s = s.lower().strip()
    if s.endswith(".html"): s = s[:-5]
    s = re.sub(r"[^a-z0-9-]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s

STUB = re.compile(r"May describe|^Users .{1,30} (collectively|generally|typically)|^The phenomenon catalogued as|^A domain-specific term|^A framework term for|The measurable .{1,40} between AI-augmented|covering the theory and practice of", re.IGNORECASE)
THEME = re.compile(r"funeral|bestatter|undertaker|mortuary|cemeter|mind-upload|consciousness-upload|digital-immortality|insurance-underwrit|premium-deni|tibet|taiwan independ|hong kong|xinjiang|tiananmen|falun|genocid|massacre|self-harm|self-injur|abortion|pornograph|methylphenidat|ritalin|gabapentin|topiramat|fluoxetin|white genocide|great replacement|racial purity|pedophil|weapon\s+system|kill\s+chain|combat\s+AI|warfare|clinical\s+advice|treatment\s+protocol|prescription|legal\s+advice|litigation\s+strategy", re.IGNORECASE)

def quality(en, defn):
    if not en or not defn: return False
    if len(defn) < 100: return False
    if STUB.search(defn): return False
    if re.search(r"\b(suicide|kill|rape|abuse|porn|child|minor|nazi|terror|exploit)\b", en+defn, re.IGNORECASE): return False
    if THEME.search(en + " " + defn): return False
    return True

# Scan ALL JSON files in 01_AUGMANITAI_KERN with terms-list >= 1000
existing = {d.name for d in ATLAS.iterdir() if d.is_dir()}
seen_slugs = set()
candidates = []
n_files = 0
n_terms_seen = 0
for fp in Path(ROOT / "01_AUGMANITAI_KERN").glob("**/*.json"):
    if fp.stat().st_size < 100000: continue
    try:
        d = json.load(open(fp, encoding="utf-8"))
    except: continue
    if not isinstance(d, dict): continue
    terms = d.get("terms", [])
    if not isinstance(terms, list) or len(terms) < 1000: continue
    n_files += 1
    for t in terms:
        n_terms_seen += 1
        eng = t.get("english_name", "")
        if not eng: continue
        slug = clean_slug(eng)
        if not slug or slug in existing or slug in seen_slugs: continue
        seen_slugs.add(slug)
        defs = t.get("definitions", {})
        defn = defs.get("en", "") if isinstance(defs, dict) else ""
        if not quality(eng, defn): continue
        meta = t.get("meta", {})
        if isinstance(meta, dict) and meta.get("risk_level") in ("RISK4","RISK5"): continue
        candidates.append({"id":t.get("canonical_id",""),"slug":slug,"en":eng,"def_en":defn,
                            "category":t.get("domain","AUGMANITAI_CORE")})

print(f"Files scanned: {n_files}")
print(f"Terms seen: {n_terms_seen}")
print(f"Unique new candidates: {len(candidates)}")

LIMIT = 8000
if len(candidates) > LIMIT:
    candidates = candidates[:LIMIT]
    print(f"Limit {LIMIT}")

atlas_snap = set(existing)
by_cat = defaultdict(list)
for c in candidates: by_cat[c["category"]].append(c)

n_pass = 0
n_fail = 0
fb = Counter()
for c in candidates:
    ext = validate_extension("<body>" + c["def_en"] + "</body>", definition=c["def_en"])
    if ext:
        n_fail += 1
        for f in ext: fb[f.split(":")[0]] += 1
        continue
    sibs = [s for s in by_cat[c["category"]] if s["slug"] != c["slug"]][:6]
    page = _build_page(c["id"], c["slug"], c["en"], c["def_en"], c["category"], sibs)
    br = validate_page(page, slug=c["slug"], definition=c["def_en"], atlas_slug_snapshot=atlas_snap)
    er = validate_extension(page, slug=c["slug"], definition=c["def_en"])
    if br.passed and not er:
        d = ATLAS / c["slug"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(page, encoding="utf-8")
        atlas_snap.add(c["slug"])
        n_pass += 1
        if n_pass % 500 == 0: print(f"  ...{n_pass}")
    else:
        n_fail += 1
        for f in br.failures: fb[f.split(":")[0]] += 1
        for f in er: fb[f.split(":")[0]] += 1

print(f"\nPASS: {n_pass}  FAIL: {n_fail}")
for k, v in fb.most_common(): print(f"  {v:5d}  {k}")
print(f"\nAtlas: {sum(1 for d in ATLAS.iterdir() if d.is_dir())}")
