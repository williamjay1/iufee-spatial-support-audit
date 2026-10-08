"""Build the journal submission bundle: main manuscript PDF + standalone LaTeX source archive."""
from pathlib import Path
import hashlib, shutil, subprocess, zipfile, json

R = Path(r'D:\MLWork\IUFEE_revision_20261005')
M = R / 'manuscript'
SUB = R / 'submission'
SUB.mkdir(exist_ok=True)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

# 1. main manuscript PDF (no supplementary material embedded)
main_pdf = SUB / 'IUFEE_GRSL_Main_Manuscript.pdf'
shutil.copy2(M / 'IUFEE_redeveloped.pdf', main_pdf)

# 2. LaTeX source archive: only main-manuscript material
members = [
    (M / 'IUFEE_redeveloped.tex', 'IUFEE_redeveloped.tex'),
    (M / 'references.bib', 'references.bib'),
    (M / 'revision_numbers.tex', 'revision_numbers.tex'),
    (M / 'IUFEE_redeveloped.bbl', 'IUFEE_redeveloped.bbl'),
    (M / 'IEEEtran.cls', 'IEEEtran.cls'),
    (M / 'IEEEtran.bst', 'IEEEtran.bst'),
    (M / 'figures/figure_1_frame.pdf', 'figures/figure_1_frame.pdf'),
    (M / 'figures/figure_1_frame.svg', 'figures/figure_1_frame.svg'),
    (M / 'figures/figure_1_frame.png', 'figures/figure_1_frame.png'),
    (M / 'figures/figure_4_representation.pdf', 'figures/figure_4_representation.pdf'),
    (M / 'figures/figure_4_representation.svg', 'figures/figure_4_representation.svg'),
    (M / 'figures/figure_4_representation.png', 'figures/figure_4_representation.png'),
    (M / 'figures/figure_5_glad.pdf', 'figures/figure_5_glad.pdf'),
    (M / 'figures/figure_5_glad.svg', 'figures/figure_5_glad.svg'),
    (M / 'figures/figure_5_glad.png', 'figures/figure_5_glad.png'),
]
for src, _ in members:
    assert src.is_file(), src
readme = SUB / 'README_compile.txt'
readme.write_text(
    'Main manuscript LaTeX source bundle\r\n'
    '===================================\r\n\r\n'
    'Contents: IUFEE_redeveloped.tex (main manuscript, 5 pages including references),\r\n'
    'references.bib, revision_numbers.tex (generated numeric macros), IUFEE_redeveloped.bbl,\r\n'
    'IEEEtran.cls and IEEEtran.bst, and the three figures used by the manuscript in PDF (used\r\n'
    'by LaTeX), SVG (editable vector) and PNG (1000 dpi) form. This bundle contains the main\r\n'
    'manuscript only; no supplementary material is included.\r\n\r\n'
    'Compile sequence (TeX Live or MiKTeX):\r\n'
    '  pdflatex IUFEE_redeveloped\r\n'
    '  bibtex   IUFEE_redeveloped\r\n'
    '  pdflatex IUFEE_redeveloped\r\n'
    '  pdflatex IUFEE_redeveloped\r\n\r\n'
    'The manuscript uses \\documentclass[journal]{IEEEtran}.\r\n', encoding='utf-8')

bundle = SUB / 'IUFEE_GRSL_Main_Manuscript_LaTeX_source.zip'
with zipfile.ZipFile(bundle, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for src, name in members:
        z.write(src, name)
    z.write(readme, 'README_compile.txt')
with zipfile.ZipFile(bundle) as z:
    assert z.testzip() is None
    names = z.namelist()
forbidden = [n for n in names if any(k in n.lower() for k in ['supplement', 'memorandum', 'technical_record', 'cover_letter', 'results/'])]
assert not forbidden, forbidden

# 3. standalone compile test from the archive
test = R / 'temp/submission_bundle_test'
if test.exists(): shutil.rmtree(test)
test.mkdir(parents=True)
with zipfile.ZipFile(bundle) as z:
    z.extractall(test)
BIN = Path(r'C:\Users\Administrator\AppData\Local\Programs\MiKTeX\miktex\bin\x64')
log = []
for cmd in [['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'IUFEE_redeveloped.tex'],
            ['bibtex', 'IUFEE_redeveloped'],
            ['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'IUFEE_redeveloped.tex'],
            ['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'IUFEE_redeveloped.tex']]:
    p = subprocess.run([str(BIN / (cmd[0] + '.exe'))] + cmd[1:], cwd=test, capture_output=True, text=True,
                       encoding='utf-8', errors='replace', timeout=300)
    assert p.returncode == 0, (cmd, p.stdout[-2000:])
    log.append(cmd[0])
tex_log = (test / 'IUFEE_redeveloped.log').read_text(encoding='utf-8', errors='replace')
critical = [l for l in tex_log.splitlines() if l.startswith('!') or 'Overfull' in l or 'undefined' in l.lower()]

import pymupdf
rebuilt = pymupdf.open(test / 'IUFEE_redeveloped.pdf')
built_pages = len(rebuilt)
built_text = '\n'.join(p.get_text() for p in rebuilt)
reference_pages_text = '\n'.join(p.get_text() for p in pymupdf.open(main_pdf))
assert built_pages == 5, built_pages
assert '0009-0007-2459-771X' in built_text and 'Zhuo Zeng, Yushi Tian, and Junjie Zhang' in built_text
assert not critical, critical
# content identity: the rebuilt PDF must match the delivered manuscript text
def norm(t): return ' '.join(t.split())
assert norm(built_text) == norm(reference_pages_text), 'rebuilt text differs from delivered manuscript'

record = {
    'main_manuscript_pdf': {'path': str(main_pdf.relative_to(R)).replace('\\', '/'), 'bytes': main_pdf.stat().st_size,
                            'pages': built_pages, 'sha256': sha(main_pdf)},
    'latex_source_archive': {'path': str(bundle.relative_to(R)).replace('\\', '/'), 'bytes': bundle.stat().st_size,
                             'members': names, 'sha256': sha(bundle)},
    'standalone_compile': {'commands': log, 'critical_diagnostics': critical,
                           'pages': built_pages, 'text_identical_to_delivered_pdf': True},
    'supplementary_material_in_bundle': False,
}
(R / 'results/revision_20261009/SUBMISSION_BUNDLE.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
print(json.dumps({'main_pdf_MB': round(main_pdf.stat().st_size / 1e6, 2),
                  'bundle_MB': round(bundle.stat().st_size / 1e6, 2),
                  'bundle_members': len(names), 'rebuilt_pages': built_pages,
                  'critical': critical}, indent=2))
print('members:', ', '.join(names))
