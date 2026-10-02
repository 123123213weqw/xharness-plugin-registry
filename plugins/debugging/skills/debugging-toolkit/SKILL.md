---
name: debugging-toolkit
description: "Produce evidence-bound debugging toolkit artifacts for the requested workflow; distinguish offline checks from runtime integration."
---

# Debugging Toolkit

Reproduce the smallest failing operation and record expected versus observed behavior. Rank hypotheses by explanatory power and the cheapest discriminating test. Trace request IDs and state transitions; do not confuse repeated retries with independent failures. After a fix run the original reproduction and neighboring edge cases. Local trace aggregation is evidence about the supplied log only, not an executed debugger session or verified root cause in production.

## Verification boundary

Use the explicit output schema requested by the caller. Do not label an offline artifact as a live integration result. Record unperformed runtime checks and unsupported integration surfaces.
