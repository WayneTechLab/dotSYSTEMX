# Image generation record

These documentation assets were created with the built-in imagegen tool and
reviewed for the exact `.SYSTEMX` spelling, legible labels, and workflow order.
The final pass edited the initial drafts to make `.SYSTEMX` the only visual
brand. Maintainer attribution belongs separately in README/wiki text.
Only the selected final PNGs are included here; the drafts are not distributed.

- `systemx-logo.png`: standalone monochrome folder/branch mark and wordmark.
- `systemx-workflow.png`: legacy six-step illustration, retained for existing links.
  Current documentation uses the full-system poster and Agent 0/X/Z diagrams
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

## Full-system infographic

`systemx-full-system.png` is the current comprehensive raster overview, generated
with the built-in imagegen tool. The exact initial and correction prompts are in
[systemx-full-system-prompt.md](systemx-full-system-prompt.md), and the accessible
[text equivalent](systemx-full-system.md) explains every section and boundary.
It uses the standard Agent 0, Agent X, and Agent Z roles; no Agent Y is introduced.

The native master is 1672 × 941 pixels. `systemx-full-system-4k.png` is the
3840 × 2160 upscaled export requested by the user; it was resized locally with
`sips` after imagegen creation and correction. Both files are retained, and the
4K export is not represented as native 4K generation.
