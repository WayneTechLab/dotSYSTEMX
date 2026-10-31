# Detailed agent field guides

These seven diagrams provide readable folder, prompt, CLI, process, and boundary text for
the second .SYSTEMX infographic set. Each SVG has a 7680 × 4320 canvas with exact vector
labels. The generated artwork has fewer native pixels; the canvas size does not create
native 8K illustration detail. The paths below are relative to an adopted project root.

From the project root on macOS/Linux, run `bash .SYSTEMX/SYSTEMX.sh ROLE --help`.
On Windows, run `pwsh -File .SYSTEMX/SYSTEMX.ps1 ROLE --help`. The installed
`systemx` package entry point does not expose these agent commands. In each SVG
panel, the first line is a copyable help command; `|` separates alternative
subcommands and is **not** a shell operator to paste. Replace `--help` with one
chosen subcommand and its required arguments. Preview first; `--apply` is explicit
where supported.
This repository has GitHub Actions disabled and includes no workflow.

## AGENT 0

[Open the detailed SVG](../Infographics/systemx-agent-0-detail.svg) — Project coordination and owner acceptance.

**Record location:** `.SYSTEMX/AGENTS/agent.0/`; `.SYSTEMX/ROOT/`.

**Example prompt:** “Plan this task, assign one owner, collect evidence, then ask me to review acceptance.”

**CLI help:** `bash .SYSTEMX/SYSTEMX.sh root --help`.

**Command panel:** `bash .SYSTEMX/SYSTEMX.sh root --help`; `Choose: init | status | packet | request`; `node | bind | observe | delta | card`; `Tasks: task-add | task-set`.

**Process:** Select scope → Add task → Route work → Review evidence → Owner accepts.

**Boundary:** Agent 0 owns canonical task coordination and integration. A task is accepted only by the designated owner; a card is evidence, not permission.

## AGENT X

[Open the detailed SVG](../Infographics/systemx-agent-x-detail.svg) — Event history, timing, and due-item records.

**Record location:** `.SYSTEMX/AGENTS/agent.x/`.

**Example prompt:** “Record this observed check and its time. Show what is due, then close the record when reviewed.”

**CLI help:** `bash .SYSTEMX/SYSTEMX.sh agent-x --help`.

**Command panel:** `bash .SYSTEMX/SYSTEMX.sh agent-x --help`; `Choose: event | list | schedule | due`; `close | validate`.

**Process:** Observe → Record event → Inspect due → Close record → Agent 0 reviews.

**Boundary:** Agent X records history and due status; it does not run a scheduler. A due item does not send a notification or perform an external action.

## AGENT Y

[Open the detailed SVG](../Infographics/systemx-agent-y-detail.svg) — Bounded CLI work and pull-request handoff.

**Record location:** `.SYSTEMX/AGENTS/agent.y/`.

**Example prompt:** “Prepare one assigned task for an installed CLI. Return branch or PR evidence for review; do not merge.”

**CLI help:** `bash .SYSTEMX/SYSTEMX.sh agent-y --help`.

**Command panel:** `bash .SYSTEMX/SYSTEMX.sh agent-y --help`; `Choose: providers | prepare | list | run`; `show | validate | pr-ready | recover`; `abandon | pr-cleanup | pr-close`.

**Process:** Assign task → Prepare lane → Run bounded → PR handoff → Recover / clean.

**Boundary:** Agent Y uses host permissions and a selected installed CLI. A PR handoff grants no merge authority or canonical task acceptance.

Native Windows `agent-y run --apply` is disabled in this beta pending
process-termination verification.

## AGENT Z

[Open the detailed SVG](../Infographics/systemx-agent-z-detail.svg) — Fixed, versioned evidence review.

**Record location:** `.SYSTEMX/AGENTS/agent.z/`.

**Example prompt:** “Review this evidence against the fixed policy. Score only supported answers and show the delta.”

**CLI help:** `bash .SYSTEMX/SYSTEMX.sh agent-z --help`.

**Command panel:** `bash .SYSTEMX/SYSTEMX.sh agent-z --help`; `Choose: policy | prepare | score`; `compare | validate`.

**Process:** Evidence packet → Prepare → Score policy → Compare delta → Advise owner.

**Boundary:** Agent Z asks 100 fixed questions across 10 categories. A scorecard is advisory evidence; it does not accept a task.

## AGENT ALPHA

[Open the detailed SVG](../Infographics/systemx-agent-alpha-detail.svg) — AUTOBOT references and optional Agenda settings.

**Record location:** `.SYSTEMX/AGENTS/agent.a/`; `.SYSTEMX/AUTOBOT/`.

**Example prompt:** “Find the relevant AUTOBOT reference for this task. Keep Agenda empty unless I choose a setting.”

**CLI help:** `bash .SYSTEMX/SYSTEMX.sh agent-a --help`.

**Command panel:** `bash .SYSTEMX/SYSTEMX.sh agent-a --help`; `Choose: init | list | context | request`; `complete | status`; `bash .SYSTEMX/SYSTEMX.sh agenda --help`.

**Process:** Select reference → Request context → Complete → Agenda optional → Share status.

**Boundary:** Agent Alpha routes up to ten bounded reference functions. Agenda defaults to empty; no worker or scheduler starts automatically.

## AGENT BETA

[Open the detailed SVG](../Infographics/systemx-agent-beta-detail.svg) — Named BOT and DOT workspace records.

**Record location:** `.SYSTEMX/AGENTB/`; `.SYSTEMX/AGENTB/.SYSTEMXB-BOT_NAME/`.

**Example prompt:** “Set up a named workspace for Atlas. Link only reviewed access intent to one task.”

**CLI help:** `bash .SYSTEMX/SYSTEMX.sh agent-beta --help`.

**Command panel:** `bash .SYSTEMX/SYSTEMX.sh agent-beta --help`; `Choose: setup | bot-add | access-link`; `assign | status | validate`.

**Process:** Set up → Add named bot → Review link → Assign task → Validate → Agent 0 reviews.

**Boundary:** The named folder records scope and task references only. It does not log in, launch a provider, or grant OS or API access.

## AGENT 1

[Open the detailed SVG](../Infographics/systemx-agent-1-detail.svg) — Advisory security and access assessment.

**Record location:** `.SYSTEMX/SECURITY/AGENT1/`; `.SYSTEMX/AGENTS/agent.1/`.

**Example prompt:** “Review security evidence and inventory .env names only. Suggest rotations; do not print credential values.”

**CLI help:** `bash .SYSTEMX/SYSTEMX.sh agent-1 --help`.

**Command panel:** `bash .SYSTEMX/SYSTEMX.sh agent-1 --help`; `Choose: setup | questions | check | review`; `status | env-inventory | env-sanitize`; `env-migrate`.

**Process:** Set up → Ask 400 → Check → Review → Preview env → Advise owner.

**Boundary:** Twenty categories and ten event buckets yield advisory findings. Actions is disabled here. No device-clean claim or live secret write is made.

On native Windows, metadata first setup, status, questions, and
warning-only filename checks remain available. Dotenv inventory,
sanitize, and migrate; answer-file review; and setup reconfiguration
fail closed. Actions remains disabled in this repository.

Agent Beta's named folder and Agent 1's `agent.1` record are generated local state;
neither is a second portable source copy. The Access Matrix records reviewed intent and
does not grant OS or provider permission. Agent 1's `.env` commands use names-only shared
records; sensitive file operations fail closed on native Windows in this beta.
