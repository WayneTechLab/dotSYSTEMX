# First-Time Setup

> **Beta: use at your own risk.** See the [release policy](RELEASE-POLICY.md).

This guide takes a new user from choosing a workspace to a project with a pinned
`.SYSTEMX` installation, empty command configuration, and a clear next step.
It does not install a product stack, fill in invented requirements, or start agents.

## 1. Choose the project and profile

Choose the **containing project directory**, such as `/home/me/projects/example`
or `C:\Projects\Example`. Use the exact `.SYSTEMX` name beneath it. Inspect
existing hidden files before adoption; do not copy over existing records.

| Profile | Choose it for |
| --- | --- |
| `project` | A repository or VS Code project root |
| `directory` | Another Windows, macOS, or Linux working directory |
| `drive` | A locally available regular-file Drive project folder |
| `chat` | A local project used to prepare a reviewable LLM chat packet |

Use `systemx setup --profile project` for the corresponding setup URL. Cloud
URLs are not local filesystem targets. Browser-only Drive and chats follow the
profile guides and explicit upload/readback workflows.

## 2. Choose a tool entry point

Documentation alone needs no runtime. For commands, install Python 3.9+ through
your platform's normal trusted method if it is not already available. The template
does not install Python, Git, an editor, cloud clients, or OS services.

For a reusable CLI/library, use a dedicated environment **outside the project**.
These paths are examples; choose paths you own and keep package logs outside the
environment so they survive its later removal.

macOS/Linux:

```bash
python3 -m venv "$HOME/.venvs/dotsystemx"
"$HOME/.venvs/dotsystemx/bin/python" -m pip --log "$HOME/dotsystemx-install.log" install \
  "git+https://github.com/WayneTechLab/dotSYSTEMX.git@v1.11.0-beta.4"
"$HOME/.venvs/dotsystemx/bin/python" -I -B -m systemx --help
```

Windows PowerShell:

```powershell
py -3 -m venv "$HOME\.venvs\dotsystemx"
& "$HOME\.venvs\dotsystemx\Scripts\python.exe" -m pip --log "$HOME\dotsystemx-install.log" install "git+https://github.com/WayneTechLab/dotSYSTEMX.git@v1.11.0-beta.4"
& "$HOME\.venvs\dotsystemx\Scripts\python.exe" -I -B -m systemx --help
```

Calling the environment's Python directly avoids changing activation policy
or global PATH. Git-based installation requires Git. The release wheel can be
installed through the same pip command by supplying its downloaded path instead
of the Git URL; no PyPI publication is implied.

Alternatively, use `python3 -I -B /path/to/reviewed-template/.SYSTEMX/manager.py`
(Windows: `py -3 -I -B ...`) for the commands below. Keep that reviewed checkout
outside the target project, especially for later uninstall/restore.

## 3. Preview and apply first run

In the following examples, `systemx` is a shorthand for the isolated command.
Define it in each shell session using the virtual environment from step 2:

```bash
systemx() { "$HOME/.venvs/dotsystemx/bin/python" -I -B -m systemx "$@"; }
```

```powershell
function systemx { & "$HOME\.venvs\dotsystemx\Scripts\python.exe" -I -B -m systemx @args }
```

If you chose the separate reviewed manager script, replace the function body
with its `python3 -I -B .../manager.py` invocation. The installed `systemx`
console entry point is a convenience for trusted Python paths; its package is
resolved before it can restart in isolated mode.

```bash
systemx first-run --target "/path/to/project" --profile project
systemx first-run --target "/path/to/project" --profile project --apply
```

Without `--apply`, this is a read-only preview for the target; a requested remote
version may be downloaded for verification. For an exact remote version, you may
pass `--version REVIEWED_VERSION --archive-sha256 TRUSTED_CODELOAD_ZIP_DIGEST`
after independently obtaining the 64-hex digest of that exact codeload ZIP.
Replace both placeholders with real values. The digest is checked before archive
parsing. The Git-based Python package installation in step 2 is a separate
download; this manager option does not pin pip's Git fetch or a wheel.
`--dry-run` explicitly selects the
same preview behavior. Applying first run:

1. Installs or adopts `.SYSTEMX`, preserving existing root files. An unmanaged
   folder with a conflicting manifest-listed `.py`, `.sh`, or `.ps1` executable
   stops adoption for review instead of using or overwriting that file.
2. Pins a new installation to its selected release and uses manual updates.
3. Creates an empty `project.json` only when absent.
4. Records local installation/first-run operations and prints the remaining steps.

Add `--lowercase-alias` to opt into the local `.systemx -> .SYSTEMX` link if the
filesystem needs one. Case-insensitive filesystems need no link. Conflicting case
variants stop setup. On an already managed project, first run preserves the
selected version and policy; use the explicit update command to change them.

The ordinary `install` command remains available when you want only the managed
folder without configuration initialization. Both workflows use the same defaults.

## 4. Record this project's actual facts

- Fill `.SYSTEMX/GLOBAL/CONTEXT.md` with purpose, constraints, accepted sources,
  terminology, and privacy boundaries for this project.
- Define outcomes, milestones, and acceptance in `.SYSTEMX/PLAN/MASTER-PLAN.md`.
- Add only known commands to `.SYSTEMX/project.json`; keep unsupported operations
  empty. Check the selected [stack](STACK-GUIDE.md).
- Use `onboard bridge` to preview a short root `AGENTS.md` pointer when no
  root instruction file exists. If one already exists, review and manually
  merge the [entry-point template](../templates/AGENT-ENTRYPOINT.md) with it.
  No host instruction is installed automatically; record any manual integration
  so you can reverse it later.
- Start with `agent.0`; create worker records only for authorized assignments.

## 5. Verify and start work

```bash
systemx run --target "/path/to/project" --offline -- validate
systemx run --target "/path/to/project" --offline -- doctor
systemx run --target "/path/to/project" --offline -- context --agent agent.0
systemx audit --target "/path/to/project"
```

Validation checks the format; empty checks do not prove product readiness. Add
the first accepted task and current focus through the [work workflow](../WORK/README.md).
Use focused context to avoid redundant loading; see [efficiency](EFFICIENCY.md).
Save the [uninstall/restore instructions](UNINSTALL.md) with the handoff.

Menu option 13 opens this guide. Option 14 opens the removal guide. Selecting
these guide entries makes no setup or removal changes. Option 18 opens the
[CLI and tools guide](CLI-TOOLS.md), also available as `tools-guide` through
the local launcher or managed `run` command.

## Optional: review provider, instruction, and credential setup

Use `onboard plan` after installation to select an entry point, provider
surface, and credential consumer without starting a provider. `onboard status`
shows the selected-scope catalog and current Agent1/roster state. Omitted
provider, surface, account, and consumer choices remain unset. A chosen
consumer proposes a new key class unless `none` or `existing-test` is supplied;
no key is created. For example, to plan a local Codex CLI:

```bash
systemx run --target "/path/to/project" --offline -- onboard status
systemx run --target "/path/to/project" --offline -- onboard plan \
  --account-context personal --surface cli --provider codex-cli \
  --credential-consumer local-cli --credential-class new
systemx run --target "/path/to/project" --offline -- agent-1 setup
systemx run --target "/path/to/project" --offline -- agent-y providers
```

An application embedding the [Codex SDK](https://learn.chatgpt.com/docs/codex-sdk)
uses a separate plan. A human using [Kiro CLI](https://kiro.dev/docs/cli/)
can select its CLI surface to read provider setup steps:

```bash
systemx run --target "/path/to/project" --offline -- onboard plan \
  --surface sdk --provider codex-sdk --credential-consumer server-application
systemx run --target "/path/to/project" --offline -- onboard plan \
  --surface cli --provider kiro-cli --credential-consumer local-cli
```

The SDK is owned by that application; the plan does not inherit a Codex CLI
login or store a key. These examples leave all template defaults unset.

For a registered child, use `systemx projects --target "/path/to/project"
-- onboard plan --project Project-A` with the desired selection flags. The
catalog separates Codex CLI/IDE from an OpenAI dot, Grok Build CLI from Grok
Bot, and Muse Code CLI from personal Muse and Meta Model API. A dot, Grok Bot,
or personal Muse is an external Agent Beta reference in this template; catalog
selection does not connect one. Grok Build is discoverable for manual use while
Agent Y execution awaits a reviewed adapter. Kiro CLI, Kiro IDE, and Kiro Web
are separate [Amazon coding surfaces](https://kiro.dev/docs/); the AWS CLI is
separate infrastructure account tooling. The six documented third-party CLI
choices, `claude-code`, `opencode-cli`, `blackbox-cli`, `gemini-cli`,
`cursor-agent`, and `aider`, are manual discovery paths until each has a
reviewed Agent Y adapter. Their own sign-in and repository permissions apply.
See [CLI and tools](CLI-TOOLS.md)
and the [Agent 0 roster](AGENT-0-ROSTER.md) for the role lanes.

Run `agent-1 status` and `agent-1 setup` in the selected scope to see the
required personal or enterprise, repository, role, secret target, local store,
and rotation questions. `agent-1 check` performs a warning-only All-In-One
local review. If a dotenv file exists, select it explicitly with `onboard plan
--env-file .env` or `agent-1 env-inventory --env-file .env` to inspect key
names, duplicates, unsupported lines, and Git tracking without returning
values. `agent-1 env-sanitize --env-file .env` previews a names-only
`.env.example`; `--apply` creates it without deleting the source or rotating
credentials. Prefer a newly issued credential for the actual consumer; an
existing value is test-only until rotation is reviewed.

Choose the credential consumer before selecting a remote secret target.
[GitHub Actions secrets](https://docs.github.com/en/code-security/reference/secret-security/secret-types)
are available to Actions workflows, not a local CLI or VS Code process.
[GitHub Agents secrets](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/configure-secrets-and-variables),
Codespaces secrets, and Dependabot secrets have distinct consumers and access
rules. The repository publishing this template currently has GitHub Actions
disabled; downstream projects set their own policy. Agent1 `env-migrate`
currently targets only repository or environment **Actions** secrets, one
name at a time through hidden terminal input after account and admin checks.
It does not populate a local `.env` or OS credential store.

`onboard bridge` previews an optional fixed project-root `AGENTS.md` pointer
to `.SYSTEMX/AGENTS.md`. If the root file is absent, review `contentSha256`
and apply with `onboard bridge --apply --expected-sha256 HASH_FROM_PREVIEW`.
Existing files, links, and directories are preserved as conflicts. The bridge
does not authorize a provider or copy all rules into every harness. Preview is
available on Windows; applying the bridge requires POSIX anchored directory
operations and fails closed on native Windows in this beta.
Tools vary in whether they read `AGENTS.md` directly. The
[provider guide](CLI-TOOLS.md#first-time-provider-and-credential-plan) lists
the documented Kiro/OpenCode behavior and Claude/Gemini conditions; the bridge
does not create parallel rules files for each product.

`agent-beta setup` previews a separate BOT/DOT record panel; `agenda status`
reads empty project selections and the Access Matrix. `agenda catalog` reads
stock setting definitions and decision rules without activating an option or
recording a decision. These setup and catalog commands do not start a bot,
upload a credential, grant access, or install a background service. Read the
[CLI tools guide](CLI-TOOLS.md), [security policy](../SECURITY/AGENT1/README.md),
and [service protocol](../Setup/SERVICE.md) before applying optional setup.

Supply all eight setup answers before the first `--apply`: account context,
exact `OWNER/REPO`, review scope, actor role, Actions secret target, local store,
tracked-history review, and rotation decision. To change an existing setup,
preview again with **all eight** corresponding flags. Review its `proposed`
record and `existingSHA256`, then repeat the full command with
`--apply --replace-existing --expect-sha256 SHA_FROM_PREVIEW`. A missing answer
or stale digest stops replacement. On native Windows, metadata-only first
setup, `status`, `questions`, and advisory `check` work, while dotenv
inventory/sanitization/migration, `review --answers`, and changing an existing
setup fail closed because anchored file-handle operations are unavailable.

## Optional: initialize multiple projects

After outer setup, use [SYSTEMX PROJECTS](PROJECTS.md) to preview and create
`Projects/NAME/.SYSTEMXP` records. Choose a project explicitly for every scoped
command. Each new project starts blank with Agent 0 only; existing folders are
never replaced. Do not run a second installer inside `.SYSTEMX`.

```bash
systemx projects --target "/path/to/project" -- add Project-A --kind software
systemx projects --target "/path/to/project" -- add Project-A --kind software --apply
systemx projects --target "/path/to/project" -- context --project Project-A --agent agent.0
```

`--target` still selects the containing outer directory. Direct `projects`
defaults to offline startup; add `--online` before `--` only when you want to
permit the independently opted-in startup release check. The compatible
`systemx run --target PATH --offline -- projects ...` form and reviewed local
launchers remain available. A child's `.SYSTEMXP` shares the outer defaults
and keeps its own records; it is never a second installer target.

Windows PowerShell, using the `systemx` function from step 3 and the containing
project directory you selected:

```powershell
$projectRoot = 'C:\Projects\Example'
systemx projects --target $projectRoot -- add Project-A --kind software
systemx projects --target $projectRoot -- add Project-A --kind software --apply
systemx projects --target $projectRoot -- context --project Project-A --agent agent.0
```

## Optional: activate standard Agent X, Agent Y, and Agent Z roles

Preview `systemx run --target "/path/to/project" --offline -- roles-init`, then
add `--apply` to create
project-owned event/schedule ledgers, CLI job records, a review policy, and X/Y/Z memory. Use the
scoped variant for a child. This activation is separate from installing defaults
and starts no worker, provider, or scheduler. Follow [Agent X](AGENT-X.md),
[Agent Y](AGENT-Y.md), and [Agent Z](AGENT-Z.md); existing projects remain
unchanged until activation. Choose a provider and branch/PR policy per task.

On Windows PowerShell, using the same `$projectRoot` and `systemx` function:

```powershell
systemx run --target $projectRoot --offline -- roles-init
systemx run --target $projectRoot --offline -- roles-init --apply
```

For a named child, select it explicitly. This creates role records without
starting any CLI provider:

```bash
systemx projects --target "/path/to/project" -- roles-init --project Project-A
systemx projects --target "/path/to/project" -- roles-init --project Project-A --apply
systemx projects --target "/path/to/project" -- agent-y providers --project Project-A
```

Configure a child's application commands in its `.SYSTEMXP/project.json`.
Their working directory is `.SYSTEMX/Projects/Project-A/`, so explicitly address
`code/` or the intended project script. Read the [CLI and tools guide](CLI-TOOLS.md)
before connecting provider, repository, or cloud tooling.

## Optional: adopt ROOT, Agent Alpha, and DATA

Initialize only the features useful to the selected project. Each operation
previews missing files first; repeat it with `--apply` to add them. Existing
records are preserved, and older scopes remain valid without these features.

| Feature | Use it for | Setup and limits |
| --- | --- | --- |
| [ROOT](../ROOT/SX-MILESTONE.md) | Internal rules, flexible plan references, and explicit harness/bot task-state observations | `root init`; no external connector, card execution, or duplicate task-status ledger |
| [Agent Alpha and AUTOBOT](AUTOBOT.md) | Selected design, brand, research, rules, and other detailed references | `autobot init`; separate from X/Y/Z activation, without launching models |
| [DATA](DATA.md) | Local temporary, large, imported, and private payloads | `data init`; payloads ignored by Git by default; check adopted exclusions with `data audit` |

For the outer scope, using the `systemx` function defined above:

```bash
systemx run --target "/path/to/project" --offline -- root init
systemx run --target "/path/to/project" --offline -- autobot init
systemx run --target "/path/to/project" --offline -- data init
```

For an existing named child, use the outer installation as the target and select
the child explicitly. These examples also preview before applying:

```bash
systemx projects --target "/path/to/project" -- root init --project Project-A
systemx projects --target "/path/to/project" -- autobot init --project Project-A
systemx projects --target "/path/to/project" -- data init --project Project-A
```

The same arguments work with the PowerShell function from step 3. Use
`root-guide` through managed `run`, or local menu option 21, for the ROOT manual.
Keep one canonical task ledger, load only the relevant packet or references,
and verify actual harness/bot readback before recording an observation. A ROOT
delta compares saved snapshots; equal state labels do not establish live
synchronization or task acceptance.
