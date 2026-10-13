# Dots / Codex Cloud

[Gallery](../README.md) · [4K JPEG](../Infographics/dots-codex-cloud-4k.jpg)

[![Dots / Codex Cloud: six steps connecting project context, work, review and a saved handoff.](../Infographics/dots-codex-cloud-4k.jpg)](../Infographics/dots-codex-cloud-4k.jpg)

**Artwork baseline:** the retained card depicts Agent 0/X/Z. See the current
[full-system map](cli-projects.md) for all four roles and the optional Agent Y
CLI lane. This text guide follows the current format.

## Workflow

1. **Brief.** Define the outcome, budget, tools and action permissions.
2. **Route.** Choose the dot's cloud computer or a configured Codex cloud environment.
3. **Snapshot.** Load the selected .SYSTEMX scope and record its source revision.
4. **Execute.** Run a bounded task or authorized worker wave. Keep run evidence.
5. **Review.** Agent Z reviews the result. Agent 0 / user resolves the remaining delta.
6. **Persist.** Save accepted changes to the canonical Git or Drive source and verify.

## Agent responsibilities

- **Agent 0:** scope, tasks, handoffs and acceptance within user authority.
- **Agent X:** events, timestamps and due items; the host executes schedules.
- **Agent Y (optional):** a bounded external CLI task on an authorized connected
  computer. It is separate from a cloud app worker.
- **Agent Z:** the fixed review policy with 10 categories and 100 questions.

These are roles implemented through the available toolchain. The public template
starts with Agent 0 only; [activate X/Y/Z](../../docs/AGENT-Y.md#activate-and-inspect) explicitly in
the selected scope. A review score is advisory and does not approve external actions.
The pictured card focuses on Agent 0/X/Z; [Agent Y](../../docs/AGENT-Y.md) adds
an optional separate CLI runtime when the chosen host actually supports it.

Treat the dot and its selected coding environment as distinct runtimes. Carry
the task ID, root or named child scope, source revision, actual run IDs, evidence,
and next checkpoint across handoffs. Persist accepted record changes to the
canonical Git/Drive source and verify them before ending or replacing a runtime.
A cloud task does not automatically see unsaved local files. Local execution
depends on the connected computer being available. Configure scheduling in the
host separately; Agent X records intended occurrences and observed outcomes.
Agent Y receives only the approved task packet and returns bounded job, exit,
commit/diff, and optional owned draft PR metadata for Agent 0 to reconcile.
The controller discards provider stdout/stderr; Agent 0 obtains original check
results separately. A dot or cloud session does not
install or authenticate the CLI, mount local files, or sync its `.SYSTEMX`
automatically. Count the CLI run in the same project worker and cost budget.

## Copyable prompt

```text
Use [canonical .SYSTEMX source]. Confirm the runtime and revision, run the authorized scope, then persist a reviewed handoff with evidence.
```

## Platform reference

A dot can work on its cloud computer and route coding work to a configured Codex cloud environment. Its cloud and connected-computer access are separate. See [Computers and apps](https://learn.chatgpt.com/docs/dots/computers-and-apps).

Platform references checked 2026-10-04. Availability and permissions depend on
the account, host and configuration. The workflow is a .SYSTEMX usage pattern,
not a built-in integration or third-party endorsement.
