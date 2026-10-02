---
name: pr-evidence
description: Derive a pull-request description, checklist, risk and review plan from actual Git comparison and test evidence, including renames, binary files, split suggestions and unavailable coverage.
---

# Evidence-grounded pull requests

Identify the intended base and head before writing the PR. Read [comparison and reporting rules](references/reporting.md). The merge-base comparison is normally appropriate for a feature PR; use a caller-selected alternative only when explicit. A missing/ambiguous ref stops the comparison—never invent `main`, silently create a base or compare an unrelated worktree instead.

Collect commits and real Git name/status/numstat with NUL-delimited parsing. Preserve rename source/destination and paths containing spaces; binary numstat is unknown line counts, not zero textual changes. Keep staged/unstaged/untracked work out of a committed PR comparison unless explicitly requested. Examine the changes themselves and surrounding code; extensions alone do not establish risk or feature intent.

Write summary/why, categorized changes, compatibility/migrations, dependencies, tests/coverage, risk/mitigations, review checklist and applicable deployment/rollback or UI evidence. Bind factual metrics and test conclusions to the exact comparison and evidence source. Missing screenshots, benchmarks, scans and coverage remain pending or unavailable. An unchecked checklist is a review task, not proof the property holds.

Prefer cohesive PRs. For a large change, suggest logical file/commit groups with ordering and dependencies; do not automatically cherry-pick, create branches or publish split PRs. Add a diagram only when actual architecture relationships changed and can be supported by source/docs. Choose feature/bugfix/refactor emphasis from the change, not a one-size template or invented user story. Constructive response drafts should refer to a real reviewer question and documented tradeoffs; missing context calls for clarification.

This skill prepares local evidence and descriptions. Remote PR edits/comments, labels, links, CI and reviewer metadata require an available authorized provider. Offline output cannot claim a real PR URL or review status.
