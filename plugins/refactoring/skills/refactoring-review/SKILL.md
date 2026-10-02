---
name: refactoring-review
description: "Review a refactor for preserved behavior, security, configuration and caller compatibility, separating actual analyzer evidence from manual hypotheses."
---

# Review a refactoring change

Anchor the exact diff and relevant callers/tests/project rules. Identify which behavior is claimed unchanged and which migration is approved. Inspect return/error/effect semantics, resource/cancellation ownership, concurrency/cache/state boundaries, API/schema/config compatibility and docs. A prettier structure is not enough if ordering or precision changed.

Prioritize reproducible or source-proven introduced problems; distinguish pre-existing defects, risk hypotheses and optional style. Give current-side path/line, triggering input/state, actual evidence, consequence, actionable fix and validation. Verify a suggested patch against real behavior when execution is authorized.

Choose installed analyzers/profilers/security/dependency/license tools according to language and changed risk. Record argv/environment/revision/output/outcome; a configured workflow or keyword match is not a scan. Do not infer production exposure, legal compliance, canary/rollback success or team/IDE/webhook integration from source alone. Missing tool/runtime evidence is not clean.

Assess test strength, error handling, observability/rollback/configuration and maintainability using the project's needs, not universal line quotas. Deduplicate findings and teach the invariant/tradeoff. Return a scoped review/checklist and unperformed checks; future follow-up/notifications happen only through actual authorized systems.
