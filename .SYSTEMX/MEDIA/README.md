# .SYSTEMX media library

The public white paper and four standalone use-case cards explain the format.
The cards connect the same project records to different
execution environments. Each card includes a six-step workflow, Agent 0/X/Z
responsibilities, durable records, an example prompt, and the relevant access or
handoff boundary. The brand is **.SYSTEMX**; provider names describe use cases.

## White paper

**Portable project memory for agentic work** - edition 1.0, 4 October 2026.
A 17-page paper for founders, engineering teams and AI tooling practitioners,
covering architecture, Agent 0/X/Z, multi-project coordination, installation,
efficiency measurement, evidence limits and a worked web-app example.

[Read the PDF](SYSTEMX-White-Paper-v1.0.pdf) ·
[Editable Markdown](SYSTEMX-White-Paper-v1.0.md) ·
[Document metadata and checksums](SYSTEMX-White-Paper-v1.0.json) ·
[Wiki overview](https://github.com/WayneTechLab/dotSYSTEMX/wiki/White-Paper)

The paper pins technical claims to v1.8.2-alpha.1 and ships in the documentation
patch v1.8.3-alpha.1. Its worked examples are illustrative; it does not claim
measured savings, AGI, vendor endorsement or production certification. The PDF
has selectable text, vector diagrams, bookmarks and clickable references; the
Markdown is the accessible editable source. Optional PDF build tooling lives
outside the portable runtime in the repository's `docs/media/` directory.

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
