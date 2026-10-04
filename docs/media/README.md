# White-paper publishing

`build_white_paper.py` typesets the editable Markdown in `.SYSTEMX/MEDIA` into
its sibling PDF. It uses ReportLab in a separate maintainer environment; this
is optional publication tooling, not a dependency of the installed template.

```bash
python docs/media/build_white_paper.py
```

The document uses A4 pages, selectable text, two vector diagrams, bookmarks and
clickable references. The PDF is not a tagged PDF/UA export; retain the Markdown
for accessible reading and editing. The diagrams represent the architecture and
workflow described in the source's Mermaid blocks. The custom PDF drawing code
must be updated alongside those blocks if their semantics change.

When revising an edition, check all pages visually after rendering with Poppler,
verify text extraction and page bounds, update document metadata and hashes, and
rebuild the distribution manifest. Keep individual portable files under 2 MiB.
Future published editions should use new filenames to support additive updates.
Do not replace a published edition in place or change frozen release assets.
PDF bytes may vary with build timestamps and ReportLab versions; verification
checksums identify the exact published PDF, not a reproducible-build guarantee.
