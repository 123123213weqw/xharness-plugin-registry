---
name: compose-inspection
description: "Inspect Compose configuration and summarize actual container state without starting services."
---

# Compose Inspection

Identify the current Docker context and exact Compose project/configuration before running commands. Check `docker version` and `docker compose version` without installing or starting a daemon. `docker compose -f FILE config --quiet` validates configuration without dumping interpolated secrets. Capture `docker compose -f FILE ps --all --format json` with its real exit code, then use [the state helper](scripts/compose_state.py) on the saved JSON/JSONL. Read [the workflow guide](references/workflow.md). The helper parses observations only: empty output, missing healthcheck and unknown states are not proof the service is healthy.
