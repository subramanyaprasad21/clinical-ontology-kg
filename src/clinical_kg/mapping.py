"""Pure identifier syntax conversions; never establish equivalence by themselves."""
PREFIXES = {
 'DOID': 'http://purl.obolibrary.org/obo/DOID_',
 'ICD10CM': 'http://purl.bioontology.org/ontology/ICD10CM/',
 'ICD10WHO': 'https://icd.who.int/browse10/2019/en#/',
 'MEDGEN': 'http://identifiers.org/medgen/',
 'MESH': 'http://identifiers.org/mesh/',
 'NCIT': 'http://purl.obolibrary.org/obo/NCIT_',
 'OMIM': 'https://omim.org/entry/',
 'SCTID': 'http://identifiers.org/snomedct/',
 'UMLS': 'http://linkedlifedata.com/resource/umls/id/',
 'icd11.foundation': 'http://id.who.int/icd/entity/',
}

def mapping_uri(curie):
    prefix, _, local = curie.partition(':')
    return PREFIXES[prefix] + local if prefix in PREFIXES and local else None
