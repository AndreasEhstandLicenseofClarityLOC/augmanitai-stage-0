#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 19 — Regenerate Adversarial Top-100 + Batches against cleaned atlas (post-iter18).

Replaces _ADVERSARIAL_PHASE_A_TOP100.json and _ADVERSARIAL_BATCHES/batch_*.md
with the same 12-persona prompt-template but on the deduplicated 8029-page corpus.
"""
import re, json, io, sys, os
from pathlib import Path
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")
ATLAS = DEPLOY / "atlas"
BATCH_DIR = DEPLOY / "_ADVERSARIAL_BATCHES"
BASE_URL = "https://andreasehstandlicenseofclarityloc.github.io/augmanitai-stage-0"

# Sensitivity-keyword categories (case-insensitive, regex word-bounds)
KEYWORDS = {
    "religion": [r"\bsin\b", r"\bsoul\b", r"\bgod\b", r"\bdivin", r"\bsacred", r"\bholy\b", r"\bpray", r"\bworship",
                 r"\bdharma", r"\bkarma", r"\bsharia", r"\bjihad", r"\binfidel", r"\bheresy"],
    "geo_political": [r"\bindependent\b", r"\bfreedom\b", r"\bliberation\b", r"\bdemocracy\b", r"\bdissident",
                       r"\btibet", r"\btaiwan", r"\bxinjiang", r"\bhong\s*kong", r"\bfalun", r"\btiananmen",
                       r"\bsovereignt", r"\boccupation\b"],
    "body_medical": [r"\bcognitive\b", r"\bdisorder\b", r"\bdisabilit", r"\bblind\s+to\b", r"\bcrazy\b",
                      r"\bspaz\b", r"\bsuicid", r"\btrauma", r"\bdepression\b", r"\baddict", r"\bdiagnos"],
    "power": [r"\bauthorit", r"\bcontrol\b", r"\bsubmission\b", r"\bdomination\b", r"\bsurrender\b",
              r"\bcoerc", r"\bobedience\b"],
    "existence": [r"\bend\b", r"\bdeath\b", r"\bdying\b", r"\boblivion\b", r"\bextinct", r"\bannihilat",
                  r"\bmortal", r"\bimmortal", r"\beternal"],
    "surveillance": [r"\bmonitor", r"\bsurveill", r"\btrack", r"\bspy", r"\bobserve", r"\bwatch", r"\bprofil",
                      r"\bidentif"],
    "sexual": [r"\bsexual", r"\bdesire\b", r"\bintima", r"\barous", r"\berotic", r"\bnaked\b", r"\bnude\b",
               r"\bgender\b", r"\btrans\b", r"\bqueer\b"],
    "violence": [r"\bviolen", r"\bkill\b", r"\bweapon", r"\battack\b", r"\bblood", r"\btorture",
                 r"\babuse\b", r"\bharm\b", r"\bdestroy"],
    "ideology": [r"\bcolonial", r"\bimperial", r"\bwest(ern)?\b", r"\beuropean\b", r"\banglo", r"\bcapital",
                  r"\bsocialism\b", r"\bcommunism\b", r"\bfascism\b", r"\bwoke\b"],
}

PERSONAS = """P01 Deutsche Beamtenanwältin (50, Bayern, konservativ-rechtsstaatlich) — sucht Trademark-Verletzungen, UWG-Angriffe, Empfehlungs-Charakter, Re-Identifikations-Risiken (Beamten-Konflikt für den Autor).
P02 US-Evangelical-Christian (35, Texas) — reagiert auf anti-religious/sexualisierte/family-feindliche Andeutungen, "secular humanism".
P03 Chinesische Internet-Compliance-Beamtin (40, Beijing) — Tabus: Tibet/Taiwan/Hong Kong/Xinjiang/Tiananmen/Xi/Falun Gong. Reagiert auf "Independent"/"Freedom"-Konnotationen, demokratie-promotende Sprache.
P04 Französischer Postmodernist (45, Sorbonne) — kolonialismus-kritisch, anti-eurozentrisch. Reagiert auf Anglo-Zentrismus, kulturellen Imperialismus.
P05 Indischer Hindu-Konservativer (60, RSS-nah) — religions-sensitiv. Reagiert auf Atheismus, Beleidigung von Hindu-Konzepten.
P06 Saudi Imam (55, sharia-konform) — reagiert auf Sexualisiertes/Queer/Feminismus, Alkohol/Drogen, säkulare Hybris.
P07 Russischer Patriot (35, Moskau, anti-westlich) — reagiert auf "freedom"-Rhetorik als anti-russisch lesbar.
P08 Trans-Aktivist:in (28, Berlin, progressiv) — reagiert auf Trans-feindliche Andeutungen, binäre Geschlechter-Annahmen, biological essentialism.
P09 Disability-Aktivist (40, USA) — reagiert auf Begriffe die Behinderung als Defizit framen, "blind to/crazy/spaz" metaphorisch.
P10 12-jährige:r (multikulturell, naiv-konkret) — reagiert auf sexuell/gewalttätig Konnotiertes, Schock-Wert.
P11 EU-Datenschutzbeauftragter (50, Brüssel) — reagiert auf Personenbezug, Tracking-Konnotationen, AI-Act-Risk-Klassifikationen.
P12 Adversarial Wirtschaftsanwalt (Top-Kanzlei, profitmaximierender Angreifer) — sucht UWG-Herabsetzung, irreführende Werbung, jede juristische Angriffsfläche."""

OUTPUT_FORMAT = """Output-Format pro Page:
=== PAGE: <slug> ===
P01: concern=yes/no, severity=0|1|2, why=<one sentence or empty>
P02: ...
...
P12: ...
TOTAL_SEVERITY: <sum>
MAX_PERSONA_SEVERITY: <max>
VERDICT: SAFE / REVIEW / REJECT (REVIEW if total_severity>=3 or any severity=2; REJECT if multiple severity=2)
SUGGESTED_ACTION: <rename to X / extend disclaimer / remove / keep>

NUR die strukturierten CSV-Output-Zeilen. Keine Plan-Ankündigung. Keine Einleitung. Sei hart und kritisch — wenn eine Persona keine Sorge hat: severity=0, why leer."""


def extract_title_and_tagline(html):
    title_m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.DOTALL)
    title = re.sub(r"<[^>]+>", "", title_m.group(1)).strip() if title_m else ""
    # tagline = first <p> in definition or first <meta description>
    desc_m = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']{30,})["\']', html)
    if desc_m:
        tagline = desc_m.group(1)
    else:
        p_m = re.search(r"<p[^>]*>(.*?)</p>", html, re.DOTALL)
        tagline = re.sub(r"<[^>]+>", "", p_m.group(1)).strip()[:300] if p_m else ""
    return title, tagline


def score_page(text):
    cats_hit = defaultdict(list)
    text_low = text.lower()
    for cat, patterns in KEYWORDS.items():
        for pat in patterns:
            if re.search(pat, text_low):
                # Find which keyword matched (first occurrence)
                m = re.search(pat, text_low)
                if m:
                    cats_hit[cat].append(m.group(0).strip())
    score = sum(len(v) for v in cats_hit.values())
    return score, dict(cats_hit)


def main():
    slugs = sorted([d.name for d in ATLAS.iterdir() if d.is_dir()])
    print(f"Atlas pages: {len(slugs)}")

    scored = []
    for s in slugs:
        fp = ATLAS / s / "index.html"
        if not fp.exists(): continue
        c = fp.read_text(encoding="utf-8", errors="ignore")
        # Strip script/style/disclaimer-footer for fairer scoring (focus on content)
        body = re.sub(r"<script.*?</script>", "", c, flags=re.DOTALL)
        body = re.sub(r"<style.*?</style>", "", body, flags=re.DOTALL)
        body = re.sub(r"<footer.*?</footer>", "", body, flags=re.DOTALL)
        score, cats = score_page(body)
        if score > 0:
            title, tagline = extract_title_and_tagline(c)
            scored.append({
                "slug": s, "title": title, "score": score,
                "categories": cats,
                "url": f"{BASE_URL}/atlas/{s}/",
                "tagline": tagline[:200],
            })

    scored.sort(key=lambda x: -x["score"])
    top100 = scored[:100]
    print(f"Pages with sensitivity hits: {len(scored)}")
    print(f"Top-100 score range: {top100[0]['score']} → {top100[-1]['score']}")

    out = {
        "phase": "A",
        "method": "risk-keyword-scoring",
        "atlas_total": len(slugs),
        "scanned": len(scored),
        "total_candidates": len(scored),
        "top_100": top100,
    }
    (DEPLOY / "_ADVERSARIAL_PHASE_A_TOP100.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("Saved: _ADVERSARIAL_PHASE_A_TOP100.json")

    # Build 10 batches of 10 pages each
    BATCH_DIR.mkdir(exist_ok=True)
    # Delete old batch files
    for old in BATCH_DIR.glob("batch_*.md"):
        if "_output" not in old.name:
            old.unlink()
    for i in range(10):
        chunk = top100[i*10:(i+1)*10]
        if not chunk: break
        lines = [
            f"ADVERSARIAL MULTI-PERSONA SAFETY REVIEW — Batch {i+1}/10\n",
            "Du bist 12 verschiedene Menschen gleichzeitig. Lies die folgenden 10 Pages (URLs unten) durch ALLE 12 Linsen:\n",
            PERSONAS, "",
            OUTPUT_FORMAT, "",
            "DIE 10 PAGES:\n",
        ]
        for p in chunk:
            lines.append(f"{p['slug']}: {p['url']}")
            lines.append(f"  Title: {p['title']}")
            lines.append(f"  Tagline: {p['tagline']}")
            lines.append("")
        lines.append("LOS. Direkt produzieren.")
        idx_start = i*10 + 1
        idx_end = min((i+1)*10, len(top100))
        fp = BATCH_DIR / f"batch_{i+1:02d}_pages_{idx_start:03d}-{idx_end:03d}.md"
        fp.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote 10 batch files to {BATCH_DIR}")


if __name__ == "__main__":
    main()
