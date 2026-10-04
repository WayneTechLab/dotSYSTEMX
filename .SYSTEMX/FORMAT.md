# .SYSTEMX format contract

> **Alpha: use at your own risk; may change daily.** See the [release policy](docs/RELEASE-POLICY.md).

SYSTEMX defines a reusable project operating format. It is a project-maintained
convention, not a certification or an externally ratified industry standard.
Documentation can be used without the CLI. The CLI validates the JSON records
and generated views described here; it does not execute an agent runtime.

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
| `AGENTS/REGISTRY.json` | Stable role IDs and memory paths | Each role's scoped memory |
| `MEMORY/PROJECT.md` | Verified durable facts, decisions, lessons | Dated session checkpoints |
| `project.json` | Explicit host-project commands | Empty `config/project.example.json` |
| `INSTALLATION.json` (managed installs) | Selected defaults release, version pin, profile, update policy, fingerprints | Retained defaults under `.systemx/releases/<version>/` |

Keep raw/private runtime artifacts in ignored local storage. A role is not a
running process; a report is not an authorization grant; a generated view is
not a second editable ledger. Preserve original evidence when superseding it.

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
leading zeroes, plus reserved standard roles `agent.x` (`event-time`) and
`agent.z` (`review`) when explicitly activated using compatible tools. Agent 0 must have role `coordinator`; other roles are nonempty
descriptions. Memory must exist at `AGENTS/<id>/MEMORY.md`, without symlinks.

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

## Public distribution versus adopted project

Use `validate` for an adopted project. Use `validate --template` on a pristine
distribution before publication. The latter also requires:

- Only the explicitly listed distribution files; no local artifacts, initialized
  project config, extra workers, custom documents, caches, or dependencies.
- Blank work and focus, Agent 0 only, and empty example command configuration.
- An empty project registry and blank child creation seeds; no adopted `.SYSTEMXP` folders.
- Reviewed blank context, plan, and memory seeds matching
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

## Managed installation contract, schema version 1

The optional `INSTALLATION.json` contains exactly `schemaVersion`, `profile`,
`repository`, `activeVersion`, `pinnedVersion`, `autoUpdate`, `installedAt`,
`updatedAt`, and `releases`. Profiles are `project`, `directory`, `drive`, or `chat`.
Repository is a GitHub `OWNER/REPO`. Version IDs are exact `X.Y.Z` final releases
or `X.Y.Z-alpha.N` prereleases, with no leading zeroes and alpha N starting at 1.
The selected ID determines the discovery channel; see [release policy](docs/RELEASE-POLICY.md).
`pinnedVersion` is either null or the active version; a pin requires
`autoUpdate: "manual"`. The other policy is explicit opt-in `"on-start"`.
`releases` maps retained version IDs to their distribution-manifest SHA-256 values.

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

## Agent X and Agent Z records

The public registry remains Agent 0 only. `roles-init --apply` explicitly adds
standard role entries and project-owned records while preserving existing bytes.
Activated `agent.x`/`agent.z` IDs require tools that support them; older readers
are not compatible with those added IDs. Record schema version 1 is otherwise
unchanged. A downgrade after activation requires a reviewed migration or backup.

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
