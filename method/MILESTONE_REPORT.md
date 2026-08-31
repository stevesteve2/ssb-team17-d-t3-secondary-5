# First milestone report — approval checkpoint

## Outcome

The benchmark has been reconstructed, 30 external evidence records and a 208-pair evidence-routing map have been assembled, the three distinct methods have been historically tested, exact execution protocols are locked, and every design input is fingerprinted. **No benchmark target forecast has been generated.**

Recommended configuration:

- sole primary: **Tier 2 direct cell-level forecasts**;
- Tier 1 size: **9,000** (500 per intervention, 1,000 control);
- Tier 1 secondary: demographic-only matched participant simulation;
- Tier 3 secondary: direct evidence-conditioned ATE forecast;
- calibration: 0.5 on treatment-minus-control effects only;
- rank reconciliation: none;
- cross-method ensemble: none.

The primary choice follows the requested rule. Tier 1's held-out pooled Pearson was highest (0.385 uncalibrated), but one study/four treatment clusters cannot distinguish correlations. Tier 2 therefore wins the RMSE tie-break: 1.569 pp uncalibrated and 1.445 pp with locked calibration, versus Tier 3's 1.590/1.478. Proposed-method Tier 1 block calibration yields RMSE 1.671.

## Deliverables

- `RUN_CONFIG.md`: execution and forecast model/interface/settings.
- `BENCHMARK_SPEC.md`: official conditions, items, formulas, quotas, schema, scoring, validator, registration/deposit requirements.
- `EVIDENCE_MEMO.md`: concise synthesis (under five manuscript pages at ordinary formatting).
- `EVIDENCE_LIBRARY.csv`: 30 structured source records.
- `TARGET_EVIDENCE_MAP.csv`: all 16 × 13 pairs, source provenance, no target effects.
- `EXTERNAL_VALIDATION_SPEC.md`: archive rules, estimand, split limitation, and leakage controls.
- `EXTERNAL_VALIDATION_RESULTS.md`: all requested metrics, method decision, cost, limitations.
- `PROTOCOLS_AND_PROMPTS.md`: exact tier protocols, prompt templates, calibration/coherence/retry rules.
- `MODERATOR_WEIGHTS.csv`: all 27 fixed aggregation weights and provenance.
- `COST_ESTIMATE.md`: calls, tokens, runtime, costs, sample-size curve, approval gates.
- `DESIGN_LOCK.md`, `SHA256_MANIFEST.csv`, and `DESIGN_LOCK.sha256`: locked decision and fingerprints.
- `validation/`: raw prompts/logs, parsed forecasts, hidden human ATEs, metrics, usage, and scripts.

## Unresolved assumptions, access issues, and risks

1. **Required personal metadata is missing:** team ID, author names, ORCID(s), affiliations, and any requested contact/deposit details. None will be invented.
2. **Allowance visibility:** the compact run uses the ChatGPT-included Codex allowance and has expected incremental cash cost of $0. The CLI does not expose a reliable dollar value for allowance consumption. A historical compact-schema probe will verify capacity; execution stops rather than purchasing credits or switching to API billing.
3. **Validation is narrow:** one U.S. filler-control study, four interventions, 16 ATEs. Study-level calibration/evaluation separation was impossible with fully recoverable close-match stimuli; pretraining memorization is also possible.
4. **Moderator weights:** gender `Other`, education degree split, and custom income bins require approximations because benchmark quotas/source tables do not align exactly. Sensitivity checks are allowed diagnostically, but locked submitted weights cannot be selected after seeing target forecasts.
5. **Tier 1 calibration:** the matched-control response-block mixture is automated and coherent but is supported by a small validation replay, not broad microdata validation.
6. **Access limits:** several cited supplements/datasets were unavailable or view-only. They were used qualitatively, never as invented numerical estimates. The post-cutoff coordinated-ensemble study could not serve as a scored holdout because exact stimuli were inaccessible.
7. **Operational risk:** the compact design uses 134 target calls (down from 1,467). It may still encounter allowance or rate limits. Frozen retries and raw logs cover failures; valid values cannot be cherry-picked.
8. **Submission status:** no template directories, team-specific filenames, registration metadata, deposit, email, or submission have been created or sent. Those actions wait for approval and real metadata.

## Approval requested

Approve only the next stage if you want target execution to begin under `DESIGN_LOCK.md`. The revised design authorizes **no incremental dollar spend**: it uses included Codex allowance and stops if paid credits would be required. Supply the non-inventable metadata before final packaging.
