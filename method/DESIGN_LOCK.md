# Silicon Sample design lock

**Re-locked UTC:** 2026-08-30T23:52:50Z  
**Input fingerprint manifest:** `SHA256_MANIFEST.csv`  
**Manifest SHA-256:** `3ae7c0e4c34dba69609d384d71a6c6e7db5a4f590236f9eca88e0d0e48913d57`  
**Status:** target generation has not begun. This lock supersedes the 23:46:27Z version after the user's explicit instruction to make execution cheaper.

## Locked decisions

- Forecast model: OpenAI `gpt-5.6-sol`; ChatGPT-authenticated Codex CLI; low reasoning; compact structured JSON; ephemeral, read-only calls. No API key or separately billed endpoint. Temperature, top-p, and provider seed unavailable/unset. Construction seed `20260830`.
- Exactly three entries: Tier 1 participant simulation; Tier 2 independent direct cell means; Tier 3 independent evidence-conditioned direct ATEs.
- Exactly one primary: **Tier 2**. Tier 1 and Tier 3 are secondary.
- Tier 1: 9,000 respondents (500 × 16 interventions, 1,000 shared control), compact fixed-order arrays, two 250-person calls per intervention and one call per control filler (35 calls), concise demographics only, matched core profiles, exact state branches and filler assignment, scored survey session, code-computed composites.
- Tier 2: one condition per call containing 13 separately labeled condition×outcome batches and all 27 moderator levels; three independent calls per condition (51 calls), componentwise median, fixed weights, and constrained coherence projection. No call contains multiple treatment conditions.
- Tier 3: one intervention per call containing 13 separately labeled outcome forecasts; three independent calls per intervention (48 calls) and outcome-wise median; no numerical mechanism ontology and no other treatment condition in a call.
- Calibration: control levels unchanged; multiply treatment-minus-control effects by 0.5. Tier 1 implements this as an exactly half-profile, SHA-ranked matched-control response-block mixture; Tier 2 calibrates coherent deviations; Tier 3 calibrates median ATEs.
- Comparative rank reconciliation: disabled because no held-out improvement was established.
- Cross-method ensemble: disabled because weights could not be learned and independently tested at study level.
- Retry: no more than two identical-substance retries for transport, timeout, rate-limit, refusal, schema, completeness, finite-value, duplicate-ID, or arithmetic errors. Never retry based on forecast value.
- Cost: 134 target calls; expected incremental cash cost $0 within the included ChatGPT/Codex allowance. Stop before any credit purchase, flex billing, API-key switch, or paid continuation. Conservative API-equivalent planning value $25–42 is not an invoice.
- Post-lock handling: only deterministic parsing, composite computation, the locked calibration, bounds/coherence projection, validation, and naming/metadata completion are allowed. No method edits based on target values and no manual target-number edits.

The complete execution definition is in `PROTOCOLS_AND_PROMPTS.md`; evidence routing is in `TARGET_EVIDENCE_MAP.csv`; baseline aggregation weights are in `MODERATOR_WEIGHTS.csv`; model behavior is in `RUN_CONFIG.md`; and costs/gates are in `COST_ESTIMATE.md`. These files and all official/evidence inputs are fingerprinted by the manifest.

## Approved changes after lock

The sole revision was the user-directed 2026-08-30 cost reduction, made before target generation: compact serialization and condition-level multi-outcome batching reduced projected target calls from 1,467 to 134 without mixing treatments or reducing coverage. A genuine official-schema conflict may be corrected only by documenting the authoritative source, exact diff, reason, timestamp, replacement manifest, and replacement lock hash before any affected call. Forecast values can never motivate a change.
