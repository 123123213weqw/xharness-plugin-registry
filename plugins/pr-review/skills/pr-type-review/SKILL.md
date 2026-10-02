---
name: pr-type-review
description: "Evaluate a changed type’s construction, mutation and exposed-state invariants with pragmatic enforcement and explained design tradeoffs."
---

# Type invariant review

Identify business/state/field relationships and pre/postconditions the type intends to encode. Inspect construction, mutation methods, serialization/deserialization, aliasing/exposed collections and callers. Find concrete ways an invalid state can enter or escape; documentation alone may not enforce it, but not every simple data carrier needs a domain framework.

Evaluate encapsulation, invariant expression, usefulness and enforcement. Consider compile-time guarantees where the actual language/compiler supports them, constructor/mutation validation otherwise, and immutability only when it fits the API. Runtime validation and static typing protect different boundaries. Do not claim a compile proof without an actual compatible compiler run.

When requested, explain optional1–10 ratings per axis with strengths/concerns and located examples. Recommend the smallest helpful redesign/test that prevents a real illegal state while accounting for complexity, migration, performance and project conventions. An anemic type, mutable field or exposed method is a risk pattern, not proof of a defect absent its contract.

Return identified invariants and evidence-bound improvements; review-only scope does not authorize editing or migrations. Missing TypeScript/Java/Rust compilation remains pending, with Rust build/check/test remote only under the repository policy.
