---
name: pr-code-simplify
description: "Simplify caller-authorized changed code while preserving public behavior, errors and side effects under actual project conventions."
---

# Scoped simplification

Confirm editing is authorized and identify recently modified code or explicit broader scope. Capture public features/results/failures/effects and regression anchors. Read applicable project instructions; source example ES-module/function/React/return-type conventions do not override this project's actual rules.

Prefer clear explicit branches, good names, useful helper seams and consolidated repeated invariants. Remove redundant nesting or abstraction only when understanding improves. Avoid nested ternaries/clever one-liners, mixing unrelated concerns, removing helpful architecture/comments or treating fewer lines as a quality metric.

Preserve behavior including ordering, aliasing, lazy consumption, precision, exception/cause and cleanup. Apply small transformations and run unchanged tests plus affected boundaries; inspect callers for import/signature/compatibility drift. If behavior changes, stop and expose it as a separate proposed change rather than hide it in polish.

Deliver a complete patch, actual test/equivalence evidence and significant rationale. No automatic source-agent persona/dispatch is installed; a review request alone never authorizes immediate autonomous edits. Missing test/compiler/provider evidence remains unperformed, not green.
