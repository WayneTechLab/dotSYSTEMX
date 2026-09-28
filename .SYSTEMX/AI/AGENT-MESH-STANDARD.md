# Agent coordination

The coordinator is recorded as `agent.0`. See the
[agent operating contract](../AGENTS/README.md) for registry and memory ownership,
and the [work ledger](../WORK/README.md) for task state and review commands.
For solo work, Agent 0 can also implement the task; additional workers are optional.

## Optional delegation

Use a single worker by default. Delegate only when allowed by the user and the
active environment, and when a concrete independent subtask improves the work.
This document does not authorize creating agents or separate user tasks.

The coordinator owns scope, integration, review, and the final result. A worker
owns a bounded subtask and supplies evidence. The project owner retains authority
over consequential actions under the project's existing policies. Tool access
does not grant independent production or spending authority.

## Task envelope

For each delegated task, record:

- objective and acceptance criteria;
- owner, allowed tools, and files or systems in scope;
- known constraints and dependencies;
- expected evidence and stop conditions;
- completion result, unresolved issues, and next action.

Keep concurrent edits separate or coordinate ownership explicitly. Avoid shared
state mutations that can invalidate another worker's evidence. Review delegated
findings against source and tests before integration.

## Optional durable format

Projects needing machine-readable coordination can use the
[message schema](agent-mesh.schema.json). For example:

```json
{
  "id": "message-001",
  "missionId": "task-001",
  "waveId": "review-01",
  "lane": "test",
  "from": "coordinator",
  "to": "test-worker",
  "type": "task",
  "status": "planned",
  "summary": "Verify the changed behavior in an isolated fixture.",
  "evidence": [],
  "blockers": [],
  "nextAction": "Run the relevant regression check.",
  "createdAt": "2026-01-01T00:00:00Z"
}
```

The schema's statuses are `planned`, `in_progress`, `blocked`, `needs_review`,
`done`, and `archived`. Use `blocked` for a concrete dependency that prevents
progress, not merely difficult work. `done` requires acceptance evidence.
The example timestamp and identifiers are placeholders.

These describe optional messages, not the canonical task lifecycle. Task status
uses `todo` for planned work and `cancelled` for intentionally stopped work.
Archiving a message or session never changes a task's completion state. Do not
maintain a second task database in the message format.

## Context and promotion

Keep active summaries small. Store durable decisions and sanitized evidence
references rather than full conversation transcripts. Archive superseded work
without erasing the reason for a decision. Do not create persistent memory or
retain private data unless authorized by the active environment and project.
When the project adopts this memory workflow, use
[MEMORY/README.md](../MEMORY/README.md) for checkpoints and reviewed promotion.

Before integrating delegated output, the coordinator checks scope, correctness,
conflicting edits, security implications, and evidence. Existing project release
authorization applies; a worker's success report is not deployment approval.
