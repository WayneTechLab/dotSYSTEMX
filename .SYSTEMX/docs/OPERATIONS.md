# Operations

## Git and local work

Before synchronizing, identify the intended repository, branch, remote, upstream,
and tracked, staged, untracked, and ignored changes. Remote divergence and local
cleanliness are different checks. Fetch before comparing remote revisions when
the task calls for synchronization; choose a merge strategy consistent with
the repository's policy. Preserve unrelated local work.

Do not silently reset, clean, force-push, stage everything, install hooks, or
overwrite configuration. Prefer explicit, reviewable changes. The ordinary
`check`, `build`, and `deploy` runner does not create Git commits or PRs and
cannot guarantee a clean release revision; the project release process must
establish that evidence. An explicitly applied Agent Y job has a separate
scoped Git/PR lifecycle.

For a delegated CLI task, [Agent Y](AGENT-Y.md) records the intended repository,
base, task branch, PR target, and lifecycle policy before a process starts.
Draft PR auto-opening after successful scoped work is per-task opt-in. Pushing a
branch or opening a draft PR can trigger the target repository's configured
Actions, webhooks, checks, and associated usage. Inspect those settings and
review the Agent Y preview before opting in; disabling Actions on the
dotSYSTEMX source repository does not disable them in an adopted project's
repository. Marking a draft ready for review is separate from closing an
abandoned PR, merging, or
deleting the owned branch. Close requires recorded cancellation and leaves that
unmerged branch intact. Automated cleanup requires verified merge and accepted
completion; it preserves a local bundle before an exact-head branch deletion.
Merging needs separate authorization and repository checks.
Inspect the observed remote head and PR state before
retrying a partially completed operation. A local success is not proof of
publication, and an open PR is not proof of deployment or live verification.

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
