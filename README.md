# .SYSTEMX

> **ALPHA — USE AT YOUR OWN RISK.** `.SYSTEMX` is experimental and may change daily.
> Interfaces, defaults, and guidance may change before a stable release. Pin a
> reviewed version, keep recoverable backups, and validate it in your own project.
> It is provided without warranty; template checks do not establish production readiness.

**Current release: [`1.6.0-alpha.1`](https://github.com/WayneTechLab/dotSYSTEMX/releases/tag/v1.6.0-alpha.1)** ·
[Alpha release policy](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Release-Policy)

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
[MIT license](LICENSE)

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
python -m pip install "git+https://github.com/WayneTechLab/dotSYSTEMX.git@v1.6.0-alpha.1"
systemx first-run --target "/path/to/project" --profile project
systemx first-run --target "/path/to/project" --profile project --apply
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

The [first-time setup guide](https://github.com/WayneTechLab/dotSYSTEMX/wiki/First-Time-Setup)
walks through an isolated tool environment, setup preview, project facts, and
verification. First run creates configuration only when missing and executes no
project commands.

## Start a new AI chat

Paste the prompt below into your assistant and fill in the project fields. Use
the [New Chat Setup Prompt](https://github.com/WayneTechLab/dotSYSTEMX/wiki/New-Chat-Setup-Prompt)
wiki page for the full instructions, chat-only workflow, and session handoff.

| Entry point | Link |
| --- | --- |
| Project setup | [First-Time Setup](https://github.com/WayneTechLab/dotSYSTEMX/wiki/First-Time-Setup) |
| Chat-only use | [LLM Chat Setup](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Setup-LLM-Chat) |
| Pinned folder-only download | [`.SYSTEMX 1.6.0-alpha.1` ZIP](https://github.com/WayneTechLab/dotSYSTEMX/releases/download/v1.6.0-alpha.1/SYSTEMX-1.6.0-alpha.1.zip) |

<details>
<summary>Copy the new-project setup prompt</summary>

```text
Set up the public .SYSTEMX template for my project, then use it to
coordinate this project's work.

Project name: [PROJECT NAME]
Project folder or workspace: [FULL PATH, OR "CHAT ONLY"]
Initial objective: [WHAT THIS PROJECT SHOULD ACCOMPLISH]

Template: https://github.com/WayneTechLab/dotSYSTEMX
Pinned release: 1.6.0-alpha.1
Setup: https://github.com/WayneTechLab/dotSYSTEMX/wiki/New-Chat-Setup-Prompt

Read the setup guidance and use only the selected release's .SYSTEMX
folder content. Install into MY project; keep its facts, tasks, and
memory out of the public source template.

Inspect existing hidden paths. Use exactly ".SYSTEMX", including the dot
and uppercase letters. Never create a separate ".systemx" folder.
Preserve existing files, records, Git settings, and repository instructions.
If case-conflicting paths exist, explain the conflict before making changes.

With filesystem access, use the selected release's manager to preview
first-run setup, then apply it if there are no conflicts. Keep the version
pinned and updates manual. Leave the optional lowercase alias disabled
unless I request it. Preserve any existing managed version and policy;
use the documented update workflow if a version change is needed.

Follow START-HERE.md. Initialize Global context, the Master Plan, project
memory, current focus, and tasks using only this project's known facts.
Use agent.0 as coordinator and WORK/TASKS.json as the status authority.
Generate status views with the supplied tools. Registering a role does
not authorize starting subagents. Record unknowns instead of inventing them.

Validate the adopted project and report the actual path, selected version,
changes, operation-log location, and next step.

If this is chat-only or you cannot write files, use attached records and
explicit handoff documents. If you cannot open the setup URL, request the
release ZIP or relevant extracted files. Distinguish proposed changes
from saved changes; claim persistence only after a successful write and
readback. Ask for missing project details only when needed to proceed.
```

</details>

A URL provides instructions; it does not grant filesystem access or persistent
memory. Review exported context before sharing it with another chat. The pinned
release keeps setup repeatable while this alpha project continues to change.

## Spend less context on repeated work

A focused `.SYSTEMX` handoff can reduce repeated input tokens and avoidable
searches, planning restarts, and tool calls. Current focus, one task ledger,
bounded resume context, and scoped worker memory help an assistant load the
information needed for the next task instead of repeatedly reading full histories.

Fewer billable tokens can lower usage-based API costs; fewer repeated steps can
save processing time. Results depend on the model, caching, output, tools, and
workflow. **No fixed percentage of token, money, or time savings is guaranteed.**
A fixed-price subscription may gain capacity without a smaller bill. The
[efficiency guide](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Tokens-Cost-and-Time)
explains the mechanisms, an illustrative calculation, and how to measure results.

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

## Setup you can inspect and remove

Installation operations have local logs. `systemx audit --target PATH` checks the
selected project's footprint. Uninstall previews by default; applying it moves
the complete `.SYSTEMX` folder, including your records, to a chosen backup and
writes a verified inventory and removal log. Restore checks that backup before
putting it back. The [uninstall guide](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Uninstall-and-Cleanup)
also covers package removal and manual integrations without removing shared tools.

## Documentation

- [About .SYSTEMX](https://github.com/WayneTechLab/dotSYSTEMX/wiki/About)
- [Technical Guide](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Technical-Guide)
- [Stack Guide](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Stack-Guide)
- [First-Time Setup](https://github.com/WayneTechLab/dotSYSTEMX/wiki/First-Time-Setup)
- [New Chat Setup Prompt](https://github.com/WayneTechLab/dotSYSTEMX/wiki/New-Chat-Setup-Prompt)
- [Standard format](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Standard-Format)
- [Agent 0 and subagents](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Agent-0-and-Subagents)
- [Planning and memory](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Planning-and-Memory)
- [Task workflow](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Task-Workflow)
- [Evidence and acceptance](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Evidence-and-Acceptance)
- [Command reference](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Command-Reference)
- [Versions and changelog](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Versions-and-Changelog)
- [Contributing](CONTRIBUTING.md)
- [Support and bug reports](SUPPORT.md)
- [Security reporting](SECURITY.md)

.SYSTEMX defines a project operating convention. Project quality and delivery
readiness come from the acceptance criteria, configured checks, and verified
evidence of each adopted project. Keep private records out of public exports.

## Project and license

Maintained by **[Wayne Tech Lab LLC](https://github.com/WayneTechLab)** and released
under the [MIT License](LICENSE).

The standalone template is derived from the operating folder in
[SFWA-WTL-TEMPLATE](https://github.com/WayneTechLab/SFWA-WTL-TEMPLATE).
[Source provenance](.SYSTEMX/SOURCE.json) records the extraction scope.
Retain the license and attribution when copying or redistributing the folder.
