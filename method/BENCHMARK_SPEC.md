# Silicon Sample Benchmark specification

Status: reconstructed from the official benchmark site and submission repository at the pinned commits below. No target human outcomes, pilot results, interim findings, or other teams' submissions were accessed.

## Authority and provenance

- Benchmark/scoring site: `janpfander/llm_predictions_megastudy`, commit `b25667b297c036e86c80a51a9594b10cd41644ac` (2026-08-15), vendored read-only in `official_benchmark_site/`.
- Submission template/validator: `janpfander/silicon-sample-submission`, commit `546f9284e56777ce1aa555fa358d8506f529a6a8` (2026-08-15), vendored read-only in `official_submission_template/`.
- Full survey representations inspected: `survey.qsf` (SHA-256 `a672c434312d27cf803f1bc006c468dbd9eedd6a585c42fe7ae92b47f98424e1`), `survey.json` (`2144815888a8413c191b5f69efe1f36a21929b77e4de4f37a7161068cc68b6c0`), and `questionnaire.txt` (`b9f5ab1ce8566fca5684aa66b6ed25eb6918ccdee0ba6d800296105a3e3e`).
- If this document differs from a later official release, the later official material controls and the discrepancy must be logged before the design is locked.

## Conditions

The canonical factor levels, including capitalization, are:

1. `control`
2. `Corporate reliance`
3. `Social justice`
4. `Interview Prof. Maraun`
5. `Funding`
6. `Oil industry misinformation`
7. `Measurement & modeling (1)`
8. `Former skeptics`
9. `High public trust`
10. `Measurement & modeling (2)`
11. `Peer-review`
12. `Scientist community helpers`
13. `Consensus`
14. `Portrait Prof. Cherry`
15. `Model accuracy`
16. `Interview Prof. Sebille`
17. `Extreme weather predictions`

Control participants are randomly assigned one of three content-neutral filler texts: neckties, baseball, or dances. The internal survey labels are `control neckties`, `control baseball`, and `control dances`; all are submitted as the single canonical condition `control`. The intervention comparison is therefore against this shared mixture, not a no-message control.

### State-dependent extreme-weather branch

The extreme-weather condition asks state first and shows exactly one state-tailored introduction:

- Flooding: Alabama, Arkansas, Delaware, Florida, Georgia, Illinois, Indiana, Iowa, Kansas, Kentucky, Louisiana, Maryland, Mississippi, Missouri, Nebraska, North Carolina, North Dakota, Ohio, Oklahoma, Pennsylvania, South Carolina, South Dakota, Tennessee, Texas, Virginia, West Virginia, or District of Columbia.
- Wildfires: Alaska, Arizona, California, Colorado, Idaho, Montana, Nevada, New Mexico, Oregon, Utah, Washington, Wyoming, or Hawaii.
- Extreme cold/snow: Connecticut, Maine, Massachusetts, Michigan, Minnesota, New Hampshire, New Jersey, New York, Rhode Island, Vermont, or Wisconsin.
- Prefer-not-to-say branch: the survey's generic fourth case.

No participant may receive more than one branch. Synthetic profiles must use a state consistent with their branch.

## Scored outcomes and scales

| Canonical outcome | Construction | Submitted scale |
|---|---|---:|
| `trust_multidimensional` | Mean of the four three-item trust subscales; equivalently the mean of all 12 trust items | integer/component inputs 0–100; composite 0–100 |
| `trust_post` | Single post-treatment trust item | integer 0–100 |
| `distrust_post` | Single post-treatment distrust item | integer 0–100 |
| `funding_perceptions` | `100 - funding_5` | 0–100 |
| `policy_role_mean` | Mean of four policy-role items | 0–100 |
| `inst_trust_mean` | Mean trust in EPA, NASA, NOAA, universities, and federal government | 0–100 |
| `belief_post` | Climate-change belief item | integer 0–100 |
| `concern_mean` | Mean of three concern items | 0–100 |
| `policy_general` | General climate-policy support item | integer 0–100 |
| `policy_specific_mean` | Mean of seven specific-policy items | 0–100 |
| `behavior_mean` | Mean of six behavioral-intention items | 0–100 |
| `donation_ams` | Whole-dollar allocation to the American Meteorological Society | integer 0–10 dollars |
| `newsletter_signup` | Yes = 1, No = 0 | binary for Tier 1; probability 0–1 for Tier 2 |

The 12 trust components are `trust_competence_1`–`trust_competence_3`, `trust_integrity_1`–`trust_integrity_3`, `trust_benevolence_1`–`trust_benevolence_3`, and `trust_openness_1`–`trust_openness_3`. Each is an integer slider from 0 to 100. The four subscales are the within-dimension means of three items. `trust_multidimensional` is the mean of the four subscale means. Tier 1 composites are used as submitted, so the submitted composite must be numerically consistent with these 12 inputs.

Other formulas are: `funding_perceptions = 100 - funding_5`; `policy_role_mean` is the mean of four items; `inst_trust_mean` is the mean of five named institutions; `concern_mean` is the mean of three items; `policy_specific_mean` is the mean of seven items; and `behavior_mean` is the mean of six items. The exact wordings and anchors are preserved in `official_submission_template/survey/questionnaire.txt` and mapped in its `codebook.csv`.

The newsletter outcome depends on the immediately preceding offer page: respondents are offered the free *Talking Climate* newsletter by Katharine Hayhoe and the link opens in a new tab. A synthetic survey must reproduce this context before eliciting signup.

### Survey order and optional content

The source survey proceeds through consent/bot screening, demographics, unscored pretreatment measures, one randomized condition, the 12 trust items, then randomized secondary and tertiary post-treatment blocks. Scored items are the 13 outcomes above plus the 12 trust components needed for the Tier 1 composite. Unscored/optional content includes consent and filter variables, climate education, household and social-class measures, rurality/ZIP code, attention checks, partisan importance, religion/religiosity, epistemic autonomy, alienation, pretreatment belief/trust, stimulus manipulation checks, and comments. Such items may be omitted only under the frozen protocol; they are never forecast targets.

## Moderators and levels

There are six moderators and exactly 27 levels:

- `gender`: `Male`, `Female`, `Other`
- `age_band`: `18-29`, `30-44`, `45-59`, `60+`
- `race`: `White / Caucasian`, `Black / African American`, `Hispanic / Latino`, `Asian / Asian American`, `Other`
- `education`: `Less than high school`, `High school diploma / GED`, `Some college or Associate's degree`, `Bachelor's degree`, `Master's degree / Professional degree`, `Doctorate degree / Ph.D.`
- `income`: `Less than $30,000`, `$30,000 to $55,999`, `$56,000 to $99,999`, `$100,000 to $167,999`, `$168,000 or more`
- `party`: `Republican`, `Democrat`, `Independent`, `Other`

Age is derived as `2026 - year_birth` before categorization.

## Target population and quotas

The human target is U.S. adults aged 18 or older in a nonprobability opt-in sample who pass the prespecified checks. The planned human sample is approximately 18,000: 1,000 per intervention and 2,000 shared control participants. Census-matched quotas are enforced jointly for gender × age and gender × race; `Other` gender is not quota constrained.

Age quotas (total; male; female) are: 18–29: 3,629; 1,848; 1,781. 30–44: 4,688; 2,365; 2,323. 45–59: 4,122; 2,048; 2,074. 60+: 5,561; 2,566; 2,995. Race quotas are: Asian: 1,201; 568; 633. Black: 2,212; 1,042; 1,170. Hispanic: 3,263; 1,646; 1,617. Other: 492; 240; 252. White non-Hispanic: 10,832; 5,332; 5,500.

## Canonical files and complete grids

Prediction filenames use the assigned, non-invented team ID:

- Tier 1: `<team_id>_T1_<primary|secondary-k>_v<n>.csv`
- Tier 2 population cells: `<team_id>_T2_<primary|secondary-k>_v<n>_cells_main.csv`
- Tier 2 moderator cells: `<team_id>_T2_<primary|secondary-k>_v<n>_cells_moderator.csv`
- Tier 3: `<team_id>_T3_<primary|secondary-k>_v<n>.csv`

Tier 1 requires one row per synthetic respondent and the canonical profile, condition, six-moderator, outcome, and 12 trust-item columns. It requires at least 500 respondents in every intervention and 1,000 controls (at least 9,000 total). Tier 2 main requires `condition,outcome,mean`: 17 × 13 = 221 rows. Tier 2 moderator requires `condition,moderator,moderator_level,outcome,mean`: 17 × 27 × 13 = 5,967 rows. Tier 3 requires `condition,outcome,ate`: 16 × 13 = 208 rows and excludes control.

All grids must be complete, with no missing values, duplicate keys, extra factor labels, omitted cells, or non-finite numbers. Tier 1 and Tier 2 means must stay within the original outcome range. Tier 3 ATEs are in original outcome units; the validator does not impose an ATE range, but logical range checks remain part of this project.

## Scoring model

- The preregistered split uses seed 42. Human 1 is the scoring reference; Human 2 is the human-replication reference, not an assumed ceiling.
- ATEs are intervention means minus the shared control mean.
- The 11 continuous 0–100 outcomes and donation use unadjusted treatment models with HC2 uncertainty. Newsletter signup uses a logistic model and marginal effects on the probability scale.
- Scoring models do not adjust for demographic covariates. Moderator interactions use unadjusted interaction models (including a linear-probability specification for newsletter interactions).
- If the preregistered heterogeneous differential-attrition rule triggers, submissions are compared with inverse-probability-weighted human ATEs and moderator interactions in both human halves. Distribution and demographic analyses remain unweighted as specified.
- Cross-outcome effects are converted to percentage points of the outcome range: the eleven 0–100 outcomes are unchanged, donation effects are multiplied by 10, and newsletter probability effects are multiplied by 100.
- Exact-zero predictions earn half credit for directional agreement.
- ATE metrics are directional agreement, Spearman correlation, pooled Pearson correlation across 208 cells, Pearson correlation after mean-centering predictions and outcomes within outcome, RMSE, noise-corrected Pearson/RMSE, and calibration intercept/slope from human ATE on predicted ATE. The user's primary-selection metric is pooled Pearson; safeguards are RMSE, within-outcome Pearson, Spearman, direction, and calibration.
- Tier 1 additionally receives distributional (variance ratio, overlap, KS, Wasserstein), subgroup, demographic-baseline, parity-gap, and stereotyping analyses. Tier 2 additionally receives subgroup, demographic-baseline, and parity-gap analyses. Tier 3 receives ATE and calibration analyses.
- There is no official composite winner. Official displayed rankings use pooled Pearson with RMSE as the tie-breaker; this project follows the user's stricter prespecified primary-selection sequence on external validation.

## Validator and submission controls

From within a populated template, run `make check`; for Tier 1 also run `make clean`. Build supporting artifacts with `make manifest` and `make zenodo_citation` (or the documented equivalent R scripts). The environment requires R 4.2+ and the template's R dependencies, including tidyverse, jsonlite, and digest.

The validator checks parseable and complete `metadata.json`, completed `registration.md`, tier/entry/filename agreement, model and approach disclosures, attestation, canonical schemas, exact complete grids, types, legal factor levels, ranges, duplicates, and missing values. It warns on a Tier 1 sample below the benchmark floor, inconsistent trust composites, and unexpected repository contents. Deposit preparation additionally requires `.zenodo.json`, hashes/manifests, author metadata and ORCIDs where applicable.

One repository represents one entry, at most three entries per tier are accepted, and exactly one entry across all repositories must be designated `primary`. Tier 1 already receives the lower-tier ATE analyses, so it cannot be presented as a deterministic restacking. Tier 1/Tier 2 raw model logs and any Tier 3 intermediate generations must be retained. Registration, model/version, prompts, profiles, calls, tokens, costs, retry/exclusion behavior, data provenance, and SHA-256 fingerprints must be disclosed.

Nothing will be published, deposited, emailed, or submitted without explicit user approval. Team ID, author names, contact information, and ORCIDs remain unresolved and will not be invented.
