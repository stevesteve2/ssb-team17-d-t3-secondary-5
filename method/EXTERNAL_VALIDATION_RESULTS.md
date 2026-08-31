# External validation results

## Held-out performance

The uncalibrated results below cover 16 ATEs from one U.S. study. Point estimates should not be mistaken for precise method rankings.

| Method | Pooled Pearson | Within-outcome Pearson | Spearman | Direction | RMSE pp | Signed error pp | Calibration intercept | Calibration slope |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Tier 1 participant simulation | 0.385 | 0.566 | 0.391 | 0.625 | 2.830 | 1.663 | 0.388 | 0.216 |
| Tier 2 direct cell means | −0.071 | 0.485 | −0.082 | 0.625 | **1.569** | 0.379 | 1.172 | −0.166 |
| Tier 3 evidence-conditioned ATE | −0.134 | 0.548 | −0.072 | 0.625 | 1.590 | 0.267 | 1.319 | −0.301 |

Tier 1 has the highest pooled correlation, but with only four treatment clusters and one study the correlations are not distinguishable with credible study-level uncertainty. The required tie-break therefore favors Tier 2's lower RMSE. Tier 2 is the recommended primary entry; Tier 1 and Tier 3 are secondary entries.

All methods overpredicted on average. Applying the prespecified simple 0.5 multiplier changes RMSE to 1.482 (Tier 1), 1.445 (Tier 2), and 1.478 (Tier 3), while leaving rank correlations unchanged. It also changes mean signed error to 0.356, −0.286, and −0.342 points. The locked rule is therefore to apply 0.5 to all base ATE/deviation forecasts before constructing condition means, with logical clipping only afterward. Control baselines themselves are not halved.

For Tier 1, an individual file cannot contain a fractional ATE. The locked matched-control block-mixture implementation (specified in `PROTOCOLS_AND_PROMPTS.md`) was therefore replayed on the frozen records. Its final-method diagnostics were pooled Pearson 0.218, within-outcome Pearson 0.386, Spearman 0.226, direction 0.688, RMSE 1.671, and signed error 0.361 pp. The simple scalar diagnostic above (RMSE 1.482) is not reported as if it were an executable individual-level result. Final calibrated Tier 2 and Tier 3 RMSEs are 1.445 and 1.478 respectively; Tier 2 remains primary.

## Decisions supported—and not supported

- Use concise demographic-only, matched profiles for Tier 1 and full post-message sessions. The validation does not support elaborate biographies or condition-dependent latent traits.
- Use two independent sessions for Tier 2 historical testing, but three condition-level sessions for target calls so a true median is defined. The historical runner already forecast all four validation outcomes in each condition-level call, supporting the cheaper multi-outcome batching pattern.
- Use three independent Tier 3 condition-level sessions and the outcome-wise median. No comparative rank pass is allowed because it was not externally tested within the validation budget.
- Disable cross-method ensembling. A single held-out study cannot both learn and independently test weights, and equal-weight blending was not preregistered.
- Apply the simple 0.5 scale calibration to all non-control effects; preserve the base forecast ordering.
- Select Tier 2 as the sole primary by the stated uncertainty/tie-break rule.

## Cost and audit

Twenty-three successful calls used 371,682 input tokens (15,104 cached), 14,540 output tokens, and 409.4 call-seconds. At published `gpt-5.6-sol` rates ($4/M uncached input, $0.40/M cached input, $20/M output), API-equivalent cost was **$1.7232**, below the $2 gate. All successful calls recorded zero tool-use events. Machine-readable results are `validation/validation_metrics.csv`, predictions are `validation/validation_predictions.csv`, usage is `validation/validation_usage.json`, and raw JSONL plus stderr logs are retained under `validation/raw/`.

## Limitations

This is a small, single-study, four-treatment evaluation; it estimates workflow feasibility more reliably than future benchmark rank. Pretraining memorization cannot be excluded. Tier 1 has only 50 simulated participants per validation cell, so it includes appreciable Monte Carlo error. Only four attitude/intention outcomes were available in the fixed slice; trust, donation, and newsletter calibration rest on the external literature rather than held-out cells. These limits are why no optimized coefficient, rank reconciliation, or ensemble is authorized.
