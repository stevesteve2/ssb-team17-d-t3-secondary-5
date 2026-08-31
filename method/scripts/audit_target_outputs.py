#!/usr/bin/env python3
"""Independent schema/count/range/composite audit; never modifies predictions."""
import csv, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; TG=ROOT/'target_generation'; P=TG/'predictions'
conds=['Corporate reliance','Social justice','Interview Prof. Maraun','Funding','Oil industry misinformation','Measurement & modeling (1)','Former skeptics','High public trust','Measurement & modeling (2)','Peer-review','Scientist community helpers','Consensus','Portrait Prof. Cherry','Model accuracy','Interview Prof. Sebille','Extreme weather predictions']
outs=['trust_multidimensional','trust_post','distrust_post','funding_perceptions','policy_role_mean','inst_trust_mean','belief_post','concern_mean','policy_general','policy_specific_mean','behavior_mean','donation_ams','newsletter_signup']
bounds={o:(0,100) for o in outs};bounds['donation_ams']=(0,10);bounds['newsletter_signup']=(0,1)
weights=list(csv.DictReader((ROOT/'MODERATOR_WEIGHTS.csv').open())); levels={(r['moderator'],r['moderator_level']) for r in weights}

def read(name): return list(csv.DictReader((P/name).open()))
t1=read('T1_secondary_predictions.csv');m=read('T2_primary_cells_main.csv');sg=read('T2_primary_cells_moderator.csv');t3=read('T3_secondary_predictions.csv')
errors=[]
def ck(x,msg):
    if not x: errors.append(msg)
ck(len(t1)==9000,'T1 rows');ck(len({x['profile_id'] for x in t1})==9000,'T1 IDs unique')
ck({x['condition'] for x in t1}=={'control',*conds},'T1 conditions')
for c,n in [('control',1000)]+[(c,500) for c in conds]:ck(sum(x['condition']==c for x in t1)==n,f'T1 count {c}')
trust=[f'trust_{d}_{j}' for d in ('competence','integrity','benevolence','openness') for j in (1,2,3)]
for i,r in enumerate(t1,2):
    tv=[float(r[x]) for x in trust]; expected=sum(sum(tv[k:k+3])/3 for k in range(0,12,3))/4
    ck(abs(float(r['trust_multidimensional'])-expected)<1e-9,f'T1 trust composite row {i}')
    for o in outs:
        lo,hi=bounds[o];ck(lo<=float(r[o])<=hi,f'T1 range {o} row {i}')
    ck(float(r['donation_ams']).is_integer(),'T1 donation integer');ck(float(r['newsletter_signup']) in (0,1),'T1 signup binary')

ck(len(m)==221 and len({(x['condition'],x['outcome']) for x in m})==221,'T2 main grid')
ck({x['condition'] for x in m}=={'control',*conds} and {x['outcome'] for x in m}==set(outs),'T2 main factors')
for r in m:
    lo,hi=bounds[r['outcome']];ck(lo<=float(r['mean'])<=hi,'T2 main range')
ck(len(sg)==5967 and len({(x['condition'],x['moderator'],x['moderator_level'],x['outcome']) for x in sg})==5967,'T2 moderator grid')
ck({(x['moderator'],x['moderator_level']) for x in sg}==levels,'T2 moderator factors')
for r in sg:
    lo,hi=bounds[r['outcome']];ck(lo<=float(r['mean'])<=hi,'T2 moderator range')
mm={(x['condition'],x['outcome']):float(x['mean']) for x in m};maxerr=0
for c in ['control']+conds:
 for o in outs:
  for mod in dict.fromkeys(r['moderator'] for r in weights):
   ww=[r for r in weights if r['moderator']==mod]; vals={r['moderator_level']:float(r['mean']) for r in sg if r['condition']==c and r['outcome']==o and r['moderator']==mod}
   err=abs(sum(float(r['weight'])*vals[r['moderator_level']] for r in ww)-mm[(c,o)]);maxerr=max(maxerr,err)
ck(maxerr<1e-8,'T2 coherence')

ck(len(t3)==208 and len({(x['condition'],x['outcome']) for x in t3})==208,'T3 grid')
ck({x['condition'] for x in t3}==set(conds) and {x['outcome'] for x in t3}==set(outs),'T3 factors')
for r in t3:
    lo,hi=bounds[r['outcome']];ck(-(hi-lo)<=float(r['ate'])<=hi-lo,'T3 logical range')

attempts=list((TG/'raw').glob('tier*.jsonl')); parsed=[p for p in (TG/'parsed').glob('tier*.json') if not p.name.endswith('.meta.json')]
report={'status':'PASS' if not errors else 'FAIL','errors':errors,'rows':{'tier1':len(t1),'tier2_main':len(m),'tier2_moderator':len(sg),'tier3':len(t3)},
 'unique_profile_ids':len({x['profile_id'] for x in t1}),'tier2_max_coherence_error':maxerr,'successful_target_calls':len(parsed),'raw_attempt_logs':len(attempts)}
(TG/'processed/independent_audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if errors: raise SystemExit(1)
