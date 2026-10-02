# Comparison and report mechanics

## Comparison facts

Use the resolved base/head and merge base. `git diff --name-status -z -M <merge-base> <head> --` and `git diff --numstat -z -M ...` avoid whitespace/tab splitting errors; rename numstat uses a separate old/new path form. Keep binary additions/deletions nullable and list binary paths explicitly. Categories are context-dependent: recognize tests before generic source extensions, docs before broad config guesses, and distinguish build files from ordinary JSON.

For each changed manifest/lockfile/API/schema/config, state old/new values and compatibility implications. A lockfile change is not automatically a vulnerability. Do not run package installers, third-party bots or vulnerability services solely because the source command named them; record availability and scope.

## Test and coverage evidence

Bind command, tested revision/environment, status, actual failures/skips and evidence path. A supplied CI receipt can be reported as supplied evidence, but not as a locally rerun test. Coverage before/after needs matching tools/config/scope; compute percentage-point deltas only for comparable numeric metrics. If coverage is missing, say unavailable, not 0% or 100%. Preserve failed tests in the description and risk assessment. Do not call unchecked acceptance criteria complete.

## Risk and reviewability

Separate size, complexity, critical paths, dependencies, compatibility and testing risk. Use concrete findings/unknowns and mitigation/owner; avoid precise universal risk or review-time numbers without an explicit model. A 20-file/1000-line source heuristic is a review prompt, not a correctness threshold. Split suggestions must partition logical changes and account for shared APIs/migrations; don't duplicate a file across supposedly independent groups without explanation.

Review automation can identify observed debug statements, TODOs, size or validation defects, but comment/string matches alone are not executable-code findings. Security and correctness findings need location/data flow; a console statement may be legitimate logging. Expose tool/rule limitations rather than claim SonarQube/CodeQL/Snyk ran when unavailable.

## Description and response modes

- Feature: purpose, evidenced behavior, acceptance checks, implementation, tests, rollout, UI evidence if applicable.
- Bug fix: supplied issue/context, actual root cause and behavior change, reproduction/regression evidence, affected scope (unknown versions stay unknown).
- Refactor: compatibility boundaries, preservation evidence and verified metrics only.
- Review response: acknowledge the precise issue; explain alternatives with evidence, ask clarification if needed, or propose a concrete change. Do not assert a fix has shipped before it has.

Diagrams show only relationships supported by code/docs; no decorative fictional cache/gateway. Include an explicit unavailable/pending section for provider metadata, screenshots, performance, scanners and deployed behavior that were not observed.
