# Agent X: events, time, and schedule tracking

Agent X is the standard **event-time** role (`agent.x`). It connects observed
human, agent, bot, and automation activity to the selected project's work without
becoming another task coordinator. Agent 0 still routes work and accepts results.
A role record does not launch a process or grant external authority.

## Activate once in the selected scope

```bash
bash .SYSTEMX/SYSTEMX.sh roles-init
bash .SYSTEMX/SYSTEMX.sh roles-init --apply
# For one child project instead:
bash .SYSTEMX/SYSTEMX.sh projects roles-init --project Project-A --apply
```

Setup previews first. Applying it registers Agent X and Agent Z, creates their
blank memory and records, and logs the operation. It preserves all existing files
and role identities, and is idempotent. New definitions travel with the public
template; only Agent 0 is registered in its blank distribution so older managed
launchers can still verify a new release. Activate X/Z only with selected defaults
that support them. Older tools cannot read activated X/Z role IDs; restore a
pre-activation backup before a deliberate downgrade. The current manager cannot
newly select releases older than 1.8.7-alpha.1, although it can run an already
selected verified older snapshot with an isolated compatibility shim. That old
runner still may not understand activated X/Z roles. Reselection below the floor
requires a separately reviewed backup or legacy path. Updates alone do not activate
roles or rewrite an existing registry.

Root records live in `.SYSTEMX`; child records live in the selected `.SYSTEMXP`.
Use `projects agent-x COMMAND --project NAME` for a child, or `--root` for the
outer scope. Existing top-level `agent-x` commands address root records.

## Record an event, not a second task status

`EVENTS/EVENTS.json` is an append-only-by-command event ledger. An event records a
stable retry key, occurrence time, recording time, actor kind/ID, event kind,
evidence stage, source revision, task references, summary, and original evidence
references. `WORK/TASKS.json` remains the sole task-state authority.

```bash
bash .SYSTEMX/SYSTEMX.sh agent-x event \
  --key verification-attempt-001 --at 2026-10-04T12:00:00Z \
  --actor-kind automation --actor-id project-checks \
  --kind check --stage checked --revision OBSERVED_REVISION \
  --summary "Relevant checks completed" --task TASK-001 \
  --evidence "artifacts/check-result.txt"
```

Replace the example with real timestamps, revisions, existing task IDs, and
original evidence. References are recorded data; the command does not inspect,
execute, or fetch them. Actor kinds are `human`, `agent`, `bot`, `automation`, and
`system`. IDs describe observed actors; they do not authenticate them.

Kinds are `work`, `check`, `deploy`, `runtime`, `communication`, `schedule`,
`review`, `decision`, and `incident`. Stages are `planned`, `implemented`,
`checked`, `deployed`, `live_verified`, `failed`, `cancelled`, and `observed`.
A checked/deployed/live-verified claim requires an evidence reference. These are
attested claims requiring review, not automatically proven states.

Occurrence time (`at`) and recording time (`recordedAt`) use
`YYYY-MM-DDTHH:MM:SS[.fraction]Z` or an explicit `+HH:MM`/`-HH:MM` offset, with
one to six fractional digits when present. Seconds and a timezone are required;
the parser rejects looser spellings consistently across supported Python
versions. Times are compared as instants, and occurrence times are stored in UTC.
New `recordedAt` values include microseconds.
Only a `planned` event may have an `at` later than `recordedAt`. Completed work,
checks, deployments, live verification, failures, cancellations, and observations
must have occurred by the time they are recorded. The validator applies this rule
to existing ledgers as well as new writes. Do not replace an old observation's
time with the current recording time. Preserve failed runs and original events;
record corrections as new events referring to their IDs.
A repeat with the same key and same facts reuses the original record. Reusing a
key for different facts is refused, so retries cannot silently change history.

```bash
bash .SYSTEMX/SYSTEMX.sh agent-x list --since 2026-10-04T00:00:00Z --limit 25
bash .SYSTEMX/SYSTEMX.sh agent-x list --task TASK-001
bash .SYSTEMX/SYSTEMX.sh agent-x validate
```

Listings sort by occurrence time, report the total matching count, and default
to 25 entries (maximum 1000). No full history is automatically added to LLM
context. Records currently use a JSON ledger with a 32 MiB input limit; they are
not a streaming event database. Archive deliberately with retained references if
needed. Ten thousand recorded events do not prove a throughput or cost target.

## Track deadlines and external schedules

`EVENTS/SCHEDULE.json` tracks one due occurrence per item. It is not an OS or cloud
scheduler. Recording a future item does not execute it, register a recurring job,
send a notification, or prove that an external automation ran.

```bash
bash .SYSTEMX/SYSTEMX.sh agent-x schedule \
  --key follow-up-001 --title "Review the delivered result" \
  --due 2026-10-05T09:00:00-07:00 --owner user \
  --external-ref "Authorized scheduler job or calendar reference"
bash .SYSTEMX/SYSTEMX.sh agent-x due --as-of 2026-10-05T17:00:00Z
```

`due` is read-only and reports open items at or before the explicit `--as-of`
time, or the current UTC time when omitted. It never advances states or launches
work. An external scheduler owns recurrence, timezone/DST rules, credentials,
actual job execution, retries, and notifications. Track each observed occurrence
with a stable key and retain the external job/run reference. Avoid ambiguous
local times; record the actual offset for that occurrence. A cancelled tracking
item does not cancel its external job.

Close an item with its returned `SCH-...` ID:

```bash
bash .SYSTEMX/SYSTEMX.sh agent-x close SCH_RETURNED_ID \
  --state complete --note "Owner reviewed the observed result" \
  --evidence "Original result reference"
```

Use `--state cancelled --note REASON` for cancelled bookkeeping. Completion needs
evidence. Closure is immutable through the command interface; correcting a due
time or following up creates a new item after deliberately closing/superseding
the old one. Closing a due item does not complete a task or cancel a remote job.

## Keep the cycle moving

Agent X records when the idea was accepted, implementation changed, checks ran,
a revision was delivered, and the actual live state was rechecked. Every event
keeps its scope and original revision. Agent Z can cite these records when
reviewing the remaining delta. Neither role automatically rebuilds or repeatedly
reviews unchanged work. See [Agent Z](AGENT-Z.md), [evidence](EVIDENCE.md), and
[SYSTEMX PROJECTS](PROJECTS.md).

Use one cooperating writer per scope. CLI writes wait up to one second for the
local coordination lock, then report the recorded owner process ID, host, and
creation time. A crash can leave that directory behind. Confirm that the owner
has stopped before manually removing a stale lock; the CLI never guesses or
removes one automatically. This is not a distributed lock or protection against
manual editors. Event and schedule facts are private project data when appropriate.
Updates preserve these records; whole-installation backup/restore includes them.
