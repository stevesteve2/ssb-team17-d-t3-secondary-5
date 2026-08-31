# Locked protocols and prompt templates

## Shared execution contract

All three entries use OpenAI `gpt-5.6-sol` through `codex exec`, authenticated by the existing ChatGPT login, low reasoning effort, ephemeral sessions, read-only forecast workspaces, and strict JSON Schema. No API key or separately billed API endpoint is used. The run may consume only the included ChatGPT/Codex allowance: if the CLI reports that the allowance is exhausted or requests purchased credits, execution stops and asks the user rather than buying or authorizing credits. Temperature, top-p, and provider seed are not exposed by this interface and remain unset. The deterministic construction seed is `20260830`; SHA-256 supplies stable tie-breaking and calibration assignments. Calls time out after 600 seconds. A failed transport, timeout, rate-limit, schema, duplicate-ID, missing-field, nonfinite-value, or arithmetic-consistency check receives at most two retries with the identical substantive prompt plus the validation error. A valid response is never rejected because its values are surprising. Every prompt, JSONL event stream, stderr stream, parsed response, retry, refusal, clip, and exclusion is retained.

The three base-forecast directories are isolated. No base prompt or model session can read another method's outputs. Shared inputs are restricted to the official survey, benchmark specification, evidence library/map, external baseline sources, moderator weights, and code utilities. Target calls cannot browse or use tools. The target call list and canonical sorting are generated before the first call.

The externally selected calibration multiplier is 0.5. It applies only to treatment-minus-control effects, not to control levels. Rank reconciliation is disabled. Cross-method ensembling is disabled. Tier 2 alone is marked primary; Tier 1 and Tier 3 are secondary.

## Tier 1: individual synthetic participants

### Sample and construction

Use exactly 9,000 submitted respondents: 500 in each of 16 interventions and 1,000 control. Create 500 quota-matched core profiles and reuse the same profiles once in every intervention; the first 500 controls use those core profiles, while another 500 independently drawn control profiles improve the shared baseline. Assign control fillers by seeded shuffle as 334 neckties, 333 baseball, and 333 dances. Intervention respondents are split into two 250-profile calls; each control filler is one call. This is **35 calls total**, and every call still contains one condition/text only. For Extreme weather predictions, group profiles by the exact rendered state branch within the condition payload while ensuring each record sees only its own branch; for control, insert only the assigned filler.

Profiles contain only `profile_id`, state, gender, age band/year, race, education, income, and party, using official factor levels and quota distributions. They contain no biography, expected reaction, condition-dependent trait, or forecast. Demographics are generated once with iterative proportional fitting to the joint gender×age and gender×race quotas; other margins use `MODERATOR_WEIGHTS.csv`. No latent pretreatment attitudes are used because the validation did not justify an external joint distribution.

Each batch is one persistent post-message survey session. It follows the official scored order: message; 12 multidimensional-trust items; remaining scored item blocks in survey order; newsletter offer page; newsletter signup. Optional unscored content is omitted. The model returns raw scored item responses, including the four policy-role, five institution, three concern, seven specific-policy, and six behavior items. To avoid repeated JSON keys, the structured output is a compact array of integer arrays with one frozen field-order header; code expands it immediately and checks row width and ID uniqueness. Code computes every composite; it never asks the model for a composite. Sliders are integers 0–100, donation is an integer 0–10, and signup is 0/1.

To implement the validated 0.5 effect calibration without arbitrary cell editing, create matched control responses independently. For each intervention, rank its 500 core IDs by `SHA256(condition|profile_id|calibration)` and replace the complete response block of exactly 250 IDs with that ID's independently generated matched-control block. The other 250 retain their intervention response. Replacement is all-or-none across outcomes, preserving individual coherence, integer formats, and the newsletter dependency. The expected intervention effect is halved; the operation is fixed and condition-blind. Controls are unchanged. Composites are recomputed after replacement.

### Tier 1 batch prompt

```text
SYSTEM CONTRACT
Act as ordinary U.S. survey respondents, not as an analyst. Do not use tools, files,
the web, literature, hypotheses, or knowledge of other conditions. Every profile sees
only the message below. Respond independently and preserve ordinary human variance.
Neutral, skeptical, internally mixed, and negative reactions are allowed. Do not make
answers conform to an expected treatment effect. Return JSON only, exactly matching
the supplied schema and profile IDs.

MESSAGE SHOWN TO EVERY PROFILE IN THIS BATCH
{{exact rendered intervention, state branch, or single control filler}}

PROFILE BATCH
{{250 concise profiles, or one control-filler batch of 333/334; compact canonical JSON}}

SURVEY
{{exact official scored item wording, anchors, order, and newsletter offer page}}

RESPONSE RULES
Answer each raw item. All sliders are integers 0..100; donation is a whole dollar
0..10; newsletter signup is 0 or 1. Return one compact integer array per profile in
the supplied fixed field order. Do not repeat field names, return explanations, or
return composites.
```

## Tier 2: direct cell-level means

Tier 2 never consumes Tier 1 records. A call contains **one condition only**, never multiple treatment conditions, and contains 13 separately labeled condition×outcome forecast batches; every batch includes all 27 moderator levels. This preserves the prompt's treatment-isolation rule while amortizing the agent envelope. Three independent ephemeral calls are made per condition and the componentwise median is frozen: 3 control calls plus 16×3 intervention calls, **51 calls total**. Each condition×outcome batch receives the exact relevant filler control, exact treatment, exact outcome wording/scale, applicable baseline, `MODERATOR_WEIGHTS.csv`, and compact source rows routed by `TARGET_EVIDENCE_MAP.csv`. Results use compact numeric arrays with a frozen header.

Control forecasts return a population mean and 27 subgroup means. Within each moderator, center subgroup deviations so their fixed-weight mean equals the control population mean. Intervention calls return a raw population shift and raw subgroup shifts relative to their corresponding control cells. Unsupported interaction deviations must be zero; evidence-backed deviations remain strongly pooled. After medians, let `e` be the population shift, `e_l` level shifts, and weights `w_l`. Set the calibrated coherent shift to `e*_l = 0.5[e_l − sum(w_l e_l) + e]`; the main shift is `e*=0.5e`. Thus each moderator's weighted treatment mean equals the Tier 2 main mean. Apply a bounded least-squares projection only if required to respect 0–100, 0–10, or 0–1 bounds while retaining the weighted mean. All projection events are logged.

### Tier 2 control prompt

```text
Forecast human population means for the exact U.S. survey cell below. Do not simulate
individuals, use tools, browse, or recall benchmark outcomes. Estimate what people
would report, not what they should report. Similar external questions are anchors,
not identical measures.

CONTROL: one respondent sees exactly one randomly assigned filler:
{{neckties}} / {{baseball}} / {{dances}}
OUTCOME: {{exact wording, response anchors, original scale, survey position}}
BASELINE SOURCES: {{dated population/wording/scale table}}
MODERATOR LEVELS AND WEIGHTS: {{all 27 canonical levels}}

Return JSON containing the population mean and all 27 level means. Use the original
scale. Introduce subgroup differences only when supported; otherwise return a common
or nearly common mean. Include no explanation outside the schema.
```

### Tier 2 intervention prompt

```text
Forecast human cell means in a U.S. randomized survey experiment. Do not simulate
individual records, use tools, browse, or rely on other treatments. You see exactly
one treatment condition and 13 independent outcome batches. For each batch, estimate a shift relative to the exact
filler control, not a normatively desirable response. Small, null, and negative
effects are allowed. Do not transfer an attitude effect into behavior.

CONTROL TEXTS: {{three exact fillers}}
TREATMENT: {{canonical name for logging only, followed by exact rendered text}}
OUTCOME: {{exact wording, anchors, original scale, survey position}}
CONTROL BASELINE: {{population and 27 level means}}
CLOSEST EVIDENCE: {{compact published rows with population, intervention/control,
outcome/scale, effect and uncertainty, date, and transport caveats}}
MODERATOR WEIGHTS: {{27 canonical levels}}

Return compact JSON arrays with, for each outcome, one raw population treatment shift
and 27 raw level shifts plus corresponding means. Unsupported interaction deviations
must be zero or strongly pooled. Enforce shift = treatment mean − supplied control
mean. Do not reason across outcomes; JSON only.
```

## Tier 3: evidence-conditioned ATEs

Tier 3 never consumes Tier 1 or Tier 2 forecasts. Make three independent ephemeral calls per intervention, each returning 13 separately labeled absolute forecasts: **48 calls total**. Thus every one of the 208 intervention×outcome pairs still receives three independent forecasts and a median. A call sees one intervention, all exact outcome wordings, the three fillers, compact outcome-specific empirical priors, and relevant baselines/headroom; it never sees another intervention or previous forecast. Multiply each median by 0.5. Clamp only to the mathematically possible ATE range implied by the original scale and control baseline, logging any clamp.

The empirical-prior table contains actual studies, populations, controls, formats, outcome wordings/scales, estimates/uncertainty, and transport concerns. It contains no numerical mechanism ontology or mechanism-to-outcome matrix. A comparative rank pass is not run because it did not receive held-out validation. The direct Tier 3 forecast is submitted without a cross-method ensemble.

### Tier 3 absolute prompt

```text
Forecast 13 separately labeled absolute average treatment effects for one intervention
in a U.S. randomized survey. Do not
use tools, browse, recall benchmark results, inspect other interventions, or infer a
mechanism score. Estimate intervention mean minus the shared filler-control mean in
the outcome's ORIGINAL UNITS. Human one-shot effects are often small; null and
negative effects are allowed. Proximal changes do not automatically imply policy,
donation, signup, or behavior changes.

CONTROL: {{three exact filler texts and assignment rule}}
INTERVENTION: {{exact rendered text; state-weighted branches where applicable}}
OUTCOMES: {{13 exact wordings, anchors, scales, survey order and newsletter dependency}}
U.S. BASELINES/HEADROOM: {{13 dated, wording-aware anchors}}
CLOSEST HUMAN EXPERIMENTS: {{13 compact outcome-specific tables from evidence map}}

Return one compact record per outcome with: ate_original_units; plausible_low;
plausible_high; closest_reference_ids; adjustment code; confidence 0..1; and
null_or_negative_plausible. Do not compare outcomes or mention another target condition.
```

## Automated final checks

Before writing templates, check Tier 1 count/condition minima, unique IDs, canonical factors, integer/binary formats, raw-item bounds, exact composite formulas, and treatment/control calibration provenance. Check Tier 2 has exactly 221 and 5,967 unique rows, all factor labels and bounds, and weighted aggregation residual below `1e-8`. Check Tier 3 has exactly 208 unique original-unit ATEs. Then run the official `Rscript scripts/check.R`, create repository manifests/fingerprints, and retain raw logs. No team ID, author, ORCID, or deposit metadata is invented.
