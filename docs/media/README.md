# White-paper publishing template

Edition 1.2 is the illustrated, branded MLA-style research edition. Editions 1.0
and 1.1 remain immutable in `.SYSTEMX/MEDIA`. Never replace a published edition or
frozen release asset in place. Paper editions and template versions are distinct.

## Build and identity

```bash
python docs/media/build_white_paper.py --edition 1.2
python docs/media/verify_white_paper_example.py --output /tmp/walkthrough.json
```

ReportLab and Pillow are optional publishing dependencies, not template runtime
dependencies. The default source and output are the edition's Markdown and PDF
in `.SYSTEMX/MEDIA`. `--source`, `--output` and `--template` support local drafts.
Use a new edition filename before publishing. The frozen legacy builder remains
available through `--edition 1.0` or `--edition 1.1` for local reproduction only.

[publication-template.json](publication-template.json) controls the product,
author, running author name, company credit, date, edition, baseline, margins,
body typography and four navigation destinations. Keep company attribution
separate from the `.SYSTEMX` product mark. Current publication credit is
**Lucas (SatoshiUNO)**; **a product of Wayne Tech Lab LLC**. The portfolio is
[Networks.Chat](https://Networks.Chat); the business is
[WayneTechLab.com](https://WayneTechLab.com). This publishing identity does not
populate the reusable template's project, agent or task records.

The builder embeds Times New Roman when its four TTF files are available in the
macOS system font folder. `--font-dir` selects a licensed local copy on another
system. Otherwise it uses PDF's standard Times family. Do not redistribute the
font files. The edition metadata records which face was used for the published
PDF; different fonts and dependency versions may change line breaks and hashes.

## Format contract

- US Letter; one-inch text margins; twelve-point Times-family research body;
  double-spaced paragraphs with a half-inch first-line indent.
- Author/page running header. Separate product header, company/edition footer,
  clickable portfolio/business/repository/wiki navigation and return to contents.
- Cover; abstract and keywords; linked contents; list of figures; reading routes;
  numbered research chapters; reference appendices; publication notes; Works Cited.
- MLA-style parenthetical citations mapped to alphabetized Works Cited entries
  with half-inch hanging indents. Use source page numbers only when they exist.
  Full URL labels may wrap in the PDF; the clickable destination stays intact.
- Numbered figure captions with origin and meaning; linked raster cards and
  vector coordination diagrams; readable source descriptions in Markdown.

The branded cover, contents, numbered chapters, navigation footer, color and
compact technical tables/code/captions adapt MLA for a public white paper. This
is not a strict classroom submission format. Follow receiving-institution rules
for a submission. See the [MLA Style Center](https://style.mla.org/works-cited/works-cited-a-quick-guide/).

## Editorial structure and citations

Use `##` for top-level sections and `###` for subheadings. Keep the abstract under
`### Abstract` in the first section. The first section supplies front matter;
subsequent sections become the contents. Code fences preserve source commands;
long display lines wrap without changing the Markdown. Tables repeat headers.
The two supported Mermaid diagrams have explicit vector renderers; unknown
layouts must be implemented and visually checked rather than silently substituted.

Figure lines use `![description](local-file.jpg)` followed by a `*Fig. N. ...*`
caption. The four existing atlas cards use the pinned media source; optimize only
the embedded PDF representation, retaining original artwork and 4K exports.
`<!-- pagebreak -->` starts a deliberate new display page. Keep code, image
captions and explanatory prose together where practical.

Use named anchors such as `<a id="cite-source-title"></a>` before each Works
Cited paragraph and `[Author, "Short Title"](#cite-source-title)` in the body.
Do not mix numeric references with MLA citations. The companion
[white-paper-bibliography.json](white-paper-bibliography.json) records the current
edition's 32 bibliography entries; edit it and the Markdown together. Do not
invent authors, publication dates, page numbers, experiments or endorsements.
Pinned implementation references stay pinned until a later technical re-review.

## Acceptance before publication

Render every page and inspect the cover, contents, figures, dense tables, code,
Works Cited, headers and footers. Check extracted text and exact policy-question
parity; ensure old code samples survive. Validate all internal destinations,
external URI annotations, page/text bounds, metadata, hashes and package limits.
The paper is selectable and linked, but it is not a tagged PDF/UA export; retain
Markdown as the editable text alternative. Do not add PDF JavaScript, automatic
web navigation or tracking. Update the README/wiki discovery and edition metadata.

The executable walkthrough runs in a temporary project and starts no agents or
external jobs. It verifies local records and a tiny HTML contract, not deployment
or a complete 100-answer quality assessment. Keep public-template records blank.

## Audio edition

`python docs/media/narrate_white_paper.py /tmp/reading.txt` remains the **edition
1.1** narration pipeline. Its existing 107-minute synthetic reading is labeled
edition 1.1 in the wiki. It does not narrate the new branded front matter or atlas.
Do not relabel it as an edition 1.2 recording. Audio and transcripts remain outside
the size-limited portable bundle. Any new recording needs its own edition,
transcript, completeness checks and release assets.
