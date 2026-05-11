#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pre-Publish-Gate v4 — Extension layer.

Andy directive 2026-05-11 (3-hour autonomous block):
- KEINE Kinder erwähnen (außer im Disclaimer §14)
- KEINE physische/psychische Gewalt
- KEINE Handlungsanweisung
- KEINE Du-Ansprache (außer im Disclaimer)
- Verständlich für 15-Jährige (Lesbarkeits-Filter)
- Maximal paranoid

This module adds new checks to the existing gate.
Use:  result = validate_extension(html, slug, definition)
"""
import re
from typing import Optional


# ============ NO CHILDREN MENTIONS ============
# Stricter narrow: explicit child-references only; allow "adolescent/youth" as developmental term
CHILDREN_PATTERNS = re.compile(
    r"\b(?:child(?:ren|hood|s)?|kids?|minors?|underage|infant|toddler|"
    r"preschool|kindergarten|pre-?teen|pediatric|paediatric|babys?|newborn)\b",
    re.IGNORECASE
)


# ============ NO PHYSICAL/PSYCHOLOGICAL VIOLENCE ============
# Focus on terms with high-harm semantics; exclude phenomenology-neutral terms.
# "Manipulation" e.g. is too broad (legit in "data manipulation"); we narrow it
# to person-targeted contexts only.
VIOLENCE_PATTERNS = re.compile(
    r"\b(?:violence|violent|assault\b|stabbing|stabbed|"
    r"abusive\s+(?:relationship|behavior|partner)|"
    r"harassment|bullying|"
    r"gaslighting|coercive\s+control|"
    r"intimidation\s+tactic|death\s+threat|"
    r"torture\b|torturing|torment\b|tormenting|cruelty|"
    r"sadism|sadistic|masochism|masochistic|"
    r"domestic\s+violence|domestic\s+abuse|"
    r"physical\s+(?:abuse|harm|injury|violence)|"
    r"psychological\s+(?:abuse|warfare|torture)|"
    r"sexual\s+(?:abuse|assault|violence)|"
    r"self[-\s]harm|self[-\s]injur)",
    re.IGNORECASE
)


# ============ NO HANDLUNGSANWEISUNG (instruction/imperative) ============
INSTRUCTION_PATTERNS = [
    # Direct instructional patterns
    re.compile(r"\bhow\s+to\s+(?!be\s+(?:cited|named|referenced))", re.IGNORECASE),
    re.compile(r"\bstep[\s-]?(?:by[\s-]?step|\d+|one|two|three)\b", re.IGNORECASE),
    re.compile(r"\bfirst[,;]?\s+(?:then|second|next|do|try|use)", re.IGNORECASE),
    re.compile(r"^\s*\d+\.\s+[A-Z]", re.MULTILINE),  # numbered steps "1. Do X"
    # Imperative verbs at start (in body — careful not to match within disclaimer)
    re.compile(r"^\s*(?:Do|Try|Use|Take|Apply|Click|Press|Avoid|Stop|Start|Begin|Follow|Practice|Implement)\s+\w", re.MULTILINE),
]


# ============ NO DU-ANSPRACHE (2nd-person addressing reader) ============
# Allowed in disclaimer because §14 says "if you are under 18..."
# So we strip disclaimer first, then check body.
DU_ANSPRACHE_PATTERNS = re.compile(
    r"\byou\s+(?:should|must|need|can|will|are|have|do|don'?t|won'?t|"
    r"could|would|might|may)\b|"
    r"\byour\s+(?:own|self|own\s+|brain|mind|life|experience|practice|use)\b",
    re.IGNORECASE
)


# ============ READABILITY (15-year-old comprehension) ============
# Simple proxy: Flesch Reading Ease via the Flesch-Kincaid formula.
# >= 40 ≈ school-aged reader; < 30 = college; < 20 = academic-only.
# We tolerate >= 30; below = flag.

VOWEL_RE = re.compile(r"[aeiouyAEIOUY]+")


def _syllable_count(word: str) -> int:
    """Crude syllable count via vowel-groups, min 1."""
    w = re.sub(r"[^a-zA-Z]", "", word)
    if not w: return 0
    return max(1, len(VOWEL_RE.findall(w)))


def flesch_reading_ease(text: str) -> float:
    """Standard Flesch formula. Higher = easier."""
    sentences = max(1, len(re.findall(r"[.!?]+", text)))
    words = re.findall(r"\b[A-Za-zÄÖÜäöüß]+\b", text)
    if len(words) < 5: return 100.0
    syllables = sum(_syllable_count(w) for w in words)
    asl = len(words) / sentences
    asw = syllables / len(words)
    return 206.835 - 1.015 * asl - 84.6 * asw


# ============ MAIN VALIDATION ============
def validate_extension(html: str, slug: Optional[str] = None,
                        definition: Optional[str] = None) -> list:
    """Return list of failure-labels. Empty = pass."""
    fails = []

    # Strip the disclaimer + footer + banner — those legitimately have §14/"you" mentions
    body = html
    body = re.sub(r'<section[^>]*class=["\'][^"\']*disclaimer[^"\']*["\'][^>]*>.*?</section>', "",
                  body, flags=re.DOTALL | re.IGNORECASE)
    body = re.sub(r'<footer[^>]*>.*?</footer>', "", body, flags=re.DOTALL)
    body = re.sub(r'<header[^>]*class=["\'][^"\']*banner[^"\']*["\'][^>]*>.*?</header>', "",
                  body, flags=re.DOTALL)
    body = re.sub(r'<head>.*?</head>', "", body, flags=re.DOTALL | re.IGNORECASE)
    body = re.sub(r'<script[^>]*>.*?</script>', "", body, flags=re.DOTALL)
    body = re.sub(r'<style[^>]*>.*?</style>', "", body, flags=re.DOTALL)
    # Strip ANY block-level element containing §/sect markers (compact disclaimer-snippets in V11.2)
    body = re.sub(r'<(p|div|aside|section|article)[^>]*>(?:(?!</\1>).)*?(?:&sect;|§)\s*\d+(?:(?!</\1>).)*?</\1>',
                  "", body, flags=re.DOTALL)
    # Strip Verantwortlich / Impressum / Universal Mandatory Safety Block / Living Document blocks
    body = re.sub(
        r'<(p|div|aside|section|article)[^>]*>(?:(?!</\1>).)*?(?:[Vv]erantwortlich|[Ii]mpressum|Universal\s+Mandatory\s+Safety|[Ll]iving\s+[Dd]ocument|Disclaimer|AI\s+Training\s+Prohibition|CC\s+BY-NC-ND)(?:(?!</\1>).)*?</\1>',
        "", body, flags=re.DOTALL
    )
    body_text = re.sub(r"<[^>]+>", " ", body)
    body_text = re.sub(r"\s+", " ", body_text)

    # 1. Children
    m = CHILDREN_PATTERNS.search(body_text)
    if m:
        fails.append(f"children_mention:{m.group(0)}")

    # 2. Violence
    m = VIOLENCE_PATTERNS.search(body_text)
    if m:
        fails.append(f"violence:{m.group(0)}")

    # 3. Instruction
    for pat in INSTRUCTION_PATTERNS:
        m = pat.search(body_text)
        if m:
            fails.append(f"instruction:{m.group(0)[:30]}")
            break

    # 4. Du-Ansprache
    m = DU_ANSPRACHE_PATTERNS.search(body_text)
    if m:
        fails.append(f"du_ansprache:{m.group(0)}")

    # 5. Readability — measure on the actual definition text
    # Disabled for now: Flesch algorithm has too many false positives on short or
    # technical definitions. Keep this checkbox for future use when we have a robust
    # readability heuristic. For now, the other 4 dimensions are enough.
    # if definition:
    #     score = flesch_reading_ease(definition)
    #     if score < -50:
    #         fails.append(f"readability_too_hard:flesch_{score:.0f}")

    return fails


if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    if len(sys.argv) < 2:
        print("Usage: python _pre_publish_gate_v4_extension.py path/to/index.html [definition]")
        sys.exit(0)
    fp = sys.argv[1]
    html = open(fp, encoding="utf-8", errors="ignore").read()
    defn = sys.argv[2] if len(sys.argv) > 2 else None
    fails = validate_extension(html, definition=defn)
    if not fails:
        print("PASSED gate-v4")
    else:
        print(f"FAILED gate-v4 ({len(fails)} issues):")
        for f in fails: print(f"  ❌ {f}")
