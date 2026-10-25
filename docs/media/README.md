# White-paper publishing tools

Edition **2.0**, *Portable Project Coordination for AI-Assisted Work*, is the
current publication. It explains the operating model before the implementation,
using four original figures, a reproducible local example, and clearly separated
implementation evidence and proposed evaluation. Its examined software baseline
is `1.11.0-alpha.4`, commit
`e086ba15a1e70c6b585b8f12a703defc5c984b2c`; its publication release is
`1.11.0-alpha.5`. Paper editions, template versions, and infographic editions are
separate identifiers.

[Current PDF](../../.SYSTEMX/MEDIA/White-Paper/SYSTEMX-White-Paper-v2.0.pdf) ·
[Editable manuscript](../../.SYSTEMX/MEDIA/White-Paper/SYSTEMX-White-Paper-v2.0.md) ·
[Edition metadata](../../.SYSTEMX/MEDIA/White-Paper/SYSTEMX-White-Paper-v2.0.json) ·
[Figure sources](../../.SYSTEMX/MEDIA/White-Paper/figures/)

Only the latest paper is distributed in `.SYSTEMX/MEDIA/White-Paper`. Published
editions remain immutable in tagged history. Never rebuild over a published PDF:
timestamps, document IDs, font selection, and dependency versions can change its
bytes even when the visible layout looks identical.

## Introduction film and poster

The [introduction film guide](introduction/README.md) provides the approximately
1 minute 50 second Blender overview, a 4K poster, the transcript, captions, and
asset checksums. The film has its own `media-intro-v1.0` publication identity;
its feature baseline is `1.11.0-alpha.5`. Large video files are release assets,
while a compact 3840 × 2160 JPEG supplies the README and wiki preview.
The public [YouTube introduction](https://www.youtube.com/watch?v=-EM-T6uNQAs)
uses that poster as its custom thumbnail and provides nine chapters and selectable
English captions. The downloadable MP4 retains its ten native chapter markers.
The film does not change the portable template version or add authoring tools
to an adopting project's dependencies.

## Build a separate edition 2.0 draft

Run from a reviewed repository checkout. The verifier uses the Python standard
library and creates a disposable local project. The PDF builder additionally
requires **ReportLab and Pillow**, optional publishing dependencies rather than
`.SYSTEMX` runtime dependencies. Use a Python interpreter with them installed;
publication commands do not install packages themselves.

```bash
draft_dir="$(mktemp -d)"
python3 -I -B docs/media/verify_white_paper_v2.py \
  --output "$draft_dir/coordination-verification.json"
python3 -I -B docs/media/build_white_paper_v2.py \
  --output "$draft_dir/SYSTEMX-White-Paper-v2.0-draft.pdf"
python3 -I -B docs/media/tests/test_publication_security.py
```

[build_white_paper_v2.py](build_white_paper_v2.py) defaults to the edition 2.0
manuscript and [publication-template-v2.json](publication-template-v2.json).
`--source` and `--template` select local inputs; `--font-dir` selects a licensed
local Times New Roman font directory. The output must be a separate `.pdf`
draft under an existing directory. Published edition paths are reserved even
when their PDF is missing. The builder makes no network request, model call,
shell invocation, or Mermaid interpretation.

[verify_white_paper_v2.py](verify_white_paper_v2.py) runs synthetic local task,
ROOT, and event operations, including refusal cases. It records sanitized
argument arrays, return codes, returned IDs, and response digests, then removes
the disposable project. Its synthetic harness observations are fixtures, not
real IDE or cloud readback. It does not start agents, contact a provider, create
PRs, deploy an application, or establish model performance. An optional
`--output` writes the same JSON report printed to standard output.

Publication commands enter isolated Python mode before optional imports. Draft
output handling pins directory components, rejects linked or nonregular targets,
and replaces a completed draft atomically. External PDF links use HTTPS;
internal links must name known document destinations. These optional publishing
tools require POSIX directory-descriptor support on macOS or compatible Linux;
they are not a native Windows publishing path. The portable manager and record
format have their own platform support.

## Publication identity and layout

The edition 2.0 template records the title, author, product, company credit,
date, technical baseline, full source commit, publication release, and four
navigation destinations. Current credit is **Lucas (SatoshiUNO)**; **a product
of Wayne Tech Lab LLC**. The portfolio is [Networks.Chat](https://Networks.Chat),
the business is [WayneTechLab.com](https://WayneTechLab.com), and repository and
wiki links complete the navigation. Attribution remains separate from the
`.SYSTEMX` product mark and never populates reusable project or agent records.

The layout uses US Letter pages, one-inch margins, a twelve-point Times-family
body, double-spaced paragraphs, and a half-inch first-line indent. It adds a
branded cover, author/page running header, company/edition footer, linked
contents, list of figures, reading routes, and compact technical displays.
Parenthetical source links lead to alphabetized Works Cited entries with
hanging indents. This is an **MLA-style technical white paper**, not a strict
classroom submission; use the receiving institution's rules for a submission.

The builder embeds the four Times New Roman TTF faces when available in the
macOS supplemental font directory or the specified `--font-dir`. Otherwise it
uses the PDF standard Times family. Do not redistribute licensed fonts. Record
the actual selected face and dependency versions with the published edition.

## Manuscript, figures, and citations

Use `##` for top-level sections and `###` for subheadings. The publication
context contains `### Abstract`; subsequent sections populate the contents.
Code fences retain commands; compact tables repeat their headers. The current
manuscript introduces task authority, flexible planning, supporting roles, ROOT,
project scopes, versioned installation, evidence, and security before the
illustrative resource model and proposed evaluation.

The four edition 2.0 figures are original implementation schematics and a
declared mathematical illustration. Their PNG representations and editable SVG
sources live in [the paper's figures directory](../../.SYSTEMX/MEDIA/White-Paper/figures/).
They are separate from the unchanged four-part 4K infographic media edition
`1.11.0-alpha.3`. The PDF builder embeds direct local PNG/JPEG files from
`figures/`, with descriptive Markdown alt text and numbered `*Fig. N. ...*`
captions. It does not execute SVG or generate a diagram from an unknown layout.

Keep bibliography entries in the current manuscript's Works Cited section.
Named anchors such as `<a id="cite-source-title"></a>` connect body links such
as `[Author, "Short Title"](#cite-source-title)` to the reference. Preserve full
commit or release pins for implementation sources. Do not invent authors,
dates, page numbers, experiments, endorsements, measured savings, or verification
results. The older [white-paper-bibliography.json](white-paper-bibliography.json)
belongs to edition 1.2; it is not edition 2.0's bibliography authority.

## Review before publication

Render every page and inspect the cover, contents, figures, tables, code,
references, headers, and footers. Check extracted text, citation and contents
destinations, clickable external links, bounds, metadata, and package limits.
Confirm that figure captions distinguish implementation schematics from
illustrative accounting. Retain the verifier's positive and refusal results
with their interpreter versions and exact scope; a passing local walkthrough
is not acceptance of a real application or external system.

The PDF provides selectable text and navigation but is not tagged PDF/UA.
Retain the editable Markdown alternative. Do not add PDF JavaScript, automatic
web navigation, tracking, or secret credentials. Freeze final PDF, manuscript,
figure, and metadata hashes only after review, then update README/wiki discovery.
Publishing a new edition does not rewrite a prior released edition.

## Inspect an archived edition 1.2

The older
[PDF](https://github.com/WayneTechLab/dotSYSTEMX/blob/v1.11.0-alpha.4/.SYSTEMX/MEDIA/White-Paper/SYSTEMX-White-Paper-v1.2.pdf),
[manuscript](https://github.com/WayneTechLab/dotSYSTEMX/blob/v1.11.0-alpha.4/.SYSTEMX/MEDIA/White-Paper/SYSTEMX-White-Paper-v1.2.md),
and [metadata](https://github.com/WayneTechLab/dotSYSTEMX/blob/v1.11.0-alpha.4/.SYSTEMX/MEDIA/White-Paper/SYSTEMX-White-Paper-v1.2.json)
remain in tagged history. Read the separate
[historical citation erratum](../../.SYSTEMX/MEDIA/White-Paper/ERRATA.md)
alongside that edition.

The retained [edition 1.2 builder](build_white_paper.py) and
[template](publication-template.json) are archival tooling. Supply the archived
manuscript explicitly and write to a separate draft path; there is no automatic
download or fallback to missing published files:

```bash
draft_dir="$(mktemp -d)"
python3 -I -B docs/media/build_white_paper.py --edition 1.2 \
  --source "/path/to/archived/.SYSTEMX/MEDIA/White-Paper/SYSTEMX-White-Paper-v1.2.md" \
  --template docs/media/publication-template.json \
  --output "$draft_dir/SYSTEMX-White-Paper-v1.2-inspection.pdf"
```

Keep the archived source's required media available; use a complete archived
checkout when investigating its original rendering. Earlier editions 1.0 and
1.1 also require their matching explicit `--source` and separate `--output`.
Inspection drafts are not replacements for published exact-byte assets.

## Historical audio

[narrate_white_paper.py](narrate_white_paper.py) is the **edition 1.1** narration
pipeline. It requires the matching explicit archived `--source`; a different
edition is rejected. Existing audio does not narrate edition 2.0 and must not
be relabeled. Any new recording needs its own edition identity, transcript,
completeness review, and release assets. Audio stays outside the size-limited
portable bundle.
