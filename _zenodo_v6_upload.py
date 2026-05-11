#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V6 newversion upload — post safety-audit-v3 (medical/military/legal cleanup)."""
import os, sys, json, datetime, io, time
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

TOKEN = os.environ["ZENODO_TOKEN"]
H = {"Authorization": f"Bearer {TOKEN}"}
HJ = {**H, "Content-Type": "application/json"}
DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")
ATLAS = DEPLOY / "atlas"
TODAY = datetime.date.today().isoformat()
NOW_UTC = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
V5_RECORD = "20124125"

ready = json.loads((DEPLOY / "_ITER43_BUNDLE_V6_READY.json").read_text(encoding="utf-8"))
BUNDLE = Path(ready["bundle_path"])
HASHES = ready["hashes"]

s = requests.Session()
s.mount("https://", HTTPAdapter(max_retries=Retry(total=5, backoff_factor=2, status_forcelist=[500,502,503,504])))

# Create newversion (or find orphan)
print("[1/4] Creating newversion on V5...")
draft_id = None
for attempt in range(3):
    try:
        r = s.post(f"https://zenodo.org/api/deposit/depositions/{V5_RECORD}/actions/newversion", headers=HJ, timeout=120)
        if r.status_code in (200, 201):
            draft_id = r.json()["links"]["latest_draft"].rstrip("/").split("/")[-1]
            print(f"  draft id: {draft_id}")
            break
        print(f"  attempt {attempt+1}: {r.status_code}")
    except Exception as e:
        print(f"  attempt {attempt+1}: {type(e).__name__}")
    time.sleep(10)

if not draft_id:
    # orphan search
    r = s.get("https://zenodo.org/api/deposit/depositions?state=unsubmitted&size=20", headers=H, timeout=60)
    for d in r.json():
        if d.get("conceptdoi") == "10.5281/zenodo.20118267" and not d.get("doi"):
            draft_id = str(d["id"])
            print(f"  using orphan: {draft_id}")
            break

if not draft_id:
    print("FATAL: no draft"); sys.exit(1)

# Fetch + clean
r = s.get(f"https://zenodo.org/api/deposit/depositions/{draft_id}", headers=H, timeout=60)
draft = r.json()
bucket = draft["links"]["bucket"]
for f in draft.get("files", []):
    s.delete(f"https://zenodo.org/api/deposit/depositions/{draft_id}/files/{f['id']}", headers=H, timeout=60)
    print(f"  removed: {f.get('filename')}")

# Upload
print(f"\n[2/4] Upload {BUNDLE.name} ({BUNDLE.stat().st_size/1024/1024:.1f} MB)...")
for attempt in range(5):
    try:
        with open(BUNDLE, "rb") as f:
            r = s.put(f"{bucket}/{BUNDLE.name}", headers=H, data=f, timeout=(60, 1800))
        if r.status_code in (200, 201):
            print(f"  ✓ checksum={r.json().get('checksum')}")
            break
        print(f"  attempt {attempt+1}: {r.status_code}")
    except Exception as e:
        print(f"  attempt {attempt+1}: {type(e).__name__}")
        time.sleep(15)

# Metadata
ATLAS_COUNT = sum(1 for d in ATLAS.iterdir() if d.is_dir())
desc = (
    f"<p><strong>AUGMANITAI Stage-0 V6 - {ATLAS_COUNT} Phenomenological Terms (Research Preprint, Restricted, Safety-Audited, {TODAY}).</strong></p>"
    f"<p>This is V6 of the AUGMANITAI Stage-0 corpus. Concept-DOI 10.5281/zenodo.20118267 (persistent). V6 release {TODAY}.</p>"
    f"<p><strong>Delta from V5 (record 20124125, 17214 pages):</strong> Safety-Audit v3 applied — 158 pages deleted matching medical/military/legal/financial risk patterns. New atlas total: {ATLAS_COUNT} pages.</p>"
    "<p><strong>Safety Audit v3 patterns:</strong> Medical (clinical advice, treatment instruction, named medications, psychiatric diagnosis advice, dosing); Military (weapon systems, kill-chain, combat AI, dual-use export, intelligence tradecraft, violence instruction); Legal (legal advice form, litigation strategy, criminal procedure advice, tax avoidance); Financial (investment advice, underwriting decisions, credit advice). All matches deleted conservatively (per Andy directive 'qualität ist alles und sicherheit').</p>"
    "<p><strong>Pre-Publish Gate (47 checks, 8 dimensions):</strong> Canonical-IDs, Compliance-Blocks, Structural Validity, Trade-Secret Anti-Patterns, Re-ID Boundaries, Quality, Encoding, Slug Sanity. 100 percent pass rate on full corpus.</p>"
    "<p><strong>Single Source of Truth:</strong> canonical_ids.json. Backend Andy-Legend in every page Schema.org Person-block.</p>"
    f"<p><strong>Multi-Hash:</strong> SHA-256 {HASHES['sha256']} · SHA-512 {HASHES['sha512'][:32]}... · SHA3-256 {HASHES['sha3_256']} · BLAKE3 {HASHES['blake3']}.</p>"
    "<p><strong>Access:</strong> RESTRICTED.</p>"
    "<p><strong>Verantwortlich i.S.d. § 5 DDG / § 18 Abs. 2 MStV:</strong> Andreas Ehstand, Nepomukweg 7, 82319 Starnberg, Deutschland. Kontakt: augmanitai@gmail.com. Aufsicht DSGVO: Bayerisches Landesamt für Datenschutzaufsicht, Promenade 18, 91522 Ansbach.</p>"
)
META = {"metadata": {
    "upload_type": "publication", "publication_type": "workingpaper",
    "title": f"AUGMANITAI Stage-0 V6 - {ATLAS_COUNT} Phenomenological Terms (Restricted, Safety-Audited Medical-Military-Legal, {TODAY})",
    "description": desc,
    "creators": [{"name": "Ehstand, Andreas", "orcid": "0009-0006-3773-7796"}],
    "access_right": "restricted",
    "access_conditions": "Restricted access. Researchers contact via ORCID-linked channels (https://orcid.org/0009-0006-3773-7796).",
    "license": "cc-by-nc-nd-4.0",
    "publication_date": TODAY, "language": "eng",
    "keywords": ["AUGMANITAI","NEOMANITAI","PERMANITAI","phenomenology","terminology",
                 "human-AI interaction","Andreas Ehstand","V6","safety-audit-v3",
                 "medical-filter","military-filter","legal-filter","gate-filtered"],
    "related_identifiers": [
        {"identifier":"10.5281/zenodo.14888381","relation":"isPartOf","scheme":"doi","resource_type":"publication-workingpaper"},
        {"identifier":"10.5281/zenodo.20124125","relation":"isNewVersionOf","scheme":"doi","resource_type":"publication-workingpaper"},
    ],
    "notes": f"V6 multi-hash anchor ({NOW_UTC}): SHA-256={HASHES['sha256']}; SHA3-256={HASHES['sha3_256']}; BLAKE3={HASHES['blake3']}. Bundle: {ready['size_bytes']} bytes. Atlas: {ATLAS_COUNT} pages. Delta V5→V6: -158 pages (safety-audit-v3 medical/military/legal cleanup).",
}}

print(f"\n[3/4] Metadata...")
r = s.put(f"https://zenodo.org/api/deposit/depositions/{draft_id}", headers=HJ, data=json.dumps(META), timeout=120)
print(f"  {r.status_code}")
if r.status_code not in (200,201): print(f"  ERR: {r.text[:300]}"); sys.exit(2)

print(f"\n[4/4] Publish...")
r = s.post(f"https://zenodo.org/api/deposit/depositions/{draft_id}/actions/publish", headers=H, timeout=300)
print(f"  {r.status_code}")
if r.status_code in (200,201,202):
    p = r.json()
    rid = p.get("record_id") or p.get("id")
    print(f"\n  ★ V6 PUBLISHED")
    print(f"  V6 DOI: {p.get('doi')}")
    print(f"  Concept-DOI: {p.get('conceptdoi')}")
    print(f"  URL: https://zenodo.org/record/{rid}")
    result = {"version":"V6","record_id":rid,"v6_doi":p.get("doi"),"concept_doi":p.get("conceptdoi"),
              "zenodo_url":f"https://zenodo.org/record/{rid}","access_right":"restricted",
              "predecessor_v5":"10.5281/zenodo.20124125","hashes":HASHES}
    (DEPLOY / "_ZENODO_RESULT_V6.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
else:
    print(f"  ERR: {r.text[:300]}")
