---
id: "https://atlaskno.org/concept/000"
skos:notation: "000"
skos:prefLabel:
  en: "Foundations & Formal Systems"
skos:altLabel:
  en: ["Formal Sciences", "Axiomatic Systems", "Abstract Logic"]
skos:broader:
[]
skos:narrower:
  - "[[010 Pure Mathematics]]"
  - "[[012 Discrete Mathematics]]"
skos:scopeNote:
  en: "Root class encompassing formal, abstract, and foundational disciplines that supply the axiomatic substrate for all branches of knowledge. Includes pure logic, set theory, computability, and general systems science."
skos:historyNote:
  en: "Modernized from UDC Class 0 (Science and Knowledge. Organization)."
node_type: "root_class"
layer_depth: 1
is_vacant: false
license: "CC-BY-SA-3.0"
format: "text/markdown"
---

# 000 Foundations & Formal Systems

## Scope Note

Root class encompassing formal, abstract, and foundational disciplines that supply the axiomatic substrate for all branches of knowledge. Includes pure logic, set theory, computability, and general systems science.

## History Note

Modernized from UDC Class 0 (Science and Knowledge. Organization).

## Sub-Classifications

```dataview
TABLE file.link AS "Concept", skos:notation AS "Notation", node_type AS "Type"
FROM "000_Foundations"
WHERE contains(skos:broader, "[[000 Foundations & Formal Systems]]")
SORT skos:notation ASC
```
