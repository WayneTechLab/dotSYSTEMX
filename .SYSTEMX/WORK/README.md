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
then regenerate all six status pages and [CURRENT.md](../CURRENT.md). `validate` detects stale generated pages, bad
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

## Current focus and bounded dispatch

[FOCUS.json](FOCUS.json) records the current objective, up to ten existing task
IDs, and an optional checkpoint pointer. It contains no duplicate task status,
blocker, or next action. All of those are read from the ledger when generating
`CURRENT.md`. Selected task IDs can remain as completed context until Agent 0
chooses the next focus; their completion never implies the project is complete.

```bash
bash .SYSTEMX/SYSTEMX.sh focus --objective 'Finish the accepted outcome' --task TASK-001
bash .SYSTEMX/SYSTEMX.sh task-ready --agent agent.1
# Replace the placeholder with the source revision you just verified.
bash .SYSTEMX/SYSTEMX.sh task-packet TASK-001 --base 'REPLACE_WITH_VERIFIED_REVISION'
```

Supply the actual observed revision as the base argument. Repeat `--task` to
select multiple IDs. `focus` replaces the
whole selection; include every ID to retain. Add `--checkpoint` with an existing
Markdown path relative to `.SYSTEMX` under `MEMORY/sessions/`. The objective is
limited to 600 characters. `focus --clear` clears only the selection and retains
task history and checkpoint files.

`task-ready` returns only TODO tasks whose dependencies are all done. It excludes
active, review, blocked, cancelled, and completed tasks. Dependencies on cancelled
work remain unresolved. It does not rank the critical path or check write-scope,
resource, credential, process, or permission readiness.

`task-packet` prints the existing assignment and dependency summaries, required
acceptance, source revision reported by the caller, and the owner's memory. It
does not reassign or start work. It caps the task packet at 14,000 characters and
owner memory at 3,000, with explicit truncation notices. Read `task-show` and
original dependency evidence when more detail is needed. A packet can describe
blocked work for diagnosis; it does not certify dispatch readiness.

Use the [evidence guide](../docs/EVIDENCE.md) to scope source and runtime claims
and the [upgrade guide](../docs/UPGRADING.md) when adopting an existing layout.

## Agent X events and Agent Z acceptance review

When standard roles are enabled, record meaningful observations with Agent X and
review a task once with Agent Z at `needs_review`, or reuse a scorecard for the
same source/evidence/policy inputs. Link its report as supporting evidence; Agent
0 or the user still accepts `done`. A score never changes task state or establishes
production authority. An initial prompt can be reviewed on request. See
[Agent X](../docs/AGENT-X.md) and [Agent Z](../docs/AGENT-Z.md).
