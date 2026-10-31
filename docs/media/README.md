# Published reference library

The reusable template contains the current white paper, static system diagrams,
accessible text companions, and their reference provenance. Film production,
narration, captions, editable scenes, render output, and publication workspaces
are maintained separately from this source distribution.

## Current white paper, edition 2.1

*.SYSTEMX: Portable Project Coordination for AI-Assisted Work* examines the
`1.11.0-beta.1` record model, agent roles, Access Matrix, security boundaries,
release accounting, external authoring-data boundary, and evaluation limits.
The current five-page PDF has selectable text and navigation.

[Clickable PDF](../../.SYSTEMX/MEDIA/White-Paper/SYSTEMX-White-Paper.pdf) ·
[Readable manuscript](../../.SYSTEMX/MEDIA/White-Paper/SYSTEMX-White-Paper.md) ·
[Edition provenance](../../.SYSTEMX/MEDIA/White-Paper/SYSTEMX-White-Paper.json) ·
[White-paper manual](https://github.com/WayneTechLab/dotSYSTEMX/wiki/White-Paper)

Earlier edition 2.0 examined `1.11.0-alpha.4` and was published with
`1.11.0-alpha.5`. Its original PDF, figures, manuscript, and provenance remain
available from that [immutable release](https://github.com/WayneTechLab/dotSYSTEMX/releases/tag/v1.11.0-alpha.5).
Optional publishing and narration tools are not dependencies of the template runtime.

## Static guides

[Current beta visual guide and accessible text](../../.SYSTEMX/MEDIA/Reference/current-visual-guide.md) ·
[Detailed agent sheets and text transcript](../../.SYSTEMX/MEDIA/Reference/agent-detail-guide.md) ·
[Lifecycle infographic](../../.SYSTEMX/MEDIA/Infographics/systemx-guide-lifecycle.svg) ·
[BOT/DOT workspaces](../../.SYSTEMX/MEDIA/Infographics/systemx-guide-bot-workspaces.svg) ·
[Security and access](../../.SYSTEMX/MEDIA/Infographics/systemx-guide-security-access.svg) ·
[Access Matrix](../../.SYSTEMX/MEDIA/Infographics/systemx-guide-access-matrix.svg)

The current set has four beta feature infographics, seven agent role cards,
and seven detailed agent sheets on 7680 × 4320 SVG canvases, with exact vector
labels and reading-order text companions. The detailed sheets show the folder,
example prompt, CLI subcommand map, process flow, and boundary for every role.
Imagegen illustrations have 1672 × 941 or 1536 × 1024 native pixels; the 8K
canvas is an export size. These graphics explain source behavior and boundaries,
not live provider, device, or deployment status.

The [first-set builder](build_current_visuals.py) and
[detailed-sheet builder](build_detail_visuals.py) reconstruct the stock SVGs
from reviewed external inputs. The [visual verifier](verify_current_visuals.py)
checks current asset hashes, SVG structure and contrast, and optional external
8K raster export hashes. Raw generated art and raster exports remain outside
the portable template; the SVGs are the current main-branch copies.

### Historical field guide

[Four-part field guide and accessible text](../../.SYSTEMX/MEDIA/Reference/systemx-field-guide.md) ·
[Portable reference library](../../.SYSTEMX/MEDIA/README.md) ·
[Documentation images](../assets/README.md) ·
[Visual manual](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Visual-Guide)

The four overview/detail posters explain canonical records, agent roles, ROOT,
AUTOBOT references, DATA, tools, and named `.SYSTEMXP` scopes. Their images and
stated baseline remain separate from a project's selected defaults version.
Images explain responsibilities; they do not launch workers or grant access.

For current hosted video guidance, use the public manual's YouTube links. Video
files and production metadata are not distributed with new template source.
