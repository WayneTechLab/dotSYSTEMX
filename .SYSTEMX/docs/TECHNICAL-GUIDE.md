# Technical Guide

> **Alpha: use at your own risk; may change daily.** See the [release policy](RELEASE-POLICY.md).

`.SYSTEMX` is a file-based project operating format with optional Python tools.
It supplies records, local validation, bounded context, version selection, and
reversible installation lifecycle operations. It is not a model runtime or a
service that automatically reads every project or starts agents.

## Architecture

```text
Host project
└── .SYSTEMX                       exact stored directory name
    ├── GLOBAL, PLAN, MEMORY       project context, outcomes, durable facts
    ├── WORK                       canonical tasks and current focus
    ├── AGENTS                     Agent 0 role and scoped worker memory
    ├── Projects/REGISTRY.json      explicit child identities
    ├── Projects/NAME/.SYSTEMXP     isolated child records; no nested installation
    ├── project.json               explicit project command arguments
    ├── INSTALLATION.json          selected defaults and update policy
    └── .systemx                   internal manager storage
        ├── releases/<version>     retained, fingerprinted default snapshots
        ├── history                previous installation metadata
        └── operations             local installation operation receipts
```

The optional sibling `.systemx -> .SYSTEMX` link is a second route to the same
folder. It is different from the nested manager cache. Follow the
[exact-case contract](EXACT-CASE.md).

## Components and data flow

| Component | Responsibility |
| --- | --- |
| `manager.py` | Install/update, release checks, pins, profiles, first run, audit, uninstall, restore, chat export |
| `systemx_paths.py` | Exact stored spelling, project boundaries, case-conflict and alias checks |
| `lifecycle.py` | File inventories, raw-byte hashes, atomic JSON receipts, backup boundaries |
| `scripts/systemx.py` | Configuration validation, menu, doctor, explicitly configured commands |
| `scripts/project_memory.py` | Task ledger, focus, generated views, agent records, bounded context |
| `scripts/project_workspaces.py` | Explicit project routing, blank initialization, scoped commands, local status snapshots |
| `config/distribution.json` | Explicit public file inventory with release fingerprints |
| `config/template-records.json` | Reviewed blank seed fingerprints |

The library and CLI use the same manager functions. A managed run verifies its
selected default snapshot and invokes its runner with `--root` pointing to the
outer project records. Old root defaults are preserved. Task state is stored once
in `WORK/TASKS.json`; CURRENT and status pages are derived views. The
[format contract](../FORMAT.md) defines record fields and transitions.

## Installation lifecycle

First run previews by default. Applying it installs or adopts the canonical
folder, pins a new installation, and creates an empty `project.json` only when
absent. It executes no project checks or app setup commands. Existing managed
versions and policies remain selected. Follow [first-time setup](FIRST-RUN.md).

Updates add snapshots and missing root files. They do not replace project records
or remove upstream-deleted files. Manual updates remain the default; startup
checks are opt-in and major upgrades require review. Distribution hashes normalize
CRLF to LF for portable text checkouts. They check consistency with the manifest;
they are not independent release signatures.

Uninstall is a separate explicit operation: it inventories the complete folder,
moves it to an external backup on the same filesystem, removes a valid local alias,
and writes an external receipt. It does not infer which customized files are safe
to delete. Restore compares raw-byte hashes, empty directories, and link targets
against that receipt and refuses an occupied destination. See
[uninstall and cleanup](UNINSTALL.md) for limits and recovery.

## Concurrency, integrity, and logs

Install/update and removal use an exclusive local writer lock. Operation receipts
record started, completed, or failed work; an abrupt process termination can leave
a started receipt and stale lock. Check the owner before recovery. Installation
state and lifecycle receipts are written through temporary files and atomic
replacement. Earlier state is retained. No local lock is a distributed Drive lock,
and no tool can guarantee a consistent snapshot against an uncooperative writer.
Stop active workers before removal, restore, or cloud handoff.

Uninstall inventories never follow content symlinks and do not execute files.
Backups preserve private contents and must remain private. Filesystem permissions,
the host's instruction hierarchy, and existing service authority still apply.
The tools do not provide an authentication or sandbox boundary.

## Runtime and extension points

The optional CLI requires Python 3.9+ and its standard library. Configured project
commands are explicit argument arrays and run with `shell=False` from the project
root. Integrations should preserve that boundary and canonical records. Consult
the [Stack Guide](STACK-GUIDE.md) and [library API](LIBRARY.md).

An MCP adapter could later expose bounded read/write operations over this library.
No MCP server, daemon, remote agent mesh, OAuth registration, or cloud sync engine
is currently installed. Extensions must define ownership, authorization, logs,
and removal behavior rather than implying that the template grants those powers.

## Verification and efficiency

`validate --template` checks a pristine public distribution. Ordinary `validate`
checks an adopted folder and records; configured `check` commands test the host
project. Neither establishes production readiness by itself. Tests use temporary
projects across Windows, macOS, Linux, and supported Python versions.
[Token and time efficiency](EFFICIENCY.md) explains the scoped-context design and
how to measure its effect without claiming unmeasured savings.

## Child project scopes

[SYSTEMX PROJECTS](PROJECTS.md) routes selected operations to
`Projects/NAME/.SYSTEMXP` while reusing `project_memory.py` for the same record
invariants. Configured child commands run from `Projects/NAME/`. Each ledger has
its own local coordination lock; project creation locks the outer registry.
Snapshots contain selected task counts, focus, and source hashes, not a service
health verdict. Shared default snapshots and version selection remain at the
outer installation. A scope selector is not an OS sandbox or distributed lock.

## Standard role implementation

`agent_standards.py` supplies explicit setup, exact-case contained paths, strict
JSON reads, stable fingerprints, and common scope dispatch. `agent_x.py` owns
append-by-command events and due-item bookkeeping. `agent_z.py` owns the fixed
policy, review requests, deterministic scoring arithmetic, immutable scorecards,
and comparable deltas. All are Python standard-library modules with no runtime
model, scheduler, cloud, or database dependency. Agent judgment and original
proof remain external inputs; arithmetic and hashes do not establish their truth.

`roles-init` preserves the existing registry and creates missing records only.
The release's seed registry remains Agent 0 only for older bootstrap-manager
compatibility. Activating named X/Z roles is an explicit record-format adoption;
older selected tools cannot interpret those new role IDs. Shared updates keep
project-owned question policies and past reports unchanged.
