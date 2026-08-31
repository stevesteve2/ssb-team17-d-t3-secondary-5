#!/usr/bin/env python3
"""Deterministically process frozen target generations into benchmark-shaped CSVs."""
import argparse, csv, hashlib, json, math
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]; TG=ROOT/'target_generation'; P=TG/'parsed'; PROC=TG/'processed'; PRED=TG/'predictions'
PROC.mkdir(exist_ok=True);PRED.mkdir(exist_ok=True)
COND=json.load((TG/'inputs/conditions.json').open()); ITEMS=json.load((TG/'inputs/scored_items.json').open())
OUTCOMES=json.load((TG/'inputs/outcomes.json').open()); PROFILES=list(csv.DictReader((TG/'inputs/profiles.csv').open()))
ASSIGN=json.load((TG/'inputs/control_assignment.json').open()); WEIGHTS=list(csv.DictReader((ROOT/'MODERATOR_WEIGHTS.csv').open()))
CANON=list(COND['interventions']); OPAQUE={c:f'arm_{i+1:02d}' for i,c in enumerate(CANON)}; ON=[o['name'] for o in OUTCOMES]
BOUNDS={o['name']:tuple(o['scale']) for o in OUTCOMES}; FIELD=ITEMS['field_order']; FIDX={x:i for i,x in enumerate(FIELD)}
groups=[]
for mod in dict.fromkeys(r['moderator'] for r in WEIGHTS):
    rr=[r for r in WEIGHTS if r['moderator']==mod]; groups.append((mod,[r['moderator_level'] for r in rr],np.array([float(r['weight']) for r in rr])))

def load(tag): return json.load((P/f'{tag}.json').open())
def project(vals,w,target,lo,hi):
    vals=np.asarray(vals,float); w=np.asarray(w,float); target=float(np.clip(target,lo,hi))
    left,right=lo-float(np.max(vals))-1,hi-float(np.min(vals))+1
    for _ in range(100):
        mid=(left+right)/2; mean=float(np.dot(w,np.clip(vals+mid,lo,hi)))
        if mean<target:left=mid
        else:right=mid
    return np.clip(vals+(left+right)/2,lo,hi)

def tier2_control():
    reps=[np.array(load(f'tier2_control_r{r}')['rows'],float) for r in (1,2,3)]
    raw=np.median(np.stack(reps),axis=0); out=[]
    for oi,o in enumerate(ON):
        lo,hi=BOUNDS[o]; main=float(np.clip(raw[oi,0],lo,hi)); vals=[]; pos=1
        for mod,levels,w in groups:
            n=len(levels); vals.extend(project(raw[oi,pos:pos+n],w,main,lo,hi)); pos+=n
        out.append([main]+[float(x) for x in vals])
    data={'outcome_order':ON,'level_order':[(r['moderator'],r['moderator_level'],float(r['weight'])) for r in WEIGHTS],'rows':out}
    (PROC/'tier2_control_baselines.json').write_text(json.dumps(data,indent=2)); print('wrote control baselines')

def raw_t1_records():
    rec={}
    for j,name in enumerate(COND['controls'],1):
        for row in load(f'tier1_control_f{j}')['rows']: rec[('control',int(row[0]))]=row
    for c in CANON:
        rows=load(f'tier1_{OPAQUE[c]}_p1')['rows']+load(f'tier1_{OPAQUE[c]}_p2')['rows']
        for row in rows: rec[(c,int(row[0]))]=row
    return rec

def mean(row,names): return sum(row[FIDX[x]] for x in names)/len(names)
def submitted_t1():
    rec=raw_t1_records(); prof={int(x['profile_index']):x for x in PROFILES}; rows=[]
    # Control first; raw IDs are unique only after condition prefixing.
    order=[('control',range(1,1001))]+[(c,range(1,501)) for c in CANON]
    for cond,ids in order:
        replace=set()
        if cond!='control':
            replace=set(sorted(ids,key=lambda i:hashlib.sha256(f'{cond}|{i}|calibration'.encode()).hexdigest())[:250])
        for i in ids:
            raw=list(rec[(cond,i)])
            if cond!='control' and i in replace: raw=[i]+list(rec[('control',i)][1:])
            p=prof[i]
            trust_fields=[f'trust_{d}_{j}' for d in ('competence','integrity','benevolence','openness') for j in (1,2,3)]
            tvals=[raw[FIDX[x]] for x in trust_fields]
            dims=[sum(tvals[k:k+3])/3 for k in range(0,12,3)]
            out={'profile_id':('control' if cond=='control' else OPAQUE[cond])+f'_p{i:05d}','condition':cond,
              'gender':p['gender'],'age_band':p['age_band'],'race':p['race'],'education':p['education'],'income':p['income'],'party':p['party'],
              'trust_multidimensional':sum(dims)/4}
            for x in trust_fields: out[x]=raw[FIDX[x]]
            out.update({'trust_post':raw[FIDX['trust_post']],'distrust_post':raw[FIDX['distrust_post']],
              'funding_perceptions':100-raw[FIDX['funding_5']],
              'policy_role_mean':mean(raw,[f'policy_role_{j}' for j in range(1,5)]),
              'inst_trust_mean':mean(raw,['inst_trust_epa','inst_trust_nasa','inst_trust_noaa','inst_trust_universities','inst_trust_federal_gov']),
              'belief_post':raw[FIDX['belief_post']], 'concern_mean':mean(raw,[f'concern_{j}' for j in range(1,4)]),
              'policy_general':raw[FIDX['policy_general']], 'policy_specific_mean':mean(raw,[f'policy_specific_{j}' for j in range(1,8)]),
              'behavior_mean':mean(raw,['behavior_meat','behavior_transport','behavior_solar','behavior_fly','behavior_talk','behavior_donate']),
              'donation_ams':raw[FIDX['donation_ams']],'newsletter_signup':raw[FIDX['newsletter_signup']]})
            rows.append(out)
    fields=(['profile_id','condition','gender','age_band','race','education','income','party','trust_multidimensional']+
      [f'trust_{d}_{j}' for d in ('competence','integrity','benevolence','openness') for j in (1,2,3)]+
      ['trust_post','distrust_post','funding_perceptions','policy_role_mean','inst_trust_mean','belief_post','concern_mean','policy_general','policy_specific_mean','behavior_mean','donation_ams','newsletter_signup'])
    with (PRED/'T1_secondary_predictions.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fields);w.writeheader();w.writerows(rows)
    return rows

def submitted_t2():
    base=json.load((PROC/'tier2_control_baselines.json').open())['rows']; main_rows=[]; mod_rows=[]
    # Control.
    for oi,o in enumerate(ON):
        main_rows.append({'condition':'control','outcome':o,'mean':base[oi][0]});pos=1
        for mod,levels,w in groups:
            for lev,val in zip(levels,base[oi][pos:pos+len(levels)]): mod_rows.append({'condition':'control','moderator':mod,'moderator_level':lev,'outcome':o,'mean':val})
            pos+=len(levels)
    for c in CANON:
        reps=[np.array(load(f'tier2_{OPAQUE[c]}_r{r}')['rows'],float) for r in (1,2,3)]
        eff=np.median(np.stack(reps),axis=0)
        for oi,o in enumerate(ON):
            lo,hi=BOUNDS[o]; target=float(np.clip(base[oi][0]+.5*eff[oi,0],lo,hi));main_rows.append({'condition':c,'outcome':o,'mean':target});pos=1
            for mod,levels,w in groups:
                n=len(levels); eraw=eff[oi,pos:pos+n]; ecoh=.5*(eraw-float(np.dot(w,eraw))+eff[oi,0]); cand=np.array(base[oi][pos:pos+n])+ecoh
                vals=project(cand,w,target,lo,hi)
                for lev,val in zip(levels,vals):mod_rows.append({'condition':c,'moderator':mod,'moderator_level':lev,'outcome':o,'mean':float(val)})
                pos+=n
    with (PRED/'T2_primary_cells_main.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,['condition','outcome','mean']);w.writeheader();w.writerows(main_rows)
    with (PRED/'T2_primary_cells_moderator.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,['condition','moderator','moderator_level','outcome','mean']);w.writeheader();w.writerows(mod_rows)
    return main_rows,mod_rows

def submitted_t3():
    rows=[]
    for c in CANON:
        reps=[{x['outcome']:x for x in load(f'tier3_{OPAQUE[c]}_r{r}')['rows']} for r in (1,2,3)]
        for o in ON:
            lo,hi=BOUNDS[o]; ate=.5*float(np.median([x[o]['ate'] for x in reps])); ate=float(np.clip(ate,-(hi-lo),hi-lo))
            rows.append({'condition':c,'outcome':o,'ate':ate})
    with (PRED/'T3_secondary_predictions.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,['condition','outcome','ate']);w.writeheader();w.writerows(rows)
    return rows

def audit(t1,t2main,t2mod,t3):
    assert len(t1)==9000 and len({r['profile_id'] for r in t1})==9000
    counts={c:sum(r['condition']==c for r in t1) for c in ['control']+CANON};assert counts['control']==1000 and all(counts[c]==500 for c in CANON)
    assert len(t2main)==221 and len({(r['condition'],r['outcome']) for r in t2main})==221
    assert len(t2mod)==5967 and len({(r['condition'],r['moderator'],r['moderator_level'],r['outcome']) for r in t2mod})==5967
    assert len(t3)==208 and len({(r['condition'],r['outcome']) for r in t3})==208
    # Exact Tier 2 coherence.
    mm={(r['condition'],r['outcome']):float(r['mean']) for r in t2main}
    maxerr=0
    for c in ['control']+CANON:
      for o in ON:
       for mod,levels,w in groups:
        vals=[float(next(r['mean'] for r in t2mod if r['condition']==c and r['outcome']==o and r['moderator']==mod and r['moderator_level']==lev)) for lev in levels]
        maxerr=max(maxerr,abs(float(np.dot(w,vals))-mm[(c,o)]))
    assert maxerr<1e-7,maxerr
    usage={'calls':0,'input_tokens':0,'cached_input_tokens':0,'output_tokens':0,'seconds':0.0}
    for p in P.glob('*.meta.json'):
        if p.name.startswith('probe_'):continue
        m=json.load(p.open());u=m.get('usage') or {};usage['calls']+=1;usage['seconds']+=m.get('seconds',0)
        for k in ('input_tokens','cached_input_tokens','output_tokens'):usage[k]+=u.get(k,0)
    unc=usage['input_tokens']-usage['cached_input_tokens'];usage['api_equivalent_usd']=unc*4/1e6+usage['cached_input_tokens']*.4/1e6+usage['output_tokens']*20/1e6
    usage['expected_incremental_cash_usd']=0;usage['tier2_max_coherence_error']=maxerr
    (PROC/'target_usage_and_audit.json').write_text(json.dumps({'counts':counts,'usage':usage},indent=2));print(json.dumps(usage,indent=2))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--phase',choices=['tier2_control','all'],required=True);a=ap.parse_args()
    if a.phase=='tier2_control':tier2_control();return
    t1=submitted_t1();m,sg=submitted_t2();t3=submitted_t3();audit(t1,m,sg,t3)

if __name__=='__main__':main()
