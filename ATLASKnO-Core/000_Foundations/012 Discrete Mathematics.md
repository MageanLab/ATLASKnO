---
id: "https://atlaskno.org/concept/012"
skos:notation: "012"
skos:prefLabel:
  en: "Discrete Mathematics"
skos:altLabel:
  en: ["Finite Mathematics", "Combinatorics & Logic"]
skos:broader:
  - "[[010 Pure Mathematics]]"
skos:narrower:
  - "[[012.3 Graph Theory]]"
skos:scopeNote:
  en: "Study of mathematical structures that are discrete rather than continuous: combinatorics, graph theory, Boolean algebra, and formal languages."
skos:historyNote:
  en: "Formalized in mid-20th century alongside computer science."
node_type: "meso_branch"
layer_depth: 2
is_vacant: false
license: "CC-BY-SA-3.0"
format: "text/markdown"
---

# 012 Discrete Mathematics

## Scope Note

Study of mathematical structures that are discrete rather than continuous: combinatorics, graph theory, Boolean algebra, and formal languages.

## History Note

Formalized in mid-20th century alongside computer science.

## Sub-Classifications

```dataview
TABLE file.link AS "Concept", skos:notation AS "Notation", node_type AS "Type"
FROM "000_Foundations"
WHERE contains(skos:broader, "[[012 Discrete Mathematics]]")
SORT skos:notation ASC
```
