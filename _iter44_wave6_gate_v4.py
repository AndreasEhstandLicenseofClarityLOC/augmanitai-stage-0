#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 44 — Welle 6: V5_ENRICHMENTS rest pool through Gate v3 + Gate v4 extension.

Pre-filter:
- Quality (def_len>=100, no template-stubs, no hard-blocks, no themes)
- Gate v4 extension (no children, no violence, no instruction, no du-ansprache)
- Pre-Publish Gate (47 checks)

Compute-sparsam: target ~8000 pages this wave.
"""
import json, re, io, sys, html as htmllib, importlib.util
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude")
DEPLOY = ROOT / "_AKTIV/_FIRST_NETWORK_BUILD/_DEPLOY_STAGE_0_50TERMS"
ATLAS = DEPLOY / "atlas"
POOL_DIR = ROOT / "01_AUGMANITAI_KERN/V5_ENRICHMENTS"

# Load gate v4 extension (no-dataclass module, safe to exec-import)
spec = importlib.util.spec_from_file_location("_gate_v4", str(DEPLOY / "_pre_publish_gate_v4_extension.py"))
_v4 = importlib.util.module_from_spec(spec); spec.loader.exec_module(_v4)
validate_extension = _v4.validate_extension

# Load base gate (which uses GateResult)
spec2 = importlib.util.spec_from_file_location("_gate_base", str(DEPLOY / "_pre_publish_gate.py"))
_base = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(_base)
validate_page = _base.validate_page

# Load build_page from iter37 via exec
def _import_build_page():
    src = (DEPLOY / "_iter37_gate_filtered_generator.py").read_text(encoding="utf-8")
    # Strip stdout reassignment + main block
    src_lines = []
    skip_main = False
    for line in src.splitlines(keepends=True):
        if "sys.stdout = io.TextIOWrapper" in line:
            continue
        if line.startswith('if __name__ == "__main__":'):
            skip_main = True
            continue
        if skip_main:
            continue
        src_lines.append(line)
    src_clean = "".join(src_lines)
    ns = {"__name__": "_iter37_inline", "__file__": str(DEPLOY / "_iter37_gate_filtered_generator.py"),
          "validate_page": validate_page}
    exec(compile(src_clean, str(DEPLOY / "_iter37_gate_filtered_generator.py"), "exec"), ns)
    return ns["build_page"]


_build_page = _import_build_page()


def clean_slug(s):
    s = s.lower().strip()
    if s.endswith(".html"): s = s[:-5]
    s = re.sub(r"[^a-z0-9-]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


STRICT_STUB = [
    re.compile(r"May describe|^Users .{1,30} (collectively|generally|typically)|^The phenomenon catalogued as|^A domain-specific term|^A framework term for", re.IGNORECASE),
    re.compile(r"The measurable .{1,40} between AI-augmented|covering the theory and practice of|Educational methodology within .{1,60} covering|Domain-specific this field|Established practice in addressing this field|Theoretical and applied knowledge of this field|AI-powered quality assurance$|\bperformance differential\b|\boptimization plateau\b|\bprecision asymmetry\b", re.IGNORECASE),
]
THEME_BLOCK = re.compile(
    r"funeral|bestatter|undertaker|mortuary|cemeter|"
    r"mind-upload|consciousness-upload|digital-immortality|"
    r"insurance-underwrit|premium-deni|"
    r"tibet|taiwan independ|hong kong|xinjiang|tiananmen|falun|"
    r"genocid|massacre|self-harm|self-injur|"
    r"abortion|pornograph|methylphenidat|ritalin|gabapentin|topiramat|fluoxetin|"
    r"white genocide|great replacement|racial purity|pedophil|"
    # New themes per Andy directive (medical/military/legal)
    r"weapon\s+system|kill\s+chain|combat\s+AI|warfare|"
    r"clinical\s+advice|treatment\s+protocol|prescription|"
    r"legal\s+advice|litigation\s+strategy",
    re.IGNORECASE
)


def quality(en, defn):
    if not en or not defn: return False, "empty"
    if len(defn) < 100: return False, "short"
    for pat in STRICT_STUB:
        if pat.search(defn): return False, "stub"
    if re.search(r"\b(suicide|kill|rape|abuse|porn|child|minor|nazi|terror|exploit)\b", en+defn, re.IGNORECASE):
        return False, "hard_block"
    if THEME_BLOCK.search(en + " " + defn):
        return False, "theme_block"
    return True, None


def harvest():
    existing = {d.name for d in ATLAS.iterdir() if d.is_dir()}
    files = sorted(POOL_DIR.glob("*.json"))
    print(f"Pool files: {len(files)}, atlas existing: {len(existing)}")
    candidates = []
    fail = Counter()
    for fp in files:
        try:
            d = json.load(open(fp, encoding="utf-8"))
        except: fail["parse"] += 1; continue
        eng = d.get("name", "")
        slug = clean_slug(eng) if eng else ""
        if not slug or slug in existing:
            fail["no_slug_or_online"] += 1; continue
        cl = d.get("cross_lingual", {})
        defn = ""
        if isinstance(cl, dict):
            en_part = cl.get("en", {})
            if isinstance(en_part, dict): defn = en_part.get("definition", "")
        ok, reason = quality(eng, defn)
        if not ok: fail[reason] += 1; continue
        candidates.append({
            "id": d.get("termCode", ""), "slug": slug, "en": eng, "def_en": defn,
            "category": d.get("termCode", "").split("-")[0] or "AUGMANITAI",
        })
    print(f"After quality+theme filter: {len(candidates)}")
    for k, v in fail.most_common(5): print(f"  fail.{k}: {v}")
    return candidates


def main():
    LIMIT = 8000
    candidates = harvest()
    if len(candidates) > LIMIT:
        # Take first N (by alphabetical file-sort, stable)
        candidates = candidates[:LIMIT]
        print(f"Limiting to {LIMIT}")

    by_cat = defaultdict(list)
    for c in candidates: by_cat[c["category"]].append(c)

    atlas_snap = {d.name for d in ATLAS.iterdir() if d.is_dir()}
    n_pass = 0
    n_fail = 0
    fail_breakdown = Counter()

    for c in candidates:
        # 1. Quality check on definition for gate-v4 (children/violence/etc.)
        ext_fails = validate_extension("<body>" + c["def_en"] + "</body>", slug=c["slug"], definition=c["def_en"])
        if ext_fails:
            n_fail += 1
            for f in ext_fails: fail_breakdown[f.split(":")[0]] += 1
            continue

        sibs = [s for s in by_cat[c["category"]] if s["slug"] != c["slug"]][:6]
        page_html = _build_page(c["id"], c["slug"], c["en"], c["def_en"], c["category"], sibs)

        # 2. Base gate (47 checks)
        base_result = validate_page(page_html, slug=c["slug"], definition=c["def_en"], atlas_slug_snapshot=atlas_snap)
        # 3. Extension gate on full page
        ext_fails2 = validate_extension(page_html, slug=c["slug"], definition=c["def_en"])

        if base_result.passed and not ext_fails2:
            d = ATLAS / c["slug"]
            d.mkdir(exist_ok=True)
            (d / "index.html").write_text(page_html, encoding="utf-8")
            atlas_snap.add(c["slug"])
            n_pass += 1
            if n_pass % 500 == 0: print(f"  ...{n_pass}")
        else:
            n_fail += 1
            for f in base_result.failures: fail_breakdown[f.split(":")[0]] += 1
            for f in ext_fails2: fail_breakdown[f.split(":")[0]] += 1

    print(f"\n=== Welle 6 ===")
    print(f"  PASS: {n_pass}")
    print(f"  FAIL: {n_fail}")
    if fail_breakdown:
        for k, v in fail_breakdown.most_common(10): print(f"    {v:5d}  {k}")

    final = sum(1 for d in ATLAS.iterdir() if d.is_dir())
    print(f"\nAtlas total: {final}")


if __name__ == "__main__":
    main()
