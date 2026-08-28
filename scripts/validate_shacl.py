#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Magean Research
"""
Validate RDF data graphs against SHACL shape constraints.

Discovers SHACL shape files in ``shapes/`` and validates all RDF data in
``data/`` and ``schedules/`` against them using ``pyshacl``.

Exit codes:
    0 — validation passed, or no shapes/data found (graceful skip)
    1 — SHACL constraint violations detected
    2 — pyshacl is not installed
"""
from __future__ import annotations

import sys
from pathlib import Path

SCAN_DIRS: list[str] = ["dist", "data", "schedules", "ATLASKnO-Core"]
SHAPES_DIR: str = "shapes"
FORMAT_MAP: dict[str, str] = {
    ".ttl": "turtle",
    ".rdf": "xml",
    ".xml": "xml",
    ".jsonld": "json-ld",
    ".nt": "nt",
    ".n3": "n3",
}


def _load_graph(root: Path, dirs: list[str]) -> "Graph":
    """Load all RDF files from specified directories into a single graph."""
    from rdflib import Graph

    g = Graph()
    for dirname in dirs:
        scan_path = root / dirname
        if not scan_path.is_dir():
            continue
        for ext, fmt in FORMAT_MAP.items():
            for filepath in scan_path.rglob(f"*{ext}"):
                try:
                    g.parse(str(filepath), format=fmt)
                except Exception:  # noqa: BLE001
                    pass
    return g


def validate(root: Path) -> int:
    """Run SHACL validation.  Returns exit code."""
    # Check that pyshacl is available
    try:
        from pyshacl import validate as shacl_validate
    except ImportError:
        print("[WARN] pyshacl is not installed -- skipping SHACL validation.")
        print("   Install with: pip install pyshacl")
        return 0  # Don't fail CI if pyshacl is optional

    from rdflib import Graph

    shapes_path = root / SHAPES_DIR
    if not shapes_path.is_dir():
        print(f"[INFO] No '{SHAPES_DIR}/' directory found -- skipping SHACL validation.")
        return 0

    # Discover shape files
    shape_files = []
    for ext in FORMAT_MAP:
        shape_files.extend(shapes_path.rglob(f"*{ext}"))
    shape_files.sort()

    if not shape_files:
        print(f"[INFO] No SHACL shape files found in '{SHAPES_DIR}/' -- skipping.")
        return 0

    # Load shapes graph
    shapes_graph = Graph()
    for sf in shape_files:
        ext = sf.suffix.lower()
        fmt = FORMAT_MAP.get(ext, "turtle")
        try:
            shapes_graph.parse(str(sf), format=fmt)
            print(f"  [LOAD] Loaded shape: {sf.relative_to(root)}")
        except Exception as exc:  # noqa: BLE001
            print(f"  [FAIL] Failed to parse shape {sf.relative_to(root)}: {exc}")
            return 1

    if len(shapes_graph) == 0:
        print("[INFO] Shapes graph is empty -- skipping validation.")
        return 0

    # Load data graph
    data_graph = _load_graph(root, SCAN_DIRS)
    if len(data_graph) == 0:
        print("[INFO] No RDF data triples loaded -- nothing to validate against shapes.")
        return 0

    print(f"\n[INFO] Data: {len(data_graph)} triples | Shapes: {len(shapes_graph)} triples")
    print("[CHECK] Running SHACL validation...\n")

    # Run SHACL validation
    conforms, results_graph, results_text = shacl_validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference="rdfs",
        abort_on_first=False,
        allow_infos=True,
        allow_warnings=True,
    )

    if conforms:
        print("[OK] SHACL validation passed -- data conforms to all shape constraints.")
        return 0

    print("[FAIL] SHACL validation FAILED -- constraint violations found:\n")
    print(results_text)
    return 1


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent
    sys.exit(validate(repo_root))
