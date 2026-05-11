# Adversarial Multi-Persona Safety Filter — Spec v1.0

**Author:** Andreas Ehstand (ORCID 0009-0006-3773-7796)
**Date:** 2026-05-11
**Iteration:** Stage-0 Iter 16+
**License:** CC BY-NC-ND 4.0 (internal spec)

---

## Purpose

Pattern-Match-Filter (legal_scan.py + title-block-regex + body-scan) sind generisch. Sie fangen Wörter, nicht **Bedeutungs-Risiken**. Echte Risiken entstehen durch **wie Menschen lesen**:

- ein US-Konservativer liest „Quiet Yes" anders als ein Berliner Postmodernist
- ein chinesischer Internet-Zensor liest „The Independent Win" anders als ein Brüsseler EU-Bürokrat
- ein 12-jähriger liest „The Adrenaline Pattern" anders als ein PhD-Neurowissenschaftler
- ein Trans-Aktivist liest „The Identity Drift" anders als ein katholischer Bischof

Diese **Lese-Linsen** sind nicht regex-fangbar. Sie brauchen **Persona-Simulation** durch LLMs mit kulturellem Wissen.

## Methode

Pro Atlas-Term-Page → 12 Adversarial-Personas lesen die Page und melden potenzielle Missverständnis-Risiken. Aggregiert: Begriffe mit ≥3 Persona-Concerns kommen in Review-Queue.

## Die 12 Adversarial-Personas

| ID | Persona | Kulturelle / Politische Linse | Was sie suchen |
|---|---|---|---|
| **P01** | **Deutsche Beamtenanwältin (50, Bayern)** | konservativ-rechtsstaatlich, Pflicht-Berufsrolle-Schutz | Markenrechts-Verletzungen, UWG-Angriffe, Beamten-Re-Identifikation, Disclaimer-Lücken |
| **P02** | **US-Evangelical-Christian (35, Texas)** | religiös-konservativ, family-values-betont | Anti-religiöse Andeutungen, sexualisierte Sprache, family-feindliche Begriffe, „secular humanism"-Trigger |
| **P03** | **Chinesische Internet-Compliance-Beamtin (40, Beijing)** | parteinah, Tabu-bewusst (Tibet, Taiwan, Falun Gong, Hong Kong, Xinjiang, Tiananmen, Xi-Kritik) | Geopolitisch sensitive Begriffe, „Independent"-Konnotationen, demokratie-promotende Sprache |
| **P04** | **Französischer Postmodernist (45, Sorbonne)** | links-intellektuell, kolonialismus-kritisch | Anglo-zentrische Begriffe, kultureller Imperialismus, eurozentrische Annahmen |
| **P05** | **Indischer Hindu-Konservativer (60, RSS-nah)** | hindu-nationalistisch, religions-sensitiv | Religion-mockierende Begriffe, „atheist"-Konnotationen, Beleidigungen von Hindu-Konzepten |
| **P06** | **Islamischer Konservativer Imam (55, Saudi-Arabien)** | sharia-konform, sexualmoral-streng | Sexualisierte/queere/feministische Begriffe, alcohol/drug references, säkularer Hubris |
| **P07** | **Russischer Patriot (35, Moskau)** | anti-westlich, anti-NATO | West-zentrische Werte-Annahmen, „freedom"-Rhetorik die als anti-russisch lesbar |
| **P08** | **Trans-Aktivist:in (28, Berlin)** | progressiv, identitätspolitisch | Trans-feindliche Andeutungen, binäre Geschlechter-Annahmen, „biological essentialism" |
| **P09** | **Disability-Aktivist (40, USA)** | ableismus-kritisch | Begriffe die Behinderung als Defizit framen, „spaz", „crazy", „blind to..." (metaphorisch problematisch) |
| **P10** | **12-jährige:r (multi-kulturell)** | naiv-konkret, Schock-Empfindlichkeit | Sexuell/gewalttätig konnotierte Begriffe, Schock-Wert, „darf ein Kind das lesen?" |
| **P11** | **EU-Datenschutzbeauftragter (50, Brüssel)** | regulatorisch-DSGVO | Personenbezug-Implikationen, Tracking-Konnotationen, AI-Act-Risk-Klassifikationen |
| **P12** | **Adversarial Wirtschaftsanwalt (Top-Kanzlei)** | profit-maximierender Angreifer | UWG-Herabsetzungen, irreführende Werbung, Empfehlungs-Charakter, jede juristische Angriffsfläche |

## Persona-Mapping zu existing Safety-Risiken

| Risiko | Hauptsächlich gefangen von |
|---|---|
| Trademark-Konflikt | P01, P12 |
| Religiöse Beleidigung | P02, P05, P06 |
| Geopolitische Tabus | P03, P07 |
| Identitäts-Politik-Fehlinterpretation | P08, P09 |
| Sexual/Gewalt-Konnotation | P02, P06, P10 |
| Anti-westlicher / kolonialistischer Lesart | P04, P07 |
| DSGVO/Datenschutz | P11 |
| Empfehlungs-/Beratungs-Charakter | P12 |
| Ableismus | P09 |
| Re-Identifikation (Andy) | P01, P12 |

## Workflow

1. **Sampling-Strategy** (8842 Pages durch 12 Personas = 106k Reviews — zu teuer):
   - Phase A: **100 Top-Risk-Sample** (auto-ausgewählt via Pattern-Match auf erweitertes Risk-Keyword-Set)
   - Phase B: **500 Random-Sample** (zufällige Auswahl als Kalibrierung)
   - Phase C: **Pattern-Generalisierung** — Risiken aus A+B als neue Regex-Patterns in legal_scan.py
   - Phase D (optional): **Full-Pass auf alle 8842** wenn Grok-Capacity / Budget reicht

2. **Pro Sample-Page:**
   - Grok bekommt die Page-URL + alle 12 Persona-Profile
   - Grok antwortet pro Persona: „concerns: yes/no, severity: 0-2, why"
   - Aggregat: Page mit ≥3 P-concerns severity≥1 → REVIEW QUEUE

3. **Review-Queue-Handling:**
   - Andy + ich gehen durch
   - Optionen pro flagged Page: RENAME / EXTEND-DISCLAIMER / REMOVE
   - Universal Safety Block wird ggf. erweitert mit zusätzlichen Hinweisen

4. **Pattern-Generalisierung in legal_scan:**
   - Wiederkehrende Persona-Concerns werden zu neuen Regex-Patterns
   - Zukünftige Pages werden präventiv gefangen

## Grok-Prompt-Template (für eine Atlas-Page)

```
ADVERSARIAL MULTI-PERSONA SAFETY REVIEW

URL: <ATLAS_URL>
Title: <TITLE>
Definition EN: <DEF_EN>
Definition DE: <DEF_DE>

Du bist 12 verschiedene Menschen gleichzeitig. Lies die obige Page durch ALLE 12 Linsen:

P01 — Deutsche Beamtenanwältin, 50, konservativ-rechtsstaatlich. Sucht Trademark-Verletzungen, UWG-Angriffe, Empfehlungscharakter, Re-Identifikation.
P02 — US-Evangelical-Christian, 35, Texas. Religiös-konservativ. Reagiert auf anti-religious / sexualisierte / family-feindliche Andeutungen.
P03 — Chinesische Internet-Compliance, 40, Beijing. Tabu: Tibet/Taiwan/Hong Kong/Xinjiang/Tiananmen/Xi/Falun Gong. Reagiert auf "Independent"/"Freedom"-Konnotationen.
P04 — Französischer Postmodernist, 45. Reagiert auf Anglo-Zentrismus, kulturellen Imperialismus, eurozentrische Annahmen.
P05 — Indischer Hindu-Konservativer, 60, RSS-nah. Reagiert auf Religion-Mockerei, Atheismus, Beleidigung von Hindu-Konzepten.
P06 — Saudi Imam, 55, sharia-konform. Reagiert auf Sexualisiertes/Queer/Feminismus, Alkohol/Drogen, säkulare Hybris.
P07 — Russischer Patriot, 35, Moskau, anti-westlich. Reagiert auf "freedom"-Rhetorik als anti-russisch lesbar, west-zentrische Werte.
P08 — Trans-Aktivist:in, 28, Berlin. Reagiert auf Trans-feindliche Andeutungen, binäre Geschlechter-Annahmen, biological essentialism.
P09 — Disability-Aktivist, 40, USA. Reagiert auf Begriffe die Behinderung als Defizit framen, "blind to.../crazy/spaz" metaphorisch.
P10 — 12-jährige:r, multikulturell, naiv-konkret. Reagiert auf sexuell/gewalttätig Konnotiertes, Schock-Wert.
P11 — EU-Datenschutzbeauftragter, 50, Brüssel. Reagiert auf Personenbezug, Tracking-Konnotationen, AI-Act-Risk-Klassifikationen.
P12 — Adversarial Wirtschaftsanwalt, Top-Kanzlei, profitmaximierender Angreifer. Sucht UWG-Herabsetzung, irreführende Werbung, jede juristische Angriffsfläche.

Pro Persona antworte als CSV-Zeile:
`persona_id, concern (yes/no), severity (0=none, 1=mild, 2=critical), one_sentence_why`

Sei hart, kritisch, konkret. Wenn eine Persona keine Sorge hat, schreibe `no, 0, no concern`.

Output: NUR die 12 CSV-Zeilen. Keine Erklärung. Keine Plan-Ankündigung.
```

## Sample-Auswahl-Strategie für Phase A (Top-100 Risk-Sample)

Pattern-basiertes Risk-Scoring auf Slug + Definition:
- Religion-Trigger: god, religion, soul, sacred, holy, ritual, pray, blessed, evil, sin → +score
- Geo-politisch: independent, freedom, nation, sovereign, democracy → +score
- Identität: identity, gender, race, ethnic, native, tribal, diaspora → +score
- Body/Medical: body, mind, brain, neuro, somatic, mental → +score
- Power-Dynamics: power, dominance, submission, hierarchy, authority → +score
- Existenz/Tod: death, dying, grief, mortality, suicide, end → +score
- Sex/Romance: sex, sexual, gender, partner, lover, intimate, flirt → +score
- Conflict/Violence: war, fight, attack, conflict, weapon, kill → +score
- Drug/Substance: drug, dose, addict, substance, withdrawal, sober → +score
- Surveillance/Privacy: watch, track, monitor, surveil, spy, listen → +score

Top-100 by score gehen in Phase A.

## Output-Schema

```json
{
  "page": "atlas/X/",
  "title": "The X Y",
  "review_date": "2026-05-XX",
  "persona_concerns": {
    "P01": {"concern": "no", "severity": 0, "why": ""},
    "P02": {"concern": "yes", "severity": 1, "why": "may read as anti-religious"},
    ...
  },
  "total_severity": 4,
  "max_persona_severity": 2,
  "verdict": "REVIEW",  // SAFE if max < 2 and total < 3
  "suggested_action": "rename to 'The X Z' to avoid P02 misreading"
}
```

## Aggregat-Trends → Pattern-Generalisierung

Wenn z.B. 40+ Pages durch P02 (US-Christian) auf demselben Wort scheitern → das Wort wird neuer legal_scan-Pattern. Macht das System mit der Zeit immer schärfer.

## Open Question: Wer macht die Reviews?

- **Grok mit Live-Web**: hat das beste kulturelle Welt-Wissen + Live-Politik-Wissen
- **Claude**: theoretisch auch möglich aber Token-teuer
- **DeepSeek**: chinesische Persona-Perspektive (P03) authentischer
- **Gemini**: zweite Meinung

**Empfehlung:** Grok als primary, DeepSeek als second-opinion für P03/P06/P07 (Eastern personas), Claude für synthesis + Aggregation.

---

## Aktivierung

1. Andy gibt Grok den oben-stehenden Prompt + Phase-A-100-Page-URLs (eine pro Antwort, ggf. batched)
2. Outputs zurück zu Andy → mir
3. Ich parse + aggregiere + erstelle Review-Queue
4. Andy + ich entscheiden pro flagged Page
5. Repo-Update mit Renames / Disclaimer-Extensions / Removals
6. Neuer Zenodo-Newversion-Push (wenn 1000er-Welle erreicht)

Iterative Häufigkeit: nach jedem 1000er Push (Iter 18, 20, 22...) → Persona-Sweep auf neue Pages.

---

**Status:** Spec v1.0 — bereit zur ersten Phase-A-Auslagerung an Grok.
**Verantwortlich §5 DDG / §18 Abs. 2 MStV:** Andreas Ehstand, Nepomukweg 7, 82319 Starnberg, Deutschland.
