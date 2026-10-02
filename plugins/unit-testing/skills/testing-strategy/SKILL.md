---
name: testing-strategy
description: "Design a risk-based test and maintenance strategy across unit, contract, UI and performance layers, with measured runner/CI evidence and explicit unavailable integrations."
---

# Testing strategy and quality evidence

Start from critical user behavior, failure impact, component boundaries, current suite cost/flakiness and deployment constraints. Choose the smallest useful layers rather than a mandatory percentage or framework catalog. A getter with no logic may need no new test; a payment/auth/state transition usually needs precise positive, negative and recovery cases. Separate characterization, regression, TDD, integration, performance and exploratory objectives.

Read [the strategy guide](references/strategy.md) for TDD chronology, framework and CI/data/analytics decisions. Use installed project tools and current configuration; list missing accounts/runtimes/devices/connectors. AI/self-healing/visual/low-code tools are possible integrations, not capabilities established by writing a prompt or wrapper.

For TDD, preserve the same meaningful test through red, minimal green and refactor; verify red fails for the intended behavior, not a missing import or stage-name test. For behavior/property/mutation work, choose a finite meaningful domain and describe its limits. Broader fuzzing, statistical A/B and chaos claims need their own protocol, budget and real execution evidence.

Design reliable test data and lifecycle ownership: synthetic/private fixtures, deterministic clocks/seeds, explicit DB transaction cleanup and isolated dependency doubles. Never put credentials or production personal data in artifacts. Define suite commands, selection/parallelization constraints, result aggregation and maintenance owners. Container, CI, canary and cross-platform execution require available authorized systems and actual receipts.

Report counts, failures/skips, runtime, coverage and trend/TDD metrics only when measured and comparable. Keep forecasts/ROI/quality targets labeled assumptions. A local suite is not browser/mobile/cloud/load/live E2E, and authored controls are not evidence that a model or native resource loader used this skill.
