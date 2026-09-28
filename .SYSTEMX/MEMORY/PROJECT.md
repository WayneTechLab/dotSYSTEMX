# Project memory

Template state: no project facts recorded. Agent 0 maintains verified facts and
accepted decisions here. Read the [memory protocol](README.md) before editing.

## Durable facts

| Fact | Source / evidence / revision | Verified at | Recheck condition |
| --- | --- | --- | --- |

## Accepted decisions

| Decision / reference | Reason | Owner / date | Supersedes |
| --- | --- | --- | --- |

## Lessons and unsuccessful approaches

| Finding | Evidence and limit | Consequence for future work |
| --- | --- | --- |

## Continuity references

The active objective and checkpoint pointer belong in
[WORK/FOCUS.json](../WORK/FOCUS.json), maintained with `focus` and displayed in
[CURRENT.md](../CURRENT.md). Task next actions and blockers belong in the ledger.

- Durable evidence or decision references needed across sessions:
- Historical checkpoints worth retaining and why:
- Conditions requiring old observations to be rechecked:

Current task status remains in [WORK/TASKS.json](../WORK/TASKS.json). Do not infer
current runtime or production state from an old memory entry.
