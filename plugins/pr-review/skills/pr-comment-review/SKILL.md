---
name: pr-comment-review
description: "Check changed comments and docstrings against code behavior, boundaries and current references, providing advisory fixes without editing."
---

# Comment accuracy and longevity

Resolve changed comment/docstring scope and read implementation/callers/examples. Cross-check signatures/types/names, return/error/side-effect behavior, preconditions, edge cases and complexity claims. A stale link/TODO or optimistic comment is a finding only when actual code/context contradicts or no longer supports it.

Distinguish factually misleading comments from incomplete rationale and optional cleanup. Favor durable why/assumptions/business constraints over restating obvious operations, but keep information a future unfamiliar maintainer needs. Examine temporary migration claims, outdated symbols and examples against current behavior; do not invent undocumented requirements.

Provide advisory scope/summary, located factual issues, useful additions, suggested removals with rationale and good examples. Suggest exact corrected wording where evidence supports it, without changing code/comments under a review-only request. Unmeasured performance or broad architectural claims remain uncertain; a lexical contradiction detector alone is not complete narrative review.
