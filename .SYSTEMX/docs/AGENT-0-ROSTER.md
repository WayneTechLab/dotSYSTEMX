# Agent 0 roster and CLI provider setup

Agent 0 coordinates the selected project's plan, canonical tasks, delegation,
integration, and acceptance. The read-only `root roster` command gives that
coordinator one navigation view of registered roles and named instances. It
does not activate an agent, choose a provider, run a task, or grant access.
The selected scope's `WORK/TASKS.json`, role registries, Agent Beta records,
and Access Matrix JSON remain authoritative for their own facts.

## Open the roster

From the directory containing `.SYSTEMX`:

```bash
bash .SYSTEMX/SYSTEMX.sh root roster
bash .SYSTEMX/SYSTEMX.sh root roster --actor agent.0
bash .SYSTEMX/SYSTEMX.sh root roster --offset 0 --limit 20
bash .SYSTEMX/SYSTEMX.sh root roster --help
```

On Windows PowerShell, use
`pwsh -File .SYSTEMX/SYSTEMX.ps1 root roster`. A managed installation can use
`systemx run --target "/path/to/project" --offline -- root roster`. Select a
registered child explicitly with
`bash .SYSTEMX/SYSTEMX.sh projects root roster --project NAME`; root commands
otherwise address the outer scope. Use
`bash .SYSTEMX/SYSTEMX.sh projects root roster --help` for that route's options.

The JSON result reports `sourceRevision`, `counts`, bounded `rows` and
`decisions`, `page` offsets, `cliProviderOptions`, and `setupCommands`. A row
names `actorId`, `kind`, `registrationState`, `sourceRecord`, `workspace`,
`providerAlias`, `taskCount`, and `accessDecisionIds`; it also summarizes
reviewed intent, denial, and gap counts. These are pointers for review, not a
second task ledger or a live provider probe. Every row's
`externalRightsVerified` is false. The top-level `identityVerified`,
`accessGranted`, `runtimeStarted`, and `executed` are false. A
`reviewed-intent` decision remains recorded intent. Re-read the roster after
registration, a task change, or a new access decision; a saved response can
become stale.

For a host-owned process that needs several bounded reads, the
[direct I/O guide](TOOLCHAIN-IO.md) shows `service start --stdio` requests for
`roster`, compact `settings`, and unselected `onboard` status. The JSON-lines
session is read-only; reviewed changes use the direct CLI with an explicit
`--apply`.

## Choose the existing role lane

| Lane | Start or inspect through | Boundary |
| --- | --- | --- |
| Agent 0 | `root roster`, `root packet`, and canonical task commands | Coordinates and accepts; a roster row does not dispatch work. |
| Agent X, Y, Z | `roles-init` preview/apply, then each agent's status or policy commands | Registration adds records, not running processes. |
| Agent Alpha | `autobot init` preview/apply; `agenda catalog` for fixed settings | Routes selected reference requests; Agenda choices start `unset`. |
| Agent Beta | `agent-beta setup` and `bot-add` preview/apply | A named BOT/DOT workspace starts offline. |
| Agent1 | `agent-1 setup` preview/apply and advisory `check` | Does not certify device security or install a daemon. |
| Native subagent | The chosen IDE or harness | The host assigns its own runtime identity and permissions. |

The [Access Matrix guide](ACCESS-AND-MAP.md) explains why a
role row or `ACC-` decision cannot establish actual OS, GitHub, IDE, or cloud
permission. The [ROOT contract](../ROOT/SX-MILESTONE.md) describes
task mappings, tool cards, and acceptance without creating another authority.

## Configure multiple CLI providers without merging their identities

The installed `systemx` command manages the template lifecycle. The local
`.SYSTEMX/SYSTEMX.sh` and `.SYSTEMX/SYSTEMX.ps1` launch selected project
record commands. [Codex CLI](https://learn.chatgpt.com/docs/codex/cli),
[Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/overview),
[Grok Build](https://docs.x.ai/build/overview), and
[Muse Code](https://dev.meta.ai/docs/muse-code) are separate external coding
programs, each with its own installation, account, models, permissions, and
cost. GitHub CLI `gh` is separate repository/PR tooling; its presence does not
make it an AI provider. Several CLIs may be installed at once. The roster
does not select, authenticate, or start one.

```bash
bash .SYSTEMX/SYSTEMX.sh agent-y providers
bash .SYSTEMX/SYSTEMX.sh onboard plan --surface cli --provider codex-cli \
  --credential-consumer local-cli --credential-class new
bash .SYSTEMX/SYSTEMX.sh agent-y prepare --help
```

`onboard plan` is a read-only catalog of entry points and credential consumers;
it does not add a provider adapter or grant access. `agent-y providers`
detects installed names, not usable login or permission.
For each bounded Agent Y task, review the exact selected executable, active
account, project scope, Git repository, write paths, timeout, branch/PR policy,
and expected evidence before applying a preparation. Agent Y pins one provider
for that task and checks it again before execution. Native app subagents and
Agent Beta online references have different host/provider boundaries. An
[OpenAI dot](https://learn.chatgpt.com/docs/dots),
[Grok Bot](https://docs.x.ai/grok-bot/overview), or personal
[Muse](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/)
is not the similarly named local CLI; a template reference is not a live
connection. Grok Build remains manual/discovery only until a reviewed Agent Y
adapter exists. Muse Code has a source-tested Agent Y adapter, while a live
account and new-worktree trust check remain unverified. The
roster does not turn an external reference into an Agent Y run. See the
[CLI and tools guide](CLI-TOOLS.md) and
[Agent Y manual](AGENT-Y.md) for the detailed handoff.
