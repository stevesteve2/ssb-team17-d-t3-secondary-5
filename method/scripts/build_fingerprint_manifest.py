#!/usr/bin/env python3
"""Fingerprint every design, prompt, code, evidence, and authoritative input."""
import csv, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
explicit=[
 'RUN_CONFIG.md','BENCHMARK_SPEC.md','EVIDENCE_MEMO.md','EVIDENCE_LIBRARY.csv',
 'TARGET_EVIDENCE_MAP.csv','MODERATOR_WEIGHTS.csv','EXTERNAL_VALIDATION_SPEC.md',
 'EXTERNAL_VALIDATION_RESULTS.md','PROTOCOLS_AND_PROMPTS.md','COST_ESTIMATE.md'
]
paths=[ROOT/p for p in explicit]
for pat in ('scripts/*','evidence/sources/**/*','validation/prompts/*','validation/*.json',
            'official_submission_template/README*','official_submission_template/FAQ.md',
            'official_submission_template/registration.md','official_submission_template/metadata.json',
            'official_submission_template/codebook.csv','official_submission_template/scripts/*',
            'official_submission_template/survey/*'):
    paths.extend(ROOT.glob(pat))
paths=sorted({p for p in paths if p.is_file() and '.git' not in p.parts})
rows=[]
for p in paths:
    h=hashlib.sha256(); size=0
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b); size+=len(b)
    rows.append({'path':str(p.relative_to(ROOT)),'bytes':size,'sha256':h.hexdigest()})
with (ROOT/'SHA256_MANIFEST.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['path','bytes','sha256']);w.writeheader();w.writerows(rows)
print('fingerprinted',len(rows),'files')
