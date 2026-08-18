#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Magean Research
"""
Validate RDF/SKOS syntax for all semantic data files in the repository.

Walks ``data/`` and ``schedules/`` directories and attempts to parse every
recognised RDF file (.ttl, .rdf, .xml, .jsonld, .json, .nt, .n3) with
``rdflib``.  Reports parse errors with file path and error detail.

Exit codes:
    0 — all files parsed successfully (or no files found)
    1 — one or more parse failures detected
"""
from __future__ import annotations

import sys
from pathlib import Path

from rdflib import Graph

# Mapping of file extensions to rdflib format identifiers
FORMAT_MAP: dict[str, str] = {
    ".ttl": "turtle",
    ".rdf": "xml",
    ".xml": "xml",
    ".jsonld": "json-ld",
    ".nt": "nt",
    ".n3": "n3",
}

# Directories to scan (relative to repo root)
SCAN_DIRS: list[str] = ["data", "schedules"]


def _discover_files(root: Path) -> list[Path]:
    """Discover all RDF files under the configured scan directories."""
    files: list[Path] = []
    for dirname in SCAN_DIRS:
        scan_path = root / dirname
        if not scan_path.is_dir():
            continue
        for ext in FORMAT_MAP:
            files.extend(scan_path.rglob(f"*{ext}"))
    return sorted(files)


def _try_parse_json_as_jsonld(filepath: Path) -> tuple[bool, str]:
    """Attempt to parse a .json file as JSON-LD.  Return (success, error)."""
    g = Graph()
    try:
        g.parse(str(filepath), format="json-ld")
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)
    return True, ""


def validate(root: Path) -> int:
    """Validate all discovered RDF files.  Returns exit code."""
    files = _discover_files(root)

    if not files:
        print("ℹ️  No RDF data files found — nothing to validate.")
        return 0

    errors: list[tuple[Path, str]] = []
    validated = 0

    for filepath in files:
        ext = filepath.suffix.lower()

        # For .json files, try JSON-LD first; skip silently if it's plain JSON
        if ext == ".json":
            ok, err = _try_parse_json_as_jsonld(filepath)
            if not ok:
                # Check if it's intentionally a non-RDF JSON file
                try:
                    import json

                    with open(filepath) as f:
                        data = json.load(f)
                    # If it parses as JSON but not JSON-LD and has no @context,
                    # it's likely a plain config/data JSON — skip it.
                    if isinstance(data, dict) and "@context" not in data:
                        continue
                except Exception:  # noqa: BLE001
                    pass
                errors.append((filepath, err))
            validated += 1
            continue

        fmt = FORMAT_MAP.get(ext)
        if fmt is None:
            continue

        g = Graph()
        try:
            g.parse(str(filepath), format=fmt)
            validated += 1
        except Exception as exc:  # noqa: BLE001
            errors.append((filepath, str(exc)))
            validated += 1

    print(f"✅ Scanned {validated} file(s)")

    if errors:
        print(f"\n❌ {len(errors)} file(s) failed RDF syntax validation:\n")
        for filepath, err in errors:
            rel = filepath.relative_to(root)
            print(f"  FAIL  {rel}")
            print(f"        {err}\n")
        return 1

    print("✅ All RDF files passed syntax validation.")
    return 0


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent
    sys.exit(validate(repo_root))
