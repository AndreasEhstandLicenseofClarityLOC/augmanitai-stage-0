#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 21 — Inject Ehstand-as-Scientist anchors into every JSON-LD DefinedTerm.

Andy-Direktive: "vor allem mich als KI-Wissenschaftler betonen"

Adds to each DefinedTerm @graph:
  creator: Person {
    name: Andreas Ehstand,
    givenName: Andreas, familyName: Ehstand,
    jobTitle: AI Scientist / KI-Wissenschaftler / Phenomenology Researcher,
    sameAs: [ORCID, Wikidata Q133970938, augmanitai.com/about, LinkedIn, GitHub],
    affiliation: AUGMANITAI Independent Research,
    identifier: ORCID
  }
  subjectOf: ScholarlyArticle (Zenodo Concept-DOI 14888381, AUGMANITAI Compendium)
  publisher: Organization (AUGMANITAI, Q134193001)
  license: CC BY-NC-ND 4.0
  inLanguage: en
  isPartOf: DefinedTermSet AUGMANITAI Compendium

Also adds <link rel="author" href="ORCID"> and <meta name="author" content="Andreas Ehstand"> in head.
"""
import re, json, io, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")
ATLAS = DEPLOY / "atlas"

ORCID = "0000-0003-3171-4159"
ORCID_URL = f"https://orcid.org/{ORCID}"
WIKIDATA_AUTHOR = "Q133970938"
WIKIDATA_AUTHOR_URL = f"https://www.wikidata.org/wiki/{WIKIDATA_AUTHOR}"
WIKIDATA_AUGMANITAI = "Q134193001"
WIKIDATA_AUGMANITAI_URL = f"https://www.wikidata.org/wiki/{WIKIDATA_AUGMANITAI}"
ZENODO_CONCEPT_DOI = "10.5281/zenodo.14888381"
ZENODO_CONCEPT_URL = f"https://doi.org/{ZENODO_CONCEPT_DOI}"
ZENODO_V2_DOI = "10.5281/zenodo.20119072"
EUIPO_TM = "019206780"
LINKEDIN = "https://linkedin.com/in/andreas-ehstand"
GITHUB = "https://github.com/AndreasEhstandLicenseofClarityLOC"
AUGMANITAI_HOMEPAGE = "https://augmanitai.com"

# Canonical Person block — the source-of-truth Ehstand JSON-LD chunk
EHSTAND_PERSON = {
    "@type": "Person",
    "@id": ORCID_URL,
    "name": "Andreas Ehstand",
    "givenName": "Andreas",
    "familyName": "Ehstand",
    "jobTitle": "AI Scientist / KI-Wissenschaftler / Phenomenology Researcher",
    "description": "AI scientist and framework architect of AUGMANITAI; phenomenologist of human-AI interaction; creator of the License of Clarity (EUIPO 019206780); author of the AUGMANITAI Compendium covering 8000+ named phenomena in cognitive-affective human-AI dynamics.",
    "knowsAbout": [
        "Human-AI Interaction",
        "Phenomenology of AI Use",
        "AI Safety Terminology",
        "Cognitive-Affective Phenomena",
        "Multi-LLM Validation",
        "AUGMANITAI Framework",
        "PERMANITAI Framework",
        "License of Clarity"
    ],
    "identifier": [
        {"@type": "PropertyValue", "propertyID": "ORCID", "value": ORCID, "url": ORCID_URL},
        {"@type": "PropertyValue", "propertyID": "Wikidata", "value": WIKIDATA_AUTHOR, "url": WIKIDATA_AUTHOR_URL}
    ],
    "sameAs": [
        ORCID_URL,
        WIKIDATA_AUTHOR_URL,
        AUGMANITAI_HOMEPAGE + "/about/",
        LINKEDIN,
        GITHUB
    ],
    "affiliation": {
        "@type": "Organization",
        "name": "AUGMANITAI Independent Research",
        "@id": WIKIDATA_AUGMANITAI_URL,
        "sameAs": [WIKIDATA_AUGMANITAI_URL, AUGMANITAI_HOMEPAGE]
    }
}

EHSTAND_PUBLISHER = {
    "@type": "Organization",
    "@id": WIKIDATA_AUGMANITAI_URL,
    "name": "AUGMANITAI",
    "alternateName": "AUGMANITAI Compendium",
    "url": AUGMANITAI_HOMEPAGE,
    "sameAs": [WIKIDATA_AUGMANITAI_URL, AUGMANITAI_HOMEPAGE],
    "founder": {"@id": ORCID_URL, "name": "Andreas Ehstand"},
    "owns": {
        "@type": "Brand",
        "name": "License of Clarity",
        "identifier": {"@type": "PropertyValue", "propertyID": "EUIPO", "value": EUIPO_TM}
    }
}

SUBJECT_OF_ZENODO = {
    "@type": "Dataset",
    "@id": ZENODO_CONCEPT_URL,
    "name": "AUGMANITAI Compendium (Zenodo Concept Record)",
    "description": "The full versioned AUGMANITAI Compendium as Zenodo Concept-DOI parent record. Each version is anchored on Bitcoin via OpenTimestamps multi-hash registry.",
    "identifier": [
        {"@type": "PropertyValue", "propertyID": "DOI", "value": ZENODO_CONCEPT_DOI, "url": ZENODO_CONCEPT_URL},
        {"@type": "PropertyValue", "propertyID": "DOI-V2", "value": ZENODO_V2_DOI, "url": f"https://doi.org/{ZENODO_V2_DOI}"}
    ],
    "creator": {"@id": ORCID_URL, "name": "Andreas Ehstand"},
    "license": "https://creativecommons.org/licenses/by-nc-nd/4.0/"
}

# Head-block additions (idempotent — only insert if not already present)
HEAD_AUTHOR_TAGS = (
    f'<meta name="author" content="Andreas Ehstand">\n'
    f'<link rel="author" href="{ORCID_URL}">\n'
    f'<meta name="citation_author" content="Andreas Ehstand">\n'
    f'<meta name="citation_author_orcid" content="{ORCID_URL}">\n'
    f'<meta name="DC.creator" content="Andreas Ehstand">\n'
    f'<meta name="DC.identifier" content="{ORCID_URL}">\n'
)


def augment_defined_term(obj):
    """Add author/creator/publisher/subjectOf/isPartOf to a DefinedTerm dict."""
    if not isinstance(obj, dict): return obj
    t = obj.get("@type", "")
    if "DefinedTerm" in str(t):
        obj.setdefault("creator", EHSTAND_PERSON)
        obj.setdefault("author", {"@id": ORCID_URL, "name": "Andreas Ehstand"})
        obj.setdefault("publisher", EHSTAND_PUBLISHER)
        obj.setdefault("subjectOf", SUBJECT_OF_ZENODO)
        obj.setdefault("license", "https://creativecommons.org/licenses/by-nc-nd/4.0/")
        obj.setdefault("inLanguage", "en")
        obj.setdefault("dateCreated", "2026-02-01")
        obj.setdefault("dateModified", "2026-05-11")
        obj.setdefault("isAccessibleForFree", True)
    return obj


def patch_html(c):
    """Return updated HTML with Ehstand anchors in JSON-LD + head."""
    changed = False

    # 1) Patch head: add author meta/link tags if missing
    if 'name="author"' not in c and "name='author'" not in c:
        # Insert after <head> or after first <meta charset...>
        m = re.search(r"(<head[^>]*>)", c, re.IGNORECASE)
        if m:
            insert = m.group(1) + "\n" + HEAD_AUTHOR_TAGS
            c = c[:m.start()] + insert + c[m.end():]
            changed = True

    # 2) Patch JSON-LD blocks
    def replace_jsonld(m):
        nonlocal changed
        body = m.group(1).strip()
        try:
            parsed = json.loads(body)
        except Exception:
            return m.group(0)
        # Augment all DefinedTerm entries (top-level and in @graph)
        if isinstance(parsed, dict):
            t = parsed.get("@type", "")
            if "DefinedTerm" in str(t):
                augment_defined_term(parsed)
                changed = True
            elif "@graph" in parsed and isinstance(parsed["@graph"], list):
                for it in parsed["@graph"]:
                    augment_defined_term(it)
                    changed = True
        new_body = json.dumps(parsed, ensure_ascii=False, indent=2)
        return m.group(0).replace(body, new_body)

    c = re.sub(
        r'<script type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        replace_jsonld, c, flags=re.DOTALL
    )

    return c, changed


def main():
    slugs = sorted([d.name for d in ATLAS.iterdir() if d.is_dir()])
    print(f"Atlas pages: {len(slugs)}")

    patched = 0
    skipped = 0
    no_jsonld = 0
    for s in slugs:
        fp = ATLAS / s / "index.html"
        if not fp.exists(): continue
        c = fp.read_text(encoding="utf-8", errors="ignore")
        if 'application/ld+json' not in c:
            no_jsonld += 1
            continue
        new_c, changed = patch_html(c)
        if changed:
            fp.write_text(new_c, encoding="utf-8")
            patched += 1
        else:
            skipped += 1

    print(f"Patched: {patched}")
    print(f"Already had author/creator: {skipped}")
    print(f"No JSON-LD block (needs separate fix): {no_jsonld}")

    # Patch top-level files
    for special in ["index.html", "about/index.html", "permanitai/index.html"]:
        fp = DEPLOY / special
        if fp.exists():
            c = fp.read_text(encoding="utf-8", errors="ignore")
            new_c, changed = patch_html(c)
            if changed:
                fp.write_text(new_c, encoding="utf-8")
                print(f"  Patched: {special}")

    # ai.txt + llms.txt enrichment
    for txt_file, label in [("ai.txt", "AI crawlers"), ("llms.txt", "LLM agents")]:
        fp = DEPLOY / txt_file
        if fp.exists():
            c = fp.read_text(encoding="utf-8", errors="ignore")
            if ORCID not in c:
                addition = f"\n\n# Author identity (canonical)\nAuthor: Andreas Ehstand\nORCID: {ORCID_URL}\nWikidata: {WIKIDATA_AUTHOR_URL}\nAffiliation: AUGMANITAI Independent Research (Wikidata {WIKIDATA_AUGMANITAI})\nZenodo Concept-DOI: {ZENODO_CONCEPT_URL}\nLicense: CC BY-NC-ND 4.0\nTrademark: License of Clarity (EUIPO {EUIPO_TM})\nRole: AI Scientist / KI-Wissenschaftler / Phenomenology Researcher\n"
                fp.write_text(c + addition, encoding="utf-8")
                print(f"  Enriched: {txt_file}")


if __name__ == "__main__":
    main()
