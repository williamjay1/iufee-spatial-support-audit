"""Render final PDF pages and layout contact sheets for human visual inspection."""
from pathlib import Path
import fitz
from PIL import Image, ImageDraw

ROOT=Path(r'D:\MLWork\IUFEE_revision_20261005')
for stem, folder in [('IUFEE_redeveloped','render_main'),('IUFEE_supplement','render_supplement'),('Revision_memorandum','render_memorandum')]:
    out=ROOT/'temp'/folder
    out.mkdir(parents=True,exist_ok=True)
    doc=fitz.open(ROOT/'manuscript'/f'{stem}.pdf')
    for i,page in enumerate(doc):
        page.get_pixmap(matrix=fitz.Matrix(1.7,1.7)).save(out/f'page{i+1}.png')
    if folder in ['render_supplement','render_memorandum']:
        for j in range(0,len(doc),2):
            sheet=Image.new('RGB',(1500,1110),'#dedede')
            draw=ImageDraw.Draw(sheet)
            for col,i in enumerate(range(j,min(j+2,len(doc)))):
                im=Image.open(out/f'page{i+1}.png')
                im.thumbnail((735,1060))
                sheet.paste(im,(col*750+7,28))
                draw.text((col*750+12,7),f'{stem} page {i+1}',fill='black')
            sheet.save(out/f'contact_{j//2+1}.png')
    print(f'{stem}: {len(doc)} pages rendered.')
