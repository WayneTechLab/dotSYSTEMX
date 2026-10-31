# Agent Beta, Agent1, and Agenda

**Specification for `1.11.0-beta.2`.** These three names have separate jobs.
Beta packaging and local checks do not establish every host or provider outcome.
A role record or a
document does not authenticate an agent, grant access, launch a model, or start
an operating-system service.

## Product contract

| Area | Owner and purpose | Does not do |
| --- | --- | --- |
| Agent Beta (`agent.b`) | Optional local **BOT/DOT workspace metadata** under `AGENTB/`, including an opt-in `online-reference` with a nonsecret provider identity alias and selected-scope access-decision reference. | No credential broker, security assessment, provider process, task coordination, or automatic online sync. Current metadata marks each BOT/DOT `online: false`. |
| Agent1 (`agent.1`, `security-access`) | Opt-in **security and access assessment**, safe `.env` inventory/migration planning, and a bounded read-only local session service. | No secret-value collection in shared records, automatic upload/rotation, GitHub IAM grant, task acceptance, or always-on daemon. `agent.1` can be selected only when that numeric ID is not already assigned to another worker role. |
| Agent Alpha Agenda | A **settings and access-matrix view** with stock value/rule definitions and empty project-specific selections. | No scheduler, recurrence engine, notification delivery, or second event ledger. Agent X owns events and due items. |

Agent 0 remains the selected project's coordinator and accepts work in
`WORK/TASKS.json`. Agent X records observed events and due items; its `due`
operation is read-only. Agent Y owns a single bounded CLI handoff when
activated. Agent Z reviews. Agent Alpha routes selected reference requests and
owns the Agenda view. Beta and Agent1 cite the canonical records instead of
creating another task, job, review, or event status database. See the current
[agent entry point](../.SYSTEMX/AGENTS.md),
[Agent X](../.SYSTEMX/docs/AGENT-X.md),
[Agent Y](../.SYSTEMX/docs/AGENT-Y.md), and
[AUTOBOT](../.SYSTEMX/docs/AUTOBOT.md).

## Current implementation boundary

`session-settings` gives an IDE, harness, or bot a bounded read-only JSON
packet for one selected scope: Beta/Agent1/Agenda status, Access Matrix
revisions, and canonical fixed AUTOBOT and registered Beta Rules paths and
SHA-256 hashes. It does not include rule text, credentials, or provider state.
`session-settings --compact` substitutes a rule count, absent IDs, and a
revision digest when individual paths are unnecessary. The blank root packet
measured 3,248 bytes in full form and 1,043 bytes in compact form; this is
output size, not a billed-token or latency measurement.

The beta release adds file and CLI surfaces for these roles. The concrete
commands and schema must be read from the selected release's help before an
operator applies a change. Agent1's first service transport is the explicitly
started **stdio** session described in
[SERVICE.md](../.SYSTEMX/Setup/SERVICE.md): `service status` inspects capability;
`service start --stdio` handles bounded read-only requests and exits at `stop`,
EOF, or its request limit. It does not install a daemon, open a listening port,
persist after the client exits, or provide a secret vault. The protocol methods
are `ping`, `capabilities`, `assess`, `roster`, `settings`, `onboard`, and
`stop`. The last three expose selected-scope Agent 0, compact settings, and
unset provider setup views through custom JSON-lines, not MCP or ACP.
A successful service process
means a local protocol response was observed; it does not prove a GitHub account,
secret, workflow, or external permission works. Native macOS test results do
not establish Windows or Linux installation/runtime support. The process
inherits its launcher's OS permissions; run it as a normal user.

An Agent1 assessment is advisory and based on visible local evidence. The
current result identifies the selected project root, profile, warning codes,
question counts, local filename/host signals, and explicit limits. It does not
include a trusted observation timestamp, source revision, external identity,
or provider permission proof. `unknown` or `unavailable` is the honest result
for an external identity, policy, or service that was not checked. The public
template keeps private project facts blank.
The shipped catalog has 20 categories with 20 evidence questions each and ten
event buckets with exclusive ownership rules. `agent-1 questions` displays a
selected profile/category; `agent-1 review --answers FILE` validates complete
answer coverage and syntax without opening or authenticating evidence paths.
The bounded `agent-1 check` answers zero catalog questions, so a filename
warning must never be reported as a control pass or a clean device.

## Template settings and Access Matrix rules

`GLOBAL/ACCESS-MATRIX.json` is the canonical selected-scope table. A new beta
scope ships 20 standard role rows: Agent 0, X, Y, Z, Alpha, Beta, Agent1;
numeric worker, native-subagent, and Agent Beta BOT/DOT instance patterns;
and ten fixed AUTOBOT references. All rows have `templateGrant: none` and
`requiresReview: true`. The `decisions` array is empty in the public template.
The [Access Decision Rules catalog](../.SYSTEMX/GLOBAL/ACCESS-DECISION-RULES.json)
defines the supported outcomes and required review fields. The
[Agenda Settings catalog](../.SYSTEMX/AUTOBOT/AGENDA-SETTINGS.json) defines
the ten fixed AUTOBOT `context_selection` choices, allowed values, and safe
effective defaults. The selected-scope `AUTOBOT/AGENDA.json` still has
`options: []`. These catalogs set up the reusable template without inventing
an adopter's user, resource, evidence, approval, or permission.

| Area | Stock setting or rule | Effective value until project review |
| --- | --- | --- |
| Agenda context selection | One fixed AUTOBOT Rules path per ID; allowed recorded values `include` or `exclude` | `unset` when no option row exists; no reference is loaded automatically |
| Role entry | `templateGrant: none`; `requiresReview: true` | No template grant, including for future BOT/DOT and subagent instances |
| Access decision | Allowed outcomes `gap`, `denied`, `reviewed-intent` | No row and no reviewed permission intent |
| Reviewed intent | Actor, resource, action, environment, owner, evidence, review time, nonsecret policy reference | Recorded plan only; external identity and permission remain unverified |

The checked-in five-sheet XLSX presents the stock rules, role rows, and Agent 0
roster for human review;
it does not synchronize live changes or enforce access. Use the project-local
launcher to see the same definitions and current selected-scope state:

```bash
bash .SYSTEMX/SYSTEMX.sh agenda catalog
bash .SYSTEMX/SYSTEMX.sh agenda status
bash .SYSTEMX/SYSTEMX.sh agenda decision-add --help
bash .SYSTEMX/SYSTEMX.sh agenda set --help
```

On Windows, the catalog command is
`pwsh -File .SYSTEMX/SYSTEMX.ps1 agenda catalog`. A real decision first previews with the `accessRevision` from
`agenda status` as `--expected-revision`; applying requires the same reviewed
fields plus `--apply`. A real context choice uses `agendaRevision` in the same
preview/apply pattern. `include` requires a selected-scope `reviewed-intent`
decision and a Rules file whose digest remains current. The CLI rejects a
stale revision or changed Rules file. Neither command changes provider IAM.

Use `agenda status` to read `accessRevision`, then `agenda decision-add` with
that revision to preview or apply one `ACC-` decision. It accepts a registered
agent, fixed AUTOBOT, registered numeric worker, `native-subagent:HOST:ID`,
or `agentb:BOT_NAME` recorded in this scope. A `reviewed-intent` record needs
a nonsecret policy reference. The result reports `identityVerified: false`
and `accessGranted: false` because the CLI does not query or change IAM.
`agenda table --format csv` returns five CSV strings inside JSON, including
the fixed setting and decision-rule catalogs. An explicit
`agenda workbook-export --expected-revision SOURCE_REV --apply` writes a
formula-free six-sheet XLSX under ignored `local/`; `agenda workbook-check`
compares it
with current JSON. Upgrades retain an adopted scope's older matrix bytes,
which may have no role catalog until `agenda roles-upgrade` is explicitly
previewed and applied with its observed access revision.

For a new Agent Beta BOT/DOT, create the local workspace first. Record a
same-actor `reviewed-intent` decision for `agentb:BOT_NAME`, then preview
`agent-beta access-link BOT_NAME --access-decision-id ACC-001`. Apply the link
with the preview's combined BOT/matrix `revisionBefore` using
`--expected-revision REVISION --apply`. This stores a reference while keeping
`online: false`, `identityVerified: false`, and `accessGranted: false`.

## Threat model and controls

**Assets:** credential values, GitHub Actions secrets, repository and
organization permissions, project and backup contents, `.env` files, local
service I/O, BOT/DOT references, and evidence. **Actors:** owner, invited
guest, repository writer/admin, local same-user process, workflow author,
third-party action, and compromised host/dependency. **Boundaries:** local
workstation to GitHub; one repository/environment/organization to another;
owner to guest; shared `.SYSTEMX` records to host-local data; an online
reference to actual remote access; and a saved due item to a scheduler.

| Risk | Required behavior |
| --- | --- |
| Secret value enters Git, chat, task, logs, arguments, URLs, screenshots, or a shareable backup. | Portable records contain names and references only. Assessments redact values and structured errors. Check tracked and ignored status before exports. If exposure occurred, revoke or rotate first and follow the incident process. Git ignore is not access control. |
| Guest edits a workflow able to use a secret. | Do not promise secrecy from a repository writer. Review workflow and action changes, protected branches, environments, and least privilege. Give Read/Triage access or a forked PR path to guests who must not reach CI secrets. |
| Wrong local/GitHub account or target is used. | Show the active account, exact owner/repository/environment and operation before a provider write. At apply time require GitHub's `permissions.admin == true` for the target repository; refuse unknown or false permission. Never print the token. `GH_TOKEN` may override stored `gh` authentication. Organization writes are outside this beta CLI. |
| `.env` is mistaken for a vault or imported in bulk. | Treat it as plaintext source material; inventory key names only, classify each key, choose each destination, and require explicit import. No setup side effect uploads or deletes the file. |
| BOT/DOT provider alias or access row is treated as proof. | Record the selected source and nonsecret alias; verify any real provider connection separately. A label or matrix decision is not an authenticated session or IAM grant. |
| Process is alive but assessment or external outcome failed. | Separate process/protocol status from the assessment result and from external consumer health. Show stale or inaccessible evidence as `unknown`. |
| Agenda is interpreted as an executor. | Stock setting definitions are present, but selected options start empty; Agenda is access context, not a scheduler. Agent X's due ledger does not execute; an external scheduler needs its own explicit setup and verification. |
| Local uninstall leaves external resources active. | Inventory every separately installed scheduler, provider job, worktree, cloud copy, or secret. Verify removal through its owner. The core folder uninstall only archives `.SYSTEMX`. |

This design reduces accidental disclosure and authority confusion; it is not a
same-user sandbox. A compromised user session or a repository writer with
workflow control may reach material available to that identity.

## GitHub Actions and local secrets

GitHub Actions secrets serve workflows. They do not populate a local shell,
OS credential store, `.env` file, Agent Y provider, or Agent1 session. A local
credential store is a separate destination. An ignored `.env` file remains
plaintext. An `.env.example` can contain names and descriptions, never values.
Actions variables are for nonsensitive settings and are not masked as secrets.
Any later secret inventory may record only metadata such as name,
destination, scope, owner, observation time, and rotation decision. The
current Agent1 setup records the chosen target **type** and review answers in
ignored `local/AGENT1-CONFIG.json`, not secret names or values. It must never
store a value, token prefix, or a reversible digest in shared records.

Changing an existing setup record is preview-first and requires all eight
answers again: `--account-context`, `--repo`, `--review-scope`, `--actor-role`,
`--secret-target`, `--local-secret-store`, `--env-history-reviewed`, and
`--rotation-decision`. The preview returns `proposed`, `applyRequired`, and
`existingSHA256`. Apply the reviewed change by repeating those answers with
`--apply --replace-existing --expect-sha256 SHA_FROM_PREVIEW`; a changed record
or missing answer is refused. This changes only local warning-only metadata.

For Actions, choose the smallest useful scope: repository, named environment,
or organization with an explicit repository allowlist. Same-name precedence is
environment over repository over organization. Repository and organization
secrets are read when a workflow is queued; environment secrets are read when
the job starts. Environment reviewer and branch controls depend on the actual
plan and settings. `gh secret list` can confirm metadata, not read back values.
Prefer OIDC to a long-lived cloud credential where the provider supports it.
GitHub's current [secret guide](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets),
[secrets reference](https://docs.github.com/en/actions/reference/security/secrets),
[secure-use guidance](https://docs.github.com/en/actions/reference/security/secure-use),
and [OIDC guidance](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-cloud-providers)
govern the provider side.

| Persona | Authorized design action | Actual authority source |
| --- | --- | --- |
| Owner | Selects target, local/CI destination, import/rotation, and acceptance. | OS and GitHub permissions at action time. |
| Guest Read/Triage | Reviews sanitized plan/evidence. | Actual repository role; no implied secret administration. |
| Guest Write | May change workflows and thereby arrange use or exfiltration of Actions secrets. Treat as privileged. | Actual repository role and workflow controls. |
| Repository administrator, including a guest | May use the beta repo/environment secret command only when the active `gh` account has verified repository admin permission. | GitHub `permissions.admin == true` at apply time; a `.SYSTEMX` role label is descriptive only. |
| Organization owner | May manage organization-level secrets with separate GitHub tooling and policy. | Outside Agent1's beta `env-migrate` command. |

There is no nested GitHub guest-admin compartment that hides Actions secrets
from someone who can edit the consuming workflow. A `.SYSTEMX` role label cannot
change GitHub IAM. For separation, use distinct repositories/accounts or
withhold write access, then verify actual roles and branch/environment policy.
See [GitHub repository roles](https://docs.github.com/en/organizations/managing-user-access-to-your-organizations-repositories/managing-repository-roles/repository-roles-for-an-organization).

### `.env` migration and rotation sequence

1. In a private owner review, inventory **key names only** and classify each as
   secret, public setting, or obsolete. Do not dump values to a terminal, LLM,
   issue, or diff. Check whether the source file is tracked or was shared.
   `agent-1 env-sanitize` can preview, then explicitly create, a names-only
   `.env.example`; it leaves the source untouched and guards replacement of
   an existing example by its observed SHA-256.
2. Choose one destination per secret: approved local OS credential store for
   local use, narrowly scoped GitHub Actions secret for CI, or both through
   separate explicit imports. Confirm active account and exact target first.
   `gh secret set NAME --repo OWNER/REPO` can receive a value through an
   interactive prompt. Avoid value-bearing shell arguments and bulk
   `--env-file` upload until every key and target has been reviewed. The
   `agent-1 env-migrate` path defaults to `--credential-class new`; its
   `existing-test` option requires `--ack-test-only` and is for a bounded test
   credential. These labels do not verify that a value is newly issued. On
   `--apply`, Agent1 requires GitHub's repository admin permission before
   prompting, regardless of the first-run owner/operator/guest label. The
   beta path supports repository and named-environment targets, not org writes.
3. Read back the name/scope metadata and run a bounded authorized consumer
   check. Agent1 uses `gh secret list --json name` after `gh secret set` and
   reports `metadataReadback.state` as `verified` or `unknown`. A listed name
   proves metadata visibility, not the value or consumer success.
   Never echo a value to verify it.
4. Rotate at the source if exposure is suspected or policy requires it. Update
   consumers, verify, then revoke the old credential. Remove old plaintext
   material only after checking consumers and backups under owner retention
   policy. A tracked value is an incident; never silently rewrite Git history.

These CLI semantics are from the [GitHub CLI secret manual](https://cli.github.com/manual/gh_secret_set).
GitHub's [sensitive-data removal guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
starts with revocation/rotation after exposure.

## First-run questionnaire

The current `agent-1 setup` previews eight answers and a `missingQuestions`
list before `--apply`. Applying requires all eight, registers `agent.1` as
`security-access` when that ID is free, and writes ignored
`local/AGENT1-CONFIG.json`. A conflicting existing `agent.1` role is refused.
Its exact fields are: personal/enterprise account
context; `OWNER/REPO`; root/project review scope; owner/operator/guest actor
role; repository/environment/none Actions secret target; selected local
secret-store **type**; whether tracked `.env` history was reviewed; and
rotation decision (`rotated`, `needed`, or `not-applicable`). Missing CLI
answers remain missing; blank never means consent. Applying setup saves a
warning-only local configuration, with service installation, networking, and
automatic fixes disabled. It does not collect a credential value.
The actor-role answer is descriptive. Secret-write authority comes from an
action-time GitHub repository admin check, not this label.

The operator should additionally review these facts before claiming full
onboarding. They are **not** fields captured by the current setup command:

| Section | Questions for the owner to resolve |
| --- | --- |
| Scope and host | Which exact selected root/child, data class, host, OS, shared/synchronized locations, and private backup destination? |
| Access | Who are guests, what are their actual GitHub/OS roles, and who may approve provider writes and rotation? |
| Credentials | Which **names** are needed locally, in CI, or both? Is OIDC available? Was any value tracked or shared? Never place values in this review record. |
| Actions | Does project policy permit Actions? Which workflows/environments consume each name and what reviewer/branch controls are verified? Treat absence of a policy decision as disabled. |
| Beta | Is a BOT/DOT workspace needed? Is its source `local` or `online-reference`? If online-reference, what nonsecret provider and identity aliases and existing Access Matrix decision identify the planned boundary? Default absent. |
| Agenda | Which context choices and access rows are reviewed intent, denial, or gaps? Stock choices are defined, but selected options and decisions start empty; no schedule execution. |
| Operations | Which external resources, if any, need separate removal and provider readback? Warnings remain on by default. |

## Session and platform status

The beta's read-only Agent1 service is an explicit stdio process, not an OS
service. The client owns its lifecycle and should record the selected scope,
process exit, protocol result, and assessment result separately. The transport
limits requests and response size, rejects credential-bearing fields, and
reserves stdout for protocol JSON lines; see
[SERVICE.md](../.SYSTEMX/Setup/SERVICE.md). It must not claim that an external
permission exists because `ping` or `assess` returned successfully.

Agent1's dotenv and answer-file operations require anchored no-follow file
handles supported by the host. They fail closed on native Windows in this beta:
`env-inventory`, `env-sanitize`, `env-migrate`, and `review --answers` cannot
read or write those files there. Reconfiguring an existing Agent1 setup record
also fails closed, including its preview. Metadata-only first setup, `status`,
`questions`, and the warning-only `check` remain available on Windows. These
limits do not claim an OS malware check or a Windows service installation.

Future optional service installation on macOS `launchd`, Linux `systemd`, or
Windows Service/Task Scheduler would require a separate adapter, owner-selected
scope, preview, install/start/stop/status/uninstall, and platform readback. None
is implied by this stdio protocol. Native Windows Agent Y `run --apply` still
has its separate process-termination refusal; that does not limit core Windows
`.SYSTEMX` records or prove any Agent1 Windows service support.

## Acceptance gates

- Fresh template has no real user, value, host path, enabled schedule, account,
  or installed service. Preview is read-only; apply states exact scope.
- Beta workspaces remain metadata until an explicit online adapter/permission
  check. An unknown or stale reference is labeled as such.
- Agent1 shows only sanitized findings and never treats a role label as IAM.
  Synthetic credentials are used in tests. A provider mutation requires a
  separately authorized operation and action-time account/target check.
- Agent Alpha's Agenda starts with no options, reads the selected access-matrix
  scope, and never creates a scheduler. Agent X remains event/due authority.
- The stdio protocol is tested on each claimed platform. Until then, only the
  actually exercised host is verified; unsupported installation remains
  unclaimed.
- Setup and removal receipts identify the resources each command owns. The
  core reversible uninstall neither deletes provider secrets nor terminates
  external jobs or shared tools.
