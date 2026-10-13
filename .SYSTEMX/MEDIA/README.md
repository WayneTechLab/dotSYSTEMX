# .SYSTEMX media library

Current full-system map, latest public paper, and one retained 4K image per workflow.
**.SYSTEMX** is a product of
**Wayne Tech Lab LLC**, created by **Lucas (SatoshiUNO)**.

[Portfolio: Networks.Chat](https://Networks.Chat) ·
[Business: WayneTechLab.com](https://WayneTechLab.com) ·
[User manual](https://github.com/WayneTechLab/dotSYSTEMX/wiki)

## White paper

**Portable Project Memory for Agentic Work** - edition 1.2, 96 pages.
The reference for its examined Agent 0/X/Z baseline includes 29 chapters, all
100 Agent Z questions, record contracts, six figures and clickable research citations.

[Read the PDF](White-Paper/SYSTEMX-White-Paper-v1.2.pdf) ·
[Editable text](White-Paper/SYSTEMX-White-Paper-v1.2.md) ·
[Metadata and checksums](White-Paper/SYSTEMX-White-Paper-v1.2.json) ·
[Edition 1.2 citation erratum](White-Paper/ERRATA.md) ·
[Wiki guide](https://github.com/WayneTechLab/dotSYSTEMX/wiki/White-Paper)

The published PDF and Markdown are unchanged. The erratum corrects one broken
release-report URL in their Works Cited without altering either frozen file.
Their other pinned references and historical inventory
continue to describe its examined baseline. The Markdown image paths follow this
folder layout. The PDF is selectable and linked; it is not tagged PDF/UA.
Its installation-state discussion reflects that older baseline: from
1.8.8-alpha.1, a pinned project may opt into check-only startup release notices
without automatic selection. Use the current [format](../FORMAT.md) and
[installation guide](../docs/INSTALLATION.md) for the active contract. The paper
also predates the optional Agent Y CLI/PR lane introduced in 1.9.0-alpha.2;
read the current [Agent Y guide](../docs/AGENT-Y.md) for that role. The frozen
edition is not retroactively updated to claim it evaluated the new runtime.

## 4K workflow infographics

| Workflow | 3840 × 2160 image | Text guide |
| --- | --- | --- |
| Full-system map: Agent 0 / X / Y / Z | [4K JPEG](Infographics/systemx-cli-projects-4k.jpg) | [Current guide](Reference/cli-projects.md) |
| ChatGPT + Google Drive | [4K JPEG](Infographics/chatgpt-google-drive-4k.jpg) | [Guide](Reference/chatgpt-google-drive.md) |
| Codex + GitHub / main project | [4K JPEG](Infographics/codex-github-main-4k.jpg) | [Guide](Reference/codex-github-main.md) |
| Dots / Codex Cloud | [4K JPEG](Infographics/dots-codex-cloud-4k.jpg) | [Guide](Reference/dots-codex-cloud.md) |
| Codex / Copilot CLI + local drive | [4K JPEG](Infographics/codex-copilot-cli-local-4k.jpg) | [Guide](Reference/codex-copilot-cli-local.md) |

The full-system map includes the optional Agent Y CLI/branch/PR lane and its
separate acceptance gates. The four use-case cards are retained Agent 0/X/Z
baseline artwork, preserved byte for byte; their text guides describe the
current Agent Y option. Read the [Agent Y manual](../docs/AGENT-Y.md) for
provider identity, project checks, cancellation, merge, and cleanup details.
The map and cards were created with imagegen; 4K describes their export canvas.
Upscaling adds canvas pixels, not native image detail.
[Asset metadata](Reference/ASSETS.json) records dimensions, raw-byte SHA-256 hashes
and archived source locations. [Generation prompts](Reference/IMAGE-PROMPTS.md)
retain the original production instructions. Provider names describe use cases
and do not imply endorsement.

## Folder layout

```text
MEDIA/
  README.md       Media index
  White-Paper/    Latest PDF, editable text, metadata and a separate erratum
  Infographics/  Full-system map and four use-case 4K JPEG outputs
  Reference/     Workflow guides, image prompts and asset provenance
```

Only the latest paper and selected 4K outputs ship in the current template.
Older papers, native PNGs and prior audio remain available through
[Versions and changelog](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Versions-and-Changelog)
and the immutable release history.

Fresh installs use this layout. **Managed updates remain additive:** they add
missing files and select the new release snapshot, without removing, moving or
replacing existing local media or user directories. An existing project may keep
old media paths alongside the new folders. Keep custom assets under distinct
names and retain your own backups before any manual cleanup.

Media explains the format; it is not canonical project state. Read relevant guides
on demand. Use [START-HERE](../START-HERE.md) for normal context loading;
`WORK/TASKS.json`, plans, events, reviews and checkpoints remain in their standard
locations. This organization adds no running service, scheduler or agent.
