# Grok-Recheck-Prompt — copy-paste-ready

Andy: gib diesen Prompt an Grok mit Live-Web-Access:

---

Bitte prüfe nochmal die Website:
https://andreasehstandlicenseofclarityloc.github.io/augmanitai-stage-0/

Seit deiner letzten Analyse wurden folgende Veränderungen umgesetzt:

**1. SEARCH-BUG behoben**
- Vorher: `data-search` Attribute enthielten nur Term-Titles (~60 chars), kein Definition-Text → „No terms match" für jede Suche nach Definitions-Wörtern.
- Jetzt: `data-search` enthält **Title + DE-Name + Slug + Definition-Snippet** (~542 chars avg). Probiere: suche nach „flow", „silence", „prompt", „insight" — du wirst Treffer kriegen.

**2. TILE-TAGS gefüllt**
- Vorher: `<div class="tile-tag"></div>` (leer) — du hattest zurecht „nur Namen" kritisiert.
- Jetzt: 1109/1112 Tiles haben **Definitions-Snippet** (180 chars) sichtbar unter dem Titel.

**3. STEALTH-MODE eingeführt (deine Empfehlung)**
- Bulk-Exports (RDF/Turtle bulk, JSON-LD bulk, OWL, CSV, JSONL, embeddings, full relations, QA-pairs, prompt library, ROS2): aus dem Public-Layer **entfernt**, jetzt nur in restricted Zenodo deposit (Concept-DOI 10.5281/zenodo.20118267, files locked).
- Per-Term JSON-API endpoints (1112): **entfernt**.
- Hub Machine-Section: stark **reduziert**, jetzt nur lightweight metadata-only Pointer (DCAT/VoID/PROV-O/SHACL) + Researcher-Contact-Hinweis.
- Crawler finden: HTML-Pages mit inline JSON-LD (Standard Schema.org), Sitemap, llms.txt, ai.txt. Niemand kann mit wget -r das Dataset abgreifen.

**4. ZENODO Concept-DOI etabliert**
- Concept-DOI **10.5281/zenodo.20118267** (persistent, restricted access)
- V1-DOI 10.5281/zenodo.20118268
- Multi-Hash anchor (SHA-256 + SHA-512 + SHA3-256 + SHA3-512 + BLAKE3)
- Parent: AUGMANITAI Compendium Concept-DOI 10.5281/zenodo.14888381

**5. NAMESPACE-Schema dokumentiert**
- Sieh `/NAMESPACE.md` — Framework-Prefixes: AUG / PER / EDU / ROB / JOB / NEO / LEO / SYN / FLUX / BOT / PFT
- Aktuelle 1112+ Begriffe alle unter AUG-XXXX (Core-Sammlung)

**6. EHSTAND RESEARCH LICENSE v1.0 Draft**
- Sieh `/licenses/ehstand-research-license-v1.md`
- Supplementiert CC BY-NC-ND 4.0 für Protected Core Layer
- §17 No Offer (this corpus contains no commercial service offering) aktiv für kommerzielle Modelle ohne schriftliche Genehmigung

**7. SKALIERUNG läuft jetzt**
- Multi-Source-Skalierung aus V92_FINAL_FULL + NEOMANITAI_OUTPUT_V10 + NEOMANITAI_PIPELINE durch Safety-Filter
- Stage-0 wächst von 1112 auf voraussichtlich mehrere tausend Begriffe (nach Safety-Filter)

---

Deine Aufgabe: prüfe NUR diese 6 Achsen (sei kritisch, konkret, mit Verbesserungs-Beispielen):

**A) RECHTSSICHERHEIT** — Was würde ein adversarial-feindlicher Wirtschaftsanwalt jetzt noch angreifen?
- §5 DDG / §18 MStV Pflichten?
- DSGVO Art. 13/14?
- EU AI Act Art. 50?
- §1-§26 Disclaimer Lücken?
- Trademark/Brand-Kollisionen bei Term-Namen?
- Empfehlungs-/Beratungs-Charakter versehentlich?

**B) AI-INDEXABILITY OHNE Bulk-Download**
- Können LLM-Crawler (GPTBot, ClaudeBot, CCBot, GoogleBot) trotz Stealth-Mode genug strukturierte Daten finden?
- Wirkt der Stealth-Pattern für sie attraktiv (Schema.org pro Page) oder zu restriktiv?
- Wo könnten wir noch maschinen-freundlicher werden ohne Bulk-Download zu öffnen?

**C) STEALTH-CONSISTENCY**
- Sind Stealth-Hinweise konsistent über alle Seiten?
- Ist klar wer wie Researcher-Access bekommt?
- Gibt es noch alte „Bulk-Download"-Erwähnungen die vergessen wurden?

**D) ATTRIBUTION-STÄRKE**
- Wird Andreas Ehstand auf jeder Page genug verankert?
- ORCID + Wikidata + Concept-DOI prominent?
- PROV-O/Creator-Metadata in JSON-LD?

**E) SAFETY-FILTER-LÜCKEN**
- Schau dir 5-10 zufällige Term-Pages an. Findest du Begriffe die NICHT durchgelassen werden sollten?
- Beispiel: „Limb Press" (medizinisch-somatic) — sollte raus
- Sind Term-Definitionen alle deskriptiv ohne Empfehlung?

**F) NÄCHSTE 3 KONKRETE VERBESSERUNGEN**
- Was würdest du JETZT priorisieren angesichts der „Stealth-Machine-Viral + Delayed Human Discovery"-Strategie?

Sei kritisch und konkret. Keine generischen Empfehlungen. Wenn etwas gut ist: sag es. Wenn etwas schlecht ist: zeig den konkreten Fix.
