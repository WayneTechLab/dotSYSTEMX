# Full-system infographic generation prompt

Mode: built-in imagegen. Use case: `infographic-diagram`.
Requested canvas: 3840 × 2160, landscape. Inspect actual output dimensions before publication.
The standard roles are Agent 0, Agent X, and Agent Z; there is no standard Agent Y.

```text
Use case: infographic-diagram
Asset type: a single public GitHub README/wiki systems architecture infographic, downloadable as a large HD poster.
Primary request: Show the complete .SYSTEMX operating model, standard folders, Agent 0 / X / Z and subagents, logging, toolchain and project lifecycle in ONE exceptionally clear, detailed infographic. Render at 3840 x 2160 pixels, landscape 16:9, 4K. Do not substitute a screenshot, mockup, photographed poster, or tiny low-resolution thumbnail.
Style: professional editorial technical infographic, crisp near-vector raster artwork, precise readable sans-serif typography, monospace file paths, disciplined modular grid, clean white opaque background, black/graphite branding like the existing monochrome folder-with-branch .SYSTEMX mark. Restrained functional accent colors distinguish records, agents, external tools and evidence; not a rainbow. Simple folder, document, terminal, clock and checklist line icons. Content is the hero. No decorative robots, heads, glowing brain, circuit-board wallpaper, stock art or oversized empty areas.
Typography: meticulously spell all labels below. Legibility and exact text take priority. All text horizontal, no clipped boxes or crossing arrows. Make section titles large, body readable at full resolution. Leading dot and uppercase .SYSTEMX and .SYSTEMXP must remain exact. Agent Z is the reviewer; there is NO Agent Y in this standard. Do not print Wayne Tech Lab or any other company attribution. No brand logos for third-party tools.

Composition: top title and a thin workflow band; a broad central Agent 0 hub connecting orderly surrounding storage, worker, time, review and toolchain panels; lower portfolio and lifecycle panels; small clear legend and footer. All of this must read as one connected architecture, not disconnected slides. Use short numbered process nodes, arrows with small labels (read, assign, report, record, assess, accept, checkpoint), and dashed boundaries for optional or externally supplied capabilities. Ensure arrows reflect the relationships described below rather than inventing automatic synchronization.

Title verbatim: ".SYSTEMX"
Subtitle verbatim: "THE COMPLETE WORKSPACE • CONTEXT, AGENTS, TOOLS & EVIDENCE"

Top process strip, exact labels in order:
"RESEARCH" → "PHASES & MILESTONES" → "TASKS & WAVES" → "WORK & INTEGRATE" → "VERIFY & REVIEW" → "ACCEPT & CHECKPOINT"
Small strip caption: "Resume the next accepted step • Stop when the agreed outcome is met"

Panel: "1  SHARED CONTEXT"
".SYSTEMX/"
"START-HERE.md • AGENTS.md • STANDARD.md"
"GLOBAL/CONTEXT.md — intent and constraints"
"PLAN/MASTER-PLAN.md — outcomes and milestones"
"MEMORY/PROJECT.md — reviewed durable facts"
"MEMORY/sessions/ — saved checkpoints"
"Read the selected scope and relevant changes"
Arrow from this panel to Agent 0 labeled "read".

Central prominent panel: "2  AGENT 0 • COORDINATOR"
"agent.0"
"Decompose • route • integrate • accept"
"One canonical writer per scope"
"AGENTS/REGISTRY.json"
"AGENTS/<id>/MEMORY.md"
Connect to a small fan of three worker cards titled "AUTHORIZED SUBAGENTS" with labels "agent.1", "agent.2", "agent.N".
Worker caption: "Scoped tasks • dependencies • separate write areas"
"Up to 10 by request, subject to harness limits"
Arrows Agent 0 to workers "assign"; workers to Agent 0 "report + evidence". Worker execution connects to external toolchain. Do not imply registering an agent starts a process.

Panel: "3  CANONICAL WORK"
"WORK/TASKS.json — task authority"
"WORK/FOCUS.json — current objective"
A small process: "todo → in_progress → needs_review → done"
"Generated views:"
"TODO • WORKING-ON • BLOCKED"
"REVIEW • DONE • CANCELLED"
"CURRENT.md — current summary"
Agent 0 updates canonical work; canonical work generates views. Do not draw separate writable ledgers for the views.

Panel: "4  AGENT X • TIME & EVENTS"
"agent.x"
"EVENTS/EVENTS.json"
"EVENTS/SCHEDULE.json"
"Actor • occurrence time • recorded time"
"Revision • evidence • retry key • due item"
"Tracks schedules; does not execute them"
Dashed label: "After roles-init activation"
Connect actual work/check results to Agent X with "record"; Agent X writes EVENTS records.

Panel: "5  AGENT Z • FIXED REVIEW"
"agent.z"
"10 categories × 10 questions = 100 checks"
"REVIEWS/POLICY.json"
"REVIEWS/policies/ • requests/ • reports/"
"Scorecard • unknowns • evidence • delta"
"Reuse unchanged reviews"
"Advisory score; Agent 0 / user accepts"
Dashed label: "After roles-init activation"
Arrow evidence from work and events into review "assess". Arrow review to Agent 0 "findings". At acceptance branch show "Met → checkpoint / finish" and "Gap → next bounded task"; no endless automatic rebuild cycle.

Panel: "6  TOOLCHAIN & EXECUTION"
"Your IDE / CLI / chat / bot harness"
"Model sessions • authorized subagents • permissions"
"SYSTEMX.sh / SYSTEMX.ps1 • WSG-MENU.sh"
"Python library / systemx CLI"
"manager.py • lifecycle.py — setup and receipts"
"scripts/ — tasks, scope routing, Agent X/Z"
"project.json — explicit command arrays"
"Checks • builds • authorized deploys"
"Actual run IDs, artifacts and live probes"
Clearly mark harness and application tools as "EXTERNAL TOOLS"; .SYSTEMX stores records and invokes configured tools, it does not contain a model or install a cloud automatically.

Lower wide panel: "7  SYSTEMX PROJECTS"
"Projects/REGISTRY.json — explicit selection"
".SYSTEMX/Projects/NAME/.SYSTEMXP"
"Each child: GLOBAL/ • PLAN/ • WORK/ • MEMORY/ • AGENTS/"
"SOURCES.json • DECISIONS/ • SYNC/"
"Optional child EVENTS/ and REVIEWS/"
"One outer tool installation • isolated child records"
Show two small named examples "WebApp/.SYSTEMXP" and "Research/.SYSTEMXP", both attached through Projects, never nest .SYSTEMX.

Lower panel: "8  DEFAULTS, SETUP & RECOVERY"
"config/ • profiles/ • templates/ • AI/ • docs/ • tests/"
"VERSION • SOURCE.json • LICENSE"
"INSTALLATION.json — selected defaults"
".SYSTEMX/.systemx/ — internal versions and logs"
"Install → pin → preview update → audit"
"Additive updates preserve existing project files"
"Uninstall / restore with receipts"
"Manual updates by default • startup checks opt-in"
Label managed metadata/cache "After installation".
Tiny exact-case note: "Optional sibling alias: .systemx → .SYSTEMX"

Transport line separate from core record arrows:
"Git • local folders • Drive • cloud storage • VMs"
"Authorized access + verified snapshots; a URL alone does not sync records"

Footer exact text:
"Your tools run the work. .SYSTEMX keeps intent, state, time, evidence and memory connected."
"ALPHA • Role definitions are not running agents • Evidence supports acceptance"

Constraints: One coherent 4K infographic. Include all eight numbered sections, major paths, Agent 0/X/Z responsibilities and correct logging/review/acceptance direction. Do not invent Agent Y, built-in schedulers, cloud adapters, AGI, consciousness, automatic model learning, guaranteed savings or automatic deployment. No task history, private data or organization-specific setup. Preserve all exact path capitalization.
```

## Correction pass

The first pass was 1672 × 941 pixels and had a reversed review arrow and an unclear
acceptance heading. This targeted edit requested the corrected flow and 4K size.

```text
Edit the supplied .SYSTEMX infographic. Preserve its entire eight-panel layout, current wording and paths, all folder and tool icons, role colors, hierarchy, .SYSTEMX-only branding and opaque white background. Make ONLY these corrections:
1. Reverse the red "assess evidence" arrow between panel 3 CANONICAL WORK and panel 5 AGENT Z. It must point DOWN from work evidence into the Agent Z reviewer, not up from the reviewer into tasks.
2. Replace the garbled heading on the lower-right acceptance decision box with exactly "AGENT 0 / USER • ACCEPTANCE". Preserve both branches "Met → checkpoint / finish" and "Gap → next bounded task". The Agent Z "findings" arrow should continue to end at this acceptance box.
3. Deliver the final corrected image at EXACTLY 3840 × 2160 pixels, a genuine 4K landscape output, with all small lettering carefully regenerated sharp enough to read at full resolution. The previous result was only 1672 × 941. This explicit pixel dimension is a requirement; do not simply return that smaller dimension again. Preserve the framing and proportions across the full 16:9 canvas.
Correct spelling is critical: .SYSTEMX, .SYSTEMXP, Agent 0, Agent X, Agent Z, SOURCES.json. No Agent Y. No added claims or logos. Do not remove any of the eight sections or reduce the content.
```

## Output inspection

Both built-in generations returned 1672 × 941 pixels despite the explicit 4K
request. The corrected native master is `systemx-full-system.png`. Its review
arrow points from work evidence into Agent Z, and the acceptance owner is
explicitly Agent 0/user. No fallback API or CLI generation was used.

## Approved 4K export

The user explicitly selected “Export a 4K PNG and retain the original.” The
corrected master was exported with macOS `sips -z 2160 3840` into
`systemx-full-system-4k.png`. Its PNG header verifies **3840 × 2160** pixels.
This is an upscaled delivery copy, not additional generated detail.
