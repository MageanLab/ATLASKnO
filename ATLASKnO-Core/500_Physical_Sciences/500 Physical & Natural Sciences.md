---
id: "https://atlaskno.org/concept/500"
skos:notation: "500"
skos:prefLabel:
  en: "Physical & Natural Sciences"
skos:altLabel:
  en: ["Hard Sciences", "Empirical Physics & Chemistry"]
skos:broader: []
skos:narrower: []
skos:scopeNote:
  en: "Empirical sciences of the physical universe: physics, chemistry, astronomy, earth sciences, and materials science."
skos:historyNote:
  en: "Derived from UDC Class 5 (Mathematics and Natural Sciences)."
node_type: "root_class"
layer_depth: 1
is_vacant: false
license: "CC-BY-SA-3.0"
format: "text/markdown"
---

# 500 Physical & Natural Sciences

## Scope Note

Empirical sciences of the physical universe: physics, chemistry, astronomy, earth sciences, and materials science.

## History Note

Derived from UDC Class 5 (Mathematics and Natural Sciences).

## Sub-Classifications

```dataview
TABLE file.link AS "Concept", skos:notation AS "Notation", node_type AS "Type"
FROM "500_Physical_Sciences"
WHERE contains(skos:broader, "[[500 Physical & Natural Sciences]]")
SORT skos:notation ASC
```
