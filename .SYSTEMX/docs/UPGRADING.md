# Adoption and upgrades

Treat the reusable standard and an active project's records as different kinds
of content. Review an update in the intended checkout, preserve local changes,
and merge the standard without replacing the project's accepted plan or memory.
Each project selects its own defaults; updates do not synchronize project memory
or configure automatic updates in other projects.

## Upgrade to the alpha series

Install the new external CLI before selecting an alpha version; managers from
1.5.0 and earlier only accept numeric final IDs. Follow the exact commands in
[release policy](RELEASE-POLICY.md). Existing schema-1 project records and manager
state remain supported. The manager reads schema-1 installation state and saves
schema 2 with archive-digest receipts on its next state write; old releases receive
`null` receipts. Task and role record schemas remain unchanged. Alpha does not
grant permission to reset or overwrite them.

The new manager can inspect an older selected installation with `status`, run
its verified retained snapshot through an isolated compatibility shim, and
perform the external bootstrap/update migration below. It cannot install or
newly select a release older than **1.8.7-alpha.1**. That is the first release
with native isolated runner support, and `bootstrap-refresh` requires a target
release at or above that floor. The compatibility shim keeps the old
selected runner available if the refresh succeeds but the update fails; the old
code still has its historical behavior and record compatibility limits.
Historical reselection below this floor needs a separately reviewed backup or
legacy path, not a manager rollback flag.

## Managed installs and preserved files

The [installer and updater](INSTALLATION.md) add versioned default snapshots and
missing root files while preserving every existing project file and directory.
Use them to adopt a current managed-install release, then select the desired
version independently for each project. New installs are pinned with manual
updates. The root VERSION remains the initial seed version; installation state
identifies the currently selected defaults.

An older project's wrapper scripts are preserved by ordinary updates, too. During adoption use a
reviewed new external `systemx` command or `manager.py` from outside the target
to select new defaults. Existing old shell and PowerShell scripts are not
silently replaced and might not expose new commands. The eight stock root
bootstrap and launcher files have a narrow, explicit refresh path below.
Review any custom root guidance against the selected release, and use `validate`
to check the existing records before continuing. Adoption does not migrate or
clear incompatible legacy ledgers, rewrite old generated views, or assert
application readiness. Perform any needed record reconciliation explicitly.

## Refresh the root bootstrap before a changed release

An ordinary changed-release `update`, including its dry run, refuses a target
whose root `manager.py`, `lifecycle.py`, `versions.py`, `systemx_paths.py`,
`SYSTEMX.sh`, `SYSTEMX.ps1`, `INSTALL.sh`, or `INSTALL.ps1` differs from the
intended release. This prevents a preserved old manager or launcher from quietly
operating newer state. Use a **reviewed new tool outside the target** to preview
and, if appropriate, refresh those eight stock files first. For an offline
reviewed checkout, replace both paths in this sequence:

```bash
python3 -I -B "/path/to/reviewed-template/.SYSTEMX/manager.py" bootstrap-refresh \
  --target "/path/to/project" --source "/path/to/reviewed-template/.SYSTEMX"
python3 -I -B "/path/to/reviewed-template/.SYSTEMX/manager.py" bootstrap-refresh \
  --target "/path/to/project" --source "/path/to/reviewed-template/.SYSTEMX" --apply
python3 -I -B "/path/to/reviewed-template/.SYSTEMX/manager.py" policy \
  --target "/path/to/project" --pin none --auto manual
python3 -I -B "/path/to/reviewed-template/.SYSTEMX/manager.py" update \
  --target "/path/to/project" --source "/path/to/reviewed-template/.SYSTEMX" --dry-run
python3 -I -B "/path/to/reviewed-template/.SYSTEMX/manager.py" update \
  --target "/path/to/project" --source "/path/to/reviewed-template/.SYSTEMX"
python3 -I -B "/path/to/reviewed-template/.SYSTEMX/manager.py" policy \
  --target "/path/to/project" --pin current
python3 -I -B "/path/to/reviewed-template/.SYSTEMX/manager.py" run \
  --target "/path/to/project" --offline -- validate
```

On Windows, use `py -3 -I -B` with the same external manager path. Isolated mode
keeps the script directory and ambient Python path settings out of import lookup.
Review the preview's `add`, `replace`, and `conflicts` fields before applying it.
`bootstrap-refresh` accepts existing root bytes only if they match the target
release or an **intact retained release**. It may add a stock bootstrap file only
when the path is absent and that file was absent from every intact retained
historical release. For example, a genuine v1.5.0 installation can gain the later
`versions.py`. If a file existed in any retained release but is now missing, or
if its contents are customized or unrecognized, refresh stops for manual review.
Applying the preview creates only absent `add` files, saves byte-for-byte
originals for `replace` files under `.SYSTEMX/.systemx/history/bootstrap-.../`,
and records the operation. An add-only refresh has no original file to back up.
It replaces only recognized bootstrap and launcher files, including stock
shell/PowerShell wrappers; the refreshed launchers invoke the manager with
Python isolated mode (`-I`). It leaves project-owned records, other root defaults,
version selection, and the pin untouched. Keep the reported backup path with the
upgrade evidence.
The later `update` remains additive and selects the new default snapshot.
`bootstrap-refresh` refuses to replace these stock files with an older release;
do not present it as a rollback mechanism. A later supported-version selection
can work only when stock bootstrap and launcher files already match and the
project records remain compatible.

An external `systemx bootstrap-refresh` from a newly installed library offers
the same preview and `--apply` flow. You may use an exact remote `--version`
with `--archive-sha256` for both refresh and update if the digest belongs to the
exact downloaded codeload ZIP. Do not run the old root manager to perform this
migration. Customized or unrecognized wrappers need separate manual review; the
refresh refuses them. No command here automatically repairs custom wrappers or
application migrations.

## Existing 1.1.0 projects

1. Record the current Git state and preserve a recoverable copy or commit under
   the project's normal workflow.
2. Review changes to tooling, tests, guidance, templates, version, and provenance.
   Preserve `project.json`, `WORK/TASKS.json`, `AGENTS/REGISTRY.json`, all agent
   memories, `GLOBAL/CONTEXT.md`, `PLAN/MASTER-PLAN.md`, `MEMORY/PROJECT.md`, and
   session records. Merge instructional additions around populated content.
3. Add the blank `WORK/FOCUS.json` only if it does not exist. Preserve an existing
   focus record. `CURRENT.md` is a new generated view: if the project already has
   a hand-written file by that name, preserve it as a dated session checkpoint
   before adopting the generator. Review links to that former file.
4. Run `bash .SYSTEMX/SYSTEMX.sh refresh-work`, then `validate`. Both use the
   existing task IDs, statuses, evidence, and history; no task schema migration
   or renumbering is required.
5. Select the existing objective and relevant task IDs using `focus`. Link the
   preserved checkpoint if useful, then inspect `context --agent agent.0`.

Use ordinary `validate` on the adopted project. `validate --template` is for
blank public distributions and should reject real project records. The updated
validator also checks chronological history and rejects stale current blockers,
reviewers, or terminal next actions. If a manual edit or old integration left
inconsistent metadata, reconcile it against original evidence; do not fabricate
timestamps or clear acceptance history merely to satisfy the validator.

Example after the project already has `TASK-001`:

```bash
bash .SYSTEMX/SYSTEMX.sh focus --objective "Finish the accepted milestone" --task TASK-001
bash .SYSTEMX/SYSTEMX.sh task-ready
bash .SYSTEMX/SYSTEMX.sh context --agent agent.0
```

The focus record is a compact pointer. It contains no hand-maintained task
status, blocker, next action, totals, or runtime health. Those come from the
task ledger or freshly inspected evidence. The command replaces the selection;
include every task ID to retain in the next focus.

## Other SYSTEMX layouts

Existing projects may use `status/`, `TODO/`, `MasterPlan/`, `plans/`, `CURRENT.md`,
or domain-specific ledgers. Inventory their actual authorities before migration.
Do not copy the blank template over them or import historical queues as if they
were new assignments.

Preserve original IDs and acceptance credit in their existing ledger. Keep one
authority during a staged adoption: either retain that project's ledger and
adopt the written guidance only, or design and verify an explicit migration.
The generic CLI currently accepts `TASK-001` task IDs and `M-001` milestone IDs;
it is not a lossless importer for arbitrary legacy IDs, receipt schemas, or
controllers. A mapping must retain provenance, dependencies, open obligations,
and original evidence before switching authority. Parallel advisory views must
never become independent completion ledgers.

Keep domain extensions in the host project's chosen directories and link them
from Global context. Trading controllers, contract release policies, provider
deployment scripts, local dashboards, and active-project history are not part
of this universal template. Keep operational/private content outside public
build outputs.

## Adding SYSTEMX PROJECTS

Update the outer installation to a release containing `docs/PROJECTS.md` and
`scripts/project_workspaces.py`; review/unpin the current version first, then
re-pin after verification. Existing root tasks and memory remain in place.
Use `projects add NAME` to preview a new blank child and `--apply` to create it;
never install another `.SYSTEMX` under the outer folder.

If `Projects/REGISTRY.json` already exists, additive updates preserve it. A custom
schema or populated legacy `.SYSTEMXP` may need a reviewed migration to the
[generic registry and record contracts](PROJECTS.md). New commands reject unknown
schemas and occupied destinations without replacing them. Preserve the original
records, IDs, evidence, and private source references. Do not copy real project
records into the public template or blank creation seeds.

## Agent X/Z adoption

Update the selected defaults to a compatible release, verify it, and keep the
version pinned. Preview `roles-init` in each intended scope before applying it.
An update alone preserves registries and does not activate roles. The public seed
registry remains Agent 0 only so existing managed launchers can verify upgraded
defaults. Once `agent.x` or `agent.z` is registered, older tool versions cannot
interpret those IDs: review migration or restore a pre-activation backup before
historical recovery. The current manager cannot newly select releases below its
1.8.7-alpha.1 floor, though it can invoke an already selected verified older
snapshot through the compatibility shim. Never delete events or review records
to make a downgrade
appear successful. Project `REVIEWS/POLICY.json` is preserved; adopt later default
questions only through an explicit versioned policy edit.
