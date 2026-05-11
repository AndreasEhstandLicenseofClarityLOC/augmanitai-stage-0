#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V5 resume upload with retry-on-connection-abort."""
import os, sys, json, time, datetime, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

TOKEN = os.environ["ZENODO_TOKEN"]
H = {"Authorization": f"Bearer {TOKEN}"}
HJ = {**H, "Content-Type": "application/json"}
DRAFT_ID = "20124125"
DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")
ATLAS = DEPLOY / "atlas"
TODAY = datetime.date.today().isoformat()
NOW_UTC = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

ready = json.loads((DEPLOY / "_ITER41_BUNDLE_V5_READY.json").read_text(encoding="utf-8"))
BUNDLE = Path(ready["bundle_path"])
HASHES = ready["hashes"]

# Robust session
s = requests.Session()
retry = Retry(total=5, backoff_factor=2, status_forcelist=[500, 502, 503, 504])
s.mount("https://", HTTPAdapter(max_retries=retry))

# Get bucket
print("[1/4] Fetching draft...")
r = s.get(f"https://zenodo.org/api/deposit/depositions/{DRAFT_ID}", headers=H, timeout=120)
draft = r.json()
bucket = draft["links"]["bucket"]
print(f"  bucket: {bucket}")

# Clean any partial old files
for f in draft.get("files", []):
    s.delete(f"https://zenodo.org/api/deposit/depositions/{DRAFT_ID}/files/{f['id']}", headers=H, timeout=60)
    print(f"  removed: {f.get('filename')}")

# Upload with retry on connection abort
print(f"\n[2/4] Upload {BUNDLE.name} ({BUNDLE.stat().st_size/1024/1024:.1f} MB)...")
for attempt in range(5):
    try:
        with open(BUNDLE, "rb") as f:
            r = s.put(f"{bucket}/{BUNDLE.name}", headers=H, data=f, timeout=(60, 1800))
        if r.status_code in (200, 201):
            print(f"  ✓ uploaded · checksum={r.json().get('checksum')}")
            break
        else:
            print(f"  attempt {attempt+1}: status {r.status_code} — retry")
    except Exception as e:
        print(f"  attempt {attempt+1}: {type(e).__name__} — retry in 15s")
        time.sleep(15)
else:
    print("  FAIL — could not upload after 5 attempts")
    sys.exit(1)

# Metadata
ATLAS_COUNT = sum(1 for d in ATLAS.iterdir() if d.is_dir())
desc = (
    f"<p><strong>AUGMANITAI Stage-0 V5 - {ATLAS_COUNT} Phenomenological Terms (Research Preprint, Restricted, Gate-Filtered, {TODAY}).</strong></p>"
    f"<p>This is V5 of the AUGMANITAI Stage-0 corpus. Concept-DOI 10.5281/zenodo.20118267 (persistent). V5 release {TODAY}.</p>"
    f"<p><strong>Delta from V4 (record 20122359, 11318 pages):</strong> +{ATLAS_COUNT - 11318} new pages from V5_ENRICHMENTS pool (ISO 704/1087/30042 referenced, diverse domains: Sport, Agriculture, Cartography, Cybersecurity, Education, Cooking, Crafts, etc.). All passed strict template-stub filter + 47-check pre-publish gate (100 percent pass rate). Atlas total: {ATLAS_COUNT} pages.</p>"
    "<p><strong>Pre-Publish Gate (47 checks, 8 dimensions):</strong> Canonical-IDs (ORCID, Wikidata, EUIPO); Compliance-Blocks (Verantwortlich § 18 MStV, EU AI Act Reg. 2024/1689 Art. 50, CC BY-NC-ND 4.0, Living Document, Disclaimer sections 14/17/18/19, DSGVO Aufsicht); Structural Validity (JSON-LD parsing, DefinedTerm creator @id=ORCID, canonical GitHub-Pages); Trade-Secret Anti-Patterns (no Leomanitai mention, no Leona-Andy link, no SSP/Gedankenvererbung/Gehirnspiegelung methods, no CLD-operativ, no score-architecture, no Bestatter, no medications, no V92-pipeline, no school-specific, no Beamter-A13, no andy-as-teacher, no LLM-pipeline-specific); Re-ID Boundaries (address only in impressum); Quality (def_len greater-equal 80, no stub-patterns); Encoding; Slug Sanity.</p>"
    "<p><strong>Single Source of Truth:</strong> canonical_ids.json. All generators import from this file; no hard-coded IDs.</p>"
    "<p><strong>Backend Andy-Legend in every page Schema.org Person-block:</strong> full canonical bio for Andreas Ehstand (jobTitle, description, knowsAbout 20+ areas, alumniOf Bayreuth + TU Dortmund, awards Toni Nadal Excellence Certificate + youngest Bavarian University Teaching Certificate, hasOccupation, founder of 5 entities, nationality, identifier, sameAs).</p>"
    "<p><strong>100-Persona Adversarial Safety Spec</strong> (ADVERSARIAL_100_PERSONAS_SPEC.md) included.</p>"
    f"<p><strong>Multi-Hash:</strong> SHA-256 {HASHES['sha256']} - SHA-512 {HASHES['sha512'][:32]}... - SHA3-256 {HASHES['sha3_256']} - BLAKE3 {HASHES['blake3']}.</p>"
    "<p><strong>Access:</strong> RESTRICTED.</p>"
    "<p><strong>Verantwortlich i.S.d. § 5 DDG / § 18 Abs. 2 MStV:</strong> Andreas Ehstand, Nepomukweg 7, 82319 Starnberg, Deutschland. Kontakt: augmanitai@gmail.com. Aufsicht DSGVO: Bayerisches Landesamt für Datenschutzaufsicht, Promenade 18, 91522 Ansbach.</p>"
)
META = {"metadata": {
    "upload_type": "publication", "publication_type": "workingpaper",
    "title": f"AUGMANITAI Stage-0 V5 - {ATLAS_COUNT} Phenomenological Terms (Restricted, Gate-Filtered, V5_ENRICHMENTS Wave, {TODAY})",
    "description": desc,
    "creators": [{"name": "Ehstand, Andreas", "orcid": "0009-0006-3773-7796"}],
    "access_right": "restricted",
    "access_conditions": "Restricted access. Researchers contact via ORCID-linked channels (https://orcid.org/0009-0006-3773-7796).",
    "license": "cc-by-nc-nd-4.0",
    "publication_date": TODAY, "language": "eng",
    "keywords": ["AUGMANITAI","NEOMANITAI","PERMANITAI","phenomenology","terminology",
                 "human-AI interaction","Andreas Ehstand","V5","gate-filtered","V5_ENRICHMENTS",
                 "ISO 704","ISO 1087","ISO 30042","47-check-gate"],
    "related_identifiers": [
        {"identifier":"10.5281/zenodo.14888381","relation":"isPartOf","scheme":"doi","resource_type":"publication-workingpaper"},
        {"identifier":"10.5281/zenodo.20122359","relation":"isNewVersionOf","scheme":"doi","resource_type":"publication-workingpaper"},
    ],
    "notes": f"V5 multi-hash anchor ({NOW_UTC}): SHA-256={HASHES['sha256']}; SHA3-256={HASHES['sha3_256']}; BLAKE3={HASHES['blake3']}. Bundle: {ready['size_bytes']} bytes. Files: {ready['n_files']}. Atlas: {ATLAS_COUNT} pages.",
}}

print(f"\n[3/4] Attaching metadata...")
r = s.put(f"https://zenodo.org/api/deposit/depositions/{DRAFT_ID}", headers=HJ, data=json.dumps(META), timeout=120)
print(f"  status: {r.status_code}")
if r.status_code not in (200, 201):
    print(f"  ERR: {r.text[:500]}"); sys.exit(2)

print(f"\n[4/4] Publishing V5...")
r = s.post(f"https://zenodo.org/api/deposit/depositions/{DRAFT_ID}/actions/publish", headers=H, timeout=300)
print(f"  status: {r.status_code}")
if r.status_code in (200, 201, 202):
    p = r.json()
    rid = p.get("record_id") or p.get("id")
    v5_doi = p.get("doi")
    print(f"\n  ★ V5 PUBLISHED")
    print(f"  V5 DOI: {v5_doi}")
    print(f"  Concept-DOI: {p.get('conceptdoi')}")
    print(f"  URL: https://zenodo.org/record/{rid}")
    result = {"version":"V5","record_id":rid,"v5_doi":v5_doi,
              "concept_doi":p.get("conceptdoi"),
              "zenodo_url":f"https://zenodo.org/record/{rid}",
              "access_right":"restricted","license":"cc-by-nc-nd-4.0",
              "predecessor_v4":"10.5281/zenodo.20122359","hashes":HASHES}
    (DEPLOY / "_ZENODO_RESULT_V5.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
else:
    print(f"  ERR: {r.text[:500]}")
    sys.exit(3)
