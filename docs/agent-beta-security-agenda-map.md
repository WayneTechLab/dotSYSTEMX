# Agent Beta, Agent1, and Agenda: architecture map

This is a text map of the `1.11.0-beta.1` design. It separates record
ownership, runtime processes, and external authorities. A file link or role
name does not prove that a service, provider connection, or permission exists.

## Mind map

```text
Selected .SYSTEMX root or Projects/NAME/.SYSTEMXP child
|
+-- Agent 0: canonical task planning, delegation, integration, acceptance
|   +-- WORK/TASKS.json: one task status and acceptance authority
|   +-- GLOBAL/CONTEXT.md and PLAN/: accepted project facts and milestones
|
+-- Agent Beta (agent.b): optional BOT/DOT workspace metadata
|   +-- AGENTB/: named offline workspaces, kind, canonical task references
|   +-- Optional online-reference: nonsecret provider/identity aliases,
|   |   selected-scope ACC- decision; still online=false
|   +-- Actual online destination: separate connection and permission check
|   +-- No secret store, model process, or automatic synchronization
|
+-- Agent1 (agent.1; security-access): opt-in advisory assessment
|   +-- SECURITY/AGENT1/: fixed question and event-bucket catalog
|   +-- local/AGENT1-CONFIG.json: ignored warning-only local config
|   +-- GLOBAL/ACCESS-MATRIX.json: 20 default-deny role rows; empty
|   |   reviewed decisions until a selected-scope decision-add
|   +-- GLOBAL/ACCESS-MATRIX.md/.xlsx: guidance and stock Excel view;
|   |   live scoped table is JSON/CSV, not an external IAM policy
|   +-- .env: private source, names-only inventory/sanitized example;
|   |        explicit one-name Actions set with hidden input
|   +-- Local credential store: separate owner-selected destination
|   +-- GitHub Actions secret: separate provider-selected CI destination
|   +-- Read-only stdio session: status/start; ping/capabilities/assess/stop
|
+-- Agent Alpha (agent.a): selected reference requests
|   +-- Agenda: blank settings and access-matrix view
|   +-- AUTOBOT/: existing bounded reference panel
|   +-- No scheduling or notification process
|   +-- session-settings --compact: rule count and revision digest
|
+-- Agent X: observed events and due items in EVENTS/
|   +-- due is read-only; external scheduler remains separate
|
+-- Agent Y: one authorized CLI provider handoff in JOBS.json
|   +-- Provider account, worktree, branch/PR are separately verified
|
+-- Agent Z: requested evidence review
|
+-- Template lifecycle (outside selected project task authority)
|   +-- VERSION + SOURCE.json + Python package metadata + release manifest
|   +-- Read-only template CI, local verification, immutable beta tag
|   +-- Release counter: on-demand GitHub software/media/deployment records
|   +-- Current public images and white paper; prior media in tagged history
|   +-- Raw Blender/large authoring data: external or ignored storage
|
+-- External authorities
    +-- OS user/session and credential store
    +-- GitHub account, repository, org, Actions, environment
    +-- Optional external scheduler, online BOT/DOT source, cloud copy
```

## Data and control edges

| From | To | Flow | Check at boundary |
| --- | --- | --- | --- |
| Owner/Agent 0 | Agent Beta | Named BOT/DOT workspace plan | Selected root/child, name, kind, `local` or `online-reference`, and opt-in. Online references need nonsecret provider/identity aliases and may cite an existing selected-scope ACC- decision. All current records have `online: false` and do not contact a service. |
| Agent Beta | `AGENTB/` | Registration, offline workspace, and existing task ID reference after reviewed apply | Preserve blank template and existing records; no credentials or provider output. |
| Agent Beta | Access Matrix | Optional `access-link` to a same-actor reviewed-intent ACC row | Create BOT/DOT first, then decision, then preview/link with combined BOT/matrix revision. Metadata remains offline; no identity or IAM grant is verified. |
| Owner/Agent 0 | Agent1 | Advisory assessment and setup request | Confirm selected scope and whether `agent.1` is free for `security-access`. Setup registers the role and ignored local configuration; no task authority is transferred. |
| Agent1 | `SECURITY/AGENT1/` and `local/AGENT1-CONFIG.json` | Fixed catalog plus optional ignored local configuration | Setup stores first-run review answers locally; assessment is returned on demand. Do not retain values or raw `.env` lines. |
| Agent1 | Access matrix | Read/view and proposed decisions | Matrix describes reviewed intent; actual OS/GitHub ACL is checked separately. |
| Private `.env` | Agent1 inventory / GitHub Actions | Names-only inventory; optional one-name interactive Actions set | Confirm account/repo/scope, enter one value through hidden input, test the consumer, rotate as needed. The current command does not import into a local store or read values from `.env`. |
| IDE/client | Agent1 stdio session | Bounded JSON-lines requests | Explicit launch, selected scope, fixed methods, no credential fields, no network listener or daemon. |
| Agent Alpha | Agenda | Read selected blank settings/access view | No recurrence or notification side effect. |
| Agent X | `EVENTS/` | Event/due observations | `due` is read-only; external scheduler controls any actual recurrence. |
| Agent Y | Provider/GitHub | Scoped CLI handoff | Verify provider account, binary, repo, branch, write scope, and actual PR state under Agent Y's existing contract. |
| Agent 0 | `WORK/TASKS.json` | Acceptance and current state | Original evidence and selected scope; no other component creates a competing status authority. |
| Selected IDE or harness | `session-settings` | One read-only packet with Beta/Agent1/Agenda status and bounded Rules paths and SHA-256 hashes | No Rules text, secret, provider account, access grant, or live cloud state is asserted. |
| Selected reviewer | `agenda decision-add` | One revision-guarded selected-scope decision for a fixed role or named instance | Preview before apply; a record of intent is not proof of actor identity or an IAM change. |
| Maintainer | `release_counters.py` | Timestamped GitHub release and deployment record counts | `unknown` on missing provider data; a template release is not an application deployment. |

## Status vocabulary

For every claimed capability, report three facts independently:

1. **Source:** present in the selected release, planned, or absent.
2. **Local observation:** tested on the named OS/host and revision, failed,
   stale, or untested.
3. **External outcome:** provider or consumer readback, failed, unknown, or not
   applicable.

For the current stdio service, `service status` is a capability report; it is
not a persistent service monitor. `ping` confirms only an active protocol
session. `assess` reports an advisory local assessment; it cannot attest to
GitHub IAM or a usable CI secret without separate provider evidence. A process
exit, protocol error, or stale observation must not be called healthy.
macOS-local tests alone do not establish Windows or Linux behavior. Future OS
installation adapters must explicitly identify their resource, process owner,
configuration fingerprint, last probe, and removal evidence.

The stock Access Matrix lists 20 default-deny role and instance types. Actual
agent registration, BOT/DOT creation, provider authentication, and native
subagent identity are separate observations. A workbook row or CLI decision
does not grant access. The checked-in XLSX is the stock catalog; selected-scope
changes live in canonical JSON and can be exported as CSV for spreadsheet use.

## Ownership and lifecycle

```text
Preview -> choose selected scope and owner -> record blank configuration
        -> optional Beta/Agent1/Agenda activation -> local validation
        -> explicit read-only session start when needed -> stop/EOF
        -> inspect external resources -> reversible .SYSTEMX uninstall
        -> optional restore or separately verified external cleanup
```

The current managed installer previews and pins `.SYSTEMX` but does not install
OS services, schedulers, GitHub Actions secrets, online BOT/DOT connections, or
providers. The current uninstaller archives the entire folder to a new external
backup; it does not revoke a credential, close a PR, stop a provider process, or
delete cloud copies. Keep those actions in the external resource inventory and
verify them at the owning boundary. Raw Blender and other large authoring files
belong in external or ignored storage, not the public template distribution.
See [setup](../.SYSTEMX/Setup/README.md),
[service protocol](../.SYSTEMX/Setup/SERVICE.md), and
[uninstall](../.SYSTEMX/Uninstall/README.md).
