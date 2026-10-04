# .SYSTEMX full-system map — text equivalent

This companion explains the public infographic without relying on its colors,
icons, or raster text. The standard roles are **Agent 0, Agent X, and Agent Z**.
Numeric subagents are registered for specific assignments. Role records do not
start processes; the authorized IDE, CLI, chat, or bot harness supplies execution.

## 1. Shared context

The exact canonical folder name is `.SYSTEMX`. Start with applicable instructions,
`START-HERE.md`, `AGENTS.md`, and `STANDARD.md`, then read current focus and relevant
project records. `GLOBAL/CONTEXT.md` retains intent and constraints;
`PLAN/MASTER-PLAN.md` defines outcomes, milestones, and acceptance;
`MEMORY/PROJECT.md` holds reviewed durable facts. `MEMORY/sessions/` retains saved
checkpoints. In a managed installation, selected defaults and project-owned
records can live in different locations; inspect `INSTALLATION.json` and the
bounded context packet before proceeding.

## 2. Agent 0 and subagents

Agent 0 (`agent.0`) decomposes work, routes assignments, integrates results, and
accepts against the agreed criteria. `AGENTS/REGISTRY.json` records roles;
`AGENTS/<id>/MEMORY.md` holds scoped continuity. Authorized numeric workers such
as `agent.1` and `agent.2` receive a task, dependencies, base revision, permitted
write scope, acceptance criteria, and a report contract. They return original
evidence for integration. Up to ten workers can be requested, subject to lower
harness limits and useful independence. Keep one canonical writer per record scope.

## 3. Canonical work and generated views

`WORK/TASKS.json` owns task state. `WORK/FOCUS.json` points to the current objective
and selected tasks. The ordinary path is `todo → in_progress → needs_review → done`;
blocked or cancelled work remains explicit. Task updates regenerate `TODO.md`,
`WORKING-ON.md`, `BLOCKED.md`, `REVIEW.md`, `DONE.md`, and `CANCELLED.md` in `WORK/`,
plus the root `CURRENT.md` summary. Generated pages are views, not separately
maintained ledgers. A worker report alone does not establish completion.

## 4. Agent X: time and events

After scoped role activation, Agent X (`agent.x`) records meaningful human, bot,
agent, and automation events in `EVENTS/EVENTS.json`. Records identify actors,
occurrence and recording times, revisions, original evidence, and retry keys.
`EVENTS/SCHEDULE.json` tracks due occurrences. Agent X does not execute a scheduler;
the external host owns any authorized scheduled run. Retain failed attempts and
reuse matching retry keys without manufacturing new activity.

## 5. Agent Z: fixed review

After scoped role activation, Agent Z (`agent.z`) uses `REVIEWS/POLICY.json`:
ten categories with ten questions each. Frozen policies, requests, and scorecards
live in `REVIEWS/policies/`, `REVIEWS/requests/`, and `REVIEWS/reports/`.
Reviews preserve unknowns, evidence, applicability, and comparable deltas.
The same questions are assessed at meaningful boundaries or on request; unchanged
inputs reuse existing reports. Scores are advisory. Agent 0/user decides whether
the original acceptance is met or a concrete gap needs another bounded task.

## 6. Toolchain and actual execution

The host supplies model sessions, authorized processes, tools, and permissions.
`.SYSTEMX` exposes shell/PowerShell entry points (`SYSTEMX.sh`, `SYSTEMX.ps1`,
and the compatible `WSG-MENU.sh`), a Python library, and the external `systemx` CLI.
`manager.py` and `lifecycle.py` handle installation/lifecycle operations;
`scripts/` supplies task records, project routing, role activation, Agent X/Z,
validation, and distribution checks. `project.json` names explicit application
command arrays for checks, builds, and authorized deployments. Record actual run
IDs and artifacts; verify the live target when that delivery scope is authorized.
The folder does not supply a model, application framework, cloud service, or bot runtime.

## 7. SYSTEMX PROJECTS

`Projects/REGISTRY.json` selects named children at
`.SYSTEMX/Projects/NAME/.SYSTEMXP`. Each child has scoped `GLOBAL/`, `PLAN/`,
`WORK/`, `MEMORY/`, `AGENTS/`, `SOURCES.json`, `DECISIONS/`, and `SYNC/` records,
with optional `EVENTS/` and `REVIEWS/` after activation. Examples such as
`WebApp/.SYSTEMXP` and `Research/.SYSTEMXP` are separate record scopes using one
outer tool installation and selected version. Do not nest another `.SYSTEMX` or
combine sibling task ledgers. Source references do not establish a live connection.

## 8. Defaults, setup, and recovery

Reusable support locations are `config/`, `profiles/`, `templates/`, `AI/`,
`docs/`, and `tests/`; `VERSION`, `SOURCE.json`, and `LICENSE` identify the
distribution. Managed installs add `INSTALLATION.json` and the internal
`.SYSTEMX/.systemx/` cache for retained releases and operation logs. This internal
cache differs from the optional sibling alias `.systemx → .SYSTEMX`.
Install, pin a reviewed version, preview updates, and audit the footprint.
Additive updates preserve existing project files. Uninstall/restore uses backups
and receipts. Manual updates are the default; startup checks are opt-in.

## Complete workflow and shared storage

Research becomes phases and milestones, dependency-linked tasks, and bounded
execution waves. Work is integrated, verified, reviewed, and accepted; checkpoint
the next incomplete step or finish when the agreed outcome is met. No automatic
review/rebuild loop is implied. Git, local folders, Drive, cloud storage, and VMs
can carry records through authorized access and verified snapshots. A URL alone
does not grant access or synchronize concurrent writes.

See the [Visual Guide](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Visual-Guide),
[command reference](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Command-Reference),
and [shared-workspace guide](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Shared-Workspaces-Cloud-and-Bots)
for executable instructions and operational limits. This remains an alpha template.
