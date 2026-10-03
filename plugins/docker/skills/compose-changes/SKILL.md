---
name: compose-changes
description: "Make explicitly scoped Compose changes and validate readiness and preserved data after authorized execution."
---

# Compose Changes

Read [the change guide](../compose-inspection/references/workflow.md). Match requested changes to the exact project, services, mounts, ports and environment-variable names. Preserve unrelated edits and volumes. Prepare a diff and validate with `config --quiet`; build/up/down/restart/prune/volume deletion are not read-only inspection and must match current user authorization and Host approval. After execution verify state and application readiness separately. A container running without a healthcheck is not necessarily ready. Failed/unknown outcomes require state inspection before replaying mutations. Acknowledge absent daemon/account/tooling instead of fabricating success.
