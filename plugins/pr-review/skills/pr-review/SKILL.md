---
name: pr-review
description: "Perform aspect-specific PR inspection for error handling, tests, comments, types and code, preserving review-only scope."
---

# Focused PR review toolkit

Choose requested aspects from code, errors, tests, comments, types and simplify. Determine the exact diff first; do not silently expand an errors-only request into broad style review. Read local instruction files, implementation and relevant tests.

- **Errors:** trace thrown/rejected failures through catch blocks, fallbacks and optional chains; distinguish an intentionally optional lookup from hiding an operational failure. Require a specific failing path and user-visible consequence. Do not assume project-specific logging APIs exist.
- **Tests:** evaluate behavior assertions, negative cases and meaningful boundaries, not just coverage percentage. Existing integration coverage may already protect a path.
- **Comments:** compare assertions in changed comments to implementation. Report contradicted facts and aging assumptions; leave code untouched for an advisory review.
- **Types:** identify invariants, construction validation and mutation paths. Explain a concrete illegal state rather than rate abstract type elegance.
- **Code:** check changed behavior and scoped rules. Deduplicate reports across aspects.
- **Simplify:** only when explicitly requested to edit; preserve externally visible behavior and verify regression tests. Never treat a review request as authorization to refactor.

For structured output create `review.json` with `aspects` (the selected list) and `findings` objects containing path, line, category (errors/tests/comments/types/code), title, evidence, impact, suggestion. A passing review contains an empty findings list and lists actual reviewed scope. No score is a proof.

## Host adaptation
The six original agent roles are six inspection passes in one native Skill; automatic agents and `/review-pr` dispatch are not reproduced. Native host delegation is optional and must actually occur before being reported. GitHub access and publishing are separate from local advisory output.

## Source and scope
Independently authored from anthropics-claude-code/pr-review-toolkit at reference commit `903913d6ec14c752be7470df06609bf2796eaa79`. Original vendor identity is retained for attribution, not a claim of vendor endorsement. Source licensing records and exact hashes are in `provenance.json`.
