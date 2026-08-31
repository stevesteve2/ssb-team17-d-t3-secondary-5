#!/usr/bin/env python3
"""Score blinded forecasts after all generations are frozen."""
import csv, json, math
from pathlib import Path
import numpy as np
try:
    from scipy.stats import pearsonr, spearmanr
except ImportError:
    pearsonr=spearmanr=None

ROOT=Path(__file__).resolve().parents[1]; V=ROOT/'validation'; OUT=V/'model_outputs'
human=list(csv.DictReader((V/'hidden_outcomes/human_ates.csv').open()))
keys=[(r['condition'],r['outcome']) for r in human]
y=np.array([float(r['human_ate_pp']) for r in human])

def load(name): return json.load((OUT/name).open())
def tier1():
    controls=[]
    for n in ('tier1_control_baseball.json','tier1_control_neckties.json','tier1_control_dances.json'):
        controls += load(n)['participants']
    cm={o:np.mean([p[o] for p in controls]) for o in ('belief','concern','general_policy','political_intention')}
    pred={}
    for cond in sorted({k[0] for k in keys}):
        ps=load('tier1_'+cond.lower().replace(' ','_')+'.json')['participants']
        assert len(ps)==50 and len({p['id'] for p in ps})==50
        for o in cm: pred[(cond,o)]=float(np.mean([p[o] for p in ps])-cm[o])
    return pred

def group(method):
    pred={}
    for cond,o in keys:
        vals=[]
        for rep in (1,2):
            if method=='tier3' and rep==1 and cond=='Consensus Framing 1': name='pilot_tier3_consensus.json'
            else: name=f'{method}_r{rep}_'+cond.lower().replace(' ','_')+'.json'
            rec=next(x for x in load(name)['forecasts'] if x['outcome']==o)
            assert abs((rec['treatment_mean']-rec['control_mean'])-rec['ate_pp']) <= .011
            vals.append(float(rec['ate_pp']))
        pred[(cond,o)]=float(np.median(vals))
    return pred

def metric(method,pred):
    p=np.array([pred[k] for k in keys])
    # Center each vector separately within each outcome, as preregistered.
    pc=p.copy(); yc=y.copy()
    for o in sorted({k[1] for k in keys}):
        idx=np.array([k[1]==o for k in keys]); pc[idx]-=pc[idx].mean(); yc[idx]-=yc[idx].mean()
    def corr(a,b,rank=False):
        if rank and spearmanr: return float(spearmanr(a,b).statistic)
        if pearsonr: return float(pearsonr(a,b).statistic)
        return float(np.corrcoef(a,b)[0,1])
    signs=[]
    for a,b in zip(p,y):
        if a==0: signs.append(.5)
        else: signs.append(float(np.sign(a)==np.sign(b)))
    slope,intercept=np.polyfit(p,y,1)
    return {'method':method,'n_ates':len(p),'pooled_pearson':corr(p,y),
            'within_outcome_centered_pearson':corr(pc,yc),'spearman':corr(p,y,True),
            'directional_agreement':float(np.mean(signs)),
            'rmse_pp':float(np.sqrt(np.mean((p-y)**2))),
            'mean_signed_error_pp':float(np.mean(p-y)),
            'calibration_intercept_human_on_prediction':float(intercept),
            'calibration_slope_human_on_prediction':float(slope)}

preds={'tier1':tier1(),'tier2':group('tier2'),'tier3':group('tier3')}
metrics=[metric(k,v) for k,v in preds.items()]
with (V/'validation_predictions.csv').open('w',newline='') as f:
    fields=['method','condition','outcome','prediction_ate_pp','human_ate_pp']; w=csv.DictWriter(f,fields); w.writeheader()
    for method,pred in preds.items():
        for row in human:
            k=(row['condition'],row['outcome']); w.writerow({'method':method,'condition':k[0],'outcome':k[1],'prediction_ate_pp':pred[k],'human_ate_pp':row['human_ate_pp']})
with (V/'validation_metrics.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,metrics[0].keys()); w.writeheader(); w.writerows(metrics)

# Exact API-equivalent cost from CLI-reported usage, including the pilot.
total={'input_tokens':0,'cached_input_tokens':0,'output_tokens':0,'seconds':0.0,'calls':0,'toolish_events':0}
for path in OUT.glob('*.meta.json'):
    m=json.load(path.open()); u=m.get('usage') or {}
    total['calls']+=1; total['seconds']+=m.get('seconds',0); total['toolish_events']+=m.get('toolish_events',0)
    for k in ('input_tokens','cached_input_tokens','output_tokens'): total[k]+=u.get(k,0)
uncached=total['input_tokens']-total['cached_input_tokens']
total['api_equivalent_cost_usd']=uncached*4/1e6+total['cached_input_tokens']*.4/1e6+total['output_tokens']*20/1e6
(V/'validation_usage.json').write_text(json.dumps(total,indent=2))
print(json.dumps({'metrics':metrics,'usage':total},indent=2))
