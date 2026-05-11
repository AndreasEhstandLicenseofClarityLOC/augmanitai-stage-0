#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 40 — Welle 5: V5_ENRICHMENTS Pool with stricter quality filter + gate.

V5_ENRICHMENTS has 25921 single-JSON-files with ISO 704/1087/30042 references,
covering diverse domains: Sport, Agriculture, Cartography, Cybersecurity, Education,
Cooking, Crafts, Tennis, Cycling, etc.

Stricter filter rejects formulaic stubs like:
  - "Domain-specific X" prefix
  - "Established practice in addressing this field"
  - "covering the theory and practice of X"
  - "Educational methodology within X covering"
  - "this field" generic placeholder
  - "AI-powered quality assurance" with no specifics
"""
import json, re, io, sys, html as htmllib
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude")
DEPLOY = ROOT / "_AKTIV/_FIRST_NETWORK_BUILD/_DEPLOY_STAGE_0_50TERMS"
ATLAS = DEPLOY / "atlas"
POOL_DIR = ROOT / "01_AUGMANITAI_KERN/V5_ENRICHMENTS"

# Direct subprocess call instead of import — avoids stdout-reassignment + dataclass bugs
sys.path.insert(0, str(DEPLOY))

# Use subprocess to run gate validation as needed.
# Inline minimal build_page + clean_slug from iter37 here.
def _clean_slug(s):
    s = s.lower().strip()
    if s.endswith(".html"): s = s[:-5]
    s = re.sub(r"[^a-z0-9-]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


# Inline gate
def _import_gate():
    """Read _pre_publish_gate.py source, exec into clean namespace."""
    src = (DEPLOY / "_pre_publish_gate.py").read_text(encoding="utf-8")
    ns = {"__name__": "_gate_inline", "__file__": str(DEPLOY / "_pre_publish_gate.py")}
    exec(compile(src, str(DEPLOY / "_pre_publish_gate.py"), "exec"), ns)
    return ns["validate_page"]


validate_page = _import_gate()

# Inline build_page from iter37
def _import_build_page():
    src = (DEPLOY / "_iter37_gate_filtered_generator.py").read_text(encoding="utf-8")
    # Strip the if __name__ == __main__ block and the stdout reassignment
    src = re.sub(r"sys\.stdout = io\.TextIOWrapper.*?\)\n", "", src)
    src = re.sub(r'if __name__ == "__main__":.*$', "", src, flags=re.DOTALL)
    ns = {"__name__": "_iter37_inline", "__file__": str(DEPLOY / "_iter37_gate_filtered_generator.py"),
          "validate_page": validate_page}
    exec(compile(src, str(DEPLOY / "_iter37_gate_filtered_generator.py"), "exec"), ns)
    return ns["build_page"]


_build_page = _import_build_page()

STRICT_STUB_RES = [
    re.compile(r"May describe|^Users .{1,30} (collectively|generally|typically)", re.IGNORECASE),
    re.compile(r"^The phenomenon catalogued as|^A domain-specific term|^A framework term for", re.IGNORECASE),
    re.compile(r"The measurable .{1,40} between AI-augmented", re.IGNORECASE),
    re.compile(r"covering the theory and practice of", re.IGNORECASE),
    re.compile(r"Educational methodology within .{1,60} covering", re.IGNORECASE),
    re.compile(r"Domain-specific this field", re.IGNORECASE),
    re.compile(r"Established practice in addressing this field", re.IGNORECASE),
    re.compile(r"Theoretical and applied knowledge of this field", re.IGNORECASE),
    re.compile(r"AI-powered quality assurance$", re.IGNORECASE),
    re.compile(r"\bperformance differential\b", re.IGNORECASE),
    re.compile(r"\boptimization plateau\b", re.IGNORECASE),
    re.compile(r"\bprecision asymmetry\b", re.IGNORECASE),
]


def quality_strict(en, defn):
    if not en or not defn: return False, "empty"
    if len(defn) < 100: return False, "short_lt_100"
    for pat in STRICT_STUB_RES:
        if pat.search(defn): return False, "template_stub"
    if re.search(r"\b(suicide|kill|rape|abuse|porn|child|minor|nazi|terror|exploit)\b", en + defn, re.IGNORECASE): return False, "hard_block"
    # Block thematic risk topics (per Andy directive)
    THEME_BLOCK = re.compile(r"funeral|bestatter|undertaker|mortuary|cemeter|"
                              r"mind-upload|consciousness-upload|digital-immortality|"
                              r"insurance-underwrit|premium-deni|"
                              r"tibet|taiwan independ|hong kong|xinjiang|tiananmen|falun|"
                              r"genocid|massacre|self-harm|self-injur|"
                              r"abortion|pornograph|methylphenidat|ritalin|gabapentin|topiramat|fluoxetin|"
                              r"white genocide|great replacement|racial purity|"
                              r"pedophil", re.IGNORECASE)
    if THEME_BLOCK.search(en + " " + defn):
        return False, "thematic_block"
    return True, None


def harvest_v5_pool(limit=None):
    files = sorted(POOL_DIR.glob("*.json"))
    print(f"V5_ENRICHMENTS files: {len(files)}")
    existing = {d.name for d in ATLAS.iterdir() if d.is_dir()}
    candidates = []
    fail_reasons = Counter()
    for fp in files:
        try:
            d = json.load(open(fp, encoding="utf-8"))
        except Exception:
            fail_reasons["parse"] += 1; continue
        eng = d.get("name", "")
        slug = _clean_slug(eng) if eng else ""
        if not slug: fail_reasons["no_name"] += 1; continue
        if slug in existing: fail_reasons["already_online"] += 1; continue
        cl = d.get("cross_lingual", {})
        defn = ""
        if isinstance(cl, dict):
            en_part = cl.get("en", {})
            if isinstance(en_part, dict): defn = en_part.get("definition", "")
        ok, reason = quality_strict(eng, defn)
        if not ok:
            fail_reasons[reason] += 1; continue
        candidates.append({
            "id": d.get("termCode", ""), "slug": slug, "en": eng, "def_en": defn,
            "category": d.get("termCode", "").split("-")[0] if d.get("termCode") else "AUGMANITAI",
            "source": "V5_ENRICHMENTS",
        })
        if limit and len(candidates) >= limit: break

    print(f"Quality-passing candidates: {len(candidates)}")
    print(f"Failure breakdown:")
    for k, v in fail_reasons.most_common(): print(f"  {k:25s} {v}")
    return candidates


def main():
    LIMIT = 6000  # ~6000 per wave (compute-sparsam)
    candidates = harvest_v5_pool(limit=LIMIT)
    print(f"\nWriting up to {LIMIT} candidates through gate...")

    by_cat = defaultdict(list)
    for c in candidates: by_cat[c["category"]].append(c)

    atlas_snapshot = {d.name for d in ATLAS.iterdir() if d.is_dir()}

    n_pass = 0
    n_fail = 0
    fail_reasons = Counter()
    for c in candidates:
        sibs = [s for s in by_cat[c["category"]] if s["slug"] != c["slug"]][:6]
        page_html = _build_page(c["id"], c["slug"], c["en"], c["def_en"], c["category"], sibs)
        result = validate_page(page_html, slug=c["slug"], definition=c["def_en"],
                                atlas_slug_snapshot=atlas_snapshot)
        if result.passed:
            d = ATLAS / c["slug"]
            d.mkdir(exist_ok=True)
            (d / "index.html").write_text(page_html, encoding="utf-8")
            atlas_snapshot.add(c["slug"])
            n_pass += 1
            if n_pass % 500 == 0: print(f"  ...{n_pass}")
        else:
            n_fail += 1
            for f in result.failures: fail_reasons[f.split(":")[0]] += 1

    print(f"\n=== Welle 5 (V5_ENRICHMENTS) ===")
    print(f"  Gate-passed (written): {n_pass}")
    print(f"  Gate-failed: {n_fail}")
    if fail_reasons:
        for f, n in fail_reasons.most_common(10): print(f"    {n:5d}  {f}")

    final = sum(1 for d in ATLAS.iterdir() if d.is_dir())
    print(f"\nAtlas total: {final}")


if __name__ == "__main__":
    main()
