#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 22 — Patch 80 cluster-hub pages with full JSON-LD CollectionPage + Ehstand-author.

Cluster pages (absence, adapt, bridge, choice, clarity, witness, ...) are thematic
hubs without JSON-LD. Inject:
- @type CollectionPage with author/creator/publisher
- Backlink list to specific term pages matching the cluster prefix
- Schema.org breadcrumb
"""
import re, json, io, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")
ATLAS = DEPLOY / "atlas"
BASE_URL = "https://andreasehstandlicenseofclarityloc.github.io/augmanitai-stage-0"

ORCID_URL = "https://orcid.org/0000-0003-3171-4159"
WIKIDATA_AUTHOR_URL = "https://www.wikidata.org/wiki/Q133970938"
WIKIDATA_AUGMANITAI_URL = "https://www.wikidata.org/wiki/Q134193001"
ZENODO_CONCEPT_URL = "https://doi.org/10.5281/zenodo.14888381"

EHSTAND_PERSON_MIN = {
    "@type": "Person",
    "@id": ORCID_URL,
    "name": "Andreas Ehstand",
    "jobTitle": "AI Scientist / KI-Wissenschaftler / Phenomenology Researcher",
    "sameAs": [ORCID_URL, WIKIDATA_AUTHOR_URL, "https://augmanitai.com/about/"]
}


def main():
    slugs_all = sorted([d.name for d in ATLAS.iterdir() if d.is_dir()])
    existing = set(slugs_all)
    cluster_pages = []
    for s in slugs_all:
        fp = ATLAS / s / "index.html"
        if not fp.exists(): continue
        c = fp.read_text(encoding="utf-8", errors="ignore")
        if "application/ld+json" not in c:
            cluster_pages.append(s)
    print(f"Cluster pages without JSON-LD: {len(cluster_pages)}")

    patched = 0
    for cluster in cluster_pages:
        fp = ATLAS / cluster / "index.html"
        c = fp.read_text(encoding="utf-8", errors="ignore")

        # Find related term pages with same prefix
        related = [s for s in existing if s != cluster and (s.startswith(cluster + "-") or "-" + cluster + "-" in s)]
        related = related[:50]  # cap

        title_m = re.search(r"<title>([^<]+)</title>", c)
        title = title_m.group(1) if title_m else cluster.upper()
        desc_m = re.search(r"<meta name=['\"]description['\"] content=['\"]([^'\"]+)['\"]", c)
        description = desc_m.group(1) if desc_m else f"{cluster.upper()} cluster within AUGMANITAI Compendium"

        # Build CollectionPage JSON-LD
        collection = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "@id": f"{BASE_URL}/atlas/{cluster}/",
            "name": title,
            "description": description,
            "url": f"{BASE_URL}/atlas/{cluster}/",
            "inLanguage": "en",
            "license": "https://creativecommons.org/licenses/by-nc-nd/4.0/",
            "dateCreated": "2026-02-01",
            "dateModified": "2026-05-11",
            "creator": EHSTAND_PERSON_MIN,
            "author": {"@id": ORCID_URL, "name": "Andreas Ehstand"},
            "publisher": {
                "@type": "Organization",
                "@id": WIKIDATA_AUGMANITAI_URL,
                "name": "AUGMANITAI",
                "founder": {"@id": ORCID_URL, "name": "Andreas Ehstand"}
            },
            "subjectOf": {
                "@type": "Dataset",
                "@id": ZENODO_CONCEPT_URL,
                "name": "AUGMANITAI Compendium (Zenodo Concept-DOI)",
                "creator": {"@id": ORCID_URL, "name": "Andreas Ehstand"}
            },
            "isPartOf": {
                "@type": "DefinedTermSet",
                "name": "AUGMANITAI Compendium",
                "url": "https://augmanitai.com"
            },
            "hasPart": [
                {
                    "@type": "DefinedTerm",
                    "name": rel.replace("-", " ").title(),
                    "url": f"{BASE_URL}/atlas/{rel}/",
                    "creator": {"@id": ORCID_URL, "name": "Andreas Ehstand"}
                }
                for rel in related
            ]
        }

        breadcrumb = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "AUGMANITAI Compendium", "item": f"{BASE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": "Atlas", "item": f"{BASE_URL}/atlas/"},
                {"@type": "ListItem", "position": 3, "name": title, "item": f"{BASE_URL}/atlas/{cluster}/"}
            ]
        }

        # Inject before </head>
        injection = (
            f'<script type="application/ld+json">\n{json.dumps(collection, ensure_ascii=False, indent=2)}\n</script>\n'
            f'<script type="application/ld+json">\n{json.dumps(breadcrumb, ensure_ascii=False, indent=2)}\n</script>\n'
        )

        # Also add author meta if missing
        head_tags = ""
        if 'name="author"' not in c and "name='author'" not in c:
            head_tags = (
                f'<meta name="author" content="Andreas Ehstand">\n'
                f'<link rel="author" href="{ORCID_URL}">\n'
                f'<meta name="citation_author" content="Andreas Ehstand">\n'
                f'<meta name="citation_author_orcid" content="{ORCID_URL}">\n'
            )

        if "</head>" in c:
            c = c.replace("</head>", head_tags + injection + "</head>")
        else:
            # fallback: prepend at body start
            c = c.replace("<body>", "<body>\n" + injection)
        fp.write_text(c, encoding="utf-8")
        patched += 1

    print(f"Patched cluster pages: {patched}")


if __name__ == "__main__":
    main()
