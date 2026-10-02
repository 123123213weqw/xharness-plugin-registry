---
name: git-change-delivery
description: Review, validate and deliver an explicitly approved Git change while preserving unrelated staged and working-tree work; includes resumable checkpoints and local-only delivery.
---

# Git change delivery

Work in the repository the caller names, never in an incidental current directory. This skill coordinates work through native tools; it does not install the upstream agent personas or reproduce a particular Task/AskUserQuestion runtime. Before execution read [the operation and recovery guide](references/operations.md), especially for resume, partial commits, branch changes or network operations.

## Establish the transaction

Record repository root, HEAD, branch/detached state, upstream, remotes, both index and working-tree diffs, untracked paths, and applicable project instructions. Preserve path boundaries and filenames containing whitespace. `git diff` alone omits staged changes. An existing workflow is input: resume only after checking its baseline against current Git facts; archive/start fresh only with approval. The optional [snapshot helper](scripts/snapshot.py) captures read-only object/index/worktree fingerprints without trusting a model-written baseline.

Separate five decisions: review approval, test approval, message approval, exact local Git-operation approval, and remote/PR approval. A caller may explicitly preapprove a narrowly described fixture transaction; that is not permission for other paths, history rewriting or a push. Without approval, write the next proposed action and stop. Store each stage's artifact and source fingerprints under a caller-chosen workflow directory, then advance state only after the artifact exists. A failed tool/test is a blocked stage, not a completed stage.

## Review → tests → commit

Review the actual diff with location and severity, then assess dependency/API/schema/configuration compatibility and migration/documentation requirements. Use the change-review skill when substantive review is requested. Run the project's declared test commands in the permitted environment and record real exit codes, failures, skipped suites and coverage availability. `--skip-tests` means explicitly skipped, never passed. Fixes invalidate prior review/test anchors; rerun the affected stages before proceeding.

Group commits by coherent behavior, not by file extension. A Conventional Commit subject describes the actual change; a breaking-change footer needs evidence and migration guidance. Present exact path selection and message before committing. A whole-file approval and an approval of only staged hunks are different: `commit --only -- <paths>` includes those paths' working-tree content, so use it only for explicitly approved whole-file changes. Never use `git add .` to absorb someone else's work. After committing, verify the new tree, parent, residual index and working-tree states against the transaction boundary.

## Branch and remote stages

Inspect local ancestry/conflicts without merging or checking out over dirty work. Use an isolated disposable worktree when integration needs execution; clean it up only after preserving its needed work. Feature/trunk policies belong to the project, not a universal naming rule. Squash/rebase/amend and protected-branch updates require separate explicit authorization. A missing target, unresolved merge or failed hook stops delivery; do not bypass hooks or force-push to make it green.

`no_push` blocks every network write while independently authorized local commits remain possible. Draft PR affects remote PR metadata only. Check signatures, protection rules, CI and remote review state only through available tools; missing credentials or network means pending, not verified. After a separately approved push, derive a PR description from anchored review, compatibility and test evidence using pr-evidence. Create/update a real PR only with authorization and an available provider connection; record the returned URL, not a guessed URL.

Finish with completed, skipped, blocked and pending stages, actual commit IDs, remaining dirty/staged work, and recovery choices. Prefer a new revert commit over destructive reset of shared history. Feature-flag disable, hotfix and team notification are recommendations until their separate systems actually acknowledge them.
