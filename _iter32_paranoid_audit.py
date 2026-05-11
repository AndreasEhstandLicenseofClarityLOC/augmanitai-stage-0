#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 32 — PARANOID DEEP AUDIT v3.

Per Andy directive 2026-05-11: "es ist garantiert nur ein bruchteil aller scheiße die passiert ist".
Look for everything we missed.

11 SCAN-DIMENSIONS:
1. Trade-Secret-Patterns FULL (per TRADE_SECRET_NOTE.md 1.B + 1.C)
   - SSP, Gedankenvererbung-operative, Gehirnspiegelung-operative, CLD-operativ
   - SYC/CONF/HALL/ZTH scores
   - V92-Pipeline-Architektur
   - ISO/IEC 42001 Compliance-Mapping
   - "Mind Upload" architecture details
   - Bestatter (Funeral home — CLD vendor)
   - Family-Office references
   - Periodic Table contents
2. Person-Privacy (Leona, Andy as Beamter, school)
3. Medikamente (Gabapentin, Topiramat, Fluoxetin, Ritalin, Methylphenidat, SSRI)
4. Encoding corruption (U+FFFD, RTL marks)
5. JSON-LD validity check (each block parses)
6. Author-tag duplicates / inconsistencies
7. URL consistency (canonical == og:url == @id?)
8. Slug malformation (-- , trailing -, length, umlauts)
9. Duplicate titles (different slug, same title)
10. Phantom related-term IDs (AUG-XXXX references that don't exist in atlas)
11. Variants v3 (broader patterns)
"""
import re, json, io, sys
from pathlib import Path
from collections import defaultdict, Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")
ATLAS = DEPLOY / "atlas"

# ============ EXPANDED TRADE-SECRET PATTERNS ============
TRADE_SECRET_PATTERNS = {
    # 1.B operations
    "trade_ssp": r"\bSSP\b(?!\s*[a-z])",  # SSP not followed by lowercase (avoid SSPnetwork)
    "trade_gedankenvererbung_method": r"Gedankenvererbung.{0,80}(?:method|protocol|operativ|pipeline|measurement)",
    "trade_gehirnspiegelung_method": r"Gehirnspiegelung.{0,80}(?:method|protocol|operativ|pipeline|architectur|fidelity)",
    "trade_cld_operativ": r"\bCLD\b.{0,40}(?:method|protocol|pricing|workflow|interview|pilot|operativ|client)",
    "trade_score_arch": r"\b(?:SYC|CONF|HALL|ZTH)\b",
    "trade_v92_pipeline": r"\bV92\b.{0,40}(?:build|pipeline|architectur|spec)",
    "trade_iso42001_mapping": r"ISO[/\- ]?IEC[/\- ]?42001.{0,80}(?:mapping|compliance|score)",
    "trade_mind_upload_arch": r"mind[\s-]?upload.{0,60}(?:architectur|protocol|spec|phase)",
    "trade_bestatter": r"\bBestatter\b|\bfuneral home\b|\bundertaker\b",
    "trade_family_office": r"\bfamily[\s-]?office\b",
    "trade_periodic_table": r"periodic table.{0,40}(?:human[\s-]?AI|interaction|element)",
    "trade_tier_system": r"\btier[\s-]?(?:1|2|3|4|system)\s+(?:promotion|curat|architectur)",

    # 1.C strict
    "trade_leona_andy_link": r"Leona.{0,100}(?:Andreas|Ehstand|Vater|father|daughter|Tochter|family)",
    "trade_andy_leomanitai_link": r"(?:Andreas|Ehstand).{0,100}Leomanitai|Leomanitai.{0,100}(?:Andreas|Ehstand|founder|gründer|owns)",
    "trade_leona_ceo": r"Leona.{0,30}(?:CEO|GF|Geschäftsführer)",
    "trade_school_specific": r"\b(?:Gymnasium|Realschule|Mittelschule|Hauptschule|Grundschule)\s+[A-ZÄÖÜ]\w+",
    "trade_beamter_a13": r"\bA[\s\.]?13\b|\bBesoldungsgruppe",
    "trade_andy_teacher_andy": r"(?:Andreas|Ehstand).{0,50}(?:Lehrer|teacher|Beamter)",

    # Medications
    "trade_med_gabapentin": r"\bGabapentin",
    "trade_med_topiramat": r"\bTopiramat",
    "trade_med_fluoxetin": r"\bFluoxetin",
    "trade_med_ritalin": r"\b(?:Ritalin|Methylphenidat)",
    "trade_med_ssri": r"\bSSRI\b(?!\-)",

    # Concrete address details
    "trade_addr_full": r"Nepomukweg\s*7|82319\s*Starnberg",
    "trade_phone": r"\+49[\s\-]?\d{2,4}[\s\-]?\d{4,}",

    # Specific LLM pipeline ops (V2 OK as begriff, not as ops)
    "trade_llm_pipeline_specific": r"(?:Claude|GPT-4|Gemini|Grok|Anthropic|OpenAI)\s+(?:validates|generates|coordinates|orchestrat|provides|outputs)",
}


def trade_secret_paranoid_scan(text):
    hits = {}
    for label, pat in TRADE_SECRET_PATTERNS.items():
        for m in re.finditer(pat, text, re.IGNORECASE):
            hits.setdefault(label, []).append(m.group(0)[:80])
    return hits


# ============ ENCODING CORRUPTION ============
def encoding_check(text):
    hits = []
    if "�" in text:
        hits.append(f"replacement_char_{text.count(chr(0xfffd))}x")
    if "‫" in text or "‬" in text or "‭" in text or "‮" in text:
        hits.append("rtl_ltr_mark")
    if "‎" in text or "‏" in text:
        hits.append("ltr_rtl_invisible_mark")
    return hits


# ============ JSON-LD VALIDITY ============
def jsonld_validity_check(html):
    hits = []
    blocks = re.findall(r'<script type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.DOTALL)
    for i, b in enumerate(blocks):
        try:
            j = json.loads(b.strip())
            # Check creator @id
            if isinstance(j, dict):
                creator = j.get("creator")
                if isinstance(creator, dict):
                    cid = creator.get("@id", "")
                    if cid and "orcid.org/0009-0006-3773-7796" not in cid:
                        hits.append(f"creator_id_mismatch:{cid[:60]}")
        except json.JSONDecodeError as e:
            hits.append(f"jsonld_parse_error_block{i+1}")
    return hits


# ============ AUTHOR TAG CONSISTENCY ============
def author_tag_check(html):
    hits = []
    author_metas = re.findall(r'<meta name=["\']author["\'][^>]*content=["\']([^"\']+)', html)
    if len(author_metas) > 1:
        hits.append(f"duplicate_author_meta_{len(author_metas)}x")
    if author_metas and author_metas[0] != "Andreas Ehstand":
        hits.append(f"wrong_author_value:{author_metas[0]}")
    rel_authors = re.findall(r'<link rel=["\']author["\'][^>]*href=["\']([^"\']+)', html)
    if len(rel_authors) > 1:
        hits.append(f"duplicate_rel_author_{len(rel_authors)}x")
    if rel_authors and "orcid.org/0009-0006-3773-7796" not in rel_authors[0]:
        hits.append(f"wrong_rel_author:{rel_authors[0][:60]}")
    return hits


# ============ URL CONSISTENCY ============
def url_consistency_check(html, slug):
    hits = []
    canonical = re.search(r'<link rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', html)
    og_url = re.search(r'<meta property=["\']og:url["\'][^>]*content=["\']([^"\']+)', html)
    expected = f"/atlas/{slug}/"
    if canonical:
        if expected not in canonical.group(1):
            hits.append(f"canonical_slug_mismatch:{canonical.group(1)[:80]}")
    if og_url and canonical:
        if og_url.group(1) != canonical.group(1):
            hits.append("og_url_canonical_mismatch")
    duplicate_canonicals = len(re.findall(r'<link rel=["\']canonical["\']', html))
    if duplicate_canonicals > 1:
        hits.append(f"duplicate_canonical_{duplicate_canonicals}x")
    return hits


# ============ SLUG MALFORMATION ============
def slug_check(slug):
    hits = []
    if "--" in slug:
        hits.append("double_dash")
    if slug.startswith("-") or slug.endswith("-"):
        hits.append("edge_dash")
    if len(slug) > 100:
        hits.append("too_long")
    if re.search(r"[äöüÄÖÜß]", slug):
        hits.append("umlaut_in_slug")
    if slug[0].isdigit():
        hits.append("starts_with_digit")
    return hits


# ============ PHANTOM RELATED-TERMS in definitions ============
def phantom_id_check(html, existing_ids):
    hits = []
    # Find "AUG-NNNN" / "NEO-NNNN" references
    for m in re.finditer(r"\b(AUG|NEO|PER|RPH|EDU|ROB)-(\d{3,5})\b", html):
        full_id = f"{m.group(1)}-{m.group(2)}"
        if full_id not in existing_ids:
            hits.append(full_id)
    return list(set(hits))[:10]  # cap


# ============ MAIN ============
def main():
    print("Loading atlas...")
    slugs = sorted([d.name for d in ATLAS.iterdir() if d.is_dir()])
    print(f"Atlas pages: {len(slugs)}")

    # Collect all known IDs (from JSON-LD termCode fields)
    existing_ids = set()
    titles_by_slug = {}
    print("First-pass: collecting term-IDs and titles...")
    for s in slugs:
        fp = ATLAS / s / "index.html"
        if not fp.exists(): continue
        c = fp.read_text(encoding="utf-8", errors="ignore")
        # extract termCode from JSON-LD
        for m in re.finditer(r'"termCode"\s*:\s*"([A-Z]+-\d+)"', c):
            existing_ids.add(m.group(1))
        # title from <h1>
        t = re.search(r"<h1[^>]*>([^<]+)</h1>", c)
        if t: titles_by_slug[s] = t.group(1).strip()
    print(f"Collected term-IDs: {len(existing_ids)}")

    # Duplicate titles
    title_to_slugs = defaultdict(list)
    for s, t in titles_by_slug.items():
        title_to_slugs[t.lower()].append(s)
    dup_titles = {t: slugs for t, slugs in title_to_slugs.items() if len(slugs) > 1}
    print(f"Duplicate titles: {len(dup_titles)}")

    print("\nSecond-pass: 11-dimension audit...")
    results = {}
    counters = defaultdict(int)
    for i, s in enumerate(slugs):
        if i and i % 2000 == 0: print(f"  ...{i}/{len(slugs)}")
        fp = ATLAS / s / "index.html"
        if not fp.exists(): continue
        c = fp.read_text(encoding="utf-8", errors="ignore")

        page_flags = {}
        ts = trade_secret_paranoid_scan(c)
        if ts: page_flags["trade_secret"] = list(ts.keys())
        ec = encoding_check(c)
        if ec: page_flags["encoding"] = ec
        jv = jsonld_validity_check(c)
        if jv: page_flags["jsonld"] = jv
        at = author_tag_check(c)
        if at: page_flags["author_tag"] = at
        uc = url_consistency_check(c, s)
        if uc: page_flags["url_inconsistency"] = uc
        sm = slug_check(s)
        if sm: page_flags["slug_malform"] = sm
        pid = phantom_id_check(c, existing_ids)
        if pid: page_flags["phantom_ids"] = pid[:5]

        if page_flags:
            results[s] = page_flags
            for k in page_flags:
                counters[k] += 1

    n = len(slugs)
    print(f"\n=== PARANOID AUDIT SUMMARY (n={n}) ===\n")
    for k in ["trade_secret", "encoding", "jsonld", "author_tag", "url_inconsistency",
              "slug_malform", "phantom_ids"]:
        c = counters.get(k, 0)
        pct = 100*c/n if n else 0
        verdict = "✅ CLEAN" if c == 0 else "🟡 SOME" if c < 50 else "🔴 MANY"
        print(f"  {k:25s} {c:5d} pages ({pct:5.1f}%) {verdict}")
    print(f"  duplicate_titles          {len(dup_titles):5d} title-groups")

    # Trade-secret breakdown
    ts_pattern_counts = Counter()
    for r in results.values():
        for p in r.get("trade_secret", []):
            ts_pattern_counts[p] += 1
    if ts_pattern_counts:
        print(f"\nTrade-secret patterns hit:")
        for p, n in ts_pattern_counts.most_common():
            print(f"  {n:5d}  {p}")

    # Encoding breakdown
    enc_counts = Counter()
    for r in results.values():
        for e in r.get("encoding", []):
            enc_counts[e.split("_")[0]] += 1
    if enc_counts:
        print(f"\nEncoding issues:")
        for p, n in enc_counts.most_common():
            print(f"  {n:5d}  {p}")

    # Slug-malform breakdown
    slug_counts = Counter()
    for r in results.values():
        for sl in r.get("slug_malform", []):
            slug_counts[sl] += 1
    if slug_counts:
        print(f"\nSlug malformations:")
        for p, n in slug_counts.most_common():
            print(f"  {n:5d}  {p}")

    # Save full report
    (DEPLOY / "_ITER32_PARANOID_AUDIT.json").write_text(
        json.dumps({
            "n_total": n,
            "n_flagged": len(results),
            "duplicate_titles": {t: s for t, s in dup_titles.items()},
            "trade_secret_breakdown": dict(ts_pattern_counts),
            "encoding_breakdown": dict(enc_counts),
            "slug_breakdown": dict(slug_counts),
            "results": results,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"\nSaved: _ITER32_PARANOID_AUDIT.json")


if __name__ == "__main__":
    main()
