#!/usr/bin/env python3
"""Create a spoken-text companion; audio synthesis is a separate optional step.

Keeps the complete prose, questions, code and inventory; converts tables into
header/value sentences and diagrams into ordered labels. Omits Markdown markup,
long link destinations and inline numeric reference markers. No network access.
"""
from pathlib import Path
import argparse
import re

def spoken(source):
    lines=source.splitlines(); result=[]; index=0
    def clean(s):
        s=re.sub(r'\[([^\]]+)\]\([^)]+\)',r'\1',s)
        s=re.sub(r'\[(?:\d+(?:[, -]+\d+)*)\]','',s)
        s=s.replace('**','').replace('`','').replace('.SYSTEMXP','Dot System X P').replace('.SYSTEMX','Dot System X').replace('.systemx','lowercase dot system x')
        s=s.replace('Agent 0','Agent Zero').replace('->',' leads to ').replace(' / ',' slash ')
        # Native speech engines may interpret angle-bracket placeholders as markup.
        # Verbalize them so a path such as <version> cannot truncate the reading.
        s=s.replace('<',' less than ').replace('>',' greater than ').replace('&',' and ')
        return s
    while index<len(lines):
        line=lines[index]
        if line.startswith('```'):
            kind=line[3:];block=[];index+=1
            while index<len(lines) and not lines[index].startswith('```'):
                block.append(lines[index]);index+=1
            if kind=='mermaid':
                labels=re.findall(r'\["([^"]+)"\]','\n'.join(block))
                result.append('Diagram, in order. '+'. Then, '.join(clean(x) for x in labels)+'.')
            else:result.append('Code or layout example.\n'+clean('\n'.join(block))+'\nEnd of example.')
            index+=1;continue
        if line.startswith('|'):
            rows=[]
            while index<len(lines) and lines[index].startswith('|'):
                cells=[x.strip() for x in lines[index].strip('|').split('|')]
                if not all(re.fullmatch(r'[: -]+',x) for x in cells):rows.append(cells)
                index+=1
            headers=rows[0]
            result.append('Table.')
            for row in rows[1:]:result.append('. '.join(clean(h)+': '+clean(v) for h,v in zip(headers,row))+'.')
            result.append('End of table.');continue
        result.append(clean(re.sub(r'^#{1,6}\s+','',line)))
        index+=1
    return ('Dot System X. Expanded white paper, edition 1.1. This is a synthetic voice reading. '
            'Tables are read by their column labels; diagrams are described in order. '
            'Long web addresses and inline reference numbers are omitted. The PDF retains the exact formatting.\n\n'
            +'\n'.join(result)+'\n\nEnd of the expanded white paper.\n')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path)
    parser.add_argument('--source',type=Path,required=True,help='Edition 1.1 Markdown from its archived release')
    args=parser.parse_args()
    source=args.source.resolve()
    if source==args.output.resolve():parser.error('Output must not replace source')
    if not re.search(r'^Edition 1\.1 \|',source.read_text(encoding='utf-8'),re.M):
        parser.error('This historical narration format requires edition 1.1')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(spoken(source.read_text(encoding='utf-8')),encoding='utf-8')
    print(args.output)
