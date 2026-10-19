# Image generation record

These documentation assets were created with the built-in imagegen tool and
reviewed for the exact `.SYSTEMX` spelling, legible labels, and workflow order.
The final pass edited the initial drafts to make `.SYSTEMX` the only visual
brand. Maintainer attribution belongs separately in README/wiki text.
Only the selected final PNGs are included here; the drafts are not distributed.

- `systemx-logo.png`: standalone monochrome folder/branch mark and wordmark.
- `systemx-workflow.png`: legacy six-step illustration, retained for existing links.
  Current documentation uses the four-part field guide and focused diagrams
  listed in [asset notes](README.md).

Both files have an opaque white background. They are raster assets, not editable
vector masters. The workflow is an illustration of a human/agent-maintained
process; it does not imply automatic orchestration by the folder.

## Final logo edit prompt

```text
Use case: text-localization
Edit target: the supplied .SYSTEMX logo.
Change only the branding lockup: remove the smaller text "Wayne Tech Lab" completely. The brand must stand alone as ".SYSTEMX" with the existing folder/branch icon. Rebalance the vertical whitespace so the one-line logo feels centered and intentional, retaining generous clean padding.
Preserve the exact .SYSTEMX wordmark, visible leading dot, uppercase lettering, folder/branch symbol, neutral monochrome treatment, and solid white background. No replacement subtitle, attribution, slogan, extra brand, or new design element. Keep the rest of the design unchanged.
```

## Final infographic edit prompt

```text
Use case: text-localization
Edit target: the supplied .SYSTEMX workflow infographic.
Remove only the small "Wayne Tech Lab" attribution at the lower-right corner and replace that area with the matching clean white background. Do not add any replacement attribution.
Preserve every other element exactly: .SYSTEMX title including the leading dot, subtitle, all six step labels and descriptions, numbers, icons, the directed cycle arrows, the footer sentence "Your AI tools run the work. .SYSTEMX keeps the records.", the layout, neutral monochrome colors, and solid white background. No other changes.
```

The current Mermaid `.mmd`, SVG, and PNG diagrams are technical renderings, not
imagegen edits. Their source and maintenance notes are in [README.md](README.md).

## Current four-part field guide

The [four-page field guide](../../.SYSTEMX/MEDIA/Reference/systemx-field-guide.md)
replaces the previous one-page raster overview. It shows Agent 0/X/Y/Z,
AGENTA / Agent Alpha, all ten AUTOBOT reference functions, ROOT,
SX-RULES, SX-MILESTONE, canonical/harness/optional bot TODO reconciliation,
local DATA, tools, and `.SYSTEMXP` project scopes. The feature baseline is
1.11.0-alpha.2; the ROOT-inclusive media edition is 1.11.0-alpha.3.

Its [generation and correction prompts](../../.SYSTEMX/MEDIA/Reference/systemx-field-guide-prompts.md)
describe the approved copy, relationships, and final corrections. The
[asset record](../../.SYSTEMX/MEDIA/Reference/ASSETS.json) supplies native/output
dimensions, export methods, and exact-byte hashes for each selected 4K JPEG.
Upscaling a canvas does not add native detail. The accessible companion
explains every page and takes precedence over an ambiguous drawn connector.

## Historical one-page infographic

The previous [4K PNG](https://github.com/WayneTechLab/dotSYSTEMX/blob/v1.10.0-alpha.2/docs/assets/systemx-full-system.png)
and [portable 4K JPEG](https://github.com/WayneTechLab/dotSYSTEMX/blob/v1.10.0-alpha.2/.SYSTEMX/MEDIA/Infographics/systemx-cli-projects-4k.jpg)
remain in tagged history. They cover the earlier Agent 0/X/Y/Z, CLI, and
`.SYSTEMXP` baseline and predate Agent Alpha/AUTOBOT.
[Historical edit prompts](systemx-full-system-prompt.md) retain their original
production copy and export details; [this index](systemx-full-system.md)
routes readers to the current series and archived text equivalent.
Historical use-case card prompts are retained unchanged in the
[portable media library](../../.SYSTEMX/MEDIA/Reference/IMAGE-PROMPTS.md).
