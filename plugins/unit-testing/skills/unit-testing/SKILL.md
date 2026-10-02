---
name: unit-testing
description: "Produce evidence-bound unit testing artifacts for the requested workflow; distinguish offline checks from runtime integration."
---

# Unit Testing

Generate tests from public behavior and the failure contract, not private implementation details. Include a normal path, boundary input and expected error without making mocks decide the outcome. Fixtures should isolate side effects and assertions should survive a reasonable refactor. Execute the tests and report the command; absent tooling is a limitation. The isolated transformation verifies one testable behavior, not every source language or a complete suite.

## Verification boundary

Use the explicit output schema requested by the caller. Do not label an offline artifact as a live integration result. Record unperformed runtime checks and unsupported integration surfaces.
