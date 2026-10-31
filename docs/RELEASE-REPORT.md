# .SYSTEMX 1.11.0-beta.3 release report

This report records the current source and media qualification for the beta.3
template. The previous beta.2 report remains available at its
[immutable release tag](https://github.com/WayneTechLab/dotSYSTEMX/blob/v1.11.0-beta.2/docs/RELEASE-REPORT.md).
The [GitHub beta.3 release](https://github.com/WayneTechLab/dotSYSTEMX/releases/tag/v1.11.0-beta.3)
holds the published asset checksums and exact source identity. A source release
does not install a downstream project, connect a provider, grant a permission,
certify a device, or deploy an application.

## Version and scope

- Template version: 1.11.0-beta.3. Python package version: 1.11.0b3.
- The distribution manifest covers 269 portable files, including 155 Markdown
  documents. The stock Agenda and Access Matrix records remain unset and
  default-deny; no credential or provider connection is shipped.
- The media set has one current infographic per topic: four system maps, seven
  detailed agent guides, and one final combined atlas. Earlier posters,
  overlapping role cards, and detail sheets are absent from the current tree.
- No video, Blender project, narration, or raw generated master is distributed
  in the source or wheel. The retained white paper is edition 2.1 and explicitly
  examines the beta.1 research baseline.

## Media evidence

| Check | Result |
| --- | --- |
| Current graphic inventory | Exactly 12 SVGs in the portable Infographics directory; 4,810,816 bytes total |
| Atlas | 832,145-byte SVG; eleven embedded thumbnails rendered from and hash-bound to the eleven final full-size panels |
| Source art and export | Each embedded illustration is a compact derivative of a 1672 × 941 imagegen master; SVGs declare 7680 × 4320 and retain selectable vector labels |
| Accessibility and SVG safety | Title and description metadata, adjacent reading-order text guide, no external/active SVG content, checked minimum text contrast 10.43:1 |
| Functional copy | All printed agent CLI examples returned successfully; four maps, seven roles, ten unset Agenda settings, twenty default-deny Access Matrix roles, and Agent1 20 × 20 questions with ten event buckets match source catalogs |
| Media verifier | Exact 12-file inventory, embedded image bytes and dimensions, atlas source hashes and thumbnails, text bounds, video absence, and metadata checks passed |

The [asset record](../.SYSTEMX/MEDIA/Reference/ASSETS.json) contains each
current SVG hash and its embedded art provenance. The
[complete text alternative](../.SYSTEMX/MEDIA/Reference/visual-guide.md)
lists paths, prompts, commands, five-step flows, and authority boundaries.
The [separate 8K PNG export pack](https://github.com/WayneTechLab/dotSYSTEMX/releases/download/v1.11.0-beta.3/dotsystemx-1.11.0-beta.3-current-graphics-8k.zip)
contains exactly twelve 7680 × 4320 exports, a source-bound manifest,
checksums, and the text guide. Its source art does not gain native 8K detail.

## Archive and preservation

The beta.2 state of all twenty-two infographic files and earlier media
references was preserved before fifteen paths were removed and the seven
standard agent paths were refreshed. An owner-held external archive and a
byte-verified Google Drive copy contain those prior bytes. The media ZIP was
13,106,820 bytes with SHA-256
1beef5d3b4a93a7fce2ab08213326e3121a22c09c47b85e6fc8bc9d5e25e2fa9.
Selected beta.3 original art, compact derivatives, and exact prompts were
backed up separately: 21,230,605 bytes, SHA-256
815a3de713d8c42041eb79e2b4590b185b7d759cf5450cb3395d74758472288a.
Both archives were verified against their member manifests. Prior public
source remains readable at the beta.2 tag.

## Source, package, and runtime checks

| Boundary | Evidence |
| --- | --- |
| Source distribution | Release manifest regenerated: 26,664 bytes, SHA-256 47f1cd41d8b46ee669186e1c986c4287591ca24571b8dd753d96353c498aa121. release.py --check validates 269 files and 155 Markdown documents. |
| Python suites | Python 3.14.5: 406 tests, OK, 6 skipped, 472.540 seconds. Python 3.11.15 (resolved interpreter path): 406 tests, OK, 6 skipped, 412.163 seconds. Both terminal reruns used the stable beta.3 distribution manifest after media and documentation edits. |
| Wheel | Clean build: dotsystemx-1.11.0b3-py3-none-any.whl, 4,176,540 bytes, SHA-256 bbc9d09be2c7e5af1db8e576bd8c72486fa39d66de86a5fb95e48c8be0f7955c. The full-wheel gate passed: 269 package files match the current source and manifest byte for byte, expected metadata and entry point are present, and no extra installable member or stale graphic is present. |
| Installed wheel | Fresh isolated Python 3.11 and 3.14 installations reported beta.3; first-run applied to temporary project roots, and selected-template validate and doctor exited zero on both. |
| GitHub Actions | Repository Actions permission readback returned enabled=false. |
| Public pages | README and wiki current embeds point to the twelve beta.3 SVGs; historical media is linked as archived context. Publication and rendered public readback are recorded in the release/wiki receipts. |

The first local wheel attempt reused an ignored build cache and included
nineteen superseded media and companion files. That wheel was rejected.
The cache was removed, the wheel was rebuilt, and an exact wheel-to-manifest
payload comparison passed. A reusable
[wheel verification gate](media/verify_wheel_payload.py) now rejects extra
installable members as well as missing, stale, or altered portable files.
The release asset is built only after that gate passes.

## Remaining product boundaries

The diagrams describe current source behavior. Host-owned CLI or stdio
integration remains explicit; provider labels are discovery records, not
native IDE bindings or active accounts. Agent1 warnings remain advisory,
and a workbook row does not grant OS, GitHub, IDE, or provider access.
The GitHub deployment counter reports observations, not a deployment.
A downstream project still needs its own installation, configuration,
security review, and owner acceptance.
