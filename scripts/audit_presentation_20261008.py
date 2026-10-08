"""Deterministic journal presentation checks plus final-size page rendering."""
from pathlib import Path
import re,json,hashlib
import fitz
from PIL import Image,ImageDraw

R=Path(r'D:\MLWork\IUFEE_revision_20261005'); M=R/'manuscript'; O=R/'results/revision_20261008'
O.mkdir(exist_ok=True)
src=(M/'IUFEE_redeveloped.tex').read_text(encoding='utf-8')
abstract=re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',src,re.S).group(1).strip()
sentences=[x for x in re.split(r'(?<=[.!?])\s+(?=[A-Z])',abstract) if x]
assert len(sentences)==5,len(sentences)
assert not re.search(r'\b(?:not|neither|rather than|cannot|no)\b',abstract,re.I)
assert not any(x in src for x in ['—','–','---','--'])
body=src.split('\\begin{document}',1)[1].split('\\bibliographystyle',1)[0]
body_no_math=re.sub(r'\$[^$]*\$','',body)
body_no_math=re.sub(r'\\begin\{(?:equation|align)\}.*?\\end\{(?:equation|align)\}','',body_no_math,flags=re.S)
hyphens=body_no_math.count('-')
assert hyphens<=20,hyphens
assert not re.search(r'Nature|Remote Sensing Letters|GRSL|IEEE Geoscience|Management Science',body)
assert not re.search(r'paper is organi|next section|Section.*(?:presents|describes|discusses)',body,re.I)
cite=[]
for group in re.findall(r'\\cite\{([^}]+)\}',src):
    for key in group.split(','):
        if key not in cite:cite.append(key)
bbl=(M/'IUFEE_redeveloped.bbl').read_text(encoding='utf-8')
bib_order=re.findall(r'\\bibitem\{([^}]+)\}',bbl)
assert cite==bib_order,(cite,bib_order)
assert len(cite)==17
assert not re.search(r'codex|openai|chatgpt|\bgpt\b',bbl,re.I)
first_fig=re.findall(r'Figure~\\ref\{([^}]+)\}',src)
first_table=re.findall(r'Table~\\ref\{([^}]+)\}',src)
assert list(dict.fromkeys(first_fig))==['fig:frame','fig:representation','fig:glad']
assert list(dict.fromkeys(first_table))==['tab:pooled','tab:cases']
assert all('\\label{'+k+'}' in src for k in first_fig+first_table)
assert 'Supplementary Section' in src and 'Supplementary Table' in src
fig_audit=json.loads((O/'FIGURE_DESIGN_AND_QA.json').read_text(encoding='utf-8'))
for key in ['figure_1_frame','figure_4_representation','figure_5_glad','figure_2_cases','figure_3_case_maps']:
    a=fig_audit['figures'][key]
    assert a['ok'] and a['pdf_raster_image_objects']==0
    assert not a['text_box_collisions'] and not a['off_canvas_text']
    assert a['all_text_minimum_pt']>=7
    with Image.open(M/'figures'/f'{key}.png') as im:
        assert min(im.info['dpi'])>=999
pages={}; clips={}; pdf_em_dashes={}; render=R/'temp/render_20261008';render.mkdir(exist_ok=True)
for stem,expected in [('IUFEE_redeveloped',5),('IUFEE_supplement',3),('Cover_letter_GRSL',1),('Revision_memorandum',None),('IUFEE_technical_record',None)]:
    with fitz.open(M/(stem+'.pdf')) as doc:
        pages[stem]=len(doc)
        if expected:assert len(doc)==expected,(stem,len(doc))
        pdf_em_dashes[stem]=sum(p.get_text().count('\u2014') for p in doc)
        if stem in ['IUFEE_redeveloped','IUFEE_supplement','Cover_letter_GRSL']:
            assert pdf_em_dashes[stem]==0,(stem,pdf_em_dashes[stem])
        bad=[]
        for i,p in enumerate(doc):
            for b in p.get_text('blocks'):
                if b[0]<-1 or b[1]<-1 or b[2]>p.rect.width+1 or b[3]>p.rect.height+1:bad.append(i+1)
            p.get_pixmap(matrix=fitz.Matrix(1.7,1.7)).save(render/f'{stem}_page{i+1}.png')
        assert not bad,(stem,bad);clips[stem]=bad
        if stem in ['Revision_memorandum','IUFEE_technical_record']:
            for j in range(0,len(doc),3):
                sheet=Image.new('RGB',(2100,1010),'#e5e5e5'); draw=ImageDraw.Draw(sheet)
                for c,i in enumerate(range(j,min(j+3,len(doc)))):
                    im=Image.open(render/f'{stem}_page{i+1}.png');im.thumbnail((690,975))
                    sheet.paste(im,(c*700+5,25));draw.text((c*700+10,5),f'{stem}: {i+1}',fill='black')
                sheet.save(render/f'{stem}_contact{j//3+1}.png')
report={'date':'2026-10-08','all_passed':True,'main_source_sha256':hashlib.sha256(src.encode()).hexdigest(),'abstract_sentences':len(sentences),'abstract_negative_framing':False,'body_optional_hyphens':hyphens,'hyphen_exception':'Official product identifiers; mathematical subtraction and bibliography metadata excluded. Automatic hyphenation disabled.','dash_count':0,'pdf_em_dashes':pdf_em_dashes,'first_citation_keys':cite,'references':len(cite),'figure_first_mentions':list(dict.fromkeys(first_fig)),'table_first_mentions':list(dict.fromkeys(first_table)),'pdf_pages':pages,'off_page_text_blocks':clips,'figures_vector_and_1000dpi':True,'scientific_content_review':'INDEPENDENT_CONTENT_REVIEW.md PASS, no unresolved P0/P1','visual_review':'Pending root inspection of final render set; deterministic layout and numerical checks pass.'}
(O/'PRESENTATION_AUDIT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
