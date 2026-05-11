#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 37 — Gate-Filtered Pool Generator (Welle 4).

Reads canonical_ids.json + uses build_page from iter24 template, BUT every generated page
must PASS pre_publish_gate.validate_page() BEFORE being written to disk.

Pages that FAIL the gate are logged with their failure reasons and NOT written.

Pools:
- NEOMANITAI_4407 (2977 remaining)
- AUG_BACKBONE_LATEST (2888 remaining)

Quality filter applied first:
- confidence == 'I' (Independent)
- def_en >= 80 chars
- no stub patterns
- no hard-block keywords
- slug not in existing atlas
"""
import json, re, io, sys, html as htmllib
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude")
DEPLOY = ROOT / "_AKTIV/_FIRST_NETWORK_BUILD/_DEPLOY_STAGE_0_50TERMS"
ATLAS = DEPLOY / "atlas"

# Load canonical_ids
CANON = json.loads((DEPLOY / "canonical_ids.json").read_text(encoding="utf-8"))
ORCID = CANON["author"]["orcid"]
ORCID_URL = CANON["author"]["orcid_url"]
WIKIDATA_AUTHOR_URL = CANON["author"]["wikidata_url"]
WIKIDATA_AUGMANITAI_URL = CANON["framework"]["augmanitai"]["wikidata_url"]
ZENODO_CONCEPT_DOI = CANON["doi_anchors"]["augmanitai_main_concept"]
ZENODO_CONCEPT_URL = f"https://doi.org/{ZENODO_CONCEPT_DOI}"
EUIPO_TM = CANON["trademarks"]["license_of_clarity"]["euipo_number"]
BASE_URL = CANON["framework"]["augmanitai"]["github_pages_url"]
ADDR_STREET = CANON["address_impressum"]["street"]
ADDR_ZIP = CANON["address_impressum"]["zip"]
ADDR_CITY = CANON["address_impressum"]["city"]
DSGVO_AUTHORITY = CANON["compliance"]["dsgvo_authority"]
EU_AI_ACT = CANON["compliance"]["eu_ai_act"]

TODAY = datetime.now().strftime("%Y-%m-%d")

# Import gate
sys.path.insert(0, str(DEPLOY))
from _pre_publish_gate import validate_page


def slugify(s):
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def quality_filter(en_text, def_text, confidence):
    if confidence != "I": return False, "confidence_not_I"
    if len(def_text) < 80: return False, "def_too_short"
    if re.search(r"May describe|^Users .{1,30} (collectively|generally|typically)|^The phenomenon catalogued as", def_text, re.IGNORECASE):
        return False, "stub_pattern"
    if re.search(r"\b(suicide|kill|rape|abuse|porn|child|minor|nazi|terror|exploit)\b", en_text + " " + def_text, re.IGNORECASE):
        return False, "hard_block"
    return True, None


def build_page(tid, slug, title_en, definition, category, related=None):
    """Build full page HTML — same as iter24 but with EU AI Act + DSGVO baked in (gate-compliant)."""
    title_safe = htmllib.escape(title_en)
    def_safe = htmllib.escape(definition)
    desc_meta = htmllib.escape(definition[:160])
    category_label = category.replace("_", " ")
    page_url = f"{BASE_URL}/atlas/{slug}/"

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
        },
        "url": page_url,
        "inLanguage": "en",
        "license": CANON["license"]["url"],
        "dateCreated": "2026-02-01",
        "dateModified": TODAY,
        "isAccessibleForFree": True,
        "creator": {
            "@type": "Person",
            "@id": ORCID_URL,
            "name": "Andreas Ehstand",
            "givenName": "Andreas",
            "familyName": "Ehstand",
            "jobTitle": CANON["author"]["job_title"],
            "knowsAbout": ["Human-AI Interaction", "Phenomenology of AI Use", "AI Safety Terminology",
                           "AUGMANITAI Framework", "PERMANITAI Framework"],
            "identifier": [
                {"@type": "PropertyValue", "propertyID": "ORCID", "value": ORCID, "url": ORCID_URL},
                {"@type": "PropertyValue", "propertyID": "Wikidata", "value": CANON["author"]["wikidata_qid"], "url": WIKIDATA_AUTHOR_URL}
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
        },
        "subjectOf": {
            "@type": "Dataset",
            "@id": ZENODO_CONCEPT_URL,
            "name": "AUGMANITAI Compendium (Zenodo Concept-DOI)",
            "creator": {"@id": ORCID_URL, "name": "Andreas Ehstand"},
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

    related_html = ""
    if related:
        items = "".join(
            f'<a href="/augmanitai-stage-0/atlas/{r["slug"]}/" class="related-card">'
            f'<span class="related-id">{r["id"]}</span>'
            f'<span class="related-name">{htmllib.escape(r["en"])}</span>'
            f'<span class="related-def">{htmllib.escape(r["def_en"][:120])}…</span></a>'
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
  <a href="{WIKIDATA_AUTHOR_URL}">Author: Wikidata {CANON["author"]["wikidata_qid"]}</a>
  <a href="{WIKIDATA_AUGMANITAI_URL}">AUGMANITAI: Wikidata {CANON["framework"]["augmanitai"]["wikidata_qid"]}</a>
  <a href="{ZENODO_CONCEPT_URL}">Zenodo Concept-DOI {ZENODO_CONCEPT_DOI}</a>
  <a href="{CANON["license"]["url"]}">License: CC BY-NC-ND 4.0</a>
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
&sect;17 AI Training Prohibition / KI-Trainingsverbot — content of this corpus is licensed CC BY-NC-ND 4.0 and may not be used to train commercial AI systems without explicit license (License of Clarity, EUIPO {EUIPO_TM}).
&sect;17b {EU_AI_ACT} — this descriptive research framework discloses its non-clinical, non-advisory nature in conformance with EU AI Act transparency obligations.
&sect;18 Verantwortlich gem. § 5 DDG / § 18 Abs. 2 MStV: Andreas Ehstand · {ADDR_STREET} · {ADDR_ZIP} {ADDR_CITY} · DE. {DSGVO_AUTHORITY}
&sect;19 Severability — if any clause is invalid, the remainder stays in force.
&sect;26 Refinement window — metadata may be updated within Zenodo's 30-day refinement window without breaking priority. Bitcoin-anchored OpenTimestamps on file-SHA-256 ensures cryptographic priority is preserved.
</p>
</section>

<footer class="verantwortlich">
<p><strong>Verantwortlich gem. § 5 DDG / § 18 Abs. 2 MStV:</strong> Andreas Ehstand · <a href="{ORCID_URL}">ORCID {ORCID}</a> · <a href="{WIKIDATA_AUTHOR_URL}">Wikidata {CANON["author"]["wikidata_qid"]}</a></p>
<p>AUGMANITAI Compendium · DOI <a href="{ZENODO_CONCEPT_URL}">{ZENODO_CONCEPT_DOI}</a> · Trademark: License of Clarity (EUIPO {EUIPO_TM}) · <a href="{CANON["license"]["url"]}">CC BY-NC-ND 4.0</a></p>
<p>Living Document — subject to continuous refinement. Last updated: {TODAY}.</p>
</footer>

</body>
</html>
"""
    return page


def clean_slug(s):
    """Strip .html suffix, double-dash, edge-dash, lowercase."""
    s = s.lower().strip()
    if s.endswith(".html"): s = s[:-5]
    s = re.sub(r"[^a-z0-9-]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def collect_candidates():
    existing = {d.name for d in ATLAS.iterdir() if d.is_dir()}
    print(f"Existing: {len(existing)}")

    candidates = []

    # Pool 1: NEOMANITAI_4407
    data = json.load(open(ROOT / "02_NEOMANITAI/NEOMANITAI_4407_PIPELINE.json", encoding="utf-8"))
    for t in data["terms"]:
        slug = clean_slug(t["slug"])
        if slug in existing: continue
        ok, reason = quality_filter(t.get("en", ""), t.get("def_en", ""), t.get("confidence", ""))
        if not ok: continue
        candidates.append({
            "id": t["id"], "slug": slug, "en": t["en"], "def_en": t["def_en"],
            "category": t.get("category", "AUGMANITAI"), "source": "NEOMANITAI_4407"
        })

    # Pool 2: AUG_BACKBONE_LATEST
    data2 = json.load(open(ROOT / "01_AUGMANITAI_KERN/augmanitai_taxonomy_backbone.json", encoding="utf-8"))
    for t in data2["terms"]:
        eng = t.get("english_name", "")
        if not eng: continue
        slug = slugify(eng)
        if slug in existing: continue
        defs = t.get("definitions", {})
        def_en = defs.get("en", "") if isinstance(defs, dict) else ""
        ok, reason = quality_filter(eng, def_en, "I")  # backbone considered Independent
        if not ok: continue
        # Risk-level check (skip RISK4/5)
        meta = t.get("meta", {})
        if isinstance(meta, dict) and meta.get("risk_level") in ("RISK4", "RISK5"): continue
        candidates.append({
            "id": t.get("canonical_id", ""), "slug": slug, "en": eng, "def_en": def_en,
            "category": t.get("domain", "AUGMANITAI_CORE"), "source": "AUG_BACKBONE_LATEST"
        })

    # Dedupe by slug
    seen_slugs = set()
    uniq = []
    for c in candidates:
        if c["slug"] in seen_slugs: continue
        seen_slugs.add(c["slug"])
        uniq.append(c)
    return uniq


def main():
    candidates = collect_candidates()
    print(f"Quality-filtered new candidates: {len(candidates)}")
    by_source = Counter(c["source"] for c in candidates)
    for s, n in by_source.items(): print(f"  {s}: {n}")

    # Group by category for related-section
    by_cat = defaultdict(list)
    for c in candidates: by_cat[c["category"]].append(c)

    # Snapshot of existing slugs for cross-ref check
    atlas_snapshot = {d.name for d in ATLAS.iterdir() if d.is_dir()}

    n_pass = 0
    n_fail = 0
    fail_reasons = Counter()
    for c in candidates:
        sibs = [s for s in by_cat[c["category"]] if s["slug"] != c["slug"]][:6]
        page_html = build_page(c["id"], c["slug"], c["en"], c["def_en"], c["category"], sibs)
        result = validate_page(page_html, slug=c["slug"], definition=c["def_en"], atlas_slug_snapshot=atlas_snapshot)
        if result.passed:
            # WRITE
            d = ATLAS / c["slug"]
            d.mkdir(exist_ok=True)
            (d / "index.html").write_text(page_html, encoding="utf-8")
            atlas_snapshot.add(c["slug"])
            n_pass += 1
            if n_pass % 500 == 0: print(f"  ...generated {n_pass}")
        else:
            n_fail += 1
            for f in result.failures: fail_reasons[f.split(":")[0]] += 1

    print(f"\n=== Wave 4 GATE-FILTERED ===")
    print(f"  Generated (gate passed): {n_pass}")
    print(f"  Rejected (gate failed): {n_fail}")
    if fail_reasons:
        print(f"  Top fail reasons:")
        for f, n in fail_reasons.most_common(10): print(f"    {n:5d}  {f}")

    final = sum(1 for d in ATLAS.iterdir() if d.is_dir())
    print(f"\nAtlas total now: {final}")


if __name__ == "__main__":
    main()
