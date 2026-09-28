# Active work

[TASKS.json](TASKS.json) is the canonical task ledger. Agent 0 maintains it with
the task commands. The following pages are generated views; do not edit them
independently:

| View | Status | Meaning |
| --- | --- | --- |
| [TODO](TODO.md) | `todo` | Accepted work waiting to start. |
| [WORKING-ON](WORKING-ON.md) | `in_progress` | Work has actually started. |
| [BLOCKED](BLOCKED.md) | `blocked` | A named dependency or decision prevents progress. |
| [REVIEW](REVIEW.md) | `needs_review` | Implementation/findings await acceptance review. |
| [DONE](DONE.md) | `done` | Acceptance evidence reviewed by Agent 0 or the owner. |
| [CANCELLED](CANCELLED.md) | `cancelled` | Work intentionally stopped; reason retained. |

The shipped ledger is empty so it is reusable. It does not claim the project
is complete. `status` prints counts and recorded work; it does not inspect live
agent processes. `task-show` prints the full task, including transition history.

## Commands

Run these from the repository containing `.SYSTEMX`:

```bash
bash .SYSTEMX/SYSTEMX.sh status
bash .SYSTEMX/SYSTEMX.sh agent-add agent.1 --role test
bash .SYSTEMX/SYSTEMX.sh task-add --title 'Verify the selected behavior' \
  --owner agent.1 --acceptance 'The affected behavior has reproducible evidence' \
  --scope 'tests/' --next 'Inspect the relevant existing test'
bash .SYSTEMX/SYSTEMX.sh task-set TASK-001 --status in_progress \
  --next 'Run the focused regression check'
bash .SYSTEMX/SYSTEMX.sh task-set TASK-001 --status needs_review \
  --evidence 'Record the actual command, revision, result, and evidence path here'
bash .SYSTEMX/SYSTEMX.sh task-set TASK-001 --status done --reviewer agent.0
bash .SYSTEMX/SYSTEMX.sh context --agent agent.1
```

These are example commands for an adopted project, not tasks to run in the blank
template. Replace the example acceptance and evidence with real observations.
Recording evidence does not run a test or independently verify its truth.

`task-add` assigns the next stable `TASK-001` ID. Repeat `--acceptance`, `--scope`,
or `--depends-on` to supply multiple entries. `--milestone M-001` links work to a
milestone ID declared in the master plan. Omit it for unassigned intake work.

`task-set` accepts `--status`, `--owner`, `--next`, `--blocker`, repeated
`--evidence`, `--reviewer`, and `--note`. Evidence is appended. Register owners
before assigning work. Dependencies must be done before starting/reviewing or
completing a dependent task. `blocked` needs a blocker; cancellation needs a
note. `done` requires the `needs_review` state, evidence, and reviewer `agent.0`
or `user`. Failed review returns to `in_progress` or `blocked`.

Completed or cancelled tasks can reopen to `todo`. Prior completion evidence
stays in history, while current acceptance evidence/reviewer are cleared. Reopen
dependent tasks first if they would otherwise rely on an unfinished dependency.

## Consistency and concurrency

Commands validate records, take a local coordination lock, update JSON atomically,
then regenerate all six pages. `validate` detects stale generated pages, bad
owners, missing dependencies, cycles, and invalid completion records.

After an intentional manual edit or resolved Git merge, run:

```bash
bash .SYSTEMX/SYSTEMX.sh refresh-work
bash .SYSTEMX/SYSTEMX.sh validate
```

The lock coordinates CLI writes in one checkout. It is not a distributed lock,
and direct file edits do not acquire it. Agent 0 owns shared writes. If a process
crashes and leaves `state/coordination.lock`, establish that no writer is running
before removing that empty lock directory. Do not delete task or agent records
to recover a stale lock.
