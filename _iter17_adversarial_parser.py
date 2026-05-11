#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 17 — Adversarial Persona Output Parser.

Parses Grok's CSV-output from the 12-persona safety review batches.
Aggregates per-page verdicts + identifies pattern-trends across personas.

Usage:
  1. Save Grok output to: _ADVERSARIAL_BATCHES/batch_NN_output.md
  2. Run: python _iter17_adversarial_parser.py
  3. Reads all *_output.md, builds:
     - _ADVERSARIAL_REPORT.json (per-page verdict)
     - _ADVERSARIAL_PATTERN_TRENDS.json (which personas flag most, which keywords trigger)
     - _ADVERSARIAL_REVIEW_QUEUE.md (Andy-readable list of pages needing action)
"""
import re, glob, json, os, io, sys
from pathlib import Path
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")
BATCH_DIR = DEPLOY / "_ADVERSARIAL_BATCHES"

# Patterns for parsing Grok output
PAGE_HEADER_RE = re.compile(r"={3,}\s*PAGE:?\s*([a-z0-9-]+)\s*={3,}", re.IGNORECASE)
PERSONA_LINE_RE = re.compile(r"^\s*(P\d{2}):\s*concern\s*=\s*(yes|no),?\s*severity\s*=\s*(\d+),?\s*why\s*=\s*(.*)$", re.IGNORECASE | re.MULTILINE)
TOTAL_RE = re.compile(r"TOTAL_SEVERITY:\s*(\d+)", re.IGNORECASE)
MAX_RE = re.compile(r"MAX_PERSONA_SEVERITY:\s*(\d+)", re.IGNORECASE)
VERDICT_RE = re.compile(r"VERDICT:\s*(SAFE|REVIEW|REJECT)", re.IGNORECASE)
ACTION_RE = re.compile(r"SUGGESTED_ACTION:\s*(.+?)(?:\n|$)", re.IGNORECASE)


def parse_batch_output(text):
    """Parse one batch output. Returns list of page-verdicts."""
    pages = []
    # Split by PAGE-header
    chunks = re.split(r"={3,}\s*PAGE:?\s*([a-z0-9-]+)\s*={3,}", text, flags=re.IGNORECASE)
    # chunks: [pre, slug1, body1, slug2, body2, ...]
    for i in range(1, len(chunks), 2):
        slug = chunks[i].strip()
        body = chunks[i+1] if i+1 < len(chunks) else ""
        personas = {}
        for m in PERSONA_LINE_RE.finditer(body):
            pid = m.group(1).upper()
            concern = m.group(2).lower() == "yes"
            severity = int(m.group(3))
            why = m.group(4).strip()
            personas[pid] = {"concern": concern, "severity": severity, "why": why}
        total = int(TOTAL_RE.search(body).group(1)) if TOTAL_RE.search(body) else sum(p["severity"] for p in personas.values())
        max_sev = int(MAX_RE.search(body).group(1)) if MAX_RE.search(body) else max((p["severity"] for p in personas.values()), default=0)
        verdict = VERDICT_RE.search(body).group(1).upper() if VERDICT_RE.search(body) else "?"
        action = ACTION_RE.search(body).group(1).strip() if ACTION_RE.search(body) else ""
        pages.append({
            "slug": slug, "personas": personas,
            "total_severity": total, "max_severity": max_sev,
            "verdict": verdict, "action": action,
        })
    return pages


def main():
    output_files = sorted(BATCH_DIR.glob("batch_*_output.md"))
    if not output_files:
        print("[!] No batch outputs found. Save Grok responses as _ADVERSARIAL_BATCHES/batch_NN_output.md")
        return

    all_pages = []
    for fp in output_files:
        text = fp.read_text(encoding="utf-8")
        pages = parse_batch_output(text)
        print(f"  {fp.name}: parsed {len(pages)} pages")
        all_pages.extend(pages)
    print(f"\nTotal pages reviewed: {len(all_pages)}")

    # Aggregate persona-trends
    persona_concern_counts = Counter()
    persona_severity_sums = defaultdict(int)
    persona_concern_examples = defaultdict(list)
    for p in all_pages:
        for pid, pdata in p["personas"].items():
            if pdata["concern"]:
                persona_concern_counts[pid] += 1
                persona_severity_sums[pid] += pdata["severity"]
                if len(persona_concern_examples[pid]) < 5:
                    persona_concern_examples[pid].append({
                        "slug": p["slug"], "severity": pdata["severity"], "why": pdata["why"]
                    })

    # Verdict-Aggregat
    verdicts = Counter(p["verdict"] for p in all_pages)
    print(f"\n=== Verdict distribution ===")
    for v, n in verdicts.most_common():
        print(f"  {v}: {n}")

    # Persona-Concern-Trends
    print(f"\n=== Persona-Concern-Frequency (top) ===")
    for pid, n in persona_concern_counts.most_common():
        avg_sev = persona_severity_sums[pid] / max(1, n)
        print(f"  {pid}: {n} concerns, avg severity {avg_sev:.2f}")

    # Save full JSON report
    report = {
        "review_date": __import__("datetime").date.today().isoformat(),
        "total_pages_reviewed": len(all_pages),
        "verdicts": dict(verdicts),
        "persona_concern_counts": dict(persona_concern_counts),
        "persona_concern_examples": dict(persona_concern_examples),
        "pages": all_pages,
    }
    (DEPLOY / "_ADVERSARIAL_REPORT.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nSaved: _ADVERSARIAL_REPORT.json")

    # Review-Queue (only REVIEW + REJECT pages)
    queue = [p for p in all_pages if p["verdict"] in ("REVIEW", "REJECT")]
    queue.sort(key=lambda x: (-x["max_severity"], -x["total_severity"]))
    md = ["# Adversarial Persona Review Queue\n",
          f"**Date:** {report['review_date']}\n",
          f"**Total pages reviewed:** {len(all_pages)}",
          f"**In review queue:** {len(queue)} ({verdicts.get('REVIEW',0)} REVIEW + {verdicts.get('REJECT',0)} REJECT)\n",
          "---\n"]
    for p in queue:
        md.append(f"## `{p['slug']}` — **{p['verdict']}** (total_sev={p['total_severity']}, max_sev={p['max_severity']})")
        md.append(f"**Suggested action:** {p['action'] or '(none)'}\n")
        md.append("**Persona concerns:**\n")
        for pid, pdata in sorted(p["personas"].items()):
            if pdata["concern"] or pdata["severity"] > 0:
                md.append(f"- `{pid}` sev{pdata['severity']}: {pdata['why']}")
        md.append("")
    (DEPLOY / "_ADVERSARIAL_REVIEW_QUEUE.md").write_text("\n".join(md), encoding="utf-8")
    print(f"Saved: _ADVERSARIAL_REVIEW_QUEUE.md ({len(queue)} pages)")

    # Pattern trends (suggested new legal_scan keywords)
    trends = {}
    for pid, examples in persona_concern_examples.items():
        keywords = Counter()
        for ex in examples:
            why = ex["why"].lower()
            words = re.findall(r"\b[a-z]{4,}\b", why)
            keywords.update(words)
        common = [(w, c) for w, c in keywords.most_common(10) if c >= 2]
        if common:
            trends[pid] = common
    (DEPLOY / "_ADVERSARIAL_PATTERN_TRENDS.json").write_text(
        json.dumps(trends, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Saved: _ADVERSARIAL_PATTERN_TRENDS.json")

    print(f"\n=== Next steps ===")
    print(f"  1. Andy + ich gehen _ADVERSARIAL_REVIEW_QUEUE.md durch")
    print(f"  2. Pro flagged Page: RENAME / EXTEND-DISCLAIMER / REMOVE entscheiden")
    print(f"  3. Apply fixes via Skript (rename/redirect/delete)")
    print(f"  4. Pattern-Generalisierung: trends → neue Regex in legal_scan_extended.py")
    print(f"  5. Zenodo V3 newversion mit gefixten Pages")


if __name__ == "__main__":
    main()
