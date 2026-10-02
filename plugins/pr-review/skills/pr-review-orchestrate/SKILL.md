---
name: pr-review-orchestrate
description: "Coordinate caller-selected local PR review aspects, de-duplicate located findings and keep advisory inspection separate from simplification or publishing."
---

# PR review orchestration

Resolve exact files/revisions/index/worktree scope and requested aspects: code, tests, errors, comments, types, simplify or all. Inspect applicable project instructions. Do not silently replace a committed comparison with unstaged diff, or expand an errors-only request into style review. No real PR exists until a provider actually reports one.

Route only applicable passes: [code](../pr-code-review/SKILL.md), [tests](../pr-test-review/SKILL.md), [errors](../pr-error-review/SKILL.md), [comments](../pr-comment-review/SKILL.md), [types](../pr-type-review/SKILL.md). Review-only requests leave files untouched. [Simplification](../pr-code-simplify/SKILL.md) is an editing workflow requiring the caller's scope/approval; it is not an automatic post-review mutation. Read the requested pass's body before carrying it out.

Default to clear sequential inspection. User-requested native parallel delegation is allowed only through available authorized native tools and real calls; preserve identical diff/scope/constraints for each pass. These six Skills are not installed Claude Task agents, separate vendor contexts or model personas. Sequential aspect labels do not claim independence.

Aggregate overlapping findings by violated invariant/root cause; retain aspect evidence, current file:line, impact and specific remedy. Distinguish critical/important/optional/positive observations and supported findings vs unresolved hypotheses. Re-review changed anchors after a fix; never reuse stale green evidence. An empty report means no supported issue within inspected scope, not exhaustive correctness.

Deliver review scope/aspects, located findings, actual checks/unperformed checks and prioritized next actions. PR metadata lookup/posting, commits/pushes/CI and external notifications need separate authorization and available providers; no guessed URLs, fabricated analyzer outcomes or automatic source command dispatch.
