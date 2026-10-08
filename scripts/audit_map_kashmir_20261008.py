"""Check the restored Kashmir layers against the original official vector map."""
from pathlib import Path
import json, hashlib
import numpy as np
import fitz
from official_boundary_layers import extract_layers, as_mpl_path

R=Path(r'D:\MLWork\IUFEE_revision_20261005')
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

before=json.loads((R/'temp/map_before_kashmir_20261008/official_boundary_paths.json').read_text(encoding='utf-8'))
after=json.loads((R/'datasets/official_boundary_paths.json').read_text(encoding='utf-8'))
for kind in ['land','national','coast']:
    assert before['paths'][kind]==after['paths'][kind],kind
with fitz.open(R/'temp/MNR_Asia_GS2023_2761.pdf') as doc:
    source=doc[0].get_drawings()
layers=extract_layers()
for kind in ['regional','ceasefire']:
    assert len(layers[kind])==len(after['paths'][kind])==1
    index,drawing=layers[kind][0]
    path=as_mpl_path(drawing)
    record=after['paths'][kind][0]
    assert index==record['source_drawing_index']
    assert np.array_equal(path.vertices,np.asarray(record['vertices']))
    assert np.array_equal(path.codes,np.asarray(record['codes']))
    assert drawing['dashes']==source[index]['dashes']==record['source_dash']
    if kind=='regional':
        assert index==1914 and drawing['items']==source[index]['items']
    else:
        assert index==1913 and drawing['items']==source[index]['items'][14:54]
        assert record['source_item_range']==[14,54]
        assert np.count_nonzero(path.codes==1)==40
        assert len(path.vertices)==80

source_record=json.loads((R/'results/OFFICIAL_MAP_SOURCE.json').read_text(encoding='utf-8'))
assert sha(Path(source_record['eps']['raw_path']))==source_record['eps']['sha256']
assert sha(R/'temp/MNR_Asia_GS2023_2761.pdf')==source_record['vector_conversion']['output_sha256']
qa=json.loads((R/'results/revision_20261008/FIGURE_DESIGN_AND_QA.json').read_text(encoding='utf-8'))
placement=qa['figures']['figure_1_frame']['label_placement']
assert placement['all_labels_outside_map'] and placement['transparent_label_background']
expected={'Delhi','Guwahati','Sultanpur','China','Kashmir region'}
assert set(placement['annotations'])==expected
assert placement['minimum_observed_gap_pt']>=2
assert placement['minimum_observed_leader_length_pt']>=16
assert all(not a['leader_text_intersections'] for a in placement['annotations'].values())
figure=R/'manuscript/figures/figure_1_frame.pdf'
pdf_gaps={}
with fitz.open(figure) as doc:
    assert len(doc[0].get_images())==0
    text=doc[0].get_text()
    assert 'Kashmir' in text and 'region' in text
    assert 'Regional boundary' in text and 'Ceasefire line' in text
    words=doc[0].get_text('words')
    map_bbox=placement['map_bbox_figure_pt']
    for name,a in placement['annotations'].items():
        matches=[w for w in words if w[4] in name.split()]
        if name=='China':
            matches=[w for w in matches if w[0]>map_bbox[2]]
        assert len(matches)==len(name.split()),name
        left=min(w[0] for w in matches);right=max(w[2] for w in matches)
        gap=map_bbox[0]-right if a['side']=='left' else left-map_bbox[2]
        assert gap>=2,(name,gap)
        pdf_gaps[name]=gap

oldtex=(R/'temp/map_before_kashmir_20261008/IUFEE_redeveloped.tex').read_text(encoding='utf-8')
newtex=(R/'manuscript/IUFEE_redeveloped.tex').read_text(encoding='utf-8')
addition=' Kashmir is labelled as a region; its regional boundary and ceasefire symbols retain the official source geometry.'
assert newtex.replace(addition,'')==oldtex
label_backup=R/'temp/map_labels_white_20261008'
assert (R/'manuscript/IUFEE_redeveloped.tex').read_bytes()==(label_backup/'IUFEE_redeveloped.tex').read_bytes()
with fitz.open(R/'manuscript/IUFEE_redeveloped.pdf') as doc:
    assert len(doc)==5

map_audit=json.loads((R/'results/OFFICIAL_MAP_FIGURE_AUDIT.json').read_text(encoding='utf-8'))
assert map_audit['displayed_study_points']==91 and map_audit['all_points_in_crop']
map_audit['boundary_method']='Exact national-boundary, coastline, Kashmir regional-boundary and military-demarcation vector paths from the official source; original independent ceasefire symbols preserved. No invented continuous centreline.'
map_audit['layer_extraction']={
    'layer_counts':{k:len(v) for k,v in after['paths'].items()},
    'reusable_vector_json_sha256':sha(R/'datasets/official_boundary_paths.json')}
map_audit['kashmir_correction']={
    'regional_boundary_source':1914,'ceasefire_source':1913,'ceasefire_source_items':[14,54],
    'ceasefire_independent_strokes':40,'original_national_coast_land_geometry_unchanged':True,
    'land_fill':'Uniform neutral; study coverage represented only by 91 registered points',
    'label':'Kashmir region','source_symbol_semantics':'Regional boundary and ceasefire symbols are distinct from national boundaries.'}
(R/'results/OFFICIAL_MAP_FIGURE_AUDIT.json').write_text(json.dumps(map_audit,indent=2),encoding='utf-8')

report={
    'all_passed':True,'scope':'Cartographic correction and external annotation layout only; manuscript scientific content unchanged.',
    'official_eps_sha256':source_record['eps']['sha256'],
    'original_three_layer_records_exactly_equal':True,
    'regional_path_exact':True,'ceasefire_subpaths_exact':True,'ceasefire_independent_movetos':40,
    'figure_pdf_sha256':sha(figure),'vector_json_sha256':sha(R/'datasets/official_boundary_paths.json'),
    'main_pdf_before_sha256':sha(R/'temp/map_before_kashmir_20261008/IUFEE_redeveloped.pdf'),
    'main_pdf_after_sha256':sha(R/'manuscript/IUFEE_redeveloped.pdf'),
    'tex_only_change':'One figure-caption sentence identifying the restored regional and ceasefire geometry',
    'main_tex_unchanged_since_label_request':True,
    'main_pdf_before_label_request_sha256':sha(label_backup/'IUFEE_redeveloped.pdf'),
    'label_placement':placement,'actual_pdf_label_gap_pt':pdf_gaps,
    'displayed_study_points':91,'main_pages':5,
    'visual_review':'Pending final figure and manuscript rendering review'}
(R/'results/revision_20261008/KASHMIR_MAP_CORRECTION.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
