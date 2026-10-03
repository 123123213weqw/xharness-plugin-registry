---
name: migration-review
description: "Review database migrations and execute only separately authorized, reversible fixture changes."
---

# Migration Review

Read [the migration guide](../database-inspection/references/workflow.md), the project migration framework and the target engine. Inspect forward/backward behavior, locks, null/default semantics, index creation, transaction support and existing data compatibility. Prepare a reproducible migration test on a disposable database with before/after assertions. Changing production data or schema requires the current user's explicit scope and existing Host approval. The bundled SQLite helper is intentionally read-only; do not claim it applied a migration. Report which rollback was actually executed and which is a proposal.
