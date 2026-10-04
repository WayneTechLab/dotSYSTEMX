# Start here: selected project

The exact project marker is .SYSTEMXP: SYSTEMX PROJECTS. It holds this project's
records, while the outer .SYSTEMX owns shared defaults, tools, and version policy.
Never create a nested .SYSTEMX, lowercase duplicate, or recursive Projects tree.

Confirm the explicit project name, record path, source revision, and authorized
scope before work. Read the outer selected defaults' STANDARD.md and PROJECTS
guide, then this project's records:

1. CURRENT.md, generated from the focus and task ledger.
2. [Global context](GLOBAL/CONTEXT.md).
3. [Master Plan](PLAN/MASTER-PLAN.md).
4. [Project memory](MEMORY/PROJECT.md).
5. [Work and acceptance](WORK/README.md).
6. [Agent 0 memory](AGENTS/agent.0/MEMORY.md), or the assigned worker's memory.
7. [Source references](SOURCES.json) relevant to the selected task.

Use the outer launcher with projects and an explicit --project selection.
Task IDs and agent roles belong to this scope; a matching ID elsewhere is a
different record. Root and sibling memories are not automatically inherited.
Recheck volatile evidence before resuming. An empty ledger is not completion.
