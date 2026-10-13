# CLI and tools guide

Use one reviewed command entry point and one explicitly selected record scope.
The canonical outer folder is **`.SYSTEMX`**. A registered child stores its
records at **`.SYSTEMX/Projects/Project-A/.SYSTEMXP`** and reuses the outer tools
and selected defaults. `.SYSTEMXP` is a record scope, not another installation.

## Choose the entry point

| Entry point | Purpose | Target and execution boundary |
| --- | --- | --- |
| External `systemx` CLI or reviewed `manager.py` | First run, install/update, version policy, audit, export, uninstall/restore | `--target` is the directory containing the outer `.SYSTEMX`; keep this tool outside the target for lifecycle work |
| `systemx run --target PATH --offline -- COMMAND` | Root record commands and explicitly configured project actions | Requires a managed installation; verifies and runs its selected default snapshot |
| `systemx projects --target PATH -- COMMAND` | Registered `.SYSTEMXP` record and role commands | Uses the same managed runner; defaults to offline; the target remains the outer containing directory |
| Local `SYSTEMX.sh` / `SYSTEMX.ps1` | Commands from a reviewed copied folder or managed installation | Folder-only copies run their reviewed local tools; managed installations use their verified selected cache |
| Python `systemx.run(...)` / `systemx.projects(...)` | Integration in an existing Python application | Returns `subprocess.CompletedProcess`; the caller owns import trust, permissions, and error handling |
| Git, `gh`, and a selected installed CLI provider | Optional Agent Y repository work and owned draft PR operations | Separate external tools with their own installation, authentication, costs, and host-account access |

The installed console command is convenient when its Python environment is
trusted. For an untrusted current directory or Python import path, call your
reviewed environment's Python as `python -I -B -m systemx ...` from the initial
start. See [library installation](LIBRARY.md) and [first-time setup](FIRST-RUN.md)
for platform-specific paths and the reusable `systemx` shell function.

`--offline` suppresses the manager's optional startup release check. It does
**not** prohibit network access by an explicitly configured project command,
an Agent Y provider, Git, or `gh`. Direct `systemx projects` defaults to this
offline behavior; `--online` permits the separately opted-in startup check.
Neither mode selects or downloads new defaults during command startup.

## Required and optional tools

| Tool | When it is needed | What setup does |
| --- | --- | --- |
| Python 3.9+ standard library | Optional SYSTEMX command and library operations | The template requires it; it does not install Python |
| Bash or PowerShell | The corresponding local launcher | Launches the reviewed Python tools; documentation also works without a shell |
| Git | Git-based package installation and Agent Y worktrees/branches | No application repository or Git configuration is created automatically |
| GitHub CLI `gh` | Agent Y operations that inspect or write its assigned GitHub PR | Uses the user's existing authorized GitHub account; role activation supplies no credentials |
| Codex, Copilot, or explicitly configured provider CLI | A selected Agent Y execution task | Must already be installed and authorized; preparation detects and pins the chosen executable |
| Project build/test/deploy tools | Commands the project owner configures | SYSTEMX stores reviewed argument arrays; it does not infer or install the application's stack |
| Drive/cloud client or connector | Authorized transport of records and evidence | A URL identifies a location; no connection, sharing change, or synchronization is created by these records |

Agent Y's provider discovery reports installed CLI names and paths; it is not a
model capability, authentication, or service-health check. Choose a provider per
task. A configured provider must use a reviewed executable and explicit argument
array. The app or IDE's native subagents and an external CLI have separate
contexts, runtime IDs, and permissions. See [Agent Y](AGENT-Y.md) for the exact
packet, executable identity, timeout, evidence, and PR gates.

## Root workspace commands

These examples assume a managed installation and a reviewed external `systemx`
command. Replace `/path/to/workspace` with the **containing directory**, not
`/path/to/workspace/.SYSTEMX`.

```bash
systemx status --target "/path/to/workspace"
systemx run --target "/path/to/workspace" --offline -- validate
systemx run --target "/path/to/workspace" --offline -- doctor
systemx run --target "/path/to/workspace" --offline -- context --agent agent.0
systemx run --target "/path/to/workspace" --offline -- tools-guide
```

Manager `status` reports the selected installation version and policy. Runtime
`status`, invoked through `run`, reports root task and focus records. `doctor`
reports available configured command executables; it does not authenticate
providers or prove an application's correctness. `tools-guide` prints this
guide. The interactive local menu offers it as **option 18**.

To use a reviewed folder-only copy directly, run the launcher from the containing
directory. Managed launchers select their verified cache; malformed or missing
managed state must be repaired through reviewed tools, never used as a reason
to bypass verification.

```bash
bash .SYSTEMX/SYSTEMX.sh tools-guide
bash .SYSTEMX/SYSTEMX.sh context --agent agent.0
```

```powershell
& .\.SYSTEMX\SYSTEMX.ps1 tools-guide
& .\.SYSTEMX\SYSTEMX.ps1 context --agent agent.0
```

Execute a local launcher only after reviewing and trusting its checkout. A
manifest or installation record inside an untrusted folder is not independent
proof of origin. External manager `run` refuses unmanaged targets; its behavior
is deliberately different from explicitly executing a trusted copied folder.

## `.SYSTEMXP`: one outer toolchain, separate project records

Create two blank scopes only when you intend to track them. Creation previews
without `--apply`; existing destinations are never replaced.

```bash
systemx projects --target "/path/to/workspace" -- list
systemx projects --target "/path/to/workspace" -- add Project-A --kind software
systemx projects --target "/path/to/workspace" -- add Project-A --kind software --apply
systemx projects --target "/path/to/workspace" -- add Project-B --kind research --apply
systemx projects --target "/path/to/workspace" -- context --project Project-A --agent agent.0
systemx projects --target "/path/to/workspace" -- status --project Project-A
```

The compatible longer form remains available:

```bash
systemx run --target "/path/to/workspace" --offline -- projects context --project Project-A --agent agent.0
bash .SYSTEMX/SYSTEMX.sh projects context --project Project-A --agent agent.0
```

Every scoped record command requires `--project NAME` or `--root`. There is no
remembered current project. `list` reads registered identities; `add` creates a
new scope; `validate` without a selector checks root and all registered scopes.
Ordinary top-level `context`, `status`, and task commands address root records.

```text
workspace/                                      external CLI --target
└── .SYSTEMX/                                   one installation/defaults pin
    ├── GLOBAL/ PLAN/ WORK/ AGENTS/ MEMORY/       root workspace records
    ├── scripts/ config/ docs/ templates/        shared tools and blank seeds
    └── Projects/
        ├── REGISTRY.json                       explicit names and record paths
        ├── Project-A/                          configured child command CWD
        │   ├── code/                           optional working files
        │   └── .SYSTEMXP/                      Project-A records only
        │       ├── GLOBAL/ PLAN/ WORK/ MEMORY/
        │       ├── AGENTS/ EVENTS/ REVIEWS/      optional roles after activation
        │       ├── SOURCES.json SYNC/
        │       └── project.json                Project-A check/build/deploy args
        └── Project-B/
            └── .SYSTEMXP/                      independent ledger and memory
```

All children share the outer default version and update policy. Updates retain
existing child records, adopted policies, code, and prior files. No child has a
second `.SYSTEMX`, independent cache, or recursive Projects tree. Agent Y jobs,
Agent X events, and Agent Z reviews belong to the same selected scope as the
assigned task. `Project-A:TASK-001` and `Project-B:TASK-001` are different tasks.
Root records coordinate cross-project dependencies; they do not silently combine
the child ledgers. See [SYSTEMX PROJECTS](PROJECTS.md).

## Activate and inspect child roles

```bash
systemx projects --target "/path/to/workspace" -- roles-init --project Project-A
systemx projects --target "/path/to/workspace" -- roles-init --project Project-A --apply
systemx projects --target "/path/to/workspace" -- agent-x due --project Project-A
systemx projects --target "/path/to/workspace" -- agent-y providers --project Project-A
systemx projects --target "/path/to/workspace" -- agent-z policy --project Project-A
```

Activation creates missing role records while preserving existing ones. It does
not launch models, install providers, schedule work, accept tasks, or grant
GitHub access. Agent 0 owns the scoped plan and acceptance. Agent X records
events/time. Agent Y carries an explicit task into a selected external CLI and
optional draft PR lane. Agent Z applies the versioned review policy to matching
evidence. An Agent Y PR may trigger the target repository's workflows or
webhooks; review those effects before opting in.

For application checks, edit only known command arrays in the selected child's
`project.json`. Then preview the configured plan:

```bash
systemx projects --target "/path/to/workspace" -- check --project Project-A --dry-run
systemx projects --target "/path/to/workspace" -- check --project Project-A
```

Child `check`, `dev`, `build`, and `deploy` commands execute from
`.SYSTEMX/Projects/Project-A/`, **not** from `.SYSTEMXP`. Use paths relative to
that working directory, such as `code/`, or a deliberately reviewed absolute
script path. `SOURCES.json` references never redirect the working directory or
fetch a repository. Command arrays execute without shell expansion; put
pipelines in an explicit project script.

## Handoffs and operating limits

Export one reviewed scope for a new chat without uploading it:

```bash
systemx export-chat --target "/path/to/workspace" --project Project-A --output "/path/to/new-project-a-packet.md"
```

The output must be a new file and may contain private project facts. Review it
before sharing. Drive/cloud URLs and chat references remain metadata until an
authorized connector or sync client provides transport. Assign one writer per
scope and verify saved revisions before handing ownership to another session.
Local coordination locks do not serialize remote Drive copies.

Scope routing, worktrees, allowed-path checks, and PR gates are workflow controls,
not an OS sandbox. External CLIs and configured application commands have their
host account's filesystem/network access. For untrusted workers, use an isolated
OS identity or container without controller credentials or `.SYSTEMX` write
access. This alpha's Agent Y native Windows `run --apply` fails closed because
descendant process termination is unverified there; core record tools and
PowerShell launchers remain available.

Use [installation/update](INSTALLATION.md) and [uninstall/restore](UNINSTALL.md)
for reversible lifecycle operations and receipts. A whole-installation backup
includes the complete Projects tree, including working code stored there. Use
[evidence and acceptance](EVIDENCE.md) to distinguish valid records, local
application checks, and verified live outcomes.
