---
name: git-pr-workflows
description: "Produce evidence-bound git pr workflows artifacts for the requested workflow; distinguish offline checks from runtime integration."
---

# Git Pr Workflows

Inspect status and diff before proposing staging or commits. Keep unrelated user changes out of the task, describe behavior changes and test evidence in the PR, and separate requested mutation from advisory output. Preserve commit hooks and signing policy. Onboarding instructions should reflect actual setup commands. Offline file classification is not a created branch, pushed commit or published pull request.

## Verification boundary

Use the explicit output schema requested by the caller. Do not label an offline artifact as a live integration result. Record unperformed runtime checks and unsupported integration surfaces.
