#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 41 — Build V5 bundle + Zenodo V5 newversion + GitHub push (one shot).

Assumes hub+sitemap+gate-sweep already passed.
"""
import os, json, hashlib, zipfile, datetime, io, sys, subprocess
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude")
DEPLOY = ROOT / "_AKTIV/_FIRST_NETWORK_BUILD/_DEPLOY_STAGE_0_50TERMS"
ATLAS = DEPLOY / "atlas"
TODAY = datetime.date.today().isoformat()
NOW_UTC = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
BUNDLE_NAME = f"augmanitai_stage_0_v5_{TODAY}.zip"
BUNDLE_PATH = DEPLOY / BUNDLE_NAME

# Build bundle
print(f"[1/4] Building V5 bundle...")
INCLUDE_DIRS = ["atlas", "disclaimer", "about", "accessibility", "ai-transparency", "audit",
                "citation", "datenschutz", "impressum", "iso-conformance", "license-of-clarity",
                "licenses", "living-document-policy", "permanitai", "trade-secret-layer",
                "witness-quorum", "exports"]
INCLUDE_FILES = ["index.html", "README.md", "CITATION.cff", "LICENSE", "CNAME",
                 "sitemap.xml", "llms.txt", "ai.txt", "robots.txt", "ROADMAP.md", "NAMESPACE.md",
                 "canonical_ids.json", "ADVERSARIAL_100_PERSONAS_SPEC.md"]
n_files = 0
if BUNDLE_PATH.exists(): BUNDLE_PATH.unlink()
with zipfile.ZipFile(BUNDLE_PATH, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
    for f in DEPLOY.rglob("*"):
        if not f.is_file(): continue
        rel = f.relative_to(DEPLOY)
        if rel.parts[0] in INCLUDE_DIRS or rel.parts[0] in INCLUDE_FILES:
            zf.write(f, str(rel))
            n_files += 1
sz = BUNDLE_PATH.stat().st_size
print(f"  Bundle: {BUNDLE_NAME} | {n_files} files | {sz/1024/1024:.1f} MB")

# Multi-hash
print(f"[2/4] Computing multi-hash anchor...")
hashes = {"sha256": hashlib.sha256(), "sha512": hashlib.sha512(),
          "sha3_256": hashlib.sha3_256(), "sha3_512": hashlib.sha3_512()}
try:
    import blake3
    hashes["blake3"] = blake3.blake3()
except Exception:
    hashes["blake3"] = None
with open(BUNDLE_PATH, "rb") as f:
    for chunk in iter(lambda: f.read(65536), b""):
        for h in hashes.values():
            if h: h.update(chunk)
H = {k: h.hexdigest() if h else "NA" for k, h in hashes.items()}
for k, v in H.items(): print(f"  {k}: {v[:32]}...")

# Manifest
hreg = ROOT / "10_RECHTLICHES" / "PRIOR_ART_TIMESTAMPS"
manif = hreg / f"MANIFEST_stage0_v5_{TODAY}.txt"
manif.write_text(
    f"AUGMANITAI Stage-0 V5 Bundle Hash Manifest\n"
    f"Date: {TODAY}\n"
    f"Author: Andreas Ehstand (ORCID 0009-0006-3773-7796, Wikidata Q138634675)\n"
    f"Programme: AUGMANITAI Compendium (Wikidata Q138522830)\n"
    f"Bundle: {BUNDLE_NAME}\nFiles: {n_files}\nSize: {sz} bytes\n"
    f"Concept-DOI: 10.5281/zenodo.20118267\n"
    f"Predecessor V4-DOI: 10.5281/zenodo.20122359\n\n"
    f"SHA-256: {H['sha256']}\nSHA-512: {H['sha512']}\nSHA3-256: {H['sha3_256']}\n"
    f"SHA3-512: {H['sha3_512']}\nBLAKE3: {H['blake3']}\n",
    encoding="utf-8"
)
mreg_path = hreg / "MULTI_HASH_REGISTRY_stage0.json"
mreg = json.loads(mreg_path.read_text(encoding="utf-8")) if mreg_path.exists() else {"entries": []}
mreg["entries"].append({"bundle": BUNDLE_NAME, "date": TODAY, "version": "V5",
                        "concept_doi": "10.5281/zenodo.20118267",
                        "n_files": n_files, "size_bytes": sz, "hashes": H})
mreg_path.write_text(json.dumps(mreg, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"  Manifest: {manif.name}")

# Save sentinel
sentinel = {"ready": True, "bundle_path": str(BUNDLE_PATH), "bundle_name": BUNDLE_NAME,
            "concept_doi": "10.5281/zenodo.20118267", "predecessor_v4": "10.5281/zenodo.20122359",
            "n_files": n_files, "size_bytes": sz, "hashes": H, "date": TODAY}
(DEPLOY / "_ITER41_BUNDLE_V5_READY.json").write_text(
    json.dumps(sentinel, ensure_ascii=False, indent=2), encoding="utf-8")

# Zenodo V5 upload
TOKEN = os.environ.get("ZENODO_TOKEN", "").strip()
if not TOKEN:
    print("\n[3/4] ZENODO_TOKEN not set — skip upload, only bundle ready")
    print("Bundle ready for manual upload via _zenodo_v5_upload.py")
    sys.exit(0)

print(f"\n[3/4] Zenodo V5 newversion upload...")
import requests
HJ = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
H_h = {"Authorization": f"Bearer {TOKEN}"}
V4 = "20122359"

# Try newversion (may 504, then orphan-search)
r = requests.post(f"https://zenodo.org/api/deposit/depositions/{V4}/actions/newversion", headers=HJ, timeout=120)
draft_id = None
if r.status_code in (200, 201):
    draft_id = r.json()["links"]["latest_draft"].rstrip("/").split("/")[-1]
    print(f"  draft id: {draft_id}")
else:
    print(f"  newversion status {r.status_code}, searching orphan...")
    r2 = requests.get("https://zenodo.org/api/deposit/depositions?state=unsubmitted&size=20", headers=H_h)
    for d in r2.json() if r2.status_code == 200 else []:
        if d.get("conceptdoi") == "10.5281/zenodo.20118267" and not d.get("doi"):
            draft_id = str(d["id"])
            print(f"  using orphan: {draft_id}")
            break
    if not draft_id:
        print("  FAIL: no draft. Aborting Zenodo step.")
        sys.exit(1)

# Clean old files
r = requests.get(f"https://zenodo.org/api/deposit/depositions/{draft_id}", headers=H_h)
draft = r.json()
bucket = draft["links"]["bucket"]
for f in draft.get("files", []):
    requests.delete(f"https://zenodo.org/api/deposit/depositions/{draft_id}/files/{f['id']}", headers=H_h)
    print(f"  removed old: {f.get('filename')}")

# Upload
print(f"  Uploading {sz/1024/1024:.1f} MB...")
with open(BUNDLE_PATH, "rb") as f:
    r = requests.put(f"{bucket}/{BUNDLE_NAME}", headers=H_h, data=f)
print(f"  upload: {r.status_code}")

# Metadata
ATLAS_COUNT = sum(1 for d in ATLAS.iterdir() if d.is_dir())
desc = (
    f"<p><strong>AUGMANITAI Stage-0 V5 - {ATLAS_COUNT} Phenomenological Terms (Research Preprint, Restricted, Gate-Filtered, {TODAY}).</strong></p>"
    f"<p>This is V5 of the AUGMANITAI Stage-0 corpus. Concept-DOI 10.5281/zenodo.20118267 (persistent). V5 release {TODAY}.</p>"
    f"<p><strong>Delta from V4 (record 20122359, 11318 pages):</strong> +{ATLAS_COUNT - 11318} new pages from V5_ENRICHMENTS pool (diverse domains: Sport, Agriculture, Cartography, Cybersecurity, Education, Cooking, Crafts, etc. with ISO 704/1087/30042 references). All passed strict template-stub filter + 47-check pre-publish gate. Atlas total: {ATLAS_COUNT} pages.</p>"
    "<p><strong>Pre-Publish Gate (47 checks, 8 dimensions):</strong> Canonical-IDs, Compliance-Blocks (Verantwortlich § 18 MStV, EU AI Act Art. 50, CC BY-NC-ND, Living Document, Disclaimer §14/§17/§18/§19, DSGVO), Structural Validity, Trade-Secret Anti-Patterns, Re-ID Boundaries, Quality, Encoding, Slug Sanity.</p>"
    "<p><strong>Backend Andy-Legend:</strong> Every page Schema.org Person-block contains full canonical bio (jobTitle, description, knowsAbout 20+ areas, alumniOf Bayreuth + TU Dortmund, awards, hasOccupation, founder of 5 entities, nationality, identifier, sameAs).</p>"
    "<p><strong>100-Persona Adversarial Safety Spec</strong> included.</p>"
    f"<p><strong>Multi-Hash:</strong> SHA-256 {H['sha256']} - SHA-512 {H['sha512'][:32]}... - SHA3-256 {H['sha3_256']} - BLAKE3 {H['blake3']}.</p>"
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
    "keywords": ["AUGMANITAI", "NEOMANITAI", "PERMANITAI", "phenomenology", "terminology",
                 "human-AI interaction", "Andreas Ehstand", "V5", "gate-filtered",
                 "V5_ENRICHMENTS", "ISO 704", "ISO 1087", "ISO 30042"],
    "related_identifiers": [
        {"identifier": "10.5281/zenodo.14888381", "relation": "isPartOf", "scheme": "doi", "resource_type": "publication-workingpaper"},
        {"identifier": "10.5281/zenodo.20122359", "relation": "isNewVersionOf", "scheme": "doi", "resource_type": "publication-workingpaper"},
    ],
    "notes": f"V5 multi-hash anchor ({NOW_UTC}): SHA-256={H['sha256']}; BLAKE3={H['blake3']}. Bundle: {sz} bytes. Files: {n_files}. Atlas: {ATLAS_COUNT} pages.",
}}
r = requests.put(f"https://zenodo.org/api/deposit/depositions/{draft_id}", headers=HJ, data=json.dumps(META))
print(f"  metadata: {r.status_code}")
r = requests.post(f"https://zenodo.org/api/deposit/depositions/{draft_id}/actions/publish", headers=H_h)
print(f"  publish: {r.status_code}")
if r.status_code in (200, 201, 202):
    p = r.json()
    rid = p.get("record_id") or p.get("id")
    v5_doi = p.get("doi")
    print(f"\n  ★ V5 PUBLISHED")
    print(f"  V5 DOI: {v5_doi}")
    print(f"  Concept-DOI: {p.get('conceptdoi')}")
    print(f"  URL: https://zenodo.org/record/{rid}")
    result = {"version": "V5", "record_id": rid, "v5_doi": v5_doi,
              "concept_doi": p.get("conceptdoi"),
              "zenodo_url": f"https://zenodo.org/record/{rid}",
              "access_right": "restricted", "license": "cc-by-nc-nd-4.0",
              "predecessor_v4": "10.5281/zenodo.20122359", "hashes": H}
    (DEPLOY / "_ZENODO_RESULT_V5.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
else:
    print(f"  ERR: {r.text[:400]}")
    sys.exit(2)

# GitHub Push
print(f"\n[4/4] GitHub push...")
subprocess.run(["git", "add", "-A"], cwd=DEPLOY, check=True)
r = subprocess.run(["git", "commit", "-m", "bearbeitung"], cwd=DEPLOY, capture_output=True, text=True)
print(f"  commit: {r.returncode}")
r = subprocess.run(["git", "push", "origin", "main"], cwd=DEPLOY, capture_output=True, text=True)
print(f"  push: {r.returncode}")
print(f"  {r.stdout[-200:] if r.stdout else r.stderr[-200:]}")
