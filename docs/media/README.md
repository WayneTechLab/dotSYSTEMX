# White-paper publishing

The immutable edition 1.0 remains in `.SYSTEMX/MEDIA`. Edition 1.1 adds the detailed
implementation reference. The PDF builder defaults to edition 1.1 and takes
`--edition 1.0` only when explicitly rebuilding that source for local inspection.
Never replace a published edition or frozen release asset in place.

```bash
python docs/media/build_white_paper.py --edition 1.1
python docs/media/verify_white_paper_example.py --output /tmp/walkthrough.json
python docs/media/narrate_white_paper.py /tmp/reading.txt
```

ReportLab is an optional maintainer dependency, not a template runtime dependency.
PDFs use A4, selectable text, vector diagrams, numbered contents, bookmarks and
clickable references. They are not tagged PDF/UA exports; retain the Markdown.
The PDF drawings must stay consistent with their source Mermaid diagrams.

The walkthrough creates and removes a temporary project. It starts no subagents
or external jobs. It tests local record mechanics and a tiny HTML contract, not
browser behavior, a deployment or a complete 100-answer quality assessment.

The narration tool retains prose, code, questions and inventory. It converts tables
to header/value sentences and diagrams to ordered labels, and omits Markdown,
long link destinations and inline numeric references. Synthesize audio separately
with an available local voice; publish audio outside the size-limited portable
bundle and identify it as synthetic. Do not install a voice or cloud service silently.

Render and visually inspect every new PDF edition. Check extraction, page bounds,
policy-question parity, metadata hashes and the distribution manifest. PDF bytes
may vary by build timestamp/version; published hashes identify exact output bytes.
