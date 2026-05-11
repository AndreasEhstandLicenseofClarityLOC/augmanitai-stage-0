#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 23 — Top-level polish.

- Inject ORCID author meta into Hub (index.html) and permanitai/index.html if missing.
- Inject OG + Twitter Card tags into 80 cluster-hub pages.
- Create atlas/index.html (was missing) as a simple alphabetical jump-table referring back to Hub.
- Enrich robots.txt with sitemap + ORCID-comment.
"""
import re, json, io, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")
ATLAS = DEPLOY / "atlas"
BASE_URL = "https://andreasehstandlicenseofclarityloc.github.io/augmanitai-stage-0"
ORCID = "0000-0003-3171-4159"
ORCID_URL = f"https://orcid.org/{ORCID}"
WIKIDATA_AUTHOR_URL = "https://www.wikidata.org/wiki/Q133970938"
WIKIDATA_AUGMANITAI_URL = "https://www.wikidata.org/wiki/Q134193001"
ZENODO_CONCEPT_URL = "https://doi.org/10.5281/zenodo.14888381"


AUTHOR_HEAD_TAGS = (
    f'<meta name="author" content="Andreas Ehstand">\n'
    f'<link rel="author" href="{ORCID_URL}">\n'
    f'<meta name="citation_author" content="Andreas Ehstand">\n'
    f'<meta name="citation_author_orcid" content="{ORCID_URL}">\n'
    f'<meta name="DC.creator" content="Andreas Ehstand">\n'
    f'<meta name="DC.identifier" content="{ORCID_URL}">\n'
)


def patch_top_level_authors():
    for special in ["index.html", "permanitai/index.html"]:
        fp = DEPLOY / special
        if not fp.exists(): continue
        c = fp.read_text(encoding="utf-8", errors="ignore")
        if ORCID in c:
            print(f"  {special}: ORCID already present, skipping")
            continue
        m = re.search(r"(<head[^>]*>)", c, re.IGNORECASE)
        if m:
            c = c[:m.end()] + "\n" + AUTHOR_HEAD_TAGS + c[m.end():]
            fp.write_text(c, encoding="utf-8")
            print(f"  Patched: {special} (ORCID inserted)")


def patch_cluster_og_twitter():
    """Inject OG + Twitter Card into the 80 cluster pages we patched in iter22."""
    cnt = 0
    for d in sorted(ATLAS.iterdir()):
        if not d.is_dir(): continue
        fp = d / "index.html"
        if not fp.exists(): continue
        c = fp.read_text(encoding="utf-8", errors="ignore")
        has_og = '<meta property="og:' in c or "<meta property='og:" in c
        has_tw = '<meta name="twitter:' in c or "<meta name='twitter:" in c
        if has_og and has_tw:
            continue
        title_m = re.search(r"<title>([^<]+)</title>", c)
        title = title_m.group(1) if title_m else d.name.upper()
        desc_m = re.search(r"<meta name=['\"]description['\"] content=['\"]([^'\"]+)['\"]", c)
        desc = desc_m.group(1) if desc_m else f"{title} — AUGMANITAI Compendium by Andreas Ehstand"
        url = f"{BASE_URL}/atlas/{d.name}/"
        og_tw = (
            f'<meta property="og:type" content="article">\n'
            f'<meta property="og:site_name" content="AUGMANITAI Compendium">\n'
            f'<meta property="og:title" content="{title}">\n'
            f'<meta property="og:description" content="{desc}">\n'
            f'<meta property="og:url" content="{url}">\n'
            f'<meta property="article:author" content="Andreas Ehstand">\n'
            f'<meta property="article:section" content="AUGMANITAI Compendium">\n'
            f'<meta name="twitter:card" content="summary">\n'
            f'<meta name="twitter:title" content="{title}">\n'
            f'<meta name="twitter:description" content="{desc}">\n'
            f'<meta name="twitter:creator" content="@andreasehstand">\n'
        )
        # Insert after <title>
        if title_m:
            c = c[:title_m.end()] + "\n" + og_tw + c[title_m.end():]
            fp.write_text(c, encoding="utf-8")
            cnt += 1
    print(f"Cluster pages enriched with OG+Twitter: {cnt}")


def create_atlas_index():
    """Create atlas/index.html — alphabetical jump-table."""
    fp = ATLAS / "index.html"
    if fp.exists():
        print(f"  atlas/index.html already exists")
        return
    slugs = sorted([d.name for d in ATLAS.iterdir() if d.is_dir()])
    # Group by first letter
    from collections import defaultdict
    by_letter = defaultdict(list)
    for s in slugs:
        by_letter[s[0].upper()].append(s)
    letters_nav = " ".join(f'<a href="#{l}">{l}</a>' for l in sorted(by_letter))
    sections = []
    for l in sorted(by_letter):
        items = "\n".join(f'<li><a href="/augmanitai-stage-0/atlas/{s}/">{s.replace("-"," ").title()}</a></li>' for s in by_letter[l])
        sections.append(f'<section id="{l}"><h2>{l}</h2><ul>{items}</ul></section>')
    sections_html = "\n".join(sections)
    schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "@id": f"{BASE_URL}/atlas/",
        "name": "AUGMANITAI Atlas — Alphabetical Index",
        "description": f"Alphabetical index of {len(slugs)} named phenomena in the AUGMANITAI Compendium by Andreas Ehstand (AI scientist / KI-Wissenschaftler).",
        "url": f"{BASE_URL}/atlas/",
        "inLanguage": "en",
        "license": "https://creativecommons.org/licenses/by-nc-nd/4.0/",
        "creator": {
            "@type": "Person",
            "@id": ORCID_URL,
            "name": "Andreas Ehstand",
            "jobTitle": "AI Scientist / KI-Wissenschaftler / Phenomenology Researcher",
            "sameAs": [ORCID_URL, WIKIDATA_AUTHOR_URL]
        },
        "author": {"@id": ORCID_URL, "name": "Andreas Ehstand"},
        "publisher": {
            "@type": "Organization", "@id": WIKIDATA_AUGMANITAI_URL, "name": "AUGMANITAI",
            "founder": {"@id": ORCID_URL, "name": "Andreas Ehstand"}
        },
        "subjectOf": {
            "@type": "Dataset", "@id": ZENODO_CONCEPT_URL,
            "name": "AUGMANITAI Compendium (Zenodo Concept-DOI)"
        },
        "isPartOf": {"@type": "DefinedTermSet", "name": "AUGMANITAI Compendium", "url": "https://augmanitai.com"}
    }
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AUGMANITAI Atlas — Alphabetical Index by Andreas Ehstand</title>
<meta name="description" content="Alphabetical index of {len(slugs)} named phenomena in the AUGMANITAI Compendium by Andreas Ehstand (AI scientist / KI-Wissenschaftler).">
<link rel="canonical" href="{BASE_URL}/atlas/">
{AUTHOR_HEAD_TAGS}
<meta property="og:type" content="website">
<meta property="og:title" content="AUGMANITAI Atlas — Alphabetical Index">
<meta property="og:description" content="{len(slugs)} named phenomena indexed alphabetically. By Andreas Ehstand.">
<meta property="og:url" content="{BASE_URL}/atlas/">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="AUGMANITAI Atlas">
<meta name="twitter:description" content="{len(slugs)} named phenomena by Andreas Ehstand">
<script type="application/ld+json">
{json.dumps(schema, ensure_ascii=False, indent=2)}
</script>
<style>
body {{font-family: Inter, system-ui, sans-serif; max-width: 1200px; margin: 0 auto; padding: 24px; background: #050508; color: #e8e8f0;}}
h1 {{color: #00e5ff;}}
h2 {{color: #00e5ff; border-bottom: 1px solid #1e1e3a; padding-bottom: 4px; margin-top: 32px;}}
nav.letters {{position: sticky; top: 0; background: #050508; padding: 8px 0; border-bottom: 1px solid #1e1e3a; z-index: 10;}}
nav.letters a {{display: inline-block; padding: 4px 8px; color: #00e5ff; text-decoration: none; font-weight: 500;}}
nav.letters a:hover {{background: #12121f;}}
ul {{list-style: none; padding: 0; column-count: 3; column-gap: 24px;}}
li a {{color: #e8e8f0; text-decoration: none; padding: 2px 0; display: block;}}
li a:hover {{color: #00e5ff;}}
footer {{margin-top: 64px; padding: 24px; border-top: 1px solid #1e1e3a; font-size: 0.85em; color: #7a7a9a;}}
footer a {{color: #00e5ff;}}
</style>
</head>
<body>
<h1>AUGMANITAI Atlas — Alphabetical Index</h1>
<p><strong>{len(slugs)} named phenomena</strong> by <a href="{ORCID_URL}">Andreas Ehstand</a> (AI scientist / KI-Wissenschaftler / Phenomenology Researcher).</p>
<p><a href="/augmanitai-stage-0/">← Back to Hub</a> · <a href="/augmanitai-stage-0/permanitai/">PERMANITAI Framework</a> · <a href="/augmanitai-stage-0/about/">About</a></p>
<nav class="letters">{letters_nav}</nav>
{sections_html}
<footer>
<p><strong>Verantwortlich gem. § 18 MStV:</strong> Andreas Ehstand · <a href="{ORCID_URL}">ORCID {ORCID}</a> · <a href="{WIKIDATA_AUTHOR_URL}">Wikidata Q133970938</a></p>
<p>AUGMANITAI Compendium · DOI <a href="{ZENODO_CONCEPT_URL}">10.5281/zenodo.14888381</a> · Trademark: License of Clarity (EUIPO 019206780) · License: <a href="https://creativecommons.org/licenses/by-nc-nd/4.0/">CC BY-NC-ND 4.0</a></p>
<p>Living Document — subject to continuous refinement.</p>
</footer>
</body>
</html>
"""
    fp.write_text(html, encoding="utf-8")
    print(f"  Created: atlas/index.html ({len(html)} chars, {len(slugs)} terms indexed)")


def enrich_robots():
    fp = DEPLOY / "robots.txt"
    c = fp.read_text(encoding="utf-8") if fp.exists() else ""
    if "andreas ehstand" not in c.lower():
        addition = (
            f"\n\n# AUGMANITAI Compendium · Author: Andreas Ehstand\n"
            f"# ORCID: {ORCID_URL}\n"
            f"# Wikidata: {WIKIDATA_AUTHOR_URL}\n"
            f"# AUGMANITAI Wikidata: {WIKIDATA_AUGMANITAI_URL}\n"
            f"# Zenodo Concept-DOI: {ZENODO_CONCEPT_URL}\n"
            f"# Role: AI Scientist / KI-Wissenschaftler / Phenomenology Researcher\n"
            f"Sitemap: {BASE_URL}/sitemap.xml\n"
        )
        fp.write_text(c + addition, encoding="utf-8")
        print(f"  Enriched: robots.txt")


def main():
    print("=== Patching top-level pages ===")
    patch_top_level_authors()
    print("\n=== Patching cluster pages with OG+Twitter ===")
    patch_cluster_og_twitter()
    print("\n=== Creating atlas/index.html ===")
    create_atlas_index()
    print("\n=== Enriching robots.txt ===")
    enrich_robots()


if __name__ == "__main__":
    main()
