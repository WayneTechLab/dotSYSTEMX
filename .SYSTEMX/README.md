# .SYSTEMX

A reusable project operating standard by Wayne Tech Lab LLC.

Copy this folder into a repository to give people and AI tools a common place
for project context, engineering standards, checks, release preparation, and
handoff. It works alongside the project's chosen language, framework, hosting
provider, and development tools. No application, account, service, or credential
is bundled or provisioned.

For an LLM or returning agent, begin at [START-HERE.md](START-HERE.md). For initial
adoption, read [STANDARD.md](STANDARD.md), then [docs/SETUP.md](docs/SETUP.md).

## Quick start

The documentation works on its own. The optional command tools need Python 3.9+
and use only its standard library. The Bash launchers work on macOS, Linux,
WSL, or Git Bash. On Windows, use `py -3 .SYSTEMX/scripts/systemx.py` with the
same arguments.

From the containing repository:

```bash
bash .SYSTEMX/SYSTEMX.sh validate
bash .SYSTEMX/SYSTEMX.sh doctor
bash .SYSTEMX/SYSTEMX.sh init
bash .SYSTEMX/SYSTEMX.sh
```

`init` creates `.SYSTEMX/project.json` from the example, without overwriting an
existing file. Review and fill it in, then copy the project templates you need
into `.SYSTEMX/project/`. Both config and project documents are intended to be
committed after removing sensitive information.

The original entry point is also available:

```bash
bash .SYSTEMX/WSG-MENU.sh
```

## Contents

| Path | Purpose |
| --- | --- |
| [STANDARD.md](STANDARD.md) | Shared scope, authority, applicability, and completion rules. |
| [START-HERE.md](START-HERE.md) | LLM load order and resume protocol. |
| [GLOBAL/](GLOBAL/README.md) | Context shared by all agents in the current project; optional external standards references. |
| [PLAN/MASTER-PLAN.md](PLAN/MASTER-PLAN.md) | Outcomes, milestones, dependencies, and acceptance boundaries. |
| [WORK/](WORK/README.md) | Canonical task ledger and generated TODO, working-on, blocked, review, done, and cancelled views. |
| [MEMORY/](MEMORY/README.md) | Verified project facts, decisions, lessons, and session continuity. |
| [AGENTS/](AGENTS/README.md) | Agent 0 coordinator, optional worker registry, and each agent's memory. |
| [docs/](docs/) | Setup, development, security, quality, and operations guidance. |
| [AI/](AI/README.md) | AI collaboration, optional delegation, tools, connectors, and recovery. |
| [templates/](templates/) | Project brief, architecture, decisions, tasks, releases, and handoffs. |
| [config/project.example.json](config/project.example.json) | Empty configuration; select your own tools. |
| [scripts/](scripts/) | Dependency-free command runner and folder validator. |
| [tests/test_systemx.py](tests/test_systemx.py) | Isolated regression checks for the command tools. |
| [SOURCE.json](SOURCE.json) | Exact upstream provenance and extraction scope. |
| [LICENSE](LICENSE) | Original MIT license and copyright notice. |

## Commands

| Command | Behavior |
| --- | --- |
| `help` / `--help` | Show usage. |
| `validate` | Check template structure, JSON, local Markdown file links, and removed component references. |
| `doctor` | Report local paths, Git state, configuration, and executable availability; no network calls. |
| `init` | Create project config only when it does not exist. |
| `check` | Validate the template, then execute every configured project check in order. |
| `dev` | Run the configured development command. |
| `build` | Run configured checks, then the build command. |
| `deploy` | Run configured checks, build, and then the deployment command. |
| `menu` or no arguments | Open the interactive menu; EOF exits. |
| `status` | Show recorded work and owners; does not inspect live worker processes. |
| `context --agent agent.0` | Print a bounded packet of shared context, plan, project memory, and selected agent memory. |
| `agent-add agent.1 --role test` | Create a worker role and memory file; does not start a worker. |
| `task-add`, `task-set`, `task-show` | Create, transition, or inspect canonical task records; see [WORK/README.md](WORK/README.md). |
| `refresh-work` | Regenerate status pages after reviewed manual ledger edits or merge resolution. |

Add `--dry-run` to `check`, `dev`, `build`, or `deploy` to print the command plan
without running project commands. Missing commands or empty quality checks fail
with a configuration error instead of reporting a successful project check.

```bash
bash .SYSTEMX/SYSTEMX.sh deploy --dry-run
python3 -B -m unittest discover -s .SYSTEMX/tests -v
```

The shipped template deliberately has no project config. Template validation
can pass before project initialization; project checks and releases cannot.
Project context and task records are also blank: there is no historical backlog
to clear when starting a new project. The Agent 0 role exists so work can begin.
`validate` is a template consistency check, not a security audit or application
test suite. The runner stops on the first failed command and returns its failure.

## Configuration contract

`checks` contains objects with unique `name` values and nonempty `command`
arrays. `commands` contains `dev`, `build`, and `deploy` argument arrays. An empty
array means the action is unconfigured. Every command runs from the directory
containing `.SYSTEMX`, regardless of the terminal's current directory.

For example, in a project that already defines these npm scripts:

```json
{
  "schemaVersion": 1,
  "project": { "name": "example-project", "description": "Project purpose" },
  "checks": [
    { "name": "lint", "command": ["npm", "run", "lint"] },
    { "name": "tests", "command": ["npm", "test", "--", "--run"] }
  ],
  "commands": {
    "dev": ["npm", "run", "dev"],
    "build": ["npm", "run", "build"],
    "deploy": ["bash", "scripts/deploy-project.sh"]
  }
}
```

This is an illustration, not an installed stack. A Python, Swift, Go, Rust,
documentation, or infrastructure project can supply its own commands. Commands
are argument arrays, not shell expressions: `&&`, redirects, `$VARIABLE`, and
globs are not expanded. Use a reviewed project script when orchestration is
needed. Commands inherit the current environment; keep credentials there or in
a secret manager, never in command arguments or the JSON file.

Review a downloaded template and its project commands before executing them.
Configuration is trusted executable project input, not a sandbox. `deploy` is
an explicit action; its configured script must enforce the chosen target,
authentication, release authorization, and rollback requirements described in
[operations](docs/OPERATIONS.md).

## Adopting and updating

Copy the complete hidden folder, including this license, into the destination
repository. Inspect an existing `.SYSTEMX` before combining it with a new
version; compare and merge changes without overwriting local configuration or
project records. Keep `.SYSTEMX` outside public build and deployment artifacts.
Its ignore rules apply only inside this folder; configure the host repository's
secret and build ignores separately.

This is a curated derivative of the
[upstream template](https://github.com/WayneTechLab/SFWA-WTL-TEMPLATE/tree/c3e2272efe7d9fe3fde1add3144aab3ec6e487c4/.SYSTEMX).
It has its own [version](VERSION) and [changelog](CHANGELOG.md). Copying this
folder does not link a Git remote, create hooks, install dependencies, or establish
production readiness.
