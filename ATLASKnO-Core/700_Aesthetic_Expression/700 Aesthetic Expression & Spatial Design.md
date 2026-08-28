---
id: "https://atlaskno.org/concept/700"
skos:notation: "700"
skos:prefLabel:
  en: "Aesthetic Expression & Spatial Design"
skos:altLabel:
  en: ["The Arts", "Architecture", "Sensory Design"]
skos:broader:
[]
skos:narrower:
[]
skos:scopeNote:
  en: "Root class for visual arts, architecture, performing arts, aesthetic theory, and spatial design."
skos:historyNote:
  en: "Derived from UDC Class 7 (The Arts. Recreation. Entertainment. Sport)."
node_type: "root_class"
layer_depth: 1
is_vacant: false
license: "CC-BY-SA-3.0"
format: "text/markdown"
---

# 700 Aesthetic Expression & Spatial Design

## Scope Note

Root class for visual arts, architecture, performing arts, aesthetic theory, and spatial design.

## History Note

Derived from UDC Class 7 (The Arts. Recreation. Entertainment. Sport).

## Sub-Classifications

```dataview
TABLE file.link AS "Concept", skos:notation AS "Notation", node_type AS "Type"
FROM "700_Aesthetic_Expression"
WHERE contains(skos:broader, "[[700 Aesthetic Expression & Spatial Design]]")
SORT skos:notation ASC
```
