---
name: pr-test-review
description: "Review behavioral test coverage and assertion quality for a change, prioritizing concrete regressions rather than arbitrary coverage quotas."
---

# Behavioral test review

Map changed public outcomes, state/effects, failures and boundaries to existing unit and integration tests. Read actual test assertions and fixtures. A file named test or a coverage percentage alone does not demonstrate protection. Include relevant error, negative, edge and async/concurrent lifecycle paths; avoid demanding trivial getter tests without behavior.

Identify specific important missing or weak cases: wrong-value truthiness, broad exception catches, mocks of the operation under test, stage-name/source-shape checks, unbounded waits, skipped/discovery-zero suites or brittle implementation coupling. Explain which real regression each recommended case would detect and check whether an existing integration test already covers it.

Prefer descriptive intent and refactor-resilient public contracts over private call ordering unless that order itself is required. If execution is authorized, run the real suite and meaningful mutants/equivalent implementations; report import/timeouts separately from behavior-sensitive failures. Never disable a test to make the review green.

Give scope/summary, prioritized gaps, test-quality issues and positives. Optional1–10 criticality ratings need concrete impact justification; they are not proofs. Costs and risk determine value, not academic100% coverage. Missing runner/browser/provider/CI evidence remains unperformed.
