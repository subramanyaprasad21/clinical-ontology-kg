#!/usr/bin/env python3
"""Audit only; run before modifying the semantic model."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from clinical_kg.audit import audit
if __name__ == '__main__':
    result = audit(ROOT)
    print('Verified anchor:', result['anchor']['uri'])
    print('Hierarchy nodes:', len(result['hierarchy']))
    print('HPO annotations:', len(result['hpo_annotations']))
    print('OT phenotype rows:', len(result['ot_phenotypes']))
    print('Mechanism join audit:', result['mechanism_audit'])
    print('Missing target/drug IDs:', len(result['missing_mechanism_targets']), len(result['missing_mechanism_drugs']))
