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
`py -3 -I -B .SYSTEMX\manager.py install ...`. Quote paths containing spaces.
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
    ├── INSTALLATION.json       Manager-owned selection, policy, archive digests
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

Ordinary `install` and `update` operations **never replace or delete existing
files or folders in the project**. They append a new versioned defaults directory,
create only missing root files, and update the manager-owned selection metadata.
They retain files removed or renamed upstream, older releases, custom defaults,
tasks, configuration, and memory. A separate, explicitly applied
`bootstrap-refresh` may replace recognized stock bootstrap and launcher files
after making byte-for-byte backups of the replaced originals. It may also create
a missing stock file that was absent from every intact retained historical
release; a file that once existed and is now missing remains a conflict. It
never rewrites project records or customized launchers. See
[upgrade guidance](UPGRADING.md#refresh-the-root-bootstrap-before-a-changed-release).
Removal is a separate explicit, reversible operation; see [uninstall and cleanup](UNINSTALL.md).
It archives the complete folder and logs its inventory instead of deleting records.

The root `VERSION` records the initially copied files and is preserved too.
`systemx status --target ...` reports the authoritative **selected defaults version**.
Use the selected release's guidance, templates, and runner; retained root guidance
can be older or customized. A changed-release update requires the eight stock
bootstrap/launcher files (`manager.py`, `lifecycle.py`, `versions.py`,
`systemx_paths.py`, `SYSTEMX.sh`, `SYSTEMX.ps1`, `INSTALL.sh`, and `INSTALL.ps1`)
to match that release. The managed runner always reads/writes project records
from the outer `.SYSTEMX`, never the blank seeds in a release
snapshot.

## Select, lock, or update a version

**Before moving from 1.5.0 or earlier to alpha, upgrade the external CLI/library
first.** Older managers cannot parse alpha IDs, and additive updates deliberately
preserve their original files. See [alpha migration and release policy](RELEASE-POLICY.md).
`systemx --version` reports the installed tool; `systemx status --target ...`
reports that project's selected defaults and derived `releaseChannel`.

New installations are pinned to the installed release and use manual updates.
After reviewing the [published release history](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Versions-and-Changelog):

```bash
systemx status --target "/path/to/project"
systemx policy --target "/path/to/project" --pin none
systemx update --target "/path/to/project" --version 1.8.8-alpha.1 \
  --archive-sha256 "<independently obtained codeload ZIP SHA-256>" --dry-run
systemx update --target "/path/to/project" --version 1.8.8-alpha.1 \
  --archive-sha256 "<independently obtained codeload ZIP SHA-256>"
systemx policy --target "/path/to/project" --pin current
```

Use the desired published version in place of the example. Omitting `--version`
on an unpinned update discovers the selected version's channel: stable versions
select only final releases; alpha versions select newer published alpha or final
releases. Discovery cannot silently downgrade a project. `--source` selects
a local reviewed distribution instead; its manifest determines the version.
The manager still permits an explicit manual update without a digest; its
receipt marks that archive `observed-only`, so the pinned example above is the
stronger choice when the digest comes from a separately trusted record.
This manager installs and newly selects only releases **1.8.7-alpha.1 or newer**,
where the isolated runner contract begins; `bootstrap-refresh` also requires a
target release at or above that floor. `status` can still inspect an older
managed installation. If one is already selected, the new manager can run its
verified retained snapshot through an isolated compatibility shim while a
reviewed external migration is prepared. That old runner still has its historical
behavior and record compatibility; the shim does not turn it into current code.
An explicit selection of an older release within
the supported range may be possible after unpinning when its stock bootstrap and
launcher files are unchanged; bootstrap rollback itself is refused. Recovering a
release older than 1.8.7-alpha.1 requires a separately reviewed backup or legacy
path, outside this manager's install/update selection flow. Application/schema
migrations are never reversed automatically; check compatibility before any
historical recovery.

If a changed-release update reports a root bootstrap difference, follow the
[preview, backup, and refresh sequence](UPGRADING.md#refresh-the-root-bootstrap-before-a-changed-release)
with a reviewed **new external** manager before retrying. The normal updater
will not silently replace an old root manager.

An existing version directory cannot be replaced with different content under
the same version ID. Before running its Python code, the manager checks both
the manifest fingerprints and the **complete physical inventory** of the selected
release cache. Unexpected files, Python modules, packages, links, or directories
stop selection; the manager leaves them in place for inspection. A partial cache
may still be completed by retrying an interrupted update. These checks prevent
unlisted local cache code from joining a verified runner; they do not authenticate
the remote publisher.

For an exact remote release, `install`, `update`, and `first-run` accept an
independent SHA-256 pin for the **exact GitHub codeload tag ZIP** they fetch:

```bash
systemx update --target "/path/to/project" --version 1.8.8-alpha.1 \
  --archive-sha256 "<64-hex SHA-256 of the exact codeload tag ZIP>" --dry-run
systemx update --target "/path/to/project" --version 1.8.8-alpha.1 \
  --archive-sha256 "<64-hex SHA-256 of the exact codeload tag ZIP>"
```

Replace the version and digest together, and unpin the current selection first
when changing versions. The digest must come from a separately trusted record;
a checksum fetched from the same movable tag is not independent trust. A
`SHA256SUMS` entry for a separately built release archive or wheel is **not** the
digest of this codeload ZIP. The manager checks the raw ZIP digest before parsing
its contents, then records `explicit-pin` in `INSTALLATION.json`. Without this
argument, it records the observed ZIP digest as `observed-only`; a local source
has no remote archive digest. `systemx status` shows the selected receipt.
`--archive-sha256` requires an explicit remote `--version` and cannot accompany
`--source` or unversioned discovery. Remote updates use the configured GitHub
repository's exact release tag; an explicit repository override belongs to that
installation's trusted source choice.

## Optional startup update checks

```bash
systemx policy --target "/path/to/project" --auto on-start
systemx run --target "/path/to/project" -- status

# Stop startup checks, while retaining the selected release and any pin:
systemx policy --target "/path/to/project" --auto manual
```

With this opt-in policy, the managed launcher checks release metadata at startup,
at most once per 24 hours after a successful check, and **reports** an available
release. It never downloads that release archive or changes the selected defaults,
pin, project-owned files, or release cache during the check. A pinned project
may enable these notices without unpinning. An alpha project checks for alpha or final
releases; a stable project checks only final releases. A new major version is
reported for separate review. No process runs when SYSTEMX is closed. There are
no OS scheduler, login, or Git hooks.

After a notice, review the release and its independently obtained codeload ZIP
digest, then select an exact version manually. Unpin only when changing the
selected version; preview the update, apply it, verify the result, and pin the
current version again if desired. The `--archive-sha256` command above verifies
the downloaded archive before parsing it. A checksum copied from the same
mutable location as the archive is not independent trust. If the new release
changes a root bootstrap or launcher file, use the explicitly reviewed,
backed-up `bootstrap-refresh` procedure before the update.

An unavailable check leaves the verified installed release usable. A failed check
can be retried at the next startup. Use `systemx run --offline --target ... -- ...`
to skip network checks for that invocation. Inspection via manager `status` and
`export-chat` is always offline. The check records only local manager-owned
metadata under `.SYSTEMX/.systemx/last-check.json`.

**Existing installations:** their root `manager.py` and launcher are preserved
by an ordinary update. If they still implement automatic startup selection,
do not enable `on-start` through that older root launcher. Use the reviewed new
external tool to perform the [bootstrap refresh](UPGRADING.md#refresh-the-root-bootstrap-before-a-changed-release)
and select the new release before relying on check-only behavior. Until then,
keep `--auto manual` or invoke the external tool with `--offline`.

## Existing installations and recovery

Run `install --dry-run` against the real project to inspect what will be added.
The manager never overwrites an existing `INSTALLATION.json`; recognized installs
use `update`. Unsupported legacy task layouts need the [upgrade guide](UPGRADING.md).
Installation does not assert that old records are compatible with new tooling:
run ordinary `validate` and inspect context before continuing work.
When adopting an unmanaged folder, `install --dry-run` reports any existing
manifest-listed `.py`, `.sh`, or `.ps1` default whose bytes differ from the
reviewed distribution. Applying the install refuses that conflict and leaves
the existing executable untouched. Review and reconcile the exact file or use a
clean target; do not treat a preserved unknown script as trusted bootstrap code.

If an update is interrupted, earlier defaults and project files remain. A partial
new snapshot is never selected before its files verify. Retry the same release;
if a partial file differs or an unlisted entry is present, move that incomplete
snapshot aside for inspection
before retrying. Do not delete project records to recover an update. A lock file
is a local process guard; verify that its recorded owner has stopped before
manually removing a stale lock. Drive synchronization is not a distributed lock.

The manager writes installation metadata atomically and retains previous states.
It cannot guarantee atomicity against a separate, uncooperative program changing
the same filesystem at the same instant. Coordinate writers for shared folders.

## Multiple child projects

[SYSTEMX PROJECTS](PROJECTS.md) adds `Projects/NAME/.SYSTEMXP` beneath this one
installation. Child records, source references, code, and the populated project
registry are user-owned. Updates preserve them, including folders absent from
new defaults. New children use the selected release's blank creation seeds.
All children share the outer pin and update policy; do not install or update
`.SYSTEMX` separately beneath `Projects`. Existing custom child registries need
an explicit reviewed migration before the generic routing commands can use them.
