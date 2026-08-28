# License: MIT License (c) 2026 Magean Research
import os

CLASSES = {
    "000": ("Foundations", "Foundations & Formal Systems", False),
    "100": ("Epistemology_Cognition", "Epistemology, Cognition & Sentience", False),
    "200": ("Symbolic_Systems", "Symbolic Systems & Meaning Frameworks", False),
    "300": ("Collective_Organization", "Collective Organization & Societal Dynamics", False),
    "400": ("Terra_Incognita", "Terra Incognita (Reserved)", True),
    "500": ("Physical_Sciences", "Physical & Natural Sciences", False),
    "600": ("Life_Sciences_Tech", "Complex Adaptive Systems & Technology", False),
    "700": ("Aesthetic_Expression", "Aesthetic Expression & Spatial Design", False),
    "800": ("Linguistics_Communication", "Information Transfer & Linguistics", False),
    "900": ("Spatiotemporal_Topology", "Spatiotemporal Topology & Event History", False)
}

def generate_markdown():
    base_dir = "ATLASKnO-Core"
    for notation, (folder, title, is_vacant) in CLASSES.items():
        dir_path = os.path.join(base_dir, f"{notation}_{folder}")
        file_path = os.path.join(dir_path, f"{notation} {title}.md")
        
        yaml_frontmatter = f"""---
id: "atlaskno:{notation}"
skos:notation: "{notation}"
skos:prefLabel: "{title}"
skos:broader: []
skos:narrower: []
is_vacant: {str(is_vacant).lower()}
license: "CC-BY-SA-3.0"
---

# {title}

"""
        if is_vacant:
            yaml_frontmatter += "> **System Notice:** Class 4 is deliberately unassigned to ensure notational hospitality for emerging structural orders of reality.\n"
        else:
            yaml_frontmatter += """## Sub-Classifications
```dataview
TABLE skos:notation AS "Notation", skos:prefLabel AS "Concept"
WHERE contains(skos:broader, this.file.link)
SORT skos:notation ASC
```
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(yaml_frontmatter)

if __name__ == "__main__":
    generate_markdown()
    print("Vault scaffolded successfully.")
