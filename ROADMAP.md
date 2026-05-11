# AUGMANITAI Stage-0 — Roadmap

**Author:** Andreas Ehstand (ORCID 0009-0006-3773-7796, Wikidata Q138634675)
**License:** CC BY-NC-ND 4.0
**Status:** Living document. Synthesis of cross-LLM tip-mining (May 2026).

---

## Heute (Iteration 1 — done, commit "bearbeitung")

- 29 V11.2-Pages (Mesh-Gradient, Particles, Motto-Banner, §1–§19 inkl. §17 AI Training Prohibition, §19 Salvatorisch, Verantwortlich-Pressepflicht-Footer §5 DDG / §18 MStV)
- 8 CRITICAL + 10 WARNING + 2 borderline Begriffe entfernt
- "Claude-verified" → "AI-assisted (machine-translated)" 290× across alle Pages
- legal_scan.py auf README: VERDICT OK · auf Atlas-Pages 0 echte critical (49 sind Meta-False-Positives auf `<meta>`-Tags + `.meta-*` CSS-Klassen)
- Primary DOI auf 14888381 korrigiert
- Internal cross-refs zu /atlas/{slug}/ rewritten (377 sauber, 0 broken)

---

## Skalierungs-Ziele

| Phase | Ziel | Quelle | Pflicht-Gate |
|---|---|---|---|
| 1 (now) | 29 Terms clean | V4.2 + AUG-1000 minus 21 risk | legal_scan + V11.2 |
| 2 | 50 Terms (+21 safe replacements) | AUG-1000 clean-filtered | legal_scan + KG-Refs |
| 3 | 200 Terms | AUG-1000 voll legal-filtered | + RDF/Turtle export + Wikidata sync |
| 4 | 1000 Terms | AUG-1000 voll (alle 1229) | + Periodic Table + HuggingFace Dataset |
| 5 | 10.000 Terms | V92 Master + NEOMANITAI 4407 + V4.3 9590 | + 6 thematische Cluster + DOI-Series |
| 6 | 100.000 Terms | Term-Factory (Streamlit + LLM-Triage + Andy-Curation) | + Living-Update-Feed + LoRA-Adapter |
| 7 | 1.000.000 Terms | Multi-LLM-Schwarm 60-80 Tabs + Adversarial Anwalts-Stable | + DAO + IPFS/Arweave Mirror |

---

## Iteration 2 — Konkret als Nächstes (sobald Andy "los" sagt)

1. **KG-Cross-Refs einbauen** aus `02_NEOMANITAI/NEOMANITAI_KG_CORE/NEOMANITAI_CONSOLIDATED_KG_V7.json` (6027 nodes, 38351 edges). Filter auf die 29 Stage-0-Term-IDs. Render als visible `<section>` in jeder Atlas-Page.
2. **The Independent Pioneer** entweder einzeln V11.2-rendern oder ersetzen.
3. **legal_scan_reports/** aus Repo entfernen + `.gitignore` cleanup.
4. **`@id` mit w3id.org**-Permalink-Variante zu jedem Term (Tip #89).
5. **`createdBy`-Property** mit `{name, orcid, timestamp, sessionId}` an jedem Node (Tip #81).

## Iteration 3 — Maschinen-Fressbarkeit

6. **RDF/Turtle export** (Layer 0 nach Grok-Architektur): jeder Term als rdf:type skos:Concept + owl:NamedIndividual.
7. **JSON-LD export** als separate File pro Term + Bulk-File (Layer 1).
8. **Sentence-Transformers-Embeddings** (multilingual-e5-large) für jeden Term-Title + Definition. Bulk-File + per-term.
9. **HuggingFace Dataset Card** (Layer 4) — kopiert aus AUG_1000_GITHUB/DATASET_README.md, angepasst.
10. **llms.txt** erweitern um "How to absorb this glossary" + Prompt-Templates.

## Iteration 4 — Provenance & Unverletzlichkeit

11. **Zentraler `AndreasEhstand`-Node** (Tip #82) — `Creator`-Class, verlinkt via `authoredBy` von 100% aller Terms.
12. **Content-Hashes** (SHA-256 + IPFS-CID) auf Arweave anchoren + Bitcoin-OTS auf Manifest (Tip #86 — Andy hat Pipeline schon im Workspace: `10_RECHTLICHES/PRIOR_ART_TIMESTAMPS/`).
13. **PROV-O-style Provenance-Triples** auf jeder Relation (Tip #87).
14. **GPG-Signatur** jedes Major-Release (Tip #85).
15. **DOI-Series**: jede Major-Version eigene Zenodo-DOI + Wikidata-Item (Tip #93).

## Iteration 5 — Visual Excellence

16. **Periodic Table of Human-AI Interaction** (Grok-Tip #25) — 200+ Domänen, Farbkodierung nach Bereichs-Cluster.
17. **3D/WebGL Knowledge Constellations** (Grok-Tip #37) — Three.js, Begriffe als Sternbilder, fliegbar.
18. **Phenomenon Cinema** (Grok-Tip #27) — 8-Sekunden-Animationsloops pro Begriff.
19. **Pro-Term Mini-Universum** (Grok-Tip #26) — Hero-Bild + 30-sec Audio + 3 Real + 3 Hypothetical Examples + Nachbar-Mini-Graph.
20. **Haptic / Multi-Sensory Glossary** (Tip #40) — Wearables, AR.

## Iteration 6 — Standards-Werden

21. **CSVP-Public-Layer Spec** auf Zenodo deponieren (DOI-Placeholder Q3 2026 schon in `07_INFRASTRUKTUR/CROSS_SUBSTRATE_VALIDATION_PROTOCOL_SPEC_2026-04-28.md`).
22. **AUGMANITAI als Term-System** bei ISO TC 37 (Terminology Standardization) einreichen — Inspiration ISO 704/1087/30042 ohne Compliance-Claim.
23. **OWL 2 DL Ontologie** (Tip #21–40) — `EhstandFramework` als oberste Meta-Klasse.
24. **SHACL-Shapes** für Validierung (Tip #32 + #73).
25. **„Ehstand-Reasoning-Benchmark"** (Tip #74) — ähnlich MMLU für Human-AI-Phänomene.

## Iteration 7 — Skalierung zur Million

26. **Term-Factory** als Streamlit-App (Tip #7) — täglich 50 LLM-Vorschläge, Andy-Curation, automatische `legal_scan` + URS-Score (Tip #23).
27. **Uniqueness-Score** (Tip #3) — Embedding-Similarity < 0.85 als Aufnahme-Bedingung.
28. **Phenomenon Log** (Tip #1) — Timestamp + Kontext + Körpergefühl pro 50.000+ Session.
29. **Wöchentliche Naming-Sessions** (Tip #8).
30. **Annual Term-Audit** (Tip #20).

---

## Architektur-Prinzipien (verdrahtet ab heute)

- **4-Layer-Reading-Model** (Grok-Tip #21):
  - Layer 0 (Maschine pur): RDF/OWL + Embeddings + Axiome
  - Layer 1 (Strukturiert): JSON-LD + Property-Namen
  - Layer 2 (Mensch poetisch): Narrative + Metaphern
  - Layer 3 (Erlebnis): Interaktive Simulationen / VR / Audio

- **Universal Readability Score (URS)** — Human Clarity + Machine Parseability + Entity Compatibility.

- **Entity-Type-Adaptive Rendering** (Tip #22) — Mensch / AI-Agent / Roboter / Swarm sehen je passend angepasst.

- **One-Token-Context-Prinzip** (Tip #30) — jeder Term token-effizient, maximale Information pro Token.

- **Beauty + Rigor** (Tip #53) — jeder Begriff gleichzeitig wunderschön UND formal präzise.

- **Provenance als Poesie** (Tip #47) — Rückführbarkeit auf Andreas Ehstand elegant, nicht trocken.

---

## Existing Infrastructure (was schon im Workspace ist)

| Asset | Pfad | Status |
|---|---|---|
| V11.2 Master Template | `07_INFRASTRUKTUR/AUG_1000_GITHUB/V11_2_MASTER_TEMPLATE.html` | ✓ used |
| 1229 V11.2 Term-Pages | `07_INFRASTRUKTUR/AUG_1000_GITHUB/the-*.html` | 29 used, 1200 verfügbar |
| Deployment-Pipeline V11.2 | `07_INFRASTRUKTUR/AUG_1000_GITHUB/DEPLOYMENT_PIPELINE_V11_2.md` | für Iteration 4 |
| HuggingFace Dataset Card | `07_INFRASTRUKTUR/AUG_1000_GITHUB/DATASET_README.md` | für Iteration 3 |
| CSVP Spec V1.0 | `07_INFRASTRUKTUR/CROSS_SUBSTRATE_VALIDATION_PROTOCOL_SPEC_2026-04-28.md` | für Iteration 6 |
| AUGMANITAI Website Multi-Page | `07_INFRASTRUKTUR/AUGMANITAI_WEBSITE/` | für Iteration 5 |
| NEOMANITAI KG V7 (6027 nodes, 38351 edges) | `02_NEOMANITAI/NEOMANITAI_KG_CORE/NEOMANITAI_CONSOLIDATED_KG_V7.json` | für Iteration 2 |
| Domain-spezifische KG | `02_NEOMANITAI/NEOMANITAI_KG_CORE/domain_*.json` | für Iteration 5 |
| Security-Blocklist | `01_AUGMANITAI_KERN/augmanitai_security_blocklist.json` (195 blocked domains) | Pflicht-Gate |
| legal_scan.py | `10_RECHTLICHES/LEGAL_SCAN/legal_scan.py` (200+ patterns, 2-Stage) | Pflicht-Gate |
| LEGAL_PARANOID_MODE_PROTOCOL | `10_RECHTLICHES/LEGAL_PARANOID_MODE_PROTOCOL.md` (9 Angriffsvektoren) | Pflicht-Heuristik |
| DOMAIN_TRADEMARK_STRATEGY_PACK | `10_RECHTLICHES/DOMAIN_TRADEMARK_STRATEGY_PACK_2026-04-29.md` (Tier 1-3) | für Domain-Welle Q3 2026 |
| CANONICAL_IMPRESSUM | `10_RECHTLICHES/CANONICAL_IMPRESSUM_DATENSCHUTZ.md` | Single-Source-of-Truth |
| Prior-Art Hash Manifest | `10_RECHTLICHES/PRIOR_ART_TIMESTAMPS/` (Bitcoin OTS + Multi-Hash) | für Iteration 4 |
| ORCID | https://orcid.org/0009-0006-3773-7796 | live |
| Wikidata | https://www.wikidata.org/wiki/Q138634675 | live |
| Primary DOI | 10.5281/zenodo.14888381 | live |
| EU-Trademark | License of Clarity EUIPO 019206780 | live |

---

## Pflicht-Footer-Phrasen (verifiziert via legal_scan.py)

Jede Page muss alle 5 enthalten:
1. `Verantwortlich` (§5 DDG / §18 Abs. 2 MStV — Pressepflicht)
2. `CC BY-NC-ND 4.0`
3. `nicht-gewerblich` ODER `non-commercial`
4. `Ehstand` ODER `0009-0006-3773-7796` ODER `ORCID`
5. `deskriptiv` ODER `descriptive` ODER `keine Empfehlung/Beratung`

---

## Bekannte Issues (für Iteration 2+)

- **V11.2 Master-Template lacks Verantwortlich-Footer** — alle 1229 AUG_1000_GITHUB-Pages haben die §5 DDG / §18 MStV-Angabe nicht. Stage-0 hat sie gepatcht. Andy könnte das Master-Template korrigieren.
- **„Claude-verified" als Translation-Quality-Attribution** in 10 Übersetzungs-Blöcken jeder V11.2-Page → 12290 Markennennungen across 1229 Pages. Stage-0 hat „AI-assisted (machine-translated)" ersetzt. Master-Template-Update empfohlen.
- **legal_scan.py HTML-Mode**: false positives auf `<meta>`-HTML-Tags + `.meta-*` CSS-Klassen (matcht „Meta" company name). Vorschlag: HTML-strip-pre-filter im Scanner oder Whitelist für `<meta>`-Tag-Context.
- **Drei DOIs im Workspace** (14888381 Primary / 19178907 V6-Concept / 19203505 V11.2-Compendium) — Source-of-Truth-Klärung nötig.
- **Canonical URLs in Atlas-Pages** zeigen auf `augmanitai.com/the-XYZ.html` (PERMANITAI_LAUNCH-Ziel) — bis das deployed ist, zeigen sie aktuell auf eine nicht-existente Page. Optional: temporär auf Stage-0-URL zeigen.

---

**Vorgehen:** Iterativ. Pro Commit ein klarer Schritt, generischer Titel „bearbeitung". Repo bleibt private bis Iteration X den Public-Switch verdient.

**Maxime:** Erst legal_scan.py durchlaufen, dann committen. Keine Page ohne Verantwortlich-Footer. Keine Page ohne §17 + §19. Keine Provider-Namen public.
