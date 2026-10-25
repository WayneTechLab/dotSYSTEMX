# .SYSTEMX documentation graphics

The standalone logo remains `.SYSTEMX`; attribution belongs in project information.

| Asset | Purpose | Editable source |
| --- | --- | --- |
| [Introduction poster — 4K](systemx-intro-poster-4k.jpg) | Custom thumbnail and linked preview for the [public YouTube introduction](https://www.youtube.com/watch?v=-EM-T6uNQAs); 3840 × 2160 JPEG | [Film guide and asset provenance](../media/introduction/README.md) |
| [Field guide 1 — overview](../../.SYSTEMX/MEDIA/Infographics/systemx-field-guide-01-overview-4k.jpg) | Whole-system view: ROOT, SX-RULES, SX-MILESTONE, Agent 0/X/Y/Z, AGENTA, ten AUTOBOTs, DATA, tools, and `.SYSTEMXP` | [Accessible companion](../../.SYSTEMX/MEDIA/Reference/systemx-field-guide.md#page-1--whole-system-overview) |
| [Field guide 2 — coordination](../../.SYSTEMX/MEDIA/Infographics/systemx-field-guide-02-agent-coordination-4k.jpg) | Canonical, harness, and optional bot TODO observations; read-only delta, authorized reconciliation, readback, and acceptance | [Accessible companion](../../.SYSTEMX/MEDIA/Reference/systemx-field-guide.md#page-2--agent-coordination-and-tools) |
| [Field guide 3 — ROOT/AUTOBOT](../../.SYSTEMX/MEDIA/Infographics/systemx-field-guide-03-autobot-panel-4k.jpg) | ROOT planning, requests, tool cards, Agent Alpha, ten named reference functions, and result reuse | [Accessible companion](../../.SYSTEMX/MEDIA/Reference/systemx-field-guide.md#page-3--agent-alpha-and-the-ten-autobots) |
| [Field guide 4 — DATA/projects](../../.SYSTEMX/MEDIA/Infographics/systemx-field-guide-04-data-projects-4k.jpg) | Independent child ROOT/task records, local payload storage, Git exclusions, shared outer tools, and reversible updates | [Accessible companion](../../.SYSTEMX/MEDIA/Reference/systemx-field-guide.md#page-4--local-data-and-project-scopes) |
| `systemx-logo.png` | Current brand logo | Imagegen provenance in [IMAGE-PROMPTS.md](IMAGE-PROMPTS.md) |
| `systemx-coordination.png` / `.svg` | Global/Master Plan, Agent 0/X/Y/Z, acceptance and checkpoint | [Mermaid](systemx-coordination.mmd) |
| `systemx-project-waves.png` / `.svg` | Research through accepted delivery | [Mermaid](systemx-project-waves.mmd) |
| `systemx-shared-workspace.png` / `.svg` | Readers/workers, canonical writer, transport, verified snapshot | [Mermaid](systemx-shared-workspace.mmd) |
| `systemx-workflow.png` | Legacy six-step artwork retained for existing URLs | Historical imagegen prompt |

The three focused coordination, project-wave, and shared-workspace diagrams were
rendered on 2026-10-12 with `@mermaid-js/mermaid-cli` **11.12.0** into SVG and PNG with
a white background, readable text labels, and distinct role/data/decision colors.
Documentation includes alt text and prose equivalents; meaning does not depend
on color. Mermaid is an optional documentation renderer, not a template runtime
dependency. Use a compatible Mermaid renderer, preserve the labels/relationships,
and review SVG/PNG output when changing the sources. The portable guides embed
readable Mermaid source so their meaning remains available without image downloads.

Current focused PNG dimensions are 1358 × 3048 (coordination), 1968 × 1268
(project waves), and 1676 × 2044 (shared workspace). Each was exported at scale
2 with a white background and visually checked against its source. Rendering
used a temporary tool invocation outside the repository; no renderer dependency
is installed by `.SYSTEMX` setup.

Keep `.SYSTEMX` and `.SYSTEMXP` exact casing. The diagrams describe responsibilities,
not automatic workers, model training, a cloud sync service, or a scheduler.
The [CLI and tools guide](../../.SYSTEMX/docs/CLI-TOOLS.md) supplies executable
examples for the poster's external CLI, managed/local launcher, Python API,
provider, and child-project lanes. Child `.SYSTEMXP` records share one outer
default version; select each scoped command explicitly by registered project name.

The current [four-part field guide](../../.SYSTEMX/MEDIA/Reference/systemx-field-guide.md)
uses built-in imagegen raster artwork and a complete accessible text companion.
Its feature baseline is **1.11.0-alpha.2**, and the ROOT-inclusive media edition
is **1.11.0-alpha.3**. `WORK/TASKS.json` remains the sole task-state authority;
ROOT records explicit mappings and observed harness/bot snapshots. Agent 0 uses
actual authorized tools to reconcile differences and records a fresh readback.
The drawings do not imply a live connector, equal TODO counts, or automatic
acceptance of an external `completed` state. Click an image in the README or
wiki to inspect it at full resolution. The focused Mermaid diagrams above retain their stated earlier
rendering baseline; they are supplementary views, not the complete AUTOBOT inventory.

Each selected page is a **3840 × 2160 JPEG**. The
[generation/correction prompts](../../.SYSTEMX/MEDIA/Reference/systemx-field-guide-prompts.md)
and [per-page metadata](../../.SYSTEMX/MEDIA/Reference/ASSETS.json) record native
dimensions, exact-byte hashes, and export methods. Upscaling adds canvas pixels,
not native image detail. Only the selected four-page exports ship for this series.

The prior one-page map remains available as a
[historical PNG](https://github.com/WayneTechLab/dotSYSTEMX/blob/v1.10.0-alpha.2/docs/assets/systemx-full-system.png)
and [historical JPEG](https://github.com/WayneTechLab/dotSYSTEMX/blob/v1.10.0-alpha.2/.SYSTEMX/MEDIA/Infographics/systemx-cli-projects-4k.jpg).
Its [old prompt record](systemx-full-system-prompt.md) retains the production copy;
the [map index](systemx-full-system.md) links current and historical explanations.
The four retained use-case cards and edition 1.2 white paper also describe their
stated earlier Agent 0/X/Z baseline; current manuals and the new field guide
cover Agent Y, ROOT, and AUTOBOT.
