# Technical Guide

> **Alpha: use at your own risk; may change daily.** See the [release policy](RELEASE-POLICY.md).

`.SYSTEMX` is a file-based project operating format with optional Python tools.
It supplies records, local validation, bounded context, version selection, and
reversible installation lifecycle operations. It is not a model runtime or a
service that automatically reads every project or starts agents.

## Architecture

The [Visual Guide](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Visual-Guide) provides Mermaid trees and record-flow diagrams.
The [subagent sequence](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Subagent-Processing) separates runtime messages from saved
project state; neither diagram adds an execution service to this file format.

```text
Host project
└── .SYSTEMX                       exact stored directory name
    ├── GLOBAL, PLAN, MEMORY       project context, outcomes, durable facts
    ├── WORK                       canonical tasks and current focus
    ├── AGENTS                     Agent 0, optional X/Z, and scoped worker memory
    ├── EVENTS                     event and due ledgers after activation
    ├── REVIEWS                    policy, requests, scorecards after activation
    ├── Projects/REGISTRY.json      explicit child identities
    ├── Projects/NAME/.SYSTEMXP     isolated child records; no nested installation
    ├── project.json               explicit project command arguments
    ├── INSTALLATION.json          selected defaults, update policy, archive receipts
    └── .systemx                   internal manager storage
        ├── releases/<version>     retained, fingerprinted default snapshots
        ├── history                previous state and explicit bootstrap backups
        └── operations             local installation operation receipts
```

The optional sibling `.systemx -> .SYSTEMX` link is a second route to the same
folder. It is different from the nested manager cache. Follow the
[exact-case contract](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Exact-Case-and-Alias).

## Components and data flow

| Component | Responsibility |
| --- | --- |
| `manager.py` | Install/update, explicit bootstrap refresh, release checks, pins, profiles, first run, audit, uninstall, restore, chat export |
| `systemx_paths.py` | Exact stored spelling, project boundaries, case-conflict and alias checks |
| `lifecycle.py` | File inventories, raw-byte hashes, atomic JSON receipts, backup boundaries |
| `scripts/systemx.py` | Configuration validation, menu, doctor, explicitly configured commands |
| `scripts/project_memory.py` | Task ledger, focus, generated views, agent records, bounded context |
| `scripts/project_workspaces.py` | Explicit child scope routing, blank creation, scoped commands, local snapshots |
| `scripts/agent_standards.py` | Explicit X/Z setup, safe records, common scope dispatch |
| `scripts/agent_x.py` | Event occurrence/recording time and due-item tracking |
| `scripts/agent_z.py` | Fixed 100-question policy, request/report validation, score math and deltas |
| `config/distribution.json` | Explicit public file inventory with release fingerprints |
| `config/template-records.json` | Reviewed blank seed fingerprints |

The library and CLI use the same manager functions. Refreshed stock launchers
invoke both managed and unmanaged tools in Python isolated mode (`-I`). Direct
`manager.py`, `systemx.py`, and `release.py` invocations restart in isolated mode
before importing standard libraries. The installed console entry point first
resolves its package, then restarts before importing the manager; invoke
`python -I -B -m systemx` from a reviewed environment when import paths are
untrusted. Standalone entry points load only named
local helpers from source bytes, without adding the unchecked folder to Python's
global import path or consuming its cached bytecode. A managed run
verifies its selected default snapshot and invokes its runner with `-I -B` and `--root`
pointing to the outer project records. Old root guidance remains preserved;
stock launcher updates require explicit bootstrap refresh. Task state is stored
once in `WORK/TASKS.json`; CURRENT and status pages are derived views. The
[format contract](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Standard-Format) defines record fields and transitions.
The current manager inspects older installation state but refuses to install or
newly select releases before 1.8.7-alpha.1, where native isolated runner support
begins. For an already selected, verified older snapshot, it launches an isolated
child with a compatibility shim that adds only that verified snapshot's scripts
directory to the child import path. The old code still runs with its historical
behavior. Reselecting a pre-floor release requires separately reviewed recovery.

## Installation lifecycle

First run previews by default. Applying it installs or adopts the canonical
folder, pins a new installation, and creates an empty `project.json` only when
absent. It executes no project checks or app setup commands. Existing managed
versions and policies remain selected. Follow [first-time setup](FIRST-RUN.md).

Ordinary updates add snapshots and missing root files. They do not replace
project records or remove upstream-deleted files. Fresh adoption rejects a
manifest-listed executable default whose existing contents differ from the
reviewed distribution. A changed-release update also requires the eight root
bootstrap and launcher files to match the destination release. A separate,
preview-first
`bootstrap-refresh` accepts only stock contents from the destination or intact
retained release snapshots, stores exact backups for recognized replacements,
and may create a missing stock file only if no retained release ever contained
it. A file missing from the root despite its presence in a retained release is
a conflict. It explicitly replaces only recognized files, including stock shell
and PowerShell launchers. It does
not update customized launchers or project-owned records. An opted-in startup
check never selects a release. Manual updates remain the default; startup checks
are opt-in and major upgrades require review. Existing root managers are
preserved by ordinary updates, so refresh an older stock manager with a reviewed
external tool before relying on this check-only startup contract.
Distribution hashes normalize CRLF to LF for portable text checkouts. They
check consistency with the manifest;
they are not independent release signatures. A selected release cache must also
have exactly the expected files and parent directories: unlisted modules,
packages, links, special entries, and unexpected directories are rejected before
the cached runner executes. Partial snapshots can be resumed only when every
present entry matches the reviewed distribution.

An exact remote tag ZIP can have a separately trusted raw SHA-256 pin checked
before archive parsing. `INSTALLATION.json` records `explicit-pin`,
`observed-only`, or no remote digest for each selected release. Opted-in startup
discovery reads release metadata only; it never downloads an archive or changes
the selection. The independent digest pin applies to a later explicit manual
update. Neither the manifest nor an observed digest makes a movable tag
immutable. See [installation](INSTALLATION.md).

Uninstall is a separate explicit operation: it inventories the complete folder,
moves it to an external backup on the same filesystem, removes a valid local alias,
and writes an external receipt. It does not infer which customized files are safe
to delete. Restore compares raw-byte hashes, empty directories, and link targets
against that receipt and refuses an occupied destination. See
[uninstall and cleanup](UNINSTALL.md) for limits and recovery.

## Concurrency, integrity, and logs

Install/update and removal use an exclusive local writer lock. Task, Agent X, and
Agent Z command writes use a separate per-scope coordination lock. Cooperating
coordination writers wait up to one second; the lock records a token, PID, host,
and creation time. On a crash it remains for manual inspection and is never
automatically removed as "stale." Operation receipts
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

### Designing a future adapter

Keep any new harness or MCP adapter behind the existing project boundary:

- Resolve one explicit project and selected default version for each operation.
- Separate bounded reads, proposed changes, and authorized writes. Honor the
  host's permissions; role names and reviewer strings are not credentials.
- Use canonical commands and record formats. Map runtime job IDs in coordination
  notes instead of creating a competing task database without a migration plan.
- Serialize writes across the adapter's actual deployment. The current local
  lock is not a distributed lock across machines, worktrees, or Drive copies.
- Make retries safe to reconcile: inspect the previous result before repeating
  a task creation, file write, or external action. Log enough to recover it.
- Define privacy, retained evidence, version compatibility, and removal of any
  extra integration files, services, or credentials the adapter installs.

These are extension requirements, not capabilities of a shipped MCP server.
The current integration surface is the [library and CLI](LIBRARY.md).

## Task scale and context scale

The task tool reads the JSON ledger as a whole and writes it back while updating
generated views. Bounded context output limits what an assistant initially sees;
it does not make storage or validation independent of ledger size. Histories,
evidence references, and generated status pages grow with recorded work.

The 10,000+ task-event goal concerns project continuity. It is not a throughput
benchmark, task queue, or automatic archival feature. Measure representative
large ledgers in the target environment before making capacity claims. Preserve
IDs, dependencies, and evidence when designing a future storage migration.
See [Anti-drift and long-running work](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Anti-Drift-and-Long-Running-Work).

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

## Toolchain and shared context

Read the [toolchain map](ONE-SHOT-PROJECT.md#2-prepare-the-toolchain-and-selected-scope)
for the boundary between model/harness, records, app tools, verification, and
delivery. The [shared workspace guide](SHARED-WORKSPACES.md) covers
cloud snapshot requirements, multi-chat writer ownership, and bot startup context.
These are integration patterns over the current CLI/library, not new cloud services.
