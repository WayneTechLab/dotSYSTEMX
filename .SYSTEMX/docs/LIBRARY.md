# Command and library integration

SYSTEMX can be copied as a self-contained folder or installed as the `dotsystemx`
Python distribution, which exposes the `systemx` command and importable module.
The package includes the same template files and uses no third-party runtime
dependencies. A package installation does not initialize or alter any project.

## Install into a chosen Python environment

From the public Git repository:

```bash
python3 -m venv .venv
# Activate this environment using your platform's normal command, then:
python -m pip install "git+https://github.com/WayneTechLab/dotSYSTEMX.git@v1.8.0-alpha.1"
systemx setup --profile project
systemx install --target "/path/to/project" --profile project
```

On Windows use `py -3 -m venv .venv` and `.\.venv\Scripts\Activate.ps1` if
your execution policy permits it; alternatively call that environment's Python
and SYSTEMX executables directly. No policy change or administrator access is
needed. Git-based pip installation requires Git. An extracted release can also
be installed with `python -m pip install /path/to/dotSYSTEMX`, or use its published
wheel without Git. The package is distributed through GitHub; no PyPI publication
is implied. Select exact versions from the [release history](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Versions-and-Changelog).

Upgrading the Python package only updates that tool environment. Each project's
default version and pin remain independent. `systemx update --target ...` selects
project defaults under the [preservation contract](INSTALLATION.md).

The public release ID `1.8.0-alpha.1` is spelled `1.8.0a1` in Python package
metadata and wheel filenames (PEP 440). They identify the same release.
`systemx --version` shows both; `status --target ...` shows project defaults.
The library and CLI are alpha APIs; review [release policy](RELEASE-POLICY.md)
before upgrading integrations.

## Python API

```python
from systemx import install, update, status, set_policy, export_chat, alias

# Plan without touching the target, using a local reviewed distribution:
plan = install("/path/to/project", source="/path/to/template/.SYSTEMX",
               profile="project", dry_run=True)

# Apply only after choosing the intended project:
result = install("/path/to/project", source="/path/to/template/.SYSTEMX")
print(status("/path/to/project"))

# Updates require explicit unlocking of the default pin:
set_policy("/path/to/project", pin="none")
update("/path/to/project", source="/path/to/new-template/.SYSTEMX", dry_run=True)

# Export only to a new file; nothing is uploaded:
export_chat("/path/to/project", "/path/to/new-session.md", agent="agent.0")
```

Management functions return structured dictionaries. `run` and `projects` return
`subprocess.CompletedProcess`; inspect `returncode`, `stdout`, and `stderr`. Importing the library performs no
filesystem or network actions. The CLI renders management results as JSON and
uses exit status 2 for a rejected operation. Project command execution preserves
the underlying command's exit status. Use `systemx run --target ... -- <command>`
to invoke the selected defaults against that project's canonical records.

`install` defaults to the package's bundled version. Supply `version` to fetch a
specific GitHub release, or `source` for offline installation. `update` uses the
installation's selected repository unless given a local source. Downloaded files
are bounded, path-checked, and fingerprint-verified; archives are never blindly
extracted into a project. Existing root files are opened only for inspection or
left alone, and missing files are created exclusively.

These functions are a possible future adapter boundary for MCP or other tools.
Such an adapter would still need explicit target selection, access controls,
permission handling, and evidence of writes. No server, remote endpoint, or
additional authority is included by installing this library.

Packaging references: [PyPA project metadata](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
and [entry points](https://packaging.python.org/en/latest/specifications/entry-points/).

## Exact directory casing

The API always manages the real `.SYSTEMX` directory beneath its target.
`install(target, lowercase_alias=True)` optionally creates a local relative
`.systemx -> .SYSTEMX` link. `alias(target)` reports the layout without writing;
`alias(target, create=True, dry_run=True)` previews and `alias(target, create=True)`
requests creation. Case-insensitive filesystems report `filesystem-equivalent`.
The `status` response includes `pathLayout`. Conflicting case variants raise
`ValueError` without merging or deleting them. See the [case contract](EXACT-CASE.md).

## First run and reversible removal

```python
from systemx import first_run, audit, uninstall, restore

first_run("/path/to/project")  # preview
first_run("/path/to/project", apply=True)
audit("/path/to/project")      # read-only, scoped footprint and operation history
uninstall("/path/to/project", backup="/path/to/new-backup")  # preview
uninstall("/path/to/project", backup="/path/to/new-backup", apply=True)
restore("/path/to/project", backup="/path/to/new-backup")    # preview
restore("/path/to/project", backup="/path/to/new-backup", apply=True)
```

Uninstall moves the whole `.SYSTEMX` folder, including user records, to an external
backup on the same filesystem. It does not uninstall this Python package. Run
removal/restore from an external environment or checkout. Preserve the receipt
and use the [cleanup guide](UNINSTALL.md) for package removal and intentional leftovers.

## SYSTEMX PROJECTS API and selected chat export

```python
from systemx import projects, export_chat

preview = projects("/path/to/workspace", ["add", "Project-A", "--kind", "software"])
preview.check_returncode()
created = projects("/path/to/workspace", ["add", "Project-A", "--apply"])
created.check_returncode()
packet = projects("/path/to/workspace", ["context", "--project", "Project-A"])
packet.check_returncode()
print(packet.stdout)
export_chat("/path/to/workspace", "/path/to/project-a-chat.md", project="Project-A")
```

`projects(target, arguments, *, offline=True, capture=True)` runs the selected
outer release's `projects` command. The target is the directory containing the
outer `.SYSTEMX`, not a child's folder. Arguments are a nonempty list/tuple of
strings. Scope commands require `--project NAME` or `--root`.

`export_chat(..., project="Project-A")` includes only that child's active records
with shared default guidance. Omit `project` for the root packet. The equivalent
CLI is `systemx export-chat --target PATH --project Project-A --output NEW_FILE`.
It never overwrites an existing output or uploads the packet. The returned
management dictionary includes `project` (null for root), `version`, `output`,
and `uploaded: false`. Review private context before sharing. See
[SYSTEMX PROJECTS](PROJECTS.md) for scoping, commands, and preservation rules.

## Standard role commands

```python
from systemx import run, projects

result = run("/path/to/workspace", ["roles-init"], offline=True, capture=True)
result.check_returncode()  # preview; add --apply after reviewing the intended scope
projects("/path/to/workspace", ["agent-z", "policy", "--project", "Project-A"]).check_returncode()
```

`run` is exported by the package and returns `subprocess.CompletedProcess`.
Arguments must be an explicit string array; they cannot override the chosen
workspace's global `--root`. Scoped `projects ... --root` remains valid.
Role commands perform local record operations; they do not schedule external
jobs, call a model, run checks, or upload evidence. Use `offline=True` to suppress
an independently enabled startup update check. See [Agent X](AGENT-X.md) and
[Agent Z](AGENT-Z.md).
