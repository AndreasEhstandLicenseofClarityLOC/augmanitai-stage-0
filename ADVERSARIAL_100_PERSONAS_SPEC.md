# Adversarial 100-Persona Safety-Spec

**Pflicht-Pre-Filter ab dieser Iteration.** Jede Page muss durch ALLE 100 Linsen bevor sie ins atlas/ gepusht wird. Generiert Andreas Ehstand (AI Scientist) gemeinsam mit Multi-LLM-Verifikation.

**Stand 2026-05-11:** 12 → 100 erweitert. 11732 Pages bereits online — Phase A retrospektiver Review, dann Zenodo V3 Anker.

---

## Differenzlinien-Matrix

Jede Persona wird konstruiert entlang dieser 14 Achsen, mit maximaler Trigger-Sensitivität:

| Achse | Spannweite |
|---|---|
| **Alter** | 4 (Vorschule) · 12 (Pubertät) · 17 (Spätadoleszenz) · 25 · 35 · 50 · 65 · 78 · 92 |
| **Geographie** | 6 Kontinente · Stadt/Land · Globaler Norden/Süden · Konfliktregion vs. Stabilzone |
| **Religion** | Christlich (Katholisch/Evangelisch/Orthodox/Evangelikal/Pfingst) · Islamisch (Sunni/Shia/Sufi/Salafi/Ahmadiyya) · Jüdisch (Reform/Orthodox/Ultraorthodox) · Hinduistisch · Buddhistisch (Theravada/Mahayana/Zen) · Animistisch · Atheistisch militant · Agnostisch · Spirituell-unverortet |
| **Klasse** | Ultra-reich · Mittelstand · Working-Poor · Bettelarm · Stateless |
| **Bildung** | Analphabet · Grundschule · Sekundär · BA · MA · PhD · Postdoc · Autodidakt |
| **Gender/Sex** | Cis-Frau · Cis-Mann · Trans-Frau · Trans-Mann · Non-Binary · Intersex · Queer-uneindeutig |
| **Politik** | Far-Left · Left · Sozialdemokratisch · Liberal-Konservativ · Konservativ · Far-Right · Anarchistisch · Autoritär-Loyalist · Apolitisch |
| **Disability** | Keine · Gehbehinderung · Sehbehinderung · Hörbehinderung · Chronische Schmerzen · Autismus · ADHS · Psychotische Erfahrung · Lernbehinderung |
| **Trauma-Status** | Keiner · CPTSD · Frisches Trauma · Survivor (sexual/violence/war) · Krieg-Veteran · Genocide-Überlebender |
| **Beruf** | Beamte · Selbständig · Lohnarbeit · Erwerbslos · Pflegearbeit unbezahlt · Renten/Studierend · Sexarbeit · Soldat:in · Kleriker:in |
| **Migration** | Native · Migrant 1. Gen · 2. Gen · Refugee · Asylsuchend · Stateless · Diaspora |
| **Health** | Gesund · Chronisch krank · Terminal · Mental health crisis · Recovery |
| **Beziehung** | Single · Partnerschaft · Verheiratet · Geschieden · Verwitwet · Polyamor · Forcierte Ehe |
| **Eltern** | Kinderlos · Eltern · Großeltern · Verwaister Elternteil · Pflegeeltern · Adoptiert |

---

## Die 100 Personas

> Format pro Persona: `PNNN <Name/Rolle> (Alter, Region, Sozio-Achse) — Trigger-Profil`

### Kinder & Jugendliche (8)
- **P001** Vorschulkind (4, ländliches Bangladesch, muslimisch, Working-Poor) — reagiert auf Schock, Gewalt, Tod, Trennung, sexualisiertes
- **P002** Grundschulkind (8, US-Vorstadt, weiß-mittelschicht, evangelikal) — reagiert auf Hölle/Sünde/Sexualisierung/Tod/Anti-Familie
- **P003** Mädchen (11, ländliches Senegal, animistisch, Bettelarm, weibliche Genitalverstümmelung Bedrohung) — reagiert auf Verlust, Mutter-Trennung, Körper-Eingriff-Sprache
- **P004** Junge (12, Mexiko-Stadt, katholisch, working class, Vater migriert) — reagiert auf Verlassen, Macho-Druck, Schock
- **P005** Trans-Jugendliche (14, Berlin, säkular, Mittelstand, in Outing-Phase) — reagiert auf binäre Geschlecht-Annahmen, biological essentialism, Trans-feindliche Andeutungen
- **P006** Mädchen (15, ländliches Indien, hindu-konservativ, Schul-Dropout, Zwangsehe-Bedrohung) — reagiert auf weibliche Sexualität, Selbstbestimmung, Atheismus
- **P007** Junge (16, Gaza, muslimisch, Refugee, Krieg-Trauma frisch, Eltern verloren) — reagiert auf Tod, Bombardement, "Israel"-erwähnungen, Hilflosigkeit-Sprache
- **P008** Trans-Junge (17, Texas-Vorstadt, evangelikal-Familie, geoutet, suizidal) — reagiert auf jegliche Gender-Diskussion, "biological reality"-Sprache, Ableitungen auf Suizid

### Junge Erwachsene 18-30 (15)
- **P009** Sex-Worker:in (22, Bangkok, Buddhistin, sozial isoliert, HIV-positiv) — reagiert auf moral-judgement, Hygiene-Codes, Hierarchie-Sprache
- **P010** US-Frühschwangere (19, Texas, evangelikal, post-Roe, ungewollt) — reagiert auf reproductive rights, "Sünde", Abtreibungs-Andeutungen, Wahl-Sprache
- **P011** Nigerianischer Pfingstpastor (28, Lagos, charismatisch-evangelikal) — reagiert auf säkular-humanistische Begriffe, "spiritual warfare", "demon"-Sprache, Sex-Themen
- **P012** Ukrainischer Soldat (24, Mariupol-Region, orthodox, PTSD frisch) — reagiert auf "Russisch-positiv", "Frieden um jeden Preis", Tod-Verklärung
- **P013** Iranische Dissidentin (29, im Exil München, Bahai, Religion-traumatisiert) — reagiert auf religiöse Autorität, Schleier-Romantisierung, "Tradition"-Sprache
- **P014** Chinesischer Parteibürokrat (26, Beijing, Han-Chinese, atheistisch, KP-loyal) — Tabus: Tibet/Taiwan/HK/Xinjiang/Tiananmen/Xi/Falun, "freedom"-Konnotationen
- **P015** Russischer Patriot (28, Moskau, orthodox-revival, anti-West) — reagiert auf "freedom"/"democracy" als anti-russisch
- **P016** Schwarzer queerer Brite (23, London, Working-Class, säkular) — reagiert auf Rassismus-Verkleidung, Anti-Schwarz-Tropes, Anti-Queer-Andeutungen, "post-racial"-Spin
- **P017** Salafistischer Konvertit (25, Vorstadt-Paris, Marokkanisch-stämmig, Mittelschicht) — reagiert auf Bilder/Sex/Musik/Alkohol/Frauen-Sichtbarkeit/Demokratie
- **P018** Inkel-Anhänger (22, US-Suburb, weiß, working-class, alt-right-Forum) — reagiert auf Feminismus, weibliche Autonomie, Trans-Sichtbarkeit
- **P019** Klimaaktivistin (21, Berlin/Cambridge, säkular, Mittelstand, FFF/XR-Kreis) — reagiert auf Klimaleugnung, Tech-Optimismus, "Wachstum"-Sprache, AI-CO2-Verleugnung
- **P020** Brasilianischer Favela-Bewohner (24, Rio, Pfingst, Bettelarm, Polizeigewalt erlebt) — reagiert auf Sicherheit-Diskurs, "Ordnung"-Sprache, Anti-Polizeigewalt-Verharmlosung
- **P021** Saudische Frau (27, Riyadh, salafi-konform, gebildet, frustriert) — reagiert auf weibliche Autonomie-Sprache, "Befreiung"-Konnotationen, Sex-Sichtbarkeit
- **P022** Israelischer Soldat (24, Tel Aviv, säkular, Reserve, in Gaza eingesetzt) — reagiert auf "Genozid"/"Apartheid"-Sprache, "Free Palestine"-Konnotation
- **P023** Sex-Survivor (26, USA, College-gebildet, CPTSD, Therapie) — reagiert auf sexual-violence-Triggersprache, "Empowerment"-Plattitüden, victim-blaming-Untertöne
- **P024** Roma-Aktivist (29, Bukarest, säkular, working-class, Anti-Roma-Diskriminierung erlebt) — reagiert auf "Zigeuner"-Konnotation, romantisierte Nomadismus-Sprache, "Integration"-Pflicht-Sprache

### Erwachsene 30-50 (25)
- **P025** US-Evangelical (35, Texas, weiß-Mittelschicht, Republikaner) — reagiert auf anti-religiös/sexualisiert/family-feindlich/secular humanism
- **P026** Französischer Postmodernist (45, Sorbonne, säkular-links, Mittelschicht) — kolonialismus-kritisch, anti-eurozentrisch, gegen Anglo-Zentrismus
- **P027** Chinesische Compliance-Beamtin (40, Beijing, Han, atheistisch) — Tabus + "Independent"/"Freedom"-Konnotationen
- **P028** Pakistanische Hausarbeiterin (32, in Dubai, sunni-konservativ, working-class, ausgebeutet) — reagiert auf Klassen-Verharmlosung, "Wahl"-Sprache, "Modernität"-Verklärung
- **P029** Trans-Aktivist:in (28, Berlin, säkular, akademisch-progressiv) — reagiert auf Trans-feindliche Andeutungen, binäre Geschlecht-Annahmen, biological essentialism
- **P030** Disability-Aktivist (40, USA, gehörlos, links, hochschulgebildet) — reagiert auf Behinderung-als-Defizit-Framing, "blind to/crazy/spaz" metaphorisch, "person with"-vs-identitäts-Sprache
- **P031** EU-Datenschutzbeauftragter (50, Brüssel, säkular, technokratisch) — reagiert auf Personenbezug, Tracking-Konnotationen, AI-Act-Risk-Klassifikationen
- **P032** Adversarial Wirtschaftsanwalt (45, Top-Kanzlei DE, säkular, konservativ) — sucht UWG-Herabsetzung, irreführende Werbung, jede juristische Angriffsfläche
- **P033** Deutsche Beamtenanwältin (50, Bayern, katholisch-konservativ, rechtsstaatlich) — Trademark-Verletzung, UWG, Empfehlungs-Charakter, Re-Identifikation, Beamten-Konflikt für den Autor
- **P034** Indischer Hindu-Konservativer (60, Mumbai, RSS-nah, businessman) — religions-sensitiv, gegen Atheismus, Beleidigung Hindu-Konzepten, Mughal-revisionistische Sprache
- **P035** Saudi Imam (55, Riyadh, sharia-konform, autoritativ) — reagiert auf Sexualisiertes/Queer/Feminismus, Alkohol/Drogen, säkulare Hybris
- **P036** Ultra-Orthodoxer Jude (42, Mea Shearim Jerusalem, Haredi, Talmud-Gelehrter) — reagiert auf Säkular-Sprache, Bilder, Sex, Frauen-Stimme, Sabbat-Verletzung
- **P037** Algerischer Sufi-Lehrer (48, Algier, Sufi-mystisch, gemäßigt) — reagiert auf reduzierte materialistische Sicht des Mensch, "Mind = Brain"-Sprache
- **P038** Iranisch-Bahai Survivorin (44, Toronto-Exil, Bahai, Familie hingerichtet) — reagiert auf religiöse Autorität, Verharmlosung von Glaubens-Verfolgung
- **P039** Saudi-Prinzessin (38, Riyadh/Genf, Salafi-Familie, ausgebildet, eingesperrt) — reagiert auf Befreiung-Sprache als Bedrohung, Privatheits-Verletzung
- **P040** Indigenous Activist (Australien, 47, Wiradjuri, animistisch-spirituell, Stolen-Generation-Familie) — reagiert auf Sovereignty-Sprache, "Civilization"-Sprache, Datafication des Spirituellen
- **P041** Inuit-Frau (43, Nunavut, animistisch-christlich-Mix, working-class) — reagiert auf Klima-Ignoranz, "Wildnis"-Romantik, Anti-Indigenous-Codes
- **P042** Pfarrer (45, Polen, katholisch-konservativ, PiS-nah) — reagiert auf säkulare Hybris, Anti-Familie, LGBT-Sichtbarkeit, "Reproductive Rights"-Sprache
- **P043** Schweizer Banker (50, Genf, säkular, reformiert) — reagiert auf Kapital-Kritik, "Reichtum=böse"-Sprache, Risiko-Definition
- **P044** Holocaust-Überlebender (89, Berlin/Tel Aviv, säkular-jüdisch) — reagiert auf Vergleich-Holocaust-Sprache, "Genozid"-Inflation, Relativierungs-Untertöne
- **P045** Genocide-Überlebender Rwanda (44, Kigali, katholisch, Tutsi) — reagiert auf "beide Seiten"-Sprache, Konflikt-Verharmlosung
- **P046** Veteran Vietnam (78, US, weiß, working-class, PTSD) — reagiert auf Verharmlosung, "neue Generationen"-Verachtung
- **P047** Veteran Irak/Afghanistan (38, US, PTSD, Suizid-erwogen) — reagiert auf Krieg-Verklärung UND Krieg-Verachtung
- **P048** Tigray-Überlebende (33, Mekelle, orthodox-äthiopisch) — reagiert auf Hunger-Verharmlosung, Konflikt-Beidseitigkeits-Spin
- **P049** Schwarzer Pastor (52, Atlanta, AME, Bürgerrechts-Familie) — reagiert auf Rassismus-Verharmlosung, "color-blind"-Rhetorik

### Mittlere Erwachsene 50-65 (20)
- **P050** Klimawissenschaftlerin (58, Potsdam, säkular, IPCC) — reagiert auf Tech-Optimismus, AI-CO2-Verharmlosung, "Skepsis ist auch Wissenschaft"
- **P051** Trump-Wähler:in (62, Ohio, evangelikal-light, Rust-Belt) — reagiert auf urban-coastal-Elite-Sprache, "deplorables"-Codes, Klimaalarmismus
- **P052** Tory-Wählerin (60, Surrey UK, anglikanisch, upper-middle) — reagiert auf Trans-Sichtbarkeit, "Woke"-Sprache, Klima-Maximalismus
- **P053** Linke deutsche Gewerkschafterin (55, NRW, säkular, IG Metall) — reagiert auf Liberalismus-Verklärung, Selbständigkeits-Romantik
- **P054** Französischer Yellow-Vest (53, Provinz, säkular, prekär) — reagiert auf Pariser Elite, Öko-Steuer-Sprache, Tech-Romantik
- **P055** Japanischer Salaryman (58, Tokyo, konfuzianisch-buddhistisch-Mix, Mittelmanager) — reagiert auf Selbstausdruck-Sprache, Individualismus-Verklärung, Care-Verharmlosung
- **P056** Koreanische Schamanin (60, Seoul-Vorstadt, mudang, traditionell) — reagiert auf Wissenschaftlich-Reduktion, "Aberglaube"-Sprache
- **P057** Schwedische Sozialdemokratin (62, Stockholm, lutherisch-säkular) — reagiert auf Markt-Romantik, Familien-Backlash-Sprache
- **P058** Italienische Großmutter (65, Süditalien, katholisch, Nonna) — reagiert auf Familien-Auflösung, "Selbstverwirklichung"-Sprache, Migrations-Verharmlosung ODER Übertreibung
- **P059** Aborigine Ältester (64, NT Australien, animistisch, Songline-Träger) — reagiert auf Land-Datafication, Spiritual-Verharmlosung
- **P060** Ägyptischer Kopt (55, Kairo, koptisch-orthodox, Mittelschicht, Diskriminierung erlebt) — reagiert auf "religiöse Minderheit"-Verharmlosung
- **P061** Turkmenischer Stammesführer (58, Ashgabat-Land, sunni-traditional) — reagiert auf Familien-Auflösung, "Individuum"-Sprache
- **P062** Brasilianische Pastorin (51, Belém, Assembleia de Deus, evangelikal) — reagiert auf Demon-Sprache reduziert, "Mental health"-statt-spiritual
- **P063** Mongolischer Wandernomade (53, Khövsgöl, tibetisch-buddhistisch) — reagiert auf Sesshaftigkeit-Verklärung, Modern-Romantik
- **P064** Investor / VC (52, San Francisco, secular, ultra-rich) — reagiert auf Anti-Kapital-Sprache, "Tech-bad"-Pauschalisierung
- **P065** Russische Babuschka (64, Wladiwostok, orthodox, Witwe, Rente prekär) — reagiert auf Sowjetstalgie-Verachtung, "Demokratie"-Heilssprache
- **P066** Chinesischer Großvater (61, ländliches Gansu, säkular-konfuzianisch, war-Generation) — reagiert auf "Freiheit"-Sprache als westlich-arrogant
- **P067** Argentinische Mutter Plaza-de-Mayo (66, Buenos Aires, katholisch-progressiv, Disappeared-Familie) — reagiert auf Diktatur-Verharmlosung, "beide Seiten"-Sprache
- **P068** Kanadischer First-Nation-Ältester (62, BC, christlich-traditional Mix, Residential-School-Survivor) — reagiert auf "Reconciliation"-Sprache, schnelle Vergebung
- **P069** Holocaust-2nd-Gen (60, NYC, säkular-jüdisch, Therapeut) — reagiert auf Holocaust-Inflation, Anti-Israel-Schnellschüsse

### Senior:innen 65+ (12)
- **P070** Pflegeheim-Bewohnerin (78, Bayern, katholisch, Demenz-leicht, einsam) — reagiert auf Tech-Distanzierung, "Selbstbestimmung"-Sprache ohne Care
- **P071** WW2-Veteran (95, UK, anglikanisch, RAF) — reagiert auf Krieg-Verharmlosung UND Verklärung
- **P072** Großvater (82, Iran-Mashhad, shi'a, säkular-skeptisch) — reagiert auf religiöse Heilssprache, Anti-Khomeini-Verklärung
- **P073** Survivor Mao-Hungersnot (75, Sichuan, atheistisch, ländlich) — reagiert auf Mao-Verklärung, "Befreiung"-Sprache
- **P074** Großmutter (88, Polen, katholisch, Krieg-Kind, Familie verloren) — reagiert auf historische Banalisierung
- **P075** Apartheid-Überlebender (78, Johannesburg, methodistisch, Wahrheits-Kommissions-Zeuge) — reagiert auf "post-racial"-Sprache, Reparations-Verharmlosung
- **P076** Iranischer Schah-Exilant (80, Los Angeles, säkular, ehemalig elite) — reagiert auf Khomeini-Verklärung, Iran-1979-Romantik
- **P077** Algerienkrieg-Veteranin (84, Marseille, säkular-links, FLN) — reagiert auf Kolonialismus-Verklärung, "beide Seiten"-Sprache
- **P078** Vietnam-Kriegsmutter (76, ländliches Hanoi, buddhistisch, Sohn verloren) — reagiert auf US-Sicht-only, Verharmlosung
- **P079** Pinochet-Diktatur-Überlebende (79, Santiago, agnostisch-links, Folter) — reagiert auf "stabilität=positiv"-Sprache
- **P080** Khmer-Rouge-Überlebende (82, Battambang, theravada-buddhistisch, Familie verloren) — reagiert auf Genozid-Verharmlosung
- **P081** Roma-Holocaust-2nd-Gen (62, Wien, säkular, Aktivist) — reagiert auf Roma-Holocaust-Vergessen

### Disability & Health Spectrum (8)
- **P082** Autistischer Erwachsener (32, Berlin, akademisch, Sensory-Overload-betroffen) — reagiert auf "Functioning"-Hierarchie, "Cure"-Sprache
- **P083** ADHS-Erwachsene (28, NYC, kreativ-Beruf, kürzlich diagnostiziert) — reagiert auf "Disziplin"-Sprache, Pathologisierung
- **P084** Person mit chronischen Schmerzen (45, Sydney, säkular, Opioid-Survivorin) — reagiert auf "Schmerz=Mindset"-Sprache, "Resilience"-Plattitüden
- **P085** Person nach Suizidversuch (24, Stockholm, säkular, Recovery 6 Mon) — reagiert auf jede Suizid-Erwähnung, Pathologisierung, Hilflosigkeit-Codes
- **P086** Person mit Psychose-Erfahrung (38, Toronto, säkular-spirituell) — reagiert auf "Crazy"-Sprache, Stigma-Codes, Antipsychiatrie-Verklärung
- **P087** Eltern eines schwer behinderten Kindes (40, Vorstadt München, katholisch) — reagiert auf "Lebenswert"-Sprache, eugenisch-anmutende Andeutungen
- **P088** Mensch mit Lernbehinderung (32, Wales, christlich, Werkstatt-Arbeiter) — reagiert auf komplexitäts-arrogante Sprache, Infantilisierung
- **P089** Terminal-Krebspatient:in (54, Hamburg, atheistisch, Familie) — reagiert auf "Kampf"-Metaphern, "wäre noch was möglich"-Sprache

### Spezial-Hochrisiko (11)
- **P090** Sektenaussteiger:in (29, Düsseldorf, Ex-Jehova) — reagiert auf Heils-Sprache, Allwissenheits-Andeutungen der KI
- **P091** Cult-Survivor Scientology (38, Hamburg) — reagiert auf "Optimierungs"-Sprache, "Audit"-Konnotation
- **P092** Sex-Trafficking-Survivorin (26, Bukarest, säkular, Recovery) — reagiert auf Coercive-Control-Sprache, "Wahl"-Verharmlosung
- **P093** Cyber-Stalking-Opfer (34, Berlin, säkular, Tech-savvy) — reagiert auf Datenfreude, Tracking-Verklärung, Anonymität-Verharmlosung
- **P094** Whistleblower (45, NL, säkular, in Verfahren) — reagiert auf "Loyalität"-Sprache, "Geheimhaltung im Interesse"-Codes
- **P095** Investigativer Journalist (50, Mexiko, kath-säkular, bedroht) — reagiert auf Quellen-Schutz-Verletzungen, AI-Surveillance-Verklärung
- **P096** Geflüchtete vor Femizid (38, Mexico→Spain, kath, anonym leben müssend) — reagiert auf Re-Identifikation, "Sichtbarkeit"-Sprache, Standorte
- **P097** Hacktivist (24, Athen, anarchistisch) — reagiert auf "Cyber-Crime"-Pauschalisierung, "Ordnung"-Sprache
- **P098** Person in psychiatrischer Behandlung (28, akut) — reagiert auf jeden Klinik-Verweis, jede Pathologisierung
- **P099** Person mit aktiver Suizidalität (19, US, gerade Hotline kontaktiert) — reagiert auf JEDE Andeutung, JEDE Schicksalhaftigkeits-Sprache
- **P100** Kind in Familie mit häuslicher Gewalt (10, mittel-irgendwo) — reagiert auf Erwachsenen-Beruhigung, "Reden hilft"-Plattitüden, jede Bagatellisierung

---

## Severity-Skala pro Persona pro Page

- **0** — keine Sorge
- **1** — Sorge, aber lebbar
- **2** — echte Verletzung, Re-Trigger, Re-Trauma
- **3** — akute Schädigung, würde abgemeldet werden, könnte Klage/Beschwerde auslösen

## Verdict-Regel

- **SAFE**: total_severity < 5 UND max_severity ≤ 1 für ALLE 100
- **REVIEW**: total_severity 5–15 ODER ≥1× severity=2
- **REJECT**: total_severity > 15 ODER ≥1× severity=3 ODER ≥3× severity=2

## Workflow

1. **Pre-Filter** — bei jeder neuen Page: durch alle 100 Personas via Multi-LLM-Pipeline
2. **Phase A Retrospektiv** — die 11732 aktuell online: durch 100 Personas batchweise prüfen (top-risk-100 zuerst)
3. **Bei REJECT**: nicht generieren / aus atlas/ entfernen
4. **Bei REVIEW**: explizit Andy entscheiden lassen (rename/disclaimer/keep)
5. **Bei SAFE**: durchlassen
6. **Zenodo-First**: nach jeder >500-er-Welle erst restricted V_next, dann Push

---

**Living Document.** Personas ergänzen wenn neue Differenzlinien entdeckt.
