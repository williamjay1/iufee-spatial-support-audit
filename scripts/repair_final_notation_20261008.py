"""Replace table dash placeholders without changing scientific values."""
from pathlib import Path

R = Path(r'D:\MLWork\IUFEE_revision_20261005')
path = R / 'manuscript/IUFEE_technical_record.tex'
text = path.read_text(encoding='utf-8')
# Only the finite-integral reference rows lack an extreme-change city.
text = '\n'.join(line.replace('---', 'n/a' if line.startswith('Finite integral &') else 'none') if '& --- \\\\' in line else line for line in text.split('\n'))
text = text.replace('A dash in the reference row avoids labelling an arbitrary city as an extreme when every difference is zero.', 'The n/a entry in the reference row avoids labelling an arbitrary city as an extreme when every difference is zero.')
# Remaining placeholders occur only in the QA column of selected source cells.
text = '\n'.join(line.replace('& n/a \\\\', '& none \\\\') if not line.startswith('Finite integral &') else line for line in text.split('\n'))
text = text.replace('P and S indicate positive permanent-water and spurious-depth QA, respectively.', 'P and S indicate positive permanent-water and spurious-depth QA, respectively; none indicates neither recorded flag is positive.')
assert '---' not in text and '\u2014' not in text
path.write_text(text, encoding='utf-8')

path = R / 'manuscript/IUFEE_supplement.tex'
text = path.read_text(encoding='utf-8')
text = text.replace('\\begin{table}[htbp]\\centering\\small\n\\caption{Equal budget review queue coverage}', '\\begin{table}[!ht]\\centering\\small\n\\caption{Equal budget review queue coverage}')
path.write_text(text, encoding='utf-8')
print('Technical table placeholders clarified; supplement queue table anchored.')
