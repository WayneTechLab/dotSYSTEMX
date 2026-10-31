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
| `service start --stdio` | Agent 0, Agent1, settings, and onboarding reads through a host-owned pipe | Fixed bounded JSON-lines methods; no write method, MCP/ACP server, or native IDE extension |
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
| Codex CLI, Copilot CLI, or a reviewed configured CLI | A selected Agent Y execution task | Must already be installed and authorized; preparation detects and pins the chosen executable |
| Muse Code CLI | A selected Agent Y task after provider-owned trust and sign-in | Adapter is source-tested; a live Muse run remains unverified |
| Grok Build CLI | Provider-specific onboarding and manual work | Discovery is a local name check; this beta has no Agent Y Grok execution adapter |
| Kiro CLI and six other documented coding CLIs | Optional provider-specific onboarding and manual work | Catalog discovery does not add an Agent Y execution adapter; review each CLI's login, tool approval, and Git behavior |
| Codex SDK, Kiro IDE/Web, and AWS CLI | Application, IDE, cloud-agent, and AWS account setup | Each has separate host or provider authority; AWS CLI is infrastructure tooling, not an Agent Y coding provider |
| Project build/test/deploy tools | Commands the project owner configures | SYSTEMX stores reviewed argument arrays; it does not infer or install the application's stack |
| Drive/cloud client or connector | Authorized transport of records and evidence | A URL identifies a location; no connection, sharing change, or synchronization is created by these records |

Agent Y's provider discovery reports installed CLI names and paths; it is not a
model capability, authentication, or service-health check. Choose a provider per
task. A configured provider must use a reviewed executable and explicit argument
array. The app or IDE's native subagents and an external CLI have separate
contexts, runtime IDs, and permissions. See [Agent Y](AGENT-Y.md) for the exact
packet, executable identity, timeout, evidence, and PR gates.
Agent 0's read-only `root roster` is a different view: it lists selected-scope
role and instance records with setup pointers. It does not install, select,
authenticate, or launch any of those CLIs. See the
[Agent 0 roster guide](AGENT-0-ROSTER.md).

## First-time provider and credential plan

`onboard status` and `onboard plan` read the selected scope, Agent1 setup state,
Agent 0 roster, and a fixed provider catalog. They do not authenticate a
provider, run a model, install a service, create a secret, or choose a provider
for Agent Y. `--env-file PATH` explicitly asks Agent1 to inventory a contained
dotenv file's key names; values are not returned. The five plan questions can
be supplied through `--account-context`, `--surface`, `--provider`,
`--credential-consumer`, and `--credential-class`. Omitted provider, surface,
account, and consumer answers stay unset. With a selected consumer, the plan
proposes `new` for the credential class unless `none` or `existing-test` is
given; it does not create a key.
Human-readable text is the default; `--format json` returns the same bounded
data for callers that need structured fields. Prefer the precise
`vscode-terminal`, `vscode-extension`, `codex-ide`, `ide`, `sdk`, or `cloud`
surface over the broad `vscode` and `codex` aliases when the actual entry
point is known. An application that consumes a credential can select
`--credential-consumer server-application`; this records a plan, not a secret
destination or a running service.

```bash
systemx run --target "/path/to/workspace" --offline -- onboard status
systemx run --target "/path/to/workspace" --offline -- onboard plan \
  --account-context enterprise --surface vscode-extension --provider codex-ide \
  --credential-consumer vscode-extension --credential-class new
systemx projects --target "/path/to/workspace" -- onboard plan --project Project-A \
  --surface cli --provider codex-cli --credential-consumer local-cli
systemx run --target "/path/to/workspace" --offline -- onboard plan \
  --surface sdk --provider codex-sdk --credential-consumer server-application
systemx run --target "/path/to/workspace" --offline -- onboard bridge
```

`onboard bridge` previews a single fixed project-root `AGENTS.md` pointer to
`.SYSTEMX/AGENTS.md`. To create it only when absent, repeat with `--apply
--expected-sha256` set to the preview's `contentSha256`. An existing file,
link, or directory is a preserved conflict. Preview works on Windows; apply
requires anchored POSIX directory operations and fails closed on native
Windows in this beta. The pointer gives compatible
tools a path to reviewed guidance; it does not alter a host's instruction
hierarchy or grant tool access.

| Catalog choice | Runtime lane in this template | External product boundary |
| --- | --- | --- |
| `codex-cli` | Agent Y task handoff | [Codex CLI](https://learn.chatgpt.com/docs/codex/cli) is an independently installed terminal coding agent with its own sign-in. |
| `codex-ide` | Host IDE | The [Codex IDE extension](https://learn.chatgpt.com/docs/codex/ide) runs in its host; `agent-y` does not launch it. |
| `codex-sdk` | Host application | The [Codex SDK](https://learn.chatgpt.com/docs/codex-sdk) is an application-managed TypeScript or Python integration, distinct from Codex CLI, the IDE extension, and OpenAI dots; Agent Y has no SDK adapter. |
| `openai-dot` | Agent Beta offline reference | An [OpenAI dot](https://learn.chatgpt.com/docs/dots) is a separate cloud agent; a local record is not its connection or login. |
| `grok-build` | Manual/discovery; no Agent Y execution adapter yet | [Grok Build](https://docs.x.ai/build/overview) is xAI's `grok` coding CLI; [CLI reference](https://docs.x.ai/build/cli/reference) documents its own login and inspect commands. |
| `grok-bot` | Agent Beta offline reference | [Grok Bot](https://docs.x.ai/grok-bot/overview) is a separate persistent cloud Bot product. |
| `muse-code` | Agent Y task handoff | [Muse Code](https://dev.meta.ai/docs/muse-code) is Meta's `muse` terminal coding agent. This beta has a reviewed adapter, but a live Muse run and fresh-worktree trust remain unverified. |
| `meta-muse` | Agent Beta offline reference | [Personal Muse](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/) is a separate personal agent. [Meta Model API](https://dev.meta.ai/docs/overview) is an API for building applications, not Muse Code or a personal Muse session. |
| `kiro-cli` | Manual/discovery; no Agent Y execution adapter yet | [Kiro CLI](https://kiro.dev/docs/cli/) supersedes the Amazon Q Developer CLI [name](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/upgrade-to-kiro.html). Its own sign-in, workspace trust, sandbox, and tool approvals govern manual use. |
| `kiro-ide` | Host IDE | [Kiro IDE](https://kiro.dev/docs/getting-started/installation/) owns its editor session and sign-in; the CLI entry does not start it. |
| `kiro-web` | Agent Beta offline reference | [Kiro Web](https://kiro.dev/docs/web/setup/) has separate account and GitHub app repository access; a local Bot record is only a reference. |
| `aws-cli` | Host account/infrastructure tool | [AWS CLI IAM Identity Center profiles](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html) are selected and signed in by the user. `aws` is not an Agent Y coding provider and its account authority is separate from Kiro. |
| `claude-code` | Manual/discovery; no Agent Y execution adapter yet | [Claude Code CLI](https://code.claude.com/docs/en/cli-reference) uses `claude` and its own [identity settings](https://code.claude.com/docs/en/iam); its VS Code extension is host managed. |
| `opencode-cli` | Manual/discovery; no Agent Y execution adapter yet | [OpenCode CLI](https://dev.opencode.ai/v2/docs/cli) uses `opencode`; version, provider login, and background service behavior need review. |
| `blackbox-cli` | Manual/discovery; no Agent Y execution adapter yet | [BLACKBOX AI CLI](https://docs.blackbox.ai/features/blackbox-cli/commands-reference) uses `blackbox`. Its internal multi-agent branches are outside Agent Y's task and branch ownership. |
| `gemini-cli` | Manual/discovery; no Agent Y execution adapter yet | [Gemini CLI](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/cli-reference.md) uses `gemini`; [Google sign-in, API key, and Vertex AI](https://github.com/google-gemini/gemini-cli/blob/main/docs/get-started/authentication.mdx) are distinct credentials. |
| `cursor-agent` | Manual/discovery; no Agent Y execution adapter yet | [Cursor CLI](https://cursor.com/docs/cli/installation) uses the generic executable `agent`; verify the installed binary's provenance, account, and write permissions before use. |
| `aider` | Manual/discovery; no Agent Y execution adapter yet | [Aider](https://aider.chat/docs/usage.html) uses `aider` and multiple model providers; its [automatic commit behavior](https://aider.chat/docs/config/options.html) needs review before delegation. |
| `copilot-cli` | Agent Y task handoff | [GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli) has its own account and repository authorization. |
| `configured-cli` | Agent Y reviewed adapter | Supply an explicit executable and arguments under [Agent Y's controls](AGENT-Y.md); catalog presence is no compatibility claim. |

These six additional CLI examples are selected for documented command entry
points, not a measured popularity ranking. `onboard` performs only installed
name checks for unique executable names; `cursor-agent` deliberately has no
automatic `agent` probe because that name is generic. No catalog entry invokes
a provider. `agent-y providers` reports only its built-in or explicitly
configured task adapters, which currently cover Codex CLI, Copilot CLI, Muse
Code, and reviewed configured commands.

The [Codex SDK guide](https://learn.chatgpt.com/docs/codex-sdk) documents
`@openai/codex-sdk` for server-side Node.js 18+ and `openai-codex` for Python
3.10+. These are application dependencies, not packages installed by
`.SYSTEMX` or Agent Y executables. `onboard plan --surface sdk` records the
intended host-application lane without choosing a package or account.

The root `AGENTS.md` bridge can provide one shared guide where a tool reads
that file. [Kiro](https://kiro.dev/docs/steering/) and
[OpenCode V2](https://dev.opencode.ai/v2/docs/instructions/) document its use.
[Claude Code](https://code.claude.com/docs/en/memory#agentsmd) support depends
on its version and instruction settings; an existing `CLAUDE.md` can take
precedence. [Gemini CLI](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md)
defaults to `GEMINI.md` and can be configured to read `AGENTS.md`. The bridge
does not rewrite tool-specific files or claim every provider consumes it.

For Muse Code, check `muse --version` and start `muse` interactively in the
selected project to review [workspace trust and authentication](https://dev.meta.ai/docs/muse-code/auth)
under the provider's own account. Agent Y invokes a selected Muse job with
`muse exec` in its isolated worktree and does not forward a Meta credential.
Its source tests do not prove that a new worktree is already trusted or that
a live provider run will complete. `agent-y providers` probes installed
executable names only; `gh` in that output is GitHub PR tooling, not an AI
provider. For a specific
task, its `prepare` and `run` commands apply stricter executable and Git
checks; the active account, model entitlement, cost, and external permissions
still require separate review. An Agent Beta reference never becomes an Agent
Y executable by sharing a product name.

Credential destinations are equally distinct. GitHub CLI
[`gh secret set`](https://cli.github.com/manual/gh_secret_set) supports separate
`actions`, `agents`, `codespaces`, and `dependabot` applications. GitHub says
[Actions secrets are workflow-only](https://docs.github.com/en/code-security/reference/secret-security/secret-types),
and [Copilot cloud agent uses Agents secrets](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/configure-secrets-and-variables).
No GitHub secret is a local `.env` symlink. Agent1's current `env-migrate` writes
only one explicitly selected Actions secret after its own checks; `onboard`
never calls it. Use the provider's sign-in or an approved local credential
store for a local CLI or VS Code extension, and keep any credential value out
of portable `.SYSTEMX` records. A Codex SDK host application uses its own
documented authentication and approved server-side secret destination; the
SDK plan does not inherit a Codex CLI login. For AWS CLI, prefer the
[IAM Identity Center flow](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html)
under a named, human-selected profile. Do not copy static AWS keys into a
project `.env` or portable template record. Kiro sign-in does not imply AWS
resource permission. Agent1 currently offers no AWS Secrets Manager writer.

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

The [AUTOBOT reference tier](AUTOBOT.md) is available through `autobot` and its
`agent-a` alias. Tools can explicitly request a bounded selection under Agent
Alpha; a menu or caller label does not authorize execution. The runtime returns
selected context and request records without starting models or external tools.
`autobot-guide` and `data-guide` print their manuals; local menu option **19**
opens the AUTOBOT guide and option **20** runs the read-only DATA audit.
`root-guide` prints the optional ROOT planning/observation manual; local menu
option **21** opens the same guide.

## Agent Beta, Agent1, Agenda, and local session commands

The beta release adds optional, selected-scope commands. The local menu
offers read-only status, setup previews, Agent1's warning-only All-In-One check,
the update guide, and session settings as options **22–31**. Apply steps remain explicit CLI
commands so their exact target and arguments can be reviewed.

```bash
systemx run --target "/path/to/workspace" --offline -- agent-beta setup
systemx run --target "/path/to/workspace" --offline -- agent-beta setup --apply
systemx run --target "/path/to/workspace" --offline -- agent-beta bot-add EXAMPLE --kind bot
systemx run --target "/path/to/workspace" --offline -- agent-beta bot-add EXAMPLE --kind bot --apply
systemx run --target "/path/to/workspace" --offline -- agent-beta access-link --help
systemx run --target "/path/to/workspace" --offline -- agent-1 status
systemx run --target "/path/to/workspace" --offline -- agent-1 setup
systemx run --target "/path/to/workspace" --offline -- agent-1 check
systemx run --target "/path/to/workspace" --offline -- agenda status
systemx run --target "/path/to/workspace" --offline -- agenda table --format csv
systemx run --target "/path/to/workspace" --offline -- agenda decision-add --help
systemx run --target "/path/to/workspace" --offline -- agenda roles-upgrade --help
systemx run --target "/path/to/workspace" --offline -- agenda workbook-export
systemx run --target "/path/to/workspace" --offline -- agenda workbook-check
systemx run --target "/path/to/workspace" --offline -- service status
systemx run --target "/path/to/workspace" --offline -- session-settings
systemx run --target "/path/to/workspace" --offline -- session-settings --compact
systemx run --target "/path/to/workspace" --offline -- release-counters
```

Agent Beta creates local BOT/DOT records only. To retain an Access Matrix
reference, create the named workspace first, add a `reviewed-intent` decision
for `agentb:BOT_NAME`, then preview `agent-beta access-link BOT_NAME
--access-decision-id ACC-001`. The preview's `revisionBefore` fingerprints
the BOT and matrix; repeat with `--expected-revision REVISION --apply` after
review. The link never verifies identity, grants access, or opens a provider
session. `agent-1 setup` reports unanswered
first-run questions; review personal or enterprise context, repository identity,
owner/operator/guest role, GitHub Actions target, local secret store, and `.env`
history/rotation before applying. `agent-1 check` defaults to All-In-One and
returns warnings with coverage limits. The 400-question policy is an assessment
catalog; a local filename scan does not answer those questions. The setup
role label is descriptive. An applied repository/environment
`env-migrate` requires GitHub's action-time repository admin permission and
reads back only the secret name/scope metadata; organization secret writes are
outside this beta CLI. `agenda` starts
with 20 default-deny role and instance rows, empty decisions, and empty Agenda
options; it never grants external access. `agenda decision-add` records one
reviewed intent, denial, or gap after an `accessRevision` check, and reports
`accessGranted: false`. The checked-in XLSX is a stock view of the role rows;
`agenda roles-upgrade` can add those rows to an adopted legacy scoped matrix
after a revision-guarded preview while preserving existing decisions.
`agenda table --format csv` returns live selected-scope CSV fields within JSON.
`agenda workbook-export` previews a formula-free XLSX under ignored `local/`;
repeat with its `sourceRevision` as `--expected-revision` and `--apply` to
write it. `agenda workbook-check` detects when that view is stale against the
canonical JSON. `service start --stdio` runs an explicit
read-only JSON-lines session under the caller's process lifetime; it installs no
OS daemon. The [Agent 0 direct I/O guide](TOOLCHAIN-IO.md) gives the exact pipe
contract, host routes, and a separate revision-guarded CLI write example.
See [Agent1's policy](../SECURITY/AGENT1/README.md), [service setup](../Setup/SERVICE.md),
and the [Access Matrix](../GLOBAL/ACCESS-MATRIX.md).

For an existing Agent1 setup, preview a proposed change with all eight setup
answers: `--account-context`, `--repo`, `--review-scope`, `--actor-role`,
`--secret-target`, `--local-secret-store`, `--env-history-reviewed`, and
`--rotation-decision`. Review `proposed` and `existingSHA256`, then repeat the
full command with `--apply --replace-existing --expect-sha256 SHA_FROM_PREVIEW`.
Missing answers or a changed record stop replacement. On native Windows,
metadata-only first setup, `status`, `questions`, and warning-only `check` are
available; `env-inventory`, `env-sanitize`, `env-migrate`, `review --answers`,
and existing-setup reconfiguration fail closed because anchored file-handle
operations are unavailable. No Windows Agent1 service is installed.

`session-settings` combines selected-scope Agent Beta, Agent1, and Agenda
status with fixed AUTOBOT and registered Beta Rules file paths and SHA-256
hashes. It returns no rule text, secret, account, permission grant, or provider
state. `--compact` returns a rule count and revision digest in place of the
per-file path/hash list. A child requires
`projects session-settings --project NAME`.

For the public template repository, the optional read-only
`release-counters` command and standalone
[`release_counters.py`](../scripts/release_counters.py) report GitHub published
software/media release counts and deployment records separately. It queries on
demand, reports the observation time, and returns `unknown` if a provider read
fails. It neither deploys an application nor creates a persistent counter. See
the [counter guide](RELEASE-COUNTERS.md). From a reviewed folder-only checkout,
run `python3 -I -B .SYSTEMX/scripts/systemx.py release-counters
--repository OWNER/REPO`. Local menu option **32** opens the default repository
counter on demand.

For first run, update, uninstall, and restore, use the external manager commands
with an explicit `--target`. A copied folder cannot safely update or uninstall
itself while its own files are in use. The [installation guide](INSTALLATION.md)
and [uninstall guide](UNINSTALL.md) remain the lifecycle authorities. The menu's
option **30** opens the update guide and option **14** opens the uninstall guide.

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
        │       ├── ROOT/                        optional plan and task-state mappings
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

## Optional ROOT planning and task delta

ROOT adds selected-scope operating rules, request/plan references, task-surface
mappings, local observations, and bounded tool cards. It preserves the existing
Master Plan and canonical task ledger. Use the selected defaults' tools and
preview mutations before adding `--apply`:

```bash
systemx run --target "/path/to/workspace" --offline -- root init
systemx run --target "/path/to/workspace" --offline -- root init --apply
systemx run --target "/path/to/workspace" --offline -- root status
systemx run --target "/path/to/workspace" --offline -- root roster
systemx run --target "/path/to/workspace" --offline -- root delta --layer harness --layer bot
systemx run --target "/path/to/workspace" --offline -- root packet --limit 5
systemx projects --target "/path/to/workspace" -- root init --project Project-A
systemx projects --target "/path/to/workspace" -- root init --project Project-A --apply
systemx projects --target "/path/to/workspace" -- root delta --project Project-A --layer harness --layer bot
```

`root request`, `node`, `bind`, `observe`, and `card` each require an explicit
idempotency key and preview by default. `request` captures root/delegated origin;
`node` links planning structure to canonical tasks; `bind` maps actual harness
or bot items; `observe` retains readback evidence and state; `card` describes one
bounded call to an actual available tool. Use each command's `--help` and the
[SX-MILESTONE contract](../ROOT/SX-MILESTONE.md) for current required fields.

`root delta` is read-only. It compares saved observations, not live harness or
cloud services, and leaves missing, stale, unavailable, or divergent state
visible. Source and expected revisions are caller-provided comparison inputs;
they need independent readback from the actual source. Mappings may be
many-to-many, and external completion does not change canonical acceptance.
`root-guide` explains the hierarchy and generic tool-card boundary. These
commands neither execute cards nor install MCP or provider integrations.
The delta defaults to the harness layer and a bounded task selection; repeat
`--layer harness --layer bot` to assess both external surfaces. Excluded layers
remain unassessed. Repeat `--task TASK-ID` to select explicit tasks, rather
than assuming a bounded report covers the whole backlog. `root packet` prepares
a selected coordination packet, capped at ten tasks and 64 KiB, without
dispatching work or loading the entire plan/history.

## On-demand AUTOBOT and local DATA

Use the selected defaults' tools for a specific root or child scope:

```bash
systemx run --target "/path/to/workspace" --offline -- autobot init
systemx run --target "/path/to/workspace" --offline -- autobot init --apply
systemx run --target "/path/to/workspace" --offline -- autobot list
systemx run --target "/path/to/workspace" --offline -- autobot context --bot autobot.tokens
systemx run --target "/path/to/workspace" --offline -- data audit
systemx projects --target "/path/to/workspace" -- autobot init --project Project-A
systemx projects --target "/path/to/workspace" -- data init --project Project-A
```

Agent Alpha activation is separate from X/Y/Z `roles-init`. The fixed panel has
ten named functions plus its coordinator; there is no extra allowance for
running agents. `request` and `complete` preview by default and require explicit
`--apply` for writes. Matching requests/results are reused; changed facts need
an honest current input revision. Neither a request nor a changed file starts
provider execution, research, task acceptance, or a repeated review loop.

`data init` previews missing scaffold; `--apply` adds only missing files.
`data status` and `data audit` inspect effective Git exclusions without payload
ingestion, upload, or deletion. Child commands use `.SYSTEMXP/AUTOBOT` and
`.SYSTEMXP/DATA`, with separate records and shared outer tools. See the
[AUTOBOT manual](AUTOBOT.md) and [DATA manual](DATA.md) for exact file names,
ten-slot catalog, current command arguments, privacy, and evidence boundaries.

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
access. This beta's Agent Y native Windows `run --apply` fails closed because
descendant process termination is unverified there; core record tools and
PowerShell launchers remain available.

Use [installation/update](INSTALLATION.md) and [uninstall/restore](UNINSTALL.md)
for reversible lifecycle operations and receipts. A whole-installation backup
includes the complete Projects tree, including working code stored there. Use
[evidence and acceptance](EVIDENCE.md) to distinguish valid records, local
application checks, and verified live outcomes.
