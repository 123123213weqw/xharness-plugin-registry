---
name: pr-error-review
description: "Trace catch, fallback and retry paths for hidden operational failures while recognizing intentional optional behavior and actual project logging standards."
---

# Error-path review

Inspect relevant try/catch, Result/rejection/callback, default/optional-chain, fallback/retry and log-and-continue paths. Trace concrete expected and unexpected error types through propagation, user-visible result and cleanup. Broad handling is suspicious when it erases distinct operational failures, not automatically a vulnerability merely because it exists.

Compare behavior to the actual specification: an intentionally optional lookup may legitimately return None; a failed required write presented as success may not. Verify retries are bounded and exhaustion is surfaced. Check whether fallback is explicit/justified and whether fake production data masks failure. Preserve original/cause and secondary-cleanup diagnostics.

Assess logging context/severity and actionable feedback without leaking secrets or internals to inappropriate users. Use actual project logger/error identifiers only; source examples logForDebugging/logError/Sentry/Statsig/constants are not assumed installed. Do not infer deployed HTTP status/exposure from a fragment.

For a supported issue, provide location, consequence/severity, specific hidden failure types, evidence, remedy and a corrected example or validation plan. Review-only scope forbids edits. A real test of the failing path improves evidence; substring matches or a model confidence score do not certify the whole narrative. Mark unavailable integrations/checks explicitly and never bypass tests as a repair.
