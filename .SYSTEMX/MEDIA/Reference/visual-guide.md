# Current .SYSTEMX visual field guide

This is the reading-order and text alternative for the beta.3 twelve-image
suite: four system maps, one detailed guide for each of seven agent roles, and
one combined atlas. Each image is linked below at full size. The SVGs use
selectable vector text and a 7680 × 4320 declared canvas. Their generated
illustrations have separate source dimensions recorded in [ASSETS.json](ASSETS.json);
the larger canvas does not create native 8K illustration detail.

These diagrams explain the portable template. A drawn arrow is a relationship,
not an automated process. A role or Access Matrix entry does not authenticate a
provider, install an IDE extension, grant OS rights, or accept a task. The user
or designated owner retains acceptance, and `WORK/TASKS.json` is the canonical
task-status ledger in the selected scope.

| System map | Full-size SVG | Main question |
| --- | --- | --- |
| 1. Architecture | [Open architecture map](../Infographics/systemx-map-architecture.svg) | Where are the canonical records and selected project scope? |
| 2. Task and evidence cycle | [Open task-cycle map](../Infographics/systemx-map-task-cycle.svg) | How does one task move through observation, work, review, and acceptance? |
| 3. Governance records | [Open governance map](../Infographics/systemx-map-governance.svg) | How do Agenda, Access Matrix, BOT/DOT, and Agent1 records relate? |
| 4. First run and toolchain | [Open onboarding map](../Infographics/systemx-map-onboarding.svg) | How does a host choose a scope and read records without claiming a native integration? |

| Agent | Full-size SVG | Primary role |
| --- | --- | --- |
| Agent 0 | [Open Agent 0 guide](../Infographics/systemx-agent-0.svg) | Coordinate and integrate one canonical project task |
| Agent X | [Open Agent X guide](../Infographics/systemx-agent-x.svg) | Record events, time, and due items |
| Agent Y | [Open Agent Y guide](../Infographics/systemx-agent-y.svg) | Carry one assigned task through a selected CLI |
| Agent Z | [Open Agent Z guide](../Infographics/systemx-agent-z.svg) | Review evidence against a fixed policy |
| Agent Alpha | [Open Agent Alpha guide](../Infographics/systemx-agent-alpha.svg) | Select bounded AUTOBOT references and Agenda context |
| Agent Beta | [Open Agent Beta guide](../Infographics/systemx-agent-beta.svg) | Record named BOT/DOT workspaces |
| Agent1 | [Open Agent1 guide](../Infographics/systemx-agent-1.svg) | Offer advisory security and access review |

The [combined atlas](../Infographics/systemx-atlas.svg) connects all eleven
individual subjects in one navigable overview. Read the full-size images or the
sections below for commands and small text; a reduced atlas is not a substitute
for an agent's detailed guide.

## Command convention

The examples assume an adopted project root containing `.SYSTEMX`. On macOS or
Linux, `bash .SYSTEMX/SYSTEMX.sh COMMAND --help` shows exact arguments. On
Windows, use `pwsh -File .SYSTEMX/SYSTEMX.ps1 COMMAND --help` where that
command is supported. A managed installation can route the same selected-root
command with `systemx run --target "/path/to/project" --offline -- COMMAND`.
For a registered child, explicitly choose `--project NAME` through
`systemx projects --target "/path/to/project" -- COMMAND`; never infer a child
from the last chat or current directory. A `|` between command names in a
graphic means alternatives, not a shell pipeline. Read-only and preview
commands are shown first; applying changes requires an explicit `--apply` where
supported. The [CLI guide](../../docs/CLI-TOOLS.md) governs actual syntax.

<a id="map-1"></a>

## System map 1 - Architecture

**Record locations.** The outer `.SYSTEMX/` holds shared template tools and a
selected root record scope. Its canonical context, plan, task state, and focus
are `GLOBAL/CONTEXT.md`, `PLAN/MASTER-PLAN.md`, `WORK/TASKS.json`, and
`WORK/FOCUS.json`. `ROOT/` retains optional request, plan, and observed-task
coordination. A registered child has its own records at
`.SYSTEMX/Projects/NAME/.SYSTEMXP/`; it is not another outer installation.

**Example prompt.** “Select the root or named child explicitly. Read its focus,
plan, and task ledger, then tell me the next incomplete task and its evidence.”

**CLI route.** `bash .SYSTEMX/SYSTEMX.sh validate`; `bash
.SYSTEMX/SYSTEMX.sh root roster`; for a child, `systemx projects --target
"/path/to/project" -- context --project NAME --agent agent.0`.

**Flow.** Human objective → selected scope → context and plan → canonical task
ledger → evidence and memory → owner review.

**Boundary.** A child keeps independent records. Its outer shared tools do not
merge child task status with root or sibling scopes.

<a id="map-2"></a>

## System map 2 - Task and evidence cycle

**Record locations.** `WORK/TASKS.json` owns status. Agent 0 coordinates work;
Agent X records event and time facts; Agent Y can run one explicitly selected
CLI task; Agent Z returns a fixed-policy review. ROOT may store harness and
optional BOT TODO observations and explicit `TASK-` bindings.

**Example prompt.** “For TASK-001, compare the saved harness observation with
the canonical task, assign bounded work, collect evidence, and present the
remaining delta for owner review.”

**CLI route.** `bash .SYSTEMX/SYSTEMX.sh root packet --help`; `bash
.SYSTEMX/SYSTEMX.sh root delta --help`; use `agent-x`, `agent-y`, and `agent-z`
help only for roles activated in that selected scope.

**Flow.** Objective → canonical `TASK-` record → optional X/Y/Z work → evidence
return → Agent 0 integration → designated owner acceptance and checkpoint.

**Boundary.** ROOT delta reads saved observations; it does not contact an IDE,
BOT, or provider. A CLI result or review score never accepts a task by itself.

<a id="map-3"></a>

## System map 3 - Governance records

**Record locations.** Agent Alpha selects references under `AUTOBOT/`. The
fixed `AUTOBOT/AGENDA-SETTINGS.json` catalog contains ten context-selection
definitions, all `unset` by default; selected project options remain empty.
`GLOBAL/ACCESS-MATRIX.json` starts with 20 default-deny role and instance rows.
`GLOBAL/ACCESS-DECISION-RULES.json` defines `no-row`, `gap`, `denied`, and
`reviewed-intent`; selected decisions start empty. Agent Beta records a named
BOT/DOT at `AGENTB/.SYSTEMXB-BOT_NAME/`. Agent1 uses `SECURITY/AGENT1/` and
its selected `AGENTS/agent.1/` state.

**Example prompt.** “Show the unset Agenda choices and Access Matrix revision.
Create no decision until I identify the actor, resource, evidence, owner, and
review time.”

**CLI route.** `bash .SYSTEMX/SYSTEMX.sh agenda catalog`; `bash
.SYSTEMX/SYSTEMX.sh agenda status`; `bash .SYSTEMX/SYSTEMX.sh agent-beta
status`; `bash .SYSTEMX/SYSTEMX.sh agent-1 status`.

**Flow.** Select reference → inspect catalogs and scope → review named actor and
evidence → preview a local decision → apply only when authorized → read back.

**Boundary.** The workbook is a readable view of canonical JSON. Even a
`reviewed-intent` row records a decision, not an OS, GitHub, IDE, or provider
permission. A named BOT/DOT folder starts offline. Agent1's checks are
warning-only; 20 categories × 20 questions and ten event buckets do not prove
a device is clean.

<a id="map-4"></a>

## System map 4 - First run and toolchain

**Record locations.** An adopted installation lives at the selected project
root. Local payloads under `DATA/` are ignored by Git by default. A host may
read selected records through the reviewed CLI or start the bounded
`service start --stdio` JSON-lines process explicitly. VS Code, Codex, Cursor,
Kiro, and JetBrains are host routes, not bundled native integrations.

**Example prompt.** “Preview first-time setup for this project, show my unset
provider and credential choices, and give me the read-only Agent 0 roster.”

**CLI route.** `systemx first-run --target "/path/to/project" --profile
project`; after adoption, `systemx run --target "/path/to/project" --offline
-- onboard status`, `onboard plan`, or `service status`.

**Flow.** Preview install → explicitly adopt one scope → inspect Agent1 and
provider choices → read CLI or stdio records → review work → release separately
from deployment.

**Boundary.** The stock provider, account, surface, and credential consumer
remain unset. The custom stdio protocol has fixed read-only methods; it is not
MCP, ACP, an installed IDE extension, or a persistent OS daemon. A GitHub
release record is not a deployment record.

## Agent 0

**Record location:** `.SYSTEMX/AGENTS/agent.0/` and optional `.SYSTEMX/ROOT/`.

**Example prompt:** “Plan one task, show the roster, gather evidence, then ask
the owner to review acceptance.”

**CLI:** `bash .SYSTEMX/SYSTEMX.sh root roster`; `bash .SYSTEMX/SYSTEMX.sh
root packet --help`; `bash .SYSTEMX/SYSTEMX.sh session-settings --compact`;
`bash .SYSTEMX/SYSTEMX.sh service status`.

**Five-step flow:** Select scope → read roster → plan task → review evidence →
designated owner accepts.

**Boundary:** Agent 0 coordinates canonical work and integration. A roster
entry does not start a worker or grant permission.

## Agent X

**Record location:** `.SYSTEMX/AGENTS/agent.x/` and selected-scope `EVENTS/`.

**Example prompt:** “Record the observed event and time, show due items, then
close only the reviewed event record.”

**CLI:** `bash .SYSTEMX/SYSTEMX.sh agent-x event --help`; `bash
.SYSTEMX/SYSTEMX.sh agent-x due --help`; `bash .SYSTEMX/SYSTEMX.sh agent-x
close --help`.

**Five-step flow:** Observe → record event → inspect due state → close reviewed
record → Agent 0 reviews.

**Boundary:** Agent X records history and due data; it does not execute a
scheduler, notification, or external action.

## Agent Y

**Record location:** `.SYSTEMX/AGENTS/agent.y/` and its selected `JOBS.json`.

**Example prompt:** “Prepare this one assigned task for the selected installed
CLI. Return branch or draft-PR evidence without merging.”

**CLI:** `bash .SYSTEMX/SYSTEMX.sh agent-y providers`; `bash
.SYSTEMX/SYSTEMX.sh agent-y prepare --help`; `bash .SYSTEMX/SYSTEMX.sh
agent-y run --help`; `bash .SYSTEMX/SYSTEMX.sh agent-y pr-ready --help`.

**Five-step flow:** Assign task → prepare isolated lane → run selected CLI →
return branch or PR evidence → owner reviews.

**Boundary:** Agent Y inherits host permissions and has no merge or task
acceptance authority. Native Windows `agent-y run --apply` remains unavailable
in this beta pending process-termination verification.

## Agent Z

**Record location:** `.SYSTEMX/AGENTS/agent.z/` and selected `REVIEWS/`.

**Example prompt:** “Review this evidence against the fixed policy, score only
supported answers, and show the changed findings.”

**CLI:** `bash .SYSTEMX/SYSTEMX.sh agent-z policy`; `bash .SYSTEMX/SYSTEMX.sh
agent-z prepare --help`; `bash .SYSTEMX/SYSTEMX.sh agent-z score --help`.

**Five-step flow:** Receive evidence → prepare review → answer fixed policy →
compare delta → advise owner.

**Boundary:** Agent Z's 100 questions across ten categories produce an
advisory scorecard, not task acceptance or certification.

## Agent Alpha

**Record location:** `.SYSTEMX/AGENTS/agent.a/` and `.SYSTEMX/AUTOBOT/`.

**Example prompt:** “Find one relevant AUTOBOT reference for this task. Leave
Agenda unset unless I select an option.”

**CLI:** `bash .SYSTEMX/SYSTEMX.sh autobot list`; `bash .SYSTEMX/SYSTEMX.sh
autobot context --help`; `bash .SYSTEMX/SYSTEMX.sh agenda catalog`; `bash
.SYSTEMX/SYSTEMX.sh agenda status`.

**Five-step flow:** Select reference → load bounded context → answer request →
review optional Agenda → share concise status.

**Boundary:** The ten AUTOBOT functions are reference selectors, not automatic
model workers. Agenda starts empty and runs no scheduler.

## Agent Beta

**Record location:** `.SYSTEMX/AGENTB/` and a generated
`.SYSTEMX/AGENTB/.SYSTEMXB-BOT_NAME/` for each named BOT or DOT.

**Example prompt:** “Set up one named BOT workspace. Link reviewed intent to a
canonical task.”

**CLI:** `bash .SYSTEMX/SYSTEMX.sh agent-beta setup`; `bash
.SYSTEMX/SYSTEMX.sh agent-beta bot-add --help`; `bash .SYSTEMX/SYSTEMX.sh
agent-beta access-link --help`; `bash .SYSTEMX/SYSTEMX.sh agent-beta assign
--help`.

**Five-step flow:** Set up → add named BOT → review access link → assign task →
Agent 0 reviews.

**Boundary:** A named folder stores offline identity and task references. It
does not log in, start a BOT, or grant OS or API access.

## Agent1

**Record location:** `.SYSTEMX/SECURITY/AGENT1/` and optional
`.SYSTEMX/AGENTS/agent.1/`.

**Example prompt:** “Review evidence and list `.env` names only. Suggest
rotation; never print secret values.”

**CLI:** `bash .SYSTEMX/SYSTEMX.sh agent-1 setup --help`; `bash
.SYSTEMX/SYSTEMX.sh agent-1 check --help`; `bash .SYSTEMX/SYSTEMX.sh agent-1
env-inventory --help`; `bash .SYSTEMX/SYSTEMX.sh agent-1 env-migrate --help`.

**Five-step flow:** Set up → ask questions → check local signals → preview key
names → advise owner.

**Boundary:** Agent1's 400-question catalog and ten event buckets support
warning-only review. A local scan does not certify a clean device; GitHub
Actions secrets cannot populate a local `.env` through symlinks. Sensitive
file operations fail closed on native Windows in this beta.

## Combined atlas

[Open the full-size atlas](../Infographics/systemx-atlas.svg). It places the
four system maps and seven agent guides into one reading path: selected scope
and canonical records → task and evidence cycle → governance records → host
toolchain and first run. Agent 0 coordinates the task; X, Y, and Z contribute
bounded records or reviews; Alpha, Beta, and Agent1 provide optional context,
workspace records, and advisory findings. Follow the full-size links above for
paths, command syntax, and readable detailed text. The atlas adds no new
status authority, service, provider connection, or access grant.

## Provenance and historical editions

[ASSETS.json](ASSETS.json) records exact current bytes and generated-art
provenance. The previous alpha field-guide JPEGs and beta.1 graphic suite remain
in [immutable beta.2 source history](https://github.com/WayneTechLab/dotSYSTEMX/tree/v1.11.0-beta.2/.SYSTEMX/MEDIA/Infographics)
and the separately verified private media archive. They are historical editions,
not current template assets. No video or Blender project is distributed in the
portable code repository.
