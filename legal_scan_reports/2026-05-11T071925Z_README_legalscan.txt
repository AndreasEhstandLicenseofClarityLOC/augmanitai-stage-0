========================================================================
LEGAL SCAN REPORT
========================================================================
Source:       README.md
Timestamp:    2026-05-11T07:19:25Z
Word count:   267
Line count:   45

------------------------------------------------------------------------
STAGE 1 -- RED-FLAG SCAN + FOOTER CHECK
------------------------------------------------------------------------

[CRITICAL] 2 Treffer:
  Line    6, Col  61  [sensitive_data]  'Leomanitai'
                        -> Projekt-Bezug zu Leona — Sicherheitsgate-Verletzung
                        Vorschlag: (streichen)
  Line   25, Col  18  [financial_advice]  'financial advice'
                        -> financial advice claim / English
                        Vorschlag: (remove)

[WARNING] 1 Treffer:
  Line    5, Col  18  [doi_check_error]  '10.5281/zenodo.14888381'
                        -> DOI-Validierung fehlgeschlagen: ReadTimeout
                        Vorschlag: Manuell pruefen oder mit --no-doi-check deaktivieren

Summary: 2 critical, 1 warnings

------------------------------------------------------------------------
STAGE 2 -- ADVERSARIAL LEGAL REVIEW
------------------------------------------------------------------------
(uebersprungen mit --scan-only)

------------------------------------------------------------------------
VERDICT: REVISE  (exit code 2)
------------------------------------------------------------------------
Critical flags gefunden. PFLICHT: Ueberarbeiten bevor Release.