---
name: project-onboarding
description: Build a role- and location-specific first-90-day onboarding plan from an existing project's real setup, workflow and team context, with ownership, milestones and explicit access blockers.
---

# Project onboarding

Use the requested role, level, start date, manager/team, location/time zones and technical scope. Missing personnel, policies or budgets stay unknown; do not copy fictional company details into the plan. Read [the planning guide](references/plan.md) for phase outcomes and owner/action boundaries.

Inspect the existing project before recommending setup: manifests, supported runtime, lockfiles, declared scripts, CI, contribution guide, architecture/ADRs and runbooks. Preserve the repository and the employee's local work. Prefer a verified existing test/setup command to a new scaffold. If execution is permitted, run non-destructive commands in the designated fixture/development environment and record what actually ran; network installs, production connections and credentials need separate authorization.

Produce a reusable plan plus machine-readable milestones when requested. Tie every technical instruction to a source path or an observed tool result. Assign an owner and status to access, hardware, HR and learning tasks; a plan is not an account-provisioning receipt. Use secrets-manager enrollment instructions, never invented or printed temporary passwords, SSH private keys or API tokens.

Sequence pre-arrival readiness, Day 1 orientation/security/admin, first-week codebase and team immersion, guided first contribution, then 30/60/90-day outcomes. Calibrate expected PR counts and on-call responsibility to role and team policy rather than inherit a universal quota. Remote plans account for explicit overlapping hours, asynchronous docs and recorded sessions; senior plans bring forward architecture/postmortem/stakeholder learning without skipping access or security prerequisites.

Give each milestone a due date relative to the provided start date, a measurable artifact/outcome, a responsible person or unassigned role, and dependencies. Track first usable environment/first reviewed contribution/independent work as observations, not forecasts already achieved. Include buddy and manager check-in cadence, feedback questions, adjustment criteria and one documentation-improvement loop. Unknown permissions or missing tools block only dependent actions, not the rest of the plan.
