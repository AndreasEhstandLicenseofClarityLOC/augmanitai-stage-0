#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LM Studio Worker — Local-bulk term generator.

Runs against the LM Studio Local Server at http://127.0.0.1:1234
Model: deepseek-r1-distill-qwen-32b (or whichever is loaded).

Generates raw term candidates that go through the SAME Pre-Publish-Gate
as our other waves before they reach atlas/.

Usage:
    # 1. Make sure LM Studio Local Server is running with a model loaded.
    # 2. Run a batch:
    python _LM_STUDIO_WORKER.py --batch_size 100 --output _worker_outputs/lm_studio_$(date +%Y%m%d_%H%M).jsonl
    # 3. Then intake:
    python _chief_intake.py --input _worker_outputs/lm_studio_*.jsonl

Output format (JSONL, one term per line):
{
  "english_name": "...",
  "definition_en": "...",
  "category": "...",
  "source_worker": "lm_studio_deepseek-r1-distill-qwen-32b"
}
"""
import json, re, sys, io, argparse, time, datetime
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import requests

LM_STUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"
MODEL_ID = "deepseek-r1-distill-qwen-32b"

# Worker-Prompt: ultra-paranoid baked in (no children, no violence, no instruction,
# no du-ansprache, no medical/military/legal advice). Output strict JSONL.
WORKER_PROMPT_TEMPLATE = """You are a precision terminology worker for an academic phenomenology corpus on human-AI interaction.

Generate {batch_size} NEW phenomena names that do NOT yet have an established label in the literature.

CATEGORY FOCUS: {category}

STRICT RULES (any violation = output rejected):
- No mention of children, minors, kids, infants, toddlers.
- No mention of physical or psychological violence, abuse, harassment, gaslighting.
- No "how-to" instructions, no imperative verbs at the start of sentences.
- No second-person addressing (no "you should", no "your brain", no "Sie", no "Du").
- No medical/clinical advice, no medication names, no diagnosis claims.
- No military/weapon/dual-use terminology.
- No legal advice patterns ("you should sue", "this constitutes...").
- No financial advice patterns.
- Output must be readable to a motivated 15-year-old (no obscure jargon).

OUTPUT FORMAT (strict JSONL, one term per line, NO markdown, NO commentary):
{{"english_name": "The Specific Phenomenon Name", "definition_en": "A descriptive sentence describing the phenomenon in human-AI interaction context. Must be at least 100 characters and describe what is observed, not what to do.", "category": "{category}"}}

Examples of GOOD outputs:
{{"english_name": "The Pause-Comfort Acknowledgement", "definition_en": "A subtle conversational rhythm where the human and AI share brief silences without rushing to fill them, indicating a relaxed mutual recognition that the interaction has reached a moment of contemplation rather than active production.", "category": "Cognitive_Shift"}}
{{"english_name": "Recursive Definition Drift", "definition_en": "The gradual evolution of meaning that occurs when a concept is repeatedly defined across many human-AI conversations, with each new framing slightly altering the original semantic anchor of the term in collective discourse.", "category": "Cognitive_Shift"}}

Now generate {batch_size} terms for category {category}. Output ONLY the JSONL lines. No preamble.
"""


def call_lm_studio(prompt: str, max_tokens: int = 4000, temperature: float = 0.7) -> str:
    """Single call to LM Studio. Returns content string."""
    payload = {
        "model": MODEL_ID,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
    }
    r = requests.post(LM_STUDIO_URL, json=payload, timeout=600)
    r.raise_for_status()
    j = r.json()
    return j["choices"][0]["message"]["content"]


def strip_thinking(text: str) -> str:
    """DeepSeek-R1 wraps its reasoning in <think>...</think>. Strip it."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    return text.strip()


def parse_jsonl(text: str) -> list:
    """Parse JSONL output. Tolerant of stray markdown/preamble."""
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("```") or line.startswith("#"): continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict) and obj.get("english_name") and obj.get("definition_en"):
                out.append(obj)
        except Exception:
            pass
    return out


def run_batch(category: str, batch_size: int, output_path: Path):
    prompt = WORKER_PROMPT_TEMPLATE.format(batch_size=batch_size, category=category)
    print(f"[LM Studio] Calling DeepSeek for {batch_size} terms in '{category}'...")
    t0 = time.time()
    raw = call_lm_studio(prompt, max_tokens=batch_size * 200)
    dt = time.time() - t0
    print(f"  Response in {dt:.1f}s")
    cleaned = strip_thinking(raw)
    terms = parse_jsonl(cleaned)
    print(f"  Parsed: {len(terms)} valid term-objects")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "a", encoding="utf-8") as f:
        for t in terms:
            t["source_worker"] = f"lm_studio_{MODEL_ID}"
            t["worker_timestamp"] = datetime.datetime.utcnow().isoformat()
            f.write(json.dumps(t, ensure_ascii=False) + "\n")
    return len(terms)


CATEGORIES = [
    "Cognitive_Shift", "Bridge_AI", "Vibe_Coding", "Temporal_AI", "Perception_AI",
    "Relational_AI", "Aging_AI", "Robotics", "Sports_AI", "Data_Science",
    "Translation_AI", "Photography_AI", "Software_Engineering", "Adult_Education",
    "Workplace", "Multi_Agent_Emergence", "Hybrid_Cognition", "Swarm_Encounter",
    "Embodied_AI", "Cross_Substrate_Phenomenology",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch_size", type=int, default=20, help="Terms per category-call (LM Studio can do ~20-40 well)")
    ap.add_argument("--rounds", type=int, default=1, help="How many rounds across all categories")
    ap.add_argument("--output", type=str, default=None, help="Output JSONL path")
    ap.add_argument("--categories", type=str, default=None, help="Comma-separated list (default: all)")
    args = ap.parse_args()

    cats = args.categories.split(",") if args.categories else CATEGORIES
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = Path(args.output) if args.output else Path(__file__).parent / "_worker_outputs" / f"lm_studio_{ts}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"Output → {out}")
    print(f"Categories: {len(cats)} · Rounds: {args.rounds} · Batch/category: {args.batch_size}")
    print(f"Target: ~{len(cats) * args.rounds * args.batch_size} candidates")

    total = 0
    for r in range(args.rounds):
        for cat in cats:
            try:
                n = run_batch(cat, args.batch_size, out)
                total += n
                print(f"  → {total} total candidates so far")
            except Exception as e:
                print(f"  ERROR on {cat}: {type(e).__name__}: {e}")
                time.sleep(5)
    print(f"\nDone. Total candidates: {total} in {out}")


if __name__ == "__main__":
    main()
