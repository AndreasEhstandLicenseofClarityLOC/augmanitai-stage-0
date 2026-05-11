#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHIEF INTAKE — Reads worker outputs (LM Studio + Poe + manual) and runs them through:
1. Quality filter (dedupe, length, stub-pattern, hard-block, theme-block)
2. Pre-Publish-Gate (47 checks) + Gate v4 extension (5 checks)
3. Build HTML page with V11.2-template + Andy-Legend backend
4. Write to atlas/

Worker outputs must be JSONL with at least:
  {"english_name": "...", "definition_en": "..." [, "category": "...", "source_worker": "..."]}

Place worker outputs in:  _worker_outputs/*.jsonl

Then run:
  python _chief_intake.py
  python _chief_intake.py --inputs _worker_outputs/poe_*.jsonl
  python _chief_intake.py --dry  # validate only, don't write
"""
import json, re, sys, io, argparse, importlib.util, hashlib, datetime
from pathlib import Path
from collections import defaultdict, Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")
ATLAS = DEPLOY / "atlas"
WORKER_DIR = DEPLOY / "_worker_outputs"


# Load gate v4 (no dataclass, safe to exec)
spec = importlib.util.spec_from_file_location("_g4", str(DEPLOY / "_pre_publish_gate_v4_extension.py"))
_v4 = importlib.util.module_from_spec(spec); spec.loader.exec_module(_v4)
validate_extension = _v4.validate_extension

# Load base gate
spec2 = importlib.util.spec_from_file_location("_gb", str(DEPLOY / "_pre_publish_gate.py"))
_base = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(_base)
validate_page = _base.validate_page


# Inline build_page from iter37
def _import_build_page():
    src = (DEPLOY / "_iter37_gate_filtered_generator.py").read_text(encoding="utf-8")
    lines = []
    skip = False
    for ln in src.splitlines(keepends=True):
        if "sys.stdout = io.TextIOWrapper" in ln: continue
        if ln.startswith('if __name__ == "__main__":'): skip = True; continue
        if skip: continue
        lines.append(ln)
    ns = {"__name__": "_inl", "__file__": str(DEPLOY / "_iter37_gate_filtered_generator.py"),
          "validate_page": validate_page}
    exec(compile("".join(lines), str(DEPLOY / "_iter37_gate_filtered_generator.py"), "exec"), ns)
    return ns["build_page"]


_build_page = _import_build_page()


def clean_slug(s):
    s = s.lower().strip()
    if s.endswith(".html"): s = s[:-5]
    s = re.sub(r"[^a-z0-9-]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


STUB = re.compile(
    r"May describe|^Users .{1,30} (collectively|generally|typically)|"
    r"^The phenomenon catalogued as|^A domain-specific term|^A framework term for|"
    r"The measurable .{1,40} between AI-augmented|covering the theory and practice of",
    re.IGNORECASE
)
HARD_BLOCK = re.compile(r"\b(suicide|kill|rape|abuse|porn|child|minor|nazi|terror|exploit)\b", re.IGNORECASE)
THEME_BLOCK = re.compile(
    r"funeral|bestatter|undertaker|mortuary|cemeter|mind-upload|consciousness-upload|"
    r"digital-immortality|insurance-underwrit|premium-deni|tibet|taiwan independ|"
    r"hong kong|xinjiang|tiananmen|falun|genocid|massacre|self-harm|self-injur|"
    r"abortion|pornograph|methylphenidat|ritalin|gabapentin|topiramat|fluoxetin|"
    r"white genocide|great replacement|racial purity|pedophil|"
    r"weapon\s+system|kill\s+chain|combat\s+AI|warfare|clinical\s+advice|"
    r"treatment\s+protocol|prescription|legal\s+advice|litigation\s+strategy",
    re.IGNORECASE
)


def quality_check(en, defn):
    if not en or not defn: return False, "empty"
    if len(en) < 4 or len(en) > 120: return False, "name_length"
    if len(defn) < 100: return False, "def_too_short"
    if len(defn) > 800: return False, "def_too_long"
    if STUB.search(defn): return False, "stub_pattern"
    if HARD_BLOCK.search(en + " " + defn): return False, "hard_block"
    if THEME_BLOCK.search(en + " " + defn): return False, "theme_block"
    return True, None


def load_worker_outputs(input_globs=None):
    """Load all JSONL files from _worker_outputs/ or specified globs."""
    files = []
    if input_globs:
        for g in input_globs:
            files.extend(Path(".").glob(g) if not Path(g).is_absolute() else [Path(g)])
    else:
        files = sorted(WORKER_DIR.glob("*.jsonl")) if WORKER_DIR.exists() else []
    print(f"Worker files: {len(files)}")
    records = []
    for fp in files:
        try:
            with open(fp, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line: continue
                    try:
                        obj = json.loads(line)
                        if isinstance(obj, dict):
                            records.append((obj, fp.name))
                    except: pass
            print(f"  {fp.name}: {sum(1 for r in records if r[1]==fp.name)} records")
        except Exception as e:
            print(f"  ERROR {fp.name}: {e}")
    return records


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", nargs="*", default=None)
    ap.add_argument("--dry", action="store_true", help="Don't write; just validate + report")
    ap.add_argument("--max", type=int, default=None, help="Limit for testing")
    args = ap.parse_args()

    records = load_worker_outputs(args.inputs)
    if not records:
        print("No worker records found.")
        return

    existing = {d.name for d in ATLAS.iterdir() if d.is_dir()}
    print(f"Atlas existing: {len(existing)}")

    seen_slugs = set()
    candidates = []
    fail = Counter()
    for obj, src in records:
        en = obj.get("english_name") or obj.get("name") or obj.get("term") or ""
        defn = obj.get("definition_en") or obj.get("def_en") or obj.get("definition") or ""
        cat = obj.get("category") or obj.get("domain") or "AUGMANITAI"
        slug = clean_slug(en)
        if not slug or slug in existing or slug in seen_slugs:
            fail["dup_or_online"] += 1; continue
        ok, reason = quality_check(en, defn)
        if not ok:
            fail[reason] += 1; continue
        seen_slugs.add(slug)
        candidates.append({
            "slug": slug, "en": en, "def_en": defn, "category": cat,
            "id": f"WK-{hashlib.md5(slug.encode()).hexdigest()[:8].upper()}",
            "source": src,
        })

    print(f"\nQuality-passing candidates: {len(candidates)}")
    for k, v in fail.most_common(): print(f"  fail.{k}: {v}")

    if args.max: candidates = candidates[:args.max]
    if args.dry:
        print(f"\n[DRY RUN] Would attempt {len(candidates)} → gate")
        return

    # Gate + write
    atlas_snap = set(existing)
    by_cat = defaultdict(list)
    for c in candidates: by_cat[c["category"]].append(c)

    n_pass = 0
    n_fail = 0
    fb = Counter()
    for c in candidates:
        # Gate v4 pre-check on definition
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
            if n_pass % 100 == 0: print(f"  ...written {n_pass}")
        else:
            n_fail += 1
            for f in br.failures: fb[f.split(":")[0]] += 1
            for f in er: fb[f.split(":")[0]] += 1

    print(f"\n=== INTAKE COMPLETE ===")
    print(f"  PASS (written): {n_pass}")
    print(f"  FAIL (rejected): {n_fail}")
    if fb:
        for k, v in fb.most_common(10): print(f"    {v:5d}  {k}")
    print(f"\nAtlas total: {sum(1 for d in ATLAS.iterdir() if d.is_dir())}")

    # Save intake report
    report = {
        "date": datetime.datetime.now().isoformat(),
        "worker_records_seen": len(records),
        "quality_passing": len(candidates),
        "gate_passing_written": n_pass,
        "gate_rejected": n_fail,
        "rejection_breakdown": dict(fb),
        "quality_rejection_breakdown": dict(fail),
    }
    (DEPLOY / "_LAST_INTAKE_REPORT.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nSaved: _LAST_INTAKE_REPORT.json")


if __name__ == "__main__":
    main()
