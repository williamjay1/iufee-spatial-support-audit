from pathlib import Path
import subprocess,sys,json
R=Path(r'D:\MLWork\IUFEE_revision_20261005');M=R/'manuscript'
BIN=Path(r'C:\Users\Administrator\AppData\Local\Programs\MiKTeX\miktex\bin\x64')
stems=sys.argv[1:] or ['IUFEE_redeveloped','IUFEE_supplement','Revision_memorandum']
for stem in stems:
    commands=[[str(BIN/'pdflatex.exe'),'-interaction=nonstopmode','-halt-on-error',stem+'.tex']]
    if stem=='IUFEE_redeveloped':commands += [[str(BIN/'bibtex.exe'),stem]]
    commands += [[str(BIN/'pdflatex.exe'),'-interaction=nonstopmode','-halt-on-error',stem+'.tex']]*2
    for j,cmd in enumerate(commands):
        p=subprocess.run(cmd,cwd=M,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=180)
        (R/f'temp/{stem}_compile_20261007_{j}.txt').write_text(p.stdout+'\n'+p.stderr,encoding='utf-8')
        if p.returncode:
            print(p.stdout[-5000:]);raise RuntimeError((stem,j,p.returncode))
    log=(M/(stem+'.log')).read_text(encoding='utf-8',errors='replace')
    issues=[line for line in log.splitlines() if line.startswith('!') or 'Overfull' in line or 'undefined' in line.lower()]
    print(json.dumps({'document':stem,'critical':issues}))
