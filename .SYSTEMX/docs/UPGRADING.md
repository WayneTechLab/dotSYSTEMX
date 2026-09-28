# Adoption and upgrades

Treat the reusable standard and an active project's records as different kinds
of content. Review an update in the intended checkout, preserve local changes,
and merge the standard without replacing the project's accepted plan or memory.
The template does not synchronize itself into other repositories.

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
