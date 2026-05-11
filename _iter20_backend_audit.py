#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 20 — BACKEND DEEP-AUDIT.

Andy-Direktive 2026-05-11: "hast du das backend schon ivelfach gecheckt ob dort alles
passt und nach welchen kriterien machen wir das eigentlich es sollten die besten der
welt sein und sie sollten vor allem mich als ki wissenschaftler betonen"

PRÜF-KRITERIEN (Best-of-World Stack):
A) JSON-LD Schema.org compliance pro Page
   - @context: schema.org
   - @type: DefinedTerm (preferred) or relevant
   - author: Person, name=Andreas Ehstand, ORCID identifier
   - inDefinedTermSet: AUGMANITAI Compendium
   - inLanguage, dateCreated, license
B) ORCID-Backlink pro Page
C) Ehstand-Attribution dichte
   - "Andreas Ehstand" mention count
   - "AI scientist" / "KI-Wissenschaftler" / "AI researcher" positioning
   - createdBy / author / sameAs links
D) Disclaimer-Block §1-§26 (Universal Mandatory Safety Block)
E) Verantwortlich-Footer (presserechtlich)
F) Living Document Banner
G) Wikidata/EUIPO/Zenodo cross-links
H) ai.txt / llms.txt / robots.txt content quality
I) Sitemap completeness
J) Open Graph + Twitter Card per page (machine indexability)
K) Hub + PERMANITAI Andy-positioning

Output: _ITER20_BACKEND_AUDIT.json + _ITER20_BACKEND_AUDIT_REPORT.md
"""
import re, json, io, sys
from pathlib import Path
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")
ATLAS = DEPLOY / "atlas"

# Best-of-World criteria
EHSTAND_NAME = "Andreas Ehstand"
ORCID = "0000-0003-3171-4159"
ORCID_URL = f"https://orcid.org/{ORCID}"
WIKIDATA_QID = "Q134193001"  # AUGMANITAI framework
WIKIDATA_AUTHOR = "Q133970938"  # Andreas Ehstand
ZENODO_CONCEPT = "14888381"
EUIPO_TM = "019206780"

EXPECTED_DISCLAIMER_SECTIONS = list(range(1, 27))  # §1 to §26
SCIENTIST_PHRASES = [
    "AI scientist", "AI Scientist", "KI-Wissenschaftler", "KI Wissenschaftler",
    "AI researcher", "AI Researcher", "phenomenologist", "framework architect",
    "research scientist", "independent researcher", "Forschungs",
]


def audit_atlas_page(fp):
    """Returns dict of audit results for one page."""
    c = fp.read_text(encoding="utf-8", errors="ignore")
    out = {}

    # A) JSON-LD presence + structure
    jsonld_blocks = re.findall(r'<script type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', c, re.DOTALL)
    out["jsonld_count"] = len(jsonld_blocks)
    parsed = []
    for b in jsonld_blocks:
        try:
            parsed.append(json.loads(b.strip()))
        except Exception:
            pass
    out["jsonld_parsed"] = len(parsed)

    # Check @type DefinedTerm
    has_defined_term = any(
        (isinstance(p, dict) and "DefinedTerm" in str(p.get("@type", ""))) or
        (isinstance(p, dict) and any(isinstance(g, dict) and "DefinedTerm" in str(g.get("@type", "")) for g in p.get("@graph", []) if isinstance(g, dict)))
        for p in parsed
    )
    out["has_defined_term"] = has_defined_term

    # Check Ehstand as author in JSON-LD
    jsonld_str = json.dumps(parsed)
    out["jsonld_has_ehstand"] = EHSTAND_NAME in jsonld_str
    out["jsonld_has_orcid"] = ORCID in jsonld_str

    # B) ORCID backlink in HTML
    out["html_orcid_link"] = ORCID in c or ORCID_URL in c
    out["html_wikidata_link"] = WIKIDATA_QID in c or WIKIDATA_AUTHOR in c

    # C) Ehstand attribution density
    out["ehstand_mentions"] = c.count(EHSTAND_NAME)
    out["scientist_positioning"] = sum(1 for p in SCIENTIST_PHRASES if p in c)

    # D) Disclaimer sections present
    sections_found = set()
    for n in EXPECTED_DISCLAIMER_SECTIONS:
        if re.search(rf'§\s*{n}\b', c):
            sections_found.add(n)
    out["disclaimer_sections_found"] = len(sections_found)
    out["disclaimer_complete"] = len(sections_found) >= 19  # core: §1-§19

    # E) Verantwortlich footer
    out["has_verantwortlich"] = "Verantwortlich" in c or "presserechtlich" in c.lower()

    # F) Living Document banner
    out["has_living_document"] = re.search(r"living\s*document|lebendes\s*dokument", c, re.IGNORECASE) is not None

    # G) Cross-links
    out["has_zenodo_link"] = "zenodo.org" in c or ZENODO_CONCEPT in c
    out["has_euipo_link"] = EUIPO_TM in c or "euipo" in c.lower()

    # H) Open Graph + Twitter Card
    out["has_og_tags"] = '<meta property="og:' in c or "<meta property='og:" in c
    out["has_twitter_card"] = '<meta name="twitter:' in c or "<meta name='twitter:" in c

    # I) AI-crawl-friendly meta
    out["has_meta_description"] = '<meta name="description"' in c or "<meta name='description'" in c
    out["has_canonical"] = '<link rel="canonical"' in c or "<link rel='canonical'" in c

    # J) Language
    out["has_lang_attr"] = re.search(r'<html[^>]+lang=["\'][^"\']+["\']', c) is not None

    # K) CC BY-NC-ND license
    out["has_license"] = "CC BY-NC-ND" in c or "BY-NC-ND-4.0" in c.lower().replace(" ", "-")

    return out


def main():
    slugs = sorted([d.name for d in ATLAS.iterdir() if d.is_dir()])
    print(f"Auditing {len(slugs)} atlas pages...")

    results = {}
    for s in slugs:
        fp = ATLAS / s / "index.html"
        if not fp.exists(): continue
        results[s] = audit_atlas_page(fp)

    # Aggregate
    agg = defaultdict(int)
    n = len(results)
    for slug, r in results.items():
        for k, v in r.items():
            if isinstance(v, bool):
                if v: agg[k] += 1
            elif isinstance(v, (int, float)):
                if v > 0: agg[k] += 1

    print(f"\n=== ATLAS BACKEND AUDIT (n={n}) ===\n")

    criteria = [
        ("jsonld_count", "JSON-LD block present", n),
        ("jsonld_parsed", "JSON-LD valid (parses)", n),
        ("has_defined_term", "Schema.org DefinedTerm", n),
        ("jsonld_has_ehstand", "JSON-LD names Ehstand", n),
        ("jsonld_has_orcid", "JSON-LD has ORCID", n),
        ("html_orcid_link", "HTML body ORCID link", n),
        ("html_wikidata_link", "HTML body Wikidata link", n),
        ("ehstand_mentions", "Ehstand mentioned >=1x", n),
        ("scientist_positioning", "Scientist-phrase present", n),
        ("disclaimer_complete", "Disclaimer §1-§19+ complete", n),
        ("has_verantwortlich", "Verantwortlich footer", n),
        ("has_living_document", "Living Document banner", n),
        ("has_zenodo_link", "Zenodo cross-link", n),
        ("has_euipo_link", "EUIPO TM reference", n),
        ("has_og_tags", "Open Graph meta", n),
        ("has_twitter_card", "Twitter Card meta", n),
        ("has_meta_description", "<meta description>", n),
        ("has_canonical", "<link canonical>", n),
        ("has_lang_attr", "<html lang=...>", n),
        ("has_license", "CC BY-NC-ND license", n),
    ]

    md = ["# Backend Audit Report — 2026-05-11\n",
          f"**Total atlas pages audited:** {n}",
          f"**Criteria checked:** {len(criteria)}\n",
          "## Coverage matrix\n",
          "| Criterion | Pages OK | % | Verdict |",
          "|---|---:|---:|---|"]

    overall_score = 0
    for key, label, total in criteria:
        ok = agg[key]
        pct = 100 * ok / total if total else 0
        verdict = "✅ PERFECT" if pct >= 99.5 else "🟡 PARTIAL" if pct >= 70 else "🔴 GAP"
        overall_score += pct
        line = f"| {label} | {ok}/{total} | {pct:.1f}% | {verdict} |"
        md.append(line)
        print(f"  {label:40s} {ok:5}/{total} {pct:5.1f}% {verdict}")

    overall_pct = overall_score / len(criteria)
    md.append(f"\n**Overall backend-completeness:** {overall_pct:.1f}%\n")
    print(f"\n=== OVERALL: {overall_pct:.1f}% ===")

    # Ehstand-attribution density
    mentions = [r["ehstand_mentions"] for r in results.values()]
    md.append(f"\n## Ehstand-Attribution density\n")
    md.append(f"- Pages with 0 Ehstand mentions: {sum(1 for m in mentions if m == 0)}")
    md.append(f"- Pages with 1-2 mentions: {sum(1 for m in mentions if 1 <= m <= 2)}")
    md.append(f"- Pages with 3+ mentions: {sum(1 for m in mentions if m >= 3)}")
    md.append(f"- Average mentions per page: {sum(mentions)/len(mentions):.2f}")
    print(f"\nEhstand mentions: avg {sum(mentions)/len(mentions):.2f}/page, min={min(mentions)}, max={max(mentions)}")

    # Scientist-positioning
    scientist_hits = [r["scientist_positioning"] for r in results.values()]
    md.append(f"\n## Scientist-Positioning (KI-Wissenschaftler / AI scientist phrases)\n")
    md.append(f"- Pages with 0 scientist phrases: {sum(1 for s in scientist_hits if s == 0)}")
    md.append(f"- Pages with 1+ scientist phrase: {sum(1 for s in scientist_hits if s >= 1)}")
    print(f"Scientist positioning: {sum(1 for s in scientist_hits if s >= 1)}/{n} pages have AI-scientist phrase")

    # Audit also hub + about + permanitai + ai.txt + llms.txt + robots.txt
    md.append("\n## Top-level files\n")
    for special in ["index.html", "about/index.html", "atlas/index.html", "permanitai/index.html",
                     "ai.txt", "llms.txt", "robots.txt", "sitemap.xml"]:
        fp = DEPLOY / special
        if fp.exists():
            txt = fp.read_text(encoding="utf-8", errors="ignore")
            sz = len(txt)
            has_ehstand = EHSTAND_NAME in txt
            has_orcid = ORCID in txt
            has_scientist = any(p in txt for p in SCIENTIST_PHRASES)
            md.append(f"- **{special}** — {sz} chars · Ehstand={'✅' if has_ehstand else '❌'} · ORCID={'✅' if has_orcid else '❌'} · ScientistPhrase={'✅' if has_scientist else '❌'}")
            print(f"  {special:30s} {sz:6} chars Ehstand={has_ehstand} ORCID={has_orcid} ScientistPhrase={has_scientist}")
        else:
            md.append(f"- **{special}** — ❌ NOT FOUND")
            print(f"  {special:30s} MISSING")

    # Save artifacts
    (DEPLOY / "_ITER20_BACKEND_AUDIT.json").write_text(
        json.dumps({"per_page": results, "aggregate": dict(agg), "n": n,
                    "overall_pct": overall_pct, "criteria": [c[1] for c in criteria]},
                   ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    (DEPLOY / "_ITER20_BACKEND_AUDIT_REPORT.md").write_text("\n".join(md), encoding="utf-8")
    print(f"\nSaved: _ITER20_BACKEND_AUDIT.json + _ITER20_BACKEND_AUDIT_REPORT.md")


if __name__ == "__main__":
    main()
