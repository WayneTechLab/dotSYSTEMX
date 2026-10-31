# Access matrix and project map

The [root access matrix](../GLOBAL/ACCESS-MATRIX.md) and
[root map](../PLAN/MAP.md) are reusable project records. A selected
`.SYSTEMXP` child receives its own access guidance and blank `PLAN/MAP.md`.
Populate decisions only in the selected scope after adoption; never copy
another project's identities, topology, task history, or private evidence.

## Access decisions

Use the matrix when the project has protected data, privileged actions, shared
resources, or distinct environments. For each reviewed access path, identify
the actor or role, resource, action, allow/deny/defer decision, environment or tenant,
decision owner, applicable policy or approval, verification evidence, and review
or expiry condition. State `unknown`, `not applicable`, or `deferred` with a
reason and owner instead of inventing a permission.

The matrix records intent and review history. Actual authorization is enforced
by the relevant operating system, repository, cloud provider, application, or
service. An Agent 0/X/Y/Z/Alpha registry entry is not an authenticated identity or a
grant. If [Agent Y](AGENT-Y.md) uses a selected CLI, review that process's
actual account, filesystem access, Git remote, branch, and PR permissions as
separate access paths. Confirm the live account, target, and permission at the
external boundary before a consequential action. Keep credentials and secret
values out of records.

The structured [Access Matrix JSON](../GLOBAL/ACCESS-MATRIX.json) ships 20
standard `roleDefaults` rows: Agent 0/1/X/Y/Z/Alpha/Beta, three instance
patterns for numeric workers, native subagents and Agent Beta BOT/DOT workspaces,
and ten fixed AUTOBOT references. Every row has `templateGrant: none` and
`requiresReview: true`. The checked-in [Excel view](../GLOBAL/ACCESS-MATRIX.xlsx)
shows those same stock rows. Neither file gives a user, process or provider
access. The JSON `decisions` array starts empty; reviewed records use stable
`ACC-` IDs and `reviewed-intent`, `denied`, or `gap` outcomes.
The [decision-rules catalog](../GLOBAL/ACCESS-DECISION-RULES.json) defines
those outcomes, required fields, and review conditions without inserting a
project decision. Agent Alpha's [Agenda settings catalog](../AUTOBOT/AGENDA-SETTINGS.json)
defines the fixed AUTOBOT context choices and their `unset` defaults. The
[selected Agenda JSON](../AUTOBOT/AGENDA.json) still has an
empty `options` array. Stock definitions are configured; an adopter's choices,
identities, approvals, and permissions are not.

| Stock rule | Effective template value | Project-specific action |
| --- | --- | --- |
| AUTOBOT `context_selection` | `unset` when no option is recorded; no automatic inclusion | Review one fixed Rules file and selected-scope access decision before `include`; `exclude` is an explicit recorded choice. |
| Role access | `templateGrant: none`, `requiresReview: true` | Verify the real actor and provider/OS permission separately. |
| Access decision | No row, so no reviewed intent or grant | Record `gap`, `denied`, or `reviewed-intent` with actor, resource, action, environment, owner, evidence, review time, and any required policy reference. |

From the containing project directory, inspect the catalogs and selected
scope before making a change:

```bash
bash .SYSTEMX/SYSTEMX.sh agenda catalog
bash .SYSTEMX/SYSTEMX.sh agenda status
bash .SYSTEMX/SYSTEMX.sh agenda decision-add --help
bash .SYSTEMX/SYSTEMX.sh agenda set --help
```

Windows PowerShell uses `pwsh -File .SYSTEMX/SYSTEMX.ps1 agenda catalog`.
For a real project decision, take `accessRevision` from `agenda status`, fill
the exact actor/resource/action/environment/owner/evidence fields in
`agenda decision-add`, and preview with `--expected-revision ACCESS_REV`.
Apply the same reviewed command with `--apply` while that revision is still
current. `reviewed-intent` additionally needs a nonsecret `--policy-ref`; the
result still reports `identityVerified: false` and `accessGranted: false`.
For a context choice, `agenda set` uses `agendaRevision`, a fixed AUTOBOT ID,
its exact Rules path, and a separate preview/apply. `include` requires a
same-scope reviewed-intent decision; the Rules digest is checked again at
apply time. A revision mismatch or changed Rules file calls for a fresh review.

Agent Alpha's [Agenda JSON](../AUTOBOT/AGENDA.json) can refer to one of those IDs
when selecting advisory context. `agenda status` and `agenda table --format csv`
read the canonical JSON and report whether referenced Rules files still match
their reviewed digests. `agenda status` returns an `accessRevision`; use that
with `agenda decision-add --expected-revision SHA256` to preview one scoped
decision, then repeat with `--apply` after review. A registered Agent Beta
instance uses `agentb:BOT_NAME`; a native worker uses
`native-subagent:HOST:ID`. The command validates the actor and record shape,
but `identityVerified` and `accessGranted` remain false until checked at the
actual provider. In a child scope, `agenda init` previews and adds the stock
role and rule catalogs with empty decisions and selected settings only after
explicit selection. An adopted beta.1 scope may show `agenda catalog` as a
`distribution-preview` with `installed: false`; review `agenda init`, activate
Agent Alpha if needed, then apply `agenda init --apply` to add the missing
catalog pair without replacing existing options or decisions. Recheck
`agenda status` for `catalogsInstalled: true`.
For a new BOT/DOT instance, create its blank Agent Beta record first. After
recording a same-actor `reviewed-intent` decision, `agent-beta access-link
BOT_NAME --access-decision-id ACC-001` previews the link; repeat it with the
preview's combined BOT/matrix `revisionBefore` and `--apply`. The link remains
offline metadata, not a permission change.
For an adopted legacy matrix without `roleDefaults`, `agenda roles-upgrade
--expected-revision ACCESS_REV` previews the additive catalog; repeat with
`--apply` to preserve existing decisions and options while adding the 20
default-deny rows.

The distributed workbook is a human-readable default catalog. It is not a
live editor of scoped JSON decisions or an authorization source. For a live
Excel-readable view, `agenda table --format csv` returns JSON containing
separate `roleCsv`, `accessCsv`, `agendaCsv`, `settingCsv`, and
`decisionRuleCsv` text. The checked-in stock XLSX has five sheets, including an
Agent 0 roster. To make a current six-sheet selected-scope XLSX, preview
`agenda workbook-export`, take its `sourceRevision`, then apply with
`agenda workbook-export --expected-revision SHA256 --apply`. The generated
formula-free workbook is written only under the selected scope's ignored
`local/` directory. `agenda workbook-check` compares it with current JSON and
reports `current: false` after the source changes. Preserve the canonical JSON
and its revision when exporting or sharing a view.

For [AUTOBOT](AUTOBOT.md), separately record who may view or change detailed
brand, policy, research, and private-source references. A request's caller label
is attribution, not permission evidence. [DATA](DATA.md) ignore rules influence
Git additions, not local access, cloud sharing, or external sync. Map the actual
storage boundary and approved retrieval path when payloads are sensitive.
When an access gap requires work, create or update a task in the selected
`WORK/TASKS.json`; do not add status columns or competing checkboxes here.

## Source and system boundaries

Use the map when a navigation view helps the team locate code, data, interfaces,
and owners. Cite the actual architecture, repository path and revision,
configuration, inventory, or observed endpoint for each entry. Distinguish a
planned connection from an implemented one and an observed live path from a
source-only description. A URL in `SOURCES.json` or a map is a reference; it
does not mount Drive, fetch a repository, open a chat, or prove access.

The map is supporting navigation. `GLOBAL/CONTEXT.md` owns accepted project
identity and source hierarchy; `PLAN/MASTER-PLAN.md` owns outcomes and
milestones; `WORK/TASKS.json` owns task state, dependencies, and acceptance
evidence; `WORK/FOCUS.json` owns the selected objective; and original source
files or external systems remain authoritative for their actual implementation
and permissions. Link these records rather than copying their changing content.

An optional Agent Y handoff may cross app, CLI, worktree, and GitHub boundaries;
map the actual source and destination only when they exist. Its PR is a delivery
artifact linked to the canonical task, not another project or task ledger.

## Scope and upkeep

Root records cover the outer project or shared workspace. Child records cover
only the explicitly selected `.SYSTEMXP`. Use qualified references for
cross-project links, and reconcile shared policy with child-specific decisions.
Neither file is part of the default bounded agent context packet; open the
relevant section when the task needs it to avoid loading an entire inventory
on every turn.

Review entries after a material change to identity, resource, environment,
architecture, or ownership. Preserve prior evidence and record the observation
date and revision. These Markdown records are not executable policy, an access
scanner, a topology crawler, or production-readiness proof. The CLI validates
their location and local links as distribution files, not the truth of their
claims. See [security](SECURITY.md), [evidence](EVIDENCE.md), and
[SYSTEMX PROJECTS](PROJECTS.md).
