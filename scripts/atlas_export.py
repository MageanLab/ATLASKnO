# License: MIT License (c) 2026 Magean Research
import os
import yaml
from rdflib import Graph, Literal, Namespace, URIRef, BNode
from rdflib.namespace import SKOS, RDF, DCTERMS

ATLASKNO = Namespace("https://w3id.org/magean/atlaskno/")
SYNTAX = Namespace("https://w3id.org/magean/atlaskno/syntax/")

def parse_vault(root_dir):
    g = Graph()
    g.bind("skos", SKOS)
    g.bind("atlaskno", ATLASKNO)
    g.bind("syntax", SYNTAX)
    
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if not file.endswith(".md"):
                continue
                
            path = os.path.join(subdir, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                
            if content.startswith("---"):
                try:
                    # Extract YAML frontmatter
                    fm_str = content.split("---")[1]
                    data = yaml.safe_load(fm_str)
                    
                    notation = data.get("skos:notation", "")
                    if not notation: continue
                    
                    # Handle Synthesized Coordinates (e.g., [012.3:310])
                    if ":" in notation and "[" in notation:
                        bnode = BNode()
                        subjects = notation.strip("[]").split(":")
                        g.add((bnode, RDF.type, SKOS.Concept))
                        g.add((bnode, SKOS.prefLabel, Literal(data.get("skos:prefLabel", ""))))
                        g.add((bnode, SYNTAX.relates, ATLASKNO[subjects[0]]))
                        g.add((bnode, SYNTAX.relates, ATLASKNO[subjects[1]]))
                    else:
                        # Handle Atomic Concepts
                        uri = ATLASKNO[notation]
                        g.add((uri, RDF.type, SKOS.Concept))
                        g.add((uri, SKOS.notation, Literal(notation)))
                        g.add((uri, SKOS.prefLabel, Literal(data.get("skos:prefLabel", ""))))
                        
                        if data.get("is_vacant"):
                            g.add((uri, DCTERMS.description, Literal("Permanently Vacant Expansion Zone")))
                except yaml.YAMLError:
                    pass
    return g

if __name__ == "__main__":
    graph = parse_vault("ATLASKnO-Core")
    os.makedirs("dist", exist_ok=True)
    graph.serialize(destination="dist/atlaskno-core.ttl", format="turtle")
    graph.serialize(destination="dist/atlaskno-core.jsonld", format="json-ld")
    print("Exported RDF/SKOS graphs to dist/")
