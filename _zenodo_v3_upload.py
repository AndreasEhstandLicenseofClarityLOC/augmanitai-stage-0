#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zenodo V3 NEWVERSION on Stage-0 Concept-DOI 10.5281/zenodo.20118267.

Predecessor: V2 record 20119072 (8842 atlas pages, 2026-05-11 earlier).
V3: 9510 atlas pages after quality-cleanup (iter27 audit + iter30 cleanup of 2222 garbage pages)
    + canonical-ID fix (iter28: 228551 wrong-ID replacements)
    + Leomanitai UG trade-secret leak removal (iter29: 8029 files)
    + ORCID/Wikidata/Zenodo anchor injection (iter21-23)
    + Pool-pages from NEOMANITAI_4407 (iter24) and AUG_BACKBONE (iter26)
    + .html-suffix slug fix (iter25)

Bundle pre-built by _iter31_prepare_v3_bundle.py with multi-hash already computed.

ACCESS RIGHT: RESTRICTED (per Andy directive 2026-05-11).
"""
import os, sys, io, json, datetime
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
try:
    import requests
except ImportError:
    print("ERROR: pip install requests"); sys.exit(1)

TOKEN = os.environ.get("ZENODO_TOKEN", "").strip()
if not TOKEN:
    print("ERROR: set ZENODO_TOKEN env var first.")
    print("       PowerShell: $env:ZENODO_TOKEN='your_token_here'")
    sys.exit(1)

DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")
TODAY = datetime.date.today().isoformat()
NOW_UTC = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
API = "https://zenodo.org/api"

# Load pre-built bundle info
ready_sentinel = DEPLOY / "_ITER31_BUNDLE_READY.json"
if not ready_sentinel.exists():
    print("ERROR: _ITER31_BUNDLE_READY.json missing. Run _iter31_prepare_v3_bundle.py first.")
    sys.exit(2)
ready = json.loads(ready_sentinel.read_text(encoding="utf-8"))
BUNDLE_PATH = Path(ready["bundle_path"])
BUNDLE_NAME = ready["bundle_name"]
HASHES = ready["hashes"]
N_FILES = ready["n_files"]
BUNDLE_SIZE = ready["size_bytes"]

CONCEPT_DOI = "10.5281/zenodo.20118267"
V2_RECORD_ID = "20119072"

headers_json = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
headers_bucket = {"Authorization": f"Bearer {TOKEN}"}

print(f"=== Zenodo V3 Newversion Upload ===")
print(f"Bundle: {BUNDLE_NAME}")
print(f"Size: {BUNDLE_SIZE:,} bytes ({BUNDLE_SIZE/1024/1024:.1f} MB)")
print(f"Files: {N_FILES}")
print(f"SHA-256: {HASHES['sha256'][:32]}...")

# === STEP 1: Create newversion ===
print(f"\n[1/4] Creating newversion on V2 record {V2_RECORD_ID}...")
r = requests.post(f"{API}/deposit/depositions/{V2_RECORD_ID}/actions/newversion", headers=headers_json)
if r.status_code not in (200, 201):
    print(f"  FAIL: {r.status_code} {r.text[:500]}"); sys.exit(3)
new_dep = r.json()
new_deposit_id = new_dep["links"]["latest_draft"].rstrip("/").split("/")[-1]
print(f"  New draft deposit ID: {new_deposit_id}")

# Fetch draft to get bucket + clean old files
r = requests.get(f"{API}/deposit/depositions/{new_deposit_id}", headers=headers_json)
r.raise_for_status()
draft = r.json()
bucket_url = draft["links"]["bucket"]
print(f"  Removing inherited V2 files...")
for f in draft.get("files", []):
    f_id = f.get("id")
    if f_id:
        del_r = requests.delete(f"{API}/deposit/depositions/{new_deposit_id}/files/{f_id}", headers=headers_json)
        if del_r.status_code in (204, 200):
            print(f"    Removed: {f.get('filename')}")

# === STEP 2: Upload V3 bundle ===
print(f"\n[2/4] Uploading V3 bundle ({BUNDLE_SIZE/1024/1024:.1f} MB)...")
with open(BUNDLE_PATH, "rb") as f:
    r = requests.put(f"{bucket_url}/{BUNDLE_NAME}", headers=headers_bucket, data=f)
if r.status_code not in (200, 201):
    print(f"  UPLOAD FAIL: {r.status_code} {r.text[:500]}"); sys.exit(4)
print(f"  Server checksum: {r.json().get('checksum')}")

# === STEP 3: Metadata ===
DESCRIPTION = f"""<p><strong>AUGMANITAI Stage-0 V3 — 9510 Phenomenological Terms (Research Preprint, Restricted, Post-Quality-Cleanup).</strong></p>
<p>This is V3 of the AUGMANITAI Stage-0 corpus. Concept-DOI {CONCEPT_DOI} (persistent). V3 release date: {TODAY}.</p>
<p><strong>Delta from V2 (record 20119072, 8842 pages):</strong> Net +668 atlas pages (V2=8842 → V3=9510). Substantive changes:</p>
<ul>
<li><strong>+2748 new pool pages</strong> (iter24, NEOMANITAI_4407 pool): Bridge_AI, Creative_AI, Vibe_Coding, Cognitive_Shift, Education_Learning, Temporal_AI, Robotics, etc. — quality-filtered (confidence=I + def≥80 chars + stub-free + hard-block-clean).</li>
<li><strong>+955 backbone pages</strong> (iter26, AUG_BACKBONE_LATEST): 850 AUGMANITAI_CORE original phenomenology + 105 RPH_SUBJECTIVE_EXPERIENCE.</li>
<li><strong>−813 version-N dedupe</strong> (iter18): variant-2..N, trust-var-NN, and stub-pattern duplicates removed.</li>
<li><strong>−2222 quality-cleanup</strong> (iter30): trailing-N pipeline-IDs (adu-010..100 style), boilerplate stubs ("May describe aspect of X"), def-too-short fragments (bond-a/edge-b/ethics-q).</li>
<li><strong>Canonical-ID fix</strong> (iter28): 228,551 wrong-ID replacements across 11,739 files — corrected ORCID and Wikidata identifiers throughout.</li>
<li><strong>Trade-secret leak removal</strong> (iter29): "Inhaber Leomanitai UG" annotation removed from 8029 V11.2 pages.</li>
<li><strong>Ehstand-anchor injection</strong> (iter21-23): every page now has Schema.org DefinedTerm with Person(@id=ORCID), Organization(@id=Wikidata-AUGMANITAI), subjectOf(@id=Zenodo Concept-DOI), Open Graph + Twitter Card metadata, citation_author meta tags.</li>
<li><strong>.html-suffix slug fix</strong> (iter25): 1541 malformed directory names renamed.</li>
<li><strong>100-Persona Adversarial Safety Spec</strong> (ADVERSARIAL_100_PERSONAS_SPEC.md): extended from 12 to 100 personas across 14 difference axes (age 4–92, geography 6 continents, religion 30+ traditions, class, disability, trauma, gender, politics, migration, health, profession, family status). Pre-filter for future generation waves.</li>
</ul>
<p><strong>Universal Mandatory Safety Block (Iter 13 + post-V2 updates):</strong> all 9510 pages: §14 Age 18+, §17 AI Training Prohibition, §18 Verantwortlich, §19 Severability, §26 Refinement Window, EUIPO 019206780 License of Clarity (mark-holder anonymized per trade-secret-protocol), EU AI Act Reg. 2024/1689 Art. 50, Living Document marker, ORCID 0009-0006-3773-7796, Wikidata Q138634675, AUGMANITAI Wikidata Q138522830, CC BY-NC-ND 4.0.</p>
<p><strong>Backend completeness (iter20 audit):</strong> 100% pages with ORCID-link, Wikidata-link, Zenodo cross-link, Open Graph, Twitter Card, canonical, lang attribute, license, Verantwortlich footer, Living Document banner. Avg 14.42 Andreas-Ehstand mentions per page (min 10, max 60).</p>
<p><strong>Multi-Hash Anchoring:</strong> SHA-256 {HASHES['sha256']} · SHA-512 {HASHES['sha512'][:32]}... · SHA3-256 {HASHES['sha3_256']} · SHA3-512 {HASHES['sha3_512'][:32]}... · BLAKE3 {HASHES['blake3']}. External manifest archived in 10_RECHTLICHES/PRIOR_ART_TIMESTAMPS/.</p>
<p><strong>Access:</strong> RESTRICTED. Researchers contact via ORCID-linked channels (https://orcid.org/0009-0006-3773-7796).</p>
<p><strong>Public Stealth Layer:</strong> https://andreasehstandlicenseofclarityloc.github.io/augmanitai-stage-0/ — per-term HTML with inline JSON-LD; bulk machine-readable exports stored in this restricted Zenodo deposit.</p>
<p><strong>Verantwortlich i.S.d. § 5 DDG / § 18 Abs. 2 MStV:</strong> Andreas Ehstand, Nepomukweg 7, 82319 Starnberg, Deutschland. Kontakt: augmanitai@gmail.com. Aufsicht DSGVO: Bayerisches Landesamt für Datenschutzaufsicht, Promenade 18, 91522 Ansbach.</p>
"""

METADATA = {
    "metadata": {
        "upload_type": "publication",
        "publication_type": "workingpaper",
        "title": f"AUGMANITAI Stage-0 V3 — 9510 Phenomenological Terms (Research Preprint, Restricted, Quality-Cleanup, {TODAY})",
        "description": DESCRIPTION,
        "creators": [{"name": "Ehstand, Andreas", "orcid": "0009-0006-3773-7796"}],
        "access_right": "restricted",
        "access_conditions": "Restricted access. Researchers seeking access for legitimate scholarly purposes contact via ORCID-linked channels (https://orcid.org/0009-0006-3773-7796).",
        "license": "cc-by-nc-nd-4.0",
        "publication_date": TODAY,
        "language": "eng",
        "keywords": ["AUGMANITAI", "NEOMANITAI", "PERMANITAI", "phenomenology", "terminology",
                     "human-AI interaction", "research preprint", "License of Clarity",
                     "Andreas Ehstand", "living document", "V3", "quality cleanup",
                     "adversarial persona spec", "100-persona safety review"],
        "related_identifiers": [
            {"identifier": "10.5281/zenodo.14888381", "relation": "isPartOf", "scheme": "doi", "resource_type": "publication-workingpaper"},
            {"identifier": f"10.5281/zenodo.{V2_RECORD_ID}", "relation": "isNewVersionOf", "scheme": "doi", "resource_type": "publication-workingpaper"},
        ],
        "notes": f"V3 multi-hash anchor ({NOW_UTC}): SHA-256={HASHES['sha256']}; SHA3-256={HASHES['sha3_256']}; BLAKE3={HASHES['blake3']}. Bundle: {BUNDLE_SIZE:,} bytes. File count: {N_FILES}. Delta from V2: +668 net pages (2748+955 added, 813+2222 deleted) + safety + canonical-ID + trade-secret + Ehstand-anchor fixes.",
    }
}
print(f"\n[3/4] Attaching metadata...")
r = requests.put(f"{API}/deposit/depositions/{new_deposit_id}", headers=headers_json, data=json.dumps(METADATA))
if r.status_code not in (200, 201):
    print(f"  METADATA FAIL: {r.status_code} {r.text[:1000]}"); sys.exit(5)
print("  OK.")

# === STEP 4: Publish ===
print(f"\n[4/4] Publishing V3...")
r = requests.post(f"{API}/deposit/depositions/{new_deposit_id}/actions/publish", headers=headers_json)
if r.status_code not in (200, 201, 202):
    print(f"  PUBLISH FAIL: {r.status_code} {r.text[:1000]}"); sys.exit(6)
pub = r.json()
v3_doi = pub.get("doi")
concept_doi = pub.get("conceptdoi")
record_id = pub.get("record_id") or pub.get("id")
print(f"\n  ★ PUBLISHED V3")
print(f"  V3 DOI: {v3_doi}")
print(f"  Concept-DOI (persistent): {concept_doi}")
print(f"  Record ID: {record_id}")
print(f"  Zenodo URL: https://zenodo.org/record/{record_id}")

result = {
    "version": "V3", "deposit_id": new_deposit_id, "record_id": record_id,
    "v3_doi": v3_doi, "concept_doi": concept_doi,
    "zenodo_url": f"https://zenodo.org/record/{record_id}",
    "bundle_name": BUNDLE_NAME, "bundle_size_bytes": BUNDLE_SIZE,
    "n_files": N_FILES, "publish_timestamp_utc": NOW_UTC,
    "access_right": "restricted", "license": "cc-by-nc-nd-4.0",
    "title": METADATA["metadata"]["title"], "hashes": HASHES,
    "predecessor_v2_record": V2_RECORD_ID, "predecessor_v2_doi": f"10.5281/zenodo.{V2_RECORD_ID}",
}
(DEPLOY / "_ZENODO_RESULT_V3.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nResult: _ZENODO_RESULT_V3.json")
