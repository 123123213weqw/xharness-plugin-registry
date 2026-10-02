---
name: legacy-migration
description: "Plan and implement incremental legacy modernization with characterization tests, compatibility seams, explicit deprecation and reversible phases."
---

# Legacy modernization

Identify the exact legacy language/framework/database/dependency boundary and target supported environment. Read callers, persisted formats, deployment constraints and known consumers. Characterize existing behavior including failures, effects and edge cases before changing it. A version-name swap or compatibility shim alone is not a migration.

Define phases with acceptance tests, owners, dependencies and rollback. Start with a narrow adapter/facade or strangler seam; keep old and new paths observable and compare their contracts. Preserve public imports/signatures/protocols/storage semantics where promised. If behavior must break, get that change approved and document versioned migration, deprecation warnings/timeline and consumer updates.

Run actual regression/compatibility tests on each supported runtime and validate data conversion separately from source refactoring. Feature flags, database rewrites, traffic shifts and deployments require explicit tools/authorization. Dependency upgrades need actual compatibility/security/license evidence; no network install or broad framework migration is implied by a local plan.

Deliver changed code, legacy behavior tests, adapters, measured phase outcomes and recovery instructions. Missing Java/TypeScript/browser/database runtimes or connectors remain blocked/pending. Never call a mock or authored fixture a completed production modernization.
