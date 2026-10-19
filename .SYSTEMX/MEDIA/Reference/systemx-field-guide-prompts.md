# .SYSTEMX four-part field guide — generation prompts

Media edition **1.11.0-alpha.3**, feature baseline **1.11.0-alpha.2**.

Generated using the built-in imagegen tool. The corresponding previous image was inspected and supplied as a style reference. Each request consists of the common specification followed by its page specification. Only the selected 3840 × 2160 exports ship; native originals are retained outside the repository. Exact dimensions, export method and byte hashes are in [ASSETS.json](ASSETS.json). A requested 4K canvas does not establish native 4K detail. Read the [accessible companion](systemx-field-guide.md) for full mechanics and limits. The previous edition remains in [tagged history](https://github.com/WayneTechLab/dotSYSTEMX/tree/v1.10.0-alpha.3/.SYSTEMX/MEDIA).

## Common specification

```text
Use case: infographic-diagram. Asset: one page of a coherent four-page public .SYSTEMX technical field guide.
The supplied image is a STYLE REFERENCE of this page's previous edition, already inspected. Redesign the page to fit ROOT; retain recognizable large bold black .SYSTEMX wordmark with small outline folder/network mark, white background, editorial headings, restrained colored section bars, thin borders, functional line icons, crisp sans-serif and monospace labels. Requested output 3840 x 2160 landscape 16:9, 4K. ONE page, not a collage. Generous margins and medium-size readable text. Exact labels matter more than decoration.
Colors: Agent0 green, X blue, Y coral, Z violet, Alpha amber, scopes teal, DATA graphite, ROOT dark blue. No robot faces, brains, AGI claims, third-party logos or Wayne Tech Lab attribution. Brand only .SYSTEMX. Exact case: .SYSTEMX, .SYSTEMXP, SX-RULES.md, SX-MILESTONE.md, PLAN.json, MIRRORS.json, WORK/TASKS.json. AUTOBOT filenames use uppercase .MD. No invented paths or commands.
All diagrams describe on-demand coordination, not automatic continuous provider synchronization. Status authority is only WORK/TASKS.json. Host tools and permissions control execution. Footer: ALPHA • On demand • Roles do not grant permissions. Page number upper right.
```

## 01-overview

Output: `systemx-field-guide-01-overview-4k.jpg`

```text
Page 01 / 04. Title .SYSTEMX. Subtitle THE COMPLETE SYSTEM WITH ROOT.
Five spacious architecture bands.
1 Top context strip: Human objective + authorized harness tools. Four record cards: GLOBAL/CONTEXT.md — purpose; PLAN/MASTER-PLAN.md — outcomes; WORK/TASKS.json — canonical status; MEMORY/PROJECT.md — continuity.
2 Prominent ROOT/ band with four file cards: SX-RULES.md — internal contract; SX-MILESTONE.md — planning + tool cards; PLAN.json — requests + structure; MIRRORS.json — bindings + observations + cards. Caption: ROOT links context and work; it does not own task status.
3 Green AGENT 0 • agent.0 — plan, assign, integrate, accept. Direct branches to blue AGENT X • agent.x — events + time; coral AGENT Y • agent.y — selected CLI + owned worktree + optional draft PR; violet AGENT Z • agent.z — evidence review: 10 × 10 fixed checks. Results and evidence return to Agent0. Small precise notes: X records; host executes schedules. Y has no merge command. Z is advisory. Separate tools bar: TOOLS: systemx CLI • shell / PowerShell • Python API • installed providers. Native IDE subagents and external CLI are distinct lanes.
4 Large amber AGENTA • AGENT ALPHA • agent.a panel: selected references on demand; results return to Agent0. AUTOBOT/ has all TEN exact filenames in two rows of five: Design.MD, Soul.MD, Memory.MD, Rules.MD, Research.MD; Brand.MD, Media.MD, Tokens.MD, Data.MD, Archive.MD. Caption: Alpha is outside the 10 reference slots. Adjacent compact DATA/ panel: TEMP • LARGE • IMPORTS • RESEARCH • ASSETS • EXPORTS • CACHE • ARCHIVE. Caption: payload Git-ignored by default; scaffold guides tracked. Adjacent PROJECTS panel: .SYSTEMX/Projects/ → Project-A/.SYSTEMXP/ and Project-B/.SYSTEMXP/. Caption: independent records; shared outer tools; optional child ROOT.
5 Bottom sync strip: SYSTEMX tasks + observed harness TODO + optional bot TODO → read-only delta → Agent0 + authorized tools → readback + evidence → checkpoint. Note: Explicit TASK-ID bindings • snapshots are not live sync • reuse unchanged results.
Do not route assignments through AgentX. Preserve all ROOT files, 5 agent identities and 10 specialists.
```

## 02-agent-coordination

Output: `systemx-field-guide-02-agent-coordination-4k.jpg`

```text
Page 02 / 04. Title .SYSTEMX. Subtitle THREE TODO SURFACES, ONE TASK AUTHORITY.
This is a spacious reconciliation diagram, not four duplicate large agent cards.
Top ROOT contract strip: ROOT/SX-RULES.md — operating rules; ROOT/SX-MILESTONE.md — planning + tool-card contract.
Main upper area three columns, visibly different authority labels. Left green CANONICAL SYSTEMX: WORK/TASKS.json; stable TASK IDs • owner • acceptance • evidence; todo / in_progress / blocked / needs_review / done / cancelled. Middle blue IDE / HARNESS TODO, labeled OBSERVED: actual app plan or task list; native tool readback • item ID • raw state. Right teal OPTIONAL BOT TODO, labeled OBSERVED: cloud / bot run or external CLI attempt; run handle • item ID • observed result.
Bindings converge into ROOT/MIRRORS.json: Scope + TASK-ID mappings; many-to-many, not equal item counts. Snapshot fields: raw + normalized state; observed + recorded time; source revision + evidence; canonical fingerprints. Revision is caller-supplied, not authenticated by ROOT.
Large central process: 1 Select scope + tasks → 2 Read actual external TODOs → 3 Retain bindings + snapshots → 4 Run read-only delta → 5 Agent0 reconciles via authorized tools → 6 Read back + retain new evidence → 7 Review + checkpoint. Straight arrows, no always-running loop. At most one return arrow labeled on change / handoff from readback to new observation.
Delta findings panel: unmapped • unavailable • unknown • state difference • stale canonical • revision difference / unverified. Bot layer is opt-in; absent is not assessed. All bound TASKs participate in aggregate state and fingerprint checks.
Clearly labeled EXAMPLE: harness item H-01 → TASK-001 done + TASK-002 in_progress → expected external running. One binding can cover several tasks.
Acceptance strip: todo → in_progress → needs_review → done. Side exits blocked / cancelled. done requires evidence + reviewer agent.0 or user. External completed, CLI exit 0, a draft PR or Agent Z score does not mean done.
Compact roles bar: Agent0 reconciles / accepts • X records events / time • Y runs selected CLI • Z reviews evidence • Alpha supplies selected references. Boundary: ROOT records local observations; actual tools perform provider writes.
```

## 03-autobot-panel

Output: `systemx-field-guide-03-autobot-panel-4k.jpg`

```text
Page 03 / 04. Title .SYSTEMX. Subtitle ROOT PLANNING & ON-DEMAND SPECIALISTS.
Top third two technical panels. Left ROOT PLAN: SX-RULES.md — internal contract below actual user / host instructions. SX-MILESTONE.md — vocabulary + tool-card contract. PLAN.json — RTask / STask provenance + structural nodes. Hierarchy Milestone → Wave → Phase → optional Group → Task → optional Subtask → Single action. Skip levels; counts follow the project. RTask = originating request; STask = bounded child request. Task status stays in WORK/TASKS.json.
Right BOUNDED TOOL CARD: MIRRORS.json retains cards + observations. Short field list: Task + purpose; selected context; intended tool + arguments; permissions; expected evidence; stop conditions. Caption: A card describes a call; the authorized harness executes it. ROOT packet ≤ 10 tasks / 64 KiB; other ROOT responses ≤ 128 KiB. No automatic tool execution.
Amber AGENTA • AGENT ALPHA • agent.a routing band: Agent0 / X / Y / Z / Tools → selected AUTOBOT references → result + evidence → Agent0. AUTOBOT/AGENTA.MD; Alpha is outside the ten slots.
Exactly 10 specialist cards, 5 columns by 2 rows. Exact bold filename + one short detail line: Design.MD — layouts + accessibility; Soul.MD — purpose + voice; Memory.MD — summaries + decisions; Rules.MD — policy references; Research.MD — sources + uncertainty; Brand.MD — identity + brand kit; Media.MD — logo + ICO + asset rights; Tokens.MD — fonts + CSS + themes; Data.MD — handling + provenance; Archive.MD — superseded reference index. Reference files, not autonomous running models.
Bottom lifecycle: Select references → purpose + input revision → fingerprint sources → Matching request? YES → reuse retained result; NO → retain request → explicit response + evidence. No repeat loop.
Small records/limits panel: AUTOBOT/CATALOG.json • AUTOBOT/REQUESTS.json; selected context ≤ 64 KiB; reference file ≤ 256 KiB; ledger ≤ 8 MiB / 4096 requests. Initialize root and child panels separately from blank seeds. References do not start models or accept tasks.
```

## 04-data-projects

Output: `systemx-field-guide-04-data-projects-4k.jpg`

```text
Page 04 / 04. Title .SYSTEMX. Subtitle SCOPED ROOT, DATA & THE TOOLCHAIN.
Four spacious quadrants.
Upper left ONE OUTER INSTALLATION: .SYSTEMX/ tree contains ROOT/, GLOBAL/, PLAN/, WORK/, MEMORY/, AGENTS/, AUTOBOT/, DATA/, MEDIA/, scripts/, config/, templates/, Projects/. Under Projects/ show siblings Project-A/.SYSTEMXP/ and Project-B/.SYSTEMXP/. Two small child cards show ROOT/ optional, GLOBAL/, PLAN/, WORK/, MEMORY/, AGENTS/; AUTOBOT/ + DATA/ optional. Caption: shared outer tools + selected version; independent tasks, bindings and evidence. Carry scope with every TASK ID. Never create .SYSTEMX inside .SYSTEMX.
Upper right DATA/ — LOCAL PAYLOAD. Eight cells: TEMP — scratch; LARGE — datasets / binaries; IMPORTS — original inputs; RESEARCH — source captures; ASSETS — logos / fonts; EXPORTS — delivery drafts; CACHE — reproducible output; ARCHIVE — inactive payload. Caption: payload ignored by Git by default; exact scaffold guides tracked. Git ignore is not encryption, tracked-history removal or cloud-sync control. DATA audit checks sampled rules + tracked index, not every untracked path. No automatic ingestion or upload. MEDIA/ is the separate public graphics folder.
Lower left CLI & PROJECT ROUTING. Three complete monospace lines with enough width:
systemx run --target OUTER --offline -- root init
systemx run --target OUTER --offline -- root delta --layer harness --layer bot
systemx projects --target OUTER -- root status --project Project-A
OUTER = directory containing .SYSTEMX. ROOT must be initialized first. Init previews; --apply writes. Delta reads only. Child ROOT initializes independently. Tool bar: Bash / PowerShell • Python 3.9+ library • Git + gh for optional PR work. Native IDE subagents and external CLI workers are distinct.
Lower right UPDATES & RECOVERY: Manual updates by default; opt-in startup notices only. Pin reviewed release + trusted checksum. Add missing files; preserve existing user files and records. New defaults live in a versioned release snapshot. Local graphics stay; selected defaults may contain a newer edition. Uninstall / restore use backups, receipts and logs. .SYSTEMX/.systemx/ = managed release cache. AUTOBOT/Archive.MD indexes references; DATA/ARCHIVE holds payload.
Final scope rule: Select → observe → compare → authorized reconcile → readback → accept → checkpoint. No automatic background process or provider-sync promise.
```

## Review and selected exports

Each selected image is checked for exact filenames, role boundaries, scope isolation, readable text and observation-versus-execution boundaries. Any subsequent targeted correction prompts are recorded below. Upscaling adds canvas pixels, not native source detail.

## Targeted technical corrections

### 01-overview

```text
Make only these technical label corrections to page01/04. Preserve layout, all panels, exact ROOT filenames, ten AUTOBOT names, DATA folders, project tree, other accurate text, arrows, colors, brand and footer.
1. Agent0-to-X blue arrow caption 'assign tasks' → exactly 'record events'.
2. Agent0-to-Y blue arrow caption 'assign tasks' → exactly 'CLI task'.
3. AgentZ second file row currently 'REVIEWS/policies/' with 'Requests + evidence + reports' is misleading. Replace that row path with exactly 'REVIEWS/requests/ + reports/' and keep its 'Requests + evidence + reports' subtitle. Keep the first REVIEWS/POLICY.json row, 10x10 checks and advisory score row.
4. In AgentX bottom note replace 'Host executes schedules.' with exactly 'Execution needs separate host setup.' Keep 'X records events and schedule data.'.
5. MASTER-PLAN subtitle 'Outcomes • milestones • map' → 'Outcomes • milestones • acceptance'.
Do not change other accurate content. X records events, not application execution. Requested3840x2160 landscape.
```

### 02-agent-coordination

```text
Correct only the middle IDE / HARNESS TODO card, the right OPTIONAL BOT TODO card, and one short Step5 description on this page02/04. Preserve layout, all ROOT paths, canonical task status card, all other accurate text, pagebrand, colors, mappings, example, delta, and acceptance strip.
MIDDLE IDE / HARNESS TODO card: retain OBSERVED badge, title, 'Actual app plan or task list', 'Native tool readback • item ID • raw state'. REMOVE the two EVENTS file paths and their file icons; they are wrong inside an external plan card. In their place one pale-blue box saying exactly 'Authorized native plan / TODO snapshot'. Replace its five lower checklist lines with exactly these four: 'Actual plan items + raw status'; 'Native revision or labeled snapshot digest'; 'Capture time + readback evidence'; 'ROOT observes; actual host tools execute'. It is not AgentX's event/schedule file storage.
RIGHT OPTIONAL BOT TODO card: retain OBSERVED badge and top two explanatory lines. Replace only the AGENTS/agent.y/JOBS.json file box with exactly 'Actual run / TODO snapshot'. Retain its existing lower checklist content and optional/not-assessed lines. This card covers any authorized bot channel, not only AgentY.
STEP5: keep 'Agent0 reconciles via authorized tools'; replace its small description 'Update WORK/TASKS.json as needed' with 'Canonical task commands + external tools'. This makes both update surfaces explicit; do not imply bypassing normal canonical task transitions.
Do not invent file paths, tools, events or new checks. Requested3840x2160 landscape.
```

### 03-autobot-panel

```text
Change only the six field labels inside the BOUNDED TOOL CARD panel of this page03/04 to match actual stored tool-card metadata. Preserve the MIRRORS.json heading and 'Retains cards + observations.' line, other panels and every exact ROOT/AUTOBOT filename, 10 specialist cards, hierarchy, arrows, limits, footer, colors, layout. Replace the six existing small field rows with exactly these six, one per line: 'Task IDs + purpose'; 'Provider + tool'; 'Input revision'; 'Permission boundary'; 'Expected evidence'; 'Stop condition'. In particular remove 'selected context' and 'intended tool + arguments' from this field list because they are not serialized tool-card fields. Everything else unchanged. Requested3840x2160 landscape.
One additional precise correction in section5: the YES terminal currently 'Reuse retained result.' must read exactly 'Reuse retained record / result'. A matching pending request may exist without a completed result. Keep the NO branch and all other labels.
```
