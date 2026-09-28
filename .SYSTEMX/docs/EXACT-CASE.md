# Exact `.SYSTEMX` name and optional lowercase alias

The canonical directory is **`.SYSTEMX`**, including the leading dot and uppercase
letters, on every platform. Use that exact spelling in prompts, paths, links,
attachments, agent instructions, scripts, and version control. A leading dot can
hide a folder in file browsers; it does not make its name case-insensitive.

The command and Python module are named `systemx`; the installable package and
GitHub repository are named `dotsystemx` and `dotSYSTEMX`. Those identifiers do
not change the project directory's exact name.

## One directory, optional second route

```text
project/
├── .SYSTEMX/                 canonical real directory; all project records
└── .systemx -> .SYSTEMX      optional relative symlink on a case-sensitive filesystem
```

On a case-insensitive filesystem, `.systemx` already resolves to `.SYSTEMX`.
Setup reports `filesystem-equivalent` and creates no link. On a case-sensitive
filesystem, the opt-in link routes lowercase access to the same files and setup
reports `linked`. Other spellings such as `.SystemX` are not additional aliases.
The tools inspect directory entries and path identity rather than guessing from
the OS. Windows can enable case sensitivity per directory; see
[Microsoft's filesystem guide](https://learn.microsoft.com/en-us/windows/wsl/case-sensitivity).

## Setup, command, menu, and library

During installation:

```bash
systemx install --target "/path/to/project" --lowercase-alias --dry-run
systemx install --target "/path/to/project" --lowercase-alias
```

The same flag works with `.SYSTEMX/INSTALL.sh` and `.SYSTEMX\INSTALL.ps1`.
The target is the containing project, never `.SYSTEMX`, `.systemx`, or a path
inside either. A dry run creates no files, directories, or links. For an absent
project it reports the intent; filesystem equivalence is checked after install.

For an existing managed or manually copied folder:

```bash
systemx alias --target "/path/to/project"             # inspect only
systemx alias --target "/path/to/project" --create    # opt in
bash .SYSTEMX/SYSTEMX.sh paths                        # inspect from the folder
bash .SYSTEMX/SYSTEMX.sh alias --create
```

The interactive menu has **11: Check exact casing and alias** and **12: Enable
local lowercase alias**. Selecting 12 requests creation; it never replaces an
existing entry. In PowerShell, use `.SYSTEMX\SYSTEMX.ps1 paths` or
`.SYSTEMX\SYSTEMX.ps1 alias --create`.

```python
from systemx import install, alias

install("/path/to/project", lowercase_alias=True)
alias("/path/to/project")                # read-only layout report
alias("/path/to/project", create=True)   # idempotent local link setup
```

Creating symlinks requires filesystem support and may require Windows Developer
Mode or appropriate permissions. The tool changes neither privileges nor OS
settings. If optional link creation fails after installation, the complete
canonical installation remains usable; retry `alias --create` when supported.
The relative link remains valid when the containing project is moved together.
The supplied distribution itself contains only the uppercase directory.

## Existing case conflicts

If `.systemx`, `.SystemX`, or another case variant is already an independent
directory, file, dangling link, or unsupported link, operations stop before
creating a competing folder or updating project records. The canonical directory
must be real, not a symlink or junction. The only accepted sibling alias is the
exact relative link `.systemx -> .SYSTEMX`.

Back up all conflicting paths first. Compare task ledgers, plans, memory, local
configuration, and version metadata; decide which records are authoritative.
Reconcile contents with review, preserving both histories. Only after that review
should you move conflicting entries to distinct backup names and ensure the
canonical directory's stored name is `.SYSTEMX`. A case-only rename on an
insensitive filesystem may require an intermediate name. Re-run the path check
before opting in to an alias. The tools perform no automatic merge, rename,
overwrite, or deletion to resolve a conflict.

Install, update, policy, status, managed execution, chat export, source loading,
and the standalone runner check the layout. This is a guard in these tools,
not a filesystem access-control policy: an unrelated program can still create
other spellings. Agents must follow the naming contract even when a link exists.

## Version storage and existing installs

The manager retains its internal cache at **`.SYSTEMX/.systemx/`**, including
`releases/<version>/`, history, and a local lock. This nested manager directory
is not the sibling project alias and must never be changed into that alias.
Its existing name is retained for compatibility with installed releases and pins.
Project tasks and memory belong in the outer `.SYSTEMX`, not the cache.

Updates continue to preserve existing root files and earlier snapshots. Thus an
older copied launcher is not automatically rewritten to gain these guards. Use
the current library's `systemx` command, or the reviewed new release's `manager.py`,
to obtain the new manager checks even when the project's defaults are pinned to
an older release. Selecting the new defaults also enables the standalone runner's
checks. New options require the new tools; a version pin is never silently moved.

## Git, Drive, and chat

Treat the optional sibling alias as a local convenience. Add `/.systemx` to the
host repository's local `.git/info/exclude` if desired, without overwriting existing
rules. The installer does not edit host Git settings or ignore files. The nested
`.SYSTEMX/.gitignore` cannot ignore a sibling. Do not commit the alias to the public
template: case-insensitive checkouts and systems without symlink support may fail
to represent it correctly.

For Drive, network shares, archives, and cloud uploads, transfer the canonical
`.SYSTEMX` regular files with exact names. Do not rely on symlinks being preserved
or synchronized across providers or computers. A local alias can be set up on a
supported filesystem separately; keep it out of the cloud transfer selection.
Browser-only Drive and LLM chat use exact file paths, not OS link setup. Exported
chat packets repeat the naming rule; review and persist changes explicitly.
