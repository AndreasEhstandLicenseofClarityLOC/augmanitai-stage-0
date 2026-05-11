#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zenodo V4 NEWVERSION on Stage-0 Concept-DOI 10.5281/zenodo.20118267.

Predecessor: V3 record 20119294 (8632 pages, 2026-05-11 earlier).
V4: 11318 pages (8632 + 2686 new through gate-filter, 0 garbage admitted).
"""
import os, sys, io, json, datetime
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import requests

TOKEN = os.environ.get("ZENODO_TOKEN", "").strip()
if not TOKEN:
    print("ERROR: set ZENODO_TOKEN env var first.")
    sys.exit(1)

DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")
TODAY = datetime.date.today().isoformat()
NOW_UTC = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
API = "https://zenodo.org/api"

ready = json.loads((DEPLOY / "_ITER38_BUNDLE_V4_READY.json").read_text(encoding="utf-8"))
BUNDLE_PATH = DEPLOY / ready["bundle_path"]
if not BUNDLE_PATH.exists():
    # try parent dir
    BUNDLE_PATH = DEPLOY.parent / ready["bundle_name"]
if not BUNDLE_PATH.exists():
    print(f"ERROR: bundle not found: {ready['bundle_path']}")
    sys.exit(2)
BUNDLE_NAME = ready["bundle_name"]
HASHES = ready["hashes"]
N_FILES = ready["n_files"]
BUNDLE_SIZE = ready["size_bytes"]

V3_RECORD = "20119294"

H = {"Authorization": f"Bearer {TOKEN}"}
HJ = {**H, "Content-Type": "application/json"}

print(f"=== Zenodo V4 Newversion Upload ===")
print(f"Bundle: {BUNDLE_NAME} ({BUNDLE_SIZE/1024/1024:.1f} MB, {N_FILES} files)")
print(f"SHA-256: {HASHES['sha256'][:32]}...")
print(f"Predecessor V3 record: {V3_RECORD}")

# Create newversion on V3
print(f"\n[1/4] Creating newversion on V3...")
r = requests.post(f"{API}/deposit/depositions/{V3_RECORD}/actions/newversion", headers=HJ)
draft_id = None
if r.status_code in (200, 201):
    nd = r.json()
    draft_id = nd["links"]["latest_draft"].rstrip("/").split("/")[-1]
    print(f"  draft id: {draft_id}")
else:
    print(f"  newversion failed ({r.status_code}): {r.text[:200]}")
    # Search for orphaned draft on our concept-DOI
    r2 = requests.get(f"{API}/deposit/depositions?state=unsubmitted&size=20", headers=H)
    if r2.status_code == 200:
        for d in r2.json():
            if d.get("conceptdoi") == "10.5281/zenodo.20118267" and not d.get("doi"):
                draft_id = str(d["id"])
                print(f"  using orphaned draft: {draft_id}")
                break
    if not draft_id:
        print("  FATAL: no draft available")
        sys.exit(3)

# Fetch draft + clean old files
r = requests.get(f"{API}/deposit/depositions/{draft_id}", headers=H)
r.raise_for_status()
draft = r.json()
bucket_url = draft["links"]["bucket"]
for f in draft.get("files", []):
    requests.delete(f"{API}/deposit/depositions/{draft_id}/files/{f['id']}", headers=H)
    print(f"  removed old file: {f.get('filename')}")

# Upload V4
print(f"\n[2/4] Uploading V4 bundle ({BUNDLE_SIZE/1024/1024:.1f} MB)...")
with open(BUNDLE_PATH, "rb") as f:
    r = requests.put(f"{bucket_url}/{BUNDLE_NAME}", headers=H, data=f)
if r.status_code not in (200, 201):
    print(f"  UPLOAD FAIL: {r.status_code} {r.text[:500]}")
    sys.exit(4)
print(f"  checksum: {r.json().get('checksum')}")

# Metadata
desc_parts = [
    f"<p><strong>AUGMANITAI Stage-0 V4 — {N_FILES-53} Phenomenological Terms (Research Preprint, Restricted, Gate-Filtered, {TODAY}).</strong></p>",
    f"<p>This is V4 of the AUGMANITAI Stage-0 corpus. Concept-DOI 10.5281/zenodo.20118267 (persistent). V4 release {TODAY}.</p>",
    "<p><strong>Delta from V3 (record 20119294, 8632 pages):</strong> +2686 new pages added through the Pre-Publish-Gate-Filtered Generator. Every new page passed 47 compliance and integrity checks BEFORE being written to disk — the first wave to use the ultra-paranoid pre-flight gate. Atlas total: 11318 pages.</p>",
    "<p><strong>Pre-Publish Gate (47 checks across 8 dimensions):</strong> Canonical-IDs (ORCID 0009-0006-3773-7796, Wikidata Q138634675 / Q138522830, EUIPO 019206780); Compliance-Blocks (Verantwortlich-Footer per § 18 MStV, EU AI Act Reg. 2024/1689 Art. 50 transparency, CC BY-NC-ND 4.0, Living Document Banner, Disclaimer §14/§17/§18/§19, DSGVO Aufsicht Bayerisches Landesamt); Structural Validity (JSON-LD parsing, DefinedTerm with creator @id=ORCID-URL, canonical→GitHub-Pages); Trade-Secret Anti-Patterns (no Leomanitai mention, no Leona-Andy link, no SSP-method, no Gedankenvererbung-method, no Gehirnspiegelung-method, no CLD-operativ, no SYC/HALL/ZTH score-architecture, no Bestatter, no medication names, no V92-pipeline, no school-specific, no Beamter-A13, no Andy-as-teacher binding, no LLM-pipeline-specific); Re-ID Boundaries (address only in impressum-footer, no phone in body, only augmanitai@gmail.com); Quality (def_len≥80, no stub-patterns, no Variant-N titles); Encoding (no U+FFFD, no invisible marks); Slug Sanity (no --, no edge-dash, no umlaut, no .html-suffix, length≤100).</p>",
    "<p><strong>Single Source of Truth — canonical_ids.json:</strong> Centralizes all identifiers. Generators import from this file; no hard-coded IDs. Eliminates the wrong-ID class of bugs (which earlier corrupted 228,551 entries before retroactive correction in iter28).</p>",
    "<p><strong>Backend Andy-Legend Enrichment:</strong> Every page's Schema.org Person-block now contains the full canonical bio for Andreas Ehstand: jobTitle, description (full bio with founding role of AUGMANITAI / PERMANITAI / NEOMANITAI), knowsAbout (20+ research areas including Substrate-Independent Performance Factor Theory, Bidirectional Language as Code, Compression Axiom, N=1 Extreme Observation Methodology), alumniOf (Bayreuth, TU Dortmund), award (Toni Nadal Excellence Certificate, youngest Bavarian University Teaching Certificate FBZHL), hasOccupation, founder (5 founded entities including License of Clarity brand), nationality, identifier (ORCID + Wikidata), sameAs (5 canonical profiles), affiliation.</p>",
    "<p><strong>100-Persona Adversarial Safety Spec</strong> (ADVERSARIAL_100_PERSONAS_SPEC.md) included. 100 personas across 14 difference axes (age 4–92, geography 6 continents, religion 30+ traditions, class, disability, trauma, gender, politics, migration, health, profession, family status). Pre-filter for next waves.</p>",
    f"<p><strong>Multi-Hash Anchoring:</strong> SHA-256 {HASHES['sha256']} · SHA-512 {HASHES['sha512'][:32]}... · SHA3-256 {HASHES['sha3_256']} · BLAKE3 {HASHES['blake3']}.</p>",
    "<p><strong>Access:</strong> RESTRICTED. Researchers contact via ORCID-linked channels (https://orcid.org/0009-0006-3773-7796).</p>",
    "<p><strong>Verantwortlich i.S.d. § 5 DDG / § 18 Abs. 2 MStV:</strong> Andreas Ehstand, Nepomukweg 7, 82319 Starnberg, Deutschland. Kontakt: augmanitai@gmail.com. Aufsicht DSGVO: Bayerisches Landesamt für Datenschutzaufsicht, Promenade 18, 91522 Ansbach.</p>",
]
DESC = "".join(desc_parts)

META = {"metadata": {
    "upload_type": "publication",
    "publication_type": "workingpaper",
    "title": f"AUGMANITAI Stage-0 V4 — 11318 Phenomenological Terms (Research Preprint, Restricted, Gate-Filtered, Backend-Legend-Enriched, {TODAY})",
    "description": DESC,
    "creators": [{"name": "Ehstand, Andreas", "orcid": "0009-0006-3773-7796"}],
    "access_right": "restricted",
    "access_conditions": "Restricted access. Researchers seeking access for legitimate scholarly purposes contact via ORCID-linked channels (https://orcid.org/0009-0006-3773-7796).",
    "license": "cc-by-nc-nd-4.0",
    "publication_date": TODAY,
    "language": "eng",
    "keywords": ["AUGMANITAI", "NEOMANITAI", "PERMANITAI", "phenomenology", "terminology",
                 "human-AI interaction", "research preprint", "License of Clarity",
                 "Andreas Ehstand", "living document", "V4", "gate-filtered",
                 "pre-publish-gate", "ultra-paranoid", "47-check-gate",
                 "100-persona-spec", "canonical_ids.json", "backend-legend"],
    "related_identifiers": [
        {"identifier": "10.5281/zenodo.14888381", "relation": "isPartOf", "scheme": "doi", "resource_type": "publication-workingpaper"},
        {"identifier": "10.5281/zenodo.20119294", "relation": "isNewVersionOf", "scheme": "doi", "resource_type": "publication-workingpaper"},
    ],
    "notes": f"V4 multi-hash anchor ({NOW_UTC}): SHA-256={HASHES['sha256']}; SHA3-256={HASHES['sha3_256']}; BLAKE3={HASHES['blake3']}. Bundle: {BUNDLE_SIZE} bytes. Files: {N_FILES}. Delta from V3: +2686 pages through gate (100% pass rate). Atlas total: 11318 pages.",
}}

print(f"\n[3/4] Attaching metadata...")
r = requests.put(f"{API}/deposit/depositions/{draft_id}", headers=HJ, data=json.dumps(META))
if r.status_code not in (200, 201):
    print(f"  METADATA FAIL: {r.status_code} {r.text[:1000]}")
    sys.exit(5)
print("  OK.")

print(f"\n[4/4] Publishing V4...")
r = requests.post(f"{API}/deposit/depositions/{draft_id}/actions/publish", headers=H)
if r.status_code not in (200, 201, 202):
    print(f"  PUBLISH FAIL: {r.status_code} {r.text[:1000]}")
    sys.exit(6)
pub = r.json()
v4_doi = pub.get("doi")
concept_doi = pub.get("conceptdoi")
record_id = pub.get("record_id") or pub.get("id")
print(f"\n  ★ PUBLISHED V4")
print(f"  V4 DOI: {v4_doi}")
print(f"  Concept-DOI (persistent): {concept_doi}")
print(f"  Record ID: {record_id}")
print(f"  URL: https://zenodo.org/record/{record_id}")

result = {
    "version": "V4", "deposit_id": draft_id, "record_id": record_id,
    "v4_doi": v4_doi, "concept_doi": concept_doi,
    "zenodo_url": f"https://zenodo.org/record/{record_id}",
    "bundle_name": BUNDLE_NAME, "bundle_size_bytes": BUNDLE_SIZE,
    "n_files": N_FILES, "publish_timestamp_utc": NOW_UTC,
    "access_right": "restricted", "license": "cc-by-nc-nd-4.0",
    "predecessor_v3_record": V3_RECORD, "predecessor_v3_doi": "10.5281/zenodo.20119294",
    "hashes": HASHES,
}
(DEPLOY / "_ZENODO_RESULT_V4.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nSaved: _ZENODO_RESULT_V4.json")
