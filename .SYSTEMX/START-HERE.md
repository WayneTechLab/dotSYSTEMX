# Start here: load the active project

This is the entry point for an LLM starting or resuming work in a project that
uses SYSTEMX. The template ships with empty project records. Populate them only
with the current project's authorized facts and work; do not carry the template
repository's build history into every new project.

## Read in this order

1. Applicable environment/repository instructions and [STANDARD.md](STANDARD.md).
2. [Global context](GLOBAL/CONTEXT.md): purpose, constraints, source hierarchy,
   shared standards, and references for this project.
3. [Master plan](PLAN/MASTER-PLAN.md): outcomes, milestones, acceptance, dependencies.
4. [Project memory](MEMORY/PROJECT.md): verified durable facts, decisions, lessons,
   and the latest resume checkpoint.
5. [Work overview](WORK/README.md) and the tasks relevant to the current objective.
6. Your assigned agent memory. Agent 0 begins at
   [AGENTS/agent.0/MEMORY.md](AGENTS/agent.0/MEMORY.md).

The command `bash .SYSTEMX/SYSTEMX.sh context --agent agent.0` prints a bounded
resume packet containing these shared records and the selected agent's memory.
`task-show TASK-001` reads the complete record for a particular task. Neither
command starts agents, resumes processes, contacts services, or executes work.

## Resume protocol

- Confirm repository, working tree, branch, and current objective. Recheck
  volatile facts such as active processes, ports, remote revisions, credentials,
  service health, and release state.
- Inspect the existing plan and blockers. Continue from the next incomplete
  accepted step; do not restart planning or broad testing just because the chat
  context changed.
- Agent 0 owns task assignments, integration, shared-memory promotion, and review.
  Read the [coordination contract](AGENTS/README.md).
- A subagent reads its assignment, dependency records, shared context, and its
  own memory. It does not need every other agent's transcript or private notes.
- Before pausing, switching tasks, or losing context, checkpoint facts, evidence,
  exact next action, and unresolved blockers using the
  [memory protocol](MEMORY/README.md).

## Blank versus active

An empty task list means no work has been recorded, not that the project is done.
An agent registry entry is a role record, not proof that a worker is running.
Memory is a versioned project document, not automatic model recall. Each session
must load it through files or its tools. Existing platform memory and instruction
policies still apply.
