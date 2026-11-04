# Meta integration: synthetic counted stock → confirmed planner inputs

**Integration code included; live verification blocked.** No response in this checkout is claimed as actual Meta output. Tests mock the provider and explicitly label their response IDs `MOCK-TEST-NOT-LIVE`.

## The narrow existing-workflow feature

Meta converts a synthetic natural-language counted-stock note into dough/cheese/sauce quantities, units and exact source quotes. The UI shows source, candidate, request/model identifiers and usage, then requires human correction/confirmation. Confirmed grams initialize the existing Prep Planner. The deterministic planner owns the quantities, fixed recipes and constraints; the model never modifies recipes or authorizes a purchase.

This uses a counted-stock note deliberately: a supplier invoice describes a purchase and is not automatically current inventory. The older image adapter still exists but is unverified and is not part of this narrow demonstration. PDF and image extraction, tool-calling explanations and additional features are not implemented here.

Only the fixed synthetic note and extraction instructions/schema can be sent. No free-text private upload is offered. Session state retains before/after values, source hash and request ID; it is not a durable operational audit database. Model output is never silently replaced by a fake fixture. Null/invalid fields, invented quotes, refusal, truncation and failed requests cannot confirm stock.

## Exact service and blocked setup

- Service: Meta Model API, `POST https://api.meta.ai/v1/chat/completions`.
- Model: `muse-spark-1.3`, **Standard** variant (fixed for this lane; no Contributor fallback).
- Private runtime settings: `MODEL_API_KEY` and `META_LIVE_ENABLED=true`. Configure them locally in the process launching Streamlit; `.env` is not auto-loaded. Never paste a key in chat, source files or GitHub. Do not create/rotate credentials or accept account terms through this task without the required separate approval.
- At this check, `MODEL_API_KEY` was absent and live enablement false in the agent process. Only presence booleans were checked; ignored secrets were not read. Account sign-in was subsequently verified. Latest dashboard check showed zero keys/requests and no payment method. User reports submitting the credit form; credited balance remains unverified. No personal account identifiers are included here.
- UI consent authorizes one request for the displayed synthetic note. No call has been authorized/executed by the assistant. The user still needs to confirm account access and authorize one synthetic test's API usage after local credentials are ready. The UI is disabled until configured and opted in.
- Request bound: 1,024 completion tokens including reasoning, 10-second connect / 45-second read timeout, no automatic retries or redirects, `store=false`. A timeout can still consume tokens; reset/retry is a separate deliberate action. Session restart can reset the attempted-request guard, so this is not an account-wide spending cap.

Official rates checked November 4: Standard input $1.25/million tokens, output $4.25/million. For example, exactly 1,000 input plus 1,024 output tokens would cost $0.005602 at those rates. That is arithmetic illustration, not a measured quote, credit guarantee or hard dollar cap. Verify the actual account's budget/credits before enabling requests. No inference spend occurred here.

Official references: [models](https://dev.meta.ai/docs/models), [structured output](https://dev.meta.ai/docs/structured-output), [request/response schema](https://dev.meta.ai/docs/api-reference/chat-completions/schemas), [pricing](https://dev.meta.ai/docs/pricing-rate-limits). Standard mode does not use content to train models according to these docs; this is not a zero-retention promise.

Self-hosted Muse options exist in the official model catalog, but no `ollama`, `llama-server` or `muse` executable was found on PATH in the checked environment. No runtime/weights were installed and hardware suitability was not established. Hosted API is the prepared route, not an assertion that local inference is impossible.

## Account and credit handoff

The hackathon claim form states $150 credits per accepted participant, added within two business days after a successful claim. Submission alone does not establish an available balance. The service requires a payment method before the first request; API usage before credits arrive may be billed. Billing spend-limit email alerts are not a verified hard cap. Teammates can use their own authorized account for the demo; a Team ID identifies the account/team but is not the secret needed by the app.

Use the official dashboard's API keys page to create a named key yourself after reviewing access and costs. Configure `MODEL_API_KEY` only in your private launch environment and enable `META_LIVE_ENABLED=true` deliberately. Never send the key through chat, commit it, or include it in demo recordings. Browser login does not configure the local app.

## One live validation after access and spend approval

1. Launch the app with the private runtime settings, then choose Meta Evidence. Review the exact synthetic note and account rates/limits.
2. Opt into one request and click **Extract synthetic counted stock with Meta** once. Inspect actual request ID, usage and each source quote. Expected interpretation is 10,000 g dough / 2,000 g cheese / 3,000 g sauce, but the app must validate the actual output rather than assume it.
3. Correct ambiguous quantities if necessary and explicitly confirm. Open Prep Planner and review its form. Confirm/calculate: 29 expected, 20 feasible, nine unmet, 900 g cheese shortage.
4. Changing the planner's stock afterward is a manual what-if scenario. Never represent that edit as Meta output. Record only after the real call and confirmation have actually succeeded.

No live result, credentials or paid request occurred during implementation. This code is included in the authorized private upload; public release and deployment have not occurred. Until step 2 succeeds, the feature is **offline-tested integration code**, not a demonstrated Meta-powered application.
