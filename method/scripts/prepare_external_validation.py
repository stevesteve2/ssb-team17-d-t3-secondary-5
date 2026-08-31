#!/usr/bin/env python3
"""Prepare a blinded five-treatment validation slice from Voelkel et al. (2026)."""
import csv, html, json, re, statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QSF = ROOT / "evidence/sources/voelkel_2026_questionnaire.qsf"
DATA = ROOT / "evidence/sources/voelkel_2026_deidentified.csv"
OUT = ROOT / "validation"
BLIND = OUT / "blind_context"
HIDDEN = OUT / "hidden_outcomes"
for p in (BLIND / "stimuli", HIDDEN): p.mkdir(parents=True, exist_ok=True)

selected = {
    "Consensus Framing 1": "Consensus Framing I",
    "Dire But Solvable Framing": "Dire But Solvable Framing",
    "Purity Framing": "Purity Framing",
    "Warmth Framing": "Warmth Framing",
}
controls = ["Control Baseball", "Control Neckties", "Control Dances"]
control_blocks = {"Control Baseball":"Rules of Baseball", "Control Neckties":"History of Neckties", "Control Dances":"Different Types of Dances"}

qsf = json.load(QSF.open())
blocks = next(x for x in qsf["SurveyElements"] if x["Element"] == "BL")["Payload"]
questions = {x["PrimaryAttribute"]: x["Payload"] for x in qsf["SurveyElements"] if x["Element"] == "SQ"}

def clean(text):
    text = re.sub(r"<img[^>]*>", " [image shown in original] ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()

def block_text(description):
    block = next(b for b in blocks.values() if b.get("Description") == description)
    parts = []
    for e in block.get("BlockElements", []):
        q = questions.get(e.get("QuestionID"))
        if not q or q.get("QuestionType") != "DB": continue
        txt = clean(q.get("QuestionText", ""))
        if txt: parts.append(txt)
    return "\n\n".join(parts)

stimuli = {name: block_text(block) for name, block in selected.items()}
control_texts = {name: block_text(block) for name, block in control_blocks.items()}
(BLIND / "stimuli/stimuli.json").write_text(json.dumps({"treatments":stimuli,"controls":control_texts}, indent=2))

outcome_cols = {
    "belief": ["Belief_Post_1_1", "Belief_Post_2_1", "Belief_Post_3_1"],
    "concern": ["Concern_Post_1_1", "Concern_Post_2_1", "Concern_Post_3_1"],
    "general_policy": ["Policies_Post_1", "Policies_Post_2", "Policies_Post_3"],
    "political_intention": ["Intent_Post_1", "Intent_Post_2", "Intent_Post_3", "Intent_Post_4"],
}
groups = {k:{o:[] for o in outcome_cols} for k in list(selected)+["pooled_control"]}
with DATA.open(newline="") as f:
    for row in csv.DictReader(f):
        cond = row["Condition"]
        key = cond if cond in selected else ("pooled_control" if cond in controls else None)
        if key is None: continue
        for outcome, cols in outcome_cols.items():
            try: vals = [float(row[c]) for c in cols]
            except (ValueError, TypeError): continue
            groups[key][outcome].append(sum(vals)/len(vals))

means = {g:{o:statistics.fmean(v) for o,v in os.items()} for g,os in groups.items()}
rows=[]
for cond in selected:
    for outcome in outcome_cols:
        rows.append({"condition":cond,"outcome":outcome,"human_ate_pp":means[cond][outcome]-means["pooled_control"][outcome],"n_treatment":len(groups[cond][outcome]),"n_control":len(groups["pooled_control"][outcome])})
with (HIDDEN / "human_ates.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
(HIDDEN / "control_means.json").write_text(json.dumps(means["pooled_control"],indent=2))

outcome_text = {
 "belief":"Mean of three 0–100 sliders: climate change is real; caused by human activity; scientific evidence points to it.",
 "concern":"Mean of three 0–100 sliders: worry; negative feelings; importance of climate change.",
 "general_policy":"Mean of three 0–100 support sliders: reduce greenhouse gases; more renewable energy; stronger governmental action.",
 "political_intention":"Mean of four 0–100 likelihood sliders: petition, environmental-group membership, contact official, donate to environmental group.",
}
(BLIND / "outcomes.json").write_text(json.dumps(outcome_text,indent=2))
print("prepared",len(rows),"hidden ATEs; treatment texts",{k:len(v) for k,v in stimuli.items()})
