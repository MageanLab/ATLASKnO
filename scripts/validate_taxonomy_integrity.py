#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Magean Research
"""
Validate taxonomy and graph integrity for ATLASKnO SKOS data.

Performs three categories of checks:

1. **Cycle Detection** — DFS-based detection of circular references in
   ``skos:broader`` / ``skos:narrower`` hierarchies.
2. **Broken URI Detection** — Verifies that all ``skos:broader`` /
   ``skos:narrower`` object URIs reference subjects that exist within the
   loaded graph.
3. **Faceted Operator Validation** — Validates that notation strings only
   contain legal UDC faceted operators: ``+``, ``:``, ``/``, ``[ ]``.

Exit codes:
    0 — all checks passed (or no data found)
    1 — one or more integrity violations detected
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, SKOS

SCAN_DIRS: list[str] = ["dist", "data", "schedules", "ATLASKnO-Core"]
FORMAT_MAP: dict[str, str] = {
    ".ttl": "turtle",
    ".rdf": "xml",
    ".xml": "xml",
    ".jsonld": "json-ld",
    ".nt": "nt",
    ".n3": "n3",
}

# Faceted operators allowed in UDC notations
# + (addition), : (relation), / (extension), [ ] (subgrouping)
VALID_OPERATORS_RE = re.compile(r"^[A-Za-z0-9.\-()'+:/\[\] =\"]*$")


def _load_all_rdf(root: Path) -> Graph:
    """Load all RDF files from scan directories into a single graph."""
    g = Graph()
    for dirname in SCAN_DIRS:
        scan_path = root / dirname
        if not scan_path.is_dir():
            continue
        for ext, fmt in FORMAT_MAP.items():
            for filepath in scan_path.rglob(f"*{ext}"):
                try:
                    g.parse(str(filepath), format=fmt)
                except Exception:  # noqa: BLE001
                    # Syntax errors are caught by validate_rdf_syntax.py
                    pass
    return g


def check_cycles(g: Graph) -> list[str]:
    """Detect cycles in skos:broader hierarchy using iterative DFS."""
    errors: list[str] = []

    # Build adjacency list: child -> [parents]
    adj: dict[URIRef, list[URIRef]] = defaultdict(list)
    for s, _p, o in g.triples((None, SKOS.broader, None)):
        if isinstance(s, URIRef) and isinstance(o, URIRef):
            adj[s].append(o)

    visited: set[URIRef] = set()
    on_stack: set[URIRef] = set()

    for start_node in adj:
        if start_node in visited:
            continue

        stack: list[tuple[URIRef, int]] = [(start_node, 0)]

        while stack:
            node, idx = stack.pop()

            if idx == 0:
                if node in on_stack:
                    # Cycle detected — reconstruct the cycle path
                    cycle_nodes = [str(n) for n, _ in stack] + [str(node)]
                    errors.append(f"Cycle detected: {' → '.join(cycle_nodes[-4:])}")
                    continue
                if node in visited:
                    continue
                on_stack.add(node)

            neighbours = adj.get(node, [])
            if idx < len(neighbours):
                stack.append((node, idx + 1))
                stack.append((neighbours[idx], 0))
            else:
                on_stack.discard(node)
                visited.add(node)

    return errors


def check_broken_uris(g: Graph) -> list[str]:
    """Check that broader/narrower targets reference existing subjects."""
    errors: list[str] = []

    # Collect all subjects in the graph
    subjects: set[URIRef] = set()
    for s in g.subjects():
        if isinstance(s, URIRef):
            subjects.add(s)

    # Check broader links
    for s, _p, o in g.triples((None, SKOS.broader, None)):
        if isinstance(o, URIRef) and o not in subjects:
            errors.append(f"Broken broader URI: {s} → {o} (target not found as subject)")

    # Check narrower links
    for s, _p, o in g.triples((None, SKOS.narrower, None)):
        if isinstance(o, URIRef) and o not in subjects:
            errors.append(f"Broken narrower URI: {s} → {o} (target not found as subject)")

    return errors


def check_faceted_operators(g: Graph) -> list[str]:
    """Validate that notation values only use legal UDC faceted operators."""
    errors: list[str] = []

    for s, _p, o in g.triples((None, SKOS.notation, None)):
        notation = str(o)
        if not VALID_OPERATORS_RE.match(notation):
            # Identify the invalid characters
            invalid_chars = set()
            for ch in notation:
                if not re.match(r"[A-Za-z0-9.\-()'+:/\[\] =\"]", ch):
                    invalid_chars.add(ch)
            errors.append(
                f"Invalid notation '{notation}' on {s} — "
                f"illegal characters: {invalid_chars}"
            )

    return errors


def validate(root: Path) -> int:
    """Run all integrity checks.  Returns exit code."""
    g = _load_all_rdf(root)

    if len(g) == 0:
        print("[INFO] No RDF triples loaded -- nothing to validate.")
        return 0

    print(f"[INFO] Loaded {len(g)} triples from data files.\n")

    all_errors: list[str] = []

    # 1. Cycle detection
    print("[CHECK] Checking for circular references...")
    cycle_errors = check_cycles(g)
    if cycle_errors:
        all_errors.extend(cycle_errors)
        print(f"   [FAIL] Found {len(cycle_errors)} cycle(s)")
    else:
        print("   [OK] No cycles detected")

    # 2. Broken URI detection
    print("[CHECK] Checking for broken URI references...")
    uri_errors = check_broken_uris(g)
    if uri_errors:
        all_errors.extend(uri_errors)
        print(f"   [FAIL] Found {len(uri_errors)} broken URI(s)")
    else:
        print("   [OK] All URI references are valid")

    # 3. Faceted operator validation
    print("[CHECK] Checking faceted operator syntax...")
    op_errors = check_faceted_operators(g)
    if op_errors:
        all_errors.extend(op_errors)
        print(f"   [FAIL] Found {len(op_errors)} invalid notation(s)")
    else:
        print("   [OK] All notations use valid operators")

    if all_errors:
        print(f"\n[ERROR] Total: {len(all_errors)} integrity issue(s):\n")
        for err in all_errors:
            print(f"  * {err}")
        return 1

    print("\n[OK] All taxonomy integrity checks passed.")
    return 0


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent
    sys.exit(validate(repo_root))
