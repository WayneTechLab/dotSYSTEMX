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
python -m pip install "git+https://github.com/WayneTechLab/dotSYSTEMX.git@v1.3.0"
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

## Python API

```python
from systemx import install, update, status, set_policy, export_chat

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

Functions return structured dictionaries. Importing the library performs no
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
