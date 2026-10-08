"""Verify preserved official map sources and regenerate the D-drive vector PDF."""
from pathlib import Path
import hashlib, json, shutil, stat, subprocess

ROOT=Path(r'D:\MLWork\IUFEE_revision_20261005')
RAW=Path(r'F:\AcademicData\IUFEE_revision_20261005\raw\MNR_standard_map_20261005')
GHOSTSCRIPT=Path(r'C:\Users\Administrator\AppData\Local\Programs\MiKTeX\miktex\bin\x64\mgs.exe')
FILES={
    'eps_zip':('MNR_Asia_GS2023_2761_EPS_20261005.zip',32094372,'96bf98faf401a0b985ec708ab66e94359e5ad2a7dfbb42078a89261bdeddbf1d'),
    'eps':('MNR_Asia_GS2023_2761_20261005.eps',49274038,'455a607155b283145149a21c98d2320c4ef24f805d0c4a0e41e1a0ef0b2ad8c3'),
}
record=json.loads((ROOT/'results/OFFICIAL_MAP_SOURCE.json').read_text(encoding='utf-8'))
for kind,(filename,size,expected) in FILES.items():
    path=RAW/filename
    assert path.is_file(), f'Preserved official source required: {path}'
    actual=hashlib.sha256(path.read_bytes()).hexdigest()
    assert path.stat().st_size==size and actual==expected
    assert path.stat().st_file_attributes & stat.FILE_ATTRIBUTE_READONLY
    record[kind]=dict(raw_path=str(path),bytes=size,sha256=actual,readonly=True)
record['eps_zip']['official_source_url']='https://bzdt-sbsm.obs.cn-north-4.myhuaweicloud.com/prototype/4/4o28b0625501ad13015501ad2bfc2193b.zip'
assert shutil.disk_usage('D:\\').free>100000000
assert GHOSTSCRIPT.is_file(), 'Use an available Ghostscript; do not install or change raw sources implicitly.'
output=ROOT/'temp/MNR_Asia_GS2023_2761.pdf'
output.parent.mkdir(parents=True,exist_ok=True)
command=[str(GHOSTSCRIPT),'-dSAFER','-dBATCH','-dNOPAUSE','-dEPSCrop','-sDEVICE=pdfwrite',f'-sOutputFile={output}',str(RAW/FILES['eps'][0])]
run=subprocess.run(command,capture_output=True,text=True,check=True)
(ROOT/'results/OFFICIAL_MAP_CONVERSION_LOG.txt').write_text(run.stdout+'\n'+run.stderr,encoding='utf-8')
record['vector_conversion']=dict(command=command,output_path=str(output),
    output_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
    treatment='EPS to PDF on D; no geographic reprojection, boundary edits or raster tracing. Raw sources remain read-only.')
(ROOT/'results/OFFICIAL_MAP_SOURCE.json').write_text(json.dumps(record,indent=2,ensure_ascii=False),encoding='utf-8')
print('Verified official EPS ZIP/EPS identities and regenerated the vector PDF on D.')
