#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITER 31 — Prepare Zenodo V3 bundle + multi-hash anchor (offline, before upload).

Builds:
- ZIP bundle of 9510 atlas + top-level
- SHA-256 + SHA-512 + SHA3-256 + SHA3-512 manifest
- BLAKE3 if available
- Pre-flight metadata diff for V2 → V3
- _ITER31_BUNDLE_READY.json sentinel when done

After this runs: just `export ZENODO_TOKEN=...` then run _zenodo_newversion.py (adapted for V3).
"""
import os, json, hashlib, zipfile, datetime, io, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DEPLOY = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\_AKTIV\_FIRST_NETWORK_BUILD\_DEPLOY_STAGE_0_50TERMS")
TODAY = datetime.date.today().isoformat()
BUNDLE_NAME = f"augmanitai_stage_0_v3_{TODAY}.zip"
BUNDLE_PATH = DEPLOY.parent / BUNDLE_NAME

INCLUDE_DIRS = ["atlas", "disclaimer", "about", "accessibility", "ai-transparency", "audit",
                "citation", "datenschutz", "impressum", "iso-conformance", "license-of-clarity",
                "licenses", "living-document-policy", "permanitai", "trade-secret-layer",
                "witness-quorum", "exports"]
INCLUDE_FILES = ["index.html", "README.md", "CITATION.cff", "LICENSE", "CNAME",
                 "sitemap.xml", "llms.txt", "ai.txt", "robots.txt", "ROADMAP.md", "NAMESPACE.md",
                 "_ITER18_DEDUPE_MANIFEST.json", "_ITER20_BACKEND_AUDIT_REPORT.md",
                 "_ITER27_QUALITY_DEEP_AUDIT.json", "_ITER30_CLEANUP_MANIFEST.json",
                 "ADVERSARIAL_100_PERSONAS_SPEC.md"]
EXCLUDE_PATTERNS = ["_build_", "_scale_", "_iter1", "_iter2", "_zenodo_", ".git"]


def should_include(path: Path):
    rel = path.relative_to(DEPLOY)
    if rel.parts[0] in INCLUDE_DIRS:
        return True
    if rel.parts[0] in INCLUDE_FILES:
        return True
    # exclude
    name_lower = rel.parts[0].lower()
    for pat in EXCLUDE_PATTERNS:
        if pat in name_lower:
            return False
    return False


def build_bundle():
    n_files = 0
    total_size = 0
    if BUNDLE_PATH.exists():
        BUNDLE_PATH.unlink()
    with zipfile.ZipFile(BUNDLE_PATH, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for f in DEPLOY.rglob("*"):
            if not f.is_file(): continue
            if not should_include(f): continue
            rel = f.relative_to(DEPLOY)
            zf.write(f, arcname=str(rel))
            n_files += 1
            total_size += f.stat().st_size
            if n_files % 2000 == 0:
                print(f"  zipping... {n_files} files / {total_size//1024//1024} MB raw")
    print(f"Bundle written: {BUNDLE_PATH.name}")
    print(f"  Files: {n_files}")
    print(f"  Raw size: {total_size/1024/1024:.1f} MB")
    print(f"  Bundle size: {BUNDLE_PATH.stat().st_size/1024/1024:.1f} MB")
    return n_files


def multi_hash():
    """Compute SHA-256 + SHA-512 + SHA3-256 + SHA3-512 + optionally BLAKE3."""
    hashes = {
        "sha256": hashlib.sha256(),
        "sha512": hashlib.sha512(),
        "sha3_256": hashlib.sha3_256(),
        "sha3_512": hashlib.sha3_512(),
    }
    try:
        import blake3
        hashes["blake3"] = blake3.blake3()
    except Exception:
        hashes["blake3"] = None
    with open(BUNDLE_PATH, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            for h in hashes.values():
                if h is not None: h.update(chunk)
    return {k: h.hexdigest() if h else "BLAKE3_NOT_AVAILABLE" for k, h in hashes.items()}


def main():
    print(f"Building V3 bundle for {TODAY}...")
    n = build_bundle()
    print("\nComputing multi-hash anchor...")
    hashes = multi_hash()
    for k, v in hashes.items():
        print(f"  {k}: {v[:32]}...")

    # Update multi-hash registry
    hash_reg = Path(r"C:\Users\Andreas Ehstand\Desktop\Claude\10_RECHTLICHES\PRIOR_ART_TIMESTAMPS")
    hash_reg.mkdir(parents=True, exist_ok=True)
    multi_reg_path = hash_reg / "MULTI_HASH_REGISTRY_stage0.json"
    if multi_reg_path.exists():
        reg = json.load(open(multi_reg_path, encoding="utf-8"))
    else:
        reg = {"entries": []}
    reg["entries"].append({
        "bundle": BUNDLE_NAME,
        "date": TODAY,
        "version": "V3",
        "concept_doi": "10.5281/zenodo.20118267",
        "n_files": n,
        "size_bytes": BUNDLE_PATH.stat().st_size,
        "hashes": hashes,
    })
    multi_reg_path.write_text(json.dumps(reg, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nMulti-hash registry updated: {multi_reg_path}")

    # Write external manifest for OTS-stamp
    manifest_path = hash_reg / f"MANIFEST_stage0_v3_{TODAY}.txt"
    manifest_path.write_text(
        f"AUGMANITAI Stage-0 V3 Bundle Hash Manifest\n"
        f"Date: {TODAY}\n"
        f"Author: Andreas Ehstand (ORCID 0009-0006-3773-7796, Wikidata Q138634675)\n"
        f"Programme: AUGMANITAI Compendium (Wikidata Q138522830)\n"
        f"Bundle: {BUNDLE_NAME}\n"
        f"Files: {n}\n"
        f"Size: {BUNDLE_PATH.stat().st_size} bytes\n"
        f"Concept-DOI: 10.5281/zenodo.20118267\n"
        f"Predecessor V2-DOI: 10.5281/zenodo.20119072\n\n"
        f"SHA-256: {hashes['sha256']}\n"
        f"SHA-512: {hashes['sha512']}\n"
        f"SHA3-256: {hashes['sha3_256']}\n"
        f"SHA3-512: {hashes['sha3_512']}\n"
        f"BLAKE3: {hashes['blake3']}\n",
        encoding="utf-8"
    )
    print(f"External manifest: {manifest_path}")

    # Sentinel for ready-to-upload
    sentinel = {
        "ready": True,
        "bundle_path": str(BUNDLE_PATH),
        "bundle_name": BUNDLE_NAME,
        "concept_doi": "10.5281/zenodo.20118267",
        "v2_predecessor": "10.5281/zenodo.20119072",
        "n_files": n,
        "size_bytes": BUNDLE_PATH.stat().st_size,
        "hashes": hashes,
        "date": TODAY,
        "next_step": "set ZENODO_TOKEN env var, then run _zenodo_newversion.py (or adapted V3 script)",
    }
    (DEPLOY / "_ITER31_BUNDLE_READY.json").write_text(
        json.dumps(sentinel, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n=== BUNDLE READY ===")
    print(f"Run: $env:ZENODO_TOKEN='...' ; python _zenodo_v3_upload.py")


if __name__ == "__main__":
    main()
