# .SYSTEMX documentation graphics

The standalone logo remains `.SYSTEMX`; attribution belongs in project information.

| Asset | Purpose | Editable source |
| --- | --- | --- |
| `systemx-logo.png` | Current brand logo | Imagegen provenance in [IMAGE-PROMPTS.md](IMAGE-PROMPTS.md) |
| `systemx-coordination.png` / `.svg` | Global/Master Plan, Agent 0/X/Z, acceptance and checkpoint | [Mermaid](systemx-coordination.mmd) |
| `systemx-project-waves.png` / `.svg` | Research through accepted delivery | [Mermaid](systemx-project-waves.mmd) |
| `systemx-shared-workspace.png` / `.svg` | Readers/workers, canonical writer, transport, verified snapshot | [Mermaid](systemx-shared-workspace.mmd) |
| `systemx-workflow.png` | Legacy six-step artwork retained for existing URLs | Historical imagegen prompt |

The current diagrams are rendered from Mermaid 11 source into SVG and PNG with
a white background, readable text labels, and distinct role/data/decision colors.
Documentation includes alt text and prose equivalents; meaning does not depend
on color. Mermaid is an optional documentation renderer, not a template runtime
dependency. Use a compatible Mermaid renderer, preserve the labels/relationships,
and review SVG/PNG output when changing the sources. The portable guides embed
readable Mermaid source so their meaning remains available without image downloads.

Keep `.SYSTEMX` and `.SYSTEMXP` exact casing. The diagrams describe responsibilities,
not automatic workers, model training, a cloud sync service, or a scheduler.
