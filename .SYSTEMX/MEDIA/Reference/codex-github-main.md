# Codex + GitHub / main project

[Gallery](../README.md) · [4K JPEG](../Infographics/codex-github-main-4k.jpg)

[![Codex + GitHub / main project: six steps connecting project context, work, review and a saved handoff.](../Infographics/codex-github-main-4k.jpg)](../Infographics/codex-github-main-4k.jpg)

**Artwork baseline:** the retained card depicts Agent 0/X/Z. See the current
[full-system map](cli-projects.md) for all four roles and the optional Agent Y
CLI lane. This text guide follows the current format.

## Workflow

1. **Inspect.** Confirm the project path, branch, local changes and remote revision.
2. **Plan.** Load .SYSTEMX context. Define the task, owner and acceptance evidence.
3. **Isolate.** Use a branch or worktree for independent work when appropriate.
4. **Build.** Edit code and run the project toolchain. Record actual results.
5. **Review.** Agent Z checks the scoped result. Agent 0 / user accepts it.
6. **Integrate.** Commit code and record updates. Merge when authorized; verify main.

## Agent responsibilities

- **Agent 0:** scope, tasks, handoffs and acceptance within user authority.
- **Agent X:** events, timestamps and due items; the host executes schedules.
- **Agent Y (optional):** executes one selected task through an installed CLI in
  an isolated branch/worktree and returns evidence for integration.
- **Agent Z:** the fixed review policy with 10 categories and 100 questions.

These are roles implemented through the available toolchain. The public template
starts with Agent 0 only; [activate X/Y/Z](../../docs/AGENT-Y.md#activate-and-inspect) explicitly in
the selected scope. A review score is advisory and does not approve external actions.
The pictured card focuses on Agent 0/X/Z; [Agent Y](../../docs/AGENT-Y.md) adds
an optional external CLI branch/PR lane under Agent 0's task assignment.

Keep `.SYSTEMX/` beside the host project code and tests. `main` is a Git branch,
not a required directory name. Preserve existing local changes. Coordinate
independent workers with bounded scopes and a common source revision; workers
return changes and evidence to the coordinator. Commit accepted code and record
updates together when appropriate, then check the actual remote revision after
an authorized push or merge. Deployment and runtime verification need their own
evidence when they are part of the task.
Agent Y can open an owned draft PR only when the task explicitly opts in and the
CLI run succeeds. Marking that draft ready follows accepted `done`; closing an
unmerged owned PR follows recorded cancellation and a selected policy. Neither
transition authorizes a merge, and a PR URL does not prove live behavior.
Preparation pins the chosen CLI file and base commit. The controller verifies
exit, changed paths, and commit state; Agent 0 separately runs or verifies project
checks and original evidence. `pr-ready` refuses a changed remote base. After a
separately authorized merge and accepted task, cleanup verifies the owned head
and a recovery bundle before removal; ignored files can block that removal.

## Copyable prompt

```text
Use this project's .SYSTEMX. Inspect Git state, complete the agreed task, retain evidence, review the result, and integrate within my authorization.
```

## Platform reference

Codex worktrees provide separate Git checkouts for independent work. See [Git worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees).

Platform references checked 2026-10-04. Availability and permissions depend on
the account, host and configuration. The workflow is a .SYSTEMX usage pattern,
not a built-in integration or third-party endorsement.
