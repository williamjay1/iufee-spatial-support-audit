"""Reusable plotting layers from the Chinese official map's original vector paths.

Coordinates remain in the official EPS-derived PDF plane. Study locations use
the separately checked graticule registration; no raster tracing is involved.
"""
from pathlib import Path
import json, re, hashlib
import numpy as np
import fitz
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch

ROOT=Path(r'D:\MLWork\IUFEE_revision_20261005')
DEFAULT_CROP=(610,680,985,1110)

def as_mpl_path(drawing):
    vertices=[];codes=[];last=None
    def start(point):
        nonlocal last
        xy=tuple(point)
        if last!=xy:
            vertices.append(xy);codes.append(MplPath.MOVETO)
        last=xy
    for item in drawing['items']:
        operation=item[0]
        if operation=='l':
            start(item[1]);last=tuple(item[2])
            vertices.append(last);codes.append(MplPath.LINETO)
        elif operation=='c':
            start(item[1])
            vertices.extend(tuple(p) for p in item[2:]);codes.extend([MplPath.CURVE4]*3)
            last=tuple(item[4])
        elif operation=='re':
            rect=item[1]
            corners=[(rect.x0,rect.y0),(rect.x1,rect.y0),(rect.x1,rect.y1),(rect.x0,rect.y1)]
            if len(item)>2 and item[2]<0: corners=corners[::-1]
            vertices.extend(corners+[corners[0]]);codes.extend([MplPath.MOVETO]+[MplPath.LINETO]*3+[MplPath.CLOSEPOLY]);last=None
        elif operation=='qu':
            quad=item[1];corners=[tuple(quad.ul),tuple(quad.ur),tuple(quad.lr),tuple(quad.ll)]
            vertices.extend(corners+[corners[0]]);codes.extend([MplPath.MOVETO]+[MplPath.LINETO]*3+[MplPath.CLOSEPOLY]);last=None
        else: raise ValueError(f'Unsupported official vector operation: {operation}')
    if drawing.get('closePath') and vertices:
        vertices.append(vertices[-1]);codes.append(MplPath.CLOSEPOLY)
    path=MplPath(np.asarray(vertices,dtype=float),np.asarray(codes,dtype=np.uint8))
    path.should_simplify=False
    return path

def extract_layers(crop=DEFAULT_CROP):
    clip=fitz.Rect(crop)
    with fitz.open(ROOT/'temp/MNR_Asia_GS2023_2761.pdf') as doc:
        drawings=doc[0].get_drawings()
    land=[];national=[];coast=[];regional=[];ceasefire=[]
    for index,drawing in enumerate(drawings):
        if not drawing['rect'].intersects(clip): continue
        if index<446 and drawing['fill'] and min(drawing['fill'])>.99:
            land.append((index,drawing))
        if 1915<=index<=2096:
            assert np.allclose(drawing['color'],[.1366903,.1219501,.1252918],atol=1e-5)
            assert abs(drawing['width']-.56693)<1e-4
            national.append((index,drawing))
        if 948<=index<1188 and drawing['color']:
            coast.append((index,drawing))
        if index==1914:
            assert len(drawing['items'])==30
            assert abs(drawing['width']-.425197)<1e-4
            regional.append((index,drawing))
        if index==1913:
            # The original military demarcation is drawn as independent short
            # strokes. Items 0:14 belong to Korea; 14:54 belong to Kashmir.
            # Preserve their MOVETO boundaries; do not invent a centreline.
            subset=dict(drawing)
            subset['items']=drawing['items'][14:54]
            assert len(subset['items'])==40
            points=np.asarray([tuple(p) for item in subset['items'] for p in item[1:]],dtype=float)
            subset['rect']=fitz.Rect(*points.min(axis=0),*points.max(axis=0))
            subset['closePath']=False
            subset['source_item_range']=[14,54]
            ceasefire.append((index,subset))
    assert len(regional)==1 and len(ceasefire)==1
    return dict(land=land,national=national,coast=coast,regional=regional,ceasefire=ceasefire)

def add_layers(ax,layers):
    for index,drawing in layers['land']:
        ax.add_patch(PathPatch(as_mpl_path(drawing),facecolor='#f6f7f7',
            edgecolor='none',linewidth=0,zorder=0))
    for index,drawing in layers['coast']:
        ax.add_patch(PathPatch(as_mpl_path(drawing),facecolor='none',edgecolor='#a6b0b5',linewidth=.35,zorder=.5))
    # Convert original dash lengths in the PDF plane to figure points. This
    # retains the distinction between defined and undefined country boundaries.
    figure_scale=ax.get_window_extent().width*72/ax.figure.dpi/(ax.get_xlim()[1]-ax.get_xlim()[0])
    for kind,linewidth,zorder in [('national',.55,1),('regional',.45,1.1),('ceasefire',.45,1.2)]:
        for index,drawing in layers[kind]:
            dash=re.match(r'\[([^]]*)\]\s*([-\d.]+)',drawing['dashes'])
            parts=[float(x) for x in dash.group(1).split()] if dash else []
            style=(float(dash.group(2))*figure_scale/linewidth,tuple(x*figure_scale/linewidth for x in parts)) if parts else 'solid'
            ax.add_patch(PathPatch(as_mpl_path(drawing),facecolor='none',edgecolor='#69777e',linewidth=linewidth,linestyle=style,zorder=zorder))

def save_reusable_layers(layers,crop=DEFAULT_CROP):
    import matplotlib.pyplot as plt
    records={}
    for kind,paths in layers.items():
        records[kind]=[]
        for index,drawing in paths:
            path=as_mpl_path(drawing)
            item=dict(source_drawing_index=index,vertices=path.vertices.tolist(),
                codes=path.codes.tolist(),source_dash=drawing.get('dashes'),source_bbox=list(drawing['rect']))
            if 'source_item_range' in drawing:
                item['source_item_range']=drawing['source_item_range']
            records[kind].append(item)
    source=json.loads((ROOT/'results/OFFICIAL_MAP_SOURCE.json').read_text(encoding='utf-8'))
    record=dict(source_authority=source['source_authority'],source_approval_number=source['approval_number'],
        official_source_url=source['eps_zip']['official_source_url'],source_eps_sha256=source['eps']['sha256'],
        source_plane='Original EPS-derived PDF coordinates: origin top left, unit point. Not an officially published GIS CRS.',
        crop=list(crop),paths=records,
        extraction='Exact line/Bezier control vertices copied from official vector paths; no tracing, smoothing or geometric simplification.',
        layer_semantics=dict(national='Official defined and undefined country-boundary paths, unchanged.',
            regional='Kashmir region boundary: official drawing 1914 with original dash pattern.',
            ceasefire='Kashmir military demarcation: official drawing 1913, items 14:54; original independent short-stroke symbols and dash pattern. No continuous centreline added.'),
        land_fill='Uniform neutral fill; land colouring does not denote a national claim or analytical boundary.',
        exclusions='Printed labels, river/lake layers, graticule and original city glyphs; regional and military-demarcation lines are kept separate from national boundaries.')
    dataset=ROOT/'datasets/official_boundary_paths.json'
    dataset.write_text(json.dumps(record,indent=2),encoding='utf-8')
    fig,ax=plt.subplots(figsize=(4.6,5.4))
    ax.set(xlim=(crop[0],crop[2]),ylim=(crop[3],crop[1]))
    ax.set_aspect('equal');ax.set_axis_off()
    fig.tight_layout(pad=.1);fig.canvas.draw()
    add_layers(ax,layers)
    for extension in ['svg','pdf']:
        fig.savefig(ROOT/'manuscript/figures'/f'official_boundary_layer.{extension}',transparent=True)
    fig.savefig(ROOT/'temp/official_clean_layers_preview.png',dpi=180)
    plt.close(fig)
    return dict(layer_counts={k:len(v) for k,v in records.items()},
                reusable_vector_json_sha256=hashlib.sha256(dataset.read_bytes()).hexdigest())

if __name__=='__main__':
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    layers=extract_layers()
    print(save_reusable_layers(layers))
