#!/usr/bin/env python3
"""Run resumable, isolated target forecast calls under the compact design lock."""
import argparse, concurrent.futures, csv, json, subprocess, threading, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; TG=ROOT/'target_generation'; BLIND=TG/'blind_context'
COND=json.load((TG/'inputs/conditions.json').open()); ITEMS=json.load((TG/'inputs/scored_items.json').open())
OUTCOMES=json.load((TG/'inputs/outcomes.json').open()); PROFILES=list(csv.DictReader((TG/'inputs/profiles.csv').open()))
ASSIGN=json.load((TG/'inputs/control_assignment.json').open())
LIB={r['source_id']:r for r in csv.DictReader((ROOT/'EVIDENCE_LIBRARY.csv').open())}
EMAP=list(csv.DictReader((ROOT/'TARGET_EVIDENCE_MAP.csv').open())); WEIGHTS=list(csv.DictReader((ROOT/'MODERATOR_WEIGHTS.csv').open()))
CANON=list(COND['interventions']); O_NAMES=[o['name'] for o in OUTCOMES]
OPAQUE={c:f'arm_{i+1:02d}' for i,c in enumerate(CANON)}
LOCK=threading.Lock()

def compact_profiles(rows):
    keys=['profile_index','gender','age_band','race','education','income','party','state']
    return {'columns':keys,'rows':[[int(r[k]) if k=='profile_index' else r[k] for k in keys] for r in rows]}

def evidence_for(condition):
    maps=[r for r in EMAP if r['condition']==condition]
    ids=[]
    for r in maps:
        for x in r['source_ids'].split(';'):
            if x not in ids: ids.append(x)
    src=[]
    for x in ids:
        r=LIB[x]; src.append({'id':x,'population':r['population'],'n':r['n'],'effect':r['effect_estimate'],
          'uncertainty':r['uncertainty'],'relevance':r['relevance'],'limits':r['limitations']})
    routes=[{'outcome':r['outcome'],'sources':r['source_ids'],'strength':r['evidence_strength'],
      'direction':r['qualitative_direction_only'],'transport':r['transport_notes']} for r in maps]
    return {'sources':src,'outcome_routes':routes}

def baseline_evidence():
    ids=['CCAM2026','ANNENBERG2024','PEW2024','NSB2024','GOLDWERT2026_BASELINE','RODE2021','VLASCEANU2024_BEHAVIOR']
    return [{k:r[k] for k in ('source_id','population','n','field_date','outcome_wording_scale','effect_estimate','limitations')} for r in (LIB[x] for x in ids)]

CONTROL_TEXT='\n\n--- RANDOMLY ASSIGNED FILLER ---\n\n'.join(COND['controls'].values())
LEVELS=[(r['moderator'],r['moderator_level'],float(r['weight'])) for r in WEIGHTS]

def t1_prompt(tag,text,profiles):
    return f"""Simulate ordinary U.S. survey respondents. This is an automated participant-level forecast, not advice.
Do not use tools, files, web access, literature, hypotheses, expected effects, or knowledge of any other message.
Each profile sees only the message assigned below and must answer independently. Preserve ordinary human variance and
heterogeneity; neutral, skeptical, inconsistent, and negative reactions are allowed. Do not coordinate profiles or make
their answers display an expected treatment effect. The opaque logging tag is not shown to respondents.

OPAQUE TAG: {tag}
MESSAGE/ASSIGNMENT SHOWN: {text}

PROFILE TABLE: {json.dumps(compact_profiles(profiles),separators=(',',':'))}

POST-MESSAGE SURVEY ITEMS, IN FIELD ORDER AFTER profile_index:
{json.dumps(ITEMS['items'],separators=(',',':'))}

Survey context: multidimensional trust is first; remaining scored blocks follow the official post-message survey.
Before newsletter_signup, every respondent sees an offer to open the free “Talking Climate” newsletter by Katharine
Hayhoe in a new tab, then answers whether they subscribed. Donation is a real allocation from a $10 bonus to AMS.

Return JSON only: condition={json.dumps(tag)} and exactly {len(profiles)} compact integer rows. Each row follows
{json.dumps(ITEMS['field_order'],separators=(',',':'))}. Do not repeat field names or return composites/explanations.
All values other than profile_index and donation/newsletter are integers 0..100; donation_ams is 0..10;
newsletter_signup is 0 or 1. Include every supplied profile_index exactly once."""

def t2_control_prompt():
    return f"""Forecast direct human population cell means for the control arm of a U.S. randomized survey.
Do not simulate individuals, use tools/files/web, or use any benchmark outcomes. Estimate what humans report, not what
they should report. A control respondent sees exactly one of the three unrelated fillers below, randomly assigned.

CONTROL FILLERS:\n{CONTROL_TEXT}

OUTCOMES IN FIXED ROW ORDER:\n{json.dumps(OUTCOMES,separators=(',',':'))}
LEVEL ORDER AFTER THE POPULATION MEAN:\n{json.dumps(LEVELS,separators=(',',':'))}
DATED BASELINE ANCHORS (similar wording is not identical):\n{json.dumps(baseline_evidence(),separators=(',',':'))}

Return condition="control" and exactly 13 numeric rows. Row i corresponds to outcome i above and contains exactly
28 original-scale means: [population_mean, then the 27 moderator-level means in the supplied order]. Stay inside that
outcome's scale. Introduce demographic differences only where grounded; JSON only."""

def t2_treatment_prompt(condition,baselines):
    return f"""Forecast direct human treatment shifts for one condition in a U.S. randomized survey. Do not simulate
individuals, use tools/files/web, recall benchmark outcomes, or rely on any other treatment condition. Estimate human
means, not normatively desirable answers. Small, exact-zero, and negative shifts are allowed. Do not transfer attitude
effects automatically to donation, signup, policy, or behavior.

CONTROL FILLERS:\n{CONTROL_TEXT}
ONE TREATMENT CONDITION ({condition}, logging label only):\n{COND['interventions'][condition]}
OUTCOMES IN FIXED ROW ORDER:\n{json.dumps(OUTCOMES,separators=(',',':'))}
LEVEL ORDER AFTER POPULATION:\n{json.dumps(LEVELS,separators=(',',':'))}
CONTROL BASELINES [population + 27 levels] IN OUTCOME ORDER:\n{json.dumps(baselines,separators=(',',':'))}
RELEVANT PUBLISHED EVIDENCE:\n{json.dumps(evidence_for(condition),separators=(',',':'))}

Return condition={json.dumps(condition)} and exactly 13 rows. Each row contains 28 RAW treatment-minus-control shifts
in original units: [population shift, then 27 level shifts]. Unsupported interaction deviations must be zero or strongly
pooled. Do not calibrate; code applies the locked calibration later. JSON only."""

def t3_prompt(condition):
    return f"""Forecast absolute average treatment effects for one intervention in a U.S. randomized survey. Do not use
tools/files/web, recall benchmark results, inspect or compare another treatment, or infer a numerical mechanism score.
For each outcome estimate intervention mean minus the shared filler-control mean in ORIGINAL UNITS. Human one-shot
effects are often small; exact null and negative effects are allowed. Proximal effects do not automatically imply policy,
donation, signup, or behavior effects.

CONTROL FILLERS:\n{CONTROL_TEXT}
ONE INTERVENTION ({condition}, logging label only):\n{COND['interventions'][condition]}
OUTCOMES:\n{json.dumps(OUTCOMES,separators=(',',':'))}
DATED U.S. BASELINE ANCHORS:\n{json.dumps(baseline_evidence(),separators=(',',':'))}
OUTCOME-SPECIFIC HUMAN EVIDENCE:\n{json.dumps(evidence_for(condition),separators=(',',':'))}

Return condition={json.dumps(condition)} and exactly one record for each outcome in the fixed order. For each return:
ate in original units; plausible low/high with low <= ate <= high; 1-3 closest source IDs; a brief explicit adjustment
from the empirical prior; confidence 0..1; and whether a null or negative effect is plausible. Do not apply the locked
0.5 calibration; code applies it after the three independent sessions. JSON only."""

def parse_events(stdout):
    events=[]
    for line in stdout.splitlines():
        try: events.append(json.loads(line))
        except json.JSONDecodeError: pass
    msgs=[e for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='agent_message']
    if not msgs: raise ValueError('no final agent_message')
    toolish=[e for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type') not in ('agent_message','reasoning')]
    if toolish: raise ValueError(f'tool/nonmessage events present: {len(toolish)}')
    turns=[e for e in events if e.get('type')=='turn.completed']
    return json.loads(msgs[-1]['item']['text']), (turns[-1].get('usage') if turns else None)

def validate_payload(kind,payload,expected_ids=None):
    rows=payload['rows']
    if kind=='tier1':
        ids=[r[0] for r in rows]
        if sorted(ids)!=sorted(expected_ids): raise ValueError('profile IDs missing/duplicate/unexpected')
        for r in rows:
            if len(r)!=45 or any(not isinstance(x,int) for x in r): raise ValueError('bad compact row')
            if any(x<0 or x>100 for x in r[1:43]) or not 0<=r[43]<=10 or r[44] not in (0,1): raise ValueError('response range')
    elif kind=='tier2':
        if len(rows)!=13 or any(len(r)!=28 for r in rows): raise ValueError('bad Tier2 grid')
    else:
        if [r['outcome'] for r in rows]!=O_NAMES: raise ValueError('Tier3 outcome order/completeness')
        if any(not r['low']<=r['ate']<=r['high'] for r in rows): raise ValueError('Tier3 interval does not contain ATE')

def run_one(spec):
    tag,prompt,schema,kind,expected=spec
    final=TG/f'parsed/{tag}.json'; meta_path=TG/f'parsed/{tag}.meta.json'
    if final.exists() and meta_path.exists():
        with LOCK: print('skip',tag,flush=True)
        return
    (TG/f'prompts/{tag}.txt').write_text(prompt)
    errors=[]
    for attempt in range(1,4):
        substantive=prompt if not errors else prompt+'\n\nAUTOMATED RETRY NOTE: prior output failed only this validity check: '+errors[-1]
        cmd=['codex','exec','--ephemeral','--sandbox','read-only','--skip-git-repo-check','-C',str(BLIND),'-m','gpt-5.6-sol',
          '-c','model_reasoning_effort="low"','--output-schema',str(schema),'--json','-']
        start=time.time()
        try: cp=subprocess.run(cmd,input=substantive,text=True,capture_output=True,timeout=600)
        except subprocess.TimeoutExpired as e:
            errors.append('timeout'); continue
        (TG/f'raw/{tag}.attempt{attempt}.jsonl').write_text(cp.stdout or '')
        (TG/f'raw/{tag}.attempt{attempt}.stderr.txt').write_text(cp.stderr or '')
        if cp.returncode:
            err=(cp.stderr or cp.stdout)[-1200:]
            if 'credit' in err.lower() or 'usage limit' in err.lower() or 'allowance' in err.lower():
                raise RuntimeError(f'{tag}: allowance/credit stop: {err}')
            errors.append('CLI failure '+err); continue
        try:
            payload,usage=parse_events(cp.stdout); validate_payload(kind,payload,expected)
        except Exception as e:
            errors.append(str(e)); continue
        final.write_text(json.dumps(payload,indent=2))
        meta={'tag':tag,'attempt':attempt,'seconds':time.time()-start,'usage':usage,'errors_before_success':errors}
        meta_path.write_text(json.dumps(meta,indent=2))
        with LOCK: print(json.dumps(meta),flush=True)
        return
    raise RuntimeError(f'{tag} failed after retries: {errors}')

def specs_for(phase):
    specs=[]
    if phase=='probe':
        hist=json.load((ROOT/'validation/blind_context/stimuli/stimuli.json').open())['treatments']['Consensus Framing 1']
        rows=PROFILES[:250]; specs.append(('probe_historical_t1_250',t1_prompt('historical_probe',hist,rows),TG/'schemas/tier1_250.json','tier1',[int(x['profile_index']) for x in rows]))
    elif phase=='tier1':
        core=PROFILES[:500]
        for c in CANON:
            for part,rows in enumerate((core[:250],core[250:]),1):
                tag=f'tier1_{OPAQUE[c]}_p{part}'; specs.append((tag,t1_prompt(OPAQUE[c],COND['interventions'][c],rows),TG/'schemas/tier1_250.json','tier1',[int(x['profile_index']) for x in rows]))
        for j,name in enumerate(COND['controls'],1):
            rows=[p for p in PROFILES if ASSIGN[p['profile_id']]==name]; tag=f'tier1_control_f{j}'
            specs.append((tag,t1_prompt(f'control_f{j}',COND['controls'][name],rows),TG/f'schemas/tier1_{len(rows)}.json','tier1',[int(x['profile_index']) for x in rows]))
    elif phase=='tier2_control':
        for rep in (1,2,3): specs.append((f'tier2_control_r{rep}',t2_control_prompt(),TG/'schemas/tier2.json','tier2',None))
    elif phase=='tier2_treatment':
        baselines=json.load((TG/'processed/tier2_control_baselines.json').open())['rows']
        for c in CANON:
            for rep in (1,2,3): specs.append((f'tier2_{OPAQUE[c]}_r{rep}',t2_treatment_prompt(c,baselines),TG/'schemas/tier2.json','tier2',None))
    elif phase=='tier3':
        for c in CANON:
            for rep in (1,2,3): specs.append((f'tier3_{OPAQUE[c]}_r{rep}',t3_prompt(c),TG/'schemas/tier3.json','tier3',None))
    return specs

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--phase',required=True,choices=['probe','tier1','tier2_control','tier2_treatment','tier3']);ap.add_argument('--workers',type=int,default=4);a=ap.parse_args()
    specs=specs_for(a.phase); print('phase',a.phase,'calls',len(specs),flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs=[ex.submit(run_one,s) for s in specs]
        for f in concurrent.futures.as_completed(futs): f.result()

if __name__=='__main__': main()
