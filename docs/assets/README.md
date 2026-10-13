# .SYSTEMX documentation graphics

The standalone logo remains `.SYSTEMX`; attribution belongs in project information.

| Asset | Purpose | Editable source |
| --- | --- | --- |
| `systemx-full-system.png` | Current 4K Agent 0/X/Y/Z, CLI and tools, explicit `.SYSTEMXP` child scopes, records, and lifecycle map | [Imagegen prompt](systemx-full-system-prompt.md) · [text equivalent](systemx-full-system.md) · [portable 4K JPEG](../../.SYSTEMX/MEDIA/Infographics/systemx-cli-projects-4k.jpg) |
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

The full-system poster is a built-in imagegen raster asset. Its text equivalent
and generation/edit prompts are maintained alongside it. Click the image in the
README or wiki to inspect small path labels at full resolution. The editable
Mermaid diagrams remain available for focused technical views.

The current full-system PNG and portable JPEG are **3840 × 2160** exports.
Imagegen returned a **1672 × 941** native output; macOS `sips` resized the selected
export to 4K. Upscaling adds canvas pixels, not native image detail. The
generation/edit prompt and portable asset metadata retain this provenance.
Current documentation links one selected PNG and the portable JPEG. The four
retained use-case cards and edition 1.2 white paper
describe their older Agent 0/X/Z baseline; current text guides explain Agent Y.
