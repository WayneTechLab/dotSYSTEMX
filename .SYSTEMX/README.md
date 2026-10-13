# .SYSTEMX

> **ALPHA — USE AT YOUR OWN RISK.** `.SYSTEMX` is experimental and may change daily.
> Interfaces, defaults, and guidance may change before a stable release. Pin a
> reviewed version, keep recoverable backups, and validate it in your own project.
> It is provided without warranty; template checks do not establish production readiness.

[Versions and changelog](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Versions-and-Changelog) ·
[Alpha release policy](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Release-Policy)

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

[Use-case media library](MEDIA/README.md): ChatGPT + Drive, Codex + GitHub,
Dots / Codex Cloud, and Codex / Copilot CLI on a local drive, with 4K cards
and accessible text guides.

The [CLI and tools guide](docs/CLI-TOOLS.md) maps the external manager, verified
managed runner, reviewed folder-only launchers, Python API, and optional provider
tools. It includes explicit `.SYSTEMXP` selection and the working directory for
child application commands. Print it with `tools-guide` or local menu option 18.

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
| [WORK/](WORK/README.md) | Canonical tasks and generated status views |
| [MEMORY/](MEMORY/README.md) | Verified project facts and session checkpoints |
| [AGENTS/](AGENTS/README.md) | Coordinator, registered roles, and scoped agent memory |
| [docs/](docs/) and [AI/](AI/README.md) | Engineering, operations, and collaboration guidance |
| [Projects/](Projects/README.md) | Registered child projects using exact `.SYSTEMXP` record folders |
| [templates/](templates/) | Reusable briefs, decisions, evidence, releases, and handoffs |
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

## Complete projects and shared work

Use the [one-shot project guide](docs/ONE-SHOT-PROJECT.md) to turn a
researched brief into phases, milestones, tasks, worker waves, and accepted
delivery. Use [shared workspaces, clouds, and bots](docs/SHARED-WORKSPACES.md)
for repositories, named `.SYSTEMXP` children, authorized Drive/cloud access,
multi-chat handoffs, and persistent local/VM bot context. The harness supplies
execution and transport; the records preserve the objective, proof, and next step.
