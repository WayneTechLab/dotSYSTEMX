# Remove or restore Agent Beta, Agent1, and Agenda

This page adds role-specific checks to the existing reversible
[project-folder uninstall](../docs/UNINSTALL.md). There is no separate
`agent-beta uninstall`, `agent-1 uninstall`, or `agenda uninstall` command in
this beta release. The supported folder operation archives the **entire**
`.SYSTEMX` directory; it does not permanently delete it. Use an external
reviewed manager or installed `systemx` library, never the manager being moved.

## 1. Identify the exact scope and stop writers

Confirm the containing project path and whether it has selected
`Projects/NAME/.SYSTEMXP` children. The folder uninstaller moves the outer
`.SYSTEMX`, including all children, Agent Beta workspaces, Agent1 policy,
Agenda/access records, logs, and ignored local contents. It does not offer a
child-only folder removal. Inspect records and backups as private data even
when the template source is public.

Finish tasks and stop every process that writes inside the selected folder.
Close an Agent1 stdio client with its `stop` method or EOF, then verify the
process ended. `service status` reports transport capability; it is **not** a
daemon or process inventory. Check any Agent Y CLI run, provider subprocess,
worktree, and PR separately; a timeout or closed local record does not prove
the provider stopped. Coordinate another host or synchronized copy before
moving the folder. Agent X due records and Alpha Agenda settings do not own an
external scheduler, but inspect any separately installed scheduler that was
referenced by the project.

## 2. Inventory what the folder command cannot remove

| Item | Owner-side check |
| --- | --- |
| Agent1 registry/memory and `local/AGENT1-CONFIG.json` | `agent.1` registration and memory, the ignored local configuration, and fixed catalog under `SECURITY/AGENT1/` are archived with `.SYSTEMX`. Inspect project/account metadata before sharing the backup. Values should never be stored there. |
| Agent Beta `AGENTB/.SYSTEMXB-*` | Included in the folder archive even if ignored by Git. Review private memory and any separate online BOT/DOT provider account or remote copy. Local metadata never proves online disconnection. |
| Alpha Agenda, `GLOBAL/ACCESS-MATRIX.json`, and exported `local/` workbook | Archived with the folder. Default role rows grant nothing; reviewed decisions and spreadsheet copies are intent, not permission grants or revocations. Verify actual OS/GitHub permissions separately. |
| GitHub Actions secrets set through `agent-1 env-migrate --apply` | Remain at GitHub. Record owner, repository, environment, name, last consumer, rotation/retention decision, and provider-side deletion evidence if removal is separately authorized. Local uninstall does not revoke them. |
| Local `.env` or OS credential store | Usually outside `.SYSTEMX`; inspect exact path/store and consumers. Do not assume archiving `.SYSTEMX` deletes or rotates them. |
| Agent Y job, branch, worktree, PR, provider session | Use the [Agent Y lifecycle](../docs/AGENT-Y.md) and verify external state. |
| Cloud copy, online BOT/DOT destination, external scheduler | Use that provider's own removal/recovery controls and record readback. A URL or due item is only a reference. |
| Python package and dedicated virtual environment | Uninstall separately only after all intended projects have been handled; keep package logs outside the environment. Shared Python, Git, editors, and caches are not project-owned. |

Do not use a broad process kill, cache purge, `git clean`, or repository reset
as a substitute for identifying owned resources. A repository writer or guest
may still have access to remote Actions or copies after local removal; check
actual provider roles and revoke or rotate as required by the owner's policy.

## 3. Preview the reversible folder move

Run these from outside the target `.SYSTEMX`. `systemx` below means the
installed, external library described in the
[first-run guide](../docs/FIRST-RUN.md), or an equivalent separately reviewed
manager checkout. The backup is a **new** directory outside the project with
an existing parent, on the same filesystem:

```sh
systemx audit --target "/path/to/project"
systemx uninstall --target "/path/to/project" \
  --backup "/path/to/backups/project-removal"
```

The preview is read-only. Read its exact target, file count, bytes, alias
state, and backup destination before applying. An active writer, special file,
conflicting `.SYSTEMX` case variant, existing backup destination, or an
ineligible path requires inspection rather than a forced removal.

## 4. Apply, then verify the local boundary

```sh
systemx uninstall --target "/path/to/project" \
  --backup "/path/to/backups/project-removal" --apply
systemx audit --target "/path/to/project"
```

The backup contains `.SYSTEMX/`, `UNINSTALL-LOG.json`, and an ignore rule.
The receipt inventories paths, sizes, hashes, and a scoped post-removal audit.
Keep it private: ignored files and logs can be included. `audit` reports
`clean: true` only when no `.SYSTEMX` case variant remains at that selected
project. It does not scan other checkouts, Python environments, GitHub,
cloud copies, local credential stores, or a separately installed service.
The core installer did not install an OS daemon or scheduler; the Agent1 stdio
session exits with its client and still needs process-exit verification.

## 5. Restore if the project is needed again

Use the same external tool. The containing project must exist and the
`.SYSTEMX` destination must be empty:

```sh
systemx restore --target "/path/to/project" \
  --backup "/path/to/backups/project-removal"
systemx restore --target "/path/to/project" \
  --backup "/path/to/backups/project-removal" --apply
systemx run --target "/path/to/project" --offline -- validate
```

Restore verifies the backup inventory and does not overwrite a new
installation or conflicting alias. It restores saved role records and policy,
not revoked GitHub credentials, deleted external jobs, or removed cloud copies.
Review the active release, access matrix, `.env` consumers, and any opt-in
startup policy before a non-offline launch.

## 6. Finish separate package and provider cleanup

If this was the last intended project, follow the
[core package-removal steps](../docs/UNINSTALL.md#4-remove-the-optional-package-and-manual-integrations)
in the same Python environment that installed `dotsystemx`. Verify any manual
root instructions, aliases, editor tasks, or local Git exclusions by exact
host diff. For every external action, retain its owner, scope, original
resource ID, operation time, and readback. A completed local archive is one
boundary; it is not proof that a remote secret, schedule, provider job, or
guest permission was removed.
