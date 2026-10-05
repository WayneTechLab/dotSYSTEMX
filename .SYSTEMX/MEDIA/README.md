# .SYSTEMX media library

The public white paper and four standalone use-case cards explain the format.
The cards connect the same project records to different
execution environments. Each card includes a six-step workflow, Agent 0/X/Z
responsibilities, durable records, an example prompt, and the relevant access or
handoff boundary. The brand is **.SYSTEMX**; provider names describe use cases.

## White paper

**Portable Project Memory for Agentic Work** - illustrated research edition 1.2,
4 October 2026. A 96-page reference with the complete 29-chapter implementation
paper, exact record contracts, all 100 Agent Z questions, command families,
baseline file inventory, tested local walkthrough and a new four-card visual atlas.

**Lucas (SatoshiUNO)** · **A product of Wayne Tech Lab LLC**
[Portfolio: Networks.Chat](https://Networks.Chat) ·
[Business: WayneTechLab.com](https://WayneTechLab.com)

[Illustrated PDF](SYSTEMX-White-Paper-v1.2.pdf) ·
[Editable Markdown](SYSTEMX-White-Paper-v1.2.md) ·
[Metadata and checksums](SYSTEMX-White-Paper-v1.2.json) ·
[Wiki](https://github.com/WayneTechLab/dotSYSTEMX/wiki/White-Paper) ·
[Publication format](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Research-Paper-Format)

The paper uses an MLA-style research body and 32 alphabetized Works Cited entries,
with branded front matter and compact technical displays. It includes six numbered
figures, selectable text, linked contents/figure list, bookmarks, linked citations,
and portfolio/business/repository/wiki navigation. It is not a tagged PDF/UA export;
Markdown remains the editable text alternative. It examines v1.8.3-alpha.1 and
ships in the v1.8.5-alpha.1 documentation patch. No measured savings, AGI or
production certification is asserted. Original artwork remains unchanged.

Earlier editions remain immutable: [edition 1.0 PDF](SYSTEMX-White-Paper-v1.0.pdf)
and [source](SYSTEMX-White-Paper-v1.0.md), the 17-page introduction;
[edition 1.1 PDF](SYSTEMX-White-Paper-v1.1.pdf) and
[source](SYSTEMX-White-Paper-v1.1.md), the 50-page expanded reference.
The wiki retains the separately labeled **edition 1.1** synthetic audio and transcript.
Audio is excluded from the portable bundle. Optional publication tools and the
reusable format configuration are in `docs/media/` in the repository.

## Choose a workflow

| Card | Read the guide | Original | 4K download |
| --- | --- | --- | --- |
| 01. ChatGPT + Google Drive | [Text guide](chatgpt-google-drive.md) | [Native PNG](chatgpt-google-drive.png) | [3840 × 2160 JPEG](chatgpt-google-drive-4k.jpg) |
| 02. Codex + GitHub / main project | [Text guide](codex-github-main.md) | [Native PNG](codex-github-main.png) | [3840 × 2160 JPEG](codex-github-main-4k.jpg) |
| 03. Dots / Codex Cloud | [Text guide](dots-codex-cloud.md) | [Native PNG](dots-codex-cloud.png) | [3840 × 2160 JPEG](dots-codex-cloud-4k.jpg) |
| 04. Codex / Copilot CLI + local drive | [Text guide](codex-copilot-cli-local.md) | [Native PNG](codex-copilot-cli-local.png) | [3840 × 2160 JPEG](codex-copilot-cli-local-4k.jpg) |

## Image quality and provenance

The images were created with the built-in **imagegen** tool. The unmodified PNG
masters are retained. The separate 4K JPEG files are resized exports, not native
4K generations; enlarging the canvas does not add source detail. JPEG exports
keep every media file within the existing 2 MiB installer limit. See
[asset metadata](ASSETS.json) for dimensions, sizes, export settings and raw-byte
SHA-256 checksums, and the [exact prompt set](IMAGE-PROMPTS.md) for reproducibility.
The existing schema-1 distribution manifest uses LF-normalized fingerprints;
ASSETS.json additionally records ordinary raw-byte hashes for media verification.

## Using this folder

`MEDIA/` holds educational and presentation assets, not canonical task state.
Read the relevant text guide when needed; do not load all images into every LLM
turn. Task status remains in `WORK/TASKS.json`; context, plans, events, reviews and
checkpoints stay in their standard locations. Use [START-HERE](../START-HERE.md)
for the normal load order and [shared workspaces](../docs/SHARED-WORKSPACES.md)
for writer ownership, stale snapshots, cloud handoffs and multi-chat coordination.

The template includes these assets in its folder archive and Python wheel.
Managed updates add missing files and retain existing user files. Existing
customized copies are preserved; selected release snapshots contain that
release's originals. Future artwork revisions should use new filenames so an
additive update never needs to replace local media. A version pin stays in force.
This folder adds no running service, cloud integration, scheduler or agent.

For your own assets, use distinct filenames and keep confidential material out
of public Git. Provider names and recognizable symbols belong to their owners;
the cards are independent explanatory materials, not an endorsement.
