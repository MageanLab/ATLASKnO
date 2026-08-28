#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Magean Research
"""
scaffold_vault.py
=================
Populates ATLASKnO-Core/ with baseline Markdown note files across Classes 0–9,
Auxiliary Tables, and Synthesized Coordinates.

Every Markdown file contains SKOS-compliant YAML frontmatter mapping to W3C SKOS
data structures, including:
  - id (URI)
  - skos:notation
  - skos:prefLabel (multilingual dictionary)
  - skos:altLabel (multilingual list)
  - skos:broader (list of internal wiki links)
  - skos:narrower (list of internal wiki links)
  - skos:scopeNote (multilingual dictionary)
  - skos:historyNote (multilingual dictionary)
  - node_type, layer_depth, is_vacant, license, format

Body content features:
  - Canonical H1 header
  - Conditional callout banners (Terra Incognita / Synthesized Coordinate)
  - ## Scope Note & ## History Note sections
  - Obsidian Dataview dynamic query block

Run from workspace root:
    python scripts/scaffold_vault.py
"""
from __future__ import annotations

import argparse
import re
import sys
import textwrap
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
VAULT_ROOT = REPO_ROOT / "ATLASKnO-Core"
URI_BASE = "https://atlaskno.org/concept/"
LICENSE = "CC-BY-SA-3.0"
FORMAT = "text/markdown"


# ---------------------------------------------------------------------------
# Data Model
# ---------------------------------------------------------------------------
@dataclass
class VaultNode:
    """Represents a single classification note in the ATLASKnO vault."""

    notation: str                          # Decimal/Faceted notation (e.g. "012.3")
    pref_label_en: str                     # Primary English label
    scope_note_en: str                     # Detailed scope definition
    schedule_dir: str                      # Target directory inside ATLASKnO-Core/
    node_type: str                         # root_class | meso_branch | atomic_concept | reserved_zone | auxiliary_table
    layer_depth: int                       # 1 = root, 2 = meso, 3 = atomic
    alt_labels_en: list[str] = field(default_factory=list)
    history_note_en: str = ""
    broader: list[str] = field(default_factory=list)   # [[wiki links]]
    narrower: list[str] = field(default_factory=list)  # [[wiki links]]
    is_vacant: bool = False
    synthesized: bool = False

    @property
    def node_uri(self) -> str:
        safe_not = re.sub(r"[^A-Za-z0-9._\-:+/\[\]]", "", self.notation)
        return f"{URI_BASE}{safe_not}"

    @property
    def slug(self) -> str:
        clean = re.sub(r"[^a-z0-9]+", "-", self.pref_label_en.lower()).strip("-")
        return clean

    @property
    def filename(self) -> str:
        if self.synthesized:
            return f"[{self.notation}] {self.pref_label_en}.md"
        return f"{self.notation} {self.pref_label_en}.md"

    @property
    def output_path(self) -> Path:
        return VAULT_ROOT / self.schedule_dir / self.filename


# ---------------------------------------------------------------------------
# Predefined Taxonomy Nodes
# ---------------------------------------------------------------------------
NODES: list[VaultNode] = [
    # ── 000 Foundations & Formal Systems ──────────────────────────────────
    VaultNode(
        notation="000",
        pref_label_en="Foundations & Formal Systems",
        alt_labels_en=["Formal Sciences", "Axiomatic Systems", "Abstract Logic"],
        scope_note_en=(
            "Root class encompassing formal, abstract, and foundational disciplines "
            "that supply the axiomatic substrate for all branches of knowledge. "
            "Includes pure logic, set theory, computability, and general systems science."
        ),
        history_note_en="Modernized from UDC Class 0 (Science and Knowledge. Organization).",
        schedule_dir="000_Foundations",
        node_type="root_class",
        layer_depth=1,
        narrower=["[[010 Pure Mathematics]]", "[[012 Discrete Mathematics]]"],
    ),
    VaultNode(
        notation="010",
        pref_label_en="Pure Mathematics",
        alt_labels_en=["Theoretical Mathematics", "Abstract Algebra & Analysis"],
        scope_note_en=(
            "Mathematics pursued independently of empirical applications: number theory, "
            "algebra, analysis, geometry, and topology."
        ),
        history_note_en="Derived from UDC 51 (Mathematics).",
        schedule_dir="000_Foundations",
        node_type="meso_branch",
        layer_depth=2,
        broader=["[[000 Foundations & Formal Systems]]"],
        narrower=["[[012 Discrete Mathematics]]"],
    ),
    VaultNode(
        notation="012",
        pref_label_en="Discrete Mathematics",
        alt_labels_en=["Finite Mathematics", "Combinatorics & Logic"],
        scope_note_en=(
            "Study of mathematical structures that are discrete rather than continuous: "
            "combinatorics, graph theory, Boolean algebra, and formal languages."
        ),
        history_note_en="Formalized in mid-20th century alongside computer science.",
        schedule_dir="000_Foundations",
        node_type="meso_branch",
        layer_depth=2,
        broader=["[[010 Pure Mathematics]]"],
        narrower=["[[012.3 Graph Theory]]"],
    ),
    VaultNode(
        notation="012.3",
        pref_label_en="Graph Theory",
        alt_labels_en=["Network Topology", "Vertex-Edge Relations"],
        scope_note_en=(
            "Formal study of graphs — sets of vertices connected by edges — representing "
            "pairwise relations. Includes planarity, connectivity, spectral theory, and random graphs."
        ),
        history_note_en="Originated from Euler (1736) Seven Bridges of Königsberg problem.",
        schedule_dir="000_Foundations",
        node_type="atomic_concept",
        layer_depth=3,
        broader=["[[012 Discrete Mathematics]]"],
    ),

    # ── 100 Epistemology, Cognition & Sentience ───────────────────────────
    VaultNode(
        notation="100",
        pref_label_en="Epistemology Cognition & Sentience",
        alt_labels_en=["Cognitive Science", "Philosophy of Mind", "Substrate-Agnostic Cognition"],
        scope_note_en=(
            "Root class for the study of knowledge, belief, cognitive architectures, "
            "and consciousness across biological, synthetic, and hybrid substrates."
        ),
        history_note_en="Modernized from UDC Class 1 (Philosophy. Psychology).",
        schedule_dir="100_Epistemology_Cognition",
        node_type="root_class",
        layer_depth=1,
    ),

    # ── 200 Symbolic Systems & Meaning Frameworks ─────────────────────────
    VaultNode(
        notation="200",
        pref_label_en="Symbolic Systems & Meaning Frameworks",
        alt_labels_en=["Semiotics", "Belief Systems", "Ontological Frameworks"],
        scope_note_en=(
            "Root class for systems of symbols, signs, representations, semiotics, "
            "metaphysical frameworks, and belief systems."
        ),
        history_note_en="Modernized from UDC Class 2 (Religion. Theology).",
        schedule_dir="200_Symbolic_Systems",
        node_type="root_class",
        layer_depth=1,
    ),

    # ── 300 Collective Organization & Societal Dynamics ───────────────────
    VaultNode(
        notation="300",
        pref_label_en="Collective Organization & Societal Dynamics",
        alt_labels_en=["Social Systems", "Multi-Agent Organization", "De-Anthropocentrized Sociology"],
        scope_note_en=(
            "Root class for species-agnostic social systems: any aggregate of agents "
            "(biological, synthetic, or hybrid) co-organizing resource allocation, action, and governance."
        ),
        history_note_en="De-anthropocentrized from UDC Class 3 (Social Sciences).",
        schedule_dir="300_Collective_Organization",
        node_type="root_class",
        layer_depth=1,
        narrower=["[[310 Population & Entity Dynamics]]", "[[320 Power Dynamics & Governance]]"],
    ),
    VaultNode(
        notation="310",
        pref_label_en="Population & Entity Dynamics",
        alt_labels_en=["Demographics", "Agent Demography", "Population Ecology"],
        scope_note_en=(
            "Quantitative study of agent populations: growth, dispersal, age-structure, "
            "carrying capacity, and demographic transitions across species and agent collectives."
        ),
        history_note_en="Derived from UDC 314 (Demography).",
        schedule_dir="300_Collective_Organization",
        node_type="meso_branch",
        layer_depth=2,
        broader=["[[300 Collective Organization & Societal Dynamics]]"],
    ),
    VaultNode(
        notation="320",
        pref_label_en="Power Dynamics & Governance",
        alt_labels_en=["Political Science", "Institutional Design", "Control Systems"],
        scope_note_en=(
            "Distribution, exercise, legitimation, and contestation of power and regulatory control "
            "within multi-agent collective systems."
        ),
        history_note_en="Derived from UDC 32 (Politics).",
        schedule_dir="300_Collective_Organization",
        node_type="meso_branch",
        layer_depth=2,
        broader=["[[300 Collective Organization & Societal Dynamics]]"],
    ),

    # ── 400 Terra Incognita (Reserved) ───────────────────────────────────
    VaultNode(
        notation="400",
        pref_label_en="Terra Incognita (Reserved)",
        alt_labels_en=["Epistemic Horizon", "Reserved Expansion Zone"],
        scope_note_en=(
            "Permanently reserved expansion zone marking the epistemic horizon of ATLASKnO. "
            "Deliberately held vacant for unmapped, emergent, or future knowledge domains."
        ),
        history_note_en="Preserves UDC Class 4 (Vacant) convention.",
        schedule_dir="400_Terra_Incognita",
        node_type="reserved_zone",
        layer_depth=1,
        is_vacant=True,
    ),

    # ── 500 Physical & Natural Sciences ──────────────────────────────────
    VaultNode(
        notation="500",
        pref_label_en="Physical & Natural Sciences",
        alt_labels_en=["Hard Sciences", "Empirical Physics & Chemistry"],
        scope_note_en=(
            "Empirical sciences of the physical universe: physics, chemistry, astronomy, "
            "earth sciences, and materials science."
        ),
        history_note_en="Derived from UDC Class 5 (Mathematics and Natural Sciences).",
        schedule_dir="500_Physical_Sciences",
        node_type="root_class",
        layer_depth=1,
    ),

    # ── 600 Complex Adaptive Systems & Technology ────────────────────────
    VaultNode(
        notation="600",
        pref_label_en="Complex Adaptive Systems & Technology",
        alt_labels_en=["Applied Sciences", "Engineering & Biotech", "Computation & Life"],
        scope_note_en=(
            "Root class for complex adaptive systems: biology, ecology, biotechnology, "
            "engineering, computational hardware, and applied technology."
        ),
        history_note_en="Derived from UDC Class 6 (Applied Sciences. Medicine. Technology).",
        schedule_dir="600_Life_Sciences_Tech",
        node_type="root_class",
        layer_depth=1,
    ),

    # ── 700 Aesthetic Expression & Spatial Design ────────────────────────
    VaultNode(
        notation="700",
        pref_label_en="Aesthetic Expression & Spatial Design",
        alt_labels_en=["The Arts", "Architecture", "Sensory Design"],
        scope_note_en=(
            "Root class for visual arts, architecture, performing arts, aesthetic theory, "
            "and spatial design."
        ),
        history_note_en="Derived from UDC Class 7 (The Arts. Recreation. Entertainment. Sport).",
        schedule_dir="700_Aesthetic_Expression",
        node_type="root_class",
        layer_depth=1,
    ),

    # ── 800 Information Transfer & Linguistics ───────────────────────────
    VaultNode(
        notation="800",
        pref_label_en="Information Transfer & Linguistics",
        alt_labels_en=["Communication Science", "Linguistics", "Signaling Protocols"],
        scope_note_en=(
            "Root class for language, signaling, communication theory, semiotics, "
            "media, and information transfer protocols across human and artificial agents."
        ),
        history_note_en="Derived from UDC Class 8 (Language. Linguistics. Literature).",
        schedule_dir="800_Linguistics_Communication",
        node_type="root_class",
        layer_depth=1,
    ),

    # ── 900 Spatiotemporal Topology & Event History ──────────────────────
    VaultNode(
        notation="900",
        pref_label_en="Spatiotemporal Topology & Event History",
        alt_labels_en=["Historiography", "Spatial Geography", "Chronology"],
        scope_note_en=(
            "Root class for geographic, historical, and topological knowledge structured "
            "along space-time coordinates."
        ),
        history_note_en="Derived from UDC Class 9 (Geography. Biography. History).",
        schedule_dir="900_Spatiotemporal_Topology",
        node_type="root_class",
        layer_depth=1,
    ),

    # ── Auxiliary Tables ──────────────────────────────────────────────────
    VaultNode(
        notation="=1",
        pref_label_en="Language Form",
        alt_labels_en=["Linguistic Medium", "Textual Representation"],
        scope_note_en="Auxiliary table specifying language medium, script, or linguistic format.",
        history_note_en="Derived from UDC Table 1c (Language auxiliary).",
        schedule_dir="Auxiliary_Tables/Form",
        node_type="auxiliary_table",
        layer_depth=2,
    ),
    VaultNode(
        notation="(4)",
        pref_label_en="Europe",
        alt_labels_en=["European Geographic Sphere"],
        scope_note_en="Auxiliary spatial coordinate denoting European geographic boundary.",
        history_note_en="Derived from UDC Table 1e (Place auxiliary).",
        schedule_dir="Auxiliary_Tables/Place",
        node_type="auxiliary_table",
        layer_depth=2,
    ),

    # ── Synthesized Coordinates ───────────────────────────────────────────
    VaultNode(
        notation="012.3:310",
        pref_label_en="Topological Dynamics of Collective Populations",
        alt_labels_en=["Graph Demography", "Network Population Dynamics"],
        scope_note_en=(
            "Synthesized analytico-synthetic coordinate linking Graph Theory (012.3) "
            "with Population Dynamics (310). Models agent populations as dynamic graphs "
            "where topology co-evolves with demographic events."
        ),
        history_note_en="Synthesized coordinate using UDC relation operator ':'.",
        schedule_dir="Synthesized_Coordinates",
        node_type="atomic_concept",
        layer_depth=3,
        broader=["[[012.3 Graph Theory]]", "[[310 Population & Entity Dynamics]]"],
        synthesized=True,
    ),
]


# ---------------------------------------------------------------------------
# Generator Functions
# ---------------------------------------------------------------------------
def build_yaml_frontmatter(node: VaultNode) -> str:
    """Generate W3C SKOS-compliant YAML frontmatter."""
    alt_list = ", ".join(f'"{a}"' for a in node.alt_labels_en)
    broader_list = "\n".join(f'  - "{b}"' for b in node.broader) if node.broader else "[]"
    narrower_list = "\n".join(f'  - "{n}"' for n in node.narrower) if node.narrower else "[]"

    lines = [
        "---",
        f'id: "{node.node_uri}"',
        'skos:notation: "' + node.notation + '"',
        "skos:prefLabel:",
        f'  en: "{node.pref_label_en}"',
        "skos:altLabel:",
        f"  en: [{alt_list}]",
        "skos:broader:",
        f"{broader_list}",
        "skos:narrower:",
        f"{narrower_list}",
        "skos:scopeNote:",
        f'  en: "{node.scope_note_en}"',
        "skos:historyNote:",
        f'  en: "{node.history_note_en}"',
        f'node_type: "{node.node_type}"',
        f"layer_depth: {node.layer_depth}",
        f"is_vacant: {str(node.is_vacant).lower()}",
        f'license: "{LICENSE}"',
        f'format: "{FORMAT}"',
        "---",
    ]
    return "\n".join(lines) + "\n"


def build_markdown_body(node: VaultNode) -> str:
    """Generate Markdown body with callouts and Dataview queries."""
    content = []
    content.append(f"# {node.notation} {node.pref_label_en}\n")

    if node.is_vacant:
        content.append(
            "> [!CAUTION]\n"
            "> **Terra Incognita (Vacant Zone)** — This coordinate is permanently reserved. "
            "No sub-classifications are instantiated.\n"
        )
    elif node.synthesized:
        content.append(
            "> [!NOTE]\n"
            "> **Synthesized Coordinate** — This analytico-synthetic node bridges two or more "
            "root schedules via UDC operators. See `skos:broader` links for parent coordinates.\n"
        )

    content.append("## Scope Note\n")
    content.append(f"{node.scope_note_en}\n")

    if node.history_note_en:
        content.append("## History Note\n")
        content.append(f"{node.history_note_en}\n")

    if not node.is_vacant:
        content.append("## Sub-Classifications\n")
        content.append("```dataview")
        content.append("TABLE file.link AS \"Concept\", skos:notation AS \"Notation\", node_type AS \"Type\"")
        content.append(f'FROM "{node.schedule_dir}"')
        content.append(f'WHERE contains(skos:broader, "[[{node.filename[:-3]}]]")')
        content.append("SORT skos:notation ASC")
        content.append("```\n")

    return "\n".join(content)


def scaffold_vault(dry_run: bool = False) -> None:
    created = 0
    for node in NODES:
        target_path = node.output_path
        target_path.parent.mkdir(parents=True, exist_ok=True)

        fm = build_yaml_frontmatter(node)
        body = build_markdown_body(node)
        full_text = fm + "\n" + body

        if dry_run:
            print(f"[DRY-RUN] Would write: {target_path.relative_to(REPO_ROOT)}")
        else:
            target_path.write_text(full_text, encoding="utf-8")
            print(f"[WRITE] Created {target_path.relative_to(REPO_ROOT)}")
            created += 1

    print(f"\n[OK] Vault scaffolding complete. {created} file(s) generated.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold ATLASKnO vault markdown files.")
    parser.add_argument("--dry-run", action="store_true", help="Preview generated output without writing.")
    args = parser.parse_args()
    scaffold_vault(dry_run=args.dry_run)
