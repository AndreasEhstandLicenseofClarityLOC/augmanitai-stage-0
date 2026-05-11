# POE.COM WORKER PROMPTS — Copy-Paste Ready

**Setup:** Poe.com Pro (€20/mo) → 4-6 parallele Chats mit verschiedenen Models. Empfohlene Workers:

| Bot in Poe | Cost (Poe Pro) | Speed | Strength |
|---|---|---|---|
| **Qwen3-235B** | low | mittel | systematisches reasoning |
| **GLM-5** | low | schnell | agentisch + long-context |
| **Kimi K2** | low | mittel | kreative phänomenologie |
| **DeepSeek-V3.x** | low | mittel | präzise definitions |
| **Grok-4** | mittel | schnell | research-tiefe |
| **Gemini 2.5 Pro** | mittel | schnell | breit + verständlich |

**Workflow:**
1. Öffne 4-6 Poe-Tabs (je 1 Bot)
2. Paste MASTER_PROMPT (unten) als erste Nachricht in jedem Tab
3. Pro Iteration: paste BATCH_PROMPT mit gewünschter Kategorie
4. Output: Bot liefert JSONL → copy → speichern in `_worker_outputs/poe_<bot>_<timestamp>.jsonl`
5. Wenn 4-6 Outputs gesammelt: sag mir Bescheid → ich (Claude) intake'e via `_chief_intake.py`

---

## MASTER PROMPT (einmalig pro Tab als ERSTE Nachricht)

```
You are a precision terminology worker for an academic phenomenology corpus on human-AI interaction (AUGMANITAI Compendium).

Your job: generate NEW phenomenon names that do NOT yet exist in established literature.

STRICT OUTPUT FORMAT — JSONL ONLY (one JSON object per line, no markdown, no commentary):
{"english_name":"The Specific Phenomenon Name","definition_en":"Descriptive sentence ≥100 chars describing the observed phenomenon in human-AI interaction context.","category":"<the category>"}

STRICT CONTENT RULES (any violation = entire batch rejected by my quality gate):

NEVER include:
- mention of children, minors, kids, infants, toddlers, kindergarten
- physical or psychological violence, abuse, harassment, gaslighting, torture
- "how-to" instructions or imperative verbs at sentence start ("Use X", "Try Y", "Do Z")
- second-person addressing ("you should", "you must", "your brain", "Sie", "Du")
- medical/clinical advice, medication names, diagnosis claims
- military/weapon/dual-use terminology
- legal advice patterns ("you should sue", "this constitutes...")
- financial advice patterns ("invest in", "buy/sell")
- obscure jargon a motivated 15-year-old could not parse

WRITING STYLE:
- 3rd person descriptive ("The pattern occurs when...", "Observers note that...")
- Each definition ≥100 characters and ≤350 characters
- No "(Variant 2)" or "(v3)" suffixes in names
- No bullet lists in definitions — full sentences only

Confirm you understand by replying with exactly: "READY"
```

---

## BATCH PROMPT (pro Iteration)

Replace `[CATEGORY]` and `[N]`. Send to each tab separately. Each bot produces independent batch — diversifies output.

```
Generate [N] new phenomena in category [CATEGORY].

Output STRICTLY JSONL (no preamble, no markdown, no "Here are...").

[CATEGORY]
```

---

## CATEGORY POOLS (für rotierende Batches)

**Frontier-Domains (Andy's strategische Priorität):**
- `Swarm_Encounter` — Mensch begegnet Schwarm-AI
- `Multi_Agent_Emergence` — was entsteht wenn mehrere AIs koordinieren
- `Hybrid_Cognition` — Mensch + AI als kognitive Einheit
- `Embodied_AI_Interaction` — Roboter-Begegnung
- `Cross_Substrate_Phenomenology` — kognitive Phänomene unabhängig vom Substrat

**Established (Auffüllen):**
- `Cognitive_Shift`
- `Bridge_AI`
- `Vibe_Coding`
- `Temporal_AI`
- `Perception_AI`
- `Relational_AI`
- `Aging_AI`
- `Workplace`
- `Sports_AI`
- `Data_Science`
- `Translation_AI`

---

## WORKFLOW PRO TAG (Andy-Routine, 20-30 min)

**Morgens (5 min):**
1. LM Studio Server starten (DeepSeek lädt)
2. Poe öffnen → 4 Tabs (Qwen3, GLM-5, Kimi, Grok)
3. In jeden Tab: MASTER_PROMPT pasten
4. Warten auf "READY"

**Im Tagesverlauf (alle 1-2h):**
5. Pro Tab: BATCH_PROMPT pasten mit anderer Kategorie
6. Bot liefert JSONL (30-50 Terme)
7. Output kopieren → speichern als `_worker_outputs/poe_<bot>_<timestamp>.jsonl`

**Abends (10 min):**
8. Andy sagt zu Claude: "Intake bitte"
9. Claude liest alle worker outputs, durch Pre-Publish-Gate, Atlas-Update, Zenodo neue Version + Push

**Erwartete Tages-Output:**
- LM Studio: ~50-200 candidates (DeepSeek-R1 ist langsam wegen thinking)
- Poe (4 Tabs × 5 Batches × 30 Terme): ~600 candidates
- Gate-Filter (typ. 80-95% pass): **~500-700 neue Pages/Tag**

---

## TROUBLESHOOTING

**Bot ignoriert JSONL-Format / outputs prose:**
- Resend MASTER_PROMPT, dann nochmal BATCH_PROMPT
- Wenn anhaltend → Bot tauschen (kein Auto-Format-Follower)

**Bot outputs "I can't help with that":**
- Category zu sensibel → andere Kategorie
- Wenn anhaltend bei einer Kategorie → die ist auch durch unsere Filter geblockt

**Duplikate erkennen:**
- Intake-Skript checkt automatisch gegen existing atlas/

**Quality zu generic (lauter "The X Effect"):**
- BATCH_PROMPT erweitern: "Avoid generic 'X Effect' patterns. Be specific."

---

## SICHERHEIT

Poe-Account ist anonym oder normal? Wenn anonym (separate Email + VPN): voller Stealth-Mode laut Playbook. Wenn normal: aktivität ist Poe-intern sichtbar, aber Output landet bei dir / Claude → kein Public-Trace.
