# .SYSTEMX

**A portable operating standard for human and AI-assisted projects.**

.SYSTEMX gives people and LLMs a shared structure for project context, master
planning, task tracking, evidence, and durable memory. Start in a repository,
a working directory, a Google Drive folder, or a chat, using the same `.SYSTEMX`
format throughout.

**Keep the exact folder name `.SYSTEMX` on every platform.** Setup can add an
optional lowercase compatibility link so `.systemx` reaches the same directory.
[Exact casing and alias setup](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Exact-Case-and-Alias)
explains filesystem behavior and safe handling of existing conflicts.

[Use this template](https://github.com/WayneTechLab/dotSYSTEMX/generate) ·
[Setup guide](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Getting-Started) ·
[Documentation](https://github.com/WayneTechLab/dotSYSTEMX/wiki) ·
[MIT license](.SYSTEMX/LICENSE)

## Choose your workspace

| Location | Setup |
| --- | --- |
| Repository or VS Code project root | [Project setup](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Setup-Project) |
| Windows, macOS, or Linux working directory | [Directory setup](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Setup-Directory) |
| Google Drive project folder | [Google Drive setup](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Setup-Google-Drive) |
| LLM chat with attachments or authorized file tools | [Chat setup](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Setup-LLM-Chat) |

The profiles share one format. Each project keeps its own context, tasks,
version selection, and memory. Drive uses locally available regular files and
Drive's synchronization; chat uses an explicit context export or writable tools.

## Get started

Use the GitHub template button, or install the command and library into your
chosen Python environment:

```bash
python -m pip install "git+https://github.com/WayneTechLab/dotSYSTEMX.git"
systemx install --target "/path/to/project" --profile project
systemx run --target "/path/to/project" -- context --agent agent.0
```

From a reviewed checkout or extracted template, no package installation is needed:

```bash
bash .SYSTEMX/INSTALL.sh --target "/path/to/project" --profile project
```

Windows users can use `.SYSTEMX\INSTALL.ps1` with the same flags or invoke
`py -3 -B .SYSTEMX\manager.py install`. The optional command tools require
Python 3.9+ and use its standard library. Documentation can be used on its own.
For exact release pins, interpreter setup, and package installation, follow
[Installation and updates](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Installation-and-Updates)
and [Library integration](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Library-Integration).

## A clear place for each responsibility

| Responsibility | .SYSTEMX provides |
| --- | --- |
| Project understanding | Shared context, constraints, terminology, and authoritative references |
| Master planning | Outcomes, milestones, dependencies, and acceptance criteria |
| Work tracking | One task ledger with generated TODO, WORKING-ON, BLOCKED, REVIEW, DONE, and CANCELLED views |
| Current focus | An objective and pointers to existing tasks and checkpoints |
| Agent coordination | Agent 0 ownership, scoped worker assignments, and acceptance review |
| Memory | Verified project facts, individual agent notes, and session checkpoints |
| Delivery | Explicit project commands and reusable quality, security, and operations guidance |

Records start blank, with only the `agent.0` coordinator role. Your project
supplies the requirements, tools, commands, and evidence. Registering a worker
does not start a process or grant additional authority.

Begin at [.SYSTEMX/START-HERE.md](.SYSTEMX/START-HERE.md). In a managed installation,
that entry point explains how to load the selected defaults alongside the active
project's records. “Global” means shared within that project, with explicit
references for any organization-wide standards.

## Updates that preserve your work

Managed installs begin with a version pin and manual updates. Each update adds
a separate set of default files and creates only missing project files.
**Existing files, local folders, customizations, task history, and earlier
releases are preserved.** Select a newer default version per project when ready.

Automatic updates are optional and run only when the managed launcher starts.
They do not create background OS jobs. The [update guide](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Installation-and-Updates)
explains pins, offline use, retained defaults, and compatibility checks.

## Documentation

- [Standard format](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Standard-Format)
- [Agent 0 and subagents](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Agent-0-and-Subagents)
- [Planning and memory](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Planning-and-Memory)
- [Task workflow](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Task-Workflow)
- [Evidence and acceptance](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Evidence-and-Acceptance)
- [Command reference](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Command-Reference)
- [Versions and changelog](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Versions-and-Changelog)
- [Contributing](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Contributing)

.SYSTEMX defines a project operating convention. Project quality and delivery
readiness come from the acceptance criteria, configured checks, and verified
evidence of each adopted project. Keep private records out of public exports.

## Project and license

Maintained by **[Wayne Tech Lab LLC](https://github.com/WayneTechLab)** and released
under the [MIT License](.SYSTEMX/LICENSE).

The standalone template is derived from the operating folder in
[SFWA-WTL-TEMPLATE](https://github.com/WayneTechLab/SFWA-WTL-TEMPLATE).
[Source provenance](.SYSTEMX/SOURCE.json) records the extraction scope.
Retain the license and attribution when copying or redistributing the folder.
