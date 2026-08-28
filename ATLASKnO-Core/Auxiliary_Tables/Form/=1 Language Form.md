---
id: "https://atlaskno.org/concept/1"
skos:notation: "=1"
skos:prefLabel:
  en: "Language Form"
skos:altLabel:
  en: ["Linguistic Medium", "Textual Representation"]
skos:broader: []
skos:narrower: []
skos:scopeNote:
  en: "Auxiliary table specifying language medium, script, or linguistic format."
skos:historyNote:
  en: "Derived from UDC Table 1c (Language auxiliary)."
node_type: "auxiliary_table"
layer_depth: 2
is_vacant: false
license: "CC-BY-SA-3.0"
format: "text/markdown"
---

# =1 Language Form

## Scope Note

Auxiliary table specifying language medium, script, or linguistic format.

## History Note

Derived from UDC Table 1c (Language auxiliary).

## Sub-Classifications

```dataview
TABLE file.link AS "Concept", skos:notation AS "Notation", node_type AS "Type"
FROM "Auxiliary_Tables/Form"
WHERE contains(skos:broader, "[[=1 Language Form]]")
SORT skos:notation ASC
```
