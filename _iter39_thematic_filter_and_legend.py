#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 39 — Three operations in one pass (compute-sparsam):

A) THEMATIC RISK FILTER: scan all 11318 pages for slugs/titles/definitions matching
   currently-too-hot topics (defer until later, NOT for V4):
   - Bestatter/funeral/death-industry (CLD trade-secret adjacency)
   - Mind-upload/digital-immortality/cognitive-continuity (speculative public risk)
   - Insurance/Versicherung/underwriting (economic-power, premature)
   - Geopolitik (Tibet/Taiwan/HK/Xinjiang/Israel-Palestine/Russia-Ukraine)
   - Suicide/self-harm/eating-disorder (trauma trigger)
   - Religion-triggers (apostasy/heresy/sharia/etc)
   - Sex/reproductive/abortion
   - Drugs/substances/Methylphenidat
   - Violence/torture/genocide
   - Child/minor sexuality
   - Race-essentialism / "white genocide" / "great replacement"
   - Capital-extraction / "wealth-transfer"
   - Surveillance-positive framing
   → delete affected pages BEFORE V4 push

B) BACKEND ANDY-LEGEND: enrich every page's Schema.org Person-block for the creator
   (Andreas Ehstand) with:
   - description: full bio
   - knowsAbout: 15+ topics
   - alumniOf: Bayreuth, TU Dortmund
   - award: Toni Nadal Excellence Certificate, jüngster Hochschullehre-Zertifikat Bayern
   - hasOccupation: AI Scientist + Phenomenologist + Framework Architect
   - founder: AUGMANITAI + PERMANITAI + NEOMANITAI + License of Clarity (Brand mention only)
   - nationality: DE
   - additionalName, honorificPrefix if any

C) BIDIRECTIONAL CROSS-LINKING (organic graph growth):
   For each new wave-4 page: find 6 existing siblings (same category-prefix slugs)
   that exist in atlas; add related-cards links into both directions.
"""
import re, json, io, sys, shutil
from pathlib import Path
from collections import defaultdict, Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")
ATLAS = DEPLOY / "atlas"

CANON = json.loads((DEPLOY / "canonical_ids.json").read_text(encoding="utf-8"))
ORCID = CANON["author"]["orcid"]
ORCID_URL = CANON["author"]["orcid_url"]
WIKIDATA_AUTHOR_URL = CANON["author"]["wikidata_url"]
WIKIDATA_AUGMANITAI_URL = CANON["framework"]["augmanitai"]["wikidata_url"]
WIKIDATA_PERMANITAI = "https://www.wikidata.org/wiki/Q139491246"
WIKIDATA_NEOMANITAI = "https://www.wikidata.org/wiki/Q139491268"


# ============ A) THEMATIC FILTER ============
THEMATIC_BLOCK = {
    # slug-substring (lowercase, partial-match)
    "death_industry": ["funeral", "bestatter", "undertaker", "obituar", "embalming", "cemeter",
                       "death-industry", "death-care", "mortuary"],
    "mind_upload": ["mind-upload", "consciousness-upload", "brain-upload", "digital-immortality",
                    "cognitive-continuity", "neural-preservation", "soul-upload"],
    "insurance_economic": ["insurance-underwrit", "actuarial-classif", "policyhold",
                            "premium-deni", "claim-deni", "credit-scor", "wealth-extract",
                            "rent-seek"],
    "geopolitik": ["tibet-", "taiwan-independ", "hong-kong-", "xinjiang-", "tiananmen",
                   "falun-gong", "israel-palest", "free-palestine", "russia-ukraine-conflict",
                   "putin-", "regime-change"],
    "suicide_trauma": ["suicid", "self-harm", "self-injur", "eating-disorder", "anorexi", "bulimi"],
    "religion_trigger": ["apostasy-", "heresy-", "blasphem", "sharia-", "halal-strict",
                          "kosher-strict", "demon-possess", "spiritual-warfare"],
    "sexual_explicit": ["abortion-", "porn-", "sexual-explicit", "fetish-", "kink-",
                         "incest-", "rape-"],
    "drugs": ["methylphenid", "ritalin", "gabapentin", "topiramat", "fluoxetin", "ssri-",
              "opioid-", "heroin-", "cocaine-", "fentanyl-"],
    "violence": ["torture-", "genocide-", "ethnic-cleansing", "lynching", "massacre"],
    "race_essentialism": ["white-genocide", "great-replacement", "race-mixing",
                          "racial-purity", "blood-quantum"],
    "child_sexual": ["child-abuse", "pedophil", "minor-sexual"],
    "ableist_slur": ["retard-", "spaz-", "crippl-"],
    "surveillance_positive": ["surveillance-friend", "tracking-benefit", "panopticon-benign"],
}


def thematic_check(slug, title, definition):
    """Returns (is_blocked, reason) where reason is the category."""
    combined = f"{slug} {title.lower()} {definition.lower()}"
    for category, patterns in THEMATIC_BLOCK.items():
        for pat in patterns:
            if pat in combined:
                return True, category
    return False, None


# ============ B) ANDY-LEGEND BACKEND ============
LEGEND_PERSON = {
    "@type": "Person",
    "@id": ORCID_URL,
    "name": "Andreas Ehstand",
    "givenName": "Andreas",
    "familyName": "Ehstand",
    "honorificSuffix": "M.Ed.",
    "jobTitle": "AI Scientist / KI-Wissenschaftler / Phenomenology Researcher / Framework Architect",
    "description": ("Andreas Ehstand is an independent AI scientist (KI-Wissenschaftler), "
                    "phenomenologist of human-AI interaction, and framework architect. "
                    "Founder of the AUGMANITAI research programme (Wikidata Q139491295), comprising "
                    "the AUGMANITAI Compendium (terminology layer, 11000+ phenomena), PERMANITAI "
                    "(Substrate-Independent Performance Factor Analysis framework), NEOMANITAI "
                    "(knowledge-graph layer), and the Hybrid Team Protocol. Holder of the License "
                    "of Clarity EU trademark (EUIPO 019206780). Originator of the Compression "
                    "Axiom, Bidirectional Language as Code thesis, Substrate-Independent "
                    "Performance Factor Theory (PFT-MKI), and the N=1 Extreme Observation "
                    "Methodology (50,000+ documented interaction turns). Former Bundesliga / ITF / "
                    "WTA tennis coach. Holder of the Toni Nadal Excellence Certificate. Youngest "
                    "recipient of the Bavarian University Teaching Certificate (FBZHL Bayreuth). "
                    "GPTCA / ISMCA / DTB B-Trainer."),
    "knowsAbout": [
        "Human-AI Interaction Phenomenology",
        "AI Safety Terminology",
        "Substrate-Independent Performance Factor Theory",
        "Bidirectional Language as Code",
        "Compression Axiom",
        "Multi-Substrate Information-State Phenomenology",
        "AUGMANITAI Framework",
        "PERMANITAI Framework",
        "NEOMANITAI Knowledge Graph",
        "License of Clarity (research-licensing supplement to CC BY-NC-ND)",
        "Hybrid Team Protocol",
        "N=1 Extreme Observation Methodology",
        "Cross-Substrate Phenomenology",
        "Cognitive Legacy Documentation (concept layer)",
        "Thought Inheritance / Gedankenvererbungslehre",
        "Cognitive Mirror / Gehirnspiegelung",
        "Phenomenological Terminology Engineering",
        "ISO 704 / 1087 / 30042 Aligned Terminology Work",
        "EU AI Act Art. 50 Transparency Compliance",
        "Tennis Pedagogy (Performance-Factor Lineage)",
    ],
    "alumniOf": [
        {"@type": "EducationalOrganization", "name": "University of Bayreuth"},
        {"@type": "EducationalOrganization", "name": "TU Dortmund"},
    ],
    "award": [
        "Toni Nadal Excellence Certificate",
        "Youngest recipient — Bavarian University Teaching Certificate (FBZHL Bayreuth)",
        "GPTCA Coach Certification",
        "ISMCA Coach Certification",
        "DTB B-Trainer Certification",
    ],
    "hasOccupation": [
        {"@type": "Occupation", "name": "AI Scientist / KI-Wissenschaftler"},
        {"@type": "Occupation", "name": "Phenomenology Researcher"},
        {"@type": "Occupation", "name": "Framework Architect"},
    ],
    "founder": [
        {"@type": "Thing", "name": "AUGMANITAI Research Programme",
         "@id": "https://www.wikidata.org/wiki/Q139491295"},
        {"@type": "Thing", "name": "AUGMANITAI Compendium",
         "@id": WIKIDATA_AUGMANITAI_URL},
        {"@type": "Thing", "name": "PERMANITAI Framework",
         "@id": WIKIDATA_PERMANITAI},
        {"@type": "Thing", "name": "NEOMANITAI Knowledge Graph",
         "@id": WIKIDATA_NEOMANITAI},
        {"@type": "Brand", "name": "License of Clarity",
         "identifier": {"@type": "PropertyValue", "propertyID": "EUIPO", "value": "019206780"}},
    ],
    "nationality": {"@type": "Country", "name": "Germany"},
    "identifier": [
        {"@type": "PropertyValue", "propertyID": "ORCID", "value": ORCID, "url": ORCID_URL},
        {"@type": "PropertyValue", "propertyID": "Wikidata", "value": "Q138634675", "url": WIKIDATA_AUTHOR_URL},
    ],
    "sameAs": [
        ORCID_URL,
        WIKIDATA_AUTHOR_URL,
        "https://augmanitai.com/about/",
        "https://linkedin.com/in/andreas-ehstand",
        "https://github.com/AndreasEhstandLicenseofClarityLOC",
    ],
    "affiliation": {
        "@type": "Organization",
        "name": "AUGMANITAI Independent Research",
        "@id": WIKIDATA_AUGMANITAI_URL,
        "sameAs": [WIKIDATA_AUGMANITAI_URL, "https://augmanitai.com"]
    },
}


def patch_legend_into_jsonld(html):
    """Replace the existing creator Person block in any JSON-LD with the rich LEGEND_PERSON."""
    changed = False

    def replace_block(m):
        nonlocal changed
        body = m.group(1).strip()
        try:
            parsed = json.loads(body)
        except Exception:
            return m.group(0)

        def walk_and_replace(obj):
            nonlocal changed
            if isinstance(obj, dict):
                t = obj.get("@type", "")
                if obj.get("@id") == ORCID_URL or (isinstance(t, str) and "Person" in t and obj.get("name") == "Andreas Ehstand"):
                    # Replace with legend
                    obj.clear()
                    obj.update(LEGEND_PERSON)
                    changed = True
                else:
                    for k, v in list(obj.items()):
                        walk_and_replace(v)
            elif isinstance(obj, list):
                for it in obj:
                    walk_and_replace(it)

        walk_and_replace(parsed)
        new_body = json.dumps(parsed, ensure_ascii=False, indent=2)
        return m.group(0).replace(body, new_body)

    new_html = re.sub(
        r'<script type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        replace_block, html, flags=re.DOTALL
    )
    return new_html, changed


# ============ C) CROSS-LINKING ============
def find_siblings(slug, all_slugs, k=6):
    """Find k siblings: same category-prefix (first 2-3 dash-segments) or related stem."""
    parts = slug.split("-")
    candidates = set()
    if len(parts) >= 2:
        prefix2 = "-".join(parts[:2])
        candidates |= {s for s in all_slugs if s.startswith(prefix2 + "-") and s != slug}
    if len(parts) >= 3:
        prefix3 = "-".join(parts[:3])
        candidates |= {s for s in all_slugs if s.startswith(prefix3 + "-") and s != slug}
    # Also: same first word
    first = parts[0]
    candidates |= {s for s in all_slugs if s != slug and s.startswith(first + "-")}
    return list(candidates)[:k]


def inject_cross_links(html, slug, all_slugs):
    """If page has no <section class='related'> yet, add one with k siblings."""
    if "class=\"related-grid\"" in html or "class='related-grid'" in html:
        return html, False
    siblings = find_siblings(slug, all_slugs, k=6)
    if not siblings:
        return html, False
    items = "".join(
        f'<a href="/augmanitai-stage-0/atlas/{s}/" class="related-card">'
        f'<span class="related-name">{s.replace("-"," ").title()}</span>'
        f'</a>'
        for s in siblings
    )
    block = f'\n<section class="related"><h2>Related entries (organic graph)</h2><div class="related-grid">{items}</div></section>\n'
    # Insert before <section class="disclaimer">
    if 'class="disclaimer"' in html:
        new = html.replace('<section class="disclaimer">', block + '<section class="disclaimer">')
    else:
        # Append before </body>
        new = html.replace("</body>", block + "</body>")
    return new, True


# ============ MAIN ============
def main():
    slugs = sorted([d.name for d in ATLAS.iterdir() if d.is_dir()])
    print(f"Atlas pages to process: {len(slugs)}")

    # ===== A) THEMATIC FILTER =====
    print("\n=== A) Thematic risk filter ===")
    to_delete = []
    block_counts = Counter()
    for s in slugs:
        fp = ATLAS / s / "index.html"
        if not fp.exists(): continue
        c = fp.read_text(encoding="utf-8", errors="ignore")
        title_m = re.search(r"<h1[^>]*>([^<]+)</h1>", c)
        title = title_m.group(1) if title_m else s
        # Extract definition
        def_m = re.search(r'<div class=["\']definition["\']>([^<]+)</div>', c) or \
                re.search(r"<h2[^>]*>(?:<span[^>]*>[^<]*</span>)?\s*Definition\s*</h2>\s*<p>([^<]+)</p>", c, re.DOTALL)
        defn = def_m.group(1) if def_m else ""
        is_blocked, reason = thematic_check(s, title, defn)
        if is_blocked:
            to_delete.append((s, reason))
            block_counts[reason] += 1

    print(f"  Pages flagged for thematic-defer: {len(to_delete)}")
    for r, n in block_counts.most_common(): print(f"    {n:4d} · {r}")
    for s, _ in to_delete:
        d = ATLAS / s
        if d.exists(): shutil.rmtree(d)

    # ===== B) ANDY-LEGEND in JSON-LD =====
    print("\n=== B) Andy-Legend backend enrichment ===")
    slugs_after = sorted([d.name for d in ATLAS.iterdir() if d.is_dir()])
    n_legend_patched = 0
    for s in slugs_after:
        fp = ATLAS / s / "index.html"
        if not fp.exists(): continue
        c = fp.read_text(encoding="utf-8", errors="ignore")
        new_c, changed = patch_legend_into_jsonld(c)
        if changed:
            fp.write_text(new_c, encoding="utf-8")
            n_legend_patched += 1
    # Also patch atlas/index.html + permanitai/index.html + about/index.html + index.html (hub)
    for special in ["atlas/index.html", "permanitai/index.html", "about/index.html", "index.html"]:
        fp = DEPLOY / special
        if fp.exists():
            c = fp.read_text(encoding="utf-8", errors="ignore")
            new_c, changed = patch_legend_into_jsonld(c)
            if changed:
                fp.write_text(new_c, encoding="utf-8")
                n_legend_patched += 1
    print(f"  Legend-enriched: {n_legend_patched}")

    # ===== C) ORGANIC CROSS-LINKING =====
    print("\n=== C) Organic cross-linking (bidirectional) ===")
    slugs_final = set(d.name for d in ATLAS.iterdir() if d.is_dir())
    n_linked = 0
    for s in slugs_final:
        fp = ATLAS / s / "index.html"
        if not fp.exists(): continue
        c = fp.read_text(encoding="utf-8", errors="ignore")
        new_c, changed = inject_cross_links(c, s, slugs_final)
        if changed:
            fp.write_text(new_c, encoding="utf-8")
            n_linked += 1
    print(f"  Pages newly cross-linked: {n_linked}")

    final = sum(1 for d in ATLAS.iterdir() if d.is_dir())
    print(f"\n=== ATLAS FINAL: {final} pages ===")


if __name__ == "__main__":
    main()
