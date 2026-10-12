# Agent Y memory

Role: `cli-worker` (delegated CLI work). This memory belongs to the explicitly selected root
or `.SYSTEMXP` scope. It starts blank and records only verified facts needed to
resume an authorized assignment. Environment and user instructions remain
authoritative.

## Current delegation

- Selected project and canonical task ID:
- Agent Y job ID from `AGENTS/agent.y/JOBS.json`:
- Coordinator and shared-resource owner:
- Authorized provider/tool and account reference (names only):
- Repository identity, base revision, allowed files (local paths stay in ignored execution state):
- Branch name, PR target, and permitted lifecycle actions:
- Acceptance/check references, resource limit, and stop condition:

## Observed execution

- Process/session reference, start time, and last observed state:
- Host-local worktree state reference and cleanup owner (no absolute path here):
- Source revision, changed files, and relevant uncommitted work:
- Checks and original evidence references:
- Branch and PR URL/ID, observed head/base, and publication state:
- Agent X event IDs and Agent Z review IDs, if any:
- Failure or interruption and recovery/rollback reference:

## Handoff to Agent 0

- Verified result versus unverified claims:
- Remaining acceptance or integration:
- Exact next action and owner:
- PR/branch cleanup status and evidence location:

Task state lives only in the selected `WORK/TASKS.json`. Do not store tokens,
secret values, full provider transcripts, or another project's memory here.
Submitting a report does not mark a task done or authorize remote mutation.
