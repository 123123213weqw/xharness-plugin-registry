---
name: code-refactoring
description: "Produce evidence-bound code refactoring artifacts for the requested workflow; distinguish offline checks from runtime integration."
---

# Code Refactoring

Refactor behind a captured behavior contract, not stylistic preference. Separate pure calculation from effects so tests can protect existing semantics. Identify duplicated invariants, brittle dependencies and complexity hotspots; prioritize impact and effort rather than line count. Change one boundary at a time and inspect callers. A passed isolated function test demonstrates that function only; it does not prove project-wide regression safety or successful modernization.

## Verification boundary

Use the explicit output schema requested by the caller. Do not label an offline artifact as a live integration result. Record unperformed runtime checks and unsupported integration surfaces.
