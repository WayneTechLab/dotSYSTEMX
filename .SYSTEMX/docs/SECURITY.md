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

## Dependencies and execution

Review new dependencies, licenses, install scripts, lockfile changes, and
security advisories using the ecosystem's current tools. Pin reproducible inputs
where the project supports them. Configure relevant checks in `project.json`;
template validation does not scan dependencies or perform a penetration test.

Treat project commands and imported scripts as executable code. Argument arrays
avoid accidental shell interpolation, but a configured executable can still
read files, install software, write data, or contact external services. Review
the command source and scope before running it.

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
