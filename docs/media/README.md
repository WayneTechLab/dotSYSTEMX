# Published reference library

The beta.4 source distribution retains twelve current infographic SVGs from
the beta.3 visual edition: four system maps, seven detailed agent guides, and
one atlas built from the final individual guides. Each topic has one current file in
[the media library](../../.SYSTEMX/MEDIA/README.md). Use the
[complete text alternative](../../.SYSTEMX/MEDIA/Reference/visual-guide.md)
for the reading order, exact commands, paths, flow, and role boundaries.

## Current graphics

| System map | SVG |
| --- | --- |
| Architecture and selected scopes | [Open map 1](../../.SYSTEMX/MEDIA/Infographics/systemx-map-architecture.svg) |
| Canonical task and evidence cycle | [Open map 2](../../.SYSTEMX/MEDIA/Infographics/systemx-map-task-cycle.svg) |
| Agenda, Access Matrix, BOT/DOT, and Agent1 | [Open map 3](../../.SYSTEMX/MEDIA/Infographics/systemx-map-governance.svg) |
| First run, direct I/O, DATA, and release boundary | [Open map 4](../../.SYSTEMX/MEDIA/Infographics/systemx-map-onboarding.svg) |

| Agent | One detailed SVG |
| --- | --- |
| Agent 0 | [Coordinator and roster](../../.SYSTEMX/MEDIA/Infographics/systemx-agent-0.svg) |
| Agent X | [Events and time](../../.SYSTEMX/MEDIA/Infographics/systemx-agent-x.svg) |
| Agent Y | [Selected CLI](../../.SYSTEMX/MEDIA/Infographics/systemx-agent-y.svg) |
| Agent Z | [Evidence review](../../.SYSTEMX/MEDIA/Infographics/systemx-agent-z.svg) |
| Agent Alpha | [AUTOBOT and Agenda](../../.SYSTEMX/MEDIA/Infographics/systemx-agent-alpha.svg) |
| Agent Beta | [Named BOT/DOT records](../../.SYSTEMX/MEDIA/Infographics/systemx-agent-beta.svg) |
| Agent1 | [Security and access advice](../../.SYSTEMX/MEDIA/Infographics/systemx-agent-1.svg) |

[Combined atlas](../../.SYSTEMX/MEDIA/Infographics/systemx-atlas.svg) ·
[Asset manifest and art provenance](../../.SYSTEMX/MEDIA/Reference/ASSETS.json).
The [beta.3 8K PNG export pack](https://github.com/WayneTechLab/dotSYSTEMX/releases/download/v1.11.0-beta.3/dotsystemx-1.11.0-beta.3-current-graphics-8k.zip) is a separate release asset containing the twelve current exports, manifest, checksums, and accessible guide; it is not another source copy.
The SVGs declare a 7680 × 4320 canvas and overlay exact vector labels on
imagegen-generated illustration. The illustration's native source size is
recorded separately; an 8K export canvas does not create native 8K raster
artwork. The atlas is an overview; open the individual guides for small text.

The [current builder](build_current_visuals.py) uses reviewed external art
sources and adds deterministic labels, diagrams, and accessibility metadata.
The [visual verifier](verify_current_visuals.py) checks exact current inventory,
SVG structure, embedded-source integrity, and legibility. Its media baseline
may precede the template version when unchanged artwork is carried into a later
release; the beta.3 asset record remains the provenance for this beta.4 paper
release. Raw generated art and Blender files stay in the owner archive outside
the public template. The public repository carries one final SVG per current
topic and no video files.

Before shipping a Python wheel, remove stale generated `build/` and
`*.egg-info/` directories, then build from the reviewed source. Set the wheel
output outside the checkout and run the [wheel payload verifier](verify_wheel_payload.py):

```bash
python3 -I -B docs/media/verify_wheel_payload.py /path/to/dotsystemx-<version>-py3-none-any.whl
```

The checker compares every `systemx/` wheel file, including the embedded
distribution manifest, byte for byte with `.SYSTEMX/` and checks manifest
digests. It also rejects unexpected wheel members and checks the package
metadata, entry point, license, and complete wheel `RECORD`. It fails if stale
build output added an old image or document, if a file is missing, or if
content differs. It requires only Python's standard library and does not
change the source tree.

## Current technical paper

[Portable Project Coordination for AI-Assisted Work, edition 2.2](../../.SYSTEMX/MEDIA/White-Paper/SYSTEMX-White-Paper.pdf)
examines the `1.11.0-beta.4` source and package baseline. It includes a
[Markdown text alternative](../../.SYSTEMX/MEDIA/White-Paper/SYSTEMX-White-Paper.md)
and [provenance](../../.SYSTEMX/MEDIA/White-Paper/SYSTEMX-White-Paper.json).
The PDF has selectable text but is not tagged PDF/UA.
[Edition 2.1](https://github.com/WayneTechLab/dotSYSTEMX/blob/v1.11.0-beta.1/.SYSTEMX/MEDIA/White-Paper/SYSTEMX-White-Paper.pdf)
examined beta.1; edition 2.0 remains in
[immutable alpha.5 history](https://github.com/WayneTechLab/dotSYSTEMX/releases/tag/v1.11.0-alpha.5).

## Previous visual editions and hosted films

The four original JPEG maps, beta.1 feature graphics, role cards, and
superseded detailed sheets remain in
[immutable beta.2 source history](https://github.com/WayneTechLab/dotSYSTEMX/tree/v1.11.0-beta.2/.SYSTEMX/MEDIA/Infographics)
and the separately verified owner archive. Current README and wiki embeds use
the beta.3 set; historical links preserve earlier claims without showing old
artwork as current. For hosted video history, use the
[wiki manual](https://github.com/WayneTechLab/dotSYSTEMX/wiki). Video files,
Blender projects, narration, renders, and captions are not stored in this
source distribution.
