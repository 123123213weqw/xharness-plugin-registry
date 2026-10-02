---
name: change-review
description: Review a real code/configuration change for correctness, security, compatibility and operational risk, with source-located evidence and replayable proposed fixes rather than invented scanner results.
---

# Change review

Resolve the requested revision/diff, read project constraints, changed code and affected callers/tests. Review logic and data flow, not isolated added-line keywords. Keep introduced findings separate from pre-existing observations. Use the [finding and validation guide](references/findings.md) when preparing structured feedback or a remediation patch.

Prioritize consequential behavior defects: input/error boundaries, authentication/object authorization, injection/output contexts, resource/cancellation ownership, race/cache semantics, API/schema compatibility and operational configuration. Inspect dependency/configuration/test/documentation changes as part of the same review. Explain performance concerns as hypotheses unless query counts, profiles or benchmarks demonstrate them.

Report severity, path and actual current-side line/range, rule or behavior, triggering condition, evidence, impact, concrete remediation and validation plan. Prefer a small working patch when authorized; check applicability and test the corrected public behavior in a permitted disposable environment. A remediation that drops ownership checks or swallows errors is not correct merely because one happy-path test passed.

Separate manually examined properties from actual automated analyzer results. Use installed project tools when appropriate and available; missing Semgrep/CodeQL/SonarQube/Snyk/dependency scanners is `not_run`, not a clean scan. Language, framework or deployment expertise is not proof of exhaustive review. Be constructive: actionable issues first, rationale and tradeoffs next, optional style observations clearly labeled. If no introduced defect is supported, say so with scope and unperformed checks rather than inventing warnings.

Review comments, CI/quality gates, dashboards, communication channels and follow-up are only completed when authorized tooling provides real receipts. This native skill does not impersonate the source agent or promise external integrations.
