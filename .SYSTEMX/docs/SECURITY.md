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

## Identity and authorization

When authentication is needed, use maintained mechanisms, least privilege, and
explicit session lifecycle rules. Apply authorization at the trusted boundary
for every protected action. UI visibility or a client-side role check is not
authorization. Protect administrative paths and choose stronger authentication
for sensitive roles as appropriate.

Test rejection as well as success: unauthenticated, wrong role, wrong tenant,
expired session, malformed input, replay, and excessive requests where relevant.
Document how access is granted, reviewed, revoked, and recovered.
When access decisions apply, use the blank
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
