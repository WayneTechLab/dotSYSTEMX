# Historical white paper edition 1.2 — errata

This page records corrections to **Portable Project Memory for Agentic Work**,
edition 1.2. The published 96-page PDF, editable Markdown, and their recorded
checksums remain unchanged. Read this page alongside that historical PDF or
Markdown source.

Edition 2.0 is the current publication:
[PDF](SYSTEMX-White-Paper-v2.0.pdf) ·
[Editable text](SYSTEMX-White-Paper-v2.0.md) ·
[Metadata](SYSTEMX-White-Paper-v2.0.json).
The older edition is preserved in pinned history:
[edition 1.2 PDF](https://github.com/WayneTechLab/dotSYSTEMX/blob/v1.11.0-alpha.4/.SYSTEMX/MEDIA/White-Paper/SYSTEMX-White-Paper-v1.2.pdf) ·
[Markdown](https://github.com/WayneTechLab/dotSYSTEMX/blob/v1.11.0-alpha.4/.SYSTEMX/MEDIA/White-Paper/SYSTEMX-White-Paper-v1.2.md) ·
[metadata and original checksums](https://github.com/WayneTechLab/dotSYSTEMX/blob/v1.11.0-alpha.4/.SYSTEMX/MEDIA/White-Paper/SYSTEMX-White-Paper-v1.2.json).
The correction below applies to that historical edition, not to edition 2.0.

## E1 — release verification report URL

The Works Cited entry for “V1.8.3-alpha.1 release verification report” on
**PDF page 96** and in the edition's Markdown points to an asset named
`PUBLIC-REVIEW-1.8.2-alpha.1.json` under the `v1.8.3-alpha.1` release. That URL
returns HTTP 404. The report attached to that release is named
`PUBLIC-REVIEW-1.8.3-alpha.1.json`:

- Printed link, retained only to identify the error:
  `https://github.com/WayneTechLab/dotSYSTEMX/releases/download/v1.8.3-alpha.1/PUBLIC-REVIEW-1.8.2-alpha.1.json`
- [Correct v1.8.3-alpha.1 public review report](https://github.com/WayneTechLab/dotSYSTEMX/releases/download/v1.8.3-alpha.1/PUBLIC-REVIEW-1.8.3-alpha.1.json)

The corrected release asset returned HTTP 200 when checked on 11 October 2026.
This correction changes the destination of one citation, not the paper's
technical baseline or its claims. For current format and Agent Y behavior, use
the [version history](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Versions-and-Changelog)
and [Agent Y guide](../../docs/AGENT-Y.md).

## Later optional AUTOBOT / Agent Alpha tier

Edition 1.2 also predates the optional AUTOBOT tier added in 1.10.0-alpha.1.
Read the current [AUTOBOT manual](../../docs/AUTOBOT.md) for Agent Alpha
(`agent.a`), the ten named references, bounded context and reusable requests,
and [DATA](../../docs/DATA.md) for ignored local payload and Git audit behavior.
This is a later format addition, not a claim that the frozen paper tested it.

## Later optional ROOT planning and task-observation layer

Edition 1.2 also predates ROOT. Read the [ROOT manual](../../ROOT/SX-MILESTONE.md)
and [SX-RULES](../../ROOT/SX-RULES.md) for optional request-linked planning,
bounded tool cards, explicit harness/bot task observations, and read-only delta
comparisons. `WORK/TASKS.json` remains the canonical task-state and acceptance
ledger; recorded external completion does not accept a task or execute a tool.
This supplement identifies later features without changing the frozen PDF,
editable Markdown, or their checksums.

The [four-part system field guide](../Reference/systemx-field-guide.md), media
edition `1.11.0-alpha.3` for feature baseline `1.11.0-alpha.2`, brings ROOT,
Agent 0/X/Y/Z, Agent Alpha, AUTOBOT, DATA, and `.SYSTEMXP` together. Its text
explains the canonical/harness/optional-bot observation delta and reconciliation
through authorized real tools. That later media edition does not change the
paper's examined baseline or claim that the paper evaluated those additions.
