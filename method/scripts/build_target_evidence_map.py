#!/usr/bin/env python3
"""Build the preregistered 16 x 13 evidence-routing map (no target forecasts)."""
import csv
from pathlib import Path

conditions = {
    "Corporate reliance": ("AMAZEEN2025;GOLDBERG2021;VOELKEL2026", "corporate accountability and messenger evidence"),
    "Social justice": ("VLASCEANU2024_BELIEF;RODE2021;VOELKEL2026", "moral and justice framing evidence"),
    "Interview Prof. Maraun": ("ORCHINIK2024_HISTORY;ANNENBERG2024;RODE2021", "scientist credibility and explanatory-message evidence"),
    "Funding": ("ORCHINIK2024_INSTITUTIONS;ANNENBERG2024;NSB2024", "institutional incentives and scientist-trust evidence"),
    "Oil industry misinformation": ("AMAZEEN2025;GOLDBERG2021;RODE2021", "misinformation correction and inoculation evidence"),
    "Measurement & modeling (1)": ("ORCHINIK2024_HISTORY;ORCHINIK2024_INSTITUTIONS;HAUSFATHER2020", "climate-method and credibility evidence"),
    "Former skeptics": ("GOLDBERG2021;RODE2021;VLASCEANU2024_BELIEF", "conservative messenger and persuasion evidence"),
    "High public trust": ("ANNENBERG2024;NSB2024;SABHERWAL2026", "descriptive trust-norm and baseline evidence"),
    "Measurement & modeling (2)": ("ORCHINIK2024_HISTORY;ORCHINIK2024_INSTITUTIONS;HAUSFATHER2020", "climate-method and credibility evidence"),
    "Peer-review": ("ORCHINIK2024_INSTITUTIONS;ANNENBERG2024;NSB2024", "scientific-process and institutional-trust evidence"),
    "Scientist community helpers": ("ANNENBERG2024;NSB2024;VLASCEANU2024_BELIEF", "benevolence/community and scientist-trust evidence"),
    "Consensus": ("GEIGER2024_CONSENSUS;RODE2021;VLASCEANU2024_BELIEF", "direct consensus-message evidence"),
    "Portrait Prof. Cherry": ("ANNENBERG2024;SABHERWAL2026;RODE2021", "scientist individuation and credibility evidence"),
    "Model accuracy": ("HAUSFATHER2020;ORCHINIK2024_HISTORY;ORCHINIK2024_INSTITUTIONS", "historical model-skill evidence"),
    "Interview Prof. Sebille": ("ORCHINIK2024_HISTORY;ANNENBERG2024;RODE2021", "scientist credibility and explanatory-message evidence"),
    "Extreme weather predictions": ("THOMASWALTERS2026_ATTRIBUTION;THOMASWALTERS2026_DISTAL;RODE2021", "direct extreme-weather attribution evidence"),
}

outcomes = {
    "trust_multidimensional": ("proximal", "trust/credibility evidence receives greatest weight"),
    "trust_post": ("proximal", "general scientist-trust evidence"),
    "distrust_post": ("proximal", "reverse-valence trust evidence; negative effects remain possible"),
    "funding_perceptions": ("proximal", "funding condition is especially direct; otherwise transport cautiously"),
    "policy_role_mean": ("intermediate", "institutional-role evidence and policy-distance discount"),
    "inst_trust_mean": ("intermediate", "broader institutional trust; stronger transport penalty"),
    "belief_post": ("intermediate", "belief and scientific-consensus experiments"),
    "concern_mean": ("intermediate", "worry/concern experiments; ceiling effects likely"),
    "policy_general": ("distal", "policy support generally smaller than belief effects"),
    "policy_specific_mean": ("distal", "specific-policy evidence; ideological resistance plausible"),
    "behavior_mean": ("distal", "intentions do not inherit attitude effects automatically"),
    "donation_ams": ("behavioral", "observed donation experiments only; null is default absent direct evidence"),
    "newsletter_signup": ("behavioral", "binary conversion evidence only; probability-scale effects"),
}

common = {
    "proximal": "ASHOKKUMAR2026_MEGA;RODE2021;VOELKEL2026",
    "intermediate": "RODE2021;VLASCEANU2024_BELIEF;VOELKEL2026",
    "distal": "VLASCEANU2024_POLICY;VOELKEL2026;GOLDWERT2026_EFFECT",
    "behavioral": "VLASCEANU2024_BEHAVIOR;NISA2019;GOLDWERT2026_BASELINE;GOLDWERT2026_EFFECT",
}

rows = []
for condition, (specific_ids, condition_note) in conditions.items():
    for outcome, (distance, outcome_note) in outcomes.items():
        ids = []
        for item in (specific_ids + ";" + common[distance]).split(";"):
            if item and item not in ids:
                ids.append(item)
        direction = "uncertain; null and negative allowed"
        if outcome == "distrust_post":
            direction = "usually nonpositive, but backfire/null allowed"
        elif condition == "Consensus" and outcome in {"belief_post", "concern_mean"}:
            direction = "small positive is better supported than for distal outcomes"
        elif condition == "Extreme weather predictions" and outcome in {"belief_post", "concern_mean"}:
            direction = "small positive; frame-specific evidence exists"
        elif outcome in {"donation_ams", "newsletter_signup"}:
            direction = "near-null prior; either sign allowed"
        strength = "moderate" if (condition in {"Consensus", "Extreme weather predictions", "Model accuracy", "Oil industry misinformation"} and distance != "behavioral") else "low"
        rows.append({
            "condition": condition,
            "outcome": outcome,
            "outcome_distance": distance,
            "source_ids": ";".join(ids),
            "evidence_strength": strength,
            "qualitative_direction_only": direction,
            "transport_notes": f"{condition_note}; {outcome_note}. Match wording, scale, population, control, and headroom before numerical use.",
            "target_effect_present": "no",
        })

out = Path("TARGET_EVIDENCE_MAP.csv")
with out.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
assert len(rows) == 208
print(f"wrote {len(rows)} rows to {out}")
