# DATA: local payload storage

`DATA/` is the optional local payload area in a selected `.SYSTEMX` or
`.SYSTEMXP` scope. **Payloads are ignored by Git by default.** Only the shipped
scaffold `.gitignore` and exact README files are intended to be tracked. Keep
source code, public documentation, canonical task records, and portable evidence
references in their normal reviewed locations.

GitHub does not independently apply ignore rules. Git applies them when deciding
which untracked files to add. Already tracked files, force-added files, other
version-control tools, Drive/cloud sync clients, backups, chat attachments, and
deployment tools have their own behavior. Ignored does not mean encrypted,
private, inaccessible to agents, or excluded from other uploads.

## The local folders

| Folder | Intended use |
| --- | --- |
| `DATA/TEMP/` | Temporary inputs and scratch files with an explicit owner and retention |
| `DATA/LARGE/` | Large local artifacts that should not enter ordinary Git history |
| `DATA/IMPORTS/` | Original imported material awaiting review and classification |
| `DATA/RESEARCH/` | Source captures, working datasets, and research payloads |
| `DATA/ASSETS/` | Private or large logo, font, icon, image, and media source files |
| `DATA/EXPORTS/` | Local export drafts awaiting privacy and publication review |
| `DATA/CACHE/` | Reproducible local cached inputs or outputs with clear invalidation rules |
| `DATA/ARCHIVE/` | Retained inactive payloads with an owner, date, and recovery purpose |

These folders are empty of payload in the reusable template. Populate only the
chosen project's authorized material. The scaffold does not create an automatic
cleanup job or retention scheduler. Archive is not a backup guarantee; keep a
recoverable independent copy when the material matters.

## Setup and inspection

For a reviewed local folder, use:

```bash
bash .SYSTEMX/SYSTEMX.sh data init
bash .SYSTEMX/SYSTEMX.sh data init --apply
bash .SYSTEMX/SYSTEMX.sh data status
bash .SYSTEMX/SYSTEMX.sh data audit
```

For managed defaults, use `systemx run --target PATH --offline -- data ...`.
For a child, use the selected project's route:

```bash
systemx projects --target "/path/to/workspace" -- data init --project Project-A
systemx projects --target "/path/to/workspace" -- data init --project Project-A --apply
systemx projects --target "/path/to/workspace" -- data audit --project Project-A
```

`init` previews only missing scaffold files; `--apply` adds them without replacing
existing files or user payloads. `status` and `audit` are read-only bounded
inspections. They report scaffold presence and effective Git ignore behavior,
including tracked payload warnings. Ignore evidence covers synthetic path probes
and the tracked index, not an exhaustive proof for every actual untracked file.
Customized exceptions can escape sample probes; verify each intended export
with `git check-ignore -v -- PATH` before sharing. Without Git or a repository, Git exclusion
is unverified. The tools do not recursively read payload contents, upload,
synchronize, delete, compress, execute, or automatically ingest files.

The shipped `DATA/.gitignore` excludes all payloads at any depth and explicitly
allows only itself, the top-level README, and the eight shipped subfolder README
files. A new nested file named `README.md` is payload and remains ignored.
Existing customized ignore files are preserved on update or initialization, so
run `data audit` in the adopted checkout rather than assuming shipped defaults
are effective. Check a specific file yourself with `git check-ignore -v -- PATH`
and inspect `git ls-files -- PATH` before publication.

Inspection reads at most 1,024 direct names in the DATA root and in each known
scaffold folder, without following nested payload trees. If a folder exceeds
that metadata guard, group files into nested payload folders or use an approved
external store before auditing again. This limit bounds inspection work, not
the byte size of a payload; no payload contents are read or hashed. Git metadata
output is bounded to 256 KiB and tracked-payload samples to 20 paths, so a partial
report remains a warning rather than proof of exclusion.

When payload is already tracked, adding an ignore rule does not untrack it or
erase its history. Review and authorize the remedy in the host repository;
these commands do not remove it automatically. Rotate exposed credentials and
follow the incident process when appropriate. Store live secrets in a secret
manager or approved credential store rather than treating DATA as one.

## References, AUTOBOT, and sharing

[Data AUTOBOT](AUTOBOT.md) describes classification, source/provenance,
ownership, schema, retention, and authorized handling. Other AUTOBOT documents
can link relevant payloads: Brand to approved logo assets, Tokens to licensed
font sources, Research to original captures, and Archive to retained material.
A pointer is not an instruction to load the file. Select and review only the
material needed for the authorized task, considering type, size, sensitivity,
license, and prompt-injection risk.

The authoritative task ledger keeps references to decisive evidence; preserve
the actual evidence and its provenance under the project's retention policy.
Do not publish a local path as proof that another reviewer can retrieve the
bytes. For a reproducible shared result, use an explicitly approved accessible
location and record its revision or digest. An ignored local payload may be
absent after a fresh clone even when its reference is committed.

Root and child DATA payloads remain separate. A child can explicitly initialize
its own blank scaffold from reviewed defaults; it does not inherit the outer
project's assets or data. Template
updates add new missing scaffold files and preserve adopted files and folders.
Uninstall/restore can move the complete `.SYSTEMX` including DATA to the chosen
backup; verify capacity, privacy, and retained payloads before doing so. See
[installation](INSTALLATION.md), [uninstall](UNINSTALL.md), and
[security](SECURITY.md).
