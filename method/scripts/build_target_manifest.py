#!/usr/bin/env python3
import csv,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];TG=ROOT/'target_generation'
paths=[]
for sub in ('inputs','schemas','prompts','raw','parsed','processed','predictions'):
    paths.extend(p for p in (TG/sub).rglob('*') if p.is_file())
paths += [ROOT/'DESIGN_LOCK.md',ROOT/'DESIGN_LOCK.sha256',ROOT/'PROTOCOLS_AND_PROMPTS.md',ROOT/'EVIDENCE_LIBRARY.csv',ROOT/'TARGET_EVIDENCE_MAP.csv',ROOT/'MODERATOR_WEIGHTS.csv',ROOT/'scripts/prepare_target_generation.py',ROOT/'scripts/run_target_calls.py',ROOT/'scripts/process_target_predictions.py',ROOT/'scripts/audit_target_outputs.py',ROOT/'scripts/run_official_file_checks.R']
paths += [TG/'TARGET_EXECUTION_REPORT.md']
rows=[]
for p in sorted(set(paths)):
    h=hashlib.sha256();size=0
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b);size+=len(b)
    rows.append({'path':str(p.relative_to(ROOT)),'bytes':size,'sha256':h.hexdigest()})
with (TG/'TARGET_MANIFEST.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,['path','bytes','sha256']);w.writeheader();w.writerows(rows)
print('manifest files',len(rows))
