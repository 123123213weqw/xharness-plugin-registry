---
name: behavior-test-generation
description: "Generate executable tests from real Python/JS behavior, dependency interactions and failure contracts; diagnose coverage gaps and verify regression sensitivity."
---

# Behavior-first test generation

Inspect the source, callers, current tests, manifests and local project rules before choosing a framework. Enumerate public results, state/effects, failure types, boundaries and async ownership obligations. A function name or AST node is a routing clue, not a specification. Unknown behavior needs clarification or a characterization test, not an invented assertion.

Read [the suite and evidence guide](references/suite-evidence.md) when generating a suite, choosing doubles, reporting coverage or interpreting a failure. Preserve existing production code unless the caller separately requests implementation changes. Match the project's installed runner; no network installation or framework substitution may be reported as execution of the original framework.

Write independent Arrange/Act/Assert cases with exact expected results or typed failures. Select meaningful empty/single/multiple/boundary/invalid/effect/error cases from the contract; do not force every input to throw. Python bool is an int subclass: decide from the API specification whether it is accepted, ignored or rejected, then test that behavior. Use deterministic seeds and bound every wait/retry/resource lifetime. Include one-shot iterators and repeated use only when the API promises them.

Double only the external boundary. Let actual business logic execute; spies verify exact arguments/count/order and intentional side effects. Configure failures to exercise propagation/cleanup. Do not mock the operation being asserted, or treat a fixture's successful fake network response as a live integration. Patch the symbol where the code looks it up; restore patches and state after each test. Preserve traceback/cause and primary-versus-cleanup failures.

Run the declared suite with an actual registered test runner. Zero tests, import errors, truncated output and an early exit are not green. Verify assertion quality using focused behavioral mutations or a deliberately failing behavior test, and retain the original tests unchanged when changing implementation. Also test an equivalent implementation/refactor so source-shape assertions are exposed. A mutant killed by timeout/import error rather than its changed behavior needs investigation, not automatic credit.

Deliver source-bound test files, scenario rationale, exact runner/environment, observed outcome and limitations. Report measured line/branch coverage only from a real compatible tool's output; behavioral/mutation coverage is a different metric. Identify untested risks and non-run frameworks explicitly. Propose CI commands/configuration only for the repository's actual runner; a YAML file is not a pipeline receipt.
