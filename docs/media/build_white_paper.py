#!/usr/bin/env python3
"""Publish a branded MLA-style research paper. Optional dependencies: ReportLab, Pillow.

The JSON template controls identity and layout. Legacy editions use their frozen
builder. Sources and assets are local; the builder performs no network requests.
"""
import argparse
from functools import lru_cache
from html import escape
from io import BytesIO
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Flowable, Frame, Image, KeepTogether, PageBreak,
    PageTemplate, Paragraph, Preformatted, Spacer, Table, TableStyle,
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
FONT = 'Times-Roman'
BOLD = 'Times-Bold'
ITALIC = 'Times-Italic'
STYLES = {}
CONFIG = {}


def configure(config, font_dir=None):
    global CONFIG, MARGIN, WIDTH, STYLES, FONT, BOLD, ITALIC
    CONFIG = config
    if config.get('schemaVersion') != 1 or config.get('pageSize') != 'LETTER':
        raise ValueError('Expected publication schema 1 and LETTER pages')
    MARGIN = float(config['marginPoints'])
    WIDTH = W - 2 * MARGIN
    if not 54 <= MARGIN <= 90:
        raise ValueError('Margin must be between 54 and 90 points')
    for link in config['links']:
        if not link['url'].startswith('https://'):
            raise ValueError('Publication links must use HTTPS')
    candidate = Path(font_dir) if font_dir else Path('/System/Library/Fonts/Supplemental')
    names = [('PaperSerif', 'Times New Roman.ttf'), ('PaperSerifBold', 'Times New Roman Bold.ttf'),
             ('PaperSerifItalic', 'Times New Roman Italic.ttf'), ('PaperSerifBoldItalic', 'Times New Roman Bold Italic.ttf')]
    if all((candidate / filename).is_file() for _, filename in names):
        for name, filename in names:
            pdfmetrics.registerFont(TTFont(name, str(candidate / filename)))
        pdfmetrics.registerFontFamily('PaperSerif', normal='PaperSerif', bold='PaperSerifBold', italic='PaperSerifItalic', boldItalic='PaperSerifBoldItalic')
        FONT, BOLD, ITALIC = 'PaperSerif', 'PaperSerifBold', 'PaperSerifItalic'
    elif font_dir:
        raise ValueError('The font directory must contain the four Times New Roman TTF files')
    STYLES = {
        'body': ParagraphStyle('body', fontName=FONT, fontSize=config['bodySizePoints'], leading=config['bodyLeadingPoints'], firstLineIndent=config['paragraphIndentPoints'], textColor=colors.black, spaceAfter=0, rightIndent=5, allowWidows=0, allowOrphans=0),
        'front': ParagraphStyle('front', fontName=FONT, fontSize=12, leading=18, textColor=NAVY, spaceAfter=12),
        'small': ParagraphStyle('small', fontName='Helvetica', fontSize=9, leading=13, textColor=MUTED, spaceAfter=9),
        'h1': ParagraphStyle('h1', fontName=BOLD, fontSize=18, leading=23, textColor=NAVY, spaceAfter=20, keepWithNext=True),
        'h2': ParagraphStyle('h2', fontName=BOLD, fontSize=12, leading=18, textColor=NAVY, spaceBefore=16, spaceAfter=8, keepWithNext=True),
        'cell': ParagraphStyle('cell', fontName=FONT, fontSize=10, leading=13, textColor=colors.black),
        'th': ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=colors.white),
        'code': ParagraphStyle('code', fontName='Courier', fontSize=8, leading=11, textColor=NAVY, backColor=LIGHT, borderPadding=6, spaceBefore=10, spaceAfter=12),
        'caption': ParagraphStyle('caption', fontName=FONT, fontSize=10, leading=14, textColor=MUTED, spaceBefore=8, spaceAfter=16),
        'works': ParagraphStyle('works', fontName=FONT, fontSize=12, leading=24, leftIndent=36, firstLineIndent=-36, textColor=colors.black, spaceAfter=0, splitLongWords=True),
    }


def inline(text, small=False):
    out = escape(text, quote=False).replace('&lt;br/&gt;', '<br/>')
    out = re.sub(r'\[([^\]]+)\]\(([^\s)]+)\)', lambda m: '<link href="' + escape(m[2], quote=True) + '" color="#007981">' + m[1] + '</link>', out)
    out = re.sub(r'`([^`]+)`', lambda m: '<font name="Courier" size="' + ('8' if small else '10') + '">' + m[1] + '</font>', out)
    out = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', out)
    out = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<i>\1</i>', out)
    return out


def para(text, kind='body'):
    if kind == 'works':
        def location(match):
            label, url = match.groups()
            chunks = []
            while label:
                count = len(label)
                while pdfmetrics.stringWidth(label[:count], FONT, 12) > WIDTH - 44:
                    count -= 1
                if count < len(label):
                    natural = max(label.rfind('/', 0, count), label.rfind('-', 0, count))
                    if natural > count // 2:
                        count = natural + 1
                chunks.append(label[:count]); label = label[count:]
            return '<br/>' + '<br/>'.join('[' + chunk + '](' + url + ')' for chunk in chunks)
        text = re.sub(r'\[([^\]]+)\]\((https://[^\s)]+)\)', location, text)
    return Paragraph(inline(text, kind in ('cell', 'th', 'small', 'caption')), STYLES[kind])


class Diagram(Flowable):
    """Two explicitly supported diagrams; labels track the source Mermaid."""
    def __init__(self, kind):
        super().__init__()
        self.kind = kind
        self.width = WIDTH
        self.height = 182 if kind == 'architecture' else 76

    def draw(self):
        c = self.canv
        def box(x, y, w, h, text, accent=False):
            c.setFillColor(TEAL if accent else LIGHT)
            c.setStrokeColor(TEAL if accent else RULE)
            c.roundRect(x, y, w, h, 4, fill=1, stroke=1)
            p = Paragraph(text, ParagraphStyle('box', fontName='Helvetica-Bold' if accent else 'Helvetica', fontSize=8.5, leading=11, alignment=1, textColor=colors.white if accent else NAVY))
            _, ph = p.wrap(w-12, h)
            p.drawOn(c, x+6, y+(h-ph)/2)
        def arrow(x1, y1, x2, y2):
            c.setStrokeColor(TEAL); c.setFillColor(TEAL); c.line(x1, y1, x2, y2)
            p=c.beginPath(); p.moveTo(x2,y2)
            if x2>x1: p.lineTo(x2-4,y2+3); p.lineTo(x2-4,y2-3)
            elif x2<x1: p.lineTo(x2+4,y2+3); p.lineTo(x2+4,y2-3)
            else: p.lineTo(x2-3,y2+4); p.lineTo(x2+3,y2+4)
            p.close(); c.drawPath(p, fill=1, stroke=0)
        if self.kind == 'architecture':
            bw=(WIDTH-32)/3; bh=42; gap=16
            labels=['Accepted objective<br/>and human authority','GLOBAL + PLAN<br/>and selected memory','Agent 0<br/>coordinate bounded work','Host tools and<br/>authorized workers','Changes and<br/>original evidence','Agent X records<br/>Agent Z reviews','Agent 0 / user<br/>accept or choose next action','TASKS + focus<br/>and checkpoint','Next turn: reload scope<br/>and check freshness']
            positions=[(0,134),(bw+gap,134),(2*(bw+gap),134),(2*(bw+gap),72),(bw+gap,72),(0,72),(0,10),(bw+gap,10),(2*(bw+gap),10)]
            for i,((x,y),label) in enumerate(zip(positions,labels)):box(x,y,bw,bh,label,i==2)
            for (x1,y1),(x2,y2) in zip(positions,positions[1:]):
                if y1==y2:
                    arrow(x1+bw if x2>x1 else x1,y1+bh/2,x2 if x2>x1 else x2+bw,y2+bh/2)
                else: arrow(x1+bw/2,y1,x2+bw/2,y2+bh)
        else:
            labels=['Define<br/>scope','Assign<br/>owner','Execute<br/>with tools','Return<br/>evidence','Review<br/>and accept','Save<br/>next state']
            gap=10; bw=(WIDTH-5*gap)/6
            for i,label in enumerate(labels):
                x=i*(bw+gap);box(x,18,bw,45,label,i==4)
                if i<5:arrow(x+bw,40,x+bw+gap,40)


@lru_cache(maxsize=8)
def image_data(path):
    # Optimize only the embedded PDF representation. Source artwork stays intact.
    with PILImage.open(path) as img:
        img=img.convert('RGB')
        img.thumbnail((1950, 1950), PILImage.Resampling.LANCZOS)
        data=BytesIO(); img.save(data, format='JPEG', quality=78, optimize=True)
        return data.getvalue(), img.size


class LinkedImage(Image):
    def __init__(self, path, url, width=WIDTH):
        data, size=image_data(str(path))
        super().__init__(BytesIO(data), width=width, height=width*size[1]/size[0])
        self.url=url
    def draw(self):
        super().draw()
        self.canv.linkURL(self.url, (0,0,self.drawWidth,self.drawHeight), relative=1, thickness=0)


def table(lines):
    rows=[[x.strip() for x in line.strip().strip('|').split('|')] for line in lines]
    rows=[row for row in rows if not all(re.fullmatch(r'[: -]+',s) for s in row)]
    n=len(rows[0])
    if any(len(row)!=n for row in rows):raise ValueError('Inconsistent Markdown table')
    ratios={2:[.36,.64],3:[.25,.36,.39]}.get(n,[1/n]*n)
    t=Table([[para(x,'th' if i==0 else 'cell') for x in row] for i,row in enumerate(rows)],colWidths=[WIDTH*r for r in ratios],repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,LIGHT]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,-1),(-1,-1),.5,RULE)]))
    return [Spacer(1,10),t,Spacer(1,14)]


def content(text, source, kind='body'):
    lines=text.splitlines();result=[];i=0;pending_anchor=None
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        anchor=re.fullmatch(r'<a id="([\w-]+)"></a>',line)
        if anchor:pending_anchor=anchor[1];i+=1;continue
        if line=='<!-- pagebreak -->':result.append(PageBreak());i+=1;continue
        if line.startswith('### '):result.append(para(line[4:],'h2'));i+=1;continue
        im=re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)',line)
        if im:
            path=(source.parent/im[2]).resolve()
            if path.parent != (source.parent.parent / 'Infographics').resolve():
                raise ValueError('Figure must be in MEDIA/Infographics')
            url='https://raw.githubusercontent.com/WayneTechLab/dotSYSTEMX/v1.8.3-alpha.1/.SYSTEMX/MEDIA/'+path.name
            result.append(LinkedImage(path,url));i+=1;continue
        if line.startswith('```'):
            language=line[3:];code=[];i+=1
            while i<len(lines) and not lines[i].startswith('```'):code.append(lines[i]);i+=1
            i+=1
            if language=='mermaid':
                if 'flowchart TB' in code:result.append(Diagram('architecture'))
                elif 'flowchart LR' in code:result.append(Diagram('sequence'))
                else:raise ValueError('Unsupported diagram; add an explicit renderer')
            else:result.extend([Preformatted('\n'.join(code),STYLES['code'],maxLineLength=94,splitChars=' /',newLineChars='  ')])
            continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):rows.append(lines[i]);i+=1
            result.extend(table(rows));continue
        fig=re.match(r'^\*Fig\. (\d+)\. (.*)\*$',line)
        if fig:
            p=para('Fig. '+fig[1]+'. '+fig[2],'caption');p.figure_key='figure'+fig[1];p.figure_label='Fig. '+fig[1]+'. '+fig[2].split('. ')[0]
            # Keep the caption with the preceding illustration.
            if result and isinstance(result[-1],(Diagram,Image)):result[-1]=KeepTogether([result[-1],p])
            else:result.append(p)
            i+=1;continue
        if re.match(r'^\d+\. ',line):block=[line];i+=1
        else:
            block=[line];i+=1
            while i<len(lines) and lines[i].strip() and not lines[i].startswith(('### ','```','|','<!--','<a ','![')):
                block.append(lines[i].strip());i+=1
        p=para(' '.join(block),kind)
        if pending_anchor:
            p=Paragraph('<a name="'+pending_anchor+'"/>'+p.text,p.style)
            pending_anchor=None
        result.append(p)
    return result


class PaperDoc(BaseDocTemplate):
    def afterFlowable(self, item):
        if hasattr(item,'section_key'):
            self.canv.bookmarkPage(item.section_key)
            self.canv.addOutlineEntry(item.getPlainText(),item.section_key,0,False)
            self.notify('TOCEntry',(0,item.getPlainText(),self.page,item.section_key))
        if hasattr(item,'figure_key'):
            self.canv.bookmarkPage(item.figure_key)
            self.notify('FigureEntry',(0,item.figure_label,self.page,item.figure_key))
        if hasattr(item,'bookmark_key'):self.canv.bookmarkPage(item.bookmark_key)


class FigureContents(TableOfContents):
    def notify(self,kind,stuff):
        if kind=='FigureEntry':self.addEntry(*stuff)


def navigation(c,doc):
    c.saveState()
    c.setFillColor(MUTED);c.setFont(FONT,12)
    c.drawRightString(W-MARGIN,H-36,CONFIG['runningAuthor']+' '+str(doc.page))
    c.setFont('Helvetica',7.5);c.drawString(MARGIN,H-36,CONFIG['product']+'  |  RESEARCH WHITE PAPER')
    c.setStrokeColor(RULE);c.line(MARGIN,53,W-MARGIN,53)
    c.setFont('Helvetica',7.4)
    c.drawString(MARGIN,40,CONFIG['productCredit'])
    c.drawRightString(W-MARGIN,40,'EDITION '+CONFIG['edition']+'  |  '+CONFIG['date'])
    x=MARGIN
    for item in CONFIG['links']:
        label=item['label'];width=pdfmetrics.stringWidth(label,'Helvetica',7.4)
        c.setFillColor(TEAL);c.drawString(x,26,label);c.linkURL(item['url'],(x,24,x+width,34),relative=0,thickness=0);x+=width+15
    c.setFillColor(TEAL);c.drawRightString(W-MARGIN,26,'Contents')
    c.linkRect('', 'contents', (W-MARGIN-34,24,W-MARGIN,34),relative=0,thickness=0)
    c.restoreState()


def cover(c,doc):
    c.saveState();c.setFillColor(NAVY);c.rect(0,H-18,W,18,fill=1,stroke=0)
    c.setFillColor(TEAL);c.rect(MARGIN,94,WIDTH,4,fill=1,stroke=0)
    c.setFont('Helvetica',8);c.setFillColor(MUTED)
    c.drawString(MARGIN,76,'PUBLIC TECHNICAL WHITE PAPER')
    c.drawRightString(W-MARGIN,76,'ALPHA  |  USE AT YOUR OWN RISK')
    c.restoreState()


def build(source,output):
    text=source.read_text(encoding='utf-8')
    sections=re.split(r'^## ',text,flags=re.M)[1:]
    front=sections[0];sections=sections[1:]
    doc=PaperDoc(str(output),pagesize=letter,leftMargin=MARGIN,rightMargin=MARGIN,topMargin=MARGIN,bottomMargin=MARGIN,title=CONFIG['product']+': '+CONFIG['title'],author=CONFIG['author']+' | '+CONFIG['publisher'],subject=CONFIG['subtitle']+'; '+CONFIG['layout'],pageCompression=1)
    frame=Frame(MARGIN,MARGIN,WIDTH,H-2*MARGIN,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id='cover',frames=[frame],onPage=cover,autoNextPageTemplate='body'),PageTemplate(id='body',frames=[frame],onPage=navigation)])
    title_style=ParagraphStyle('coverTitle',fontName=BOLD,fontSize=30,leading=36,textColor=NAVY,spaceAfter=18)
    logo=ROOT/'docs/assets/systemx-logo.png'
    story=[Spacer(1,20),LinkedImage(logo,CONFIG['links'][2]['url'],width=WIDTH),Spacer(1,10),Paragraph(escape(CONFIG['title']),title_style),para(CONFIG['subtitle'],'front'),Spacer(1,12),para('RESEARCH EDITION '+CONFIG['edition']+'  |  '+CONFIG['date'],'small'),para('**'+CONFIG['author']+'**','front'),para(CONFIG['productCredit'],'front')]
    for item in CONFIG['links']:story.append(para(item['role']+': ['+item['label']+']('+item['url']+')','small'))
    story.extend([Spacer(1,13),para('Technical baseline: v'+CONFIG['technicalBaseline']+'<br/>Full implementation reference, evidence boundaries and visual workflow atlas.','small'),PageBreak()])
    h=para('Abstract and publication context','h1');h.bookmark_key='abstract';story.append(h)
    abstract=front.split('### Abstract\n',1)[1]
    story.extend(content(abstract,source,kind='front'))
    story.extend([para('Keywords','h2'),para('Agentic software development; persistent context; task coordination; human oversight; event records; repeatable review; versioned templates.','front'),PageBreak()])
    h=para('Contents','h1');h.bookmark_key='contents';story.append(h)
    story.append(para('Click a section title or page number to navigate. Each body-page footer links back here. External links open in your PDF viewer or browser.','small'))
    toc=TableOfContents();toc.levelStyles=[ParagraphStyle('toc',fontName=FONT,fontSize=11,leading=15,spaceBefore=3,spaceAfter=3,rightIndent=30)]
    story.append(toc)
    story.extend([PageBreak(),para('Figures and reading routes','h1')])
    figures=FigureContents();figures.levelStyles=[ParagraphStyle('figlist',fontName=FONT,fontSize=11,leading=16,spaceBefore=7,spaceAfter=7,rightIndent=30)]
    story.append(figures)
    story.extend([Spacer(1,15),para('Choose a reading route','h2')])
    story.extend(table(['| Reader | Suggested route |','| --- | --- |','| Founder / project lead | Purpose and boundaries: chapters 1-3, 11-14. Visual workflows: appendix F. |','| Agent operator / engineer | Coordination: chapters 15-25. Verified walkthrough: 26-27. |','| Reviewer / integrator | Evidence and operating limits: 13, 29. Exact contracts and 100 questions: appendices A-B. |','| Implementer | Command families, file inventory and module boundaries: appendices C-E. |']))
    story.append(para('Format: MLA-style research body and citations, with branded front matter and compact technical displays. See Publication and research notes for the explicit adaptations.','small'))
    for index,section in enumerate(sections):
        title,body=section.split('\n',1);heading=para(title,'h1');heading.section_key='section'+str(index)
        story.extend([PageBreak(),heading]);story.extend(content(body,source,'works' if title=='Works Cited' else 'body'))
    doc.multiBuild(story)



def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--edition',choices=('1.0','1.1','1.2'),default='1.2')
    p.add_argument('--template',type=Path,default=Path(__file__).with_name('publication-template.json'))
    p.add_argument('--source',type=Path)
    p.add_argument('--output',type=Path)
    p.add_argument('--font-dir',type=Path)
    args=p.parse_args()
    if args.edition in ('1.0','1.1'):
        if not args.source or not args.output:
            p.error('Legacy editions require --source from an archived release and a separate --output')
        if args.font_dir:p.error('Legacy editions do not support --font-dir')
        return subprocess.call([sys.executable,str(Path(__file__).with_name('build_white_paper_legacy.py')),'--edition',args.edition,'--source',str(args.source.resolve()),'--output',str(args.output.expanduser())])
    config=json.loads(args.template.read_text(encoding='utf-8'))
    configure(config,args.font_dir)
    source=(args.source or ROOT/('.SYSTEMX/MEDIA/White-Paper/SYSTEMX-White-Paper-v'+config['edition']+'.md')).resolve()
    requested_output=(args.output or source.with_suffix('.pdf')).expanduser()
    # Resolve the directory, not the final file: resolving an existing PDF
    # symlink would turn the atomic replacement into a write to its target.
    output=requested_output.parent.resolve()/requested_output.name
    if output==source:raise ValueError('Output must not replace the source')
    if output.is_symlink():raise ValueError('Output must not be a symlink')
    with tempfile.TemporaryDirectory(prefix='systemx-paper-', dir=output.parent) as temp:
        draft=Path(temp)/output.name
        build(source,draft)
        if output.is_symlink():raise ValueError('Output must not be a symlink')
        draft.replace(output)
    print(json.dumps({'output':str(output),'bytes':output.stat().st_size,'font':FONT,'edition':CONFIG['edition']}))
    return 0


if __name__=='__main__':raise SystemExit(main())
