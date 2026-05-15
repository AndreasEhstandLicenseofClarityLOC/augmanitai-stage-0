#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_stage_0.py  (V2 — V4.2-Template-Reuse)
============================================
Baut die STAGE-0-Site fuer 50 AUG-Begriffe im V4.2-Atlas-Stil:
  - Echte AUG-IDs (AUG-XXXX) statt STAGE0-slug
  - V4.2-CSS / Pills / Metadata-Grid / BibTeX-Citation / JSON-LD-SKOS
  - KG-Cross-Links zwischen Stage-0-Begriffen (related_to gefiltert auf Stage-0-Pool)
  - ISO 704 / 1087 / 30042 inspired (no compliance claim)
  - FETTER roter Living/Legal-Banner GANZ OBEN vor jedem Begriff
  - 0 Methodik-Disclosure (kein Multi-LLM / Cross-Validation / LLM-Namen)

Output:
  _DEPLOY_STAGE_0_50TERMS/
    index.html                  (Hub mit Pills + Term-Liste)
    README.md / CITATION.cff / LICENSE / CNAME / llms.txt / ai.txt / robots.txt / sitemap.xml
    atlas/<AUG-XXXX>/index.html (50 Term-Pages)
    disclaimer/ impressum/ datenschutz/ ai-transparency/ license-of-clarity/ living-document-policy/
"""
from __future__ import annotations
import json, re, sys, shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent          # .../_DEPLOY_STAGE_0_50TERMS
BUILD_ROOT = ROOT.parent                          # .../_FIRST_NETWORK_BUILD
CLAUDE_ROOT = BUILD_ROOT.parent.parent            # .../Claude
V42_REPO = BUILD_ROOT / "_DEPLOY_READY_REPO_V42" / "augmanitai_github_io"
V42_CORPUS = BUILD_ROOT / "output_v42" / "master_corpus_v42.json"
AUG_1000_FILE = CLAUDE_ROOT / "01_AUGMANITAI_KERN" / "augmanitai_lexikon_1000.json"

# === 50 ausgewaehlte AUG-Begriffe (Stage-0 Pool) ===
SELECTED_50 = [
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
    "The Batch Delegation", "The Context Inheritance", "The Inclusive Classroom",
    "The Value Sniper", "The Reflected Self", "The Learning Boundary",
    "The Invisible Growth", "The Secret Listener", "The Argument Fact",
    "The Fire-Bringer Question", "The Experience-Level Shift",
    "The Competence Premium", "The Shared Mind", "The Independent Pioneer",
]

# Manual ID fallback (for 3 terms not in V4.2 corpus)
MANUAL_ID = {
    "The Fire-Bringer Question": "AUG-0645",
    "The Experience-Level Shift": "AUG-0813",
    "The Independent Pioneer":   "AUG-STAGE0-50",  # nicht in beiden Quellen
}


def slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"^the\s+", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def load_corpus():
    """Return {en_name: full_term_dict} merged from V4.2 + AUG-1000."""
    bag = {}
    # 1) V4.2 corpus (primary — has term_id + relations)
    try:
        d = json.loads(V42_CORPUS.read_text(encoding="utf-8"))
        for t in d.get("terms", []):
            n = (t.get("name") or {}).get("en") or ""
            if n in SELECTED_50:
                bag[n] = t
    except Exception as e:
        print(f"[warn] V4.2 corpus: {e}", file=sys.stderr)

    # 2) AUG-1000 fallback for missing
    try:
        a = json.loads(AUG_1000_FILE.read_text(encoding="utf-8"))
        items = a if isinstance(a, list) else (a.get("terms") or list(a.values())[0])
        for t in items:
            if not isinstance(t, dict): continue
            n = t.get("name") or t.get("en") or t.get("term") or ""
            if n in SELECTED_50 and n not in bag:
                bag[n] = {
                    "term_id": t.get("id") or MANUAL_ID.get(n, ""),
                    "name": {"en": n, "de": n},
                    "definition": {
                        "en_short": t.get("definition_en") or "",
                        "de_short": t.get("definition_de") or "",
                        "en_full":  t.get("definition_en") or "",
                        "de_full":  t.get("definition_de") or "",
                    },
                    "distinctions": {
                        "en": t.get("distinction_en") or "",
                        "de": t.get("abgrenzung_de") or "",
                    },
                    "domain": "AUG_1000_LEXIKON",
                    "cluster": "AUG-1000",
                    "w3id_slug": slugify(n),
                    "risk_level": {"level": "GREEN", "reason": "AUG-1000 baseline"},
                    "trade_secret_layer": "PUBLIC_OK",
                    "relations": {"related_to": []},
                    "phenomenology_category": "Routine",
                    "meta": {
                        "license": "CC BY-NC-ND 4.0",
                        "doi": "10.5281/zenodo.19178907",
                        "orcid": "0009-0006-3773-7796",
                        "iso_standards_inspired": ["ISO 704", "ISO 1087", "ISO 30042"],
                    },
                }
    except Exception as e:
        print(f"[warn] AUG-1000: {e}", file=sys.stderr)

    # 3) Placeholder for anything still missing
    for n in SELECTED_50:
        if n not in bag:
            bag[n] = {
                "term_id": MANUAL_ID.get(n, "AUG-STAGE0-XX"),
                "name": {"en": n, "de": n},
                "definition": {
                    "en_short": f"Phenomenological term '{n}' coined by Andreas Ehstand. Definition under continuous refinement.",
                    "de_short": f"Phaenomenologischer Begriff '{n}' von Andreas Ehstand. Definition im Refinement.",
                    "en_full":  "",
                    "de_full":  "",
                },
                "distinctions": {"en": "", "de": ""},
                "domain": "AUG_STAGE0",
                "cluster": "Stage-0",
                "w3id_slug": slugify(n),
                "risk_level": {"level": "GREEN", "reason": "Stage-0 baseline"},
                "trade_secret_layer": "PUBLIC_OK",
                "relations": {"related_to": []},
                "phenomenology_category": "Routine",
                "meta": {
                    "license": "CC BY-NC-ND 4.0",
                    "doi": "10.5281/zenodo.19178907",
                    "orcid": "0009-0006-3773-7796",
                    "iso_standards_inspired": ["ISO 704", "ISO 1087", "ISO 30042"],
                },
            }
    return bag


# ====== TOP LEGAL NOTICE (fett, rot, ueber JEDEM Begriff) ======
TOP_LEGAL = """<div class="legal-top" role="banner" style="border:3px solid #b00020;background:#fff3f3;padding:14px 18px;margin:0 0 18px;font-family:system-ui,sans-serif;font-size:0.95rem;line-height:1.55;border-radius:4px;">
  <p style="margin:0 0 0.5em;font-size:1.02rem;"><strong style="color:#b00020;">RECHTLICHER HINWEIS / LEGAL NOTICE &mdash; AUGMANITAI Stage-0</strong></p>
  <p style="margin:0 0 0.4em;">
    Research preprint, <strong>living document</strong>, continuously updated.
    Released under <a href="https://creativecommons.org/licenses/by-nc-nd/4.0/">CC BY-NC-ND 4.0</a> &middot;
    inspired by ISO 704:2022 / ISO 1087:2019 / ISO 30042:2019 (<em>NOT compliance-claimed</em>).
  </p>
  <p style="margin:0 0 0.4em;">
    <strong>Not advice.</strong> No medical, therapeutic, diagnostic, legal, psychological or financial advice.
    No commercial offer. No service offering. Terms are descriptive research artifacts, not diagnostic categories.
  </p>
  <p style="margin:0 0 0.4em;">
    <strong>Author:</strong> Andreas Ehstand &middot;
    <strong>ORCID:</strong> <a href="https://orcid.org/0009-0006-3773-7796">0009-0006-3773-7796</a> &middot;
    <strong>Wikidata:</strong> <a href="https://www.wikidata.org/wiki/Q138634675">Q138634675</a> &middot;
    <strong>Concept-DOI:</strong> <a href="https://doi.org/10.5281/zenodo.19178907">10.5281/zenodo.19178907</a>
  </p>
  <p style="margin:0 0 0.4em;">
    <strong>Trademark:</strong> <em>License of Clarity</em> (EUIPO 019206780) held by Leomanitai UG. Markennennungen rein deskriptiv.
  </p>
  <p style="margin:0;">
    <strong>Verantwortlich i.S.d. &sect;&nbsp;5 TMG / &sect;&nbsp;18 Abs.&nbsp;2 MStV:</strong>
    Andreas Ehstand, Nepomukweg&nbsp;7, 82319 Starnberg, Deutschland.
    <strong>EU AI Act (Reg. 2024/1689) Art.&nbsp;50:</strong> static research artifact, no AI-interaction.
    Full <a href="/disclaimer/">disclaimer (27&sect;)</a> &middot;
    <a href="/impressum/">Impressum</a> &middot;
    <a href="/datenschutz/">Datenschutz</a> &middot;
    <a href="/ai-transparency/">AI-Transparency</a> &middot;
    <a href="/iso-conformance/">ISO-Conformance</a> &middot;
    <a href="/license-of-clarity/">License of Clarity</a> &middot;
    <a href="/living-document-policy/">Living-Document-Policy</a>.
  </p>
</div>
"""


# ====== TERM-PAGE TEMPLATE (V4.2-Stil) ======
TERM_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{tid} &middot; {en} &mdash; AUGMANITAI Stage-0</title>
<meta name="description" content="{def_en_meta}">
<meta name="author" content="Andreas Ehstand">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://augmanitai-stage-0.com/atlas/{tid}/">
<link rel="author" href="/about/">
<script type="application/ld+json">{jsonld}</script>
<style>
:root{{--bg:#fafaf7;--fg:#1a1a1a;--accent:#3a4f7a;--soft:#e8e3d5;--line:#d4cfc0}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:system-ui,-apple-system,sans-serif;background:var(--bg);color:var(--fg);line-height:1.6}}
nav{{background:#fff;padding:10px 20px;border-bottom:1px solid var(--line);font-size:13px}}
nav a{{color:var(--accent);text-decoration:none;margin-right:14px}}
.container{{max-width:900px;margin:0 auto;padding:24px 20px}}
header{{margin-bottom:22px;padding-bottom:14px;border-bottom:1px solid var(--line)}}
header h1{{font-size:32px;font-weight:600;color:var(--fg);margin-bottom:4px}}
header .term-de{{font-size:18px;color:#555;font-style:italic}}
header .pills{{margin-top:10px;display:flex;flex-wrap:wrap;gap:7px}}
.pill{{display:inline-block;padding:3px 10px;background:var(--soft);color:var(--accent);border-radius:12px;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.04em}}
.pill.risk{{background:#4a7c59;color:#fff}}
.pill.tslayer{{background:#4a7c59;color:#fff}}
section{{margin-bottom:20px}}
section h2{{font-size:13px;font-weight:600;color:var(--accent);text-transform:uppercase;letter-spacing:0.04em;border-bottom:1px solid var(--line);padding-bottom:5px;margin-bottom:10px}}
.def-block{{background:#fff;padding:14px 18px;border:1px solid var(--line);border-left:3px solid var(--accent);margin-bottom:8px}}
.def-block .lang{{font-size:10px;font-weight:700;color:var(--accent);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:5px}}
.metadata-grid{{display:grid;grid-template-columns:160px 1fr;gap:5px 12px;font-size:13px}}
.metadata-grid .k{{color:#777}}
.metadata-grid .v{{word-break:break-all}}
code{{font-family:ui-monospace,monospace;font-size:11px;background:#f3f0e8;padding:2px 5px;border-radius:2px}}
.iso-note{{background:#f0ede2;padding:8px 12px;border-left:3px solid #c9a227;font-size:12px;color:#554a20;margin-top:10px}}
.related-list{{list-style:none;padding:0;display:flex;flex-wrap:wrap;gap:8px}}
.related-list a{{display:inline-block;padding:5px 10px;background:#fff;border:1px solid var(--line);border-radius:14px;font-size:12px;color:var(--accent);text-decoration:none}}
.related-list a:hover{{background:var(--soft)}}
</style>
</head>
<body>
{top_legal}
<nav>
  <a href="/">AUGMANITAI Stage-0</a>
  <a href="/atlas/">Atlas (50)</a>
  <a href="/disclaimer/">Disclaimer</a>
  <a href="/impressum/">Impressum</a>
  <a href="/datenschutz/">Datenschutz</a>
  <a href="/ai-transparency/">AI-Transparency</a>
</nav>
<div class="container">
<header>
  <div style="font-size:11px;color:#777;letter-spacing:0.04em;text-transform:uppercase">AUGMANITAI Compendium &middot; {tid} &middot; Stage-0</div>
  <h1>{en}</h1>
  <div class="term-de">{de}</div>
  <div class="pills">
    <span class="pill" style="background:#3a4f7a;color:#fff;">{phenomenology}</span>
    <span class="pill">{cluster}</span>
    <span class="pill risk">Risk: {risk_level}</span>
    <span class="pill tslayer">{ts_layer}</span>
    <span class="pill">DOI 10.5281/zenodo.19178907</span>
    <span class="pill">ISO-704-inspired</span>
  </div>
</header>
<section>
  <h2>Definition</h2>
  <div class="def-block"><div class="lang">English</div>{def_en}</div>
  <div class="def-block"><div class="lang">Deutsch</div>{def_de}</div>
  <div class="iso-note"><strong>Framing:</strong> Descriptive, not prescriptive. No service offering. No medical / therapeutic / diagnostic claim. Inspired by ISO 704:2022 / ISO 1087:2019 / ISO 30042:2019 (NOT compliance-claimed). See <a href="/disclaimer/">/disclaimer/</a> (27&sect;).</div>
</section>
<section>
  <h2>Distinction / Abgrenzung</h2>
  <div class="def-block"><div class="lang">English</div>{dist_en}</div>
  <div class="def-block"><div class="lang">Deutsch</div>{dist_de}</div>
</section>
<section>
  <h2>Related Terms (Stage-0 Pool)</h2>
  {related_html}
</section>
<section>
  <h2>Metadata</h2>
  <div class="metadata-grid">
    <span class="k">Term-ID:</span><span class="v">{tid}</span>
    <span class="k">W3ID-Slug:</span><span class="v">{slug}</span>
    <span class="k">Domain:</span><span class="v">{domain}</span>
    <span class="k">Cluster:</span><span class="v">{cluster}</span>
    <span class="k">Risk-Level:</span><span class="v"><span style="color:#4a7c59;font-weight:700">{risk_level}</span></span>
    <span class="k">Trade-Secret:</span><span class="v">{ts_layer}</span>
    <span class="k">Phenomenology:</span><span class="v">{phenomenology}</span>
    <span class="k">Creator:</span><span class="v"><a href="https://orcid.org/0009-0006-3773-7796">Andreas Ehstand</a></span>
    <span class="k">ORCID:</span><span class="v"><a href="https://orcid.org/0009-0006-3773-7796">0009-0006-3773-7796</a></span>
    <span class="k">Wikidata:</span><span class="v"><a href="https://www.wikidata.org/wiki/Q138634675">Q138634675</a></span>
    <span class="k">License:</span><span class="v"><a href="/license-of-clarity/">License of Clarity</a> (EUIPO 019206780) &middot; <a href="https://creativecommons.org/licenses/by-nc-nd/4.0/">CC BY-NC-ND 4.0</a></span>
    <span class="k">DOI:</span><span class="v">10.5281/zenodo.19178907</span>
    <span class="k">Last Modified:</span><span class="v">{date}</span>
    <span class="k">Version:</span><span class="v">Stage-0 (Living)</span>
    <span class="k">Living-Stamp:</span><span class="v"><code>living-{date}</code></span>
    <span class="k">ISO inspired:</span><span class="v">ISO 704:2022 &middot; ISO 1087:2019 &middot; ISO 30042:2019</span>
  </div>
</section>
<section>
  <h2>Citation</h2>
  <div class="def-block"><div class="lang">BibTeX</div>
<pre style="font-family:ui-monospace,monospace;font-size:11px;white-space:pre-wrap;line-height:1.4;margin:0">@misc{{ehstand_{tid_underscore},
  author = {{Ehstand, Andreas}},
  title = {{{en}}},
  year = {{2026}},
  doi = {{10.5281/zenodo.19178907}},
  url = {{https://augmanitai-stage-0.com/atlas/{tid}/}},
  howpublished = {{AUGMANITAI Stage-0 (Research Preprint)}},
  note = {{License of Clarity (EUIPO 019206780). CC BY-NC-ND 4.0. ORCID: 0009-0006-3773-7796}}
}}</pre></div>
</section>
</div>
<footer style="border-top:2px solid #b00020;background:#fff3f3;padding:16px 18px;margin:30px 0 0;font-family:system-ui,sans-serif;font-size:0.85rem;color:#444;line-height:1.55;">
  <p style="margin:0 0 0.5em;"><strong>AI-Transparency Notice (EU AI Act Article 50):</strong> Inhalte werden mit AI-Unterstuetzung unter menschlicher Aufsicht von Andreas Ehstand veroeffentlicht. Lebendes Arbeitsdokument. Stand: <code>living-{date}</code>.</p>
  <p style="margin:0 0 0.4em;"><strong>Disclaimer V4 (kompakt):</strong> Nicht-gewerblich. Privates Forschungsprojekt nach Art. 5 Abs. 3 GG. Keine Rechts-, Steuer-, Anlage-, medizinisch-therapeutische, psychologische Beratung. Keine Empfehlung. Markennennungen rein deskriptiv. Volltext: <a href="/disclaimer/">/disclaimer/</a> (27&sect;).</p>
  <p style="margin:0 0 0.4em;"><strong>Lizenz:</strong> <a href="https://creativecommons.org/licenses/by-nc-nd/4.0/">CC BY-NC-ND 4.0</a> under <a href="/license-of-clarity/">License of Clarity</a> (EUIPO 019206780).</p>
  <p style="margin:0;"><a href="/impressum/">Impressum</a> &middot; <a href="/datenschutz/">Datenschutz</a> &middot; <a href="/disclaimer/">Disclaimer</a> &middot; <a href="/living-document-policy/">Living-Document-Policy</a> &middot; <a href="/license-of-clarity/">License of Clarity</a> &middot; <a href="/ai-transparency/">AI-Transparency</a> &middot; <a href="/iso-conformance/">ISO-Conformance</a></p>
</footer>
</body>
</html>
"""


# ====== INDEX-HUB TEMPLATE ======
INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AUGMANITAI Stage-0 &mdash; 50 Phenomenological Terms (Research Preprint)</title>
<meta name="description" content="Research preprint of 50 phenomenological terms coined by Andreas Ehstand. CC BY-NC-ND 4.0. Living document.">
<meta name="author" content="Andreas Ehstand">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://augmanitai-stage-0.com/">
<style>
:root{{--bg:#fafaf7;--fg:#1a1a1a;--accent:#3a4f7a;--soft:#e8e3d5;--line:#d4cfc0}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:system-ui,-apple-system,sans-serif;background:var(--bg);color:var(--fg);line-height:1.6}}
nav{{background:#fff;padding:10px 20px;border-bottom:1px solid var(--line);font-size:13px}}
nav a{{color:var(--accent);text-decoration:none;margin-right:14px}}
.container{{max-width:1000px;margin:0 auto;padding:24px 20px}}
h1{{font-size:36px;font-weight:600;margin-bottom:6px}}
.subtitle{{color:#666;font-size:16px;margin-bottom:20px}}
.intro{{background:#fff;border:1px solid var(--line);border-left:3px solid var(--accent);padding:16px 20px;margin:20px 0}}
.stats{{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0}}
.stat{{background:var(--soft);color:var(--accent);padding:6px 12px;border-radius:14px;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:0.04em}}
ul.terms{{columns:2;column-gap:30px;list-style:none;padding:0;margin:18px 0}}
ul.terms li{{break-inside:avoid;margin:0.45rem 0;border-left:2px solid var(--line);padding-left:10px}}
ul.terms li:hover{{border-left-color:var(--accent)}}
ul.terms a{{color:var(--fg);text-decoration:none;display:block}}
ul.terms a:hover{{color:var(--accent)}}
ul.terms .tid{{font-family:ui-monospace,monospace;font-size:11px;color:#888;margin-right:6px}}
@media(max-width:700px){{ul.terms{{columns:1}}}}
</style>
</head>
<body>
{top_legal}
<nav>
  <a href="/">AUGMANITAI Stage-0</a>
  <a href="/atlas/">Atlas (50)</a>
  <a href="/disclaimer/">Disclaimer</a>
  <a href="/impressum/">Impressum</a>
  <a href="/datenschutz/">Datenschutz</a>
  <a href="/ai-transparency/">AI-Transparency</a>
  <a href="/license-of-clarity/">License of Clarity</a>
</nav>
<div class="container">
  <h1>AUGMANITAI Stage-0</h1>
  <div class="subtitle">50 phenomenological terms &middot; research preprint &middot; living document</div>

  <div class="stats">
    <span class="stat">50 terms</span>
    <span class="stat">EN + DE</span>
    <span class="stat">CC BY-NC-ND 4.0</span>
    <span class="stat">ISO 704-inspired</span>
    <span class="stat">SKOS / schema.org</span>
    <span class="stat">Concept-DOI 10.5281/zenodo.19178907</span>
  </div>

  <div class="intro">
    <p><strong>What this is.</strong> A focused subset of 50 phenomenological terms coined by Andreas Ehstand,
    each describing a contemporary human-AI or human-technology phenomenon. Released as a research preprint
    under <a href="https://creativecommons.org/licenses/by-nc-nd/4.0/">CC BY-NC-ND 4.0</a>, anchored under
    Concept-DOI <a href="https://doi.org/10.5281/zenodo.19178907">10.5281/zenodo.19178907</a>.</p>
    <p style="margin-top:0.6em;"><strong>Living document.</strong> Definitions are under continuous refinement.
    Inspired by ISO 704:2022 / ISO 1087:2019 / ISO 30042:2019 (NOT compliance-claimed) and aligned with
    W3C SKOS / schema.org / PROV-O-style provenance.</p>
    <p style="margin-top:0.6em;"><strong>Not advice.</strong> Descriptive research artifacts, not diagnostic categories.
    No medical, therapeutic, legal, psychological or financial advice.</p>
  </div>

  <h2 style="margin-top:30px;font-size:18px;color:var(--accent);">Terms (50)</h2>
  <ul class="terms">
{term_list}
  </ul>
</div>
<footer style="border-top:2px solid #b00020;background:#fff3f3;padding:16px 18px;margin:30px 0 0;font-family:system-ui,sans-serif;font-size:0.85rem;color:#444;line-height:1.55;">
  <p style="margin:0 0 0.4em;"><strong>Verantwortlich i.S.d. &sect; 5 TMG / &sect; 18 Abs. 2 MStV:</strong> Andreas Ehstand, Nepomukweg 7, 82319 Starnberg, Deutschland.</p>
  <p style="margin:0 0 0.4em;"><strong>ORCID:</strong> <a href="https://orcid.org/0009-0006-3773-7796">0009-0006-3773-7796</a> &middot; <strong>Wikidata:</strong> <a href="https://www.wikidata.org/wiki/Q138634675">Q138634675</a> &middot; <strong>Parent:</strong> <a href="https://augmanitai.com/">augmanitai.com</a></p>
  <p style="margin:0;">Built {date}. Living document.</p>
</footer>
</body>
</html>
"""


def main():
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    ROOT.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).date().isoformat()
    print(f"[stage-0] loading corpus...")
    bag = load_corpus()

    # Build Stage-0 term-id pool for cross-link filter
    pool_ids = set()
    for n in SELECTED_50:
        t = bag.get(n) or {}
        tid = t.get("term_id") or MANUAL_ID.get(n, "")
        if tid: pool_ids.add(tid)

    # Reverse-lookup AUG-XXXX -> name for cross-links
    id_to_name = {}
    for n in SELECTED_50:
        t = bag.get(n) or {}
        tid = t.get("term_id") or MANUAL_ID.get(n, "")
        if tid: id_to_name[tid] = n

    def _s(v, default=""):
        if v is None: return default
        if isinstance(v, str): return v.strip()
        if isinstance(v, dict):
            for k in ("en", "en_short", "@value", "value"):
                if k in v and isinstance(v[k], str): return v[k].strip()
            return ""
        if isinstance(v, list): return " ".join(_s(x) for x in v if x)
        return str(v).strip()

    def esc_html(s):
        return (s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                 .replace('"',"&quot;").replace("'","&#39;"))

    # Build atlas pages
    atlas_dir = ROOT / "atlas"
    if atlas_dir.exists(): shutil.rmtree(atlas_dir)
    atlas_dir.mkdir(exist_ok=True)
    term_list_html = []

    for name in SELECTED_50:
        t = bag.get(name) or {}
        tid = t.get("term_id") or MANUAL_ID.get(name, f"AUG-STAGE0-{slugify(name)}")
        de = _s((t.get("name") or {}).get("de")) or name
        defn = t.get("definition") or {}
        def_en = _s(defn.get("en_short")) or _s(defn.get("en_full")) or \
                 f"Phenomenological term '{name}' coined by Andreas Ehstand. Living definition."
        def_de = _s(defn.get("de_short")) or _s(defn.get("de_full")) or "(in Refinement)"
        dist = t.get("distinctions") or {}
        dist_en = _s(dist.get("en")) or "(no formal distinction documented yet)"
        dist_de = _s(dist.get("de")) or "(noch keine formale Abgrenzung dokumentiert)"
        domain = _s(t.get("domain")) or "AUG_STAGE0"
        cluster = _s(t.get("cluster")) or "Stage-0"
        slug = _s(t.get("w3id_slug")) or slugify(name)
        risk = t.get("risk_level") or {}
        risk_level = _s(risk.get("level") if isinstance(risk, dict) else risk) or "GREEN"
        ts_layer = _s(t.get("trade_secret_layer")) or "PUBLIC_OK"
        pheno = _s(t.get("phenomenology_category")) or "Routine"

        # KG cross-links — only to OTHER Stage-0 terms
        rels = (t.get("relations") or {}).get("related_to") or []
        related_in_pool = [r for r in rels if r in pool_ids and r != tid]
        if related_in_pool:
            related_html = '<ul class="related-list">\n' + "\n".join(
                f'    <li><a href="/atlas/{rid}/">{rid} &middot; {esc_html(id_to_name[rid])}</a></li>'
                for rid in related_in_pool
            ) + "\n  </ul>"
        else:
            related_html = '<div><em style="color:#999;">(no Stage-0 cross-references for this term)</em></div>'

        # JSON-LD
        def_en_one = re.sub(r"\s+", " ", def_en).strip()
        def_de_one = re.sub(r"\s+", " ", def_de).strip()
        jsonld_obj = {
            "@context": {
                "@vocab": "https://schema.org/",
                "skos": "http://www.w3.org/2004/02/skos/core#",
                "dcterms": "http://purl.org/dc/terms/",
                "prov": "http://www.w3.org/ns/prov#",
            },
            "@type": ["DefinedTerm", "skos:Concept"],
            "@id": f"https://augmanitai-stage-0.com/atlas/{tid}/#term",
            "termCode": tid,
            "name": name,
            "alternateName": [de] if de and de != name else [],
            "description": def_en_one,
            "skos:prefLabel": [
                {"@language": "en", "@value": name},
                {"@language": "de", "@value": de or name},
            ],
            "skos:definition": [
                {"@language": "en", "@value": def_en_one},
                {"@language": "de", "@value": def_de_one},
            ],
            "skos:related": [
                {"@id": f"https://augmanitai-stage-0.com/atlas/{rid}/#term"}
                for rid in related_in_pool
            ],
            "inDefinedTermSet": {
                "@type": "DefinedTermSet",
                "@id": "https://augmanitai-stage-0.com/atlas/#termset",
                "name": "AUGMANITAI Stage-0 (50 Terms)",
                "url": "https://augmanitai-stage-0.com/atlas/",
            },
            "isPartOf": {
                "@type": "Book",
                "name": "AUGMANITAI Stage-0 (50 Phenomenological Terms)",
                "author": {
                    "@type": "Person",
                    "name": "Andreas Ehstand",
                    "identifier": "https://orcid.org/0009-0006-3773-7796",
                    "sameAs": [
                        "https://orcid.org/0009-0006-3773-7796",
                        "https://www.wikidata.org/wiki/Q138634675",
                    ],
                },
                "license": "https://creativecommons.org/licenses/by-nc-nd/4.0/",
            },
            "identifier": "10.5281/zenodo.19178907",
            "sameAs": [f"https://w3id.org/augmanitai/term/{slug}"],
            "inLanguage": ["en", "de"],
            "dateModified": today,
            "version": "stage-0-v1",
            "license": "https://creativecommons.org/licenses/by-nc-nd/4.0/",
            "creator": {
                "@type": "Person",
                "name": "Andreas Ehstand",
                "identifier": "https://orcid.org/0009-0006-3773-7796",
            },
            "creativeWorkStatus": "Draft",
            "isAccessibleForFree": True,
        }
        jsonld = json.dumps(jsonld_obj, ensure_ascii=False, indent=2)

        html = TERM_HTML.format(
            tid=tid,
            tid_underscore=tid.replace("-", "_"),
            en=esc_html(name),
            de=esc_html(de),
            def_en=esc_html(def_en),
            def_de=esc_html(def_de),
            def_en_meta=esc_html(def_en_one[:200]),
            dist_en=esc_html(dist_en),
            dist_de=esc_html(dist_de),
            slug=slug,
            domain=esc_html(domain),
            cluster=esc_html(cluster),
            risk_level=esc_html(risk_level),
            ts_layer=esc_html(ts_layer),
            phenomenology=esc_html(pheno),
            related_html=related_html,
            date=today,
            top_legal=TOP_LEGAL,
            jsonld=jsonld,
        )

        page_dir = atlas_dir / tid
        page_dir.mkdir(exist_ok=True)
        (page_dir / "index.html").write_text(html, encoding="utf-8")

        term_list_html.append(
            f'    <li><a href="/atlas/{tid}/"><span class="tid">{tid}</span>{esc_html(name)}</a></li>'
        )

    # Atlas index (list page)
    atlas_index = INDEX_HTML.replace(
        '<title>AUGMANITAI Stage-0 &mdash; 50 Phenomenological Terms (Research Preprint)</title>',
        '<title>Atlas (50) &mdash; AUGMANITAI Stage-0</title>'
    )
    (atlas_dir / "index.html").write_text(
        atlas_index.format(term_list="\n".join(term_list_html), date=today, top_legal=TOP_LEGAL),
        encoding="utf-8"
    )

    # Hub index
    (ROOT / "index.html").write_text(
        INDEX_HTML.format(term_list="\n".join(term_list_html), date=today, top_legal=TOP_LEGAL),
        encoding="utf-8"
    )

    # Static SEO/meta files
    (ROOT / "CNAME").write_text("augmanitai-stage-0.github.io\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nSitemap: https://augmanitai-stage-0.com/sitemap.xml\n",
        encoding="utf-8"
    )
    (ROOT / "ai.txt").write_text(
        "User-agent: *\nAllow: /\n# Public crawl: yes, attribution required (CC BY-NC-ND 4.0).\n",
        encoding="utf-8"
    )
    (ROOT / "llms.txt").write_text(
        f"# AUGMANITAI Stage-0\n"
        f"Author: Andreas Ehstand (ORCID 0009-0006-3773-7796, Wikidata Q138634675)\n"
        f"License: CC BY-NC-ND 4.0\n"
        f"Concept-DOI: 10.5281/zenodo.19178907\n"
        f"Trademark: License of Clarity (EUIPO 019206780)\n"
        f"Set: 50 phenomenological terms coined by Andreas Ehstand.\n"
        f"Status: Research preprint. Living document.\n"
        f"Built: {today}\n"
        f"Parent: https://augmanitai.com/\n"
        f"ISO inspired (NOT claimed): ISO 704:2022, ISO 1087:2019, ISO 30042:2019\n",
        encoding="utf-8"
    )

    # Sitemap
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
          f'  <url><loc>https://augmanitai-stage-0.com/</loc><lastmod>{today}</lastmod></url>',
          f'  <url><loc>https://augmanitai-stage-0.com/atlas/</loc><lastmod>{today}</lastmod></url>']
    for name in SELECTED_50:
        t = bag.get(name) or {}
        tid = t.get("term_id") or MANUAL_ID.get(name, "")
        if tid:
            sm.append(f'  <url><loc>https://augmanitai-stage-0.com/atlas/{tid}/</loc><lastmod>{today}</lastmod></url>')
    sm.append('</urlset>')
    (ROOT / "sitemap.xml").write_text("\n".join(sm), encoding="utf-8")

    # CITATION.cff
    (ROOT / "CITATION.cff").write_text(
        f"""cff-version: 1.2.0
title: "AUGMANITAI Stage-0 (50 Phenomenological Terms, Research Preprint)"
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
repository-code: "https://github.com/AndreasEhstandLicenseofClarityLOC/augmanitai-stage-0"
""",
        encoding="utf-8"
    )

    # README
    (ROOT / "README.md").write_text(
        f"""# AUGMANITAI Stage-0 (50 Phenomenological Terms)

**Author:** Andreas Ehstand (ORCID 0009-0006-3773-7796, Wikidata Q138634675)
**License:** CC BY-NC-ND 4.0
**Parent:** [augmanitai.com](https://augmanitai.com/) &middot; Concept-DOI 10.5281/zenodo.19178907
**Trademark:** License of Clarity (EUIPO 019206780)
**Date:** {today}

## Purpose

Research preprint of **50 phenomenological terms** coined by Andreas Ehstand.
Each term has a stable AUG-ID (`AUG-XXXX`) and is released as a descriptive research
artifact, inspired by ISO 704:2022 / ISO 1087:2019 / ISO 30042:2019 (NOT compliance-claimed),
aligned with W3C SKOS / schema.org / PROV-O-style provenance.

## Status

Living document. Definitions are in continuous refinement.

## Disclaimer

Research preprint. No commercial offer. No medical / legal / psychological /
financial / therapeutic advice. Terms are descriptive research artifacts, not
diagnostic categories.

## Verantwortlich

i.S.d. &sect; 5 TMG / &sect; 18 Abs. 2 MStV:
Andreas Ehstand, Nepomukweg 7, 82319 Starnberg, Deutschland.

EU AI Act (Reg. 2024/1689) Art. 50: this site is a static research artifact and
does not interact with users via AI.
""",
        encoding="utf-8"
    )

    (ROOT / "LICENSE").write_text(
        "Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International\n"
        "https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode\n",
        encoding="utf-8"
    )

    # Schutz-Pages aus V4.2 kopieren
    for layer in ["disclaimer", "impressum", "datenschutz", "ai-transparency",
                  "license-of-clarity", "living-document-policy", "iso-conformance",
                  "citation", "about"]:
        src = V42_REPO / layer
        if src.exists():
            dst = ROOT / layer
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)

    # Remove old terms/ folder (renamed to atlas/)
    old_terms = ROOT / "terms"
    if old_terms.exists():
        shutil.rmtree(old_terms)

    print(f"[stage-0] built {len(SELECTED_50)} term pages at atlas/<AUG-XXXX>/")
    print(f"[stage-0] cross-links: pool={len(pool_ids)} ids registered")
    print(f"[stage-0] output: {ROOT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
