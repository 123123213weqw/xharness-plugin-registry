# Compose workflow

Docker Engine and Compose must already be available. This plugin does not install Docker, start a daemon, register an MCP server or wrap subprocess ownership. All actual commands use existing Host execution tools and their timeout/cancellation/approval behavior.

Select the exact Docker context and Compose file before inspection. A remote context is not automatically the local machine. Start with version/context names, configuration validation via `docker compose -f FILE config --quiet`, and `docker compose -f FILE ps --all --format json`. Avoid `config` without --quiet: interpolation can print secrets. Supply environment variable names rather than values in reports.

## Preserve the actual command outcome

On a Unix Bash Host, enable `set -o pipefail` when using pipelines, or capture stdout to a file and inspect the original command exit before invoking the parser. On PowerShell 7, inspect `$LASTEXITCODE` immediately after the Docker command; throw/report if nonzero before passing captured output to Python. Do not let tail or the JSON parser override a failed upstream result.

`python scripts/compose_state.py compose-ps.json` parses either a JSON array (older output) or JSON Lines (current output), with typed observations and bounded input. No Docker command is invoked by the parser. It excludes the Command field and interpolated environment values. `ok` means parse success only. `issues_observed` records dead containers, unhealthy healthchecks and nonzero exits. Missing healthchecks, a new/unknown state, zero rows or a zero-code exited one-shot container require task-specific interpretation; none establishes readiness.

## Diagnosis and changes

Read bounded logs with --tail and --no-color from the selected services/time window; do not default to indefinite --follow. Verify failure hypotheses using the real state, exit and logs. Redact account tokens and passwords before saving evidence. Do not automatically restart/rebuild to inspect a service.

For requested changes, preserve volumes and unrelated services; validate the edited configuration, then use the actual approved Host command. Check application-level readiness after runtime state. `down -v`, prune, image/volume deletion and destructive cleanup require explicit scope. If a command is interrupted or its result is unknown, inspect state before replaying it.

Reference: [Docker Compose ps](https://docs.docker.com/reference/cli/docker/compose/ps/), [Compose logs](https://docs.docker.com/reference/cli/docker/compose/logs/).
