# .SYSTEMX documentation graphics

The standalone logo remains `.SYSTEMX`; attribution belongs in project information.

| Asset | Purpose | Editable source |
| --- | --- | --- |
| `systemx-full-system.png` / `systemx-full-system-4k.png` | Complete Agent 0/X/Z, record, toolchain, project and lifecycle map | [Imagegen prompt](systemx-full-system-prompt.md) · [text equivalent](systemx-full-system.md) |
| `systemx-logo.png` | Current brand logo | Imagegen provenance in [IMAGE-PROMPTS.md](IMAGE-PROMPTS.md) |
| `systemx-coordination.png` / `.svg` | Global/Master Plan, Agent 0/X/Z, acceptance and checkpoint | [Mermaid](systemx-coordination.mmd) |
| `systemx-project-waves.png` / `.svg` | Research through accepted delivery | [Mermaid](systemx-project-waves.mmd) |
| `systemx-shared-workspace.png` / `.svg` | Readers/workers, canonical writer, transport, verified snapshot | [Mermaid](systemx-shared-workspace.mmd) |
| `systemx-workflow.png` | Legacy six-step artwork retained for existing URLs | Historical imagegen prompt |

The three focused coordination, project-wave, and shared-workspace diagrams are
rendered from Mermaid 11 source into SVG and PNG with
a white background, readable text labels, and distinct role/data/decision colors.
Documentation includes alt text and prose equivalents; meaning does not depend
on color. Mermaid is an optional documentation renderer, not a template runtime
dependency. Use a compatible Mermaid renderer, preserve the labels/relationships,
and review SVG/PNG output when changing the sources. The portable guides embed
readable Mermaid source so their meaning remains available without image downloads.

Keep `.SYSTEMX` and `.SYSTEMXP` exact casing. The diagrams describe responsibilities,
not automatic workers, model training, a cloud sync service, or a scheduler.

The full-system poster is a built-in imagegen raster asset. Its text equivalent
and generation/edit prompts are maintained alongside it. Click the image in the
README or wiki to inspect small path labels at full resolution. The editable
Mermaid diagrams remain available for focused technical views.

The full-system native master is **1672 × 941**. The separately named **3840 ×
2160** PNG is a local upscale made with macOS `sips`, with user approval. It adds
canvas pixels, not native image detail. The original remains available.
