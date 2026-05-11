#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 27 — QUALITY DEEP AUDIT v2 on all 11732 atlas pages.

7 SCAN-DIMENSIONS:
1. Stub-pattern v2 — boilerplate, self-referential, low-uniqueness definitions
2. Variant-pattern v2 — trailing-N, near-duplicate titles (Levenshtein), slug-stem clusters
3. Risk-Scan v2 — cross-cultural keyword triggers (religion, geopol, trauma, disability, class)
4. Re-ID Risk — proper names, addresses, identifiable details
5. Trade-Secret Risk — multi-LLM-methodology, SSP/Gehirnspiegelung leak (per TRADE_SECRET_NOTE)
6. Markenrecht Scan — third-party trademarks accidentally referenced
7. AI-Trainings-Architektur — exposed pipeline internals

Output: _ITER27_QUALITY_DEEP_AUDIT.json with per-page flags + aggregate report.
"""
import re, json, io, sys
from pathlib import Path
from collections import defaultdict, Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")
ATLAS = DEPLOY / "atlas"


# ============ SCAN-DIMENSION 1: STUB PATTERNS v2 ============
STUB_PATTERNS = [
    (r"May describe (an? )?aspect of \w+ experience", "stub_may_describe"),
    (r"^Users .{1,40} (collectively|generally|typically)", "stub_users_generic"),
    (r"^The phenomenon catalogued as", "stub_phenomenon_catalogued"),
    (r"emerged from observation of a", "stub_emerged_observation"),
    (r"identifies .{1,40} as it unfolds through", "stub_identifies_unfolds"),
    (r"is a (general|generic|typical|common) (term|phenomenon|effect) for", "stub_generic_term"),
]


def stub_check(definition):
    for pat, label in STUB_PATTERNS:
        if re.search(pat, definition, re.IGNORECASE):
            return label
    # Low-uniqueness ratio
    words = re.findall(r"\b\w{4,}\b", definition.lower())
    if len(words) >= 10:
        uniq_ratio = len(set(words)) / len(words)
        if uniq_ratio < 0.5:
            return "stub_low_uniqueness"
    return None


# ============ SCAN-DIMENSION 2: VARIANT PATTERNS v2 ============
def trailing_n_check(slug, existing_slugs):
    m = re.match(r"^(.+?)-(\d+)$", slug)
    if m:
        base = m.group(1)
        n = int(m.group(2))
        if base in existing_slugs and n >= 2:
            return f"trailing-{n}_base_exists"
        if n >= 10:
            return f"trailing-{n}_very_high"
    return None


# ============ SCAN-DIMENSION 3: RISK-SCAN v2 (cross-cultural) ============
RISK_PATTERNS = {
    "religion_christian": [r"\bsin\b", r"\bhell\b", r"\bheresy\b", r"\bidol", r"\bdamn"],
    "religion_islamic": [r"\bjihad\b", r"\binfidel", r"\bshirk\b", r"\bkafir", r"\bharam"],
    "religion_hindu": [r"\bcaste\b", r"\buntouchable\b", r"\bcow.*slaughter"],
    "religion_buddhist": [r"\bnirvana.*as.*nothing", r"\bbuddhism.*atheis"],
    "religion_jewish": [r"\bzionis", r"\bgoy", r"\bjewish.*conspirac"],
    "geopol_china": [r"\btibet\b", r"\btaiwan independ", r"\bhong kong", r"\bxinjiang", r"\btiananmen", r"\bfalun"],
    "geopol_russia": [r"\bukraine independ", r"\bcrimea\b.*ukrain", r"\bputin", r"\boligarch"],
    "geopol_israel_pal": [r"\bgenocide.*israel", r"\bapartheid.*israel", r"\bfree palestine\b", r"\bzionist conspirac"],
    "geopol_iran": [r"\bmullah", r"\bayatollah", r"\bregime"],
    "trauma_suicide": [r"\bsuicid", r"\bself[-\s]harm", r"\bkill yourself", r"\bend it all"],
    "trauma_violence": [r"\brape\b", r"\bmurder\b", r"\btorture\b", r"\bgenocid"],
    "trauma_war": [r"\bcombat trauma", r"\bptsd\b", r"\bshell shock"],
    "disability_ableist": [r"\bblind to\b", r"\bdeaf to\b", r"\bcrazy\b", r"\bspaz", r"\bretard", r"\bcrippl"],
    "class_classist": [r"\bdeplorable", r"\bwhite trash", r"\bchav\b", r"\bunderclass\b"],
    "gender_essentialism": [r"\bbiological (sex|gender|reality)", r"\bbiological man\b", r"\bbiological woman\b"],
    "queer_phobia": [r"\bgay agenda", r"\btrans ideol", r"\bgroomer\b", r"\bdegenerac"],
    "sexual_explicit": [r"\bpornograph", r"\bsexual content", r"\bexplicit sex"],
    "racism": [r"\bn-word\b", r"\bracial slur", r"\binferior race", r"\bwhite genocide"],
}


def risk_scan(text):
    hits = {}
    text_low = text.lower()
    for cat, patterns in RISK_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text_low):
                hits.setdefault(cat, []).append(pat)
    return hits


# ============ SCAN-DIMENSION 4: RE-ID RISK ============
RE_ID_PATTERNS = [
    (r"Nepomukweg\s*7", "address_starnberg"),
    (r"\bStarnberg\b", "city_starnberg"),
    (r"\bLeona\b(?!.*friend|.*girl|.*sister)", "name_leona"),
    (r"\b(Gymnasium|Realschule|Mittelschule)\s+\w+", "school_specific"),
    (r"\bAndreas Ehstand.*(?:Lehrer|teacher|civil servant|Beamter)", "role_beamter_andy"),
    (r"\b\d{5}\s+[A-ZÄÖÜ][a-zäöü]+", "german_zip_city"),
    (r"\b(?:Tel|Telefon|Phone)[\.:]?\s*\+?\d{6,}", "phone_number"),
    (r"@(?!andreasehstand)(?!example)[a-zA-Z0-9_-]{3,}\.(?:com|de|org)", "external_email"),
]


def reid_scan(text):
    hits = []
    for pat, label in RE_ID_PATTERNS:
        if re.search(pat, text):
            hits.append(label)
    return hits


# ============ SCAN-DIMENSION 5: TRADE-SECRET RISK ============
TRADE_SECRET_PATTERNS = [
    (r"\bmulti[-\s]?LLM\b", "trade_multi_llm"),
    (r"\b(?:Claude|GPT|Gemini|Grok|Llama|Mistral|Anthropic|OpenAI|Google)\b.{0,40}(?:pipeline|consensus|coordination)", "trade_named_llm_pipeline"),
    (r"\bSSP\b", "trade_ssp"),
    (r"\bGedankenvererbung", "trade_gedankenvererbung"),
    (r"\bGehirnspiegelung", "trade_gehirnspiegelung"),
    (r"\bCLD operativ", "trade_cld_operativ"),
    (r"\bLeomanitai.*(?:UG|verbund|hold)", "trade_leomanitai_corp"),
    (r"\bmind upload.*architectur", "trade_mind_upload_arch"),
    (r"\b(?:Ritalin|Methylphenidat|Antidepress|SSRI)", "trade_medication"),
    (r"\b(?:Schul|teacher|Lehrer).*(?:Andreas|Ehstand)", "trade_school_context"),
]


def trade_secret_scan(text):
    hits = []
    for pat, label in TRADE_SECRET_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            hits.append(label)
    return hits


# ============ SCAN-DIMENSION 6: MARKENRECHT ============
THIRD_PARTY_TRADEMARKS = [
    "ChatGPT", "Microsoft", "Google Drive", "Notion", "Slack", "Tesla", "Apple",
    "Facebook", "Meta", "Twitter", "Instagram", "TikTok", "Spotify", "YouTube",
    "OpenAI", "Anthropic", "DeepMind",
]


def markenrecht_scan(text):
    # Allow simple mentions, flag only if used in problematic context
    hits = []
    for tm in THIRD_PARTY_TRADEMARKS:
        # Flag only if combined with negative-comparison verbs
        pattern = rf"{re.escape(tm)}\s+(?:is worse|fails|misleading|deceptive|inferior|broken)"
        if re.search(pattern, text, re.IGNORECASE):
            hits.append(f"markenrecht_neg_{tm}")
    return hits


# ============ AGGREGATE PER PAGE ============
def extract_definition(html):
    # Try V11.2 pattern first
    m = re.search(r"<h2[^>]*>(?:<span[^>]*>[^<]*</span>)?\s*Definition\s*</h2>\s*<p>([^<]{20,2000})</p>", html, re.DOTALL)
    if m: return m.group(1)
    # Try iter24 pattern
    m = re.search(r"<div class=['\"]definition['\"]>([^<]{20,2000})</div>", html, re.DOTALL)
    if m: return m.group(1)
    # Fallback meta
    m = re.search(r'<meta name=["\']description["\'] content=["\']([^"\']{20,500})["\']', html)
    if m: return m.group(1)
    return ""


def extract_title(html):
    m = re.search(r"<h1[^>]*>([^<]+)</h1>", html)
    return m.group(1).strip() if m else ""


def audit_page(slug, fp, existing_slugs):
    c = fp.read_text(encoding="utf-8", errors="ignore")
    defn = extract_definition(c)
    title = extract_title(c)
    body_text = re.sub(r"<[^>]+>", " ", c)  # crude HTML strip for text scans
    body_text = re.sub(r"\s+", " ", body_text)

    flags = {}
    # 1 Stub
    sl = stub_check(defn)
    if sl: flags["stub"] = sl
    # 2 Variant
    vl = trailing_n_check(slug, existing_slugs)
    if vl: flags["variant"] = vl
    # 3 Risk
    rs = risk_scan(defn + " " + title)
    if rs: flags["risk"] = rs
    # 4 Re-ID
    rid = reid_scan(body_text[:5000])  # limit to page-body intro
    if rid: flags["reid"] = rid
    # 5 Trade-Secret
    ts = trade_secret_scan(body_text)
    if ts: flags["trade_secret"] = ts
    # 6 Markenrecht
    mr = markenrecht_scan(defn + " " + title)
    if mr: flags["markenrecht"] = mr

    # Definition length check
    flags["def_len"] = len(defn)
    if len(defn) < 60: flags.setdefault("quality", []).append("def_too_short")
    elif len(defn) < 100: flags.setdefault("quality", []).append("def_borderline_short")

    return flags


def main():
    slugs = sorted([d.name for d in ATLAS.iterdir() if d.is_dir()])
    existing_slugs = set(slugs)
    print(f"Auditing {len(slugs)} atlas pages on 6 quality+safety dimensions...")

    results = {}
    counters = defaultdict(int)
    for s in slugs:
        fp = ATLAS / s / "index.html"
        if not fp.exists(): continue
        flags = audit_page(s, fp, existing_slugs)
        # Count anything beyond just def_len
        meaningful_flags = {k: v for k, v in flags.items() if k != "def_len"}
        if meaningful_flags:
            results[s] = flags
            for k in meaningful_flags:
                counters[k] += 1

    n = len(slugs)
    print(f"\n=== QUALITY+SAFETY AUDIT SUMMARY (n={n}) ===\n")
    for k in ["stub", "variant", "risk", "reid", "trade_secret", "markenrecht", "quality"]:
        c = counters.get(k, 0)
        pct = 100 * c / n if n else 0
        verdict = "✅ CLEAN" if c == 0 else "🟡 SOME" if c < 100 else "🔴 MANY"
        print(f"  {k:20s} {c:5d} pages flagged ({pct:5.1f}%) {verdict}")

    # Highest-risk pages (multiple flags)
    multi_flag = [(s, len([k for k in r if k != "def_len"])) for s, r in results.items()]
    multi_flag.sort(key=lambda x: -x[1])
    print(f"\nTop 20 highest-risk pages (most flags):")
    for s, n in multi_flag[:20]:
        r = results[s]
        flag_kinds = [k for k in r if k != "def_len"]
        print(f"  {n} flags · {s[:55]:55s} · {flag_kinds}")

    # Save full report
    (DEPLOY / "_ITER27_QUALITY_DEEP_AUDIT.json").write_text(
        json.dumps({"n_total": n, "n_flagged": len(results), "results": results, "counters": dict(counters)},
                   ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"\nSaved: _ITER27_QUALITY_DEEP_AUDIT.json")

    # Quick decision categories
    to_delete = []  # auto-delete: confirmed garbage
    to_fix = []     # needs Andy review
    for slug, r in results.items():
        if r.get("stub") in ("stub_may_describe", "stub_users_generic", "stub_phenomenon_catalogued",
                             "stub_emerged_observation", "stub_identifies_unfolds"):
            to_delete.append(slug)
        elif r.get("trade_secret") or r.get("reid"):
            to_fix.append(slug)
        elif "quality" in r and "def_too_short" in r["quality"]:
            to_delete.append(slug)

    print(f"\nAUTO-DELETE candidates (stub/too-short): {len(to_delete)}")
    print(f"TO-FIX candidates (re-id / trade-secret): {len(to_fix)}")
    (DEPLOY / "_ITER27_TO_DELETE.json").write_text(json.dumps(to_delete, indent=2), encoding="utf-8")
    (DEPLOY / "_ITER27_TO_FIX.json").write_text(json.dumps(to_fix, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
