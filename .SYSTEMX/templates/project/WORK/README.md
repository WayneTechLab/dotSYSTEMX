# Project work

[TASKS.json](TASKS.json) is the canonical ledger.
[FOCUS.json](FOCUS.json) selects the objective, existing task IDs, and checkpoint.
The outer shared tools generate CURRENT.md and TODO.md, WORKING-ON.md,
BLOCKED.md, REVIEW.md, DONE.md, and CANCELLED.md within this project.

Use projects task-add, task-set, task-show, focus, refresh-work, and context with
an explicit --project name. Follow todo → in_progress → needs_review → done.
Completion requires evidence and review by this project's Agent 0 or the user.
Dependencies are local task IDs; record cross-project handoffs explicitly.

Never edit generated work views as competing task lists. No work is recorded
in this reusable blueprint, and no worker process is started by these files.

Agent X (event/time tracking) and Agent Z (fixed evidence review) can be enabled
with the outer `projects roles-init --project NAME --apply` command after preview.
Use their guides from the selected shared defaults. Keep events, schedules,
review policy, reports, and memory in this selected child. Agent 0 accepts tasks;
unchanged review inputs reuse the existing report without starting more work.
