# Call, token, runtime, and cost estimate — compact design

## Actual billing interface

`codex login status` reports **“Logged in using ChatGPT.”** The target plan therefore uses the Codex allowance included with the user's ChatGPT plan, not an API key or separately billed API endpoint. Official OpenAI documentation says Codex is included across ChatGPT plans, usage draws from a shared agentic allowance/credit pool, and displayed dollar conversions are planning estimates rather than invoices.

**Expected incremental cash cost: $0**, provided the run stays within the included allowance. The execution rule is: never buy credits, authorize flexible billing, switch to an API key, or continue after an allowance-exhaustion/credit prompt without fresh user approval. Usage-pool consumption cannot be converted reliably to dollars from the CLI and will be reported as calls/tokens/runtime.

For comparability only, the table also reports a conservative API-equivalent planning value using published `gpt-5.6-sol` text-token rates of $4/M uncached input, $0.40/M cached input, and $20/M output. It is not the expected invoice.

| Work | Calls | Design | Input tokens | Output tokens | Runtime (4 concurrent) | Expected cash | API-equivalent planning value |
|---|---:|---|---:|---:|---:|---:|---:|
| Completed validation | 23 | historical only | 371,682 | 14,540 | 409 call-sec | $0 incremental | $1.723 observed equivalent |
| Tier 1 | 35 | 2×250 per intervention; 3 filler-control batches; compact arrays | 0.8–1.2M | 0.65–1.05M | 12–30 min | **$0** | $16–26 |
| Tier 2 | 51 | 3 sessions × 17 conditions; 13 outcome batches/session | 0.9–1.3M | 0.08–0.18M | 8–20 min | **$0** | $5–9 |
| Tier 3 | 48 | 3 sessions × 16 interventions; 13 outcomes/session | 0.8–1.2M | 0.04–0.10M | 7–18 min | **$0** | $4–7 |
| Target total | **134** | 91% fewer calls than prior lock | 2.5–3.7M | 0.77–1.33M | 27–68 min | **$0** | $25–42 |

The old design required 1,467 target calls and had a $136–201 API-equivalent estimate. It is superseded. The compact design reduces calls by 90.9%, keeps each treatment condition isolated, preserves three independent forecasts for every Tier 2/Tier 3 cell, and retains raw individual Tier 1 responses.

## Why output remains valid

- Tier 1 uses compact fixed-order integer arrays instead of repeating 40+ JSON field names 9,000 times. This changes serialization, not the participant method.
- Tier 2 validation already batched four outcomes within a condition-level call. Target calls extend this to 13 outcomes but never include another treatment condition. Each outcome remains a separately labeled condition×outcome batch with its own evidence and moderator cells.
- Tier 3 similarly batches 13 outcomes for one intervention. Every pair receives three independent sessions and an outcome-wise median.
- No forecasts are shared across methods, no treatment conditions are compared, and no target coverage is removed.

## Tier 1 sample size

Retain 9,000 respondents: 500 per intervention and 1,000 control. Larger samples chiefly reduce Monte Carlo error, not structural simulation bias, and would add output usage without sufficient held-out benefit.

## Cost guardrail

Before target generation, query the available Codex allowance if the client exposes it. Begin with one **historical**, compact target-schema serialization test—never a target condition—to confirm row capacity and token use. If the client indicates that included allowance is insufficient or that any incremental charge/credit consumption will occur, stop and ask. No dollar spend is authorized by this design.
