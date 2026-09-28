# Agent 0 and subagents

## Coordinator: agent.0

Agent 0 is the project coordinator, whether one LLM performs all work or approved
subagents assist. It maintains the master plan, decomposes work into verifiable
tasks, assigns ownership, resolves dependencies, reviews results, integrates
changes, and promotes verified findings into shared memory.

[REGISTRY.json](REGISTRY.json) records role IDs and memory paths. The template
contains only `agent.0`; a record is not a running process, authentication
identity, or permission grant.

## Worker lifecycle

1. Agent 0 defines the task, scope, dependencies, acceptance criteria, and owner.
2. If delegation is authorized and useful, register a stable worker ID with
   `agent-add agent.1 --role test`, then use the available environment to start
   the worker. Registration alone does not spawn it.
3. The worker loads shared context and its own memory with
   `context --agent agent.1`, then confirms the assigned scope.
4. Agent 0 sets the task to `in_progress` when work actually starts. Assign
   non-overlapping write scopes or coordinate shared-file changes explicitly.
5. The worker maintains its own memory and supplies a checkpoint with evidence,
   changed files, limitations, and an exact next action.
6. Agent 0 records `needs_review`, reviews the evidence, and accepts `done` only
   when the criteria are met. A failed review returns the task to `in_progress`
   or records a concrete blocker.

Subagents do not independently rewrite the master plan, shared context, project
memory, or other agents' records. They propose those changes to Agent 0. Agent 0
serializes updates to the canonical ledger. CLI writes use a local lock and
atomic file replacement; manual concurrent edits or independent Git worktrees
still require coordination and merge review.

## Handoffs and memory

Each worker gets `AGENTS/<agent-id>/MEMORY.md` from the
[agent memory template](../templates/AGENT-MEMORY.md). Task ownership lives only
in [WORK/TASKS.json](../WORK/TASKS.json); memory links the relevant IDs and captures
the observations needed to resume. Use the
[session checkpoint](../templates/SESSION-CHECKPOINT.md) for longer handoffs.

When a worker stops, its role record remains available for historical evidence.
Do not describe a registered worker as active without current runtime evidence.
Do not reuse an old memory file for a different project without deliberate reset.

## Acceptance authority

Only `agent.0` or the project owner (`user`) is recorded as the reviewer for a
completed task. This is a collaboration convention checked by the CLI, not an
authentication or access-control system. Existing production, financial, and
external-action authority remains separate from task completion.
