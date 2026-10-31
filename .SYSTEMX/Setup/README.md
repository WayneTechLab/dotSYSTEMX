# Optional Agent Beta, Agent1, and Agenda setup

This page is for an **adopted project** using a beta-capable reviewed
`.SYSTEMX` release or checkout. It is not a request to fill the public template
with an account, bot name, host path, secret, or access decision. Keep the
template seeds blank. The [core first-run guide](../docs/FIRST-RUN.md) handles
managed installation and the initial `project.json`; this page begins after
that scope is selected. [SERVICE.md](SERVICE.md) defines the separate Agent1
read-only session protocol.

## 1. Select and verify the exact project

Choose the containing project directory and either its root `.SYSTEMX` or a
registered `Projects/NAME/.SYSTEMXP` child. Check for existing files, hidden
case variants, local changes, and active writers before setup. Use Python 3.9+
for commands. The examples below use the selected project's reviewed local
launcher from its containing directory:

```sh
bash .SYSTEMX/SYSTEMX.sh validate
bash .SYSTEMX/SYSTEMX.sh doctor
bash .SYSTEMX/SYSTEMX.sh agent-beta status
bash .SYSTEMX/SYSTEMX.sh agent-1 status
bash .SYSTEMX/SYSTEMX.sh agenda status
bash .SYSTEMX/SYSTEMX.sh service status
bash .SYSTEMX/SYSTEMX.sh session-settings
```

On Windows use the reviewed `SYSTEMX.ps1`/Python entry point described in the
[core setup guide](../docs/SETUP.md), with the same commands and an explicitly
selected root. A managed installation can route the same command through
`systemx run --target PROJECT --offline -- COMMAND`. For a child use
`systemx projects --target PROJECT -- COMMAND --project NAME` where the
selected command supports that scope. Do not treat the current working
directory or a prior chat as child selection. Command availability depends on
the selected release, not merely the source checkout being viewed.

`doctor` reports local prerequisites; it does not authenticate GitHub,
exercise a secret, or prove service health. `service status` reports the
availability of an explicit stdio session, not an installed daemon.

## 2. Answer the Agent1 first-run questions

Before saving anything, identify the accountable owner, exact repository,
root/child scope, actual owner/operator/guest access, whether Actions secrets
are allowed, selected local secret-store **type**, tracked `.env` history,
and rotation decision. Unknown answers should remain visible as missing.
The `actorRole` answer describes the operator for the review; it does not
grant or withhold GitHub authority. A guest can be a repository administrator
only if GitHub confirms that permission for the exact target at action time.
Do not enter values in the questionnaire or put them in command arguments.
Preview with actual nonsecret facts, then repeat with `--apply` only after
reviewing the selected scope:

```sh
bash .SYSTEMX/SYSTEMX.sh agent-1 setup \
  --account-context personal --repo OWNER/REPO \
  --review-scope root --actor-role owner \
  --secret-target none --local-secret-store none \
  --env-history-reviewed no --rotation-decision needed
bash .SYSTEMX/SYSTEMX.sh agent-1 setup \
  --account-context personal --repo OWNER/REPO \
  --review-scope root --actor-role owner \
  --secret-target none --local-secret-store none \
  --env-history-reviewed no --rotation-decision needed --apply
bash .SYSTEMX/SYSTEMX.sh agent-1 status
bash .SYSTEMX/SYSTEMX.sh agent-1 check --profile all-in-one
```

The sample answers show syntax, not a recommended owner policy.
`setup --apply` requires all eight answers, registers `agent.1` with the
`security-access` role when that ID is unused, creates its scoped memory, and
writes ignored `local/AGENT1-CONFIG.json`. A different existing `agent.1`
role is a conflict and setup refuses it. It does not install a service,
change GitHub, or fix a finding. Choose `--secret-target repository` or
`--secret-target environment` before applying if a later GitHub Actions secret
write is intended. To change a saved choice, preview `setup` again with all
eight answers, review `proposed` and `existingSHA256`, then apply with
`--replace-existing --expect-sha256 HASH` and the same answers. Reconfiguration
changes only the local intent record; a changed hash refuses replacement. `check` is a
bounded, warning-only local scan:
filename and Git-tracking signals, adjacent JavaScript lockfile presence,
and safe host signals. It reports 20 categories/400 available questions but
answers **zero** of them automatically. It does not perform a CVE, cloud,
device, malware, keylogger, or full posture audit. Use `unknown` for evidence
that has not been checked.

To review the fixed evidence catalog in manageable pieces, use
`agent-1 questions --category C01` or select a supported profile (`app`,
`webapp`, `code`, `cloud`, or `device`). The optional
`agent-1 review --answers RELATIVE_FILE --profile PROFILE` requires one answer for every
question in that profile. Each answer has an ID, `pass`/`fail`/`unknown`/`na`
result, and short relative evidence references. Pass, fail, and N/A require
references. The command checks coverage and format only; it does not open or
authenticate the evidence or change policy. Keep the answer file in an
approved private project location, without values or raw client data. The ten
event buckets in the catalog are classification guidance, not a new task or
incident ledger.

## 3. Handle `.env` files and GitHub Actions secrets separately

Do this only if the owner has authorized a particular repository and secret.
First inspect key names without values. The selected `.env` must be a regular,
nonlinked file within the project and no larger than one MiB:

```sh
bash .SYSTEMX/SYSTEMX.sh agent-1 env-inventory --env-file .env
bash .SYSTEMX/SYSTEMX.sh agent-1 env-sanitize --env-file .env
bash .SYSTEMX/SYSTEMX.sh agent-1 env-migrate \
  --env-file .env --repo OWNER/REPO
```

The second command previews a names-only `.env.example` with empty values.
After checking names and destination, `env-sanitize --env-file .env --apply`
creates it without changing `.env`. A different existing `.env.example` is
preserved unless an explicit guarded replacement uses `--replace-existing`
and the observed `--expect-sha256`. A sanitized example is still a file to
review before committing or sharing. The third command is a preview.
It defaults to `--credential-class new`: the owner should enter a newly issued
value, then separately verify the consumer and retire the prior value.
`--credential-class existing-test` requires `--ack-test-only` and is only for
an explicitly bounded test credential. These flags label intent; they do not
prove the value was rotated or safe. Review duplicate names, unsupported lines,
Git tracking, exact account, intended CI target, and whether the secret belongs
in a repository or a named environment. When it is truly needed, one explicit
interactive operation uses hidden terminal input and standard input to `gh`:

```sh
bash .SYSTEMX/SYSTEMX.sh agent-1 env-migrate \
  --env-file .env --repo OWNER/REPO --name EXAMPLE_KEY --apply
```

For a named environment add `--environment ENVIRONMENT_NAME`. This command
does **not** read the value from `.env`, upload the source file, store a local
secret, delete the source, rotate a previously exposed value, or verify the
workflow consumer. It requires an interactive terminal and checks the active
GitHub CLI account and `permissions.admin == true` for the exact repository
before prompting for one value. Unknown or false permission refuses the set;
the owner/operator/guest label cannot override it. Stop if the shown account
or target differs from the owner-approved one. `GH_TOKEN` may override saved
`gh` authentication. After a successful `gh secret set`, the command reads
the selected repository or environment secret **name/scope metadata** with
`gh secret list --json name`. `metadataReadback.state` is `verified` when the
name appears, otherwise `unknown`; no secret value is read back or verified.
The file-backed Agent1 commands use no-follow directory handles and enforce
the one MiB input limit after opening on macOS and Linux. On Windows, dotenv
inventory, sanitization, migration, answer-file review, and setup
reconfiguration fail closed in this beta until native reparse-point-safe file
handles are implemented. First-run setup, status, questions, and warning-only
filename checks remain available. Perform hash-guarded replacement while other
writers to that directory are quiescent.
Use a bounded consumer check for actual workflow use. The beta CLI supports
repository and named-environment Actions secret targets only; organization
secret writes need a separate reviewed provider workflow. The
[GitHub CLI manual](https://cli.github.com/manual/gh_secret_set) defines the
provider operation. If any historical value was tracked or shared, rotate at
the source first; see [GitHub's removal guidance](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).

GitHub Actions secrets are remote CI configuration, not a local credential
store. The setup choice `--local-secret-store` records intended type only;
it does not import values into Keychain, Credential Manager, or Secret Service.
An ignored `.env` remains plaintext. Keep portable records, chat, screenshots,
and logs free of values.

## 4. Activate Agent Beta only when useful

Beta is an optional local index for BOT/DOT workspaces. Its current commands
remain **offline**, including an `online-reference`: no online assistant or
provider is launched. Preview and
apply blank registration, then preview and apply a named workspace:

```sh
bash .SYSTEMX/SYSTEMX.sh agent-beta setup
bash .SYSTEMX/SYSTEMX.sh agent-beta setup --apply
bash .SYSTEMX/SYSTEMX.sh agent-beta bot-add BOT_NAME --kind bot
bash .SYSTEMX/SYSTEMX.sh agent-beta bot-add BOT_NAME --kind bot --apply
bash .SYSTEMX/SYSTEMX.sh agent-beta status
bash .SYSTEMX/SYSTEMX.sh agent-beta validate
```

`BOT_NAME` must begin with an uppercase ASCII letter and contain only uppercase
letters, digits, or underscores, up to 32 characters. `--kind dot` chooses a DOT
record. The created `AGENTB/.SYSTEMXB-BOT_NAME` is ignored local workspace
metadata with `BOT.json`, `MEMORY.md`, `README.md`, and `Rules.MD`, not an
authenticated bot. To retain an online reference without connecting it, use
`--source online-reference --provider SERVICE --provider-identity ALIAS` on
`bot-add`. Both fields must be nonsecret aliases. The metadata still reports
`online: false`. To link access intent, first create the BOT/DOT record with
no decision, then use `agenda decision-add` for actor `agentb:BOT_NAME` and
a `reviewed-intent` row. Preview
`agent-beta access-link BOT_NAME --access-decision-id ACC-001`; it returns a
`revisionBefore` fingerprint of both the BOT record and Access Matrix. Repeat
with `--expected-revision REVISION --apply` after review. A changed BOT or
matrix refuses the write, and the result still reports `online: false`,
`identityVerified: false`, and `accessGranted: false`. `assign BOT_NAME --task TASK-001` records
only a reference to an existing canonical task and also previews by default.
Agent 0 still owns task state and acceptance. Do not put credentials or client
payloads in its `MEMORY.md`.

## 5. Initialize Agent Alpha Agenda

Agent Alpha must be activated in the same selected scope before an Agenda
write. First preview/apply `autobot init`, then preview/apply `agenda init`:

```sh
bash .SYSTEMX/SYSTEMX.sh autobot init
bash .SYSTEMX/SYSTEMX.sh autobot init --apply
bash .SYSTEMX/SYSTEMX.sh agenda init
bash .SYSTEMX/SYSTEMX.sh agenda init --apply
bash .SYSTEMX/SYSTEMX.sh agenda status
bash .SYSTEMX/SYSTEMX.sh agenda table --format json
bash .SYSTEMX/SYSTEMX.sh agenda workbook-export
```

The two canonical tables are `AUTOBOT/AGENDA.json` and
`GLOBAL/ACCESS-MATRIX.json`. Agenda options and access decisions begin as empty
arrays; the matrix also contains 20 default-deny role and instance rows. Every
row requires review and grants nothing. `agenda table --format csv` returns
three Excel-readable CSV fields inside JSON. The checked-in XLSX is the stock
catalog, not a live selected-scope view. `agenda workbook-export` previews a
formula-free workbook under ignored `local/`; repeat with its `sourceRevision`
as `--expected-revision` and `--apply`, then use `agenda workbook-check` after
changes. The workbook is never the source of truth.

Use `agenda status` to obtain `accessRevision`, then `agenda decision-add
--help` to preview a reviewed-intent, denied, or gap decision for a registered
agent, fixed AUTOBOT, numeric worker, native subagent, or Agent Beta BOT/DOT
instance. Applying a decision requires the observed revision and does not
change OS or provider access. `agenda set` can later record one reviewed include/exclude
context choice for an existing AUTOBOT slot, pinned to a local rules-file SHA
and an observed Agenda revision. Read its help and the access row before use.
The access matrix documents reviewed intent, denial, or gaps; it grants no
permission. Agenda neither executes schedules nor sends notifications. Agent X
remains the event/due owner; its `due` read is on demand.

## 6. Use the read-only session when a client needs it

For a client that manages both standard streams, start the selected runner
with `service start --stdio`. Root and child command forms, JSON-lines
framing, fixed methods, and request limits are in [SERVICE.md](SERVICE.md).
The process exits on `stop`, EOF, or its bounded request limit. There is no
native OS install, port, daemon, automatic restart, or background polling.
Do not claim cross-platform installed-service support from this portable
Python code; verify any host integration on its target OS.

## 7. Read back and retain the removal plan

Run selected-scope `validate`, `agent-beta validate`, `agent-1 status`,
`agenda status`, and `service status`; inspect any reported warnings and
missing answers. Save only nonsecret references to the original provider or
host evidence. Keep the [uninstall guide](../Uninstall/README.md) with the
handoff. The current setup writes local records only except for an explicitly
applied `env-migrate` secret set. It does not start Agent Y, a scheduler, or an
online BOT/DOT process.
