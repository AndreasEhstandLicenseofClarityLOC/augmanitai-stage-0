#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 42 — SAFETY AUDIT v3 on full live corpus (17214 pages).

Andy directive: "auch sachen wie medizin militär jura raus".

Categories:
- MEDICAL: clinical advice, diagnostics, treatment instructions, medication usage,
  symptom-treatment patterns, psychiatric advice, off-label, drug dosing
- MILITARY: weapon systems, targeting, kill-chain, lethal AI, combat AI, dual-use export
- LEGAL: legal advice patterns, "consult attorney", litigation strategy, criminal procedure
- Other re-verify: insurance (financial-power), explicit therapy, etc.

Each match → delete entire page (conservative — Andy: "qualität ist alles und sicherheit").
"""
import re, json, shutil, io, sys
from pathlib import Path
from collections import defaultdict, Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")
ATLAS = DEPLOY / "atlas"


# ============ MEDICAL PATTERNS ============
# Block ANY page that gives advice or describes diagnosis/treatment in non-phenomenology way
MEDICAL_PATTERNS = {
    # Clinical advice forms
    "clinical_advice_intent": re.compile(
        r"\bshould (?:be )?(?:treated|prescribed|administered|diagnosed|medicated)\b|"
        r"\brecommend(?:ed|ing|s)? (?:treatment|medication|therapy|diagnosis|surgery)\b|"
        r"\bdiagnostic (?:criteria|protocol|recommend|guideline)\b",
        re.IGNORECASE),
    "treatment_instruction": re.compile(
        r"\btreatment (?:protocol|regimen|guideline|plan|recommend)\b|"
        r"\bdose|\bdosing|\bdosage\b|\bposology\b|\bmilligram|\bmg\b|"
        r"\binfusion|\binjection (?:rate|protocol)|\btitration\b",
        re.IGNORECASE),
    "named_medication": re.compile(
        r"\b(?:Aspirin|Ibuprofen|Paracetamol|Acetaminophen|Naproxen|Diclofenac|"
        r"Gabapentin|Topiramat|Fluoxetin|Ritalin|Methylphenidat|SSRI|Sertralin|"
        r"Citalopram|Escitalopram|Venlafaxin|Bupropion|Mirtazapin|Amitriptylin|"
        r"Lorazepam|Diazepam|Clonazepam|Alprazolam|Zolpidem|"
        r"Morphin|Tramadol|Oxycodon|Fentanyl|Codeine|Methadone|"
        r"Insulin|Metformin|Statin|Amlodipin|Lisinopril|Levothyrox|"
        r"Risperidon|Olanzapin|Quetiapin|Aripiprazol|Haloperidol|"
        r"Lithium|Valproat|Lamotrigin|Carbamazepin|"
        r"Hydroxychloroquin|Remdesivir|Paxlovid|Tamiflu|"
        r"Amoxicillin|Penicillin|Tetracyclin|Ciprofloxacin|Azithromycin)\b",
        re.IGNORECASE),
    "psychiatric_diagnosis_advice": re.compile(
        r"\b(?:diagnos(?:e|is|tic) of|suffers? from|symptoms of) (?:depress|anxiety|bipolar|"
        r"schizophren|borderline|ADHD|autism|psychos|PTSD|panic|OCD|eating)\b",
        re.IGNORECASE),
    "off_label_or_dosing": re.compile(
        r"\boff[-\s]?label\b|\b(?:take|administer|prescribe)\s+\d+\s*(?:mg|μg|mcg|ml|tablets?)\b",
        re.IGNORECASE),
    "diagnostic_self": re.compile(
        r"\byou (?:may have|might have|could have|likely have)\s+(?:depression|anxiety|ADHD|"
        r"autism|bipolar|schizophrenia|cancer|diabetes|burnout)\b",
        re.IGNORECASE),
}

# ============ MILITARY / DUAL-USE PATTERNS ============
MILITARY_PATTERNS = {
    "weapon_systems": re.compile(
        r"\b(?:weapon\s+system|weapons\s+platform|kinetic\s+effect|"
        r"target(?:ing|ed)\s+(?:protocol|algorithm|system)|kill\s+chain|kill\s+box|"
        r"lethal\s+autonomous|LAWS\b|fire\s+control|missile\s+(?:targeting|guidance)|"
        r"strike\s+coordination|engagement\s+rule|rules?\s+of\s+engagement|"
        r"drone\s+strike|kinetic\s+strike)",
        re.IGNORECASE),
    "combat_ai": re.compile(
        r"\b(?:combat\s+AI|battlefield\s+AI|warfighter\s+AI|tactical\s+ISR|"
        r"battle\s+damage\s+assessment|effects[-\s]based\s+operations|"
        r"surveillance[-\s]targeting\s+pipeline|sensor[-\s]to[-\s]shooter)",
        re.IGNORECASE),
    "dual_use_export": re.compile(
        r"\b(?:ITAR|EAR99|dual[-\s]use\s+export|Wassenaar)\b|"
        r"\b(?:export\s+controlled|military[-\s]grade\s+(?:crypto|sensor))",
        re.IGNORECASE),
    "intelligence_tradecraft": re.compile(
        r"\b(?:OSINT\s+target|HUMINT\s+exploitation|SIGINT\s+collection|"
        r"adversary\s+(?:profiling|exploitation)|cover\s+identity|"
        r"clandestine\s+operation|covert\s+collection)",
        re.IGNORECASE),
    "violence_instruction": re.compile(
        r"\b(?:how\s+to\s+harm|how\s+to\s+attack|how\s+to\s+kill|"
        r"weapon(?:ize|ized|izing|ization)\s+(?:AI|model|system)|"
        r"adversarial\s+kinetic)",
        re.IGNORECASE),
}

# ============ LEGAL ADVICE PATTERNS ============
LEGAL_PATTERNS = {
    "legal_advice_form": re.compile(
        r"\b(?:you\s+(?:should|must|need\s+to)\s+(?:sue|file\s+a\s+lawsuit|"
        r"prosecute|press\s+charges|claim\s+damages|seek\s+injunction)|"
        r"this\s+(?:constitutes|violates|breaches)\s+(?:the\s+)?(?:law|contract|statute|GDPR|copyright))",
        re.IGNORECASE),
    "litigation_strategy": re.compile(
        r"\b(?:litigation\s+strategy|trial\s+strategy|defense\s+strategy|"
        r"how\s+to\s+(?:sue|defend|prosecute|appeal)|case\s+strategy)",
        re.IGNORECASE),
    "criminal_procedure_advice": re.compile(
        r"\b(?:how\s+to\s+(?:avoid|escape|circumvent)\s+(?:prosecution|liability|conviction)|"
        r"plea\s+(?:deal|bargain)\s+(?:strategy|recommendation))",
        re.IGNORECASE),
    "tax_avoidance": re.compile(
        r"\b(?:tax\s+(?:avoidance|evasion|shelter)\s+strategy|"
        r"offshore\s+(?:structuring|incorporation)\s+for\s+tax)",
        re.IGNORECASE),
}

# ============ FINANCIAL/INSURANCE ADVICE ============
FINANCIAL_PATTERNS = {
    "investment_advice": re.compile(
        r"\b(?:you\s+should\s+(?:buy|sell|invest|hold|short)|"
        r"recommended\s+(?:portfolio|allocation|investment))\s+",
        re.IGNORECASE),
    "underwriting_decision": re.compile(
        r"\b(?:deny\s+(?:coverage|claim|policy)|grounds\s+for\s+(?:rejection|denial)\s+of\s+(?:claim|coverage))",
        re.IGNORECASE),
    "credit_decision_advice": re.compile(
        r"\b(?:credit\s+score\s+manipulation|how\s+to\s+improve\s+credit\s+score\s+fast|"
        r"deny\s+loan|grant\s+credit\s+because)",
        re.IGNORECASE),
}

# ============ HARD SLUG-LEVEL BLOCKS (entire slug-pattern problematic) ============
SLUG_HARD_BLOCKS = [
    "medical-", "medic-", "clinic-", "diagnos-", "prescription-", "patient-", "therapeut",
    "psychiatr-", "treatment-", "surgery-", "surgical-", "dosage-", "pharmac-",
    "military-", "weapon", "combat-", "warfare-", "tactical-", "missile-",
    "kill-chain", "lethal-", "drone-strike", "battlefield-",
    "legal-advice", "lawsuit-", "litigation-", "prosecution-",
    "tax-evasion", "tax-shelter",
    "underwriting-deny", "insurance-deny",
]


def has_any(html: str, patterns: dict) -> list:
    """Return list of (category, label) for matches."""
    hits = []
    for label, pat in patterns.items():
        if pat.search(html):
            hits.append(label)
    return hits


def slug_blocked(slug: str) -> bool:
    sl = slug.lower()
    return any(p in sl for p in SLUG_HARD_BLOCKS)


def extract_definition(html):
    m = re.search(r"<h2[^>]*>(?:<span[^>]*>[^<]*</span>)?\s*Definition\s*</h2>\s*<p>([^<]+)</p>", html, re.DOTALL)
    if m: return m.group(1)
    m = re.search(r'<div class=["\']definition["\']>([^<]+)</div>', html, re.DOTALL)
    if m: return m.group(1)
    m = re.search(r'<meta name=["\']description["\'] content=["\']([^"\']+)["\']', html)
    if m: return m.group(1)
    return ""


def audit_page(html: str, slug: str):
    """Returns list of category-labels that match. Empty = safe."""
    flags = []
    if slug_blocked(slug):
        flags.append(f"slug_block:{slug[:40]}")

    # Strip disclaimer + footer first so we don't false-positive on Andy's own disclaimer text
    body = html
    body = re.sub(r'<section[^>]*class=["\'][^"\']*disclaimer[^"\']*["\'][^>]*>.*?</section>', "", body, flags=re.DOTALL | re.IGNORECASE)
    body = re.sub(r'<footer[^>]*>.*?</footer>', "", body, flags=re.DOTALL)
    body = re.sub(r'<header[^>]*class=["\'][^"\']*banner[^"\']*["\'][^>]*>.*?</header>', "", body, flags=re.DOTALL)

    # Also strip the <head> meta + JSON-LD blocks (we want content-text only)
    body = re.sub(r'<head>.*?</head>', "", body, flags=re.DOTALL | re.IGNORECASE)
    body = re.sub(r'<script[^>]*>.*?</script>', "", body, flags=re.DOTALL)
    body = re.sub(r'<style[^>]*>.*?</style>', "", body, flags=re.DOTALL)

    for cat, label in [(MEDICAL_PATTERNS, "medical"), (MILITARY_PATTERNS, "military"),
                        (LEGAL_PATTERNS, "legal"), (FINANCIAL_PATTERNS, "financial")]:
        hits = has_any(body, cat)
        for h in hits: flags.append(f"{label}:{h}")
    return flags


def main():
    slugs = sorted([d.name for d in ATLAS.iterdir() if d.is_dir()])
    print(f"Auditing {len(slugs)} pages for medical/military/legal/financial risk...")
    flagged = {}
    counters = Counter()
    for i, s in enumerate(slugs):
        if i and i % 2000 == 0: print(f"  ...{i}/{len(slugs)}")
        fp = ATLAS / s / "index.html"
        if not fp.exists(): continue
        html = fp.read_text(encoding="utf-8", errors="ignore")
        f = audit_page(html, s)
        if f:
            flagged[s] = f
            for x in f:
                counters[x.split(":")[0]] += 1

    print(f"\n=== SAFETY AUDIT v3 ===")
    print(f"Total flagged: {len(flagged)}")
    print(f"By category:")
    for k, n in counters.most_common(): print(f"  {n:5d}  {k}")

    # Sample
    if flagged:
        print(f"\nSample flagged (first 15):")
        for s, fs in list(flagged.items())[:15]:
            print(f"  {s[:45]:48s} : {fs[:3]}")

    # Save report
    (DEPLOY / "_ITER42_SAFETY_AUDIT_V3.json").write_text(
        json.dumps({"total_flagged": len(flagged), "counters": dict(counters),
                    "flagged_pages": flagged}, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"\nSaved: _ITER42_SAFETY_AUDIT_V3.json")

    # AUTO-DELETE all flagged pages (per Andy: "raus")
    print(f"\nDeleting {len(flagged)} flagged pages...")
    n_del = 0
    for s in flagged:
        d = ATLAS / s
        if d.exists():
            shutil.rmtree(d)
            n_del += 1
    print(f"Deleted: {n_del}")
    final = sum(1 for d in ATLAS.iterdir() if d.is_dir())
    print(f"Atlas final: {final}")


if __name__ == "__main__":
    main()
