# .SYSTEMX

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

On Windows use `INSTALL.ps1` or `py -3 -B .SYSTEMX\manager.py install` with the
same flags. Python 3.9+ is required for command tools; the documentation works
without a runtime. The [library guide](docs/LIBRARY.md) covers package installation
and the `systemx` command.

For a simple copied folder, the original commands remain available:

```bash
bash .SYSTEMX/SYSTEMX.sh validate
bash .SYSTEMX/SYSTEMX.sh context --agent agent.0
```

Managed installs select their versioned defaults automatically through the
launcher. Each project starts pinned with manual updates. See
[installation and updates](docs/INSTALLATION.md) for the preservation contract.

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
| [templates/](templates/) | Reusable briefs, decisions, evidence, releases, and handoffs |
| [config/project.example.json](config/project.example.json) | Empty project command configuration |

The template ships blank project records and only `agent.0`. Agent registration
creates a role and memory file; it does not launch an agent runtime.

## Everyday use

```bash
systemx run --target "/path/to/project" -- status
systemx run --target "/path/to/project" -- task-ready
systemx run --target "/path/to/project" -- context --agent agent.0
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
