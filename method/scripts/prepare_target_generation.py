#!/usr/bin/env python3
"""Compile official target stimuli, scored items, profiles, and compact schemas."""
import csv, json, random, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OFF=ROOT/'official_submission_template'; TG=ROOT/'target_generation'
for p in ('inputs','schemas','prompts','raw','parsed','processed','blind_context'):
    (TG/p).mkdir(parents=True,exist_ok=True)

# Exact condition text from the pinned official plain-text questionnaire.
q=(OFF/'survey/questionnaire.txt').read_text()
condition_start=q.index('### control — filler text 1')
condition_end=q.index('\n----------------------------------------------------------------------\nTRANSITION',condition_start)
segment=q[condition_start:condition_end]
parts=re.split(r'^### ',segment,flags=re.M)
sections={}
for part in parts:
    if not part.strip(): continue
    head,_,body=part.partition('\n')
    sections[head.strip()]=body.strip()
controls={
 'control neckties':sections['control — filler text 1 of 3: The History of Neckties'],
 'control baseball':sections['control — filler text 2 of 3: The Rules of Baseball'],
 'control dances':sections['control — filler text 3 of 3: Different Types of Dances'],
}
conditions=['Corporate reliance','Social justice','Interview Prof. Maraun','Funding','Oil industry misinformation',
 'Measurement & modeling (1)','Former skeptics','High public trust','Measurement & modeling (2)','Peer-review',
 'Scientist community helpers','Consensus','Portrait Prof. Cherry','Model accuracy','Interview Prof. Sebille','Extreme weather predictions']
interventions={c:sections[c] for c in conditions}
(TG/'inputs/conditions.json').write_text(json.dumps({'controls':controls,'interventions':interventions},indent=2))

# Raw scored fields: composites are deliberately excluded and computed in code.
raw_fields=['trust_competence_1','trust_competence_2','trust_competence_3',
 'trust_integrity_1','trust_integrity_2','trust_integrity_3','trust_benevolence_1','trust_benevolence_2','trust_benevolence_3',
 'trust_openness_1','trust_openness_2','trust_openness_3','trust_post','distrust_post','funding_5',
 'policy_role_1','policy_role_2','policy_role_3','policy_role_4',
 'inst_trust_epa','inst_trust_nasa','inst_trust_noaa','inst_trust_universities','inst_trust_federal_gov',
 'belief_post','concern_1','concern_2','concern_3','policy_general',
 'policy_specific_1','policy_specific_2','policy_specific_3','policy_specific_4','policy_specific_5','policy_specific_6','policy_specific_7',
 'behavior_meat','behavior_transport','behavior_solar','behavior_fly','behavior_talk','behavior_donate','donation_ams','newsletter_signup']
cb=list(csv.DictReader((OFF/'codebook.csv').open()))
by_target={r['target_label']:r for r in cb}
items=[]
for field in raw_fields:
    lookup={'funding_5':'funding_perceptions'}.get(field,field)
    r=by_target[lookup]
    items.append({'field':field,'question':r['question_text'],'response':r['response_options']})
assert len(items)==44
(TG/'inputs/scored_items.json').write_text(json.dumps({'field_order':['profile_index']+raw_fields,'items':items},indent=2))

outcomes=[
 {'name':'trust_multidimensional','scale':[0,100],'definition':'Mean of four three-item trust dimensions; 12 exact trust items listed in scored_items.json.'},
 {'name':'trust_post','scale':[0,100],'definition':'How much do you trust climate scientists? 0 not at all, 100 very strongly.'},
 {'name':'distrust_post','scale':[0,100],'definition':'How much do you distrust climate scientists? 0 not at all, 100 very strongly.'},
 {'name':'funding_perceptions','scale':[0,100],'definition':'100 minus funding_5; higher means perceives too little federal climate-research spending.'},
 {'name':'policy_role_mean','scale':[0,100],'definition':'Mean of four exact climate-scientist policy-role agreement items.'},
 {'name':'inst_trust_mean','scale':[0,100],'definition':'Mean trust in EPA, NASA, NOAA, universities/colleges, and federal government.'},
 {'name':'belief_post','scale':[0,100],'definition':'Accuracy of “Human activities are causing climate change.”'},
 {'name':'concern_mean','scale':[0,100],'definition':'Mean of concern, seriousness, and importance relative to other U.S. issues.'},
 {'name':'policy_general','scale':[0,100],'definition':'Support for “The U.S. government should do more to reduce global warming.”'},
 {'name':'policy_specific_mean','scale':[0,100],'definition':'Mean support for seven exact climate policies.'},
 {'name':'behavior_mean','scale':[0,100],'definition':'Mean likelihood of six climate-mitigation behaviors in next 12 months.'},
 {'name':'donation_ams','scale':[0,10],'definition':'Whole-dollar donation from a $10 bonus to the American Meteorological Society.'},
 {'name':'newsletter_signup','scale':[0,1],'definition':'Probability of subscribing after the exact Talking Climate newsletter offer page.'},
]
(TG/'inputs/outcomes.json').write_text(json.dumps(outcomes,indent=2))

# Deterministic quota-grounded profiles. State counts are 2020 Census apportionment populations.
weights=list(csv.DictReader((ROOT/'MODERATOR_WEIGHTS.csv').open()))
wm={}
for r in weights: wm.setdefault(r['moderator'],[]).append((r['moderator_level'],float(r['weight'])))
state_pop={
'Alabama':5024279,'Alaska':733391,'Arizona':7151502,'Arkansas':3011524,'California':39538223,'Colorado':5773714,
'Connecticut':3605944,'Delaware':989948,'Florida':21538187,'Georgia':10711908,'Hawaii':1455271,'Idaho':1839106,
'Illinois':12812508,'Indiana':6785528,'Iowa':3190369,'Kansas':2937880,'Kentucky':4505836,'Louisiana':4657757,
'Maine':1362359,'Maryland':6177224,'Massachusetts':7029917,'Michigan':10077331,'Minnesota':5706494,'Mississippi':2961279,
'Missouri':6154913,'Montana':1084225,'Nebraska':1961504,'Nevada':3104614,'New Hampshire':1377529,'New Jersey':9288994,
'New Mexico':2117522,'New York':20201249,'North Carolina':10439388,'North Dakota':779094,'Ohio':11799448,'Oklahoma':3959353,
'Oregon':4237256,'Pennsylvania':13002700,'Rhode Island':1097379,'South Carolina':5118425,'South Dakota':886667,
'Tennessee':6910840,'Texas':29145505,'Utah':3271616,'Vermont':643077,'Virginia':8631393,'Washington':7705281,
'West Virginia':1793716,'Wisconsin':5893718,'Wyoming':576851,'Washington, D.C.':689545}

def allocate(level_weights,n):
    raw=[w*n for _,w in level_weights]; base=[int(x) for x in raw]
    for i in sorted(range(len(raw)),key=lambda j:raw[j]-base[j],reverse=True)[:n-sum(base)]: base[i]+=1
    return [level for (level,_),k in zip(level_weights,base) for _ in range(k)]

rng=random.Random(20260830)
def make_profiles(n,start):
    cols={m:allocate(wm[m],n) for m in ('gender','age_band','race','education','income','party')}
    for v in cols.values(): rng.shuffle(v)
    states=rng.choices(list(state_pop),weights=list(state_pop.values()),k=n)
    rows=[]
    for i in range(n):
        band=cols['age_band'][i]; lo,hi={'18-29':(18,29),'30-44':(30,44),'45-59':(45,59),'60+':(60,85)}[band]
        age=rng.randint(lo,hi)
        rows.append({'profile_index':start+i,'profile_id':f'p{start+i:05d}','gender':cols['gender'][i],'age_band':band,
          'year_birth':2026-age,'race':cols['race'][i],'education':cols['education'][i],'income':cols['income'][i],
          'party':cols['party'][i],'state':states[i]})
    return rows

core=make_profiles(500,1); extra=make_profiles(500,501); all_control=core+extra
rng.shuffle(all_control)
sizes=[334,333,333]; filler_names=list(controls); pos=0
control_assign={}
for name,size in zip(filler_names,sizes):
    for p in all_control[pos:pos+size]: control_assign[p['profile_id']]=name
    pos+=size
with (TG/'inputs/profiles.csv').open('w',newline='') as f:
    fields=list((core+extra)[0]);w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(core+extra)
(TG/'inputs/control_assignment.json').write_text(json.dumps(control_assign,indent=2))

# Shared compact schema builders.
def write_t1_schema(n,name):
    schema={'$schema':'https://json-schema.org/draft/2020-12/schema','type':'object','additionalProperties':False,
      'required':['condition','rows'],'properties':{'condition':{'type':'string'},'rows':{'type':'array','minItems':n,'maxItems':n,
      'items':{'type':'array','minItems':45,'maxItems':45,'items':{'type':'integer'}}}}}
    (TG/f'schemas/{name}.json').write_text(json.dumps(schema,indent=2))
for n in (250,333,334): write_t1_schema(n,f'tier1_{n}')
cell_schema={'$schema':'https://json-schema.org/draft/2020-12/schema','type':'object','additionalProperties':False,
 'required':['condition','rows'],'properties':{'condition':{'type':'string'},'rows':{'type':'array','minItems':13,'maxItems':13,
 'items':{'type':'array','minItems':28,'maxItems':28,'items':{'type':'number','minimum':-100,'maximum':100}}}}}
(TG/'schemas/tier2.json').write_text(json.dumps(cell_schema,indent=2))
t3item={'type':'object','additionalProperties':False,'required':['outcome','ate','low','high','refs','adjustment','confidence','null_negative'],
 'properties':{'outcome':{'type':'string','enum':[o['name'] for o in outcomes]},'ate':{'type':'number','minimum':-100,'maximum':100},
 'low':{'type':'number','minimum':-100,'maximum':100},'high':{'type':'number','minimum':-100,'maximum':100},
 'refs':{'type':'array','minItems':1,'maxItems':3,'items':{'type':'string'}},'adjustment':{'type':'string'},
 'confidence':{'type':'number','minimum':0,'maximum':1},'null_negative':{'type':'boolean'}}}
t3schema={'$schema':'https://json-schema.org/draft/2020-12/schema','type':'object','additionalProperties':False,
 'required':['condition','rows'],'properties':{'condition':{'type':'string'},'rows':{'type':'array','minItems':13,'maxItems':13,'items':t3item}}}
(TG/'schemas/tier3.json').write_text(json.dumps(t3schema,indent=2))
print('prepared',len(conditions),'interventions,',len(items),'raw items,',len(core)+len(extra),'profiles')
