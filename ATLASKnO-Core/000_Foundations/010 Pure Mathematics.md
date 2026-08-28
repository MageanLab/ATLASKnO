---
id: "https://atlaskno.org/concept/010"
skos:notation: "010"
skos:prefLabel:
  en: "Pure Mathematics"
skos:altLabel:
  en: ["Theoretical Mathematics", "Abstract Algebra & Analysis"]
skos:broader:
  - "[[000 Foundations & Formal Systems]]"
skos:narrower:
  - "[[012 Discrete Mathematics]]"
skos:scopeNote:
  en: "Mathematics pursued independently of empirical applications: number theory, algebra, analysis, geometry, and topology."
skos:historyNote:
  en: "Derived from UDC 51 (Mathematics)."
node_type: "meso_branch"
layer_depth: 2
is_vacant: false
license: "CC-BY-SA-3.0"
format: "text/markdown"
---

# 010 Pure Mathematics

## Scope Note

Mathematics pursued independently of empirical applications: number theory, algebra, analysis, geometry, and topology.

## History Note

Derived from UDC 51 (Mathematics).

## Sub-Classifications

```dataview
TABLE file.link AS "Concept", skos:notation AS "Notation", node_type AS "Type"
FROM "000_Foundations"
WHERE contains(skos:broader, "[[010 Pure Mathematics]]")
SORT skos:notation ASC
```
