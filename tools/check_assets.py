#!/usr/bin/env python3
"""Fail when an animation or character file has no provenance, a disallowed licence or Mixamo fingerprints.

Run from anywhere: python3 tools/check_assets.py. CI and debian/rules run it.
"""

import os
import pathlib
import sys

import asset_manifest
import generate_copyright

ASSET_SUFFIXES = (".glb", ".fbx", ".blend")
ASSET_DIRS = ("animations", "characters", "src")
SKIPPED_DIRS = {".git", "debian", "build", "dist", "__pycache__"}
ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"


def find_files(root):
    """Yield (posix relative path, absolute path) for every file outside the skipped directories."""
    for directory, subdirs, names in os.walk(root):
        subdirs[:] = sorted(name for name in subdirs if name not in SKIPPED_DIRS)
        for name in sorted(names):
            path = pathlib.Path(directory, name)
            yield path.relative_to(root).as_posix(), path


def scan_content(relative, path):
    data = path.read_bytes()
    if relative.endswith(".blend") and data.startswith(ZSTD_MAGIC):
        return [f"{relative}: compressed .blend cannot be inspected; save it uncompressed"]
    if b"mixamo" in data.lower():
        return [f"{relative}: contains the Mixamo fingerprint (mixamorig/mixamo)"]
    return []


def check_repository(root):
    """Return a list of problems in the repository at root; an empty list means it passes."""
    root = pathlib.Path(root)
    entries, problems = asset_manifest.load_manifest(root)
    problems += asset_manifest.validate_entries(entries)
    manifest_valid = not problems

    listed = {entry["path"] for entry in entries if isinstance(entry, dict) and isinstance(entry.get("path"), str)}
    present = set()
    for relative, path in find_files(root):
        present.add(relative)
        if "mixamo" in relative.lower():
            problems.append(f"{relative}: file name mentions Mixamo")
        is_asset = relative.lower().endswith(ASSET_SUFFIXES)
        if is_asset and relative not in listed:
            problems.append(f"{relative}: no entry in ASSETS.yaml")
        if is_asset or relative.split("/")[0] in ASSET_DIRS:
            problems += scan_content(relative, path)

    for relative in sorted(listed - present):
        problems.append(f"{relative}: listed in ASSETS.yaml but missing")

    if manifest_valid and not generate_copyright.is_current(root, entries):
        problems.append("debian/copyright is out of sync with ASSETS.yaml; run python3 tools/generate_copyright.py")
    return problems


def main():
    root = pathlib.Path(__file__).resolve().parent.parent
    problems = check_repository(root)
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1
    entries, _ = asset_manifest.load_manifest(root)
    print(f"assets: {len(entries)} manifest entries checked, no problems")
    return 0


if __name__ == "__main__":
    sys.exit(main())
