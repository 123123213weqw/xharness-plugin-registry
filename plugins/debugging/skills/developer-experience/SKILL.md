---
name: developer-experience
description: "Improve an existing project setup, local tooling and feedback loop from measured developer friction without changing global configuration or claiming unrun integrations."
---

# Measured developer experience

Inspect actual project manifests, supported runtime, scripts/lockfiles, contribution/setup docs and the caller's pain points. Capture a baseline for clone→usable environment, manual steps, test/build/hot-reload feedback and common failure paths. If no measurement exists, propose one; do not promise a universal five-minute setup or invented satisfaction improvement.

Prefer small reversible repository-local improvements: clearer scripts/defaults/errors/help, task-runner targets, dry-run diagnostics and reproducible examples. Preserve user-selected tools and existing work. Network installs, global aliases/IDE settings, hooks and shared configuration require explicit scope; creating vendor `.claude/commands` does not recreate a native command runtime. Offer an opt-in local configuration rather than silently installing tools.

Validate normal setup and useful failure cases (missing runtime/dependency, wrong cwd/config, occupied port and interrupted work). Ensure commands have meaningful exits and help, are idempotent where promised and do not erase caches/data indiscriminately. Compare like-for-like before/after timings and manual steps. Document actual commands and prerequisites; a README example must work against the existing project, not a newly invented scaffold.

Keep feedback-loop and troubleshooting docs anchored to source paths and observed results. Record unrun OS/IDE/hook/CI cases and proposed next measurements. Team satisfaction and long-term documentation currentness need actual feedback and future maintenance, not a one-off local test.
