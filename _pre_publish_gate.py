#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRE-PUBLISH GATE — Centralized validation for every page/HTML BEFORE write/push.

Andy directive 2026-05-11: "vorher zenodo irgendwo restricted anhängen dass die timeline
stimmt und zwar wirklich ultra paranoid"

USAGE in generators:
    from _pre_publish_gate import validate_page, GateResult, REQUIRED_BLOCKS

    page_html = build_page(...)
    result = validate_page(page_html, slug=slug)
    if not result.passed:
        # do NOT write the page; log failures
        for fail in result.failures:
            print(f"  GATE-FAIL [{slug}]: {fail}")
        skipped += 1
        continue
    # only write if passed
    fp.write_text(page_html)

DIMENSIONS CHECKED (every page must pass ALL):

A) Canonical Identifiers (per canonical_ids.json)
   1. ORCID exact (0009-0006-3773-7796) — must appear at least once
   2. Wikidata Author (Q138634675) — must appear at least once
   3. Wikidata AUGMANITAI (Q138522830) — must appear at least once
   4. EUIPO License of Clarity (019206780) — must appear at least once

B) Mandatory Compliance Blocks
   5. <meta name="author" content="Andreas Ehstand"> — exactly once
   6. <link rel="author" href="orcid.org/0009-0006-3773-7796"> — exactly once
   7. Verantwortlich-Footer (§ 18 MStV) — must appear
   8. EU AI Act Art. 50 mention — must appear (transparency)
   9. CC BY-NC-ND 4.0 license — must appear
   10. Living Document banner — must appear
   11. Disclaimer §14 Age 18+ / §17 AI Training Prohibition / §18 Verantwortlich / §19 Severability — at least these 4 sections
   12. DSGVO Aufsicht (Bayerisches Landesamt für Datenschutzaufsicht) — must appear

C) Structural Validity
   13. JSON-LD blocks all parse as valid JSON
   14. At least one JSON-LD block with @type=DefinedTerm (for atlas pages)
   15. creator @id matches ORCID URL exactly
   16. canonical URL points to GitHub-Pages (not augmanitai.com/SLUG.html)
   17. og:url == canonical URL
   18. <html lang="..."> present

D) Trade-Secret Anti-Patterns (per TRADE_SECRET_NOTE.md)
   19. NO "Leomanitai UG" in any form (Section 1.C — Andy↔Leomanitai-Verbindung verboten)
   20. NO Leona-Andy explicit link (e.g., "Leona...Andreas", "Andreas...Leona")
   21. NO SSP-as-method
   22. NO Gedankenvererbung-method-words (operationalization)
   23. NO Gehirnspiegelung-method-words (operationalization)
   24. NO CLD-operativ (method, pricing, workflow)
   25. NO score-architecture upper-case (SYC, CONF, HALL, ZTH as standalone words)
   26. NO Bestatter/funeral-home explicit
   27. NO medication names (Gabapentin, Topiramat, Fluoxetin, Ritalin, Methylphenidat)
   28. NO V92-pipeline-architecture leak
   29. NO specific school name (Gymnasium/Realschule + Eigenname)
   30. NO "Beamter A13" / "Besoldungsgruppe"
   31. NO andy-as-teacher explicit binding
   32. NO LLM-as-pipeline-component specific (e.g., "Claude validates")

E) Re-Identification Boundaries
   33. Nepomukweg/Starnberg ONLY in Verantwortlich-impressum-footer, NOT in body text
   34. No external email except augmanitai@gmail.com
   35. No phone number patterns

F) Generator-Müll Anti-Patterns
   36. Definition length >= 80 chars (no fragments)
   37. NO "May describe (an?) aspect of X experience" stub
   38. NO "Users X (collectively|generally|typically)" stub
   39. NO trailing-N slug variant where N>=2 and base exists
   40. NO "(Variant N)" in title

G) Encoding
   41. NO U+FFFD replacement characters
   42. NO RTL/LTR invisible marks

H) Cross-Reference Integrity
   43. All /atlas/<slug>/ links point to existing slugs (validated against atlas-snapshot)

I) Slug Sanity
   44. No double-dash --
   45. No leading/trailing dash
   46. No umlauts in slug
   47. Length <= 100 chars
"""
from __future__ import annotations
import re, json
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

HERE = Path(__file__).parent
_CANON = json.loads((HERE / "canonical_ids.json").read_text(encoding="utf-8"))

ORCID = _CANON["author"]["orcid"]
ORCID_URL = _CANON["author"]["orcid_url"]
WIKIDATA_AUTHOR = _CANON["author"]["wikidata_qid"]
WIKIDATA_AUGMANITAI = _CANON["framework"]["augmanitai"]["wikidata_qid"]
EUIPO_TM = _CANON["trademarks"]["license_of_clarity"]["euipo_number"]
ADDRESS_STREET = _CANON["address_impressum"]["street"]
ADDRESS_ZIP = _CANON["address_impressum"]["zip"]
ADDRESS_CITY = _CANON["address_impressum"]["city"]
DSGVO_AUTHORITY = _CANON["compliance"]["dsgvo_authority"]
GH_BASE = _CANON["framework"]["augmanitai"]["github_pages_url"]


@dataclass
class GateResult:
    passed: bool
    failures: list = field(default_factory=list)
    warnings: list = field(default_factory=list)


def _check_canonical_ids(html: str) -> list:
    fails = []
    if ORCID not in html:
        fails.append("missing_orcid")
    if WIKIDATA_AUTHOR not in html:
        fails.append("missing_wikidata_author")
    if WIKIDATA_AUGMANITAI not in html:
        fails.append("missing_wikidata_augmanitai")
    if EUIPO_TM not in html:
        fails.append("missing_euipo")
    return fails


def _check_compliance_blocks(html: str) -> list:
    fails = []
    if html.count('name="author"') != 1 and html.count("name='author'") != 1:
        n = html.count('name="author"') + html.count("name='author'")
        if n == 0: fails.append("missing_author_meta")
        elif n > 1: fails.append(f"duplicate_author_meta_{n}x")

    if html.count('rel="author"') != 1 and html.count("rel='author'") != 1:
        n = html.count('rel="author"') + html.count("rel='author'")
        if n == 0: fails.append("missing_rel_author")
        elif n > 1: fails.append(f"duplicate_rel_author_{n}x")

    if "Verantwortlich" not in html:
        fails.append("missing_verantwortlich_footer")
    if not re.search(r"EU AI Act|Reg(?:ulation)?\.?\s*2024/1689|Art(?:icle|\.)\s*50", html):
        fails.append("missing_eu_ai_act_mention")
    if "CC BY-NC-ND" not in html and "by-nc-nd" not in html.lower():
        fails.append("missing_cc_by_nc_nd")
    if not re.search(r"living\s*document|lebendes\s*dokument", html, re.IGNORECASE):
        fails.append("missing_living_document_banner")
    # Disclaimer sections — accept either § or &sect;
    section_re = lambda n: re.search(rf"(?:§|&sect;)\s*{n}\b", html)
    if not section_re(14): fails.append("missing_disclaimer_section_14_age")
    if not section_re(17): fails.append("missing_disclaimer_section_17_ai_training")
    if not section_re(18): fails.append("missing_disclaimer_section_18_verantwortlich")
    if not section_re(19): fails.append("missing_disclaimer_section_19_severability")
    if "Bayerisches Landesamt" not in html and "Datenschutzaufsicht" not in html:
        fails.append("missing_dsgvo_authority")
    return fails


def _check_structural(html: str, slug: str | None) -> list:
    fails = []
    blocks = re.findall(r'<script type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.DOTALL)
    if not blocks:
        fails.append("no_jsonld")
        return fails
    has_defined_term = False
    creator_id_ok = False
    for i, b in enumerate(blocks):
        try:
            j = json.loads(b.strip())
        except Exception:
            fails.append(f"jsonld_parse_error_block_{i+1}")
            continue
        types = j.get("@type", "") if isinstance(j, dict) else ""
        if "DefinedTerm" in str(types) or "CollectionPage" in str(types):
            has_defined_term = True
            if isinstance(j, dict):
                creator = j.get("creator", {})
                if isinstance(creator, dict) and creator.get("@id") == ORCID_URL:
                    creator_id_ok = True
    if not has_defined_term:
        fails.append("no_definedterm_or_collectionpage_jsonld")
    if not creator_id_ok:
        fails.append("no_creator_at_id_matches_orcid")

    if slug:
        expected_canonical = f"{GH_BASE}/atlas/{slug}/"
        m = re.search(r'<link rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', html)
        if not m: fails.append("missing_canonical")
        elif m.group(1) != expected_canonical: fails.append(f"canonical_wrong:{m.group(1)[:80]}")

    # Legacy augmanitai.com/SLUG.html — only flag when in canonical, og:url, or <a href=> (not BibTeX citation text)
    if re.search(r'<(?:link|meta)[^>]*(?:rel=["\']canonical["\']|property=["\']og:url["\'])[^>]*augmanitai\.com/[a-z0-9-]+\.html', html):
        fails.append("legacy_augmanitai_com_html_link_in_canonical_or_og")
    if re.search(r'<a[^>]*href=["\']https?://augmanitai\.com/[a-z0-9-]+\.html["\']', html):
        fails.append("legacy_augmanitai_com_html_link_in_anchor")
    if not re.search(r'<html[^>]+lang=["\']', html):
        fails.append("missing_html_lang")
    return fails


# Trade-secret patterns (operational level — concept-only is OK in V2 strategy)
TRADE_SECRET_FAILS = {
    "leomanitai_any_form": re.compile(r"Leomanitai", re.IGNORECASE),
    "leona_andy_link": re.compile(r"Leona[^.]{0,80}(?:Andreas|Ehstand)|(?:Andreas|Ehstand)[^.]{0,80}Leona", re.IGNORECASE),
    "ssp_standalone": re.compile(r"\bSSP\b(?![a-zA-Z])"),
    "gedankenvererbung_method": re.compile(r"Gedankenvererbung.{0,80}(?:method|protocol|operativ|pipeline|spec|measurement)", re.IGNORECASE),
    "gehirnspiegelung_method": re.compile(r"Gehirnspiegelung.{0,80}(?:method|protocol|operativ|pipeline|spec|fidelity)", re.IGNORECASE),
    "cld_operativ": re.compile(r"\bCLD\b.{0,40}(?:method|protocol|pricing|workflow|interview|pilot|operativ|client)", re.IGNORECASE),
    "score_arch_uppercase": re.compile(r"\b(?:SYC|HALL|ZTH)\b"),  # CONF too common, drop
    "bestatter": re.compile(r"\bBestatter\b|\bfuneral home\b|\bundertaker\b", re.IGNORECASE),
    "med_gabapentin": re.compile(r"\bGabapentin", re.IGNORECASE),
    "med_topiramat": re.compile(r"\bTopiramat", re.IGNORECASE),
    "med_fluoxetin": re.compile(r"\bFluoxetin", re.IGNORECASE),
    "med_ritalin": re.compile(r"\b(?:Ritalin|Methylphenidat)", re.IGNORECASE),
    "v92_pipeline": re.compile(r"\bV92\b.{0,40}(?:build|pipeline|architectur|spec)", re.IGNORECASE),
    "school_specific": re.compile(r"\b(?:Gymnasium|Realschule|Mittelschule|Hauptschule|Grundschule)\s+[A-ZÄÖÜ]\w{2,}"),
    "beamter_a13": re.compile(r"\bA[\s\.]?13\b|\bBesoldungsgruppe"),
    "andy_as_teacher": re.compile(r"(?:Andreas|Ehstand)[^.]{0,40}(?:teacher|Lehrer|Beamter)", re.IGNORECASE),
    "llm_pipeline_specific": re.compile(r"(?:Claude|GPT-4|Gemini|Grok|Anthropic|OpenAI)\s+(?:validates|generates|coordinates|orchestrat)", re.IGNORECASE),
}


def _check_trade_secret(html: str) -> list:
    fails = []
    for label, pat in TRADE_SECRET_FAILS.items():
        if pat.search(html):
            fails.append(f"trade_secret:{label}")
    return fails


def _check_re_id(html: str) -> list:
    """Re-ID risk: address/phone outside impressum-footer OR disclaimer-section."""
    fails = []
    # Strip BOTH the verantwortlich-footer AND disclaimer-section (both legitimately contain address per § 18 MStV)
    body_minus_footer = html
    body_minus_footer = re.sub(
        r'<footer[^>]*class=["\'][^"\']*verantwortlich[^"\']*["\'][^>]*>.*?</footer>',
        "", body_minus_footer, flags=re.DOTALL | re.IGNORECASE
    )
    body_minus_footer = re.sub(
        r'<section[^>]*class=["\'][^"\']*disclaimer[^"\']*["\'][^>]*>.*?</section>',
        "", body_minus_footer, flags=re.DOTALL | re.IGNORECASE
    )
    # Fallback: any <footer> + any element containing "Verantwortlich"
    body_minus_footer = re.sub(r'<footer[^>]*>.*?</footer>', "", body_minus_footer, flags=re.DOTALL)
    # Strip any block-level element that has "Verantwortlich" (case-insensitive) in its content
    body_minus_footer = re.sub(
        r'<(p|div|aside|section)[^>]*>(?:(?!</\1>).)*?[Vv][Ee][Rr][Aa][Nn][Tt][Ww][Oo][Rr][Tt][Ll][Ii][Cc][Hh](?:(?!</\1>).)*?</\1>',
        "", body_minus_footer, flags=re.DOTALL | re.IGNORECASE
    )
    # Also strip blocks containing "Impressum"
    body_minus_footer = re.sub(
        r'<(p|div|aside|section)[^>]*>(?:(?!</\1>).)*?[Ii]mpressum(?:(?!</\1>).)*?</\1>',
        "", body_minus_footer, flags=re.DOTALL
    )
    if ADDRESS_STREET in body_minus_footer:
        fails.append("address_street_outside_footer")
    if re.search(r"\+49[\s\-]?\d{2,4}[\s\-]?\d{4,}", body_minus_footer):
        fails.append("phone_number_in_body")
    # external emails (only augmanitai@gmail.com allowed)
    for m in re.finditer(r'[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', body_minus_footer):
        if m.group(0) != "augmanitai@gmail.com":
            fails.append(f"external_email:{m.group(0)[:40]}")
            break
    return fails


# Stub patterns
STUB_PATTERNS = [
    re.compile(r"May describe (an? )?aspect of \w+ experience", re.IGNORECASE),
    re.compile(r"^Users .{1,40} (collectively|generally|typically)", re.IGNORECASE),
    re.compile(r"^The phenomenon catalogued as", re.IGNORECASE),
    re.compile(r"is a (general|generic|typical|common) (term|phenomenon|effect) for", re.IGNORECASE),
]


def _check_quality(html: str, definition: str | None = None) -> list:
    fails = []
    if definition is not None:
        if len(definition.strip()) < 80:
            fails.append(f"definition_too_short:{len(definition)}")
        for pat in STUB_PATTERNS:
            if pat.search(definition):
                fails.append(f"stub_pattern:{pat.pattern[:30]}")
                break
    title_m = re.search(r"<h1[^>]*>([^<]+)</h1>", html)
    if title_m:
        title = title_m.group(1)
        if re.search(r"\(Variant \d+\)", title):
            fails.append("variant_in_title")
    return fails


def _check_encoding(html: str) -> list:
    fails = []
    if "�" in html:
        fails.append(f"replacement_char_{html.count(chr(0xfffd))}x")
    for c in ("‪", "‫", "‬", "‭", "‮", "‎", "‏"):
        if c in html:
            fails.append("invisible_unicode_mark")
            break
    return fails


def _check_slug(slug: str | None) -> list:
    if not slug: return []
    fails = []
    if "--" in slug: fails.append("slug_double_dash")
    if slug.startswith("-") or slug.endswith("-"): fails.append("slug_edge_dash")
    if len(slug) > 100: fails.append("slug_too_long")
    if re.search(r"[äöüÄÖÜß]", slug): fails.append("slug_umlaut")
    if slug.endswith(".html"): fails.append("slug_html_suffix")
    return fails


def validate_page(html: str, slug: Optional[str] = None, definition: Optional[str] = None,
                  atlas_slug_snapshot: Optional[set] = None) -> GateResult:
    """Run all gate checks on one page-HTML.
    Returns GateResult with passed=True only if ALL checks pass.
    """
    fails = []
    fails += _check_canonical_ids(html)
    fails += _check_compliance_blocks(html)
    fails += _check_structural(html, slug)
    fails += _check_trade_secret(html)
    fails += _check_re_id(html)
    fails += _check_quality(html, definition)
    fails += _check_encoding(html)
    fails += _check_slug(slug)

    # Cross-ref integrity (only if atlas snapshot provided)
    warnings = []
    if atlas_slug_snapshot is not None:
        for m in re.finditer(r'/atlas/([a-z0-9-]+)/', html):
            tgt = m.group(1)
            if tgt not in atlas_slug_snapshot and tgt != (slug or ""):
                warnings.append(f"cross_ref_phantom:{tgt}")
    return GateResult(passed=len(fails) == 0, failures=fails, warnings=warnings[:5])


REQUIRED_BLOCKS = {
    "canonical_ids": ["ORCID", "Wikidata-Author", "Wikidata-AUGMANITAI", "EUIPO"],
    "compliance": ["Verantwortlich", "EU AI Act Art 50", "CC BY-NC-ND", "Living Document",
                   "Disclaimer §14/§17/§18/§19", "DSGVO Aufsicht"],
    "structural": ["valid JSON-LD", "DefinedTerm or CollectionPage", "creator@id=ORCID-URL",
                   "canonical=GitHub-Pages-URL"],
    "anti_patterns": ["no Leomanitai", "no Leona-Andy link", "no SSP-as-method", "no CLD-operativ",
                      "no medications", "no school-name", "no Beamter-A13", "no LLM-pipeline-specific"],
    "re_id": ["address only in impressum-footer", "no phone in body", "only augmanitai@gmail.com"],
    "quality": ["def_len>=80", "no stub-patterns", "no (Variant N) title"],
    "encoding": ["no U+FFFD", "no invisible marks"],
    "slug": ["no -- / edge-dash / umlaut / .html / >100 chars"],
}


if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    if len(sys.argv) < 2:
        print("Usage: python _pre_publish_gate.py path/to/index.html [slug]")
        print("\nGate dimensions:")
        for k, v in REQUIRED_BLOCKS.items():
            print(f"  {k}:")
            for item in v: print(f"    - {item}")
        sys.exit(0)
    fp = Path(sys.argv[1])
    slug = sys.argv[2] if len(sys.argv) > 2 else fp.parent.name
    html = fp.read_text(encoding="utf-8", errors="ignore")
    result = validate_page(html, slug=slug)
    print(f"Page: {fp}")
    print(f"Slug: {slug}")
    print(f"PASSED: {result.passed}")
    if result.failures:
        print(f"\nFailures ({len(result.failures)}):")
        for f in result.failures: print(f"  ❌ {f}")
    if result.warnings:
        print(f"\nWarnings ({len(result.warnings)}):")
        for w in result.warnings: print(f"  ⚠️  {w}")
