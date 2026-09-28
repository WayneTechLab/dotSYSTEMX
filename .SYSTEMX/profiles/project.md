# Project root and VS Code setup

Use the exact directory name **`.SYSTEMX`**. The installer flag
`--lowercase-alias` or menu option 12 enables an optional local `.systemx` link.
See [exact casing and conflict recovery](../docs/EXACT-CASE.md).

Choose the project's actual root directory, whether it contains application code,
research, documentation, or another kind of work. Git and VS Code are optional.

```bash
systemx install --target "/path/to/project" --profile project
systemx run --target "/path/to/project" -- context --agent agent.0
```

The installer adds `.SYSTEMX` inside that root. It does not change Git remotes,
editor settings, existing root instructions, application dependencies, or build
configuration. New installs are pinned and use manual updates.

For a VS Code workspace with several roots, install separately into each project
that needs its own context and task ledger. Do not silently merge those projects'
Global context or agent memory. A portfolio directory can have its own separate
SYSTEMX installation and explicit references to the individual projects.

Use [the root instruction template](../templates/AGENT-ENTRYPOINT.md) only after
reconciling it with any existing instructions. See [installation](../docs/INSTALLATION.md).

Reference: [VS Code multi-root workspaces](https://code.visualstudio.com/docs/editing/workspaces/multi-root-workspaces).
