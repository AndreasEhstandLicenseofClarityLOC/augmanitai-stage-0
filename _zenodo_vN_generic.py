#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generic Zenodo newversion uploader — reads sentinel + predecessor + title parts from args."""
import os, sys, json, datetime, io, time
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Args: <sentinel_json> <predecessor_record_id> <version_label> <title_suffix>
SENTINEL = sys.argv[1]
PREDECESSOR = sys.argv[2]
VERSION = sys.argv[3]  # e.g. "V7"
TITLE_SUFFIX = sys.argv[4] if len(sys.argv) > 4 else ""
DELTA_DESCRIPTION = sys.argv[5] if len(sys.argv) > 5 else ""

TOKEN = os.environ["ZENODO_TOKEN"]
H = {"Authorization": f"Bearer {TOKEN}"}
HJ = {**H, "Content-Type": "application/json"}
DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")
ATLAS = DEPLOY / "atlas"
TODAY = datetime.date.today().isoformat()
NOW_UTC = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

ready = json.loads((DEPLOY / SENTINEL).read_text(encoding="utf-8"))
BUNDLE = Path(ready["bundle_path"])
if not BUNDLE.is_absolute(): BUNDLE = DEPLOY / BUNDLE.name
HASHES = ready["hashes"]

s = requests.Session()
s.mount("https://", HTTPAdapter(max_retries=Retry(total=5, backoff_factor=2, status_forcelist=[500,502,503,504])))

print(f"[1/4] newversion on {PREDECESSOR}...")
draft_id = None
for attempt in range(3):
    try:
        r = s.post(f"https://zenodo.org/api/deposit/depositions/{PREDECESSOR}/actions/newversion", headers=HJ, timeout=120)
        if r.status_code in (200, 201):
            draft_id = r.json()["links"]["latest_draft"].rstrip("/").split("/")[-1]
            print(f"  draft: {draft_id}"); break
        print(f"  {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"  {type(e).__name__}")
    time.sleep(10)

if not draft_id:
    r = s.get("https://zenodo.org/api/deposit/depositions?state=unsubmitted&size=20", headers=H, timeout=60)
    for d in r.json():
        if d.get("conceptdoi") == "10.5281/zenodo.20118267" and not d.get("doi"):
            draft_id = str(d["id"])
            print(f"  orphan: {draft_id}"); break
if not draft_id: print("FATAL"); sys.exit(1)

r = s.get(f"https://zenodo.org/api/deposit/depositions/{draft_id}", headers=H, timeout=60)
draft = r.json()
bucket = draft["links"]["bucket"]
for f in draft.get("files", []):
    s.delete(f"https://zenodo.org/api/deposit/depositions/{draft_id}/files/{f['id']}", headers=H, timeout=60)
    print(f"  removed: {f.get('filename')}")

print(f"\n[2/4] Upload {BUNDLE.name} ({BUNDLE.stat().st_size/1024/1024:.1f} MB)...")
for attempt in range(5):
    try:
        with open(BUNDLE, "rb") as f:
            r = s.put(f"{bucket}/{BUNDLE.name}", headers=H, data=f, timeout=(60, 1800))
        if r.status_code in (200, 201):
            print(f"  ✓ {r.json().get('checksum')}"); break
        print(f"  attempt {attempt+1}: {r.status_code}")
    except Exception as e:
        print(f"  attempt {attempt+1}: {type(e).__name__}"); time.sleep(15)

ATLAS_COUNT = sum(1 for d in ATLAS.iterdir() if d.is_dir())
desc = (
    f"<p><strong>AUGMANITAI Stage-0 {VERSION} - {ATLAS_COUNT} Phenomenological Terms (Research Preprint, Restricted, {TITLE_SUFFIX}, {TODAY}).</strong></p>"
    f"<p>This is {VERSION} of the AUGMANITAI Stage-0 corpus. Concept-DOI 10.5281/zenodo.20118267 (persistent).</p>"
    f"<p><strong>Delta:</strong> {DELTA_DESCRIPTION}</p>"
    "<p><strong>Pre-Publish Gate (extended v4):</strong> 47 base checks + Children-Mentions filter, Violence (physical/psychological) filter, Instruction/Imperative filter, Du-Ansprache filter. Body-text analysis excludes Disclaimer/Footer/Verantwortlich sections (legitimately contain §14 'you' references).</p>"
    "<p><strong>Single Source of Truth:</strong> canonical_ids.json. Backend Andy-Legend in every Schema.org Person-block.</p>"
    f"<p><strong>Multi-Hash:</strong> SHA-256 {HASHES['sha256']} - SHA-512 {HASHES['sha512'][:32]}... - SHA3-256 {HASHES['sha3_256']} - BLAKE3 {HASHES['blake3']}.</p>"
    "<p><strong>Access:</strong> RESTRICTED.</p>"
    "<p><strong>Verantwortlich i.S.d. § 5 DDG / § 18 Abs. 2 MStV:</strong> Andreas Ehstand, Nepomukweg 7, 82319 Starnberg, Deutschland. Kontakt: augmanitai@gmail.com. Aufsicht DSGVO: Bayerisches Landesamt für Datenschutzaufsicht, Promenade 18, 91522 Ansbach.</p>"
)
META = {"metadata": {
    "upload_type": "publication", "publication_type": "workingpaper",
    "title": f"AUGMANITAI Stage-0 {VERSION} - {ATLAS_COUNT} Terms (Restricted, {TITLE_SUFFIX}, {TODAY})",
    "description": desc,
    "creators": [{"name": "Ehstand, Andreas", "orcid": "0009-0006-3773-7796"}],
    "access_right": "restricted",
    "access_conditions": "Restricted access. Researchers contact via ORCID-linked channels (https://orcid.org/0009-0006-3773-7796).",
    "license": "cc-by-nc-nd-4.0",
    "publication_date": TODAY, "language": "eng",
    "keywords": ["AUGMANITAI","NEOMANITAI","PERMANITAI","phenomenology","terminology",
                 "human-AI interaction","Andreas Ehstand", VERSION, "gate-v4", "safety-filtered"],
    "related_identifiers": [
        {"identifier":"10.5281/zenodo.14888381","relation":"isPartOf","scheme":"doi","resource_type":"publication-workingpaper"},
        {"identifier":f"10.5281/zenodo.{PREDECESSOR}","relation":"isNewVersionOf","scheme":"doi","resource_type":"publication-workingpaper"},
    ],
    "notes": f"{VERSION} multi-hash anchor ({NOW_UTC}): SHA-256={HASHES['sha256']}; BLAKE3={HASHES['blake3']}. Atlas: {ATLAS_COUNT} pages.",
}}
print(f"\n[3/4] Metadata...")
r = s.put(f"https://zenodo.org/api/deposit/depositions/{draft_id}", headers=HJ, data=json.dumps(META), timeout=120)
print(f"  {r.status_code}")
if r.status_code not in (200,201): print(f"  ERR: {r.text[:300]}"); sys.exit(2)

print(f"\n[4/4] Publish...")
r = s.post(f"https://zenodo.org/api/deposit/depositions/{draft_id}/actions/publish", headers=H, timeout=300)
if r.status_code in (200,201,202):
    p = r.json()
    rid = p.get("record_id") or p.get("id")
    print(f"\n  ★ {VERSION} PUBLISHED  DOI: {p.get('doi')}  Concept: {p.get('conceptdoi')}  URL: https://zenodo.org/record/{rid}")
    result = {"version":VERSION,"record_id":rid,"doi":p.get("doi"),"concept_doi":p.get("conceptdoi"),
              "zenodo_url":f"https://zenodo.org/record/{rid}","access_right":"restricted",
              "predecessor":f"10.5281/zenodo.{PREDECESSOR}","hashes":HASHES,"date":TODAY}
    (DEPLOY / f"_ZENODO_RESULT_{VERSION}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
else:
    print(f"  ERR: {r.text[:300]}")
