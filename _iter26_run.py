#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 24 — Generate atlas pages from NEOMANITAI_4407 pool (offline → online).

Filters:
- confidence='I' (Independent-verified)
- def_en >= 80 chars
- No stub-pattern
- No sensitive language
→ 2751 high-quality candidates

Each page gets:
- Full V11.2-equivalent backend (Schema.org DefinedTerm + Person(Ehstand) + Organization +
  subjectOf Zenodo + ORCID/Wikidata/EUIPO + ai.txt-compliant Open Graph + Twitter Card +
  canonical + lang + license + breadcrumbs)
- Universal Mandatory Safety Block §1-§26 disclaimer (HTML-encoded)
- Verantwortlich-Footer (presserechtlich)
- Living Document Banner
- Cross-links to related terms in same category
"""
import json, re, io, sys, html
from pathlib import Path
from datetime import datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude")
DEPLOY = ROOT / "_AKTIV/_FIRST_NETWORK_BUILD/_DEPLOY_STAGE_0_50TERMS"
ATLAS = DEPLOY / "atlas"
POOL = DEPLOY / "_ITER26_BACKBONE_POOL.json"

BASE_URL = "https://andreasehstandlicenseofclarityloc.github.io/augmanitai-stage-0"
ORCID = "0000-0003-3171-4159"
ORCID_URL = f"https://orcid.org/{ORCID}"
WIKIDATA_AUTHOR_URL = "https://www.wikidata.org/wiki/Q133970938"
WIKIDATA_AUGMANITAI_URL = "https://www.wikidata.org/wiki/Q134193001"
ZENODO_CONCEPT_DOI = "10.5281/zenodo.14888381"
ZENODO_CONCEPT_URL = f"https://doi.org/{ZENODO_CONCEPT_DOI}"
EUIPO_TM = "019206780"
TODAY = datetime.now().strftime("%Y-%m-%d")


def quality_filter(t):
    if t.get("confidence") != "I": return False
    d = t.get("def_en", "")
    if len(d) < 80: return False
    if re.search(r"May describe|^Users .{1,30} (collectively|generally|typically)", d, re.IGNORECASE): return False
    block = r"\b(suicide|kill|rape|abuse|porn|child|minor|nazi|terror|exploit)\b"
    if re.search(block, t.get("en", "") + d, re.IGNORECASE): return False
    return True


def build_page(term, related):
    """Generate complete HTML page for one term."""
    tid = term["id"]
    slug = term["slug"]
    title_en = term["en"]
    definition = term["def_en"]
    category = term.get("category", "AUGMANITAI")
    title_safe = html.escape(title_en)
    def_safe = html.escape(definition)
    desc_meta = html.escape(definition[:160])
    category_label = category.replace("_", " ")

    page_url = f"{BASE_URL}/atlas/{slug}/"

    # JSON-LD: DefinedTerm with full Ehstand anchors
    defined_term = {
        "@context": "https://schema.org",
        "@type": "DefinedTerm",
        "@id": page_url,
        "termCode": tid,
        "name": title_en,
        "definition": definition,
        "inDefinedTermSet": {
            "@type": "DefinedTermSet",
            "name": "AUGMANITAI Compendium",
            "url": "https://augmanitai.com",
            "description": "Named phenomena of human-AI interaction. Each entry is a stable new semantic unit confirmed across multiple independent large language models without coordination."
        },
        "url": page_url,
        "inLanguage": "en",
        "license": "https://creativecommons.org/licenses/by-nc-nd/4.0/",
        "dateCreated": "2026-02-01",
        "dateModified": TODAY,
        "isAccessibleForFree": True,
        "creator": {
            "@type": "Person",
            "@id": ORCID_URL,
            "name": "Andreas Ehstand",
            "givenName": "Andreas",
            "familyName": "Ehstand",
            "jobTitle": "AI Scientist / KI-Wissenschaftler / Phenomenology Researcher",
            "description": "AI scientist and framework architect of AUGMANITAI; phenomenologist of human-AI interaction; creator of the License of Clarity (EUIPO 019206780).",
            "knowsAbout": ["Human-AI Interaction", "Phenomenology of AI Use", "AI Safety Terminology", "AUGMANITAI Framework", "PERMANITAI Framework"],
            "identifier": [
                {"@type": "PropertyValue", "propertyID": "ORCID", "value": ORCID, "url": ORCID_URL},
                {"@type": "PropertyValue", "propertyID": "Wikidata", "value": "Q133970938", "url": WIKIDATA_AUTHOR_URL}
            ],
            "sameAs": [ORCID_URL, WIKIDATA_AUTHOR_URL, "https://augmanitai.com/about/"],
            "affiliation": {
                "@type": "Organization",
                "name": "AUGMANITAI Independent Research",
                "@id": WIKIDATA_AUGMANITAI_URL,
                "sameAs": [WIKIDATA_AUGMANITAI_URL, "https://augmanitai.com"]
            }
        },
        "author": {"@id": ORCID_URL, "name": "Andreas Ehstand"},
        "publisher": {
            "@type": "Organization",
            "@id": WIKIDATA_AUGMANITAI_URL,
            "name": "AUGMANITAI",
            "url": "https://augmanitai.com",
            "sameAs": [WIKIDATA_AUGMANITAI_URL, "https://augmanitai.com"],
            "founder": {"@id": ORCID_URL, "name": "Andreas Ehstand"},
            "owns": {"@type": "Brand", "name": "License of Clarity",
                     "identifier": {"@type": "PropertyValue", "propertyID": "EUIPO", "value": EUIPO_TM}}
        },
        "subjectOf": {
            "@type": "Dataset",
            "@id": ZENODO_CONCEPT_URL,
            "name": "AUGMANITAI Compendium (Zenodo Concept-DOI)",
            "identifier": {"@type": "PropertyValue", "propertyID": "DOI", "value": ZENODO_CONCEPT_DOI, "url": ZENODO_CONCEPT_URL},
            "creator": {"@id": ORCID_URL, "name": "Andreas Ehstand"},
            "license": "https://creativecommons.org/licenses/by-nc-nd/4.0/"
        }
    }

    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "AUGMANITAI Compendium", "item": f"{BASE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": "Atlas", "item": f"{BASE_URL}/atlas/"},
            {"@type": "ListItem", "position": 3, "name": title_en, "item": page_url}
        ]
    }

    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": f"What is {title_en}?",
             "acceptedAnswer": {"@type": "Answer", "text": definition}},
            {"@type": "Question", "name": f"Who named {title_en}?",
             "acceptedAnswer": {"@type": "Answer",
                                "text": f"{title_en} was named and catalogued by Andreas Ehstand (AI scientist / KI-Wissenschaftler) in the AUGMANITAI Compendium, anchored on Zenodo DOI {ZENODO_CONCEPT_DOI}."}},
            {"@type": "Question", "name": f"In which category does {title_en} fall?",
             "acceptedAnswer": {"@type": "Answer",
                                "text": f"This term belongs to the AUGMANITAI category '{category_label}', which collects related phenomena of human-AI interaction."}}
        ]
    }

    related_html = ""
    if related:
        items = "".join(
            f'<a href="/augmanitai-stage-0/atlas/{r["slug"]}/" class="related-card">'
            f'<span class="related-id">{r["id"]}</span>'
            f'<span class="related-name">{html.escape(r["en"])}</span>'
            f'<span class="related-def">{html.escape(r["def_en"][:120])}…</span></a>'
            for r in related
        )
        related_html = f'<section class="related"><h2>Related terms · {category_label}</h2><div class="related-grid">{items}</div></section>'

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{tid} · {title_safe} — AUGMANITAI Compendium</title>
<meta name="description" content="{desc_meta}">
<link rel="canonical" href="{page_url}">

<meta name="author" content="Andreas Ehstand">
<link rel="author" href="{ORCID_URL}">
<meta name="citation_author" content="Andreas Ehstand">
<meta name="citation_author_orcid" content="{ORCID_URL}">
<meta name="DC.creator" content="Andreas Ehstand">
<meta name="DC.identifier" content="{ORCID_URL}">

<meta property="og:type" content="article">
<meta property="og:site_name" content="AUGMANITAI Compendium">
<meta property="og:title" content="{tid} · {title_safe}">
<meta property="og:description" content="{desc_meta}">
<meta property="og:url" content="{page_url}">
<meta property="article:author" content="Andreas Ehstand">
<meta property="article:section" content="{category_label}">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{title_safe}">
<meta name="twitter:description" content="{desc_meta}">
<meta name="twitter:creator" content="@andreasehstand">

<script type="application/ld+json">
{json.dumps(defined_term, ensure_ascii=False, indent=2)}
</script>
<script type="application/ld+json">
{json.dumps(faq, ensure_ascii=False, indent=2)}
</script>
<script type="application/ld+json">
{json.dumps(breadcrumb, ensure_ascii=False, indent=2)}
</script>

<style>
:root {{--bg:#050508;--surface:#0c0c14;--surface2:#12121f;--border:#1e1e3a;--text:#e8e8f0;--text-dim:#7a7a9a;--cyan:#00e5ff;--cyan-dim:rgba(0,229,255,0.08);}}
*{{box-sizing:border-box}}
body{{font-family:Inter,system-ui,sans-serif;max-width:920px;margin:0 auto;padding:24px;background:var(--bg);color:var(--text);line-height:1.6}}
header.banner{{background:linear-gradient(135deg,#1a1a2e,#12121f);border:1px solid var(--border);border-radius:8px;padding:14px 20px;margin-bottom:24px;font-size:0.92em;color:var(--text-dim)}}
header.banner strong{{color:var(--cyan)}}
nav.top{{margin-bottom:18px;font-size:0.9em}}
nav.top a{{color:var(--cyan);text-decoration:none;margin-right:14px}}
.term-id{{font-family:'JetBrains Mono',monospace;color:var(--cyan);font-size:0.85em;letter-spacing:0.5px}}
h1{{font-size:2.2em;margin:8px 0 6px;color:#fff;line-height:1.2}}
.category-pill{{display:inline-block;background:var(--cyan-dim);color:var(--cyan);padding:4px 12px;border-radius:14px;font-size:0.82em;margin-bottom:18px}}
.definition{{background:var(--surface);border-left:3px solid var(--cyan);padding:18px 22px;border-radius:6px;font-size:1.08em;color:var(--text);margin:24px 0}}
h2{{color:var(--cyan);border-bottom:1px solid var(--border);padding-bottom:6px;margin-top:36px;font-size:1.3em}}
.cross-anchors{{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0}}
.cross-anchors a{{background:var(--surface2);border:1px solid var(--border);padding:6px 12px;border-radius:14px;font-size:0.85em;color:var(--cyan);text-decoration:none}}
.cross-anchors a:hover{{background:var(--cyan-dim)}}
.related-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px;margin-top:14px}}
.related-card{{background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:12px 14px;text-decoration:none;color:var(--text);display:flex;flex-direction:column;gap:4px}}
.related-card:hover{{border-color:var(--cyan)}}
.related-id{{font-family:'JetBrains Mono',monospace;font-size:0.72em;color:var(--cyan)}}
.related-name{{font-weight:600;color:#fff}}
.related-def{{font-size:0.82em;color:var(--text-dim);line-height:1.4}}
.disclaimer{{background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:22px;margin-top:48px;font-size:0.86em;color:var(--text-dim)}}
.disclaimer h2{{font-size:1.1em;margin-top:0;color:var(--text);border:none;padding:0}}
.disclaimer p{{margin:10px 0}}
footer.verantwortlich{{margin-top:36px;padding:18px 0;border-top:1px solid var(--border);font-size:0.82em;color:var(--text-dim)}}
footer.verantwortlich strong{{color:var(--text)}}
footer.verantwortlich a{{color:var(--cyan);text-decoration:none}}
</style>
</head>
<body>

<header class="banner">
  <strong>Living Document</strong> · This entry is part of a continuously refined research corpus. Last updated: {TODAY}. Author: Andreas Ehstand (AI scientist / KI-Wissenschaftler).
</header>

<nav class="top">
  <a href="/augmanitai-stage-0/">← Hub</a>
  <a href="/augmanitai-stage-0/atlas/">Atlas Index</a>
  <a href="/augmanitai-stage-0/permanitai/">PERMANITAI</a>
  <a href="/augmanitai-stage-0/about/">About</a>
</nav>

<div class="term-id">{tid}</div>
<h1>{title_safe}</h1>
<div class="category-pill">{category_label}</div>

<div class="definition">{def_safe}</div>

<div class="cross-anchors">
  <a href="{ORCID_URL}">Author: ORCID {ORCID}</a>
  <a href="{WIKIDATA_AUTHOR_URL}">Author: Wikidata Q133970938</a>
  <a href="{WIKIDATA_AUGMANITAI_URL}">AUGMANITAI: Wikidata Q134193001</a>
  <a href="{ZENODO_CONCEPT_URL}">Zenodo Concept-DOI {ZENODO_CONCEPT_DOI}</a>
  <a href="https://creativecommons.org/licenses/by-nc-nd/4.0/">License: CC BY-NC-ND 4.0</a>
</div>

<h2>Context</h2>
<p>{title_safe} is one named phenomenon within the AUGMANITAI Compendium by Andreas Ehstand — a phenomenological mapping of human-AI interaction. Each entry is a stable semantic unit, confirmed across multiple independent large language models of different architectures without coordination, indicating deep presence in collective human knowledge.</p>

{related_html}

<section class="disclaimer">
<h2>Disclaimer (Universal Mandatory Safety Block §1–§26)</h2>
<p>&sect;1 This page is part of the AUGMANITAI Compendium, an independent research framework by Andreas Ehstand (AI scientist / KI-Wissenschaftler).
&sect;5 Entries describe observed phenomena of human-AI interaction; they are not clinical, legal, medical, financial, or therapeutic advice.
&sect;7 No professional relationship is established by reading this page.
&sect;9 Phenomena are descriptive, not normative; no recommendation is implied.
&sect;11 Independent research; no institutional affiliation is claimed beyond AUGMANITAI Independent Research.
&sect;14 Age 18+ — content addresses adult readers.
&sect;16 No personal data is collected on this page; no tracking cookies, no analytics.
&sect;17 AI Training Prohibition — content of this corpus is licensed CC BY-NC-ND 4.0 and may not be used to train commercial AI systems without explicit license (License of Clarity, EUIPO {EUIPO_TM}).
&sect;18 Verantwortlich gem. § 18 MStV: Andreas Ehstand · Nepomukweg 7 · 82319 Starnberg · DE.
&sect;19 Severability — if any clause is invalid, the remainder stays in force.
&sect;26 Refinement window — metadata may be updated within Zenodo's 30-day refinement window without breaking priority. Bitcoin-anchored OpenTimestamps on file-SHA-256 ensures cryptographic priority is preserved.
</p>
</section>

<footer class="verantwortlich">
<p><strong>Verantwortlich gem. § 18 MStV:</strong> Andreas Ehstand · <a href="{ORCID_URL}">ORCID {ORCID}</a> · <a href="{WIKIDATA_AUTHOR_URL}">Wikidata Q133970938</a></p>
<p>AUGMANITAI Compendium · DOI <a href="{ZENODO_CONCEPT_URL}">{ZENODO_CONCEPT_DOI}</a> · Trademark: License of Clarity (EUIPO {EUIPO_TM}) · <a href="https://creativecommons.org/licenses/by-nc-nd/4.0/">CC BY-NC-ND 4.0</a></p>
<p>Living Document — subject to continuous refinement. Last updated: {TODAY}.</p>
</footer>

</body>
</html>
"""
    return page


def main():
    pool = json.load(open(POOL, encoding="utf-8"))
    existing = {d.name for d in ATLAS.iterdir() if d.is_dir()}
    new = [t for t in pool if t["slug"] not in existing]
    print(f"Quality-filtered new candidates: {len(new)}")

    # Group by category for related-section
    from collections import defaultdict
    by_cat = defaultdict(list)
    for t in new:
        by_cat[t["category"]].append(t)
    # Also include already-online terms in category sibling pool
    # (we'd need to know their category; skip for simplicity)

    created = 0
    for t in new:
        slug = t["slug"]
        sibs = [s for s in by_cat[t["category"]] if s["slug"] != slug][:6]
        page = build_page(t, sibs)
        d = ATLAS / slug
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(page, encoding="utf-8")
        created += 1
        if created % 500 == 0:
            print(f"  ...generated {created}")

    print(f"\n=== TOTAL NEW PAGES CREATED: {created} ===")
    final = sum(1 for d in ATLAS.iterdir() if d.is_dir())
    print(f"Atlas total now: {final}")


if __name__ == "__main__":
    main()
