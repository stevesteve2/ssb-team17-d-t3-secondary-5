#!/usr/bin/env python3
"""Run the frozen blinded forecasting procedures on historical stimuli only."""
import argparse, csv, json, random, subprocess, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
V=ROOT/'validation'; BLIND=V/'blind_context'; RAW=V/'raw'; PROMPTS=V/'prompts'; FINAL=V/'model_outputs'
for p in (RAW,PROMPTS,FINAL): p.mkdir(parents=True,exist_ok=True)
stim=json.load((BLIND/'stimuli/stimuli.json').open()); outcomes=json.load((BLIND/'outcomes.json').open())

def profiles():
    rng=random.Random(20260830)
    states=['California','Texas','Florida','New York','Pennsylvania','Ohio','Georgia','North Carolina','Michigan','Arizona']
    parties=['Democrat']*22+['Republican']*20+['Independent/other']*8
    genders=['Woman']*25+['Man']*24+['Nonbinary']
    races=['White']*29+['Black']*7+['Hispanic']*9+['Asian']*3+['Other/multiracial']*2
    ed=['High school or less']*18+['Some college']*14+['Bachelor']*11+['Postgraduate']*7
    rng.shuffle(parties); rng.shuffle(genders); rng.shuffle(races); rng.shuffle(ed)
    return [{'id':i+1,'age':rng.randint(18,80),'gender':genders[i],'race_ethnicity':races[i],
             'education':ed[i],'party':parties[i],'state':states[i%len(states)]} for i in range(50)]

EVIDENCE="""External evidence available before this historical experiment: a 76-experiment U.S. meta-analysis found a typical climate-attitude effect g=0.08, 95% CI [0.05,0.10], prediction interval [-0.04,0.19], with policy effects below belief effects. A 63-country megastudy found its best interventions shifted belief 2.3 percentage points and policy support 2.6 points, while behavior could be null or negative. A 27-country consensus message produced d=.47 on perceived consensus but only d=.06 for reality belief, d=.05 for worry, and d=.02 (null) for public action. One-shot effects are usually small; ceiling and political heterogeneity matter."""

def prompt_t1(name,text):
    return f"""You are simulating ordinary U.S. survey respondents for a blinded historical experiment. Do not use tools, files, web access, or knowledge of this experiment's results. Each respondent sees only the one message below. Independently answer for all 50 concise demographic profiles. Preserve human variance and allow neutral, skeptical, inconsistent, and negative reactions. Do not infer expected effects or coordinate answers. Return only schema-valid JSON with condition={json.dumps(name)}, method=\"tier1\" and exactly one record per ID.

Message shown:\n{text}

Post-message outcomes (each integer 0–100):\n{json.dumps(outcomes,indent=2)}

Profiles:\n{json.dumps(profiles(),separators=(',',':'))}"""

def prompt_group(name,text,method):
    controls='\n\n--- RANDOM CONTROL FILLER ---\n'.join(stim['controls'].values())
    extra = ("Forecast human population cell means directly. First estimate the pooled control mean, then the treatment mean. Do not simulate individual records."
             if method=='tier2' else
             "Forecast the absolute human ATE directly from the empirical prior, then supply compatible control and treatment means. Explicitly retain null/negative possibilities in the interval.")
    return f"""You are forecasting a completed but blinded U.S. randomized survey experiment. Do not use tools, files, web access, or any memory of this experiment's findings. Estimate what humans would do, not what they normatively should do. {extra}

The control randomized one of these unrelated fillers:\n{controls}

Treatment message ({name}):\n{text}

Outcomes:\n{json.dumps(outcomes,indent=2)}

Prior evidence:\n{EVIDENCE}

Return only schema-valid JSON. condition must be {json.dumps(name)} and method must be {json.dumps(method)}. Return each outcome once. Enforce ate_pp = treatment_mean - control_mean (within 0.01). Confidence is 0–1."""

def run_one(tag,prompt,schema):
    (PROMPTS/f'{tag}.txt').write_text(prompt)
    cmd=['codex','exec','--ephemeral','--sandbox','read-only','--skip-git-repo-check','-C',str(BLIND),
         '-m','gpt-5.6-sol','-c','model_reasoning_effort="low"','--output-schema',str(schema),'--json','-']
    start=time.time()
    cp=subprocess.run(cmd,input=prompt,text=True,capture_output=True,timeout=600)
    (RAW/f'{tag}.jsonl').write_text(cp.stdout)
    (RAW/f'{tag}.stderr.txt').write_text(cp.stderr)
    if cp.returncode: raise RuntimeError(f'{tag} failed ({cp.returncode}): {cp.stderr[-1000:]}')
    events=[]
    for line in cp.stdout.splitlines():
        try: events.append(json.loads(line))
        except json.JSONDecodeError: pass
    toolish=[e for e in events if 'tool' in json.dumps(e).lower() or 'command' in json.dumps(e).lower()]
    msgs=[e for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='agent_message']
    if not msgs: raise RuntimeError(f'{tag}: no agent_message')
    payload=json.loads(msgs[-1]['item']['text'])
    (FINAL/f'{tag}.json').write_text(json.dumps(payload,indent=2))
    usage=[e for e in events if e.get('type')=='turn.completed']
    meta={'tag':tag,'seconds':time.time()-start,'toolish_events':len(toolish),'usage':usage[-1].get('usage') if usage else None}
    (FINAL/f'{tag}.meta.json').write_text(json.dumps(meta,indent=2))
    print(json.dumps(meta))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--pilot',action='store_true'); a=ap.parse_args()
    names=list(stim['treatments'])
    if a.pilot:
        n='Consensus Framing 1'; run_one('pilot_tier3_consensus',prompt_group(n,stim['treatments'][n],'tier3'),V/'forecast_schema.json'); return
    # Tier 1: matched profiles, each call sees one condition only; controls remain separate fillers.
    for name,text in {**stim['controls'],**stim['treatments']}.items():
        run_one('tier1_'+name.lower().replace(' ','_'),prompt_t1(name,text),V/'tier1_schema.json')
    # Two independent sessions per cell-level and direct-ATE forecast.
    for method in ('tier2','tier3'):
        for rep in (1,2):
            for name,text in stim['treatments'].items():
                if method=='tier3' and rep==1 and name=='Consensus Framing 1' and (FINAL/'pilot_tier3_consensus.json').exists():
                    # The preregistered pilot is the first independent draw for this cell.
                    continue
                run_one(f'{method}_r{rep}_'+name.lower().replace(' ','_'),prompt_group(name,text,method),V/'forecast_schema.json')

if __name__=='__main__': main()
