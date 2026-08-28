---
id: "https://atlaskno.org/concept/4"
skos:notation: "(4)"
skos:prefLabel:
  en: "Europe"
skos:altLabel:
  en: ["European Geographic Sphere"]
skos:broader: []
skos:narrower: []
skos:scopeNote:
  en: "Auxiliary spatial coordinate denoting European geographic boundary."
skos:historyNote:
  en: "Derived from UDC Table 1e (Place auxiliary)."
node_type: "auxiliary_table"
layer_depth: 2
is_vacant: false
license: "CC-BY-SA-3.0"
format: "text/markdown"
---

# (4) Europe

## Scope Note

Auxiliary spatial coordinate denoting European geographic boundary.

## History Note

Derived from UDC Table 1e (Place auxiliary).

## Sub-Classifications

```dataview
TABLE file.link AS "Concept", skos:notation AS "Notation", node_type AS "Type"
FROM "Auxiliary_Tables/Place"
WHERE contains(skos:broader, "[[(4) Europe]]")
SORT skos:notation ASC
```
