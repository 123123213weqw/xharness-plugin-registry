---
name: test-failure-diagnosis
description: "Reproduce a failing test, separate assertion/fixture defects from application defects and verify a minimal cause-specific repair."
---

# Test failure diagnosis

Capture the exact command, runner/runtime, failure class/message, stack trace and relevant test/source revision. Reproduce without changing assertions first. Identify whether the failure is a deterministic application defect, invalid expectation, setup/data leak, unavailable dependency, timing race or runner/discovery problem. Never label an unknown timeout environmental merely because the test did not finish.

Form hypotheses tied to observed state and a cheap discriminating experiment. Examine recent changes, lookup/patch scope, skipped or unregistered tests and before/after effects. Broad `assertRaises(Exception)` can pass for the wrong error; a mock can predetermine the expected answer. Confirm the test exercises the intended public API and detects a real changed result, effect or specific error.

Repair the narrow underlying cause. If a test is wrong, show the specification or observed stable behavior justifying its correction; if the implementation is wrong, preserve the regression test while changing code. Do not suppress errors, bypass failing tests, replace assertions with truthiness or turn a timeout into success. Bound synchronization and cleanup; cancel/join owned tasks without interrupting their existing finalizers.

Replay the original failure and neighboring valid/invalid cases. Check isolation in repeated/reordered runs where relevant, and test the hypothesis's falsification case. Keep actual command/exit/results distinct from predictions. Explain root cause, evidence, patch and regression/prevention steps; CI/cloud/production diagnosis is pending unless those systems were actually observed.
