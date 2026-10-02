---
name: pr-code-review
description: "Inspect a scoped change for genuine bugs and applicable project-guideline violations with source-located, confidence-filtered actionable findings."
---

# Scoped code review

Resolve explicit review scope; if unspecified and the caller asks for local recent work, inspect actual unstaged changes and disclose that choice. Read the nearest applicable project instructions and affected callers/tests, not a fictional global CLAUDE.md rule. Import/style/framework/return-type conventions are requirements only when the project states them.

Trace changed behavior for logic/null/error/concurrency/resource/security/performance problems. Report an introduced consequential defect or explicit rule violation with current-side location, triggering state/input, evidence, impact and concrete repair. Keep pre-existing concerns and minor preferences separate; do not make up findings to meet a count.

When using the source workflow's confidence convention, retain only well-supported>=80 judgments and explain why; group critical vs important as requested. A score is not validation, and stylistic certainty does not establish severity. Validate a proposed fix with actual tests only when authorized; no fabricated scan/provider result.

Start with reviewed scope, then concise prioritized findings and unperformed checks. With no high-confidence issue, say what was inspected and why no supported defect was found, without asserting universal correctness or a passed remote PR review.
