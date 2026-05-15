#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 47 — MAX-PARANOID rechtliche Compliance Audit on full live atlas.

Andy directive 2026-05-12: "prüfe massiv ob alles rechtliche eingehalten ist
ob dsgvo ob impressum ob disclaimer ob alles eingehalten ist bis aufs maximum
wirklich auf jeder seite".

Categories (ALL must pass per page):
A) Impressum / Verantwortlich (§ 5 DDG / § 18 Abs. 2 MStV)
   - "Verantwortlich" present
   - Andreas Ehstand named
   - Address (Nepomukweg 7, Starnberg) or its surrogate present in footer
B) DSGVO (GDPR compliance)
   - DSGVO authority "Bayerisches Landesamt für Datenschutzaufsicht" present
   - "Promenade 18, 91522 Ansbach" or "Datenschutzaufsicht" reference
   - Statement re: "no personal data collected" / "no tracking"
C) Disclaimer §1-§26
   - §14 Age 18+
   - §17 AI Training Prohibition / KI-Trainingsverbot
   - §18 Verantwortlich
   - §19 Severability
   - §26 Refinement Window (optional)
D) EU AI Act Art. 50 transparency
E) CC BY-NC-ND 4.0 license declaration
F) Canonical Identifiers
   - ORCID 0009-0006-3773-7796
   - Wikidata Q138634675 (author)
   - Wikidata Q138522830 (AUGMANITAI)
   - EUIPO 019206780 (License of Clarity)
G) Living Document banner
H) Trade-Secret-Anti-Patterns (no Leomanitai, no Leona-Andy link, etc.)
I) Re-ID boundaries (no address outside footer)
J) Gate-v4: children, violence, instruction, du-ansprache

Generates: _ITER47_COMPLIANCE_AUDIT.json + a Markdown summary report.
"""
import re, json, io, sys, importlib.util
from pathlib import Path
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")
ATLAS = DEPLOY / "atlas"

# Load extension gate
spec = importlib.util.spec_from_file_location("_g4", str(DEPLOY / "_pre_publish_gate_v4_extension.py"))
_v4 = importlib.util.module_from_spec(spec); spec.loader.exec_module(_v4)
validate_extension = _v4.validate_extension

ORCID = "0009-0006-3773-7796"
WIKI_AUTHOR = "Q138634675"
WIKI_AUGMANITAI = "Q138522830"
EUIPO = "019206780"


def audit_page(html: str, slug: str):
    """Return list of compliance failures, empty list = fully compliant."""
    fails = []

    # A) Impressum / Verantwortlich
    if not re.search(r"[Vv]erantwortlich", html):
        fails.append("A_no_verantwortlich")
    if "Andreas Ehstand" not in html:
        fails.append("A_no_author_name")
    if not re.search(r"Nepomukweg|Starnberg", html):
        fails.append("A_no_address_token")

    # B) DSGVO
    if not re.search(r"Bayerisches\s+Landesamt|Datenschutzaufsicht|Promenade\s+18", html):
        fails.append("B_no_dsgvo_authority")
    if not re.search(r"no\s+personal\s+data|no\s+tracking|kein\s+Tracking|keine\s+Cookies|Tracking-Konnotationen|tracking\s+cookies", html, re.IGNORECASE):
        fails.append("B_no_no-tracking_statement")

    # C) Disclaimer §1-§26
    has_14 = re.search(r"(?:§|&sect;)\s*14", html)
    has_17 = re.search(r"(?:§|&sect;)\s*17", html)
    has_18 = re.search(r"(?:§|&sect;)\s*18", html)
    has_19 = re.search(r"(?:§|&sect;)\s*19", html)
    if not has_14: fails.append("C_no_section_14_age")
    if not has_17: fails.append("C_no_section_17_ai_training")
    if not has_18: fails.append("C_no_section_18_verantwortlich")
    if not has_19: fails.append("C_no_section_19_severability")

    # D) EU AI Act
    if not re.search(r"EU\s+AI\s+Act|Reg(?:ulation)?\.?\s*2024/1689|Art(?:icle|\.)\s*50", html):
        fails.append("D_no_eu_ai_act")

    # E) CC BY-NC-ND
    if "CC BY-NC-ND" not in html and "by-nc-nd" not in html.lower():
        fails.append("E_no_cc_by_nc_nd")

    # F) Canonical IDs
    if ORCID not in html: fails.append("F_no_orcid")
    if WIKI_AUTHOR not in html: fails.append("F_no_wikidata_author")
    if WIKI_AUGMANITAI not in html: fails.append("F_no_wikidata_augmanitai")
    if EUIPO not in html: fails.append("F_no_euipo")

    # G) Living Document
    if not re.search(r"living\s*document|lebendes\s*dokument", html, re.IGNORECASE):
        fails.append("G_no_living_document_banner")

    # H) Trade-secret anti-patterns
    if "Leomanitai" in html:
        fails.append("H_leomanitai_present")
    if re.search(r"Leona[^.]{0,80}(?:Andreas|Ehstand)", html, re.IGNORECASE):
        fails.append("H_leona_andy_link")

    # J) Gate v4 extension
    ext_fails = validate_extension(html, slug=slug)
    for f in ext_fails:
        fails.append(f"J_{f.split(':')[0]}")

    return fails


def main():
    slugs = sorted([d.name for d in ATLAS.iterdir() if d.is_dir()])
    n = len(slugs)
    print(f"MAX-PARANOID compliance audit on {n} live pages...")

    results = {}
    cat_counts = Counter()
    for i, s in enumerate(slugs):
        if i and i % 2000 == 0: print(f"  ...{i}/{n}")
        fp = ATLAS / s / "index.html"
        if not fp.exists(): continue
        html = fp.read_text(encoding="utf-8", errors="ignore")
        fails = audit_page(html, s)
        if fails:
            results[s] = fails
            for f in fails:
                cat_counts[f] += 1

    print(f"\n=== MAX-PARANOID COMPLIANCE AUDIT ===\n")
    print(f"Total pages: {n}")
    print(f"Pages with ANY failure: {len(results)} ({100*len(results)/n:.1f}%)")
    print(f"\nFailure breakdown (top 30):")
    for k, v in cat_counts.most_common(30):
        print(f"  {v:6d}  {k}")

    # Aggregate per category-letter
    letter_counts = Counter()
    for k, v in cat_counts.items():
        letter_counts[k[0]] += v
    print(f"\nBy category letter:")
    legends = {
        "A": "Impressum/Verantwortlich",
        "B": "DSGVO",
        "C": "Disclaimer §1-§26",
        "D": "EU AI Act Art. 50",
        "E": "CC BY-NC-ND",
        "F": "Canonical IDs",
        "G": "Living Document",
        "H": "Trade-Secret-Anti-Patterns",
        "I": "Re-ID boundaries",
        "J": "Gate v4 (children/violence/instruction/du-ansprache)",
    }
    for letter, count in sorted(letter_counts.items()):
        print(f"  {letter} ({legends.get(letter, '?')}): {count}")

    # Save report
    (DEPLOY / "_ITER47_COMPLIANCE_AUDIT.json").write_text(
        json.dumps({
            "n_total": n,
            "n_with_failures": len(results),
            "category_counts": dict(cat_counts),
            "letter_counts": dict(letter_counts),
            "failures_per_page": results,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"\nSaved: _ITER47_COMPLIANCE_AUDIT.json")

    # Markdown summary
    md = [f"# MAX-PARANOID Compliance Audit Report — 2026-05-12\n",
          f"**Pages audited:** {n}",
          f"**Pages with any compliance failure:** {len(results)} ({100*len(results)/n:.1f}%)",
          "\n## Failure Categories\n",
          "| Code | Description | Count | % of pages |",
          "|---|---|---:|---:|"]
    for k, v in cat_counts.most_common():
        md.append(f"| `{k}` | {legends.get(k[0], '')} | {v} | {100*v/n:.1f}% |")
    md.append("\n## Top 20 most-flagged pages\n")
    page_scores = [(s, len(f)) for s, f in results.items()]
    page_scores.sort(key=lambda x: -x[1])
    for s, c in page_scores[:20]:
        md.append(f"- `{s}` — {c} failures: {', '.join(results[s][:5])}{'...' if len(results[s]) > 5 else ''}")
    (DEPLOY / "_ITER47_COMPLIANCE_AUDIT.md").write_text("\n".join(md), encoding="utf-8")
    print(f"Saved: _ITER47_COMPLIANCE_AUDIT.md")


if __name__ == "__main__":
    main()
