# First-Time Setup

> **Alpha: use at your own risk; may change daily.** See the [release policy](RELEASE-POLICY.md).

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
  "git+https://github.com/WayneTechLab/dotSYSTEMX.git@v1.9.0-alpha.5"
"$HOME/.venvs/dotsystemx/bin/python" -I -B -m systemx --help
```

Windows PowerShell:

```powershell
py -3 -m venv "$HOME\.venvs\dotsystemx"
& "$HOME\.venvs\dotsystemx\Scripts\python.exe" -m pip --log "$HOME\dotsystemx-install.log" install "git+https://github.com/WayneTechLab/dotSYSTEMX.git@v1.9.0-alpha.5"
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
- Merge the optional root [agent entry-point template](../templates/AGENT-ENTRYPOINT.md)
  into existing host instructions if needed. No host instruction is installed
  automatically. Record any manual integration so you can reverse it later.
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

Preview `bash .SYSTEMX/SYSTEMX.sh roles-init`, then add `--apply` to create
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
