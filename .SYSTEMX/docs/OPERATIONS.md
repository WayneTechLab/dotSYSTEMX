# Operations

## Git and local work

Before synchronizing, identify the intended repository, branch, remote, upstream,
and tracked, staged, untracked, and ignored changes. Remote divergence and local
cleanliness are different checks. Fetch before comparing remote revisions when
the task calls for synchronization; choose a merge strategy consistent with
the repository's policy. Preserve unrelated local work.

Do not silently reset, clean, force-push, stage everything, install hooks, or
overwrite configuration. Prefer explicit, reviewable changes. The SYSTEMX
runner performs no Git mutations and cannot guarantee a clean release revision;
the project release process must establish that evidence.

## Local development

Use the configured `dev` command when available. Before starting or stopping a
service, verify its process, working directory, and port ownership. Reuse only
the intended project's service; do not kill unrelated listeners. Record active
endpoints without credentials and verify both server response and UI behavior
when the task needs them. A process starting does not prove the product works.

## Release preparation

Use a [release record](../templates/RELEASE.md) for the applicable checks:

1. Identify the approved scope, exact revision/artifact, target environment,
   owner, and existing release authorization.
2. Confirm dependency and runtime reproducibility, project checks, and build.
3. Review configuration, access controls, migrations, secret references, and
   the actual public artifact contents.
4. Confirm rollback or recovery steps, backup/restore evidence when needed, and
   compatibility with the previous version.
5. Review `bash .SYSTEMX/SYSTEMX.sh deploy --dry-run` before execution.

The `deploy` command runs configured checks, the build, and the deployment
script. It stops on failure. It does not commit, push, tag, choose a provider,
log in, auto-select an account, or verify a live release. The configured deploy
script owns explicit target selection and any project-specific release gates.
Review that script before treating the plan as authorized for production.

After deployment, inspect the live release identifier and run target-specific
smoke checks. Verify the requested behavior rather than relying solely on a CLI
exit code. Record unresolved issues and the next responsible owner. Keep local
proof, Git publication, provider release, and production acceptance distinct.

## Monitoring and cost

For operated services, choose indicators linked to user outcomes: errors,
latency, availability, saturation, queue age, data freshness, or other relevant
signals. Assign alert owners, escalation routes, and actionable thresholds.
Review costs, quotas, retention, and unexpected usage. Redact sensitive values
and limit access to logs. A static document project can mark this inapplicable.

## Incidents and recovery

1. Establish impact, affected environments, incident owner, and a timeline.
2. Preserve relevant evidence and contain the issue with the least disruptive
   authorized action.
3. Roll back, disable the affected feature, or apply a reviewed fix according to
   the project runbook. Protect data integrity before retrying writes.
4. Verify recovery in the affected environment. Reconcile partial operations
   before retrying non-idempotent actions.
5. Record causes, follow-up actions, owners, and any recovery gaps.

For local tooling and automation blockers, use the
[recovery playbook](../AI/RECOVERY-PLAYBOOK.md). Keep environment-specific contact
details and run commands in the downstream project's runbook.
