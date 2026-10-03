---
name: container-diagnosis
description: "Diagnose container exits, restart loops and health failures from bounded real state and logs."
---

# Container Diagnosis

Read [the diagnosis guide](../compose-inspection/references/workflow.md). Join service state, ExitCode, Health and bounded logs from the selected project and time window. Missing Docker, permission denied and unreachable daemon are environment failures, not application root causes. Preserve upstream command failure before parsing output; no `... | tail` false success. Capture logs with a finite `--tail`, no continuous follow by default, and avoid printing tokens or interpolated environments. Form and test a cause-specific hypothesis. Do not restart, rebuild or remove services merely to inspect them.
