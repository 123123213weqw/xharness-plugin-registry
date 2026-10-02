# Phases, ownership and evidence

| Phase | Planned outcomes | Owners/dependencies | Observable evidence |
|---|---|---|---|
| Before start | Access requests, MFA/SSO enrollment, equipment/IT session, current role docs and agenda | IT/manager/HR; user-approved systems | Request IDs/owner/status; never assumed accounts or shipment tracking |
| Day 1 | Welcome, mission/product/expectations, security/admin orientation, tool walkthrough | Manager/buddy/IT/HR | Agenda, named contacts or explicitly unassigned roles; local setup attempts |
| Week 1 | Repository/architecture map, branching/review/CI/test/deploy/incident walkthrough, guided first issue | Buddy/tech lead; repository and sandbox access | Existing source/doc links, real commands/results, reviewed learning artifact |
| Days 8–30 | Pairing/review observation/product and domain learning, document one unclear workflow | Buddy/manager | First contribution and documentation plan; actual achievements recorded later |
| Days 31–60 | Scoped feature ownership, design participation, authorized on-call shadow, cross-team contacts | Manager/tech lead; training readiness | Acceptance criteria for a small feature and shadowing evidence |
| Days 61–90 | Independent delivery/review, process improvement, mentoring as appropriate | Manager; role-calibrated readiness | Review checkpoint with demonstrated evidence, not automatic employment decisions |

## Technical map

Discover source entrypoints, test layout, public API/schema, local config template, architecture documents, CI commands and first-issue backlog. Quote exact project paths and supported toolchain versions. Explain prerequisites before dependent steps. A failed local test is an environment/test blocker with actual exit output; never replace the existing project with a sample application just to show a green setup.

Check communication and time-zone constraints from given context; state assumptions for unknown working hours. For remote hires, provide async handoff/recording choices. For senior hires, add early architecture, postmortem, debt and stakeholder assessment, followed by a decision artifact rather than arbitrary major-code-change pressure.

## Access and organization boundaries

Creating email/cloud/source-hosting accounts, granting permissions, shipping hardware, scheduling calendar events, enrolling benefits and HR records are external actions. Prepare requests and assign owners unless an authorized connector actually completes them. MFA, password managers and secrets managers are enrollment prerequisites, not reasons to generate credentials. Missing contacts are `unassigned`, missing approval is `pending`, missing runtime/service access is `blocked`; none should be marked `done` from a checklist.

Use buddy/manager check-ins that fit team availability: early frequent brief check-ins, then less frequent progress reviews. Feedback covers learning obstacles, access, documentation clarity, team connections and working-hours fit. Revise the plan when a dependency fails or evidence contradicts a target. Surveys and dashboards are proposed until populated from real responses; time-to-productivity metrics require actual timestamps.
