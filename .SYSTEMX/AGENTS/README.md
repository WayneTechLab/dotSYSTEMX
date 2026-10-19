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
   Use `task-ready` to find dependency-ready TODO work; choose based on the
   existing plan's priority and shared-resource availability. Do not invent tasks
   merely to fill worker slots.
2. If delegation is authorized and useful, register a stable worker ID with
   `agent-add agent.1 --role test`, then use the available environment to start
   the worker. Registration alone does not spawn it.
3. The worker loads shared context and its own memory with
   `context --agent agent.1`, then confirms the assigned scope.
   `task-packet TASK-001 --base <observed-revision>` provides the existing task,
   dependency states, acceptance criteria, and only its owner's memory. It
   creates no assignment or runtime process. Verify the supplied revision.
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

Reuse an existing worker when its scope and available context still fit. Keep
packets bounded: one concrete requirement or failure, exact files, required
evidence, permitted actions, and a stop condition. An uncertain investigation
should return its observations before the coordinator widens it. Concurrency
depends on the available environment and actual ready work; no fixed model,
worker count, or provider is prescribed by this standard.

Assign one owner for shared resources such as a compiler, test database, browser
session, installer, or deployment target. Record any live job/session handle and
follow it to a terminal result. Parent/coordinator integration includes checking
shared contracts and running relevant combined checks after composing changes.
Repeat tests only when a change, failure, or unresolved concern justifies it.

Each worker gets `AGENTS/<agent-id>/MEMORY.md` from the
[agent memory template](../templates/AGENT-MEMORY.md). Task ownership lives only
in [WORK/TASKS.json](../WORK/TASKS.json); memory links the relevant IDs and captures
the observations needed to resume. Use the
[session checkpoint](../templates/SESSION-CHECKPOINT.md) for longer handoffs.
Use the compact [worker report](../templates/WORKER-REPORT.md) to distinguish
the result, original evidence, limits, and next action. Keep working status in
the task ledger and select project focus with `focus`.

When a worker stops, its role record remains available for historical evidence.
Do not describe a registered worker as active without current runtime evidence.
Do not reuse an old memory file for a different project without deliberate reset.

## Acceptance authority

Only `agent.0` or the project owner (`user`) is recorded as the reviewer for a
completed task. This is a collaboration convention checked by the CLI, not an
authentication or access-control system. Existing production, financial, and
external-action authority remains separate from task completion.

## Standard specialist roles: Agent X, Agent Y, and Agent Z

[Agent X](../docs/AGENT-X.md), ID `agent.x`, owns event/time tracking and due-item
bookkeeping. [Agent Y](../docs/AGENT-Y.md), ID `agent.y`, owns a bounded
user-selected CLI provider handoff and explicitly permitted branch/PR steps.
[Agent Z](../docs/AGENT-Z.md), ID `agent.z`, owns a repeatable 100-question
evidence review. They support the coordinator and never become a second source
of task state or external authority.

Preview role setup before applying it in the selected root or child scope. It
creates blank role memory/records without replacing existing files. The public
seed registry remains Agent 0 only for compatibility with older managed
launchers. X/Y/Z are named standard roles, not numeric subagent slots or
automatic workers.

With these roles enabled, use Agent X for meaningful observed events and due
items. At a task's `needs_review` boundary, use Agent Z once against its original
acceptance and exact source/evidence revision; reuse a matching report. An initial
prompt or intermediate artifact can be reviewed on request. Questions remain
fixed for the policy version, even when some are unknown or justified N/A.
Agent 0 reviews the scorecard, resolves required gaps, and records acceptance.
Further work or repeated checks need changed inputs or a concrete unresolved
concern. A score difference alone does not authorize another build/test loop.

For an authorized CLI task, Agent 0 assigns one repository, base revision,
provider, write scope, and branch/PR policy. Agent Y checks the actual worktree
and provider before starting, retains the process handle, and reports source
changes and original evidence. Agent X can log meaningful observed transitions;
Agent Z reviews the resulting evidence at the requested boundary. A successful
CLI run does not itself complete the task. Draft PR auto-opening is per-task
opt-in. Making it ready, closing an abandoned PR, merging, and deleting its
branch are distinct actions with distinct gates. Closing an unmerged PR needs
recorded cancellation; deleting its branch needs preserved evidence and a fresh
head check. Automated cleanup follows only accepted completion, verified
remote merge, and a retained bundle; a closed unmerged PR keeps its branch.
Merge itself requires separate authority.

## Agent Alpha and the ten AUTOBOT functions

[Agent Alpha](../docs/AUTOBOT.md), ID `agent.a` and display name `AGENTA`, routes
explicit requests from Agent 0/X/Y/Z or Tools to a bounded selection of detailed
project reference files. It is a coordinator outside the fixed ten AUTOBOT slots,
not a second project coordinator or an extra subagent allowance. `autobot init`
previews its separate activation; the public registry remains Agent 0 only.

The panel covers Design, Soul, Memory, Rules, Research, Brand, Media, Tokens,
Data, and Archive. Each name maps to its exact `.MD` file. The runtime records
input/file fingerprints and reuses unchanged requests, including completed
results. Explicit changed inputs or refresh create bounded work; they never
authorize repeated checks, recursive dispatch, provider execution, or task
acceptance. Requests carry caller attribution, not authenticated identity.

Keep current work in `WORK/TASKS.json` and durable facts in `MEMORY/PROJECT.md`.
AUTOBOT working memory and archive records are concise indexes and references.
Large/private material belongs in [DATA](../docs/DATA.md) or an approved store.
Review selected content before including it in worker packets or exports. New
children receive blank records rather than copies of private root or sibling
content. Bot policies remain below the active user/system instructions.
