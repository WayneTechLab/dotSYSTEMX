# Project memory and continuity

## Memory layers

| Layer | Canonical record | Maintainer |
| --- | --- | --- |
| Current objective and task/checkpoint pointers | [WORK/FOCUS.json](../WORK/FOCUS.json), displayed in [CURRENT.md](../CURRENT.md) | Agent 0 through `focus` |
| Shared project context | [GLOBAL/CONTEXT.md](../GLOBAL/CONTEXT.md) | Agent 0 with the owner |
| Outcomes and sequencing | [PLAN/MASTER-PLAN.md](../PLAN/MASTER-PLAN.md) | Agent 0 with the owner |
| Live work and acceptance evidence | [WORK/TASKS.json](../WORK/TASKS.json) | Agent 0 through the work commands |
| Verified facts and lessons | [PROJECT.md](PROJECT.md) | Agent 0 after review |
| Scoped worker continuity | Registered agent's `MEMORY.md` | That worker; reviewed at handoff |
| Older checkpoints | [sessions/](sessions/README.md) | The checkpoint author |

The task ledger is the authority for task status. Memory references task IDs and
evidence rather than duplicating whole task lists. Shared memory records verified
facts; tentative findings remain labeled in the worker's notes until reviewed.
Do not copy changing next actions or task totals into every entry point. The
generated current view reads those facts from the ledger, and a dated checkpoint
retains what was observed then without claiming that it is still current.

## Start and resume

Load [START-HERE.md](../START-HERE.md) and the selected agent's context. Check
timestamps, source revisions, unresolved blockers, and the last exact next action.
Revalidate facts likely to drift. If the old checkpoint conflicts with live
evidence or current instructions, record the correction and use the current
state. Do not rerun every historical check merely to reconstruct context.

## Checkpoint before handoff or compaction

Update the worker's memory with:

1. Objective, task IDs, scope, and expected acceptance evidence.
2. Repository/branch/revision and relevant uncommitted changes.
3. Work completed, facts observed, checks run, and evidence paths.
4. Hypotheses versus verified conclusions; failed approaches and why.
5. Exact blocker, pending decision, and concrete next command or action.
6. Timestamp and author/session reference.

Use [SESSION-CHECKPOINT.md](../templates/SESSION-CHECKPOINT.md) for a durable
checkpoint. Keep the current resume note short; archive older checkpoints under
`MEMORY/sessions/` with a timestamp and task ID, then link them. Do not overwrite
someone else's checkpoint or retain full transcripts by default.
Point `focus --checkpoint MEMORY/sessions/<file>.md` at an existing sanitized
checkpoint when replacing the current focus selection. The command preserves
older files. `context` includes a bounded current view and prioritizes selected
focus tasks before other open work; it does not preload historical checkpoints.

## Promote and correct

Subagents submit findings and evidence to Agent 0. Agent 0 reviews them, updates
the task ledger, and promotes reusable facts or accepted decisions to project
memory. Rejected or superseded findings retain a concise reason. Completing a
task does not automatically copy all worker notes into shared memory.

This project-file workflow is for projects that adopt it under their existing
instructions. It does not authorize writing to a host tool's global memory,
editing other repositories, or retaining secrets/personal data. Keep private
runtime artifacts in ignored folders and commit only sanitized durable records.
