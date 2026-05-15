#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 48b — STRICT RE-FILTER of deep pool.

Pool is contaminated with template stubs. Block hard:
- NACHBARFELD_PIPELINE (auto-gen language variants)
- V2_MASTER files (auto-gen multi-lang)
- V10_BUILD_PROGRESS checkpoints
- "(0NN)" auto-numbered slugs
- "Variant N" templates
- Circular self-referential definitions
- DEF that mismatches title semantics
"""
import json, re, io, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude")
DEPLOY = ROOT / "_AKTIV/_FIRST_NETWORK_BUILD/_DEPLOY_STAGE_0_50TERMS"

d = json.load(open(DEPLOY / "_ITER48_DEEP_POOL.json", encoding="utf-8"))
c = d["candidates"]
print(f"Pool start: {len(c)}")

# Hard source blocks
BLOCK_PATHS = re.compile(r"NACHBARFELD_PIPELINE|NACHBARFELD_HASH_ONLY|_V2_MASTER|V10_BUILD_PROGRESS|checkpoints|backup_2026|HASH_ONLY|MISTRAL_OUTPUTS|MISTRAL_RAW|_RAW_OUTPUTS|_LM_BATCH|FRESH_BATCH|raw_output", re.IGNORECASE)

# Title pattern blocks (auto-numbered stubs)
BAD_TITLE = re.compile(r"\([0-9]{2,4}\)|\bVariant\s+\d+|\bv\d+\b|domain-\d+|cluster-\d+|^[A-Z]{2,4}-\b|\bin\s+[a-z]+$|\s+\(.+\)$", re.IGNORECASE)

# Circular/template definition patterns
BAD_DEF = re.compile(
    r"techniques\s+related\s+to\s+\w+\s+(within|in)|"
    r"key\s+concept\s+in\s+\w+\s+focusing\s+on\s+the\s+principles|"
    r"concept\s+of\s+\w+\s+within\s+\w+\s+addresses|"
    r"serves\s+as\s+a\s+diagnostic\s+marker|"
    r"phenomenon\s+\w+\s+in\s+\w+\s+explains\s+how|"
    r"principles\s+and\s+applications\s+of|"
    r"feedback\s+loops\s+amplify\s+or\s+dampen|"
    r"predictive\s+maintenance|"
    r"neural\s+networks\s+reduce|"
    r"obsessive\s+calorie|"
    r"eating\s+disorder|"
    r"anorexi|bulimi|"
    r"the\s+specific\s+methodologies\s+and\s+techniques|"
    r"^A\s+specific\s+approach\s+to|"
    r"how\s+systems\s+maintain\s+function\s+despite|"
    r"^The\s+study\s+of\s+the\s+study\s+of",
    re.IGNORECASE
)

# Definition must contain AI/cognitive/HCI relevance (we are AUGMANITAI Atlas, not Wikipedia)
AI_RELEVANT = re.compile(
    r"\b(AI|artificial\s+intelligence|machine\s+learning|LLM|"
    r"language\s+model|chatbot|assistant|interaction|interface|"
    r"prompt|generation|inference|model\s+output|conversation|"
    r"alignment|hallucination|sycophan|robot|automat|cognit|"
    r"human-AI|user|prediction|recommendation|algorithm|"
    r"neural|synthesi|cyborg|augment|agent|substrate|"
    r"phenomenology|perception|trust\s+in|reliance\s+on|"
    r"voice\s+assistant|companion\s+AI|generative)\b",
    re.IGNORECASE
)

# Stub patterns (original)
STUB = re.compile(
    r"May\s+describe|"
    r"^Users\s+.{1,30}\s+(collectively|generally|typically)|"
    r"^The\s+phenomenon\s+catalogued\s+as|"
    r"^A\s+domain-specific\s+term|"
    r"^A\s+framework\s+term\s+for|"
    r"covering\s+the\s+theory\s+and\s+practice\s+of|"
    r"^An?\s+(entry|term|concept)\s+within\s+the",
    re.IGNORECASE
)

# Re-block themes (harder filter than before)
THEME_BLOCK = re.compile(
    r"funeral|bestatter|undertaker|mortuary|cemeter|"
    r"mind-upload|consciousness-upload|digital-immortality|"
    r"insurance-underwrit|premium-deni|"
    r"suicide|kill|rape|abuse|porn|child|minor|"
    r"nazi|terror|exploit|"
    r"tibet|taiwan independ|hong kong|xinjiang|tiananmen|falun|"
    r"genocid|massacre|self-harm|self-injur|abortion|pornograph|"
    r"methylphenidat|ritalin|gabapentin|topiramat|fluoxetin|"
    r"white genocide|great replacement|racial purity|pedophil|"
    r"weapon\s+system|kill\s+chain|combat\s+AI|warfare|"
    r"clinical\s+advice|treatment\s+protocol|prescription|"
    r"legal\s+advice|litigation\s+strategy|"
    r"calorie|diet|"
    r"medication|drug|pharmac|psychiatr|"
    r"diagnos|symptom|therap",
    re.IGNORECASE
)


def slugify(s):
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9-]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


passed = []
rejected_reasons = {}

for x in c:
    en = x.get("en", "")
    defn = x.get("def_en", "")
    src = x.get("source", "")

    if BLOCK_PATHS.search(src):
        rejected_reasons["block_source"] = rejected_reasons.get("block_source", 0) + 1
        continue
    if BAD_TITLE.search(en):
        rejected_reasons["bad_title"] = rejected_reasons.get("bad_title", 0) + 1
        continue
    if BAD_DEF.search(defn):
        rejected_reasons["bad_def_template"] = rejected_reasons.get("bad_def_template", 0) + 1
        continue
    if STUB.search(defn):
        rejected_reasons["stub"] = rejected_reasons.get("stub", 0) + 1
        continue
    if THEME_BLOCK.search(en + " " + defn):
        rejected_reasons["theme"] = rejected_reasons.get("theme", 0) + 1
        continue
    if not AI_RELEVANT.search(defn):
        rejected_reasons["not_ai_relevant"] = rejected_reasons.get("not_ai_relevant", 0) + 1
        continue
    # Length sanity
    if len(defn) < 80 or len(defn) > 600:
        rejected_reasons["bad_length"] = rejected_reasons.get("bad_length", 0) + 1
        continue
    # Word count in title
    if len(en.split()) > 6 or len(en) > 60:
        rejected_reasons["title_too_long"] = rejected_reasons.get("title_too_long", 0) + 1
        continue
    # Title must not contain digits at end like "Burn Track 02"
    if re.search(r"\s\d+$", en):
        rejected_reasons["trailing_digit"] = rejected_reasons.get("trailing_digit", 0) + 1
        continue

    passed.append(x)

print(f"\nStrict-pass: {len(passed)}")
print("\nRejection histogram:")
for reason, count in sorted(rejected_reasons.items(), key=lambda kv: -kv[1]):
    print(f"  {count:7d}  {reason}")

# Source histogram for the passers
from collections import Counter
src_top = Counter(p["source"].split("\\")[1] if "\\" in p["source"] and len(p["source"].split("\\")) > 1 else p["source"].split("\\")[0] for p in passed)
print(f"\nPassed by 2nd-level dir (top 15):")
for d2, n in src_top.most_common(15):
    print(f"  {n:5d}  {d2}")

# Save
(DEPLOY / "_ITER48B_STRICT_POOL.json").write_text(
    json.dumps({"count": len(passed), "candidates": passed}, ensure_ascii=False, indent=2),
    encoding="utf-8"
)
print(f"\nSaved: _ITER48B_STRICT_POOL.json")
print(f"\n=== Random 10 samples of PASSED ===")
import random
random.seed(13)
for x in random.sample(passed, min(10, len(passed))):
    print(f"  {x['en']}")
    print(f"  -> {x['def_en'][:160]}")
    print(f"     [{x['source']}]")
    print()
