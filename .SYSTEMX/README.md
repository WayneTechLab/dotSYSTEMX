# .SYSTEMX

> **BETA — USE AT YOUR OWN RISK.** `.SYSTEMX` is a prerelease and may change.
> Interfaces, defaults, and guidance may change before a stable release. Pin a
> reviewed version, keep recoverable backups, and validate it in your own project.
> It is provided without warranty; template checks do not establish production readiness.

[Versions and changelog](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Versions-and-Changelog) ·
[Release policy](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Release-Policy)

**One project operating format, wherever the work lives.**

.SYSTEMX brings shared context, planning, tasks, evidence, and agent memory into
a portable folder. Adopt it in a repository, an OS working directory, a Google
Drive folder, or an LLM chat using the same canonical records.

**The folder name is exactly `.SYSTEMX`.** Keep the leading dot and uppercase
letters. The optional [lowercase alias](docs/EXACT-CASE.md) routes to that folder;
setup refuses independent case variants to protect project records.

[Public overview](https://github.com/WayneTechLab/dotSYSTEMX) ·
[Documentation](https://github.com/WayneTechLab/dotSYSTEMX/wiki) ·
[Setup profiles](config/profiles.json) · [MIT license](LICENSE)

[Media library](MEDIA/README.md): the historical field guide, beta.1 feature
infographics, agent cards, and accessible text companions. Earlier environment
cards remain available in their tagged release history.

[![Current beta lifecycle infographic: exact scope, records, verification and release boundaries.](MEDIA/Infographics/systemx-guide-lifecycle.svg)](MEDIA/Reference/current-visual-guide.md)

The [beta.1 visual guide](MEDIA/Reference/current-visual-guide.md) has four
feature infographics for lifecycle, BOT/DOT workspaces, Agent1 security, and
the Access Matrix, plus one role card for each of Agent 0, X, Y, Z, Alpha,
Beta, and Agent1. Its standalone SVGs have exact vector labels and icons on a
7680 × 4320 canvas. Imagegen illustration inside has 1672 × 941 native pixels;
the 8K canvas is an export size. The text companion preserves a reading-order
explanation without relying on color or image text alone.

The earlier field guide remains a separately labeled historical baseline:

[![.SYSTEMX field guide overview: ROOT, SX-RULES, SX-MILESTONE, observed harness and optional bot TODOs, Agent 0/X/Y/Z, Agent Alpha, ten AUTOBOT functions, DATA, and named .SYSTEMXP scopes.](MEDIA/Infographics/systemx-field-guide-01-overview-4k.jpg)](MEDIA/Reference/systemx-field-guide.md)

[Four-part 4K field guide](MEDIA/Reference/systemx-field-guide.md):
[1 — Overview](MEDIA/Infographics/systemx-field-guide-01-overview-4k.jpg) ·
[2 — Agents and TODO reconciliation](MEDIA/Infographics/systemx-field-guide-02-agent-coordination-4k.jpg) ·
[3 — ROOT planning and AUTOBOT](MEDIA/Infographics/systemx-field-guide-03-autobot-panel-4k.jpg) ·
[4 — Scopes, DATA, and tools](MEDIA/Infographics/systemx-field-guide-04-data-projects-4k.jpg).
The ROOT-inclusive media edition `1.11.0-alpha.3` describes the
`1.11.0-alpha.2` feature baseline. The linked companion provides accessible text,
commands, and authority boundaries. [SX-RULES](ROOT/SX-RULES.md) and
[SX-MILESTONE](ROOT/SX-MILESTONE.md) define the internal coordination contract,
planning, tool cards, and task-state comparisons. Load only the relevant
section for the current task. The [asset record](MEDIA/Reference/ASSETS.json)
distinguishes native image size from the selected 3840 × 2160 exports.

The [CLI and tools guide](docs/CLI-TOOLS.md) maps the external manager, verified
managed runner, reviewed folder-only launchers, Python API, and optional provider
tools. It includes explicit `.SYSTEMXP` selection and the working directory for
child application commands. Print it with `tools-guide` or local menu option 18.
After installation, `onboard status` and `onboard plan` show selected-scope
Agent1 state, an Agent 0 roster summary, provider lanes, and questions about the
credential consumer. A plan does not select, authenticate, or start a provider.
`onboard bridge` previews an optional project-root `AGENTS.md` pointer to the
canonical [.SYSTEMX guide](AGENTS.md); applying it requires a reviewed preview
digest and an absent root file. See [first-time setup](docs/FIRST-RUN.md).

The beta release adds optional [Agent Beta BOT/DOT workspaces](AGENTB/README.md),
[Agent1 security and access review](SECURITY/AGENT1/README.md), and Agent Alpha
[Agenda and Access Matrix settings](docs/ACCESS-AND-MAP.md). The Access Matrix
ships 20 default-deny role rows. Beta.2 also supplies ten fixed
[Agenda setting definitions](AUTOBOT/AGENDA-SETTINGS.json) and
[access decision rules](GLOBAL/ACCESS-DECISION-RULES.json) for a first-time
review. `agenda catalog` reads the allowed values and review requirements.
Project-specific Agenda options and access decisions start empty; stock rows
grant nothing. The [Agent 0 roster](docs/AGENT-0-ROSTER.md) lists selected-scope
roles, named instances, and CLI setup pointers without activating them.
The onboarding catalog distinguishes Codex CLI, IDE, SDK, and OpenAI dots;
Grok Build from Grok Bot; Muse Code from personal Muse; and Kiro CLI, IDE,
and Web from the separate AWS CLI account tool. It also lists six independent
third-party coding CLIs for manual discovery. Provider and credential choices
remain unset in the stock template. Online Bots remain offline Agent Beta
references here. Muse Code has a source-tested Agent Y adapter, while a live
account/worktree run remains unverified. The newly listed CLIs have no built-in
Agent Y execution adapter; use
the [provider guide](docs/CLI-TOOLS.md#first-time-provider-and-credential-plan)
for current execution and credential boundaries.
The [Agent 0 toolchain I/O guide](docs/TOOLCHAIN-IO.md) covers the selected-scope
JSON CLI and opt-in read-only stdio route for VS Code, Codex, Cursor, Kiro,
and JetBrains hosts. Native MCP/ACP registration is not installed.
The [session service](Setup/SERVICE.md) runs only when explicitly
started through a pipe; it installs no OS daemon. The [Setup](Setup/README.md)
and [Uninstall](Uninstall/README.md) directories point to the existing external
manager lifecycle. The original four-part media guide retains its earlier
recorded baseline; the beta feature and agent images are a separate set.
`agent-beta access-link` can retain a same-actor reviewed-intent decision after
a combined BOT/matrix revision check; it never connects or grants access.
An Agent1 repository/environment secret set requires the active GitHub
account's repository admin permission before hidden input and checks only
name/scope metadata afterward; a first-run actor label is descriptive.
The read-only `session-settings` command returns the selected scope's Agent
Beta, Agent1, and Agenda status with bounded canonical Rules file paths and
hashes for an IDE or harness to load without copying rule text into the status.
`session-settings --compact` replaces the per-file list with a count and digest.

## Focused context and reversible setup

Current focus, a single task ledger, bounded context, and scoped agent memory can
reduce repeated input and rework. That can lower usage-based token costs and save
time, depending on model, caching, output, and tools. There is no fixed savings
guarantee; see [tokens, cost, and time](docs/EFFICIENCY.md).

[First-time setup](docs/FIRST-RUN.md) previews before applying changes. Local
operation logs, scoped audits, and a [reversible uninstall](docs/UNINSTALL.md)
make the installation inspectable while retaining your records in a backup.
Read the [Technical Guide](docs/TECHNICAL-GUIDE.md),
[Stack Guide](docs/STACK-GUIDE.md), and [About page](docs/ABOUT.md).

The [current white paper](MEDIA/White-Paper/SYSTEMX-White-Paper.pdf), edition 2.1,
examines the `1.11.0-beta.1` implementation, its new roles and Access Matrix,
task authority, security boundaries, and release evidence. Its five-page PDF
has selectable text and linked navigation. Earlier edition 2.0 examined alpha.4
and remains available at the immutable alpha.5 tag. Token savings remain a
testable proposition, not a measured product claim.
[Editable text](MEDIA/White-Paper/SYSTEMX-White-Paper.md) ·
[Edition metadata](MEDIA/White-Paper/SYSTEMX-White-Paper.json) ·
[Public paper guide](https://github.com/WayneTechLab/dotSYSTEMX/wiki/White-Paper).

## Start here

For work in an active project, load [START-HERE.md](START-HERE.md). For setup,
choose [a project root](profiles/project.md), [an OS directory](profiles/directory.md),
[Google Drive](profiles/drive.md), or [a chat](profiles/chat.md).
The [format contract](FORMAT.md) defines canonical records and ownership.

From a reviewed template folder:

```bash
bash .SYSTEMX/INSTALL.sh --target "/path/to/project" --profile project
```

On Windows use `INSTALL.ps1` or `py -3 -I -B .SYSTEMX\manager.py install` with the
same flags. Python 3.9+ is required for command tools; the documentation works
without a runtime. The [library guide](docs/LIBRARY.md) covers package installation
and the `systemx` command.

For a simple copied folder, the original commands remain available:

```bash
bash .SYSTEMX/SYSTEMX.sh validate
bash .SYSTEMX/SYSTEMX.sh context --agent agent.0
```

Managed installs run their selected versioned defaults through the launcher.
Each project starts pinned with manual updates. An opt-in startup check can
report available releases even while pinned; it never selects one. See
[installation and updates](docs/INSTALLATION.md) for the preservation contract.

## Multiple projects and channels

[SYSTEMX PROJECTS](docs/PROJECTS.md) uses
`.SYSTEMX/Projects/Project-A/.SYSTEMXP` for each child's context, Master Plan,
tasks, status, sources, decisions, and scoped agent memory. Keep one outer
installation; never put another `.SYSTEMX` inside it. The registry ships empty.

```bash
systemx projects --target "/path/to/workspace" -- add Project-A --kind software
systemx projects --target "/path/to/workspace" -- add Project-A --kind software --apply
systemx projects --target "/path/to/workspace" -- context --project Project-A --agent agent.0
systemx projects --target "/path/to/workspace" -- validate --project Project-A
```

The target is the directory containing the outer `.SYSTEMX`; direct `projects`
defaults to offline startup. The compatible `systemx run --target PATH --offline
-- projects ...` and `bash .SYSTEMX/SYSTEMX.sh projects ...` forms remain available;
Windows uses the reviewed `SYSTEMX.ps1` launcher. Omit `--apply` to preview
creation. Existing destinations are never replaced.
Child scopes share the outer version pin; updates preserve all existing project
records and code. Select every scoped command explicitly with `--project NAME`
or `--root`. Referenced repositories and cloud locations are not automatically
connected. Follow the guide for library use, export, and backup/removal boundaries.
Configured child commands execute from `Projects/Project-A/`, not `.SYSTEMXP`.

## Project structure

| Path | Purpose |
| --- | --- |
| [STANDARD.md](STANDARD.md) and [FORMAT.md](FORMAT.md) | Shared operating guidance and canonical record definitions |
| [START-HERE.md](START-HERE.md) and [CURRENT.md](CURRENT.md) | Start/resume protocol and generated current focus |
| [GLOBAL/](GLOBAL/README.md) | Project identity, constraints, and accepted references |
| [PLAN/MASTER-PLAN.md](PLAN/MASTER-PLAN.md) | Outcomes, milestones, dependencies, and acceptance |
| [ROOT/](ROOT/SX-MILESTONE.md) | Optional operating rules, flexible planning structure, and explicit harness/bot state observations |
| [WORK/](WORK/README.md) | Canonical tasks and generated status views |
| [MEMORY/](MEMORY/README.md) | Verified project facts and session checkpoints |
| [AGENTS/](AGENTS/README.md) | Coordinator, registered roles, and scoped agent memory |
| [docs/](docs/) and [AI/](AI/README.md) | Engineering, operations, and collaboration guidance |
| [Projects/](Projects/README.md) | Registered child projects using exact `.SYSTEMXP` record folders |
| [templates/](templates/) | Reusable briefs, decisions, evidence, releases, and handoffs |
| [AUTOBOT/](AUTOBOT/) | Optional ten-function reference panel routed by Agent Alpha on demand |
| [DATA/](DATA/) | Local payload folders, ignored by Git by default except exact scaffold files |
| [config/project.example.json](config/project.example.json) | Empty project command configuration |

The template ships blank project records and only `agent.0`. Agent registration
creates a role and memory file; it does not launch an agent runtime.

## Everyday use

```bash
systemx run --target "/path/to/project" --offline -- status
systemx run --target "/path/to/project" --offline -- task-ready
systemx run --target "/path/to/project" --offline -- context --agent agent.0
systemx run --target "/path/to/project" --offline -- tools-guide
```

Use [the work guide](WORK/README.md) for task creation, dependencies, review, and
current focus. Keep one authoritative ledger; generated views are not separate
editable status lists. [Evidence and acceptance](docs/EVIDENCE.md) describe the
review needed before completion.

## Optional ROOT planning and task-state comparison

[SX-RULES](ROOT/SX-RULES.md) records internal coordination rules within the
active user and environment instructions. [SX-MILESTONE](ROOT/SX-MILESTONE.md)
defines milestone → wave → phase → group → task → subtask → single action.
A wave groups related phases; a phase holds a coherent task list. Skip
unnecessary levels and expand only upcoming work. Counts and worker limits are
project decisions, rather than a requirement to generate a fixed-size tree.

`RTask` captures a request's origin and `STask` a bounded delegation. Plan nodes
reference canonical `TASK-` IDs; independently owned or accepted subtasks also
need their own task records. Status stays in `WORK/TASKS.json`. Optional ROOT
mappings compare that ledger with observed IDE/harness and cloud/bot items,
including one-to-many relationships. Observations retain their scope, revision,
time, and evidence. A read-only delta reports gaps; it does not connect a
provider, execute a tool card, or accept external completion automatically.
Agent 0 reconciles affected items through the actual authorized harness or bot
tools, then reads back and records the changed state. One external item may
cover several task IDs, and one task may have multiple bot attempts. Matching
TODO counts is not required. The bot layer is optional and explicitly selected;
an unassessed layer is not evidence of alignment. A reported `completed` run
still needs normal evidence, review, and Agent 0/user acceptance before the
canonical task becomes `done`. Reconcile on a meaningful change or handoff,
then checkpoint; the format does not require continuous polling or repeat reviews.
Use ROOT only in the selected outer or `.SYSTEMXP` scope, and load a bounded
selection when needed. Follow the [ROOT manual](https://github.com/WayneTechLab/dotSYSTEMX/wiki/ROOT-Planning-and-Task-Delta)
for setup and the full contract.

## Configuration contract

Initialize `.SYSTEMX/project.json` with the project's `init` command. Existing
configuration is never overwritten. The JSON contains `schemaVersion`, a `project`
object with `name` and `description`, a `checks` array, and a `commands` object
with `dev`, `build`, and `deploy` arrays. Checks have unique names and nonempty
command argument arrays. Empty commands are unconfigured.

Commands run from the containing project directory, without shell expansion.
Configured `check`, `build`, and `deploy` actions require checks; failures stop
the sequence. Use an explicit project script for pipelines or other orchestration.
Keep secrets in an appropriate environment or secret manager, not command arguments.
See [quality](docs/QUALITY.md), [security](docs/SECURITY.md), and [operations](docs/OPERATIONS.md).

## Preserve project ownership

Installation and updates add missing root files and versioned default snapshots.
They preserve existing documents, configuration, local directories, and earlier
releases. `INSTALLATION.json` selects the current default version; root copies
can remain older or customized. An updated standard never silently resets work,
merges projects, changes sharing permissions, or grants production authority.

Use [the upgrade guide](docs/UPGRADING.md) when adopting an existing project.
The public [versions and changelog](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Versions-and-Changelog)
contains release details. The folder also retains offline release metadata and
[source provenance](SOURCE.json). Keep the [license](LICENSE) in every copy.

## Standard CLI, event, and review roles

[Agent X](docs/AGENT-X.md) tracks events, time, actors, and due items.
[Agent Y](docs/AGENT-Y.md) takes a bounded Agent 0 task through a selected,
installed CLI provider and can create an opted-in draft PR from its isolated task
branch. It is separate from app/IDE subagents and shares the same project
concurrency and cost budget. Agent 0 still owns acceptance and branch/PR policy.
[Agent Z](docs/AGENT-Z.md) applies the fixed 100-question policy across ten
categories, retains scorecards, and compares revision/evidence deltas. Preview
`roles-init`, then use `roles-init --apply` to enable all three in this scope. For a
child, use `projects roles-init --project NAME --apply`. Activation preserves
existing records. Role setup does not launch workers, install providers, schedule
jobs, accept tasks, or repeat unchanged reviews. The public seed registry stays
Agent 0 only; standard X/Y/Z definitions and blank activation templates are
included. PR ready, close, merge, and branch cleanup have separate gates;
Agent Y never merges automatically.

## Agent Alpha, AUTOBOT, and local DATA

[AUTOBOT](docs/AUTOBOT.md) is the optional second tier for deeper project
references. Its fixed ten slots map to exact files `Design.MD`, `Soul.MD`,
`Memory.MD`, `Rules.MD`, `Research.MD`, `Brand.MD`, `Media.MD`, `Tokens.MD`,
`Data.MD`, and `Archive.MD`. Agent Alpha (`AGENTA`, `agent.a`) is the coordinator
outside that ten-bot limit. Agent 0/X/Y/Z or an explicitly authorized tools call
selects only the functions needed for the current task. Agent 0 retains task
acceptance; file content and caller labels grant no authority.

Preview `autobot init`, then apply it explicitly in the intended root or child
scope. Agent Alpha activation is separate from `roles-init`; blank seeds still
register only Agent 0. Requests fingerprint inputs and selected files and reuse
unchanged results. The runtime does not launch bots, fetch research, or trigger
recursive reviews or rebuilds.

[DATA](docs/DATA.md) provides `TEMP`, `LARGE`, `IMPORTS`, `RESEARCH`, `ASSETS`,
`EXPORTS`, `CACHE`, and `ARCHIVE`. Its payloads are ignored by Git by default;
only the exact `.gitignore` and README scaffold files are intended to be tracked.
`data init` previews missing scaffold, `data status` inspects it, and `data audit`
reports effective Git exclusions and tracked-payload warnings. These commands do
not ingest, upload, or delete payloads. Existing Git history and external sync
tools require separate review.

## Complete projects and shared work

Use the [one-shot project guide](docs/ONE-SHOT-PROJECT.md) to turn a
researched brief into phases, milestones, tasks, execution batches, and accepted
delivery. Use [shared workspaces, clouds, and bots](docs/SHARED-WORKSPACES.md)
for repositories, named `.SYSTEMXP` children, authorized Drive/cloud access,
multi-chat handoffs, and persistent local/VM bot context. The harness supplies
execution and transport; the records preserve the objective, proof, and next step.

Application-specific SDKs, business workflows, provider fixtures, and service
integrations belong in the adopting project. Keep them outside the reusable
base format and connect them through the host project's reviewed tooling.
