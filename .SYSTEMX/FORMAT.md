# .SYSTEMX format contract

> **Beta: use at your own risk.** See the [release policy](docs/RELEASE-POLICY.md).

SYSTEMX defines a reusable project operating format. It is a project-maintained
convention, not a certification or an externally ratified industry standard.
Documentation can be used without the CLI. The core CLI validates the JSON
records and generated views described here. Only an explicitly applied Agent Y
job may invoke an installed external CLI provider; role setup and context reads
do not start one.

## File and version conventions

- Put the complete `.SYSTEMX` directory at the host project root. Preserve exact
  path casing on every system; the stored folder name must be `.SYSTEMX`. A
  local lowercase alias may only route to that directory under the
  [exact-case contract](docs/EXACT-CASE.md). Use UTF-8 for text records and relative references. Educational binary images
  live under `MEDIA/`; they are not canonical project state.
- `VERSION` identifies the template release. Each canonical JSON document has
  its own integer `schemaVersion`; version 1 rejects missing or unknown fields.
- Add project-specific metadata in separate project-owned documents and link
  them from Global context. Do not silently extend canonical JSON records.
- Emit UTC ISO 8601 timestamps with `Z`. The reader accepts explicit timezone
  offsets. History begins at `createdAt` and timestamps cannot go backwards.
- A compatible template update can keep record schema version 1. Incompatible
  record changes need a documented migration before an existing project adopts them.
- Reusable prompts stay blank until adoption. Example IDs, dates, and commands
  in documentation are illustrations and grant no authority.

## One home for each kind of information

| Canonical file | Owns | Derived or supporting files |
| --- | --- | --- |
| `GLOBAL/CONTEXT.md` | Project identity, constraints, accepted sources | Project brief and architecture references |
| `PLAN/MASTER-PLAN.md` | Outcomes, milestones, acceptance, sequencing rationale | Task ID references |
| `WORK/TASKS.json` | Task ownership, state, dependencies, evidence, history | Six generated work views |
| `WORK/FOCUS.json` | Selected objective, existing task IDs, checkpoint pointer | Generated `CURRENT.md` |
| `ROOT/` | Optional request/plan structure and observed harness/bot mappings | `SX-RULES.md`, `SX-MILESTONE.md`, and read-only delta output; task status stays in `WORK/TASKS.json` |
| `AGENTS/REGISTRY.json` | Stable role IDs and memory paths | Each role's scoped memory |
| `MEMORY/PROJECT.md` | Verified durable facts, decisions, lessons | Dated session checkpoints |
| `AUTOBOT/` | Optional detailed reference functions and bounded Agent Alpha requests | Exactly ten named `.MD` functions and `AGENTA.MD` charter |
| `AUTOBOT/AGENDA.json` | Optional Agent Alpha context-selection settings | Blank by default; does not schedule work or grant access |
| `GLOBAL/ACCESS-MATRIX.json` | Default-deny role catalog and structured, owner-reviewed decisions | `GLOBAL/ACCESS-MATRIX.xlsx` is the stock human view; external systems enforce permissions |
| `AGENTB/` | Optional Agent Beta registry of named BOT/DOT workspaces | Per-bot metadata under `.SYSTEMXB-BOT_NAME`; no provider credentials or process |
| `SECURITY/AGENT1/` | Agent1 assessment policy and advisory findings | The selected `agent.1` worker is opt-in; no blocking or service by default |
| `DATA/` | Local payload storage with effective Git exclusion checks | Ignored payloads; exact scaffold README and `.gitignore` files remain portable |
| `project.json` | Explicit host-project commands | Empty `config/project.example.json` |
| `INSTALLATION.json` (managed installs) | Selected defaults release, version pin, profile, update policy, fingerprints | Retained defaults under `.systemx/releases/<version>/` |

Keep raw/private runtime artifacts in ignored local storage. A role is not a
running process; a report is not an authorization grant; a generated view is
not a second editable ledger. Preserve original evidence when superseding it.

`GLOBAL/ACCESS-MATRIX.md` and `PLAN/MAP.md` are supporting records in the root
and each new `.SYSTEMXP` child. The matrix describes a 20-row default-deny role
catalog; reviewed decisions start empty. External systems enforce real
permissions. The map
points to source-backed structure and boundaries; it does not discover topology
or carry a second task status. Open them when relevant rather than loading them
into every agent context packet. See the [access and map guide](docs/ACCESS-AND-MAP.md).
The structured access decisions and Agent Alpha Agenda options are separate
optional records; their empty arrays create no access grant, scheduled action,
or bot session.

## SYSTEMX PROJECTS, schema version 1

`Projects/REGISTRY.json` contains exactly `schemaVersion: 1` and `projects`.
Each entry has exactly `name`, `path`, `records`, and `kind`. Paths are relative
to the outer `.SYSTEMX` and must equal `Projects/NAME` and
`Projects/NAME/.SYSTEMXP`. Names are unique ignoring case; use the exact stored
spelling for selection. The public registry is empty.

A child's ledger, focus, agent registry, and `project.json` use the contracts
below, scoped to that child. `project.name` must match its registry name.
`SOURCES.json` contains `schemaVersion: 1` and `sources`; each source has `kind`,
`location`, and `description`. See [SYSTEMX PROJECTS](docs/PROJECTS.md) for allowed
kinds, path rules, local status snapshots, and command examples.

IDs and dependency edges stay inside one ledger. Qualified project/task references
are prose coordination links, not cross-ledger dependencies. Each child has its
own Agent 0 memory but shares the outer defaults, pin, and update policy.
There are no nested `.SYSTEMX` installs, implicit current project, automatic
source transport, or recursive child workspaces. Unknown custom registries need
reviewed migration; the tools reject them without replacing their files.

## Task ledger, schema version 1

The top-level object contains exactly `schemaVersion` and `tasks` (an array).
Every task contains the following fields; none are optional in stored records.

| Field | Type and rule |
| --- | --- |
| `id` | Unique `TASK-` ID with at least three digits and a positive number; CLI allocates the next number |
| `title` | Nonempty string |
| `owner` | An ID in the agent registry |
| `status` | `todo`, `in_progress`, `blocked`, `needs_review`, `done`, or `cancelled` |
| `milestone` | Empty string or an `M-` ID with at least three digits declared in the master-plan table |
| `scope` | Array of nonempty strings describing intended files/systems; may be empty during intake |
| `acceptance` | Nonempty array of nonempty acceptance criteria |
| `dependsOn` | Unique IDs of existing tasks; no cycles |
| `nextAction` | String; required for `in_progress`, empty for terminal states |
| `blocker` | Nonempty only for `blocked`; empty in other states |
| `evidence` | Array of nonempty evidence references/descriptions; required for `done` |
| `reviewedBy` | `agent.0` or `user` for `done`; otherwise empty |
| `createdAt`, `updatedAt` | Timezone-aware ISO timestamps |
| `history` | Nonempty chronological array of state events |

Each history event contains exactly `at`, `status`, `owner`, `note`, `evidence`,
and `reviewedBy`. History starts at `todo`; the latest event must match the task's
state, owner, evidence, reviewer, and update time. Completed events retain their
evidence and reviewer. Cancelled tasks need a nonempty reason in the latest note.

| Current state | Allowed next states |
| --- | --- |
| `todo` | `in_progress`, `blocked`, `cancelled` |
| `in_progress` | `todo`, `blocked`, `needs_review`, `cancelled` |
| `blocked` | `todo`, `in_progress`, `cancelled` |
| `needs_review` | `in_progress`, `blocked`, `done`, `cancelled` |
| `done` or `cancelled` | `todo` |

Nonterminal states also accept updates without a state change. Dependencies must
be `done` before a task is active, under review, or complete. Reopening terminal
work clears its current evidence/reviewer while preserving historical events;
reopen dependent work first when necessary to keep that invariant valid.

Evidence sufficiency requires review under the [evidence guide](docs/EVIDENCE.md).
The CLI checks metadata consistency, not identity, authenticity, or product quality.

## Focus and agent records, schema version 1

`WORK/FOCUS.json` contains exactly `schemaVersion`, `objective`, `taskIds`,
`checkpoint`, and `updatedAt`. Its blank state has empty strings and an empty
task list. Active focus needs a nonempty objective (maximum 600 characters) and
a timestamp. It can select up to ten unique existing task IDs, including completed
context. A checkpoint is empty or a path to an existing Markdown file under
`MEMORY/sessions/`; absolute paths, parent escapes, symlinks, and archive README
pointers are rejected. Selection replaces the whole focus; it never changes tasks.

`AGENTS/REGISTRY.json` contains exactly `schemaVersion` and `agents`. Each agent
has `id`, `role`, and `memory`. IDs are unique `agent.0`, `agent.1`, etc., without
leading zeroes, plus reserved standard roles `agent.x` (`event-time`),
`agent.y` (`cli-worker`), `agent.z` (`review`), `agent.a`
(`autobot-coordinator`) when explicitly activated using compatible tools.
`agent.b` (`bot-coordinator`) is reserved for optional named BOT/DOT workspaces.
`agent.1` can be selected for Agent1 security-access only when it is not already
registered for another worker role; no public template registers it.
Agent Alpha setup is separate from X/Y/Z setup. Agent 0 must have role
`coordinator`; other roles are
nonempty descriptions. Memory must exist at `AGENTS/<id>/MEMORY.md`, without
symlinks.

## Commands and optional messages

`project.json` contains `schemaVersion`, `project`, `checks`, and `commands`.
`project` contains string `name` and `description` fields. Checks are objects with
unique nonempty `name` and nonempty `command` argument arrays. Commands contain
exactly `dev`, `build`, and `deploy`; an empty array leaves an action unconfigured.
See [configuration](README.md#configuration-contract) and [work commands](WORK/README.md).

The optional [agent-message schema](AI/agent-mesh.schema.json) describes messages,
with its own lifecycle. It neither replaces the task ledger nor adds a bus or
scheduler. Its `$id` is a schema identifier; the CLI does not fetch it or contact
any vendor. A general JSON Schema validator is needed to enforce that schema.

## Optional ROOT planning and observations

`ROOT/SX-RULES.md` describes internal coordination rules within the active
instruction hierarchy. `ROOT/SX-MILESTONE.md` defines the optional request and
planning vocabulary, ROOT record schemas, and tool-card contract. The selected
scope owns its ROOT records; a registered child uses `.SYSTEMXP/ROOT` and the
outer installation's shared tools. Existing scopes without ROOT remain valid.

Plan hierarchy, request origin, task status, and events are separate concerns.
Milestone IDs refer to the Master Plan. Structural plan nodes reference existing
canonical task IDs; they do not duplicate task status or infer milestone
acceptance. `RTask` denotes an originating request and `STask` its scoped
delegation. Hierarchy levels may be skipped and counts are project-defined.
Independently owned or accepted subtasks remain canonical tasks.

ROOT mappings relate canonical tasks to explicitly identified harness/bot
items, including many-to-many relationships and separate execution attempts.
Observations preserve source state, revision, timestamp, and evidence. Delta
output compares the saved observations; it is read-only and cannot establish
live synchronization. An expected revision supplied by the caller remains a
comparison input until verified against the original source. Missing or stale
observations remain gaps. External completion is execution evidence and does
not bypass the existing `needs_review` → `done` acceptance gate. Tool cards
describe bounded calls to actual available tools; they neither execute tools
nor register an MCP server, install providers, or grant permissions.

## Public distribution versus adopted project

Use `validate` for an adopted project. Use `validate --template` on a pristine
distribution before publication. The latter also requires:

- Only the explicitly listed distribution files; no local artifacts, initialized
  project config, extra workers, custom documents, caches, or dependencies.
- Blank work and focus, Agent 0 only, and empty example command configuration.
- An empty project registry and blank child creation seeds; no adopted `.SYSTEMXP` folders.
- Reviewed blank context, access matrix, plan, map, and memory seeds matching
  `config/template-records.json` SHA-256 values (UTF-8 text normalized to LF).
- A complete `config/distribution.json` inventory whose file fingerprints match
  the published release, including its own version and blank-record manifest.

An adopted project is expected to fail the blank-template check after it records
real work. This check is not a secret scanner or an approval of every sentence;
maintainers still review the source, provenance, examples, and exact export.
If a blank prompt intentionally changes, review that change and update its seed
hash. Do not rebaseline populated project records to make them publishable.

Publish from the reviewed tracked revision, excluding local artifacts. For a
folder-only archive from this distribution repository:

```bash
git archive --format=zip --output=../SYSTEMX-template.zip HEAD .SYSTEMX
```

Extract the archive and run `validate --template` there before sharing it. The
MIT license and source attribution remain part of every copy. Follow the
[upgrade guide](docs/UPGRADING.md) when merging into an active project.

## Managed installation contract, schema versions 1 and 2

The current optional `INSTALLATION.json` uses `schemaVersion: 2` and contains
exactly `schemaVersion`, `profile`, `repository`, `activeVersion`,
`pinnedVersion`, `autoUpdate`, `installedAt`, `updatedAt`, `releases`, and
`archiveDigests`. Historical schema-1 state omits `archiveDigests`; the manager
reads it compatibly and adds null receipts on the next state write. Profiles
are `project`, `directory`, `drive`, or `chat`.
Repository is a GitHub `OWNER/REPO`. Version IDs are exact `X.Y.Z` final releases
or `X.Y.Z-alpha.N` prereleases, with no leading zeroes and alpha N starting at 1.
The selected ID determines the discovery channel; see [release policy](docs/RELEASE-POLICY.md).
`pinnedVersion` is either null or the active version. `autoUpdate` is `"manual"`
or the explicit opt-in `"on-start"` availability check. A pinned project may
receive check-only notices, but selecting a different release requires an
explicit unpin and manual update. Startup never fetches a release archive or
changes the selected version.
`releases` maps retained version IDs to their distribution-manifest SHA-256 values.
`archiveDigests` has the same version keys, with either a null receipt or a
recorded archive SHA-256 and `verifiedBy: "explicit-pin"` or `"observed-only"`.

An update appends a verified default snapshot and creates missing root files.
It never replaces or deletes an existing project file, folder, or release snapshot.
Only manager-owned selection/check metadata changes, with earlier selection states
retained. Root VERSION and copied default files therefore retain their initial
contents; the selected defaults version comes from INSTALLATION.json. Running a
selected release must use the outer project's mutable records. Snapshot records
are blank seeds and never become the active project's ledger or memory.

The distribution manifest contains exactly `schemaVersion`, `version`, and
`files`, mapping portable relative file paths to SHA-256 fingerprints normalized
to LF. It excludes its own fingerprint. Immutable release snapshots include the
manifest itself; installation state records that manifest's fingerprint.
Fingerprints detect changed artifacts relative to the selected source; they are
not independent publisher signatures. See [installation](docs/INSTALLATION.md)
for policy, local locking, interrupted writes, and filesystem limits.

## Agent X, Agent Y, and Agent Z records

The public registry remains Agent 0 only. Explicit role setup adds standard
role entries and project-owned records while preserving existing bytes.
Activated `agent.x`/`agent.y`/`agent.z` IDs require tools that support each
one; a reader predating an activated ID is incompatible. Optional Agent Alpha
(`agent.a`, `autobot-coordinator`) uses separate `autobot init` activation and
the `AGENTS/agent.a/MEMORY.md` path. A reader predating that ID is also
incompatible. Record schema version
1 is otherwise unchanged. A downgrade after activation requires a reviewed
migration or backup.

`EVENTS/EVENTS.json` contains `schemaVersion: 1` and `events`. Each event has `id`,
`key`, `at`, `recordedAt`, `actor` (`kind`, `id`), `kind`, `stage`, `summary`,
`tasks`, `revision`, and `evidence`. Stable-key replays preserve the original
record and conflicting facts are refused. `EVENTS/SCHEDULE.json` contains
`schemaVersion: 1` and `items`, with one due occurrence per item and explicit
open/complete/cancelled bookkeeping. See [Agent X](docs/AGENT-X.md).

`REVIEWS/POLICY.json` contains `schemaVersion: 1`, `policyId`, `version`, and
exactly ten `categories`, each with `id`, `name`, and exactly ten `questions`
(`id`, `question`). Stable IDs are C01–C10 and Z01.01–Z10.10. A question change
requires a new policy version; used policy versions are frozen under `policies/`.
Requests retain the subject, code/input revision, evidence revision, stage,
policy snapshot/hash, and all 100 answers. Reports preserve answers, derived
scores, source fingerprints, and time. See [Agent Z](docs/AGENT-Z.md) for the
answer contract, scoring, comparison, and immutable-report behavior.

Normal validation checks current optional event/schedule ledgers and review
policy when present. Historical review requests/reports have explicit selected-ID
validation; they are not all loaded into context. None of these records replaces
`WORK/TASKS.json`, authenticates a worker, or proves evidence independently.

Agent Y's scoped `AGENTS/agent.y/JOBS.json` contains `schemaVersion: 1` and a
`jobs` array. Each portable job records its ID, canonical task ID, selected
provider, repository identity, observed remote base commit, owned branch,
prompt digest, allowed paths, draft-PR opt-in, state and timestamps, head/PR
references, and bounded result evidence. Host-specific absolute repository,
prompt, and worktree paths and configured adapter arguments belong in ignored
`state/agent-y/<Y-ID>.json` execution state, keyed to the job and created with
owner-only file permissions on POSIX hosts. Windows access controls need a
separate review. The
prompt text and provider transcript belong in neither record. A job's
state is one of `prepared`, `running`, `failed`, `review_pending`, `draft_pr`,
`ready`, `closed`, or `merged`; this is a delivery state, never a replacement for
the canonical task's `todo`/`in_progress`/`needs_review`/`done` status. Its
memory is a concise resume aid, and neither the portable job nor host-local
execution state replaces GitHub's actual PR state. The provider and branch/PR
lifecycle are selected per task; activating
`agent.y` does not run a CLI, install a provider, or grant GitHub permission. A
draft PR may be opened only under that task's opt-in policy after a successful
provider exit and controller scope/commit checks; project tests and acceptance
remain separate.
Ready-for-review, close, merge, and branch deletion are distinct actions.
An unmerged PR can close only after recorded cancellation; cleanup after merge
requires accepted completion and remote merge evidence. Closing an unmerged PR
retains its branch for manual disposition. Automated branch deletion needs
exact ownership/head verification and a retained local bundle. Merge requires
separate authorization. See
[Agent Y](docs/AGENT-Y.md).

## Agent Beta, Agent1, and Agenda records

Agent Beta reserves `agent.b` with role `bot-coordinator`; `agent-beta setup`
previews its selected-scope registration. `AGENTB/BOTS.json` has exactly
`schemaVersion: 1` and `bots`, empty in the public template. Each explicitly
created `.SYSTEMXB-BOT_NAME` folder contains bounded metadata, blank memory,
README, and `Rules.MD`. Uppercase ASCII names prevent ambiguous case variants.
`online: false` means no provider session was established, even when a
nonsecret online identity is documented. Task references identify existing
canonical tasks but never change their state. For a new named BOT/DOT, create
its record, add a same-actor `reviewed-intent` Access Matrix decision, then
preview and revision-guard `agent-beta access-link` to retain the ACC reference.
The link grants nothing and keeps `online: false`. See [Agent Beta](AGENTB/README.md).

Agent1 uses numeric `agent.1` with role `security-access` only when that ID is
available. `SECURITY/AGENT1/questions.json` carries twenty categories with
twenty stable evidence questions each; `event_buckets.json` has ten diagnostic
classes. The All-In-One profile is the default on explicit assessment. A local
filename check answers zero catalog questions and reports coverage limits.
First-run answers go to ignored `local/AGENT1-CONFIG.json` in the selected
scope. A complete answer file can be syntax-checked without treating its
evidence references as authenticated. Findings are advisory by default;
neither a score nor a successful stdio response certifies a device or cloud
deployment. See [Agent1](SECURITY/AGENT1/README.md).

`AUTOBOT/AGENDA.json` has exactly `schemaVersion: 1` and `options`; the public
array is empty. Agent Alpha remains the coordinator for the existing ten fixed
AUTOBOT references. An Agenda option may select advisory context and pin its
Rules file digest to a reviewed `GLOBAL/ACCESS-MATRIX.json` decision ID.
The new structured matrix has `schemaVersion: 1`, 20 fixed `roleDefaults` rows,
and an empty `decisions` array. All default rows grant nothing and require
review. A decision records `reviewed-intent`, `denied`, or `gap`, never a
permission grant. `GLOBAL/ACCESS-MATRIX.xlsx` is the distributed default
catalog for human review; JSON remains machine-readable authority. A selected
scope can add a guarded decision with `agenda decision-add`, request live CSV
fields with `agenda table --format csv`, and explicitly export a formula-free
`local/` workbook using `agenda workbook-export`. A workbook check detects
drift after JSON changes. Agent X retains
events and due items, and external IAM retains enforcement. See the
[access guide](docs/ACCESS-AND-MAP.md).
`session-settings` produces a bounded, read-only aggregate of these role
statuses and the fixed AUTOBOT and registered Beta Rules paths and SHA-256
hashes. It contains no Rules text, secret values, or live provider state.

## AUTOBOT, Agent Alpha, and DATA records

`AUTOBOT/CATALOG.json` has exactly `schemaVersion: 1`, `coordinator: "agent.a"`,
`maximum: 10`, and `bots`. The ten ordered entries each have `id`, `name`,
`file`, and a nonempty bounded `functions` array. IDs map exactly from
`autobot.design`, `autobot.soul`, `autobot.memory`, `autobot.rules`,
`autobot.research`, `autobot.brand`, `autobot.media`, `autobot.tokens`,
`autobot.data`, and `autobot.archive` to their corresponding title-case
`AUTOBOT/Name.MD` files. Identity, path case, slot order, and count are fixed.
The coordinator's charter is `AUTOBOT/AGENTA.MD`, outside the ten slots.

`AUTOBOT/REQUESTS.json` contains exactly `schemaVersion: 1` and `requests`.
Each request has `id`, `createdAt`, `identity`, `state`, and `completion`.
Its `ABR-` ID derives from the request identity, which includes scope, claimed
caller, purpose, input revision, optional canonical task ID, selected bot IDs,
catalog hash, and selected file/charter paths, byte sizes, and SHA-256 hashes.
Only explicitly named bot files and the charter enter context, bounded to 64 KiB.
The ledger is bounded to 4,096 entries and 8 MiB; capacity does not authorize
automatic history deletion. Caller labels are not authenticated identities.

State is `requested` with null completion, or `complete` with `completedAt`,
`summary`, `responseRevision`, and nonempty `evidence`. Completion is immutable;
identical requests/results are reused, conflicting completion is refused, and
changed input or file/policy fingerprints create a new request. Freshness of
external facts still depends on an honest current input revision. The runtime
does not execute models, research, tools, or DATA ingestion, and request
completion does not accept a canonical task. See [AUTOBOT](docs/AUTOBOT.md).

`DATA/` contains exact README scaffolds in `TEMP`, `LARGE`, `IMPORTS`,
`RESEARCH`, `ASSETS`, `EXPORTS`, `CACHE`, and `ARCHIVE`. Its scoped `.gitignore`
allows only the shipped scaffold and ignores payloads at any depth. Effective
Git behavior is inspected with `data status`/`data audit`; nonrepository status
is unverified and already tracked payloads need explicit host-project review.
The runtime never reads payload contents recursively, removes data, or uploads
it. Neither Git ignore nor a local path grants privacy, access, cloud exclusion,
or evidence availability to another reviewer. See [DATA](docs/DATA.md).

Merged-PR cleanup writes a verified bundle to ignored
`state/agent-y/archives/<Y-ID>.bundle` before removing owned refs. The portable
job retains its SHA-256 digest, not the bundle bytes; preserve a verified
private copy separately before uninstalling or moving hosts.
