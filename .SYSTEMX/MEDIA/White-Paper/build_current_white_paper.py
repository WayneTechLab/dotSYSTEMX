"""Build the current white paper PDF and provenance from its Markdown source.

Authoring only: requires ReportLab and pypdf, neither is a SYSTEMX runtime
dependency. Run from the repository with a reviewed Python environment:

    python .SYSTEMX/MEDIA/White-Paper/build_current_white_paper.py

The builder never reads project records, external data, or network resources.
"""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
import re

from pypdf import PdfReader, __version__ as pypdf_version
from reportlab import Version as reportlab_version
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import HRFlowable, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "SYSTEMX-White-Paper.md"
OUTPUT = HERE / "SYSTEMX-White-Paper.pdf"
PROVENANCE = HERE / "SYSTEMX-White-Paper.json"
TITLE = ".SYSTEMX: Portable Project Coordination for AI-Assisted Work"
EDITION = "2.1"
SOFTWARE = "1.11.0-beta.1"
PREPARED = "2026-10-31"
NAVY = colors.HexColor("#14263e")
TEAL = colors.HexColor("#0d7892")
GRAY = colors.HexColor("#526170")


def inline(source: str) -> str:
    """Convert the limited inline Markdown used by the paper to ReportLab XML."""
    parts = re.split(r"(\[[^]]+\]\([^)]+\)|`[^`]+`|\*\*[^*]+\*\*)", source)
    result: list[str] = []
    for part in parts:
        link = re.fullmatch(r"\[([^]]+)\]\(([^)]+)\)", part)
        if link:
            label, url = link.groups()
            if url.startswith("https://"):
                result.append('<link href="' + html.escape(url, quote=True) +
                              '" color="#0d7892"><u>' + html.escape(label) + "</u></link>")
            else:
                result.append(html.escape(label))
        elif part.startswith("`") and part.endswith("`"):
            result.append('<font name="Courier" size="8.8">' + html.escape(part[1:-1]) + "</font>")
        elif part.startswith("**") and part.endswith("**"):
            result.append("<b>" + html.escape(part[2:-2]) + "</b>")
        else:
            result.append(html.escape(part))
    return "".join(result)


class Paper(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        key = getattr(flowable, "bookmark_name", None)
        if key:
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(flowable.getPlainText(), key, level=0)


def furniture(canvas, doc):
    canvas.saveState()
    width, _ = letter
    canvas.setStrokeColor(colors.HexColor("#cdd8df"))
    canvas.setLineWidth(0.5)
    canvas.line(57, 51, width - 57, 51)
    canvas.setFont("Helvetica", 7.4)
    canvas.setFillColor(GRAY)
    canvas.drawString(57, 39, "WAYNE TECH LAB  /  .SYSTEMX  /  WHITE PAPER 2.1")
    canvas.drawRightString(width - 57, 39, f"{doc.page}")
    if doc.page > 1:
        canvas.setFont("Helvetica-Bold", 7.4)
        canvas.setFillColor(TEAL)
        canvas.drawString(57, letter[1] - 41, "PORTABLE PROJECT COORDINATION")
    canvas.restoreState()


def build():
    raw = SOURCE.read_text(encoding="utf-8")
    if not raw.startswith("# " + TITLE + "\n") or "Software baseline: " + SOFTWARE not in raw:
        raise ValueError("Current manuscript title or software baseline changed")

    title = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=23.5,
                           leading=27.5, textColor=NAVY, spaceAfter=8, alignment=TA_LEFT)
    deck = ParagraphStyle("deck", fontName="Helvetica-Bold", fontSize=10.5,
                          leading=15, textColor=TEAL, spaceAfter=8)
    byline = ParagraphStyle("byline", fontName="Helvetica", fontSize=9,
                            leading=13, textColor=GRAY, spaceAfter=7)
    body = ParagraphStyle("body", fontName="Helvetica", fontSize=10.2,
                          leading=15.4, textColor=NAVY, spaceAfter=8,
                          allowWidows=0, allowOrphans=0)
    heading = ParagraphStyle("heading", fontName="Helvetica-Bold", fontSize=13.8,
                             leading=17.5, textColor=NAVY, spaceBefore=13,
                             spaceAfter=7, keepWithNext=True)
    source_style = ParagraphStyle("source", parent=body, fontSize=9,
                                  leading=13.5, leftIndent=13, firstLineIndent=-13)

    lines = raw.splitlines()
    story = [Paragraph(html.escape(TITLE), title),
             Paragraph(inline(lines[2].strip()), deck),
             Paragraph(inline(lines[3].strip()), byline),
             Paragraph(inline(lines[4].strip()), byline),
             HRFlowable(width="100%", thickness=1.2, color=TEAL, spaceAfter=13)]
    paragraph: list[str] = []
    in_sources = False
    headings = 0

    def flush():
        if paragraph:
            text = " ".join(part.strip() for part in paragraph)
            entry = Paragraph(inline(text), source_style if in_sources else body)
            if text.startswith("`agenda decision-add` previews"):
                story.append(KeepTogether([entry]))
            else:
                story.append(entry)
            paragraph.clear()

    for line in lines[5:]:
        if not line.strip():
            flush()
            continue
        if line.startswith("## "):
            flush()
            name = line[3:]
            if name.startswith("7. "):
                story.append(PageBreak())
            in_sources = name == "Source notes"
            entry = Paragraph(html.escape(name), heading)
            entry.bookmark_name = f"section-{headings}"
            headings += 1
            story.append(entry)
            continue
        if in_sources and re.match(r"^[1-9][0-9]*\. ", line):
            flush()
            story.append(Paragraph(inline(line), source_style))
            continue
        paragraph.append(line)
    flush()

    document = Paper(str(OUTPUT), pagesize=letter, leftMargin=57,
                     rightMargin=57, topMargin=59, bottomMargin=62,
                     title=TITLE, author="Lucas (SatoshiUNO); Wayne Tech Lab LLC",
                     subject=f".SYSTEMX white paper edition {EDITION}; software {SOFTWARE}",
                     invariant=1)
    document.build(story, onFirstPage=furniture, onLaterPages=furniture)
    pdf = PdfReader(str(OUTPUT))
    extracted = "\n".join(page.extract_text() or "" for page in pdf.pages)
    for phrase in ("Access Matrix", "Agent Beta", "Agent 1", "1.11.0-beta.1",
                   "GitHub Actions", "Blender", "Source notes"):
        if phrase not in extracted:
            raise ValueError("PDF text missing: " + phrase)

    def file_record(path):
        blob = path.read_bytes()
        return {"file": path.name, "bytes": len(blob),
                "sha256": hashlib.sha256(blob).hexdigest()}

    metadata = {
        "schemaVersion": 1,
        "title": TITLE,
        "edition": EDITION,
        "technicalBaseline": SOFTWARE,
        "preparedOn": PREPARED,
        "author": "Lucas (SatoshiUNO)",
        "publisher": "Wayne Tech Lab LLC",
        "publicationTag": "v" + SOFTWARE,
        "scope": "Current reusable public template; no adopter or host acceptance claimed",
        "pages": len(pdf.pages),
        "figures": 0,
        "pageSize": "US Letter",
        "pdfTextSelectable": True,
        "pdfTaggedUa": False,
        "textAlternative": SOURCE.name,
        "pdfOutlineEntries": headings,
        "builder": "build_current_white_paper.py",
        "builderDependency": (f"ReportLab {reportlab_version} and pypdf {pypdf_version} "
                              "(authoring only)"),
        "checksumMethod": "SHA-256 of exact manuscript and PDF bytes; metadata does not hash itself",
        "historicalEdition": {
            "edition": "2.0",
            "technicalBaseline": "1.11.0-alpha.4",
            "retainedAt": "v1.11.0-alpha.5",
        },
        "files": [file_record(SOURCE), file_record(OUTPUT), file_record(Path(__file__))],
    }
    PROVENANCE.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"Built {OUTPUT.name}: {len(pdf.pages)} pages, {OUTPUT.stat().st_size} bytes")


if __name__ == "__main__":
    build()
