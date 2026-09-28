# Installation and additive updates

The same distribution supports [project roots](../profiles/project.md),
[OS directories](../profiles/directory.md), [Google Drive](../profiles/drive.md),
and [LLM chats](../profiles/chat.md). A profile describes location and persistence;
it does not fork the task format, configure a stack, or start an agent runtime.
Use `systemx setup --profile project` to print its setup URL and capabilities.

For a guided first adoption, use [first-time setup](FIRST-RUN.md). The `first-run`
command previews by default, then installs/adopts and creates empty configuration
only when explicitly applied.

## Install from a reviewed folder

```bash
bash .SYSTEMX/INSTALL.sh --target "/path/to/project" --profile project --dry-run
bash .SYSTEMX/INSTALL.sh --target "/path/to/project" --profile project
```

On Windows use `.SYSTEMX\INSTALL.ps1` with the same flags, or invoke
`py -3 -B .SYSTEMX\manager.py install ...`. Quote paths containing spaces.
The target is the containing working directory, not `.SYSTEMX`, any case variant,
a directory inside it, or a drive root. Use `--lowercase-alias` to request a local
`.systemx -> .SYSTEMX` link. The installer recognizes case-insensitive paths without
creating a link, and refuses separate case-conflicting entries. See
[exact casing and alias setup](EXACT-CASE.md) for the menu, library, and recovery.
The installer requires Python but does not install runtimes or OS services.
For installation as a command or importable package, see [the library guide](LIBRARY.md).

## Ownership and layout

```text
project/
└── .SYSTEMX/
    ├── INSTALLATION.json       Manager-owned selection and update policy
    ├── GLOBAL/, PLAN/, WORK/   Project-owned records
    ├── MEMORY/, AGENTS/        Project-owned memory and roles
    ├── project.json            Optional project-owned command configuration
    ├── STANDARD.md, scripts/…  Initial files; existing copies are preserved
    └── .systemx/              # internal cache, not the optional sibling alias
        ├── releases/<version>/ Immutable default files for each retained release
        ├── operations/        Local installation operation receipts
        ├── history/           Earlier manager state, retained locally
        ├── last-check.json    Optional startup-check metadata
        └── update.lock        Temporary local writer lock
```

The installed defaults and `INSTALLATION.json` can be committed together for
reproducible project clones. The supplied ignores exclude transient checks,
state history, operation logs, and the lock. Do not deploy this folder as public application data.

Updates **never replace or delete existing files or folders in the project**.
They append a new versioned defaults directory, create only missing root files,
and update the manager-owned selection metadata. They retain files removed or
renamed upstream, older releases, custom defaults, tasks, configuration, and memory.
Removal is a separate explicit, reversible operation; see [uninstall and cleanup](UNINSTALL.md).
It archives the complete folder and logs its inventory instead of deleting records.

The root `VERSION` records the initially copied files and is preserved too.
`systemx status --target ...` reports the authoritative **selected defaults version**.
Use the selected release's guidance, templates, and runner; retained root copies
can be older or customized. The managed runner always reads/writes project records
from the outer `.SYSTEMX`, never the blank seeds in a release snapshot.

## Select, lock, or update a version

New installations are pinned to the installed release and use manual updates.
After reviewing the [published release history](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Versions-and-Changelog):

```bash
systemx status --target "/path/to/project"
systemx policy --target "/path/to/project" --pin none
systemx update --target "/path/to/project" --version 1.5.0 --dry-run
systemx update --target "/path/to/project" --version 1.5.0
systemx policy --target "/path/to/project" --pin current
```

Use the desired published version in place of the example. Omitting `--version`
on an unpinned update selects GitHub's latest stable release. `--source` selects
a local reviewed distribution instead; its manifest determines the version.
Version selection can return to an older managed-install release, while retaining
all local data and snapshots. Application/schema migrations are never reversed
automatically; check compatibility before running older tools on newer records.

An existing version directory cannot be replaced with different content under
the same version ID. Every selected release is fingerprint-checked before execution.
Fingerprints establish consistency with the fetched manifest, not independent
signing or an audit of the publisher. Remote updates use the configured GitHub
repository's exact release tag; an explicit repository override belongs to that
installation's trusted source choice.

## Optional startup updates

```bash
systemx policy --target "/path/to/project" --pin none --auto on-start
systemx run --target "/path/to/project" -- status

# Stop automatic updates and lock the currently selected release:
systemx policy --target "/path/to/project" --pin current
```

With this opt-in policy, the managed launcher checks at startup, at most once per
24 hours after a successful check, and selects a newer stable release in the same
major version using the additive rules. A new major version requires manual review.
No process runs when SYSTEMX is closed. There are no OS scheduler, login, or Git hooks.
An unavailable check leaves the verified installed release usable. A failed check
can be retried at the next startup. Use `systemx run --offline --target ... -- ...`
to skip network checks for that invocation. Inspection via manager `status` and
`export-chat` is always offline. A version pin prevents automatic update selection.

## Existing installations and recovery

Run `install --dry-run` against the real project to inspect what will be added.
The manager never overwrites an existing `INSTALLATION.json`; recognized installs
use `update`. Unsupported legacy task layouts need the [upgrade guide](UPGRADING.md).
Installation does not assert that old records are compatible with new tooling:
run ordinary `validate` and inspect context before continuing work.

If an update is interrupted, earlier defaults and project files remain. A partial
new snapshot is never selected before its files verify. Retry the same release;
if a partial file differs, move that incomplete snapshot aside for inspection
before retrying. Do not delete project records to recover an update. A lock file
is a local process guard; verify that its recorded owner has stopped before
manually removing a stale lock. Drive synchronization is not a distributed lock.

The manager writes installation metadata atomically and retains previous states.
It cannot guarantee atomicity against a separate, uncooperative program changing
the same filesystem at the same instant. Coordinate writers for shared folders.
