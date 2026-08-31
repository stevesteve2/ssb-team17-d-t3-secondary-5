# Run configuration

Status: **pre-forecast research milestone; target generation prohibited until user approval**

- `EXECUTION_AGENT`: Codex desktop/CLI agent, `codex-cli 0.151.0-alpha.7.1`
- `FORECAST_MODEL`: `gpt-5.6-sol` (same model planned for all three base methods)
- `MODEL_PROVIDER`: OpenAI
- `MODEL_INTERFACE`: ChatGPT-authenticated Codex CLI non-interactive `codex exec --json`, with `--output-schema` for auditable structured responses; no API key or separately billed API endpoint
- `MODEL_IDENTIFIER_SOURCE`: `/Users/dan/.codex/config.toml` contains `model = "gpt-5.6-sol"`; no model substitution is authorized
- `MODEL_VERSION`: rolling alias `gpt-5.6-sol`; no dated snapshot was exposed by the local configuration or official model page
- `CONFIG_RECORDED_UTC`: 2026-08-30T22:26:36Z
- `REASONING_EFFORT`: local default is `high`; effective forecast setting is locked to `low` via `-c model_reasoning_effort="low"` for every validation and target call
- `TEMPERATURE`: unavailable/not exposed by `codex exec`; will not be claimed or silently emulated
- `TOP_P`: unavailable/not exposed by `codex exec`; will not be claimed or silently emulated
- `SEED`: unsupported/not exposed by `codex exec`; independence will use separately logged invocations, never purported seeded reproducibility
- `OTHER_SAMPLING_SETTINGS`: no user-set sampling controls currently available through this interface
- `STRUCTURED_OUTPUT`: supported through `codex exec --output-schema <schema.json>`; every invocation will also use `--json` to retain JSONL event logs
- `AUTHENTICATION`: `codex login status` reports `Logged in using ChatGPT`; credentials and secrets are never recorded
- `RETRIES`: locked maximum 2 retries for transport, timeout, explicit rate-limit, refusal, schema/completeness, nonfinite, duplicate-ID, or arithmetic-consistency failure; never retry because a valid prediction looks surprising
- `TIMEOUT`: locked at 10 minutes per invocation
- `RATE_LIMITS`: account-specific limits are unknown; use bounded concurrency and exponential backoff only for explicit rate-limit errors
- `FORECAST_ACCESS_STATUS`: repeated non-interactive structured generation was verified in 23 blinded historical-validation calls. Their observed API-equivalent cost was $1.7232. No benchmark target call has been made.

## Official model facts used for estimation

Official OpenAI documentation accessed 2026-08-30 identifies `gpt-5.6-sol` as supporting structured outputs and reports promotional text-token prices of $4 per million input tokens, $0.40 per million cached input tokens, and $20 per million output tokens, with prompts above 272k input tokens billed at higher rates. Actual Codex subscription billing may differ; estimates therefore report conservative API-equivalent cost and actual observed cost separately when available.

Source: <https://developers.openai.com/api/docs/models/gpt-5.6-sol>

## Measured and projected workload

External validation used 23 successful calls, 371,682 input tokens, 14,540 output tokens, and 409.4 call-seconds. The compact locked target design projects 35 Tier 1 calls, 51 Tier 2 condition-level calls, and 48 Tier 3 condition-level calls: 134 total. Expected target runtime at four-way concurrency is 27--68 minutes. Because the CLI is authenticated through ChatGPT, expected incremental cash cost is $0 within the included allowance; the conservative API-equivalent planning value is $25--42 and is not an expected invoice. Detailed assumptions are in `COST_ESTIMATE.md`.

## Hard spending gates

- Ask before any exploratory or validation step expected to exceed **$2**.
- Ask before any tier expected to exceed **$25**.
- Ask before aggregate project spend is expected to exceed **$50**.
- No paid target-generation call is authorized by the current instruction.
- Never purchase or consume additional paid credits, switch to API-key billing, or continue past an allowance-exhaustion/credit prompt without fresh approval.
