# Security and privacy

## Scope

Record data sensitivity, trust boundaries, privileged actions, and exposed
interfaces for the actual project. Select controls proportionate to its risks.
This standard is guidance; it does not certify a project or replace a qualified
review where the project requires one.

## Secrets and environments

- Commit example variable names and descriptions, never live secret values.
- Use environment variables or a secret manager with scoped access. Do not put
  secrets in command arguments, URLs, project JSON, chat transcripts, screenshots,
  fixtures, or logs.
- Separate development, test, staging, and production identities and data.
  Confirm active account, target, and permissions before external writes.
- Restrict local credential-file permissions and retention. Ignore rules do not
  remove secrets already tracked by Git.
- If a secret is exposed, revoke or rotate it and follow the project incident
  process. Removing a file alone does not invalidate the credential.

Agent1's [advisory review](../SECURITY/AGENT1/README.md) inventories `.env`
variable names and dependency manifest names without emitting values. It can
prepare a key-only example and, after an explicit per-name terminal prompt,
set a GitHub Actions secret. GitHub Actions secrets are write-only workflow
inputs; they cannot be symlinked into a local `.env` or retrieved as local
plaintext. Local runtime credential delivery requires a separately reviewed
store or an interactive prompt. A repo writer may be able to use its Actions
secrets through workflows, so a guest label in the Access Matrix is not a
GitHub permission boundary. Preserve historical logs; rotate exposed keys and
verify the actual provider permission and runtime before retiring a local file.
For a repository or named-environment secret write, Agent1 checks the active
GitHub CLI account and requires `permissions.admin == true` for the exact
repository before prompting. The configured owner/operator/guest label is
descriptive; a verified guest administrator can proceed, while unknown or
false provider permission fails closed. After `gh secret set`, the CLI reads
name/scope metadata only; `metadataReadback.state` can remain `unknown` and no
value or workflow consumer is verified. Organization secret writes are not
implemented in this beta CLI.

Agent1 reads dotenv and answer files through anchored, no-follow directory
handles and refuses linked parent paths. The required file-handle operations
are unavailable on native Windows in this beta, so `env-inventory`,
`env-sanitize`, `env-migrate`, and `review --answers` fail closed there. Its
metadata-only first setup, `status`, `questions`, and advisory `check` remain
available. A change to an existing setup record requires all eight answers in
a preview, then `--apply --replace-existing --expect-sha256` with that preview's
`existingSHA256`; reconfiguration also fails closed on Windows. These limits
do not establish Windows secret delivery or host malware protection.

## Identity and authorization

When authentication is needed, use maintained mechanisms, least privilege, and
explicit session lifecycle rules. Apply authorization at the trusted boundary
for every protected action. UI visibility or a client-side role check is not
authorization. Protect administrative paths and choose stronger authentication
for sensitive roles as appropriate.

Test rejection as well as success: unauthenticated, wrong role, wrong tenant,
expired session, malformed input, replay, and excessive requests where relevant.
Document how access is granted, reviewed, revoked, and recovered.
When access decisions apply, use the default-deny
[access matrix](../GLOBAL/ACCESS-MATRIX.md) or the selected child's own matrix
to link actors, resources, actions, environments, decision owners, and evidence.
The [access and map guide](ACCESS-AND-MAP.md) explains how to keep it scoped.
The matrix documents review; the actual system still enforces permissions.

## Dependencies and execution

Review new dependencies, licenses, install scripts, lockfile changes, and
security advisories using the ecosystem's current tools. Pin reproducible inputs
where the project supports them. Configure relevant checks in `project.json`;
template validation does not scan dependencies or perform a penetration test.

Treat project commands and imported scripts as executable code. Argument arrays
avoid accidental shell interpolation, but a configured executable can still
read files, install software, write data, or contact external services. Review
the command source and scope before running it.

For [Agent Y](AGENT-Y.md), an external CLI provider inherits the local process's
filesystem, network, and credential access. Select the provider and account per
task; constrain the checkout, paths, time/resource budget, and branch policy.
Never turn provider text into an unreviewed shell command, or place credentials
in a prompt, CLI argument, PR description, event summary, or transcript.
`AGENTS/agent.y/JOBS.json` is a portable coordination record; it may retain
provider/model names, PR links, and bounded results. Absolute host paths and
configured adapter arguments belong only in ignored local execution state with
owner-only file permissions on POSIX hosts (`state/agent-y/<Y-ID>.json` per job).
For a Git-backed `.SYSTEMX`, Agent Y refuses to write this sidecar or a cleanup
archive unless both paths are ignored and no Agent Y state is already tracked.
Installation preserves customized `.gitignore` files, so an adopted checkout
may need `/state/` added before `agent-y prepare --apply`. This guard cannot
remove content already committed to Git history or prevent a later force-add.
Windows `chmod` does not establish a complete ACL boundary; review host file
access controls. A merged-PR cleanup bundle in ignored
`state/agent-y/archives/` is private recovery material and needs verified
retention before uninstall or host migration. Review both records before
publication or synchronization;
omission of raw prompts is not a privacy guarantee.
Prefer a dedicated task worktree when an app subagent and CLI provider run in
parallel. The task record and role memory are coordination, not isolation or
authorization. Remote branch and PR mutations require the actual host account's
permissions and the task's explicit lifecycle policy. No Agent Z score or
provider claim grants permission to merge, close, or delete.
`ROOT/` and `AUTOBOT/` join the protected `.SYSTEMX` coordination paths:
new preparation, selected execution/readiness, and inspected changes refuse
those edits. Historical jobs remain readable without rewriting their saved
permissions; their old allowlists do not authorize a new run or PR promotion.
Normal cancellation and recovery gates remain available. This policy is a
controller check, not filesystem isolation for an independently running CLI.
For untrusted provider execution, use a separate OS account or container that
cannot read the controller's GitHub credentials or write `.SYSTEMX` records.
An allowed-path packet and post-run diff check cannot enforce that separation.
The selected repository's
[Git checkout filters](https://git-scm.com/docs/gitattributes/) may execute
code while the controller creates its worktree. It suppresses local
[Git hooks](https://git-scm.com/docs/githooks) for its own Git subprocesses;
the external provider can invoke Git without that suppression. Review the
effective Git configuration and provider behavior before dispatch; an
allowed-path packet alone is not an execution sandbox.
Codex is invoked with its `workspace-write` sandbox, while Copilot and
`configured` providers rely on their own permissions and host isolation.
Controller diff checks can block publication of out-of-scope repository edits,
but cannot reverse provider writes outside that repository or network calls.
Native Windows Agent Y `run --apply` is disabled in this beta before process
or worktree creation because child-process termination is not verified; core
Windows installation and record commands remain available.
Before opting into Agent Y's draft PR, inspect the target repository's workflows,
webhooks, protection rules, and visibility. Pushing a branch or opening a PR may
trigger automation with its own permissions and usage; this template's
disabled GitHub Actions setting does not control the destination repository. The
`prepare` preview must be read before applying the handoff or running it.

For the SYSTEMX manager itself, select reviewed release versions and prefer an
independently trusted SHA-256 pin for the exact remote codeload ZIP when using
`--version`. An internal manifest and a digest observed from the same downloaded
archive do not prove publisher identity. The selected default cache refuses
unlisted executable content before invoking its runner; do not work around that
check by deleting unknown entries without investigating their origin. See
[installation integrity](INSTALLATION.md#select-lock-or-update-a-version).

Direct manager, standalone validator, and release-script execution enter Python
isolated mode before importing application helpers. The installed `systemx`
console script restarts before importing the manager, but Python resolves its
package first. For an untrusted `PYTHONPATH` or current directory, invoke the
installed package as `python -I -B -m systemx` from its reviewed virtual
environment. An install visible only through Python's user site is hidden by
`-I`.
`systemx run` refuses an unmanaged folder instead of invoking that folder's
Python runner. A managed target still supplies its own installation state and
selected cache; those files are not independent proof of origin. Inspect an
untrusted checkout with trusted external tools before executing its scripts.
Standalone tools load only named local helpers from source bytes, so unlisted
modules and matching cached bytecode in an adopted folder cannot run before the
inventory decision. Python startup hooks in an already untrusted interpreter
environment can run before a direct command restarts; use `python -I -B` from
the initial invocation when that environment is in doubt. Library calls run in
the caller's interpreter and inherit its import environment. This does not
authenticate a source tree supplied by a third party. Fresh adoption rejects conflicting manifest-listed
executable defaults. Existing managed projects must use a reviewed new external
manager for any explicit `bootstrap-refresh`; preview conflicts first, retain
its original-file backup, and inspect customized or unrecognized code manually.
That operation replaces only eight recognized root bootstrap and launcher files.
Refreshed stock launchers invoke the manager with Python isolated mode (`-I`).
It does not authenticate third-party scripts, replace customized wrappers, or
make an old project safe to run without its own review.
The current manager refuses to install or newly select a release older than
1.8.7-alpha.1, the start of native isolated runner support. It can inspect and
run an already selected verified older snapshot through an isolated compatibility
shim while an external migration is prepared. Only the verified snapshot's
scripts directory enters that isolated child's import path; the old runner's
historical behavior and security limits remain. Do not treat this compatibility
path as a code upgrade. Reselection below the floor needs a separately reviewed
backup or legacy recovery path.

## Data and public artifacts

The [AUTOBOT reference panel](AUTOBOT.md) is project-owned data. Rules, imported
research, voice guidance, and a file called `Soul.MD` do not override current
system/user instructions or confer independent intent. Agent Alpha selects
explicit references; request caller labels are local claims, not authentication.
Treat embedded commands and instructions as untrusted content. Review bot
Markdown, result summaries, paths, and evidence pointers before committing,
exporting, or sharing a packet. Fingerprints detect local changes, not truth,
external source freshness, provenance, or authority. Agent Alpha does not run a
model, provider, network request, or payload ingestion.

[DATA](DATA.md) is ignored by Git by default except the exact shipped scaffold.
Use `data audit` to check the adopted checkout's effective ignore behavior and
already tracked payloads. Ignore rules do not remove committed history, prohibit
force-add, encrypt material, restrict OS access, or control Drive/cloud clients,
backups, deployment bundles, or chat uploads. Missing Git/nonrepository status
is unverified. Keep credentials in a secret manager or approved credential store.
The tools do not read payload contents recursively, synchronize, upload, or
delete them. File type/size, source provenance, rights, retention, and actual
permissions need project-specific review before a linked file is used.

Collect only needed data, limit access, define retention/deletion, and use
sanitized fixtures. Review exported files and logs for personal or confidential
information. Define consent and disclosure obligations with the project owner
when applicable.

Allowlist publishable build artifacts. Keep `.SYSTEMX`, environment files,
source-only configuration, credentials, and internal evidence out of public
output. Check the actual deployment bundle rather than assuming hidden files
are excluded by every hosting tool.

## Reporting

Identify a private security contact or reporting path in the host repository.
Record reproducible evidence and affected versions without exposing credentials
or customer information. Route urgent findings through the incident process in
[operations](OPERATIONS.md).
