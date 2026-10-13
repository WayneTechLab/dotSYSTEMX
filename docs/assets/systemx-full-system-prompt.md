# Current four-role full-system infographic prompt

Mode: built-in imagegen edit. Use case: `infographic-diagram`.
The previous Agent 0/X/Z poster served as the edit target and style reference.
This artwork depicts the current Agent 0/X/Y/Z workflow; previous art remains
available in tagged Git history. Company attribution is separate from the mark.
The selected public exports and actual generation dimensions are recorded in
the [media asset metadata](../../.SYSTEMX/MEDIA/Reference/ASSETS.json).

```text
Use case: infographic-diagram
Asset type: current public .SYSTEMX GitHub README/wiki architecture infographic.
Input image: existing .SYSTEMX full-system poster, EDIT TARGET and visual style reference. Update and reorganize it to include Agent Y as a first-class standard role alongside Agent 0, Agent X, Agent Z. The old image is out of date. Preserve its white editorial technical style, black folder-branch .SYSTEMX product mark, clean line icons, colored section bars, precise horizontal typography. Re-layout as necessary for equal readable panels, a prominent Agent 0 hub and coherent labeled arrows. Produce a landscape 3840 x 2160 4K image.
Product title exactly ".SYSTEMX".
Subtitle "CONTEXT • AGENTS 0 / X / Y / Z • TOOLS • EVIDENCE".
No Wayne Tech Lab text, company logos, robots, AI brains, AGI claims, automatic cloud sync, automatic merge, or guaranteed savings.
Use all these concise numbered panels with exact capitalization and accurate path labels:
1 SHARED CONTEXT
".SYSTEMX/"
"START-HERE.md • AGENTS.md • STANDARD.md"
"GLOBAL/CONTEXT.md — intent & constraints"
"GLOBAL/ACCESS-MATRIX.md — reviewed authority"
"PLAN/MASTER-PLAN.md — outcomes & milestones"
"PLAN/MAP.md — sources & toolchain"
"MEMORY/PROJECT.md • MEMORY/sessions/"
2 AGENT 0 • COORDINATOR
"agent.0"
"Plan • assign • integrate • accept"
"One canonical writer per scope"
"AGENTS/REGISTRY.json"
"AGENTS/<id>/MEMORY.md"
"APP / IDE SUBAGENTS: agent.1 • agent.2 • agent.N"
"Up to 10 by request; harness limits apply"
3 CANONICAL WORK
"WORK/TASKS.json — task authority"
"WORK/FOCUS.json — current objective"
"todo → in_progress → needs_review → done"
"Blocked / cancelled remain explicit"
"Generated: TODO • WORKING-ON • BLOCKED"
"REVIEW • DONE • CANCELLED • CURRENT.md"
4 AGENT X • TIME & EVENTS
"agent.x"
"EVENTS/EVENTS.json"
"EVENTS/SCHEDULE.json"
"Actor • occurrence time • recorded time"
"Revision • evidence • retry key"
"Tracks due items; host executes schedules"
5 AGENT Y • EXTERNAL CLI & PR
"agent.y"
"AGENTS/agent.y/JOBS.json"
"Selected per task: Codex / Copilot / configured CLI"
"Task packet → isolated Git worktree"
"Run → scoped commit → optional DRAFT PR"
"Agent 0 accepts → separate READY step"
"Cancelled → CLOSE; preserve unmerged work"
"Merged + accepted → archive → CLEANUP"
"No merge command • host permissions apply"
6 AGENT Z • FIXED REVIEW
"agent.z"
"REVIEWS/POLICY.json"
"10 categories × 10 questions = 100 checks"
"REVIEWS/policies/ • requests/ • reports/"
"Evidence • unknowns • scorecard • delta"
"Reuse unchanged reviews; scores advise"
7 TOOLCHAIN & EXECUTION
"Your IDE / CLI / chat / bot harness"
"Models • tools • permissions • real processes"
"SYSTEMX.sh • SYSTEMX.ps1 • systemx CLI"
"Python library • scripts/ • project.json"
"Checks • builds • authorized delivery"
"Role records do not start agents"
8 SYSTEMX PROJECTS
".SYSTEMX/Projects/NAME/.SYSTEMXP"
"Projects/REGISTRY.json — explicit selection"
"Each child: GLOBAL/ • PLAN/ • WORK/"
"MEMORY/ • AGENTS/ • SOURCES.json"
"DECISIONS/ • SYNC/ • optional EVENTS/ & REVIEWS/"
"One outer tool installation; separate child records"
"Never nest a second .SYSTEMX"
9 DEFAULTS, SETUP & RECOVERY
"config/ • profiles/ • templates/ • AI/ • docs/ • tests/"
"VERSION • SOURCE.json • LICENSE"
"INSTALLATION.json — selected defaults"
".SYSTEMX/.systemx/ — versions & logs"
"Install → pin → preview update → audit"
"Additive updates preserve user files"
"Uninstall / restore with backups & receipts"
"Manual by default; startup notices opt-in"
"Siblings: optional .systemx → .SYSTEMX alias"
Top slim process strip: "RESEARCH → PHASES & MILESTONES → TASKS & WAVES → WORK & INTEGRATE → VERIFY & REVIEW → ACCEPT & CHECKPOINT".
Small separate storage strip: "Git • local folders • Drive • cloud storage • VMs — authorized access and verified snapshots".
Connections must show Context → Agent 0 → app/IDE workers AND separately Agent Y task CLI; both execution lanes return evidence to Agent 0. X records meaningful events across lanes; Z reviews evidence and returns findings to Agent 0/user acceptance. Do not show X or Z as automatically executing work. Include acceptance caption "Met → checkpoint / finish • Gap → next bounded task".
Footer: "ALPHA • Roles do not grant permissions • Evidence supports acceptance • URLs do not synchronize records".
Most important: spell Agent Y correctly and include its full optional draft/ready/close/cleanup lifecycle. All leading dots and uppercase .SYSTEMX and .SYSTEMXP exact. Do not cram unreadable tiny footnotes, overlap boxes, clip text, cross arrows over labels or invent folders. Maximize text accuracy and clear visual hierarchy.
```

## Targeted correction

The first output's Agent 0 → X arrow used an assignment label. The final edit
replaced that label with `record observed events`, preserving all other panels:

```text
Correct only the green downward arrow from AGENT 0 to AGENT X: replace its label 'assign via IDE/API' with 'record observed events'. Agent X records events, never executes an assignment. Preserve every panel, all file paths, exact role labels, entire Agent Y lifecycle, white design, colors, icons, layout and other arrows. Do not add any new claims or decoration. Fix any obvious spelling typo in 'in_progress' if necessary. Maintain landscape 16:9. Export as 3840x2160 if possible.
```

The tool produced 1672 × 941 pixels. The public exports use a 3840 × 2160
canvas, resized with macOS `sips`; resizing adds no native detail. Only the
latest 4K web PNG and portable JPEG ship; the native source is retained outside
the repository. Exact-byte checksums are in the media asset metadata.
