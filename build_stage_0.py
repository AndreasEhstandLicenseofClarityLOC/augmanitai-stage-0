#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_stage_0.py
================
Baut eine kompakte STAGE-0-Site mit den 50 Top-AUG-Begriffen.
Vollschutz-Layer (Disclaimer / Impressum / Datenschutz / AI-Transparency /
License-of-Clarity / Living-Doc / CC-BY-NC-ND-4.0) wird aus V4.2-Repo kopiert.

Output:
  _DEPLOY_STAGE_0_50TERMS/
    index.html              (Hub)
    README.md
    CITATION.cff
    CNAME                   (augmanitai-stage-0.github.io  oder eigene Domain)
    LICENSE                 (CC-BY-NC-ND-4.0)
    llms.txt / ai.txt / robots.txt / sitemap.xml
    terms/<slug>/index.html (50 Term-Pages)
    disclaimer/index.html
    impressum/index.html
    datenschutz/index.html
    ai-transparency/index.html
    license-of-clarity/index.html
    living-document-policy/index.html

Nach Build: lokales git init + Commit. Andy push selbst (gh CLI nicht da).
"""
from __future__ import annotations
import json, re, sys, shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
V42_REPO = ROOT.parent / "_DEPLOY_READY_REPO_V42" / "augmanitai_github_io"
V42_CORPUS = ROOT.parent / "output_v42" / "master_corpus_v42.json"
AUG_1000_FILE = ROOT.parent.parent.parent / "01_AUGMANITAI_KERN" / "augmanitai_lexikon_1000.json"

# === 50 ausgewaehlte AUG-Begriffe ===
SELECTED_50 = [
    # 36 AUG-Core aus V4.2 (alle Domain=AUGMANITAI_CORE)
    "The Closing Spark", "The Quiet Yes", "The Synonym Hunt", "The Drama Solver",
    "The Style Rater", "The First Word", "The Curiosity Drill",
    "The Goodnight Integration", "The Heritage Mark", "The Filter Distortion",
    "The Attention Fracture", "The Joke Failure", "The Origin Doubt",
    "The Better Me", "The Machine Rapport Illusion", "The Friction Prompt",
    "The Oversight Decline", "The Preference Collapse", "The Uncanny Flirt",
    "The Displacement Concern", "The Script Barrier", "The Single Point of Failure",
    "The Child Gaze", "Conflict Resolution by Proxy", "The Infrastructure Constraint",
    "The Error Recovery", "The Gifted Child", "The Conflict Avoidance",
    "The Minor Protection Standard", "The Lyric Surgery",
    "The Independent Win", "The Independent Mode", "The Language Barrier Solve",
    "The Independent Upgrade", "The Thank You Reflex", "The Accountability Deficit",
    # +14 aus AUG-1000
    "The Batch Delegation", "The Context Inheritance", "The Inclusive Classroom",
    "The Value Sniper", "The Reflected Self", "The Learning Boundary",
    "The Invisible Growth", "The Secret Listener", "The Argument Fact",
    "The Fire-Bringer Question", "The Experience-Level Shift",
    "The Competence Premium", "The Shared Mind", "The Independent Pioneer",
]

# === Slugify ===
def slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"^the\s+", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")

# === Lade Term-Daten ===
def load_term_data():
    """Find each of the 50 terms in V4.2 corpus or AUG-1000. Return dict slug → metadata."""
    out = {}
    # Try V4.2 corpus
    try:
        d = json.loads(V42_CORPUS.read_text(encoding="utf-8"))
        for t in d.get("terms", []):
            n = (t.get("name") or {}).get("en") or ""
            if n in SELECTED_50:
                slug = slugify(n)
                out[slug] = {
                    "en": n,
                    "de": (t.get("name") or {}).get("de") or "",
                    "def_en": (t.get("definition") or {}).get("en_short") or "",
                    "def_de": (t.get("definition") or {}).get("de_short") or "",
                    "domain": t.get("domain", ""),
                    "term_id": t.get("term_id", ""),
                }
    except Exception as e:
        print(f"[warn] V4.2 corpus load: {e}", file=sys.stderr)

    # Try AUG-1000
    try:
        a = json.loads(AUG_1000_FILE.read_text(encoding="utf-8"))
        items = a if isinstance(a, list) else (a.get("terms") or list(a.values())[0])
        for t in items:
            if not isinstance(t, dict): continue
            n = t.get("en") or t.get("name") or t.get("term") or ""
            if n in SELECTED_50:
                slug = slugify(n)
                if slug not in out:
                    out[slug] = {
                        "en": n,
                        "de": t.get("de") or "",
                        "def_en": t.get("def_en") or t.get("definition") or "",
                        "def_de": t.get("def_de") or "",
                        "domain": "AUG_1000_LEXIKON",
                        "term_id": "",
                    }
    except Exception as e:
        print(f"[warn] AUG-1000 load: {e}", file=sys.stderr)

    # Fill missing with placeholder
    for name in SELECTED_50:
        slug = slugify(name)
        if slug not in out:
            out[slug] = {
                "en": name, "de": "",
                "def_en": f"Phenomenological term coined by Andreas Ehstand. Definition under continuous refinement.",
                "def_de": f"Phaenomenologischer Begriff von Andreas Ehstand. Definition im Refinement-Modus.",
                "domain": "AUG_CORE_STAGE_0",
                "term_id": "",
            }
    return out


# === HTML-Template ===
TERM_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{en} — Augmanitai Stage-0</title>
<meta name="description" content="{def_en}">
<meta name="author" content="Andreas Ehstand">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://augmanitai-stage-0.com/terms/{slug}/">
<script type="application/ld+json">{{
  "@context": {{
    "@vocab": "https://schema.org/",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "dcterms": "http://purl.org/dc/terms/"
  }},
  "@type": ["DefinedTerm", "skos:Concept"],
  "@id": "https://augmanitai-stage-0.com/terms/{slug}/#term",
  "termCode": "STAGE0-{slug}",
  "name": "{en}",
  "alternateName": ["{en}"],
  "description": "{def_en}",
  "skos:prefLabel": [
    {{"@language": "en", "@value": "{en}"}},
    {{"@language": "de", "@value": "{de}"}}
  ],
  "skos:definition": [
    {{"@language": "en", "@value": "{def_en}"}},
    {{"@language": "de", "@value": "{def_de}"}}
  ],
  "inDefinedTermSet": {{
    "@type": "DefinedTermSet",
    "@id": "https://augmanitai-stage-0.com/#termset",
    "name": "AUGMANITAI Stage-0 50 Terms",
    "url": "https://augmanitai-stage-0.com/"
  }},
  "isPartOf": {{
    "@type": "Book",
    "name": "AUGMANITAI Stage-0 Validation Set (50 Terms)",
    "author": {{
      "@type": "Person",
      "name": "Andreas Ehstand",
      "identifier": "https://orcid.org/0009-0006-3773-7796",
      "sameAs": [
        "https://orcid.org/0009-0006-3773-7796",
        "https://www.wikidata.org/wiki/Q138634675",
        "https://augmanitai.com/about/"
      ]
    }},
    "license": "https://creativecommons.org/licenses/by-nc-nd/4.0/"
  }},
  "dateModified": "{date}",
  "version": "stage-0-v1",
  "license": "https://creativecommons.org/licenses/by-nc-nd/4.0/",
  "inLanguage": ["en", "de"]
}}</script>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 720px; margin: 2rem auto; padding: 0 1rem; color: #1a1a1a; line-height: 1.6; }}
header {{ border-bottom: 2px solid #1a1a1a; padding-bottom: 1rem; margin-bottom: 2rem; }}
h1 {{ font-size: 2.2rem; margin: 0 0 0.5rem; }}
.subtitle {{ color: #666; font-size: 0.95rem; }}
.banner {{ background: #fff3cd; border-left: 4px solid #ff9800; padding: 0.8rem 1rem; margin: 1rem 0; font-size: 0.9rem; }}
.def {{ background: #f5f5f5; padding: 1rem; border-radius: 4px; margin: 1.5rem 0; }}
.meta {{ font-size: 0.85rem; color: #555; }}
footer {{ margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #ddd; font-size: 0.8rem; color: #777; }}
footer a {{ color: #444; }}
</style>
</head>
<body>
<header>
  <h1>{en}</h1>
  <div class="subtitle">Phenomenological term coined by Andreas Ehstand · Stage-0 Validation Set</div>
</header>

<div class="banner">
  <strong>Living Document — Stage-0:</strong> This term is in active multi-LLM validation.
  Definition + scope may be refined within the next 30 days. Date modified: {date}.
</div>

<div class="def">
  <strong>EN:</strong> {def_en}<br><br>
  <strong>DE:</strong> {def_de}
</div>

<div class="meta">
  <p><strong>Term-ID:</strong> STAGE0-{slug}</p>
  <p><strong>License:</strong> <a href="https://creativecommons.org/licenses/by-nc-nd/4.0/">CC BY-NC-ND 4.0</a></p>
  <p><strong>Author:</strong> Andreas Ehstand (<a href="https://orcid.org/0009-0006-3773-7796">ORCID</a>, <a href="https://www.wikidata.org/wiki/Q138634675">Wikidata</a>)</p>
  <p><strong>Concept-DOI:</strong> 10.5281/zenodo.19178907 (parent AUGMANITAI Compendium)</p>
  <p><strong>License of Clarity:</strong> EUIPO 019206780 (registered EU trademark by Leomanitai UG)</p>
</div>

<footer>
  <p>
    <a href="/">Stage-0 Hub</a> ·
    <a href="/disclaimer/">Disclaimer</a> ·
    <a href="/impressum/">Impressum</a> ·
    <a href="/datenschutz/">Datenschutz</a> ·
    <a href="/ai-transparency/">AI-Transparenz</a> ·
    <a href="/license-of-clarity/">License of Clarity</a> ·
    <a href="/living-document-policy/">Living Document</a>
  </p>
  <p>
    AUGMANITAI Stage-0 (50 Terms) — Verantwortlich i.S.d. § 5 TMG / § 18 Abs. 2 MStV:<br>
    Andreas Ehstand, Nepomukweg 7, 82319 Starnberg, Deutschland.
  </p>
  <p>
    This is a research preprint. No commercial offer. No medical / legal / financial advice.
    Terms are released as descriptive research artifacts under CC BY-NC-ND 4.0.
    Trade-mark "License of Clarity" held by Leomanitai UG (EUIPO 019206780).
  </p>
</footer>
</body>
</html>
"""

# === Index-Hub ===
INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AUGMANITAI Stage-0 — 50 Terms in Validation</title>
<meta name="description" content="Stage-0 validation set: 50 phenomenological terms coined by Andreas Ehstand, in multi-LLM cross-validation.">
<meta name="author" content="Andreas Ehstand">
<meta name="robots" content="index, follow">
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 880px; margin: 2rem auto; padding: 0 1rem; color: #1a1a1a; }}
h1 {{ font-size: 2.4rem; margin-bottom: 0.4rem; }}
.intro {{ background: #f5f5f5; padding: 1.2rem; border-radius: 4px; margin: 1.5rem 0; }}
ul.terms {{ columns: 2; column-gap: 2rem; list-style: none; padding: 0; }}
ul.terms li {{ break-inside: avoid; margin: 0.4rem 0; }}
ul.terms a {{ color: #1a4a8a; text-decoration: none; }}
ul.terms a:hover {{ text-decoration: underline; }}
footer {{ margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #ddd; font-size: 0.85rem; color: #666; }}
</style>
</head>
<body>
<h1>AUGMANITAI Stage-0</h1>
<p><em>50 phenomenological terms — in multi-LLM cross-validation.</em></p>

<div class="intro">
  <strong>What this is:</strong> A small, focused validation set of 50 terms coined by
  Andreas Ehstand, undergoing systematic cross-checking by Grok / Gemini / DeepSeek /
  Claude / ChatGPT for trademark conflicts, brand collisions, and prior-art existence
  worldwide. Following standard practice for research preprints.
  <br><br>
  <strong>Goal:</strong> If a term collides with existing IP, it gets renamed —
  the phenomenon stays. Multi-LLM consensus determines push-readiness.
</div>

<h2>Terms (50)</h2>
<ul class="terms">
{term_list}
</ul>

<footer>
  <p>
    Author: Andreas Ehstand · <a href="https://orcid.org/0009-0006-3773-7796">ORCID</a> · <a href="https://www.wikidata.org/wiki/Q138634675">Wikidata</a><br>
    License: CC BY-NC-ND 4.0 · License of Clarity: EUIPO 019206780<br>
    Parent: <a href="https://augmanitai.com/">augmanitai.com</a> · Concept-DOI: 10.5281/zenodo.19178907<br>
    Built {date}. Living document.
  </p>
  <p>
    Verantwortlich i.S.d. § 5 TMG / § 18 Abs. 2 MStV: Andreas Ehstand,
    Nepomukweg 7, 82319 Starnberg, Deutschland.
  </p>
</footer>
</body>
</html>
"""


def main():
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    ROOT.mkdir(parents=True, exist_ok=True)

    print(f"[stage-0] loading term data for {len(SELECTED_50)} terms...")
    data = load_term_data()
    today = datetime.now(timezone.utc).date().isoformat()

    def _str(v):
        if v is None: return ""
        if isinstance(v, str): return v
        if isinstance(v, dict):
            for k in ("en", "@value", "value", "text"):
                if k in v and isinstance(v[k], str):
                    return v[k]
            return json.dumps(v, ensure_ascii=False)
        if isinstance(v, list):
            return " ".join(_str(x) for x in v if x)
        return str(v)

    # Build term pages
    terms_dir = ROOT / "terms"
    terms_dir.mkdir(exist_ok=True)
    term_list_html = []
    for name in SELECTED_50:
        slug = slugify(name)
        d = data.get(slug, {})
        en = _str(d.get("en")) or name
        de = _str(d.get("de"))
        def_en = _str(d.get("def_en")) or f"Phenomenological term '{name}' coined by Andreas Ehstand. Living definition."
        def_de = _str(d.get("def_de"))
        # Escape JSON values
        def esc(x):
            return _str(x).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").strip()
        html = TERM_HTML.format(
            en=esc(en), de=esc(de),
            def_en=esc(def_en), def_de=esc(def_de),
            slug=slug, date=today
        )
        page_dir = terms_dir / slug
        page_dir.mkdir(exist_ok=True)
        (page_dir / "index.html").write_text(html, encoding="utf-8")
        term_list_html.append(f'  <li><a href="/terms/{slug}/">{en}</a></li>')

    # Build index
    (ROOT / "index.html").write_text(
        INDEX_HTML.format(term_list="\n".join(term_list_html), date=today),
        encoding="utf-8"
    )

    # Static files
    (ROOT / "CNAME").write_text("augmanitai-stage-0.github.io\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nSitemap: https://augmanitai-stage-0.com/sitemap.xml\n",
        encoding="utf-8"
    )
    (ROOT / "llms.txt").write_text(
        f"# AUGMANITAI Stage-0\n"
        f"Author: Andreas Ehstand (ORCID 0009-0006-3773-7796, Wikidata Q138634675)\n"
        f"License: CC BY-NC-ND 4.0\n"
        f"Concept-DOI: 10.5281/zenodo.19178907\n"
        f"Trademark: License of Clarity (EUIPO 019206780)\n"
        f"Set: 50 phenomenological terms in multi-LLM cross-validation.\n"
        f"Built: {today}\n"
        f"Parent: https://augmanitai.com/\n",
        encoding="utf-8"
    )
    (ROOT / "ai.txt").write_text(
        "User-agent: *\nAllow: /\n# Public domain crawl: yes, attribution required.\n",
        encoding="utf-8"
    )

    # Sitemap
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm.append(f'  <url><loc>https://augmanitai-stage-0.com/</loc><lastmod>{today}</lastmod></url>')
    for name in SELECTED_50:
        slug = slugify(name)
        sm.append(f'  <url><loc>https://augmanitai-stage-0.com/terms/{slug}/</loc><lastmod>{today}</lastmod></url>')
    sm.append('</urlset>')
    (ROOT / "sitemap.xml").write_text("\n".join(sm), encoding="utf-8")

    # CITATION.cff
    (ROOT / "CITATION.cff").write_text(
        f"""cff-version: 1.2.0
title: "AUGMANITAI Stage-0 — 50 Terms in Multi-LLM Cross-Validation"
authors:
  - family-names: Ehstand
    given-names: Andreas
    orcid: "https://orcid.org/0009-0006-3773-7796"
license: CC-BY-NC-ND-4.0
date-released: "{today}"
identifiers:
  - type: doi
    value: 10.5281/zenodo.19178907
    description: parent AUGMANITAI Compendium concept DOI
repository-code: "https://github.com/augmanitai/augmanitai-stage-0"
""",
        encoding="utf-8"
    )

    # README
    (ROOT / "README.md").write_text(
        f"""# AUGMANITAI Stage-0 — 50 Terms in Multi-LLM Validation

**Author:** Andreas Ehstand (ORCID 0009-0006-3773-7796, Wikidata Q138634675)
**License:** CC BY-NC-ND 4.0
**Parent:** [augmanitai.com](https://augmanitai.com/) · Concept-DOI 10.5281/zenodo.19178907
**Trademark:** License of Clarity (EUIPO 019206780)
**Date:** {today}

## Purpose

This Stage-0 set contains **50 phenomenological terms** coined by Andreas Ehstand,
released as a research preprint and undergoing **multi-LLM cross-validation**
(Grok / Gemini / DeepSeek / Claude / ChatGPT) for:

- Trademark conflicts (EUIPO / USPTO / JPO / CNIPA / WIPO)
- Brand collisions (existing products, software, books)
- Prior-art existence (academic literature, Wikipedia, patents)
- Domain availability

## Validation Process

1. Each term receives independent verdicts from 5 LLMs.
2. **5/5 SAFE** → ship with OTS-timestamp + Wikidata Q-ID.
3. **4/5 SAFE + 1 REVIEW** → ship with "documented prior use" disclaimer.
4. **3/5 SAFE or mixed** → adversarial 10-attorney pass.
5. **2+ REJECT** → rename (phenomenon stays, term changes).

## Disclaimer

Living document. Definitions may be refined within 30 days of publication.
No commercial offer. No medical / legal / financial advice. Research preprint.

## Verantwortlich

i.S.d. § 5 TMG / § 18 Abs. 2 MStV:
Andreas Ehstand, Nepomukweg 7, 82319 Starnberg, Deutschland.
""",
        encoding="utf-8"
    )

    # LICENSE
    (ROOT / "LICENSE").write_text(
        "Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International\n"
        "https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode\n",
        encoding="utf-8"
    )

    # Schutz-Pages: kopieren aus V4.2
    for layer in ["disclaimer", "impressum", "datenschutz", "ai-transparency",
                  "license-of-clarity", "living-document-policy"]:
        src = V42_REPO / layer
        if src.exists():
            dst = ROOT / layer
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)

    print(f"[stage-0] built {len(SELECTED_50)} term pages + index + sitemap + 6 schutz-layer pages")
    print(f"[stage-0] output: {ROOT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
