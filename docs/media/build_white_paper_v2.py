#!/usr/bin/env python3
"""Build edition 2.0 as a separate draft PDF from bounded local publication files.

Uses the edition 1.2 publisher's directory-descriptor and atomic-output patterns.
No network request, shell command, Mermaid interpretation or model call is made.
Optional dependencies: ReportLab and Pillow. Published editions are reserved;
review the separate draft before an explicit publication step.
"""
import sys
if __name__ == '__main__' and not sys.flags.isolated:
    _bootstrap_os = sys.modules.get('os')
    if _bootstrap_os is None or not sys.executable:
        sys.exit('White-paper builder requires Python isolated mode')
    try:
        _bootstrap_os.execv(sys.executable, [sys.executable, '-I', '-B', __file__, *sys.argv[1:]])
    except OSError as error:
        sys.exit('White-paper builder could not enter isolated mode: ' + str(error))

import argparse
from html import escape, unescape
from io import BytesIO
import json
import os
from pathlib import Path
import re
import secrets
import stat
from urllib.parse import urlsplit

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, KeepTogether, PageBreak, PageTemplate,
    Paragraph, Preformatted, Spacer, Table, TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).resolve().parents[2]
NAVY = colors.HexColor('#142c3c')
TEAL = colors.HexColor('#007981')
MUTED = colors.HexColor('#455a64')
LIGHT = colors.HexColor('#edf5f5')
RULE = colors.HexColor('#cbd9df')
W, H = letter
MARGIN = 72
WIDTH = W - 2 * MARGIN
FONT, BOLD, ITALIC = 'Times-Roman', 'Times-Bold', 'Times-Italic'
CONFIG, STYLES = {}, {}
MAX_SOURCE = 2 * 1024 * 1024
MAX_FIGURE = 16 * 1024 * 1024
MAX_PIXELS = 24_000_000
MAX_FIGURES = 16


def https_url(url):
    """Reject credentials, control characters, ambiguous URLs and local schemes."""
    if not isinstance(url, str) or any(ord(ch) < 33 or ch in '\\<>"' for ch in url):
        raise ValueError('Paper links must use a valid HTTPS URL')
    parsed = urlsplit(url)
    try:
        parsed.port
    except ValueError as error:
        raise ValueError('Paper links must use a valid HTTPS URL') from error
    if (parsed.scheme != 'https' or not parsed.netloc or not parsed.hostname or
            parsed.username is not None or parsed.password is not None):
        raise ValueError('Paper links must use a valid HTTPS URL')
    return url


def absolute_path(path):
    # Normalize dot components without following an input or parent symlink.
    return Path(os.path.abspath(os.path.expanduser(str(path))))


def open_directory(path):
    """Pin every parent component; do not follow a planted ancestor symlink."""
    path = absolute_path(path)
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    directory_fd = os.open(path.anchor, flags)
    try:
        for component in path.parts[1:]:
            next_fd = os.open(component, flags, dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = next_fd
        return directory_fd
    except BaseException:
        os.close(directory_fd)
        raise


def read_regular(path, limit, purpose):
    """Read a single-link regular file via a pinned, no-follow directory."""
    path = absolute_path(path)
    directory_fd = open_directory(path.parent)
    try:
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | getattr(os, 'O_NONBLOCK', 0),
                     dir_fd=directory_fd)
        with os.fdopen(fd, 'rb') as stream:
            detail = os.fstat(stream.fileno())
            if (not stat.S_ISREG(detail.st_mode) or detail.st_nlink != 1 or
                    detail.st_size > limit):
                raise ValueError(purpose + ' must be one regular file within its size limit')
            data = stream.read(limit + 1)
            if len(data) > limit:
                raise ValueError(purpose + ' exceeded its size limit while reading')
            final = os.fstat(stream.fileno())
            if (detail.st_dev, detail.st_ino, detail.st_size, detail.st_mtime_ns) != (
                    final.st_dev, final.st_ino, final.st_size, final.st_mtime_ns):
                raise RuntimeError(purpose + ' changed while reading')
            return data
    finally:
        os.close(directory_fd)


def configure(config, font_dir=None):
    global CONFIG, STYLES, MARGIN, WIDTH, FONT, BOLD, ITALIC
    if config.get('schemaVersion') != 1 or config.get('pageSize') != 'LETTER':
        raise ValueError('Expected publication schema 1 and LETTER pages')
    for key, expected in (('marginPoints', 72), ('bodySizePoints', 12),
                          ('bodyLeadingPoints', 24), ('paragraphIndentPoints', 36)):
        if isinstance(config.get(key), bool) or config.get(key) != expected:
            raise ValueError('MLA-style publication requires ' + key + '=' + str(expected))
    for key in ('edition', 'product', 'title', 'subtitle', 'author', 'runningAuthor',
                'publisher', 'productCredit', 'date', 'technicalBaseline', 'layout', 'keywords'):
        value = config.get(key)
        if not isinstance(value, str) or not 1 <= len(value) <= 500 or any(ord(c) < 32 for c in value):
            raise ValueError('Invalid publication field: ' + key)
    if config['edition'] != '2.0':
        raise ValueError('This publisher builds only edition 2.0')
    if not re.fullmatch(r'[a-f0-9]{40}', config.get('technicalBaselineCommit', '')):
        raise ValueError('Technical baseline requires a full Git commit')
    links = config.get('links')
    if not isinstance(links, list) or len(links) != 4:
        raise ValueError('Exactly four publication identity links are required')
    for link in links:
        if not isinstance(link, dict) or not all(isinstance(link.get(k), str) and
                0 < len(link[k]) <= 160 for k in ('label', 'role')):
            raise ValueError('Invalid publication identity link')
        https_url(link.get('url'))
    if sum(pdfmetrics.stringWidth(link['label'], 'Helvetica', 7.4) + 15
           for link in links) > WIDTH - 45:
        raise ValueError('Publication link labels exceed the available footer width')
    https_url(config.get('figureBaseUrl'))
    if not config['figureBaseUrl'].endswith('/'):
        raise ValueError('Figure base URL must end in a slash')
    CONFIG = config
    MARGIN, WIDTH = 72, W - 144
    FONT, BOLD, ITALIC = 'Times-Roman', 'Times-Bold', 'Times-Italic'
    candidate = absolute_path(font_dir) if font_dir else Path('/System/Library/Fonts/Supplemental')
    names = [('Paper2Serif', 'Times New Roman.ttf'), ('Paper2SerifBold', 'Times New Roman Bold.ttf'),
             ('Paper2SerifItalic', 'Times New Roman Italic.ttf'),
             ('Paper2SerifBoldItalic', 'Times New Roman Bold Italic.ttf')]
    if all((candidate / filename).is_file() for _, filename in names):
        for name, filename in names:
            data = read_regular(candidate / filename, 16 * 1024 * 1024, 'Font')
            pdfmetrics.registerFont(TTFont(name, BytesIO(data)))
        pdfmetrics.registerFontFamily('Paper2Serif', normal='Paper2Serif', bold='Paper2SerifBold',
                                     italic='Paper2SerifItalic', boldItalic='Paper2SerifBoldItalic')
        FONT, BOLD, ITALIC = 'Paper2Serif', 'Paper2SerifBold', 'Paper2SerifItalic'
    elif font_dir:
        raise ValueError('The font directory must contain four Times New Roman TTF files')
    STYLES = {
        'body': ParagraphStyle('body', fontName=FONT, fontSize=12, leading=24,
                              firstLineIndent=36, textColor=colors.black, spaceAfter=0,
                              allowWidows=0, allowOrphans=0),
        'front': ParagraphStyle('front', fontName=FONT, fontSize=12, leading=24,
                               textColor=colors.black, spaceAfter=10,
                               allowWidows=0, allowOrphans=0),
        'small': ParagraphStyle('small', fontName='Helvetica', fontSize=9, leading=13,
                               textColor=MUTED, spaceAfter=10),
        'h1': ParagraphStyle('h1', fontName=BOLD, fontSize=17, leading=22,
                            textColor=NAVY, spaceBefore=20, spaceAfter=15, keepWithNext=True),
        'h2': ParagraphStyle('h2', fontName=BOLD, fontSize=12, leading=18,
                            textColor=NAVY, spaceBefore=15, spaceAfter=8, keepWithNext=True),
        'cell': ParagraphStyle('cell', fontName=FONT, fontSize=10, leading=14,
                              textColor=colors.black),
        'th': ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=9, leading=12,
                            textColor=colors.white),
        'code': ParagraphStyle('code', fontName='Courier', fontSize=8, leading=11,
                              textColor=NAVY, backColor=LIGHT, borderPadding=6,
                              spaceBefore=10, spaceAfter=12),
        'caption': ParagraphStyle('caption', fontName=FONT, fontSize=10, leading=14,
                                 textColor=MUTED, spaceBefore=8, spaceAfter=16),
        'works': ParagraphStyle('works', fontName=FONT, fontSize=12, leading=24,
                               leftIndent=36, firstLineIndent=-36, textColor=colors.black,
                               spaceAfter=8, splitLongWords=True),
    }


def inline(text, small=False):
    out = escape(text, quote=False).replace('&lt;br/&gt;', '<br/>')
    def safe_link(match):
        url = unescape(match[2])
        if not re.fullmatch(r'#[A-Za-z][\w.-]*', url):
            https_url(url)
        return '<link href="' + escape(url, quote=True) + '" color="#007981">' + match[1] + '</link>'
    out = re.sub(r'\[([^\]]+)\]\(([^\s)]+)\)', safe_link, out)
    out = re.sub(r'`([^`]+)`', lambda match: '<font name="Courier" size="' +
                 ('8' if small else '10') + '">' + match[1] + '</font>', out)
    out = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', out)
    return re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<i>\1</i>', out)


def para(text, kind='body'):
    return Paragraph(inline(text, kind in ('cell', 'th', 'small', 'caption')), STYLES[kind])


def slug(title):
    key = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    return key if key and key[0].isalpha() else 'section-' + key


def table(lines):
    rows = [[part.strip() for part in line.strip().strip('|').split('|')] for line in lines]
    rows = [row for row in rows if not all(re.fullmatch(r'[: -]+', cell) for cell in row)]
    count = len(rows[0])
    if count > 4 or any(len(row) != count for row in rows):
        raise ValueError('Expected a consistent Markdown table with at most four columns')
    ratios = {2: [.32, .68], 3: [.24, .34, .42], 4: [.17, .24, .29, .30]}.get(count, [1])
    result = Table([[para(cell, 'th' if index == 0 else 'cell') for cell in row]
                    for index, row in enumerate(rows)],
                   colWidths=[WIDTH * ratio for ratio in ratios], repeatRows=1, hAlign='LEFT')
    result.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 7), ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, -1), (-1, -1), .5, RULE),
    ]))
    return [Spacer(1, 8), result, Spacer(1, 12)]


class LinkedImage(Image):
    """Embed a bounded PNG/JPEG snapshot; click through to its configured source."""
    def __init__(self, data, url):
        with PILImage.open(BytesIO(data)) as image:
            if image.format not in ('PNG', 'JPEG') or image.width * image.height > MAX_PIXELS:
                raise ValueError('Figure must be a PNG/JPEG of at most 24 million pixels')
            image.load()
            width, height = image.size
            if not width or not height:
                raise ValueError('Figure has no drawable area')
        self.url = https_url(url)
        display_width = min(WIDTH, WIDTH * 480 / (WIDTH * height / width))
        super().__init__(BytesIO(data), width=display_width, height=display_width * height / width)
        self.hAlign = 'CENTER'

    def draw(self):
        super().draw()
        self.canv.linkURL(self.url, (0, 0, self.drawWidth, self.drawHeight), relative=1, thickness=0)


def content(text, source, kind='body'):
    lines, result, index, pending_anchor, image_count = text.splitlines(), [], 0, None, 0
    while index < len(lines):
        line = lines[index].strip()
        if not line or line.startswith('# '):
            index += 1
            continue
        anchor = re.fullmatch(r'<a id="([A-Za-z][\w.-]*)"></a>', line)
        if anchor:
            if pending_anchor:
                raise ValueError('Anchor must be followed by content')
            pending_anchor = anchor[1]
            index += 1
            continue
        if line == '<!-- pagebreak -->':
            result.append(PageBreak())
            index += 1
            continue
        if line.startswith('<!--'):
            index += 1
            continue
        if line.startswith(('## ', '### ')):
            level = 'h1' if line.startswith('## ') else 'h2'
            title = line[3:] if level == 'h1' else line[4:]
            paragraph = para(title, level)
            paragraph.bookmark_key = pending_anchor or slug(title)
            if level == 'h1':
                paragraph.section_key = paragraph.bookmark_key
            pending_anchor = None
            result.append(paragraph)
            index += 1
            continue
        figure = re.fullmatch(r'!\[([^\]]+)\]\(([^)]+)\)', line)
        if figure:
            image_count += 1
            if image_count > MAX_FIGURES:
                raise ValueError('Too many local figures')
            filename = re.fullmatch(r'figures/([A-Za-z0-9][A-Za-z0-9._-]*\.(?:png|jpe?g))', figure[2], re.I)
            if filename is None:
                raise ValueError('Figure must be a direct local figures/ PNG or JPEG')
            path = source.parent / 'figures' / filename[1]
            data = read_regular(path, MAX_FIGURE, 'Figure')
            result.append(LinkedImage(data, CONFIG['figureBaseUrl'] + filename[1]))
            index += 1
            continue
        if line.startswith('```'):
            language, code = line[3:], []
            index += 1
            while index < len(lines) and not lines[index].startswith('```'):
                code.append(lines[index])
                index += 1
            if index == len(lines):
                raise ValueError('Unclosed code block')
            if language == 'mermaid':
                raise ValueError('Use an explicitly rendered local figure for diagrams')
            result.append(Preformatted('\n'.join(code), STYLES['code'], maxLineLength=87,
                                       splitChars=' /', newLineChars='  '))
            index += 1
            continue
        if line.startswith('|'):
            rows = []
            while index < len(lines) and lines[index].strip().startswith('|'):
                rows.append(lines[index])
                index += 1
            result.extend(table(rows))
            continue
        caption = re.fullmatch(r'\*Fig\. (\d+)\. (.*)\*', line)
        if caption:
            paragraph = para('Fig. ' + caption[1] + '. ' + caption[2], 'caption')
            paragraph.figure_key = pending_anchor or 'figure' + caption[1]
            paragraph.figure_label = 'Fig. ' + caption[1] + '. ' + caption[2].split('. ')[0]
            pending_anchor = None
            if result and isinstance(result[-1], Image):
                # KeepTogether exposes the caption to afterFlowable after splitting.
                result[-1] = KeepTogether([result[-1], paragraph])
            else:
                result.append(paragraph)
            index += 1
            continue
        block = [line]
        index += 1
        if not re.match(r'^(?:\d+\. |[-*] )', line):
            while index < len(lines) and lines[index].strip() and not lines[index].startswith(
                    ('## ', '### ', '```', '|', '<!--', '<a ', '![', '- ', '*Fig. ')):
                block.append(lines[index].strip())
                index += 1
        paragraph = para(' '.join(block), kind)
        if pending_anchor:
            paragraph.bookmark_key = pending_anchor
            pending_anchor = None
        result.append(paragraph)
    if pending_anchor:
        raise ValueError('Anchor has no following content')
    return result


class PaperDoc(BaseDocTemplate):
    def afterFlowable(self, item):
        if hasattr(item, 'section_key'):
            self.canv.bookmarkPage(item.section_key)
            self.canv.addOutlineEntry(item.getPlainText(), item.section_key, 0, False)
            self.notify('TOCEntry', (0, item.getPlainText(), self.page, item.section_key))
        elif hasattr(item, 'bookmark_key'):
            self.canv.bookmarkPage(item.bookmark_key)
        if hasattr(item, 'figure_key'):
            self.canv.bookmarkPage(item.figure_key)
            self.notify('FigureEntry', (0, item.figure_label, self.page, item.figure_key))


class FigureContents(TableOfContents):
    def notify(self, kind, stuff):
        if kind == 'FigureEntry':
            self.addEntry(*stuff)


def navigation(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(MUTED)
    canvas.setFont(FONT, 12)
    canvas.drawRightString(W - MARGIN, H - 36, CONFIG['runningAuthor'] + ' ' + str(doc.page))
    canvas.setFont('Helvetica', 7.5)
    canvas.drawString(MARGIN, H - 36, CONFIG['product'] + '  |  TECHNICAL WHITE PAPER')
    canvas.setStrokeColor(RULE)
    canvas.line(MARGIN, 53, W - MARGIN, 53)
    canvas.setFont('Helvetica', 7.4)
    canvas.drawString(MARGIN, 40, CONFIG['productCredit'])
    canvas.drawRightString(W - MARGIN, 40, 'EDITION ' + CONFIG['edition'] + '  |  ' + CONFIG['date'])
    x = MARGIN
    for item in CONFIG['links']:
        width = pdfmetrics.stringWidth(item['label'], 'Helvetica', 7.4)
        canvas.setFillColor(TEAL)
        canvas.drawString(x, 26, item['label'])
        canvas.linkURL(item['url'], (x, 24, x + width, 34), relative=0, thickness=0)
        x += width + 15
    canvas.drawRightString(W - MARGIN, 26, 'Contents')
    canvas.linkRect('', 'contents', (W - MARGIN - 35, 24, W - MARGIN, 34), relative=0, thickness=0)
    canvas.restoreState()


def cover(canvas, doc):
    canvas.setKeywords(CONFIG['keywords'])
    canvas.setCreator('.SYSTEMX publication builder 2.0')
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, H - 18, W, 18, fill=1, stroke=0)
    canvas.setFillColor(TEAL)
    canvas.rect(MARGIN, 94, WIDTH, 4, fill=1, stroke=0)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN, 76, 'PUBLIC TECHNICAL WHITE PAPER')
    canvas.drawRightString(W - MARGIN, 76, 'ALPHA  |  USE AT YOUR OWN RISK')
    canvas.restoreState()


def parse_sections(text):
    """Retain an explicit anchor immediately before each second-level heading."""
    matches = list(re.finditer(r'^(?:<a id="([A-Za-z][\w.-]*)"></a>\n+)?## ([^\n]+)\n', text, re.M))
    if len(matches) < 2:
        raise ValueError('Paper needs a front-matter section and at least one body section')
    sections = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.append((match[2], match[1] or slug(match[2]), text[match.end():end]))
    keys = [key for _, key, _ in sections]
    if len(set(keys)) != len(keys):
        raise ValueError('Duplicate section anchors')
    return sections


def validate_internal_links(text, sections):
    keys = {'abstract', 'contents', 'figures'} | {key for _, key, _ in sections}
    keys |= set(re.findall(r'<a id="([A-Za-z][\w.-]*)"></a>', text))
    keys |= {slug(title) for title in re.findall(r'^### (.+)$', text, re.M)}
    keys |= {'figure' + number for number in re.findall(r'^\*Fig\. (\d+)\.', text, re.M)}
    targets = re.findall(r'\]\(#([A-Za-z][\w.-]*)\)', text)
    missing = set(targets) - keys
    if missing:
        raise ValueError('Unresolved internal paper links: ' + ', '.join(sorted(missing)))


def build(source, output):
    text = read_regular(source, MAX_SOURCE, 'Manuscript').decode('utf-8')
    if len(re.findall(r'^!\[', text, re.M)) > MAX_FIGURES:
        raise ValueError('Too many local figures')
    sections = parse_sections(text)
    validate_internal_links(text, sections)
    _, _, front = sections.pop(0)
    if '### Abstract\n' not in front:
        raise ValueError('Front matter must contain a third-level Abstract heading')
    abstract = front.split('### Abstract\n', 1)[1]
    doc = PaperDoc(output, pagesize=letter, leftMargin=MARGIN, rightMargin=MARGIN,
                   topMargin=MARGIN, bottomMargin=MARGIN,
                   title=CONFIG['product'] + ': ' + CONFIG['title'],
                   author=CONFIG['author'] + ' | ' + CONFIG['publisher'],
                   subject=CONFIG['subtitle'] + '; ' + CONFIG['layout'], pageCompression=1)
    frame = Frame(MARGIN, MARGIN, WIDTH, H - 2 * MARGIN, leftPadding=0,
                  rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([
        PageTemplate(id='cover', frames=[frame], onPage=cover, autoNextPageTemplate='body'),
        PageTemplate(id='body', frames=[frame], onPage=navigation),
    ])
    wordmark = ParagraphStyle('wordmark', fontName='Helvetica-Bold', fontSize=42,
                              leading=48, textColor=NAVY, spaceAfter=28)
    title_style = ParagraphStyle('coverTitle', fontName=BOLD, fontSize=28,
                                 leading=33, textColor=NAVY, spaceAfter=17)
    story = [Spacer(1, 24), Paragraph(escape(CONFIG['product']), wordmark),
             Paragraph(escape(CONFIG['title']), title_style), para(CONFIG['subtitle'], 'front'),
             Spacer(1, 15), para('EDITION ' + CONFIG['edition'] + '  |  ' + CONFIG['date'], 'small'),
             para('**' + CONFIG['author'] + '**', 'front'), para(CONFIG['productCredit'], 'front')]
    for item in CONFIG['links']:
        story.append(para(item['role'] + ': [' + item['label'] + '](' + item['url'] + ')', 'small'))
    baseline_url = CONFIG['links'][2]['url'].rstrip('/') + '/tree/' + CONFIG['technicalBaselineCommit']
    story.extend([
        Spacer(1, 10), para('Technical baseline: [v' + CONFIG['technicalBaseline'] + '](' +
                            baseline_url + '). Publication edition and software version are separate.', 'small'),
        para('Baseline commit: [' + CONFIG['technicalBaselineCommit'] + '](' + baseline_url + ')', 'small'),
        PageBreak(),
    ])
    heading = para('Abstract and publication context', 'h1')
    heading.bookmark_key = 'abstract'
    story.append(heading)
    story.extend(content(abstract, source, 'front'))
    story.extend([para('Keywords', 'h2'), para(CONFIG['keywords'], 'front'), PageBreak()])
    heading = para('Contents', 'h1')
    heading.bookmark_key = 'contents'
    story.extend([heading, para('Click a section title or page number. Body-page footers return here. '
                              'External links open in your PDF viewer or browser.', 'small')])
    toc = TableOfContents()
    toc.levelStyles = [ParagraphStyle('toc', fontName=FONT, fontSize=11, leading=16,
                                     spaceBefore=4, spaceAfter=4, rightIndent=30)]
    story.append(toc)
    heading = para('Figures and reading routes', 'h1')
    heading.bookmark_key = 'figures'
    story.extend([PageBreak(), heading])
    figures = FigureContents()
    figures.levelStyles = [ParagraphStyle('figlist', fontName=FONT, fontSize=11, leading=16,
                                         spaceBefore=7, spaceAfter=7, rightIndent=30)]
    story.extend([figures, Spacer(1, 14), para('Choose a reading route', 'h2')])
    chapter_groups = [sections[:3], sections[3:9], sections[9:12], sections[12:]]
    routes = []
    for name, group in zip(('Orientation', 'Operating mechanics', 'Evaluation and adoption',
                            'Technical reference'), chapter_groups):
        if group:
            routes.append('| ' + name + ' | ' + '; '.join('[' + title + '](#' + key + ')'
                                                           for title, key, _ in group) + ' |')
    story.extend(table(['| Reading route | Sections |', '| --- | --- |'] + routes))
    story.append(para('Publication format: 12-point Times body, double-spaced prose, one-inch margins, '
                      'parenthetical source references and hanging-indent Works Cited. Branded front matter, '
                      'technical tables, code and figure captions use compact display spacing. '
                      'These are disclosed MLA-style adaptations.', 'small'))
    story.append(PageBreak())
    for index, (title, key, body) in enumerate(sections):
        if index and (title.startswith('Appendix ') or title == 'Works Cited'):
            story.append(PageBreak())
        heading = para(title, 'h1')
        heading.section_key = key
        story.append(heading)
        story.extend(content(body, source, 'works' if title == 'Works Cited' else 'body'))
    doc.multiBuild(story)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--template', type=Path, default=Path(__file__).with_name('publication-template-v2.json'))
    parser.add_argument('--source', type=Path)
    parser.add_argument('--output', type=Path, required=True,
                        help='A separate draft path; published edition paths are reserved')
    parser.add_argument('--font-dir', type=Path)
    args = parser.parse_args()
    if os.name != 'posix' or not all(hasattr(os, name) for name in ('O_DIRECTORY', 'O_NOFOLLOW')):
        raise RuntimeError('Safe PDF publication requires POSIX directory-descriptor operations')
    configure(json.loads(read_regular(args.template, 64 * 1024, 'Template').decode('utf-8')), args.font_dir)
    source = absolute_path(args.source or ROOT / '.SYSTEMX/MEDIA/White-Paper/SYSTEMX-White-Paper-v2.0.md')
    output = absolute_path(args.output)
    if output.suffix.lower() != '.pdf':
        raise ValueError('Draft output must have a .pdf extension')
    if output in (source, absolute_path(args.template)):
        raise ValueError('Output must not replace an input file')
    reserved_root = ROOT / '.SYSTEMX/MEDIA/White-Paper'
    if output.parent == reserved_root and re.fullmatch(r'SYSTEMX-White-Paper-v[^/]+\.pdf', output.name):
        raise ValueError('Published edition path is reserved; choose a separate draft output')
    directory_fd = open_directory(output.parent)
    temporary_name = None
    try:
        try:
            existing = os.stat(output.name, dir_fd=directory_fd, follow_symlinks=False)
        except FileNotFoundError:
            existing = None
        if existing is not None and (not stat.S_ISREG(existing.st_mode) or existing.st_nlink != 1):
            raise ValueError('Output must be one regular file')
        mode = stat.S_IMODE(existing.st_mode) if existing is not None else 0o600
        initial_output = None if existing is None else (
            existing.st_dev, existing.st_ino, existing.st_size, existing.st_mtime_ns)
        temporary_name = '.systemx-paper-v2-' + secrets.token_hex(16) + '.pdf'
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
        temporary_fd = os.open(temporary_name, flags, mode, dir_fd=directory_fd)
        with os.fdopen(temporary_fd, 'wb') as draft:
            os.fchmod(draft.fileno(), mode)
            build(source, draft)
            draft.flush()
            os.fsync(draft.fileno())
        try:
            existing = os.stat(output.name, dir_fd=directory_fd, follow_symlinks=False)
        except FileNotFoundError:
            existing = None
        if existing is not None and (not stat.S_ISREG(existing.st_mode) or existing.st_nlink != 1):
            raise ValueError('Output changed to a non-regular or aliased file')
        current_output = None if existing is None else (
            existing.st_dev, existing.st_ino, existing.st_size, existing.st_mtime_ns)
        if current_output != initial_output:
            raise RuntimeError('Output file changed during PDF build')
        pinned = os.fstat(directory_fd)
        current = os.stat(output.parent, follow_symlinks=False)
        if (pinned.st_dev, pinned.st_ino) != (current.st_dev, current.st_ino):
            raise RuntimeError('Output directory changed during PDF build')
        os.replace(temporary_name, output.name, src_dir_fd=directory_fd, dst_dir_fd=directory_fd)
        temporary_name = None
        size = os.stat(output.name, dir_fd=directory_fd, follow_symlinks=False).st_size
        current = os.stat(output.parent, follow_symlinks=False)
        if (pinned.st_dev, pinned.st_ino) != (current.st_dev, current.st_ino):
            raise RuntimeError('Output directory changed during PDF publication')
    finally:
        if temporary_name is not None:
            os.unlink(temporary_name, dir_fd=directory_fd)
        os.close(directory_fd)
    print(json.dumps({'output': str(output), 'bytes': size, 'font': FONT,
                      'edition': CONFIG['edition'], 'technicalBaseline': CONFIG['technicalBaseline']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
