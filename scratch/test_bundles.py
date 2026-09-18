# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.abspath("."))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from app.cross_checker import CrossVerificationEngine
from app.samples import MULTI_DOC_BUNDLES

engine = CrossVerificationEngine()

for bundle_id, bundle_data in MULTI_DOC_BUNDLES.items():
    docs = bundle_data.get("documents")
    if docs:
        res = engine.run_standard_cross_check(docs)
        print(f"\nBundle: {bundle_id} -> Overall Status: {res.get('overall_status')}, Total Checks: {res.get('total_checks')}")
        for c in res.get("matrix_results", []):
            print(f"  [{c['status']}]: {c['title']} -> {c['details']}")
