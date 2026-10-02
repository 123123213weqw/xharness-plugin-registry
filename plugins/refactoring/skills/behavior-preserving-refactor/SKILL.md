---
name: behavior-preserving-refactor
description: "Refactor scoped code incrementally behind characterization tests, preserving APIs, errors and effects while measuring maintainability changes."
---

# Behavior-preserving refactoring

Fix the scope and public behavior contract from callers/tests/project rules before changing code. Capture outputs, typed errors, ordering, mutation/aliasing, IO/resource lifecycle and compatibility—not only the happy-path return value. Write characterization/regression cases where coverage is weak. Treat intentional behavior changes as separately approved migrations, not cleanup.

Read [the equivalence guide](references/equivalence.md) before reorganizing effects or module boundaries. Identify consequential duplication, complexity, coupling, dead code, naming and SOLID problems; prioritize impact/effort/risk. Source example line-count and coverage thresholds are diagnostic examples, not universal acceptance rules. Do not decompose a small function into a framework simply to satisfy a pattern name.

Apply one useful transformation at a time: extract a repeated invariant/helper, clarify branching/names/constants, separate calculation from effects, introduce a narrow strategy/value object/dependency seam where callers benefit. Preserve side-effect count/order, exception/cause, lazy iterator consumption and monetary/encoding precision. Keep helpful abstractions/comments; fewer lines and dense ternaries are not evidence of clarity.

Run unchanged behavioral tests before and after. Add concrete boundary/error/cleanup cases for the changed seam; verify an independent caller still works. Compare performance, complexity, coverage and dependency metrics only when actually measured by compatible tools. Review security/config/API/migration implications; missing Ruff/mypy/ESLint/Semgrep/CodeQL/Sonar/AI-vendor checks remain not run.

Deliver a located analysis and prioritized plan, complete patch/tests, actual equivalence evidence and limitations. Explain significant design changes and any approved migration/adapter/deprecation/rollback steps. Never invent dashboard URLs or declare no vulnerabilities from a small local suite.
