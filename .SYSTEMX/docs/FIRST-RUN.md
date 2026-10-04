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
  "git+https://github.com/WayneTechLab/dotSYSTEMX.git@v1.8.0-alpha.1"
"$HOME/.venvs/dotsystemx/bin/systemx" --help
```

Windows PowerShell:

```powershell
py -3 -m venv "$HOME\.venvs\dotsystemx"
& "$HOME\.venvs\dotsystemx\Scripts\python.exe" -m pip --log "$HOME\dotsystemx-install.log" install "git+https://github.com/WayneTechLab/dotSYSTEMX.git@v1.8.0-alpha.1"
& "$HOME\.venvs\dotsystemx\Scripts\systemx.exe" --help
```

Calling the environment's executable directly avoids changing activation policy
or global PATH. Git-based installation requires Git. The release wheel can be
installed through the same pip command by supplying its downloaded path instead
of the Git URL; no PyPI publication is implied.

Alternatively, use `python3 -B /path/to/reviewed-template/.SYSTEMX/manager.py`
(Windows: `py -3 -B ...`) in place of `systemx` below. Keep that reviewed checkout
outside the target project, especially for later uninstall/restore.

## 3. Preview and apply first run

In the following commands, `systemx` means the executable in the environment you
selected above, or the separate reviewed manager entry point.

```bash
systemx first-run --target "/path/to/project" --profile project
systemx first-run --target "/path/to/project" --profile project --apply
```

Without `--apply`, this is a read-only preview for the target; a requested remote
version may be downloaded for verification. `--dry-run` explicitly selects the
same preview behavior. Applying first run:

1. Installs or adopts `.SYSTEMX`, preserving every existing root file.
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
these guide entries makes no setup or removal changes.

## Optional: initialize multiple projects

After outer setup, use [SYSTEMX PROJECTS](PROJECTS.md) to preview and create
`Projects/NAME/.SYSTEMXP` records. Choose a project explicitly for every scoped
command. Each new project starts blank with Agent 0 only; existing folders are
never replaced. Do not run a second installer inside `.SYSTEMX`.

```bash
bash .SYSTEMX/SYSTEMX.sh projects add Project-A --kind software
bash .SYSTEMX/SYSTEMX.sh projects add Project-A --kind software --apply
bash .SYSTEMX/SYSTEMX.sh projects context --project Project-A --agent agent.0
```

## Optional: activate standard Agent X and Agent Z roles

Preview `bash .SYSTEMX/SYSTEMX.sh roles-init`, then add `--apply` to create
project-owned event/schedule ledgers, a review policy, and X/Z memory. Use the
scoped variant for a child. This activation is separate from installing defaults
and starts no worker or scheduler. Follow [Agent X](AGENT-X.md) and
[Agent Z](AGENT-Z.md); existing projects remain unchanged until activation.
