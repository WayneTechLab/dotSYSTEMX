# Uninstall, Restore, and Cleanup

`.SYSTEMX` provides a reversible **project-folder uninstall**, separate from
removing the optional Python package. Updates remain additive; removal only
happens through an explicit uninstall invocation with `--apply`.

## What removal means

The uninstaller moves the **entire `.SYSTEMX` directory**, including your tasks,
memory, custom files, credentials stored there, logs, and all retained releases,
to a new private backup directory you choose. Your records are preserved in that
backup and become inactive in the original project. The containing project and
files outside `.SYSTEMX` stay in place. There is no permanent-delete or purge mode.

A valid local `.systemx -> .SYSTEMX` sibling alias is removed and recorded for
restore. On a case-insensitive filesystem there is no separate alias entry to
remove. Conflicting case variants are refused rather than guessed or merged.
The backup must be outside the project, on the same filesystem, with an existing
parent and a new destination name. This allows a folder rename instead of a
partially copied backup. Move or copy the verified backup elsewhere later if needed.

## 1. Stop writers and inspect

Finish active work, checkpoint evidence, and stop project/agent processes that
write inside `.SYSTEMX`. Wait for cloud synchronization and coordinate other
computers. The local writer lock cannot stop unrelated programs or remote writers.

Use the installed library in an external Python environment, or a separate
reviewed template checkout. Do not invoke removal from the target's own manager
or from a current working directory inside the folder being moved. Keep your
backup location and logs private; they may contain private project data.

```bash
systemx audit --target "/path/to/project"
systemx uninstall --target "/path/to/project" --backup "/path/to/backups/example-removal"
```

The uninstall command **previews by default**. It shows the scope, inventory
count, file bytes, backup location, and whether a separate alias will be removed.
The preview creates no backup or log. Read that scope before applying it.

## 2. Apply and verify

```bash
systemx uninstall --target "/path/to/project" --backup "/path/to/backups/example-removal" --apply
systemx audit --target "/path/to/project"
```

The backup contains `.SYSTEMX/`, `UNINSTALL-LOG.json`, and a local `.gitignore`
rule to reduce accidental Git inclusion. Ignore rules are not access control. The log records the
original target, timestamps, status, file paths, raw SHA-256 hashes, file sizes,
empty directories, link targets, alias state, and a scoped post-removal audit.
The inventory does not follow content links. The temporary writer lock is
excluded; active locks and unsupported special filesystem objects require review.
No files are uploaded and no project command is executed.

`audit` reports `clean: true` only when no `.SYSTEMX` case variant remains in
that selected project. It is **not a whole-computer scan** or proof that pip,
another project, a cloud copy, a backup, or a manual integration has been removed.
An installed project normally has `clean: false`; read its issues and installation
details. Audit is offline, read-only, and reports nonzero exit status for issues.

## 3. Restore when needed

Keep or reinstall the external library, then preview and apply:

```bash
systemx restore --target "/path/to/project" --backup "/path/to/backups/example-removal"
systemx restore --target "/path/to/project" --backup "/path/to/backups/example-removal" --apply
systemx run --target "/path/to/project" --offline -- validate
```

The containing project must exist and its `.SYSTEMX` destination must be empty.
Restore checks the backup against the receipt and will not overwrite a current
installation, user directory, or conflicting alias. It moves the folder back,
recreates a previously linked alias when needed, and records the restore result
in the external receipt. The backup directory and receipt remain as an audit trail.
Version pins, update settings, user records, and retained defaults are restored
as saved. Review an opt-in startup policy before the next non-offline launch.

## Interrupted operations and older installations

After a failure, keep both locations and inspect `UNINSTALL-LOG.json`. It may
record `prepared`, `archived`, or `incomplete` instead of `complete`. Data is never
deleted to repair a failure. A process killed during a move can leave a writer
lock in the source or backup; verify the owner has stopped before manually removing
only that stale lock. Restore accepts a verified archived folder and can recover
its recorded dangling alias. If hashes differ, review the changes before manual
recovery; do not edit the receipt merely to bypass verification.

Old installs and manually copied folders can be archived by the current external
manager. Their earlier install provenance cannot be reconstructed retroactively.
New managed install, update, policy, alias-creation, and first-run operations write
local JSON receipts under `.SYSTEMX/.systemx/operations/`; completed, failed, and
unfinished operations are distinguishable. These receipts move with the folder during uninstall. A new operation-log folder
gets its own local ignore rule, including on older installs; existing ignore files
are preserved. Already tracked or force-added files still require explicit review.

## 4. Remove the optional package and manual integrations

After all intended projects have been handled, use the **same Python environment
that installed the library**. Save the package log outside that environment:

```bash
python -m pip show -f dotsystemx
python -m pip --log "/path/to/logs/dotsystemx-uninstall.log" uninstall dotsystemx
python -m pip show dotsystemx
```

Pip will ask for its normal confirmation. The final `show` should report the
package absent. Consult the official [pip uninstall](https://pip.pypa.io/en/stable/cli/pip_uninstall/)
and [logging](https://pip.pypa.io/en/stable/cli/pip/) documentation. On Windows,
call the selected environment's `Scripts\python.exe`; on macOS/Linux, its
`bin/python`. Another environment can still contain another installation.

| Item | Cleanup and evidence |
| --- | --- |
| Project `.SYSTEMX` and optional alias | Reversible uninstall, external receipt, scoped audit |
| Python library/console command | Pip uninstall in the installing environment; retain pip log and verify absence |
| Dedicated virtual environment | After package verification, move the dedicated environment to Trash through the OS if no other tool uses it; preserve external logs |
| Reviewed template checkout or downloaded ZIP/wheel | Archive or Trash that explicitly selected copy when no longer used; do not touch an upstream source checkout |
| Manual root agent instructions, editor tasks, aliases, or local Git exclusions | Review the host diff and remove only the exact `.SYSTEMX` integration you added; log the changed paths |
| Exported chat packets or cloud copies | Review each explicit copy and use that service's normal removal/recovery controls; local uninstall cannot revoke shared attachments |
| Shared Python/Git/editor/Drive client, caches, or app dependencies | Leave shared tools in place unless separately selected for removal with their own official uninstaller |

The standard installer does not add OS packages, services, schedulers, startup
hooks, PATH edits, editor extensions, or cloud resources. Pip/source builds can
use package caches and temporary build environments; do not broadly purge shared
caches to claim cleanup. For project-specific tools you add later, record owner,
version, install location, original state, verification, uninstall steps, and log
location at installation time. A clean handoff names any intentional leftovers
and the exact scope that was checked.
