---
name: technical-debt-planning
description: "Inventory located technical debt and create a risk/effort/benefit roadmap with transparent measurements, assumptions and incremental remediation."
---

# Technical debt planning

Inspect code, boundaries, dependencies, tests, docs and build/deployment configuration in the requested scope. Record each debt item with locations, concrete failure/change friction, category and evidence. Separate measured duplication/complexity/coverage/flakiness/version health from hypotheses; source example metrics are not facts about this project. Dependency/security freshness needs a real current source/tool, not recalled version claims.

Quantify costs only with supplied or measured rates, event frequency and change effort. Show units, assumptions and sensitivity; unknown hourly rates or monthly bug counts stay unknown. Prioritize consequential reliability/security/data risks and feature bottlenecks ahead of cosmetic quotas. ROI forecasts are forecasts, not saved money.

Propose quick wins, medium-term seams and longer architecture changes with owners, dependencies, effort ranges, expected measurable outcomes and rollback. Use regression tests, compatibility facades/strangler phases and explicit feature-flag ownership rather than an unbounded rewrite. Capacity allocation and calendars are caller/team decisions, not universal source example20% targets.

Define project-specific prevention gates and debt budget, how metrics will be collected, and a developer/stakeholder communication plan. A proposed CI gate is not enforced until the actual pipeline runs. Track trends only from comparable longitudinal data and report missing baselines. Do not mutate deployment/monitoring/accounts or publish reports without separate authorization.
