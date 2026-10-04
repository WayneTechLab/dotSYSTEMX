#!/usr/bin/env python3
"""Typeset the white paper Markdown. Optional maintainer dependency: ReportLab.

Run from any directory: python docs/media/build_white_paper.py
This builder is documentation tooling, not part of the portable runtime.
"""
from pathlib import Path
import re
from html import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak,
    Table, TableStyle, Flowable, Preformatted, KeepTogether,
)

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / '.SYSTEMX/MEDIA/SYSTEMX-White-Paper-v1.0.md'
OUTPUT = SOURCE.with_suffix('.pdf')
W, H = A4
MARGIN = 48
WIDTH = W - 2 * MARGIN
NAVY = colors.HexColor('#132b3b')
TEAL = colors.HexColor('#007e87')
MUTED = colors.HexColor('#536773')
LIGHT = colors.HexColor('#edf5f5')
RULE = colors.HexColor('#d6e2e6')
BODY = colors.HexColor('#233744')

STYLES = {
    'body': ParagraphStyle('body',fontName='Helvetica',fontSize=10.2,leading=14.6,textColor=BODY,spaceAfter=10),
    'small': ParagraphStyle('small',fontName='Helvetica',fontSize=8.5,leading=12,textColor=MUTED,spaceAfter=7),
    'h1': ParagraphStyle('h1',fontName='Helvetica-Bold',fontSize=23,leading=28,textColor=NAVY,spaceAfter=17,keepWithNext=True),
    'h2': ParagraphStyle('h2',fontName='Helvetica-Bold',fontSize=12.2,leading=16,textColor=TEAL,spaceBefore=7,spaceAfter=8,keepWithNext=True),
    'cell': ParagraphStyle('cell',fontName='Helvetica',fontSize=8.5,leading=11.7,textColor=BODY,spaceAfter=0),
    'th': ParagraphStyle('th',fontName='Helvetica-Bold',fontSize=8.5,leading=11.7,textColor=colors.white,spaceAfter=0),
    'code': ParagraphStyle('code',fontName='Courier',fontSize=8,leading=11.7,textColor=NAVY,backColor=LIGHT,borderPadding=10,spaceBefore=5,spaceAfter=14),
}

def inline(text):
    out=escape(text,quote=False).replace('&lt;br/&gt;', '<br/>')
    out=re.sub(r'\[([^\]]+)\]\(([^\s)]+)\)',lambda m:'<link href="'+escape(m.group(2),quote=True)+'" color="#007e87">'+m.group(1)+'</link>',out)
    out=re.sub(r'`([^`]+)`',r'<font name="Courier" size="8.8">\1</font>',out)
    out=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',out)
    return out

def para(text,kind='body'):
    return Paragraph(inline(text),STYLES[kind])

class Diagram(Flowable):
    def __init__(self,kind):
        super().__init__();self.kind=kind;self.width=WIDTH;self.height=164 if kind=='architecture' else 72
    def draw(self):
        c=self.canv
        def box(x,y,w,h,label,accent=False):
            c.setFillColor(TEAL if accent else LIGHT);c.setStrokeColor(TEAL if accent else RULE)
            c.roundRect(x,y,w,h,5,stroke=1,fill=1)
            style=ParagraphStyle('box',fontName='Helvetica-Bold' if accent else 'Helvetica',fontSize=8.2,leading=10.6,textColor=colors.white if accent else NAVY,alignment=1)
            p=Paragraph(label,style);_,ph=p.wrap(w-12,h-6);p.drawOn(c,x+6,y+(h-ph)/2)
        def arrow(x1,y1,x2,y2):
            c.setStrokeColor(TEAL);c.setFillColor(TEAL);c.setLineWidth(1)
            c.line(x1,y1,x2,y2)
            p=c.beginPath();p.moveTo(x2,y2)
            if x2>x1:p.lineTo(x2-4,y2+3);p.lineTo(x2-4,y2-3)
            elif x2<x1:p.lineTo(x2+4,y2+3);p.lineTo(x2+4,y2-3)
            elif y2<y1:p.lineTo(x2-3,y2+4);p.lineTo(x2+3,y2+4)
            else:p.lineTo(x2-3,y2-4);p.lineTo(x2+3,y2-4)
            p.close();c.drawPath(p,fill=1,stroke=0)
        if self.kind=='architecture':
            bw=(WIDTH-32)/3;gap=16;bh=37;ys=[119,62,5]
            labels=[('Accepted objective<br/>and human authority','GLOBAL + PLAN<br/>and selected memory','Agent 0<br/>coordinate bounded work'),('Changes and<br/>original evidence','Host tools and<br/>authorized workers',''),('Agent X records<br/>Agent Z reviews','Agent 0 / user<br/>accept or choose next action','TASKS + focus<br/>and checkpoint')]
            positions=[(0,ys[0],labels[0][0]),(bw+gap,ys[0],labels[0][1]),(2*(bw+gap),ys[0],labels[0][2]),(2*(bw+gap),ys[1],'Host tools and<br/>authorized workers'),(bw+gap,ys[1],'Changes and<br/>original evidence'),(0,ys[1],'Agent X records<br/>Agent Z reviews'),(0,ys[2],'Agent 0 / user<br/>accept or choose next action'),(bw+gap,ys[2],'TASKS + focus<br/>and checkpoint')]
            for i,(x,y,l) in enumerate(positions):box(x,y,bw,bh,l,i==2)
            arrow(bw,ys[0]+bh/2,bw+gap,ys[0]+bh/2);arrow(2*bw+gap,ys[0]+bh/2,2*(bw+gap),ys[0]+bh/2)
            arrow(2*(bw+gap)+bw/2,ys[0],2*(bw+gap)+bw/2,ys[1]+bh)
            arrow(2*(bw+gap),ys[1]+bh/2,2*bw+gap,ys[1]+bh/2);arrow(bw+gap,ys[1]+bh/2,bw,ys[1]+bh/2)
            arrow(bw/2,ys[1],bw/2,ys[2]+bh);arrow(bw,ys[2]+bh/2,bw+gap,ys[2]+bh/2)
            box(2*(bw+gap),ys[2],bw,bh,'Next turn: reload scope<br/>and check freshness')
            arrow(2*bw+gap,ys[2]+bh/2,2*(bw+gap),ys[2]+bh/2)
        else:
            labels=['Define<br/>scope','Assign<br/>owner','Execute<br/>with tools','Return<br/>evidence','Review<br/>and accept','Save<br/>next state'];gap=10;bw=(WIDTH-gap*5)/6
            for i,label in enumerate(labels):
                x=i*(bw+gap);box(x,20,bw,42,label,i==4)
                if i<5:arrow(x+bw,41,x+bw+gap,41)

def table(lines):
    rows=[[x.strip() for x in line.strip().strip('|').split('|')] for line in lines]
    rows=[row for row in rows if not all(re.fullmatch(r'[: -]+',s) for s in row)]
    n=len(rows[0])
    if n==2:widths=[WIDTH*.34,WIDTH*.66]
    elif n==3:widths=[WIDTH*.23,WIDTH*.38,WIDTH*.39]
    else:widths=[WIDTH/n]*n
    cells=[[para(x,'th' if i==0 else 'cell') for x in row] for i,row in enumerate(rows)]
    t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,LIGHT]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,-1),(-1,-1),.5,RULE)]))
    return [t,Spacer(1,12)]

def content(text,refs=False):
    lines=text.splitlines();result=[];i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line.startswith('### '):result.append(para(line[4:],'h2'));i+=1;continue
        if line.startswith('```'):
            kind=line[3:];code=[];i+=1
            while i<len(lines) and not lines[i].startswith('```'):code.append(lines[i]);i+=1
            i+=1
            if kind=='mermaid':result.extend([Diagram('architecture' if 'flowchart TB' in code else 'sequence'),Spacer(1,12)])
            else:result.append(Preformatted('\n'.join(code),STYLES['code']))
            continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):rows.append(lines[i]);i+=1
            result.extend(table(rows));continue
        if re.match(r'^\d+\. ',line):
            result.append(para(line,'small' if refs else 'body'));i+=1;continue
        block=[line];i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].startswith(('### ','```','|')):block.append(lines[i].strip());i+=1
        result.append(para(' '.join(block),'small' if refs else 'body'))
    return result

class PaperDoc(BaseDocTemplate):
    def afterFlowable(self,flowable):
        if hasattr(flowable,'section_key'):
            self.canv.bookmarkPage(flowable.section_key)
            self.canv.addOutlineEntry(flowable.getPlainText(),flowable.section_key,0,False)

def header_footer(c,doc):
    if doc.page==1:return
    c.saveState();c.setFillColor(NAVY);c.setFont('Helvetica-Bold',9);c.drawString(MARGIN,H-30,'.SYSTEMX')
    c.setFillColor(MUTED);c.setFont('Helvetica',8);c.drawRightString(W-MARGIN,H-30,'WHITE PAPER  /  EDITION 1.0')
    c.setStrokeColor(RULE);c.setLineWidth(.6);c.line(MARGIN,39,W-MARGIN,39)
    c.setFont('Helvetica',7.5);c.drawString(MARGIN,26,'4 OCTOBER 2026  |  ALPHA FORMAT  |  BASELINE v1.8.2-alpha.1')
    c.drawRightString(W-MARGIN,26,str(doc.page));c.restoreState()

def cover(c,doc):
    c.saveState();c.setFillColor(NAVY);c.rect(0,H-24,W,24,fill=1,stroke=0)
    c.setFillColor(TEAL);c.rect(MARGIN,H-121,5,55,fill=1,stroke=0)
    c.setFillColor(NAVY);c.setFont('Helvetica-Bold',48);c.drawString(MARGIN+18,H-108,'.SYSTEMX')
    c.setFillColor(MUTED);c.setFont('Helvetica-Bold',10);c.drawString(MARGIN,H-158,'WHITE PAPER  /  EDITION 1.0')
    c.setStrokeColor(RULE);c.line(MARGIN,57,W-MARGIN,57)
    c.setFont('Helvetica',8);c.drawString(MARGIN,39,'PUBLIC DISCUSSION PAPER  |  4 OCTOBER 2026')
    c.drawRightString(W-MARGIN,39,'PROJECT MEMORY  /  COORDINATION  /  EVIDENCE');c.restoreState()

def build():
    text=SOURCE.read_text(encoding='utf-8')
    parts=re.split(r'^## ',text,flags=re.M)[1:]
    front=parts[0];sections=parts[1:]
    doc=PaperDoc(str(OUTPUT),pagesize=A4,leftMargin=MARGIN,rightMargin=MARGIN,topMargin=58,bottomMargin=54,title='.SYSTEMX: Portable Project Memory for Agentic Work',author='.SYSTEMX Project',subject='Architecture, evidence, lifecycle and evaluation of the .SYSTEMX alpha format',pageCompression=1)
    frame=Frame(MARGIN,54,WIDTH,H-112,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id='cover',frames=[frame],onPage=cover,autoNextPageTemplate='body'),PageTemplate(id='body',frames=[frame],onPage=header_footer)])
    story=[Spacer(1,123),para('Portable project memory<br/>for agentic work','h1'),para('A coordination format for people, AI assistants and the tools that execute their work.'),para('EDITION 1.0  |  4 OCTOBER 2026<br/>Technical baseline: v1.8.2-alpha.1','small'),Spacer(1,12)]
    abstract=front.split('### Abstract\n',1)[1]
    story.extend(content('### Abstract\n'+abstract))
    story.extend([PageBreak(),para('Reading this paper','h1'),para('Start with the executive perspective, then follow the records, roles and operating boundaries. The final sections address measurement, adoption and the evidence behind the claims.')])
    for index,section in enumerate(sections):
        title=section.split('\n',1)[0]
        story.append(Paragraph('<link href="#section'+str(index)+'" color="#007e87">'+escape(title)+'</link>',ParagraphStyle('toc',parent=STYLES['body'],spaceAfter=12,fontSize=10.5)))
    story.extend([Spacer(1,13),para('Interpretation guide','h2'),para('Implemented features are identified through pinned source references. Worked examples illustrate the method. Efficiency benefits are hypotheses for evaluation. Proposed extensions are separate from the current implementation.')])
    for index,section in enumerate(sections):
        title,body=section.split('\n',1);heading=para(title,'h1');heading.section_key='section'+str(index)
        story.extend([PageBreak(),heading]);story.extend(content(body,refs=title.startswith('References')))
    doc.build(story)
    print(OUTPUT)

if __name__=='__main__':build()
