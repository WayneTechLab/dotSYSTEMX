# SYSTEMX PROJECTS

Use **`.SYSTEMX/Projects/Project-A/.SYSTEMXP`** to track multiple projects,
channels, research streams, or operating areas under one shared `.SYSTEMX`.
The exact child directory name is **`.SYSTEMXP`**: SYSTEMX PROJECTS. Preserve
uppercase letters and the leading dot. Never install `.SYSTEMX` inside `.SYSTEMX`.

The public template has an empty project registry and blank creation templates.
`Project-A` and `Project-B` below are examples, not preloaded projects.

## Layout and ownership

```text
workspace/
└── .SYSTEMX/                         shared tools, standards, version policy
    ├── GLOBAL/                      workspace-wide context
    ├── PLAN/                        workspace-wide Master Plan
    ├── WORK/                        workspace coordination tasks
    ├── AGENTS/agent.0/               workspace coordinator memory
    ├── Projects/
    │   ├── REGISTRY.json             explicit project identities and paths
    │   ├── Project-A/
    │   │   ├── AGENTS.md             points tools to this project's records
    │   │   ├── code/                 optional working code/files
    │   │   └── .SYSTEMXP/
    │   │       ├── START-HERE.md
    │   │       ├── AGENTS.md
    │   │       ├── CURRENT.md        generated selected focus
    │   │       ├── GLOBAL/CONTEXT.md
    │   │       ├── PLAN/MASTER-PLAN.md
    │   │       ├── WORK/             ledger, focus, six generated state views
    │   │       ├── AGENTS/           registry and per-agent memory
    │   │       ├── MEMORY/           durable facts and dated checkpoints
    │   │       ├── DECISIONS/        project-owned decision records
    │   │       ├── SOURCES.json      explicit code, Drive, chat, document refs
    │   │       ├── SYNC/             optional local status snapshot
    │   │       └── project.json      explicitly configured project commands
    │   └── Project-B/
    │       └── .SYSTEMXP/            separate records with the same structure
    └── templates/project/           blank seeds; never active project memory
```

Keep working code and documents beside `.SYSTEMXP`, or reference an existing
external repository/directory in `SOURCES.json`. No code folder, Git repository,
cloud resource, or remote connection is created automatically. Project records
contain no nested installation, version cache, or recursive `Projects` tree.

The outer Global context and Master Plan describe shared constraints and
cross-project outcomes. Each child has its own context, plan, task ledger, focus,
decisions, and Agent 0 memory. Shared requirements must be explicitly referenced
and reconciled with the selected project's instructions. Do not duplicate whole
transcripts or silently import sibling memory.

## First-time setup

Install or update the outer `.SYSTEMX` using the [installation guide](INSTALLATION.md).
Run these commands from the directory containing that outer folder:

```bash
# Preview without changing files, then create blank local project records.
bash .SYSTEMX/SYSTEMX.sh projects add Project-A --kind software
bash .SYSTEMX/SYSTEMX.sh projects add Project-A --kind software --apply
bash .SYSTEMX/SYSTEMX.sh projects add Project-B --kind channel --apply
bash .SYSTEMX/SYSTEMX.sh projects list
bash .SYSTEMX/SYSTEMX.sh projects context --project Project-A --agent agent.0
```

On Windows use `powershell -File .SYSTEMX/SYSTEMX.ps1` with the same arguments.
The interactive launcher also offers **SYSTEMX PROJECTS guide** and **List projects**.
Supported kinds are `general`, `software`, `research`, `operations`, and `channel`;
they are descriptive labels and do not provision a stack.

Use a portable name of 1–80 ASCII letters, digits, spaces, `_`, or `-`, starting
with a letter and ending with a letter or digit. Quote names containing spaces.
Reserved OS names and `root` are unavailable. Names and paths are case-sensitive
identities even on a case-insensitive disk. There is no child lowercase alias.

Creation refuses any existing destination, duplicate name, linked path, or case
conflict. It never adopts, replaces, merges, or deletes an existing project.
Successful setup writes a receipt under `.SYSTEMX/logs/projects/`. A failed setup
retains any published folder for review and records recovery guidance; inspect
that folder and receipt before retrying. Creation is serialized by the outer
coordination lock. Do not remove a lock until its owner is confirmed stopped.

Fill the selected child's context, Master Plan, memory, and source references
with authorized facts. Its tasks and focus start empty; Agent 0 is the only
registered role. Parent memory is never copied into a new child.

## Daily work and explicit selection

Every scoped work command requires `--project NAME` or `--root`. There is no
persisted implicit current project. Existing top-level commands such as `context`
and `task-add` still address the outer workspace records.

```bash
bash .SYSTEMX/SYSTEMX.sh projects task-add --project Project-A \
  --title "Define the first outcome" --acceptance "Owner reviews the written criteria"
bash .SYSTEMX/SYSTEMX.sh projects focus --project Project-A \
  --objective "Agree the first outcome" --task TASK-001
bash .SYSTEMX/SYSTEMX.sh projects task-set TASK-001 --project Project-A \
  --status in_progress --next "Draft the criteria"
bash .SYSTEMX/SYSTEMX.sh projects task-show TASK-001 --project Project-A
bash .SYSTEMX/SYSTEMX.sh projects context --root --agent agent.0
```

Supported record commands are `context`, `task-add`, `task-set`, `task-show`,
`task-ready`, `task-packet`, `focus`, `agent-add`, and `refresh-work`; use their
existing [work command arguments](../WORK/README.md) plus explicit scope.
Child tasks obey the same dependency, evidence, review, and state transition
rules as root tasks. Edit the ledger through commands where possible; work views
and `CURRENT.md` are generated. `projects refresh-work --project NAME` regenerates
the selected child's views after a reviewed manual record edit.

IDs are local to each scope: both projects may own `TASK-001` and `agent.0`.
Use `Project-A:TASK-001` in cross-project prose or handoffs. JSON `dependsOn`
accepts only task IDs in that same ledger; cross-project dependencies need
explicit coordination tasks and evidence references in the outer plan.

## Agent 0 and subagents

The outer Agent 0 coordinates project boundaries and cross-project handoffs.
Each child's `agent.0` coordinates that child's ledger, integration, acceptance,
and memory. These are scoped role records, not automatically running workers.
A harness may map those roles onto authorized processes; registration does not
launch agents or establish their identity.

An assignment must name the project, task ID, working directory, allowed files,
base revision, acceptance criteria, shared-resource ownership, and return format.
Workers use only the selected child's context and their assigned memory. Route
cross-project work through the outer coordinator; do not let one worker write
both ledgers implicitly. Subagent limits belong to the authorized session or
shared resource budget, not a new automatic allowance for each child.

Example prompt:

> Use the existing outer `.SYSTEMX` and select `Project-A` from
> `.SYSTEMX/Projects/REGISTRY.json`. Read the selected defaults' standard and
> `.SYSTEMX/Projects/Project-A/.SYSTEMXP/START-HERE.md`, then load
> `projects context --project Project-A --agent agent.0`. Resume the accepted
> objective using this child's plan and task ledger. Use subagents only when
> authorized and available in the current harness. Keep assignments, evidence,
> checkpoints, and memory scoped to Project-A. Do not create a nested `.SYSTEMX`,
> import sibling memory, or claim completion without the required evidence.

## Sources, status, and validation

`SOURCES.json` contains exactly `schemaVersion: 1` and `sources: []`. Each source
has `kind`, nonempty `location`, and `description`. Supported kinds are
`repository`, `directory`, `drive`, `chat`, `document`, and `other`:

```json
{
  "schemaVersion": 1,
  "sources": [
    {"kind": "directory", "location": "code", "description": "Relative to Project-A"},
    {"kind": "repository", "location": "https://example.org/team/project", "description": "Reference only"}
  ]
}
```

State the base for relative source paths in the description. References are
metadata: commands never fetch URLs, mount Drive, clone repositories, publish
chat packets, or infer permission from them. Keep credentials out of these files.

```bash
bash .SYSTEMX/SYSTEMX.sh projects status --project Project-A
bash .SYSTEMX/SYSTEMX.sh projects refresh-status --project Project-A
bash .SYSTEMX/SYSTEMX.sh projects refresh-status --project Project-A --apply
bash .SYSTEMX/SYSTEMX.sh projects validate --project Project-A
bash .SYSTEMX/SYSTEMX.sh projects validate
```

`status` reports selected task counts, focus, and source hashes. `refresh-status`
previews a snapshot and writes only the selected `SYNC/STATUS.json` with `--apply`.
It is a local record summary, not network synchronization or runtime health.
Repeated unchanged refreshes do not rewrite the file. Root status lists project
identities; it does not aggregate child tasks or memory. Status snapshots can
become stale after work changes; compare source hashes or refresh explicitly.

`projects validate --project NAME` checks one child's records. Without a selector,
`projects validate` explicitly validates root and all registered children. The
ordinary adopted-workspace `validate` also checks registered records. Validation
does not run application code or establish deployment readiness. Selected context
does not require unrelated siblings' task ledgers to be readable. A malformed
registry must be repaired before routing because project identity is ambiguous.

## Project commands and library use

Configure child checks and command argument arrays in `.SYSTEMXP/project.json`
using the existing [configuration contract](../README.md#configuration-contract).
Its project name must equal the exact registered name. Empty commands remain
unconfigured. Review command provenance before executing them.

```bash
bash .SYSTEMX/SYSTEMX.sh projects check --project Project-A --dry-run
bash .SYSTEMX/SYSTEMX.sh projects check --project Project-A
bash .SYSTEMX/SYSTEMX.sh projects build --project Project-A
```

`check`, `dev`, `build`, and `deploy` run from `Projects/Project-A/`, not from
`.SYSTEMXP` or the repository root. Configure commands to address `code/` if used.
External source references do not redirect execution. Routing is not an OS sandbox;
a configured program has the user's normal filesystem and network permissions.

```python
import systemx

result = systemx.projects("/path/to/workspace", ["list"])
result.check_returncode()  # subprocess.CompletedProcess; stdout contains the result
systemx.projects("/path/to/workspace", ["context", "--project", "Project-A"])
systemx.export_chat("/path/to/workspace", "/path/to/packet.md", project="Project-A")
```

The library runs the installed outer defaults and defaults to offline operation.
Chat export includes shared guidance and only the selected scope's context. Review
the packet before sharing it; it may contain private project facts. See
[library integration](LIBRARY.md) for setup and return types.

## Versions, updates, and removal

All child scopes use the outer installation's selected defaults, version pin,
and update policy. There are no independent child installations or automatic
per-child upgrades. Updates preserve the project registry, existing child
records, code, and working directories. New child creation uses blank seeds from
the selected release. Later default changes do not rewrite existing child records;
apply any documented record migration deliberately after backup and review.

Existing custom `.SYSTEMXP` implementations are not automatically converted.
This registry schema contains exactly `schemaVersion` and `projects`; each entry
contains exactly `name`, `path`, `records`, and `kind`. Paths are relative to the
outer `.SYSTEMX` and must equal `Projects/NAME` and `Projects/NAME/.SYSTEMXP`.
Unknown fields or schemas are rejected without replacing data. Review a mapping
and preserve the original registry before any migration; folder naming alone does
not prove schema compatibility.

Stop all relevant writers before lifecycle changes. Whole-installation
[uninstall and restore](UNINSTALL.md) include **the entire `Projects` tree,
including code stored there**, in the reviewed external backup. Inspect the
preview and backup before removal. External repositories and cloud references
remain outside that operation. There is no individual-project delete command:
archive a child through a deliberate backup and reviewed registry edit, keeping
cross-project references and receipts. Never delete a project just because a new
template release omits it.

## Context efficiency and limits

Selecting one scope helps avoid sending unrelated plans, ledgers, and histories
to the model. Compact status, task packets, and durable checkpoints can reduce
repeated context assembly and drift between projects. Actual token, cost, and time
savings depend on the model and workflow; no fixed savings or throughput are
promised. Record tools may still load a full selected ledger for consistency
checks. See [efficiency](EFFICIENCY.md) and keep archives outside active packets.

This feature provides local scope routing and record consistency. It supplies no
background scheduler, distributed lock, automatic agent runtime, cloud transport,
credential broker, or MCP server. A Drive-synced directory is still local storage;
its sync client does not make concurrent writes safe. Assign one writer per
selected ledger and retain original evidence.

## Standard roles within a child

Use `projects roles-init --project Project-A` to preview Agent X/Z activation,
then add `--apply`. Their records stay in the selected `.SYSTEMXP`. Examples:

```bash
bash .SYSTEMX/SYSTEMX.sh projects agent-x due --project Project-A
bash .SYSTEMX/SYSTEMX.sh projects agent-z policy --project Project-A
```

[Agent X](AGENT-X.md) tracks event/time/schedule facts, while
[Agent Z](AGENT-Z.md) uses the fixed 100-question review policy. Role IDs and
record IDs are scoped; do not compare reports from different projects. Outer
updates preserve each child's adopted policy and history. Merely adding new
defaults does not activate roles or rewrite a child's registry.
