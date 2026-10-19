# Historical CLI and .SYSTEMXP full-system infographic prompt

This is the retained production record for the previous one-page map, which
predates Agent Alpha/AUTOBOT. The current four-page manual has its own
[generation and correction prompts](../../.SYSTEMX/MEDIA/Reference/systemx-field-guide-prompts.md)
and [accessible field guide](../../.SYSTEMX/MEDIA/Reference/systemx-field-guide.md).
The current feature baseline is 1.11.0-alpha.2; ROOT-inclusive media edition
1.11.0-alpha.3 shows SX-RULES, SX-MILESTONE, and explicit TODO reconciliation.
The historical prompt blocks below remain unchanged.

Mode: built-in imagegen edit. The alpha.4 four-role poster was the target and
style reference. This edition emphasizes executable CLI entry points and exact
child-project routing while retaining Agent 0/X/Y/Z responsibilities.
The former [4K web PNG](https://github.com/WayneTechLab/dotSYSTEMX/blob/v1.10.0-alpha.2/docs/assets/systemx-full-system.png)
and [portable JPEG](https://github.com/WayneTechLab/dotSYSTEMX/blob/v1.10.0-alpha.2/.SYSTEMX/MEDIA/Infographics/systemx-cli-projects-4k.jpg)
are retained in tagged history. Their actual dimensions and exact-byte hashes
remain in the [historical asset metadata](https://github.com/WayneTechLab/dotSYSTEMX/blob/v1.10.0-alpha.2/.SYSTEMX/MEDIA/Reference/ASSETS.json).

```text
Use case: infographic-diagram
Asset type: public .SYSTEMX full-system technical poster, current CLI and SYSTEMX PROJECTS edition.
Input image: existing full-system poster is the EDIT TARGET. Preserve product mark, clean white editorial infographic style, colored bars, nine-section architecture, Agent 0/X/Y/Z correct roles, scoped app/IDE subagents, task statuses, Agent Y draft/ready/close/archive/cleanup, Agent Z 100 checks, setup/recovery and external transport caveats. Keep all section names and labels readable and exact. Do not show company attribution or third-party brand logos.
Primary edit: clearly expand and emphasize the CLI/toolchain and .SYSTEMXP panels. These two areas must be readable focal points, with terminal command typography and a visible hierarchical project tree, rather than tiny footer mentions. Re-layout and enlarge them while retaining the full system. Requested landscape canvas 3840x2160 4K.
Title ".SYSTEMX"
Subtitle "CLI & TOOLS • .SYSTEMXP PROJECTS • AGENTS 0 / X / Y / Z"

Replace panel 7 with "7  CLI & TOOLS"
Exact short lines:
"EXTERNAL CLI: systemx"
"first-run • install • status • policy • update"
"audit • uninstall • restore • export-chat"
"systemx projects --target OUTER -- list"
"LOCAL LAUNCHERS"
"SYSTEMX.sh • SYSTEMX.ps1"
"tools-guide • doctor • validate"
"PYTHON API: run() • projects() • export_chat()"
"Git + gh — authorized branch / PR operations"
"Codex / Copilot / configured CLI — Agent Y"
"Outer target • selected defaults • explicit scope"
"No automatic provider install or permission grant"
Use a terminal icon and a dashed boundary for external tools. Do not confuse systemx management status with task status.

Replace panel 8 with "8  SYSTEMX PROJECTS • .SYSTEMXP"
Show an obvious tree with precise spelling:
".SYSTEMX/"
"├── scripts/ • selected defaults • shared tools"
"└── Projects/"
"    ├── Project-A/.SYSTEMXP/"
"    └── Project-B/.SYSTEMXP/"
Use two distinguishable sibling project folder cards, Project-A and Project-B. Their .SYSTEMXP folders should be large legible labels. Include:
"Each child: GLOBAL/ • PLAN/ • WORK/ • MEMORY/"
"AGENTS/ • SOURCES.json • DECISIONS/ • SYNC/"
"Optional: EVENTS/ • Agent Y jobs • REVIEWS/"
"projects context --project Project-A"
"projects roles-init --project Project-A"
"One outer tool installation • separate child records"
"Never nest .SYSTEMX inside .SYSTEMX"
Show a routed arrow from panel 7 CLI/tools to selected Project-A captioned "explicit --project", and show Project-B remaining separate; do not imply tasks or memory merge between children.
Explain OUTER with a brief caption "OUTER = directory containing .SYSTEMX".
Panel 9 should retain managed cache ".SYSTEMX/.systemx/" clearly different from child ".SYSTEMXP" and sibling ".systemx → .SYSTEMX" alias.
All other semantic content remains accurate. Agent X records observed events and does not execute schedules. Agent 0/user owns acceptance. Agent Y has no merge command. Role records do not start agents. Cloud/Drive URL alone does not sync records. Retain alpha footer. Use exact .SYSTEMX/.SYSTEMXP case everywhere. No clipped panels, overlapped labels or invented commands. At full size legibility takes priority over decorative detail.
```

## Targeted command correction

The final edit makes child operations arguments to the actual external CLI,
rather than implying a standalone `projects` executable:

```text
Change ONLY the small black terminal example inside the Project-A card in panel 8. It currently shows '$ projects context ...' and '$ projects roles-init ...', which could falsely imply a standalone projects executable. Replace with exactly three readable lines (no dollar signs): 'systemx projects --target OUTER --' then 'context --project Project-A' then 'or: roles-init --project Project-A'. The 'or:' makes clear the last two lines are alternative subcommands appended to the prefix, not a single combined command. Preserve all other content, panel 7's correct full CLI command, the .SYSTEMXP tree, Agent 0/X/Y/Z, all role boundaries and existing design. Do not introduce any new labels, folders, command flags or arrows. Maintain landscape 16:9; request native 3840x2160 where possible.
```

The built-in tool returned 1672 × 941 pixels. Those historical exports use a
3840 × 2160 canvas resized with macOS `sips`; this adds no native detail.
The portable output stays below the installer's 2 MiB per-file limit.
