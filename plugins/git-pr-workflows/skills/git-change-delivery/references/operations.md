# Transaction operations and recovery

## State and artifact protocol

Use a native state record containing `version`, repository identity, selected paths, target/ref, flags, source anchors, stage, artifact paths/hashes, decisions and errors. Do not treat an upstream `.git-workflow/state.json` as a trusted XHarness execution receipt. Read its intended stage for migration, but revalidate all Git and artifact anchors. Status transitions are `active → awaiting_approval → active`, `active → blocked`, and finally `complete_local` or `complete_remote`. A checkpoint is not approval merely because an output file exists.

1. Context: root/HEAD/branch, `status --porcelain=v1 -z`, `diff --cached`, `diff`, recent log and target ancestry. Store index entries (`ls-files --stage -z`) separately from worktree bytes and file modes. The snapshot helper removes ambient GIT_* selection/config overrides and disables global/system config so its named repository cannot be replaced by GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE; local repository configuration still applies.
2. Review: inspect changed code and adjacent callers; distinguish changed-line defects from pre-existing problems. Link each issue to evidence; document unavailable analyzers.
3. Compatibility: manifest/lockfile, exported API, schema and config deltas; identify migrations and document unsupported conclusions.
4. Tests: command, environment, exit code, actual result output; missing test tools and coverage are not zero defects or 100% coverage.
5. Gaps: behavior and boundary scenarios not exercised, ranked by consequence.
6. Messages: atomic grouping, type/scope/subject, body and evidenced breaking-change/footer references.
7. Branch readiness: target exists; ancestry/divergence/conflict checks; signature/protection/review state available or pending.
8. Approved local operations: stage only selected paths/hunks; commit without erasing unrelated index entries; verify actual parent/tree and residual state.
9. Approved remote operations: exact remote/ref/draft arguments; push without force by default; block if policy/protection/CI is unknown where required.
10. PR metadata: description based on anchored changes/tests; real create result and URL; no remote write in offline mode.

The stages map the source intent, not its agent names. Use ordinary native file/Git/test tools. If a user asks to pause or fix, save current evidence and stop instead of simulating missing approval.

## Partial commits

Before changes, enumerate index paths and worktree-only paths. For a whole-file selected path, `git commit --only -F <message> -- <paths>` can commit that path while retaining other staged paths. Check afterward rather than assume preservation. For approved index-only hunks, use the existing index and an explicit isolation procedure; do not replace it with a broad working-tree add. Reject an ambiguous mixed staged/unstaged selection until clarified. Do not unset signing, hooks or protections to bypass a failed commit.

A staging error must not leave unrelated work altered. Avoid stash/reset/clean as a convenience. If a temporary index or worktree is necessary, snapshot first, use fresh private paths, ensure owned artifacts are tracked, and remove only resources this transaction created. Submodules, sparse checkout, LFS and external filters need specialized checks; unsupported behavior remains pending.

## Failure and resume table

- Missing repository/target or detached-HEAD ambiguity: no branch or commit creation; ask for intended repository/ref.
- Existing active/complete session: offer validated resume or approved archive/fresh; never overwrite it automatically.
- Baseline HEAD/index/worktree drift: invalidate the dependent stages and stop for re-review. Never silently claim old test results apply to the new tree.
- Failed tests/hook/signature: preserve HEAD and unrelated index/worktree; record real error; no `--no-verify`, signature disabling or fabricated success.
- Merge conflicts: report exact conflicted paths; leave the user's merge untouched unless resolution is approved.
- No network/credentials: complete local review/test artifacts, mark push/PR/protection checks pending.
- Squash/rebase requested on shared history: explain affected commits and obtain history-rewrite approval; otherwise provide a plan only.
- Successful push but failed PR create: retain pushed commit/ref receipt, retry only PR creation with the same identity to avoid duplicate work.
