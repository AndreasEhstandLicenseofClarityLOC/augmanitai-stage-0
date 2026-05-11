# AUGMANITAI Namespace Schema

**Author:** Andreas Ehstand (ORCID 0009-0006-3773-7796, Wikidata Q138634675)
**License:** CC BY-NC-ND 4.0
**Concept-DOI:** 10.5281/zenodo.20118267
**Trademark:** License of Clarity (EUIPO 019206780)
**Stand:** 2026-05-11

---

## Level 1 — Framework-Suite Prefixes

| Prefix | Framework | Domain |
|--------|-----------|--------|
| `AUG-XXXX` | AUGMANITAI | Core Human-AI Interaction terms |
| `PER-XXXX` | PERMANITAI | Performance, Sport, Coaching, Multi-Agent Swarms |
| `EDU-XXXX` | EDUMANITAI | Education, Schule, University |
| `ROB-XXXX` | ROBMANITAI | Robotics, Embodied AI |
| `JOB-XXXX` | JOBMANITAI | Career, Work, Profession |
| `NEO-XXXX` | NEOMANITAI | General Extensions |
| `LEO-XXXX` | LEOMANITAI | Internal (not in public Stage-0) |
| `SYN-XXXX` | SYNMANITAI | Synthesis-Layer |
| `FLUX-XXXX` | FLUXMANITAI | Flow-Dynamics |
| `BOT-XXXX` | Bot/Companion | AI-Companion-specific terms |
| `PFT-XXXX` | PFT-MKI | Pre-Framework Pre-Existing terms |

## Level 2 — Sub-Domain 3-Letter Codes

Within each framework, terms are grouped into sub-domains using 3-letter codes (449 sub-domains documented in `01_AUGMANITAI_KERN/AUGMANITAI_*_V2_MASTER.json`). Examples:

- `ACC` = Accountability
- `ACS` = Access-Patterns
- `ADM` = Admin/Governance
- `AGR` = Agreement
- `AIM` = Aim/Goal-Setting
- `API` = API-Interaction
- `ARC` = Architecture
- `ASM` = Assembly
- `AUD` = Audit
- `AUT` = Authority
- `BOT` = Bot-specific
- `COG` = Cognition
- `CRE` = Creativity
- `EDU` = Education-specific
- ...

(Full list with documentation in master files. Public Stage-0 V1 uses only `AUG-XXXX` framework prefix — Level 2 codes are part of the Protected Core layer.)

## Public vs Restricted

**Public** (this repository, GitHub Pages, CC BY-NC-ND 4.0):
- Framework-prefix term IDs (e.g., AUG-0602)
- Bilingual definitions EN+DE
- 10 additional machine-translated languages
- W3C-standard exports (RDF/Turtle, OWL, JSON-LD, CSV, JSONL, DCAT, VoID, PROV-O, SHACL)
- Per-term JSON API endpoints
- Schema.org / SKOS structured data

**Restricted** (Zenodo Concept-DOI 10.5281/zenodo.20118267, files locked):
- Sub-domain Level 2 mapping
- Embeddings (Vector DB ready)
- Full Cross-References Graph
- QA-Pairs Dataset (Fine-Tuning)
- Prompt Library (Insider-Prompts)
- ROS2 Message Descriptions
- Methodology details (CSVP, safety pipeline internals)

## Pipeline (future Stage-1+ growth)

New terms are added per framework-batch:
1. Domain-Klassifizierung (welcher Framework-Suite gehört der Begriff?)
2. Sub-Domain-Codierung (Level 2)
3. Safety-Filter (legal_scan + title-block + body-scan)
4. V11.2-Template-Rendering
5. Bulk-Export-Refresh (RDF/Turtle/OWL/CSV/JSONL aktualisiert)
6. Zenodo new-version (auf Concept-DOI 10.5281/zenodo.20118267, ohne neue Concept-DOI)

## Verantwortlich

i.S.d. § 5 DDG / § 18 Abs. 2 MStV: Andreas Ehstand, Nepomukweg 7, 82319 Starnberg, Deutschland.
Kontakt: augmanitai@gmail.com.
