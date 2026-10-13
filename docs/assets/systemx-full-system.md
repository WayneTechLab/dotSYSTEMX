# .SYSTEMX full-system map — text equivalent

This is the current four-role architecture shown in the public infographic:
**Agent 0, Agent X, Agent Y, and Agent Z**. The artwork is explanatory;
the selected release's executable commands and record contracts remain the
authority. The older three-role poster remains in tagged Git history.

## 1. Shared context and authority

Use the exact folder name `.SYSTEMX`. Read applicable instructions,
`START-HERE.md`, `AGENTS.md`, and `STANDARD.md`, then the selected scope's
current focus and relevant changes. `GLOBAL/CONTEXT.md` retains intent and
constraints; `GLOBAL/ACCESS-MATRIX.md` records reviewed access decisions;
`PLAN/MASTER-PLAN.md` defines outcomes, milestones, and acceptance;
`PLAN/MAP.md` identifies sources, tooling, and environment boundaries.
`MEMORY/PROJECT.md` holds reviewed facts and `MEMORY/sessions/` retains
checkpoints. These files record intent and evidence; they do not grant IAM or
host permissions. Managed defaults and project records may occupy different
locations; inspect `INSTALLATION.json` and the bounded context packet.

## 2. Agent 0 and app/IDE subagents

Agent 0 (`agent.0`) plans, assigns, integrates, and accepts against the agreed
criteria. `AGENTS/REGISTRY.json` records roles and
`AGENTS/<id>/MEMORY.md` holds scoped continuity. App/IDE workers such as
`agent.1`, `agent.2`, and `agent.N` receive a task ID, dependencies,
base revision, permitted write area, checks, and report contract. They return
original evidence to Agent 0. Up to ten workers may be requested, subject to the
harness's actual capacity and useful independence. Assign one canonical writer
per shared record scope. Role activation creates records, not processes.

## 3. Canonical work and generated views

`WORK/TASKS.json` owns task state. `WORK/FOCUS.json` selects the current
objective and tasks. The ordinary path is
`todo → in_progress → needs_review → done`; blocked and cancelled work remains
explicit. Task commands regenerate `WORK/TODO.md`, `WORK/WORKING-ON.md`,
`WORK/BLOCKED.md`, `WORK/REVIEW.md`, `WORK/DONE.md`, and
`WORK/CANCELLED.md`, plus `CURRENT.md`. Generated pages are views of the
ledger. A worker exit, PR URL, or scorecard alone does not establish completion.

## 4. Agent X: events and time

After scoped activation, Agent X (`agent.x`) records meaningful human, bot,
agent, and automation events in `EVENTS/EVENTS.json`. Records identify the
actor, occurrence time, recorded time, revision, original evidence, and retry
key. `EVENTS/SCHEDULE.json` tracks due items. Planned future times are valid;
observed events and closures must pass the release's chronology rules.
Agent X records the host's observed actions; it does not execute schedules.
Keep original failed attempts and reuse matching retry keys appropriately.

## 5. Agent Y: a separate external CLI and PR lane

Agent Y (`agent.y`) carries one explicitly assigned, in-progress task from
Agent 0 to a **per-task selected** installed Codex, Copilot, or configured CLI.
It is separate from the app/IDE subagent pool and does not inherit that chat's
memory. `AGENTS/agent.y/JOBS.json` holds portable job metadata.
Ignored `state/agent-y/` sidecars retain host-local execution identity and
paths. Preparation pins the selected executable's canonical path, SHA-256, and
file identity; launch rechecks that binding. It does not pin interpreters or
dependencies.

The task packet names the task, project, repository/base revision, permitted
paths, provider, checks, and branch/PR policy. Execution uses a task-owned Git
branch and worktree. A successful provider exit and controller scope/commit
checks can open a **draft PR only if that handoff opted in**. Agent 0 separately
checks the actual result and original project evidence; Agent X records events
and Agent Z can review the matching evidence snapshot.

The subsequent transitions are distinct:

- Accepted `done` permits a separately invoked PR **ready** step, subject to
  fresh remote identity/base checks.
- Recorded `cancelled` with a reason permits closing the owned unmerged PR;
  its branch and worktree remain for reviewed disposition.
- A verified merged PR plus accepted task permits a separately invoked
  **cleanup**, after retaining a verified bundle and checking the fresh remote
  head. Ignored and untracked local data blocks worktree removal.
- Merging requires the user's separate authority and repository checks.
  Agent Y supplies **no merge command**.

A failed or partial remote operation needs inspection and reconciliation before
retry. Neither a role name nor a score grants GitHub authority. Worktree/path
checks do not isolate an external provider from its host account's credentials
or out-of-repository writes. Use a separate OS identity or container when that
is required by the project's threat model. Native Windows Agent Y execution
currently fails closed. See the [Agent Y manual](../../.SYSTEMX/docs/AGENT-Y.md).

## 6. Agent Z: fixed review

After scoped activation, Agent Z (`agent.z`) uses `REVIEWS/POLICY.json`:
ten categories of ten questions, totaling 100 checks. Frozen policies, requests,
and scorecards live in `REVIEWS/policies/`, `REVIEWS/requests/`, and
`REVIEWS/reports/`. Review preserves evidence, unknowns, applicability, policy
and revision identity, and comparable deltas. Reuse unchanged inputs at
meaningful boundaries; do not repeatedly rebuild or review without a concrete
change. Scores advise. Agent 0/user decides acceptance or the next bounded gap.

## 7. CLI, tools, and real execution

The app, IDE, CLI, chat, or bot harness supplies models, actual processes, tools,
and permissions. `SYSTEMX.sh`, `SYSTEMX.ps1`, compatible `WSG-MENU.sh`,
the Python library, and external `systemx` CLI expose the format's commands.
`manager.py` and `lifecycle.py` manage setup and receipts; `scripts/`
handles records, project routing, roles, validation, and distribution checks.
`project.json` names explicit application command arrays. Retain actual run
IDs, source revisions, artifacts, and applicable live verification.
The folder itself supplies no model, application framework, cloud service,
scheduler, or bot runtime.

The external CLI manages the **outer directory containing `.SYSTEMX`**:
`first-run`, `install`, `status`, `policy`, `update`, `audit`, `uninstall`,
`restore`, and `export-chat`. Its `status` is installation status; task status
comes from the selected record scope. The direct project-routing command is:

```bash
systemx projects --target "/path/to/outer-workspace" -- list
systemx projects --target "/path/to/outer-workspace" -- context --project Project-A --agent agent.0
```

`systemx projects` defaults to offline operation. Optional `--online` permits
only the installation's configured startup notice check; it does not select or
download defaults. The compatible longer form remains
`systemx run --target OUTER --offline -- projects ...`. Explicit scope is required
for child record operations. The outer launchers support `tools-guide`,
`doctor`, `validate`, task/agent commands, and configured project actions.
The Python API exposes `run()`, `projects()`, and `export_chat()`.
Git and `gh` supply authorized repository/PR actions; Codex, Copilot, or a
configured CLI supplies Agent Y execution when installed and authorized.
See the versioned [CLI and tools guide](../../.SYSTEMX/docs/CLI-TOOLS.md).

## 8. SYSTEMX PROJECTS

```text
.SYSTEMX/
  scripts/                         Shared operational tools
  .systemx/                        Managed defaults and logs after install
  Projects/
    Project-A/.SYSTEMXP/           Separate selected records
    Project-B/.SYSTEMXP/           Independent sibling records
```

`Projects/REGISTRY.json` selects named children at
`.SYSTEMX/Projects/NAME/.SYSTEMXP`. Each child has `GLOBAL/`, `PLAN/`,
`WORK/`, `MEMORY/`, `AGENTS/`, `SOURCES.json`, `DECISIONS/`, and
`SYNC/`. Activation adds optional events, Agent Y jobs, and reviews to the
selected scope. One outer installation supplies shared tools and selected
defaults. Do not nest another `.SYSTEMX`, combine sibling ledgers, or infer
scope from a previous chat. Explicit project selection is required.

Use `projects context --project Project-A` or
`projects roles-init --project Project-A` through the chosen outer entry point.
Role activation previews by default and creates optional records only with
`--apply`. Each child's `project.json` configures its own application commands;
those commands run from `Projects/Project-A/`, not from `.SYSTEMXP` or the outer
repository. Source URLs are references and do not change that working directory.
The shared outer installation does not merge sibling memory or task ledgers.

## 9. Defaults, setup, updates, and recovery

Support locations are `config/`, `profiles/`, `templates/`, `AI/`,
`docs/`, and `tests/`; `VERSION`, `SOURCE.json`, and `LICENSE`
identify the distribution. Managed installs add `INSTALLATION.json` and
the internal `.SYSTEMX/.systemx/` cache for retained releases and operation
logs. That cache differs from the optional sibling alias
`.systemx → .SYSTEMX`.

Preview installation, pin reviewed defaults, preview an update, and audit its
footprint. Additive updates preserve existing project files and earlier
snapshots; a new standard graphic is added without removing the user's older
media. Uninstall/restore uses backups and receipts. Updates are manual by
default; opt-in startup notices check metadata without selecting code.

## The complete loop

Research → phases and milestones → dependency-linked tasks and waves →
authorized work and integration → verification and fixed review → acceptance
and checkpoint. A concrete gap produces another bounded action; meeting the
agreed outcome permits finishing. App/IDE workers and Agent Y return evidence
to Agent 0; Agent X records observed activity and Agent Z reviews claims.
Canonical state preserves the next incomplete step across sessions.

Git, local folders, Drive, cloud storage, and VMs can carry records through
authorized access and verified snapshots. A URL alone does not connect a
service, synchronize concurrent writers, or prove deployment.

[4K download](../../.SYSTEMX/MEDIA/Infographics/systemx-cli-projects-4k.jpg) ·
[Visual Guide](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Visual-Guide) ·
[Shared-workspace guide](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Shared-Workspaces-Cloud-and-Bots)

**Alpha: use at your own risk.** The infographic and template checks do not
certify a downstream project for production.
