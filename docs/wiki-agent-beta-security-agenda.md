# Agent Beta, Agent1, and Agenda

> Source companion for the `1.11.0-beta.2` GitHub Wiki page. Verify the selected
> release and command help before operating a project.

`.SYSTEMX` keeps one project task authority while offering three optional
extensions:

| Extension | What it adds | What it never implies |
| --- | --- | --- |
| Agent Beta (`agent.b`) | Named BOT/DOT workspaces and canonical task references in `AGENTB/`; an `online-reference` may retain nonsecret provider/identity aliases and an access-decision reference. All current records remain offline. | A connected provider, synchronized remote workspace, model process, or credential permission. |
| Agent1 (`agent.1`, `security-access`) | A guided local security/access assessment, safe credential-name inventory and migration plan, plus an explicitly started read-only stdio session. | A secret vault, GitHub admin role, automatic upload or rotation, permanent daemon, or task acceptance. |
| Agent Alpha Agenda | Stock setting and decision-rule definitions, with empty selected project options and decisions. | A scheduler or notification worker. Agent X owns observed events and due items. |

Agent 0 remains the coordinator. `WORK/TASKS.json` remains the only task-status
and acceptance record. Agent Y's CLI jobs, Agent Z's reviews, Agent X's event
history, and Agent Alpha's reference requests keep their existing boundaries.
Activating a role record does not start an AI provider or grant IAM rights.

## Start with a selected scope

Use the exact `.SYSTEMX` name. Choose the containing root or an explicitly
registered `Projects/NAME/.SYSTEMXP` child; do not infer the scope from the
last chat or current shell directory. The managed first-run command previews
the installation and empty configuration before `--apply`. It installs no OS
service or scheduler. See [First-Time Setup](https://github.com/WayneTechLab/dotSYSTEMX/blob/main/.SYSTEMX/docs/FIRST-RUN.md)
and the [operator setup page](https://github.com/WayneTechLab/dotSYSTEMX/blob/main/.SYSTEMX/Setup/README.md)
for the current source.

An Agent1 first-run review asks for the project owner, host and OS, actual
owner/guest roles, GitHub account and repository, permitted Actions use,
credential **names** and destinations, suspected exposure, and backup/cleanup
plan. Unknown answers remain unknown. Beta's online workspaces and Alpha's
Agenda has stock setting definitions, but selected options start empty and
are opted into separately. The decision-rule catalog defines allowed outcomes;
it does not supply a project-specific decision.

## Keep local and CI secrets separate

GitHub Actions secrets serve workflows; they do not configure a local shell,
keychain, `.env` file, or Agent1 session. Local credentials belong in an
approved OS credential store or other selected local secret manager. An ignored
`.env` file is still plaintext. Actions variables are suitable only for
nonsensitive values.

Choose repository, named environment, or organization scope deliberately.
Same-name precedence is environment, then repository, then organization.
Environment approval/branch controls depend on actual settings and plan.
`gh secret list` reports names and scopes, not values. GitHub's
[Actions secrets guide](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets),
[secrets reference](https://docs.github.com/en/actions/reference/security/secrets),
and [CLI secret manual](https://cli.github.com/manual/gh_secret_set) provide the
current provider behavior.

For `.env` migration, inventory key names privately; classify each as secret,
public setting, or obsolete; optionally preview a names-only `.env.example`
with `agent-1 env-sanitize`; choose a destination for each; confirm the active
account and exact repository/environment before any import; verify an actual
consumer without echoing the value; rotate at the source if exposure is
suspected; and only then retire old plaintext under the owner's retention
policy. `env-migrate` defaults to a newly issued credential intent. Reuse of
an existing test credential requires `--credential-class existing-test` and
`--ack-test-only`; this assertion does not verify rotation. No first-run action
bulk uploads or removes a `.env` file. See the
[security spec](https://github.com/WayneTechLab/dotSYSTEMX/blob/main/docs/agent-beta-security-agenda.md#env-migration-and-rotation-sequence).
For an explicit repository or named-environment secret set, Agent1 verifies
the active GitHub account's repository admin permission before hidden input.
An owner/operator/guest setup label is descriptive; verified guest admins may
proceed. It reads back secret name/scope metadata only, returning `unknown`
when readback cannot verify the name. It does not verify a value or workflow
consumer. Organization secret writes are outside this beta CLI.

## Owner and guest access

A `.SYSTEMX` Access Matrix ships 20 standard role rows with `templateGrant:
none` and `requiresReview: true`: seven agent roles, ten AUTOBOT references,
and instance patterns for numeric workers, native subagents, and Agent Beta
BOT/DOT workspaces. Its reviewed `decisions` array starts empty. Use
the [Agenda settings catalog](https://github.com/WayneTechLab/dotSYSTEMX/blob/main/.SYSTEMX/AUTOBOT/AGENDA-SETTINGS.json)
and [Access Decision Rules catalog](https://github.com/WayneTechLab/dotSYSTEMX/blob/main/.SYSTEMX/GLOBAL/ACCESS-DECISION-RULES.json)
to inspect allowed values, `unset` defaults, and required review
fields. `agenda catalog` reads both definitions without changing the selected
scope. From the containing project directory:

```bash
bash .SYSTEMX/SYSTEMX.sh agenda catalog
bash .SYSTEMX/SYSTEMX.sh agenda status
bash .SYSTEMX/SYSTEMX.sh agenda decision-add --help
bash .SYSTEMX/SYSTEMX.sh agenda set --help
```

For Windows PowerShell, use `pwsh -File .SYSTEMX/SYSTEMX.ps1 agenda catalog`.
An absent option is `unset`: Agenda includes nothing automatically. An
explicit `exclude` records a reviewed exclusion;
`include` requires a reviewed-intent access row and current Rules digest. A
decision outcome can be `gap`, `denied`, or `reviewed-intent`; none is an
external access grant. Use
`agenda status` to obtain `accessRevision` and `agenda decision-add` with that
revision to preview or apply one selected-scope intent, denial, or gap. The
checked-in five-sheet XLSX shows the default rows and Agent 0 roster. Live CSV
fields from `agenda table --format csv` reflect scoped JSON records and fixed
definition catalogs. An
explicit `agenda workbook-export` writes a current, formula-free six-sheet
workbook under ignored `local/`, guarded by the
source revision; `agenda workbook-check` detects drift. None is an OS or
GitHub grant. An adopted older matrix can preview `agenda roles-upgrade` to
add the stock role rows without replacing decisions, then apply it with the
observed revision.

For a named BOT/DOT, create its Agent Beta record first, then a same-actor
`reviewed-intent` row for `agentb:BOT_NAME`. Preview `agent-beta access-link
BOT_NAME --access-decision-id ACC-001`; repeat with its combined BOT/matrix
`revisionBefore` as `--expected-revision REVISION --apply`. The reference
remains offline metadata and grants no external permission.

A guest with repository Write access can alter workflows and may arrange
use or exfiltration of Actions secrets. If a guest must not reach those secrets,
use a less privileged role or a separate repository and verify actual branch
and environment controls. A nested role label cannot provide that separation.
See [GitHub's secure-use guidance](https://docs.github.com/en/actions/reference/security/secure-use)
and [repository roles](https://docs.github.com/en/organizations/managing-user-access-to-your-organizations-repositories/managing-repository-roles/repository-roles-for-an-organization).

## Read-only session and status

`session-settings` returns a single selected-scope JSON packet with Agent
Beta, Agent1, and Agenda status plus fixed AUTOBOT and registered Beta Rules
paths and SHA-256 hashes. It does not return rule contents, secret values,
provider accounts, or live permission state. Select a child with
`projects session-settings --project NAME`. Use `--compact` to return only a
rule count, absent IDs, and a revision digest when file-level paths are not
needed. On the blank root template this reduced output from 3,248 to 1,043
bytes; that is a byte count, not a billed-token benchmark.

The first Agent1 service is a short-lived stdio process. `service status`
reports local capability; `service start --stdio` starts the protocol for a
client that owns both pipes. It accepts fixed `ping`, `capabilities`, `assess`,
`roster`, `settings`, `onboard`, and `stop` methods. The last three expose
selected-scope Agent 0 and setup views. It is custom JSON-lines, not MCP or
ACP. It has no listening port, background installation, or
secret-field input. An `assess` response is advisory local evidence, not proof
of remote IAM, a working secret, or a running deployment. The
[service protocol](https://github.com/WayneTechLab/dotSYSTEMX/blob/main/.SYSTEMX/Setup/SERVICE.md)
gives exact framing and limits after merge.
The beta source has been exercised on the current macOS development host;
Windows and Linux runtime/install behavior must be tested before being claimed.

Warnings about missing, stale, or unsafe facts are on by default. Alpha's
Agenda view does not dispatch a warning or job on a timer. Agent X `due` can
show due items on request; an external scheduler, if separately authorized,
owns actual recurrence, timezone rules, retries, and notifications.

## Remove or restore

Stop active writers and the stdio client, inspect external resources, then
preview `systemx uninstall --target PROJECT --backup NEW_EXTERNAL_PATH`.
`--apply` moves the entire `.SYSTEMX` folder to that new same-filesystem backup
and records an inventory/receipt. `systemx audit --target PROJECT` checks only
the selected project footprint. `systemx restore` previews and verifies a
return into an empty slot. The folder operation does not remove a Python
environment, GitHub secret, provider job, PR, cloud copy, or separately
installed scheduler. The [operator uninstall page](https://github.com/WayneTechLab/dotSYSTEMX/blob/main/.SYSTEMX/Uninstall/README.md)
and [core uninstall guide](https://github.com/WayneTechLab/dotSYSTEMX/blob/main/.SYSTEMX/docs/UNINSTALL.md)
describe those scopes after merge.
