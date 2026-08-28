#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Magean Research
"""
atlas_export.py
===============
Semantic Export Engine for ATLASKnO.

Parses Markdown YAML frontmatter across `ATLASKnO-Core/` and serializes the vault
into a W3C-compliant Linked Open Data graph (SKOS ontology).

Outputs:
  - dist/atlaskno_core.ttl    (Turtle format)
  - dist/atlaskno_core.jsonld (JSON-LD format)

Handles synthesized coordinates (e.g. `012.3:310`) by creating RDF Blank Nodes
representing complex SKOS coordination structures.

Run from workspace root:
    python scripts/atlas_export.py
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS, SKOS

# ---------------------------------------------------------------------------
# Constants & Namespaces
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
VAULT_ROOT = REPO_ROOT / "ATLASKnO-Core"
DIST_DIR = REPO_ROOT / "dist"

ATLASKNO = Namespace("https://atlaskno.org/concept/")


# ---------------------------------------------------------------------------
# Frontmatter Parser
# ---------------------------------------------------------------------------
def parse_frontmatter(file_path: Path) -> dict[str, Any]:
    """Extract and parse YAML frontmatter from a Markdown file."""
    text = file_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}

    yaml_text = parts[1].strip()

    # Try PyYAML if available
    try:
        import yaml
        return yaml.safe_load(yaml_text) or {}
    except ImportError:
        pass

    # Basic fallback YAML parser for required frontmatter fields
    data: dict[str, Any] = {}
    current_key = None

    for line in yaml_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if ":" in line and not line.startswith("-"):
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()

            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            elif val.startswith("'") and val.endswith("'"):
                val = val[1:-1]

            if key in ["skos:prefLabel", "skos:altLabel", "skos:scopeNote", "skos:historyNote"]:
                current_key = key
                data[current_key] = {}
            elif val in ["[]", ""]:
                data[key] = []
            elif val.startswith("[") and val.endswith("]"):
                items = [i.strip(" \"'") for i in val[1:-1].split(",") if i.strip()]
                data[key] = items
            else:
                data[key] = val
        elif line.startswith("en:") and current_key:
            val = line[3:].strip().strip("\"'")
            if val.startswith("[") and val.endswith("]"):
                items = [i.strip(" \"'") for i in val[1:-1].split(",") if i.strip()]
                data[current_key]["en"] = items
            else:
                data[current_key]["en"] = val

    return data


def extract_notation_from_wikilink(link: str) -> str:
    """Extract notation string from a [[...]] wiki link."""
    clean = link.strip("[]'\" ")
    # Match pattern like "012 Discrete Mathematics" -> "012"
    # or "[012.3:310] Topological..." -> "012.3:310"
    match = re.match(r"^\[?([A-Za-z0-9._\-:+/()]+)\]?\s*", clean)
    if match:
        return match.group(1)
    return clean


# ---------------------------------------------------------------------------
# Graph Builder
# ---------------------------------------------------------------------------
def build_skos_graph(vault_path: Path) -> Graph:
    """Construct an RDFLib Graph representing the entire vault ontology."""
    g = Graph()
    g.bind("atlaskno", ATLASKNO)
    g.bind("skos", SKOS)
    g.bind("dcterms", DCTERMS)

    # Main ConceptScheme resource
    scheme_uri = URIRef("https://atlaskno.org/scheme/core")
    g.add((scheme_uri, RDF.type, SKOS.ConceptScheme))
    g.add((scheme_uri, DCTERMS.title, Literal("ATLASKnO Core Knowledge Taxonomy", lang="en")))
    g.add((scheme_uri, DCTERMS.creator, Literal("Magean Research")))
    g.add((scheme_uri, DCTERMS.license, URIRef("https://creativecommons.org/licenses/by-sa/3.0/")))

    md_files = sorted(vault_path.rglob("*.md"))

    for md_file in md_files:
        fm = parse_frontmatter(md_file)
        if not fm or "skos:notation" not in fm:
            continue

        notation = str(fm["skos:notation"])

        # Determine subject URI
        if "id" in fm and str(fm["id"]).startswith("http"):
            subject_uri = URIRef(fm["id"])
        else:
            safe_not = re.sub(r"[^A-Za-z0-9._\-:+/\[\]]", "", notation)
            subject_uri = URIRef(f"https://atlaskno.org/concept/{safe_not}")

        # Declare SKOS Concept
        g.add((subject_uri, RDF.type, SKOS.Concept))
        g.add((subject_uri, SKOS.inScheme, scheme_uri))
        g.add((subject_uri, SKOS.notation, Literal(notation)))

        # PrefLabel
        pref_label = fm.get("skos:prefLabel", {})
        if isinstance(pref_label, dict):
            for lang, val in pref_label.items():
                g.add((subject_uri, SKOS.prefLabel, Literal(val, lang=lang)))
        elif isinstance(pref_label, str):
            g.add((subject_uri, SKOS.prefLabel, Literal(pref_label, lang="en")))

        # AltLabel
        alt_label = fm.get("skos:altLabel", {})
        if isinstance(alt_label, dict):
            for lang, vals in alt_label.items():
                if isinstance(vals, list):
                    for v in vals:
                        g.add((subject_uri, SKOS.altLabel, Literal(v, lang=lang)))
                elif isinstance(vals, str):
                    g.add((subject_uri, SKOS.altLabel, Literal(vals, lang=lang)))

        # ScopeNote
        scope_note = fm.get("skos:scopeNote", {})
        if isinstance(scope_note, dict):
            for lang, val in scope_note.items():
                g.add((subject_uri, SKOS.scopeNote, Literal(val, lang=lang)))
        elif isinstance(scope_note, str):
            g.add((subject_uri, SKOS.scopeNote, Literal(scope_note, lang="en")))

        # HistoryNote
        history_note = fm.get("skos:historyNote", {})
        if isinstance(history_note, dict):
            for lang, val in history_note.items():
                g.add((subject_uri, SKOS.historyNote, Literal(val, lang=lang)))
        elif isinstance(history_note, str):
            g.add((subject_uri, SKOS.historyNote, Literal(history_note, lang="en")))

        # Broader relations
        broader_links = fm.get("skos:broader", [])
        if isinstance(broader_links, list):
            for link in broader_links:
                target_not = extract_notation_from_wikilink(str(link))
                if target_not:
                    target_uri = URIRef(f"https://atlaskno.org/concept/{target_not}")
                    g.add((subject_uri, SKOS.broader, target_uri))

        # Narrower relations
        narrower_links = fm.get("skos:narrower", [])
        if isinstance(narrower_links, list):
            for link in narrower_links:
                target_not = extract_notation_from_wikilink(str(link))
                if target_not:
                    target_uri = URIRef(f"https://atlaskno.org/concept/{target_not}")
                    g.add((subject_uri, SKOS.narrower, target_uri))

        # TopConcept check (root classes)
        if fm.get("node_type") == "root_class" or fm.get("layer_depth") == 1:
            g.add((scheme_uri, SKOS.hasTopConcept, subject_uri))
            g.add((subject_uri, SKOS.topConceptOf, scheme_uri))

        # -------------------------------------------------------------------
        # Synthesized Coordinates -> RDF Blank Node Construction
        # -------------------------------------------------------------------
        if ":" in notation or "+" in notation or fm.get("synthesized"):
            synth_bnode = BNode()
            g.add((subject_uri, DCTERMS.relation, synth_bnode))
            g.add((synth_bnode, RDF.type, SKOS.Collection))
            g.add((synth_bnode, SKOS.notation, Literal(notation)))
            g.add((synth_bnode, RDFS.label, Literal(f"Synthesized Structure for {notation}", lang="en")))

            # Extract components from operator notation
            components = re.split(r"[:+]", notation)
            for comp in components:
                comp_not = comp.strip()
                if comp_not:
                    comp_uri = URIRef(f"https://atlaskno.org/concept/{comp_not}")
                    g.add((synth_bnode, SKOS.member, comp_uri))
                    g.add((subject_uri, SKOS.related, comp_uri))

    return g


# ---------------------------------------------------------------------------
# Exporter
# ---------------------------------------------------------------------------
def export_vault(dry_run: bool = False) -> None:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    g = build_skos_graph(VAULT_ROOT)

    print(f"📊 Graph built with {len(g)} RDF triples.")

    ttl_file = DIST_DIR / "atlaskno_core.ttl"
    jsonld_file = DIST_DIR / "atlaskno_core.jsonld"

    if dry_run:
        print(f"[DRY-RUN] Would serialize to {ttl_file} and {jsonld_file}")
        return

    g.serialize(destination=str(ttl_file), format="turtle")
    print(f"[WRITE] Serialized Turtle RDF -> {ttl_file.relative_to(REPO_ROOT)}")

    g.serialize(destination=str(jsonld_file), format="json-ld")
    print(f"[WRITE] Serialized JSON-LD RDF -> {jsonld_file.relative_to(REPO_ROOT)}")

    print("\n[OK] Semantic RDF Graph export completed successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export ATLASKnO vault to RDF formats.")
    parser.add_argument("--dry-run", action="store_true", help="Preview export without writing.")
    args = parser.parse_args()
    export_vault(dry_run=args.dry_run)
