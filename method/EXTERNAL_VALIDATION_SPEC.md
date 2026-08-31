# External validation specification and leakage controls

**Frozen operationally before forecast calls:** 2026-08-30. The executable preparation and forecasting procedures are `scripts/prepare_external_validation.py` and `scripts/run_external_validation.py`; their file modification times precede the first successful generation. The scorer was run only after all outputs were frozen.

## Inclusion and exclusion rules

Include completed randomized human experiments with (1) adult samples, prioritizing U.S. quota or probability samples; (2) text, image, or short-video messages deliverable in an online survey; (3) a no-message, attention-placebo, or unrelated-text control; (4) outcomes mappable to percentage points of their scale range; and (5) legally accessible stimuli plus respondent-level data or published cell effects. Keep a whole study in one role. Exclude this benchmark, pilots or interim results, other teams' work, studies without recoverable stimulus content, observational associations, and fitted coefficients that cannot be reconstructed on the benchmark scale.

The fixed evaluation study is Voelkel et al. (2026), selected because it is a completed U.S. climate-message megastudy using the benchmark's exact necktie/baseball/dance fillers. Four treatments were chosen before forecasting to span mechanisms and formats: Consensus Framing 1, Dire But Solvable, Purity, and Warmth. The four outcomes are belief, concern, general policy support, and political behavioral intention, each an item mean on 0–100. Effects are unadjusted treatment means minus the pooled three-filler mean, matching benchmark scoring rather than the paper's covariate-adjusted estimand. This yields 16 ATEs. No individual cell was selected or removed after inspection.

The broader archive (`EVIDENCE_LIBRARY.csv`) is calibration context, not an evaluation row set. The 63-country and 27-country megastudies and the U.S. meta-analysis supplied priors to the aggregate forecasters. The post-model-cutoff 2026 coordinated-ensemble study is retained as qualitative robustness evidence only because the exact stimuli were not publicly downloadable; it is not scored. Study-level leave-one-out validation is not possible with one fully reproducible held-out U.S. filler-control study and is an explicit limitation.

## Blinding and leakage controls

- Human effects are generated into `validation/hidden_outcomes/`; forecast calls run with working root `validation/blind_context` under a read-only sandbox.
- Prompts contain only exact historical stimuli, outcome wordings, and external priors; they prohibit tools, files, web use, and reliance on remembered findings.
- Each CLI call is ephemeral. JSONL logs are inspected automatically for tool/command events; all 23 successful calls had zero.
- Target benchmark stimuli were never passed to a forecast call. The validation study's outcomes were not read until all generations were frozen.
- Raw generations are retained without value-based rejection. One Tier 1 attempt failed before generation because the API rejected a schema missing `type`; the corrected-schema retry is logged. No valid generation was discarded.
- The model's knowledge cutoff (2026-02-16) is after the validation paper's publication. Prompt/process blinding cannot rule out memorization, so all results are labeled provisional and uncertainty is not treated as a clean study-level generalization estimate.

## Reproduced procedures

Tier 1 used 50 fixed, concise demographic profiles, matched across each treatment and each filler. Each call saw only one message and returned participant records; the control is the pooled 150 filler respondents. Tier 2 directly forecast control and treatment population cell means. Tier 3 directly forecast evidence-conditioned ATEs and compatible means. Tier 2 and Tier 3 used two independent ephemeral sessions per treatment, with all four historical outcomes batched inside each condition-level call; their cell forecasts are the median (with two values, their midpoint). This validates condition-level multi-outcome batching while preserving treatment isolation. The pilot is retained as Tier 3's first Consensus draw. Model and settings were identical: OpenAI `gpt-5.6-sol`, Codex CLI, low reasoning, structured output; temperature, top-p, and seed were unavailable.

## Metrics and selection rule

All metrics use percentage points of scale range: pooled Pearson; Pearson after separately mean-centering predictions and human effects within outcome; Spearman; directional agreement (exact predicted zero earns 0.5); RMSE; mean signed error (`prediction − human`); and OLS calibration intercept/slope from `human = intercept + slope × prediction`. Selection follows the user-specified rule: best mean held-out pooled Pearson; if methods are indistinguishable within validation uncertainty, lower RMSE; then higher within-outcome Pearson.

Candidate calibration rules were no shrinkage and a simple 0.5 multiplier. The latter was externally motivated before target prediction by simulation calibration slopes of .56 in the 70-study archive and .34 in large coordinated experiments. It is not a fitted cell-specific coefficient. Rank reconciliation and cross-method ensembles require separate held-out improvement and were not tested within the $2 validation gate; therefore both are disabled.
