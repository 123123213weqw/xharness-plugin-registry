# Suite and evidence decisions

## Specification and cases
Map each changed/public invariant to a meaningful assertion. Cover normal outputs, boundary values, empty/error behavior, one-shot input consumption and effects when promised. Verify exact exception class/cause and distinguish invalid input from a dependency failure. Broad catch or non-None assertions do not demonstrate these contracts.

## Framework and doubles
Use pytest/unittest, Jest/Node tests, React Testing Library or the project's actual runner based on installed tooling and task scope. Do not guess a DOM role or mock every result. React cases exercise actual accessible rendering, interaction/state and rerendered props; JS/TS module/async/error tests execute code, not predicted JSON. Framework unavailability is a blocker for that framework, not permission to claim its tests ran in another runner.

Use a spy/fake only for an external payment/clock/storage boundary. Validate exact request/count/order, propagate configured failures and isolate mutable fixtures. Use real logic for calculations/state transitions; distinguish a unit double from sandbox/live external E2E. For async code bound waits, retain owned tasks and join cleanup; no sleep-only evidence of cancellation.

## Validate the validator
Run real registered tests; retain runner outputs with source/test/runtime hashes. Exercise meaningful API mutants and a semantically equivalent implementation. A suite that accepts an incorrect value/error/effect is weak even if line coverage is high; a suite that rejects a harmless refactor may be overfit. Zero tests, fake stdout counts, early exits, imports/timeout and rewritten frozen source never become semantic pass evidence.

## Reports
Measured line/branch percentages require genuine coverage tool output mapped to source. Finite mutation kills are a separate measure and do not prove all regressions. Mark missing frameworks, devices, credentials, security/performance tests and CI receipts. Documentation should identify scenarios, intended failures, exact run command and non-run risks rather than fabricate a dashboard or universal coverage quota.
