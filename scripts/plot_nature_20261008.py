"""Nature-style figures from frozen, independently audited IUFEE outputs.

Only display choices change. EPS-derived national-boundary vertices, source
registration, measured fields, city selections and calculations are retained.
Run in the dedicated scifig environment. PDF/SVG are vector outputs; the PNG
backup is exported at 1000 dpi and does not add information to native grids.
"""
from pathlib import Path
import sys, json, hashlib, math
import numpy as np
import pandas as pd
# The figure environment intentionally owns matplotlib. The established
# analysis interpreter uses the same CPython 3.12 ABI; append its verified GIS
# and parquet packages after loading the figure environment's numpy/pandas.
sys.path.append(r'C:\Users\Administrator\AppData\Local\Programs\Python\Python312\Lib\site-packages')
sys.path.append(r'C:\Users\Administrator\AppData\Roaming\Python\Python312\site-packages')
sys.path.insert(0, r'C:\Users\Administrator\.agents\skills\sci-figures')
from figstyle import apply_house_style, audit, mm
from matplotlib.collections import PolyCollection
from matplotlib.text import Text
from matplotlib.transforms import Bbox
import fitz
from pyproj import Proj
from official_boundary_layers import extract_layers, add_layers, as_mpl_path

ROOT=Path(r'D:\MLWork\IUFEE_revision_20261005')
OUT=ROOT/'manuscript/figures'
RESULT=ROOT/'results/revision_20261008'
TEMP=ROOT/'temp/figures_20261008'
RESULT.mkdir(parents=True,exist_ok=True);TEMP.mkdir(parents=True,exist_ok=True)
plt=apply_house_style(fontsize=8)
plt.rcParams.update({'font.family':'Arial','axes.spines.top':False,
    'axes.spines.right':False,'axes.linewidth':.6,'axes.labelsize':7.5,
    'xtick.labelsize':7,'ytick.labelsize':7,'legend.fontsize':7,
    'xtick.top':False,'ytick.right':False,'xtick.minor.visible':False,
    'ytick.minor.visible':False,'savefig.bbox':None,'savefig.pad_inches':0,
    'mathtext.fontset':'dejavusans','lines.linewidth':.9})
BLUE='#0072B2';ORANGE='#D55E00';GREEN='#009E73';GRAY='#92999D'
REPORTS={};SOURCES={}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def trace(path):
    path=Path(path);SOURCES[str(path.relative_to(ROOT))]=sha(path)
    return path
def label(fig,x,y,letter,title):
    fig.text(x,y,letter,fontweight='bold',fontsize=8,ha='left',va='top')
    fig.text(x+.019,y,title,fontsize=8,ha='left',va='top')
def outside_text(ax,x,y,text,**kwargs):
    return ax.text(x,y,text,clip_on=False,bbox=dict(facecolor='white',
        edgecolor='none',pad=.8),fontsize=7,**kwargs)
def clean(ax):
    ax.tick_params(length=2.5,width=.6,pad=2)
    ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)

def export(fig,stem,refs,role):
    fig.canvas.draw();renderer=fig.canvas.get_renderer()
    nonrendered_ticks=set()
    for ax in fig.axes:
        if not ax.axison:
            nonrendered_ticks.update(id(t) for t in ax.get_xticklabels()+ax.get_yticklabels())
            nonrendered_ticks.update([id(ax.xaxis.label),id(ax.yaxis.label)])
            continue
        lo,hi=sorted(ax.get_xlim())
        for t in ax.get_xticklabels():
            if not lo-1e-9<=t.get_position()[0]<=hi+1e-9:nonrendered_ticks.add(id(t))
        lo,hi=sorted(ax.get_ylim())
        for t in ax.get_yticklabels():
            if not lo-1e-9<=t.get_position()[1]<=hi+1e-9:nonrendered_ticks.add(id(t))
    texts=[]
    for t in fig.findobj(match=lambda x:isinstance(x,Text)):
        if not t.get_visible() or not t.get_text().strip() or id(t) in nonrendered_ticks:continue
        bb=t.get_window_extent(renderer)
        if bb.width<.1 or bb.height<.1:continue
        texts.append((t,bb))
    clips=[];collisions=[]
    for t,bb in texts:
        if bb.x0<-.2 or bb.y0<-.2 or bb.x1>fig.bbox.x1+.2 or bb.y1>fig.bbox.y1+.2:
            clips.append(t.get_text())
    # Tick/label/legend boxes are checked at native canvas scale. Touching edges
    # do not count; duplicate artist identities are omitted.
    for i,(a,ba) in enumerate(texts):
        for b,bb in texts[i+1:]:
            if a is b:continue
            cross=Bbox.intersection(ba,bb)
            if cross and cross.width>1 and cross.height>1:
                collisions.append([a.get_text(),b.get_text()])
    report=audit(fig,max_width_mm=183,verbose=True)
    report['all_text_minimum_pt']=min(t.get_fontsize() for t,_ in texts)
    report['bold_lowercase_panel_labels']=[t.get_text() for t,_ in texts if len(t.get_text())==1
        and t.get_text() in 'abcdefghi' and t.get_fontweight()=='bold']
    report['text_box_collisions']=collisions;report['off_canvas_text']=clips
    report['role']=role;report['data_sources']=refs
    report['vector_note']='PDF and SVG contain original vector text and geometry; vector resolution is independent of dpi.'
    assert report['ok'] and not clips,report
    assert report['all_text_minimum_pt']>=7,report
    paths={}
    for ext in ['pdf','svg','png']:
        p=OUT/f'{stem}.{ext}';fig.savefig(p,dpi=1000,bbox_inches=None)
        paths[ext]={'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
    fig.savefig(TEMP/f'{stem}_preview.png',dpi=180,bbox_inches=None)
    with fitz.open(OUT/f'{stem}.pdf') as doc:
        report['pdf_size_mm']=[doc[0].rect.width/72*25.4,doc[0].rect.height/72*25.4]
        report['pdf_raster_image_objects']=len(doc[0].get_images(full=True))
        report['pdf_fonts']=[x[3] for x in doc[0].get_fonts(full=True)]
        assert report['pdf_raster_image_objects']==0
    report['png_export_dpi']=1000;report['paths']=paths
    REPORTS[stem]=report;plt.close(fig)

def map_and_periods():
    reg_path=trace(ROOT/'results/OFFICIAL_MAP_REGISTRATION.json')
    reg=json.loads(reg_path.read_text());model=reg['registration']
    roster_path=Path(r'E:\science\India_Flood_Remote_Sensing_IEEE\data\derived\roster\study_unit_roster.csv')
    roster=pd.read_csv(roster_path);roster=roster[roster.Cntry_name.eq('India')].copy()
    assert len(roster)==91
    proj=Proj(f"+proj=laea +lat_0={model['latitude_origin']} +lon_0=90 +ellps=WGS84")
    x,y=proj(roster.centroid_lon.to_numpy(),roster.centroid_lat.to_numpy())
    roster['map_x']=model['origin_x_pt']+model['scale_pdf_points_per_metre']*x
    roster['map_y']=model['origin_y_pt']-model['scale_pdf_points_per_metre']*y
    crop=(610,680,985,1110);layers=extract_layers(crop)
    # Compare every extracted original vertex/code against the reusable record.
    boundary_path=trace(ROOT/'datasets/official_boundary_paths.json')
    saved=json.loads(boundary_path.read_text())
    for kind,items in layers.items():
        assert len(items)==len(saved['paths'][kind])
        for (index,draw),stored in zip(items,saved['paths'][kind]):
            p=as_mpl_path(draw)
            assert index==stored['source_drawing_index']
            assert np.array_equal(p.vertices,np.array(stored['vertices']))
            assert np.array_equal(p.codes,np.array(stored['codes']))
    fig=plt.figure(figsize=(mm(180),mm(58)))
    # Keep the official map in its original coordinate plane. A slightly
    # taller bottom margin separates both official line classes from the
    # parent-map provenance footer without shrinking their labels below 7 pt.
    ax=fig.add_axes([.049,.155,.32,.735])
    ax.set(xlim=(crop[0],crop[2]),ylim=(crop[3],crop[1]));ax.set_aspect('equal');ax.set_axis_off()
    fig.canvas.draw();add_layers(ax,layers)
    ax.scatter(roster.map_x,roster.map_y,s=7,color=BLUE,zorder=3,edgecolors='white',linewidth=.3)
    index=roster.set_index('unit_key');annotations=[]
    map_bbox=ax.get_window_extent();clearance_pt=2.5
    def margin_annotation(text,target,side,vertical_offset_pt=0,color=ORANGE):
        target_pixels=ax.transData.transform(target)
        x_px=(map_bbox.x0-clearance_pt*fig.dpi/72 if side=='left'
            else map_bbox.x1+clearance_pt*fig.dpi/72)
        y_px=target_pixels[1]+vertical_offset_pt*fig.dpi/72
        location=fig.transFigure.inverted().transform([x_px,y_px])
        annotation=ax.annotate(text,target,xytext=location,textcoords='figure fraction',
            ha='right' if side=='left' else 'left',va='center',color=color,fontsize=7,
            # Transparent padding supplies an arrow clipping patch; it does
            # not hide or cover the map, and the actual text is outside it.
            bbox=dict(facecolor='none',edgecolor='none',pad=0),
            arrowprops=dict(arrowstyle='-',lw=.6,color=color,shrinkA=3,shrinkB=3,
                connectionstyle='arc3,rad=0'),zorder=6)
        annotations.append((text,side,annotation))
        return annotation
    for key,name,side,dy in [('IND_FUA_07466','Delhi','left',13),
        ('IND_FUA_10496','Guwahati','right',-2),
        ('IND_FUA_09258','Sultanpur','left',-23)]:
        r=index.loc[key]
        ax.scatter([r.map_x],[r.map_y],s=18,color=ORANGE,edgecolors='white',linewidth=.45,zorder=5)
        margin_annotation(name,(r.map_x,r.map_y),side,dy)
    margin_annotation('China',(838,738),'right',5,color='#59656C')
    # This annotation names the region rather than assigning sovereignty.
    # The label stays outside the map; its leader ends in the northern region,
    # away from the Srinagar centroid and the Delhi callout.
    margin_annotation('Kashmir\nregion',(708,707),'left',0,color='#59656C')
    label(fig,.018,.975,'a','Study frame: 91 cities')
    # The two official dash periods remain distinct in the legend. Matplotlib
    # scales dash values by line width, so undo that scaling when transferring
    # lengths from the EPS-derived source plane into figure points.
    import re
    from matplotlib.lines import Line2D
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path as MplPath
    figure_scale=ax.get_window_extent().width*72/fig.dpi/(crop[2]-crop[0])
    for kind,y,label_text in [('regional',.108,'Regional boundary'),
        ('ceasefire',.066,'Ceasefire line')]:
        assert layers.get(kind),f'Missing official line layer: {kind}'
        drawing=layers[kind][0][1]
        dash=re.match(r'\[([^]]*)\]\s*([-\d.]+)',drawing['dashes'])
        assert dash and dash.group(1).strip(),f'Official {kind} must remain dashed'
        parts=[float(x) for x in dash.group(1).split()];lw=.5
        style=(float(dash.group(2))*figure_scale/lw,tuple(x*figure_scale/lw for x in parts))
        if kind=='regional':
            fig.add_artist(Line2D([.081,.108],[y,y],transform=fig.transFigure,
                color='#69777E',lw=lw,ls=style))
        else:
            # The official military demarcation uses separate crossed strokes,
            # not a centreline. Copy one original cross (source items 16/51)
            # into the legend and repeat it, without joining the strokes.
            symbol=dict(drawing)
            symbol['items']=[drawing['items'][2],drawing['items'][37]]
            symbol['closePath']=False
            path=as_mpl_path(symbol);center=path.vertices.mean(axis=0)
            span=np.ptp(path.vertices,axis=0).max();symbol_scale=2.7/span
            width_pt,height_pt=fig.get_size_inches()*72
            symbol_style=(float(dash.group(2))*symbol_scale/lw,
                tuple(x*symbol_scale/lw for x in parts))
            for x_center in [.083,.095,.107]:
                vertices=(path.vertices-center)*symbol_scale
                vertices[:,0]=x_center+vertices[:,0]/width_pt
                vertices[:,1]=y-vertices[:,1]/height_pt
                fig.add_artist(PathPatch(MplPath(vertices,path.codes),
                    transform=fig.transFigure,facecolor='none',edgecolor='#69777E',
                    linewidth=lw,linestyle=symbol_style))
        fig.text(.116,y,label_text,ha='left',va='center',fontsize=7,color='#59656C')
    fig.text(.182,.026,'GS(2023)2761 · MNR China',ha='center',va='center',fontsize=7)
    tx=fig.add_axes([.625,.20,.346,.66]);tx.set(xlim=(2013.8,2020.7),ylim=(-.5,4.5))
    labels=[(4,'GHSL building surface'),(3,'WSF detection history'),
        (2,'WSF endpoint'),(1,'GLAD paired classes'),(0,'GloFAS fluvial depth')]
    for yy,text in labels:
        fig.text(.420,.20+.66*(yy+.5)/5,text,ha='left',va='center',fontsize=7.5)
    tx.plot([2015,2020],[4,4],color=BLUE,marker='o',ms=4,lw=1)
    tx.hlines(3,2014,2015,color=GREEN,lw=1)
    tx.plot([2015],[3],color=GREEN,marker='s',ms=4)
    tx.plot([2014],[3],marker='<',color=GREEN,ms=5)
    tx.text(2016,3,'1985 to 2015',fontsize=7,va='center',color=GREEN)
    tx.plot([2019],[2],color=ORANGE,marker='D',ms=4.5)
    tx.plot([2015,2020],[1,1],color='#75559C',marker='^',ms=4.5,lw=1,ls=':')
    tx.text(2014,0,'Static layers, seven return periods',fontsize=7,va='center')
    tx.set_xticks([2015,2019,2020]);tx.set_yticks([])
    tx.spines[['left','right','top']].set_visible(False);tx.set_xlabel('Mapped epoch or endpoint (year)',labelpad=3)
    clean(tx);label(fig,.420,.975,'b','Source periods')
    fig.canvas.draw()
    renderer=fig.canvas.get_renderer();map_bbox=ax.get_window_extent()
    scale=72/fig.dpi
    # Annotation.get_window_extent includes its leader. The geometric gate
    # requires the text-only extent, supplied by the base Text implementation.
    words=[]
    for t in list(fig.texts)+list(tx.texts)+[a for _,_,a in annotations]:
        if t.get_visible() and t.get_text().strip():
            words.append((t,Text.get_window_extent(t,renderer)))
    placement={}
    for name,side,annotation in annotations:
        bb=Text.get_window_extent(annotation,renderer)
        gap=(map_bbox.x0-bb.x1 if side=='left' else bb.x0-map_bbox.x1)*scale
        leader=annotation.arrow_patch.get_path().transformed(annotation.arrow_patch.get_transform())
        leader_length=float(np.linalg.norm(np.diff(leader.vertices,axis=0),axis=1).sum()*scale)
        intersections=[t.get_text() for t,b in words if leader.intersects_bbox(b,filled=False)]
        assert not map_bbox.overlaps(bb) and gap>=2-1e-8,(name,gap)
        assert leader_length>=16,(name,leader_length)
        assert not intersections,(name,intersections)
        placement[name.replace('\n',' ')]=dict(side=side,text_bbox_figure_pt=(bb.extents*scale).tolist(),
            gap_pt=float(gap),leader_length_pt=leader_length,outside_map=True,
            leader_text_intersections=intersections)
    label_qa=dict(map_bbox_figure_pt=(map_bbox.extents*scale).tolist(),annotations=placement,
        all_labels_outside_map=True,minimum_required_gap_pt=2,minimum_required_leader_length_pt=16,
        minimum_observed_gap_pt=min(x['gap_pt'] for x in placement.values()),
        minimum_observed_leader_length_pt=min(x['leader_length_pt'] for x in placement.values()),
        transparent_label_background=True)
    old=json.loads((ROOT/'results/OFFICIAL_MAP_FIGURE_AUDIT.json').read_text())
    old['style_revision']='Nature-style layout, 2026-10-08; exact official national/coast/regional/ceasefire paths and 91 registered study locations retained, with an external Kashmir region label.'
    old['exact_vertex_codes_compared_to_reusable_record']=True
    old['displayed_study_points']=91
    old['layer_extraction']={'layer_counts':{k:len(v) for k,v in layers.items()},
        'reusable_vector_json_sha256':sha(boundary_path)}
    old['regional_label']='Kashmir region'
    old['line_legend_labels']=['Regional boundary','Ceasefire line']
    old['ceasefire_legend_symbol_source_items']=[16,51]
    old['label_placement']=label_qa
    position=ax.get_position();width,height=fig.get_size_inches()*72
    old['embedded_rect_figure_pdf_points']=[position.x0*width,(1-position.y1)*height,
        position.x1*width,(1-position.y0)*height]
    refs=['results/OFFICIAL_MAP_REGISTRATION.json','datasets/official_boundary_paths.json',str(roster_path)]
    export(fig,'figure_1_frame',refs,'Letter main figure 1')
    REPORTS['figure_1_frame']['label_placement']=label_qa
    old['figure_pdf_sha256']=sha(OUT/'figure_1_frame.pdf')
    (ROOT/'results/OFFICIAL_MAP_FIGURE_AUDIT.json').write_text(json.dumps(old,indent=2),encoding='utf-8')

def representation():
    R=ROOT/'results/revision_20261007'
    d=pd.read_csv(trace(R/'diagnostics_city_decomposition.csv'))
    d=d[d.unit_key.ne('ALL91_POOLED')].copy();assert len(d)==91
    s=json.loads(trace(R/'diagnostics_summary.json').read_text())
    c=pd.read_csv(trace(R/'diagnostics_exposure_JF_symmetric_decomposition.csv'))
    q=pd.read_csv(trace(R/'diagnostics_queue_coverage.csv'))
    fig=plt.figure(figsize=(mm(180),mm(95)))
    ax=fig.add_axes([.080,.61,.385,.285]);clean(ax)
    z=d.sort_values('observed_EJ_minus_EF_m').reset_index(drop=True)
    xx=np.arange(1,92);v=z.observed_EJ_minus_EF_m.to_numpy()
    ax.plot(xx,v,'o',ms=2.6,color=BLUE,zorder=3)
    ax.axhline(0,color='.65',lw=.55,zorder=1)
    ax.set(xlim=(-2,94),ylim=(-.245,.08),xticks=[1,30,60,91],yticks=[-.2,-.1,0],
        xlabel='Cities ordered by signed difference',ylabel='$E_J-E_F$ (m)')
    for key,name,loc in [('IND_FUA_02091','Srinagar',(.15,.16)),('IND_FUA_10496','Guwahati',(.53,.92))]:
        i=int(np.flatnonzero(z.unit_key.eq(key))[0])
        ax.annotate(name,(i+1,v[i]),xytext=loc,textcoords='axes fraction',fontsize=7,
            va='center',bbox=dict(facecolor='white',edgecolor='none',pad=1),
            arrowprops=dict(arrowstyle='-',lw=.6,color='.35',shrinkA=3,shrinkB=3))
    label(fig,.019,.974,'a','City depth differences')
    ax=fig.add_axes([.606,.61,.37,.285]);clean(ax)
    keys=['IND_FUA_02091','IND_FUA_10496','IND_FUA_07466','IND_FUA_09258','IND_FUA_07499']
    names=['Srinagar','Guwahati','Delhi','Sultanpur','Nashik'];cs=c.set_index('unit_key').loc[keys];yy=np.arange(5)
    ax.barh(yy-.16,cs.model_nonzero_support_share_term_m,height=.29,color=BLUE,label='Support share')
    ax.barh(yy+.16,cs.conditional_model_depth_term_m,height=.29,color=ORANGE,label='Conditional depth')
    ax.axvline(0,color='.65',lw=.55)
    ax.set(yticks=yy,yticklabels=names,xlim=(-.225,.065),xticks=[-.2,-.1,0],
        xlabel='Contribution to $E_J-E_F$ (m)');ax.invert_yaxis()
    ax.legend(loc='upper center',bbox_to_anchor=(.5,1.16),ncol=2,handlelength=1.3,
        columnspacing=.8,handletextpad=.35,borderaxespad=0)
    label(fig,.528,.974,'b','Two sources of the difference')
    ax=fig.add_axes([.080,.145,.385,.29]);clean(ax);p=s['pooled_decomposition']
    vals=[p['positive_contributions_sum_m'],p['negative_contributions_sum_m'],p['observed_EJ_minus_EF_m']]
    ax.bar([0,1,2],vals,width=.53,color=[BLUE,ORANGE,'#4A555D'])
    ax.axhline(0,color='.65',lw=.55,zorder=0)
    ax.set(xticks=[0,1,2],xticklabels=['Positive','Negative','Net'],ylabel='Pooled contribution (m)',
        ylim=(-.018,.018),yticks=[-.01,0,.01])
    for i,val in enumerate(vals):
        outside_text(ax,i,val+(0.0009 if val>=0 else -0.0009),f'{val:+.5f}',
            ha='center',va='bottom' if val>=0 else 'top')
    ax.text(.5,.98,f"{100*p['cancellation_fraction']:.1f}% cancellation",transform=ax.transAxes,
        ha='center',va='top',fontsize=7)
    label(fig,.019,.515,'c','Pooled cancellation')
    ax=fig.add_axes([.606,.145,.37,.29]);clean(ax)
    qq=q[(q.unit_key.eq('ALL91_POOLED'))&(q.budget_rule.eq('top1pct_cells'))].set_index('queue')
    a=np.array([qq.loc[k,'absolute_representation_effect_coverage']*100 for k in ['representation_absolute_effect','standard_g_times_h']])
    b=np.array([qq.loc[k,'standard_depth_proxy_mass_coverage']*100 for k in ['representation_absolute_effect','standard_g_times_h']])
    ax.bar(np.arange(2)-.18,a,width=.33,color=BLUE,label='Absolute effect')
    ax.bar(np.arange(2)+.18,b,width=.33,color=ORANGE,label='Depth numerator')
    ax.set(xticks=[0,1],xticklabels=['Effect queue','Depth queue'],ylabel='Coverage of target quantity (%)',
        ylim=(0,86),yticks=[0,20,40,60,80],xlabel='Top 1% of eligible cells')
    for i in range(2):
        outside_text(ax,i-.18,a[i]+1.5,f'{a[i]:.1f}',ha='center',va='bottom')
        outside_text(ax,i+.18,b[i]+1.5,f'{b[i]:.1f}',ha='center',va='bottom')
    ax.legend(loc='upper center',bbox_to_anchor=(.5,1.16),ncol=2,handlelength=1.3,
        columnspacing=.8,handletextpad=.35,borderaxespad=0)
    label(fig,.528,.515,'d','Review queues at equal budget')
    export(fig,'figure_4_representation',[str(p.relative_to(ROOT)) for p in [R/'diagnostics_city_decomposition.csv',
        R/'diagnostics_summary.json',R/'diagnostics_exposure_JF_symmetric_decomposition.csv',
        R/'diagnostics_queue_coverage.csv']],'Letter main figure 2')

def glad():
    path=trace(ROOT/'results/revision_20261007/diagnostics_glad_class_allocation.csv')
    g=pd.read_csv(path);gp=g[g.unit_key.eq('ALL91_POOLED')]
    citypath=trace(ROOT/'results/glad_city_summary.csv');cities=pd.read_csv(citypath)
    fig=plt.figure(figsize=(mm(180),mm(58)))
    ax=fig.add_axes([.064,.295,.25,.57]);clean(ax)
    schemes=['G','J','F','A'];cl=['new_built','stable_built','absent_both','built_loss']
    colors=[GREEN,BLUE,'#CED3D6',ORANGE];names=['New built','Stable built','Absent both','Built loss']
    left=np.zeros(4)
    for cat,col,name in zip(cl,colors,names):
        v=np.array([gp[(gp.scheme.eq(z))&(gp.glad_pair_class.eq(cat))].glad_class_share_of_allocation.iloc[0]*100 for z in schemes])
        ax.barh(schemes,v,left=left,color=col,label=name,height=.66);left+=v
    assert np.max(abs(left-100))<1e-5
    ax.set(xlim=(0,100),xticks=[0,50,100],xlabel='Allocation composition (%)');ax.invert_yaxis()
    ax.legend(loc='upper left',bbox_to_anchor=(-.06,-.31),ncol=2,handlelength=1,
        columnspacing=.8,handletextpad=.35,borderaxespad=0,labelspacing=.45)
    label(fig,.018,.975,'a','Paired GLAD classes')
    ax=fig.add_axes([.418,.295,.225,.57]);clean(ax)
    for scheme,col,marker,ls in zip(['J','F','A'],[GREEN,BLUE,ORANGE],['o','s','^'],['-',':','--']):
        vals=[]
        for cat in cl[:3]:
            original=gp[(gp.scheme.eq('G'))&(gp.glad_pair_class.eq(cat))].allocated_surface_times_glad_class_fraction_m2.iloc[0]
            current=gp[(gp.scheme.eq(scheme))&(gp.glad_pair_class.eq(cat))].allocated_surface_times_glad_class_fraction_m2.iloc[0]
            vals.append(100*current/original)
        ax.plot(np.arange(3),vals,color=col,marker=marker,ms=4,ls=ls,label=scheme)
    ax.set(xticks=[0,1,2],xticklabels=['New','Stable','Absent'],ylim=(0,36),yticks=[0,10,20,30],
        ylabel='Retained class allocation (%)');ax.legend(ncol=3,loc='upper left',bbox_to_anchor=(0,-.29),
        handlelength=1.2,columnspacing=.8,handletextpad=.35,borderaxespad=0)
    label(fig,.366,.975,'b','Retention relative to G')
    ax=fig.add_axes([.752,.295,.225,.57]);clean(ax)
    x=cities.zero_change_cellarea_new_fraction_covered.to_numpy()*100
    y=cities.positive_cellarea_new_fraction_covered.to_numpy()*100
    limit=math.ceil(max(x.max(),y.max())/5)*5
    ax.plot([0,limit],[0,limit],ls='--',color='.5',lw=.6,zorder=1)
    ax.scatter(x,y,s=8,color=BLUE,alpha=.78,linewidths=0,zorder=2)
    ax.set(xlim=(0,limit),ylim=(0,limit),xlabel='Zero change cells (%)',ylabel='Positive change cells (%)')
    ax.text(.03,.97,'91 cities',transform=ax.transAxes,fontsize=7,ha='left',va='top',
        bbox=dict(facecolor='white',edgecolor='none',pad=1))
    label(fig,.7,.975,'c','New class fraction')
    export(fig,'figure_5_glad',[str(path.relative_to(ROOT)),str(citypath.relative_to(ROOT))],
        'Letter main figure 3')

def cases():
    path=trace(ROOT/'results/revision_frechet_city.csv');b=pd.read_csv(path).set_index('unit_key')
    apppath=trace(ROOT/'results/revision_application_cities.csv')
    app=pd.read_csv(apppath);app=app[app.hazard_metric.eq('normalized_exceedance_trapezoid')]
    jp=trace(ROOT/'results/joint_overlay_city_summary.csv');joint=pd.read_csv(jp).set_index('unit_key')
    cases=[('IND_FUA_07466','Delhi'),('IND_FUA_10496','Guwahati'),('IND_FUA_09258','Sultanpur')]
    fig=plt.figure(figsize=(mm(180),mm(60)))
    ax=fig.add_axes([.084,.33,.355,.535]);clean(ax)
    for j,(key,name) in enumerate(cases):
        br=b.loc[key];ar=app[app.unit_key.eq(key)].set_index('scenario')
        lo,hi=br.feasible_intersection_min_depth_m,br.feasible_intersection_max_depth_m
        ax.hlines(j,lo,hi,color='#BAC2C7',lw=3,zorder=1)
        for val,dy,mk,col,lab in [(ar.loc['ghsl_only','depth_m'],.11,'o',BLUE,'G'),
            (ar.loc['joint_supported_screened','depth_m'],-.11,'s',ORANGE,'A'),
            (joint.loc[key,'joint_overlay_normalized_city_depth_m'],0,'^',GREEN,'J')]:
            ax.plot(val,j+dy,marker=mk,ms=4.8,color=col,ls='none',label=lab if j==0 else None)
        outside_text(ax,hi+.018,j-.26,f'{lo:.3f} to {hi:.3f}',ha='left',va='bottom')
    ax.set(yticks=range(3),yticklabels=[n for _,n in cases],xlim=(0,1.62),xticks=[0,.5,1,1.5],
        xlabel='Mean modelled depth (m)',ylim=(-.45,2.45));ax.invert_yaxis()
    ax.legend(ncol=3,loc='upper center',bbox_to_anchor=(.5,-.30),handlelength=1,
        columnspacing=1,handletextpad=.3,borderaxespad=0)
    label(fig,.018,.975,'a','Conditional overlap bounds')
    ax=fig.add_axes([.612,.33,.364,.535]);clean(ax)
    cl=['new_built','stable_built','absent_both','built_loss','missing_pair']
    colors=[GREEN,BLUE,'#CED3D6',ORANGE,'white'];names=['New built','Stable built','Absent both','Built loss','Missing pair']
    refs=[str(path.relative_to(ROOT)),str(apppath.relative_to(ROOT)),str(jp.relative_to(ROOT))]
    for j,(key,name) in enumerate(cases):
        cp=trace(ROOT/'results'/f'glad_{key}_summary.json');refs.append(str(cp.relative_to(ROOT)))
        d=json.loads(cp.read_text());assert d['formula_version']=='GLADpair_v2_joint_s_endpoint_support'
        for k,w in enumerate(['g','joint']):
            left=0
            for cat,col,lab in zip(cl,colors,names):
                val=100*d[f'{w}_weighted_{cat}_fraction']
                ax.barh(2*j+k,val,left=left,color=col,height=.63,
                    label=lab if j==0 and k==0 and cat!='missing_pair' else None)
                left+=val
            assert abs(left-100)<1e-4
    ax.set(yticks=range(6),yticklabels=[f'{n}: {w}' for _,n in cases for w in ['G','A']],
        xlim=(0,100),xticks=[0,50,100],xlabel='Allocation composition (%)');ax.invert_yaxis()
    ax.legend(ncol=2,loc='upper left',bbox_to_anchor=(-.04,-.3),handlelength=1,
        columnspacing=.8,handletextpad=.35,borderaxespad=0,labelspacing=.4)
    label(fig,.527,.975,'b','Paired GLAD allocation')
    export(fig,'figure_2_cases',refs,'Supplementary three city examples')

def case_maps():
    cases=[('IND_FUA_07466','Delhi'),('IND_FUA_10496','Guwahati'),('IND_FUA_09258','Sultanpur')]
    fig=plt.figure(figsize=(mm(180),mm(169)))
    specs=[('added_surface_m2','GHSL positive difference','m²; colours clipped at 2,000','batlow',0,2000),
        ('integrated_modelled_depth_m','Finite depth summary','m; colours clipped at 4','batlowW',0,4),
        ('glad_new_built_fraction','GLAD new built fraction','0 to 1','lajolla',0,1)]
    import cmcrameri.cm as cmc
    from matplotlib.ticker import MaxNLocator
    refs=[];axis_art=[];col_mappables={}
    for col,(_,title,unit,*_) in enumerate(specs):
        fig.text(.2155+.303*col,.98,title,fontsize=8,ha='center',va='top')
        fig.text(.2155+.303*col,.955,unit,fontsize=7,ha='center',va='top')
    for row,(key,name) in enumerate(cases):
        path=trace(ROOT/'results/glad_cell_fractions'/f'{key}.parquet');refs.append(str(path.relative_to(ROOT)))
        import pyarrow.parquet as pq
        # Arrow's native reader avoids applying unrelated pandas extension
        # metadata from the older analysis environment.
        cells=pd.DataFrame(pq.read_table(path).to_pydict())
        cells['review_score_m3']=cells.added_surface_m2*cells.integrated_modelled_depth_m
        selected=cells.sort_values(['review_score_m3','grid_row','grid_column'],ascending=[False,True,True]).head(10)
        cx=(cells.center_x_mollweide_m.max()+cells.center_x_mollweide_m.min())/2
        cy=(cells.center_y_mollweide_m.max()+cells.center_y_mollweide_m.min())/2
        x=(cells.center_x_mollweide_m.to_numpy()-cx)/1000
        y=(cells.center_y_mollweide_m.to_numpy()-cy)/1000
        # Preserve native cell extents; each observed 100 m cell is a polygon.
        corners=np.stack([np.column_stack([x-.05,y-.05]),np.column_stack([x+.05,y-.05]),
            np.column_stack([x+.05,y+.05]),np.column_stack([x-.05,y+.05])],axis=1)
        for col,(field,title,unit,cmap,vmin,vmax) in enumerate(specs):
            ax=fig.add_axes([.108+.303*col,.69-.285*row,.215,.23]);clean(ax)
            pc=PolyCollection(corners,array=cells[field].to_numpy(),cmap=getattr(cmc,cmap),
                edgecolors='none',linewidths=0,rasterized=False)
            pc.set_clim(vmin,vmax);ax.add_collection(pc)
            ax.scatter((selected.center_x_mollweide_m-cx)/1000,(selected.center_y_mollweide_m-cy)/1000,
                s=12,marker='o',facecolors='none',edgecolors='#B83535',linewidths=.6,zorder=5)
            ax.set(xlim=(x.min()-.05,x.max()+.05),ylim=(y.min()-.05,y.max()+.05),aspect='equal')
            ax.set_xlabel('Grid x (km)',labelpad=2)
            ax.set_ylabel('Grid y (km)',labelpad=2)
            ax.xaxis.set_major_locator(MaxNLocator(nbins=3));ax.yaxis.set_major_locator(MaxNLocator(nbins=3))
            col_mappables[col]=pc
            ax.text(-.15,1.065,chr(97+3*row+col),transform=ax.transAxes,fontweight='bold',fontsize=8)
        fig.text(.018,.805-.285*row,name,fontsize=8,rotation=90,ha='center',va='center')
    # One vector colour scale per column avoids redundant colourbars and
    # leaves stable white-space gutters between every text/plot panel.
    for col in range(3):
        cbax=fig.add_axes([.108+.303*col,.037,.215,.012])
        cb=fig.colorbar(col_mappables[col],cax=cbax,orientation='horizontal')
        cb.set_ticks([[0,1000,2000],[0,2,4],[0,.5,1]][col])
        cb.outline.set_linewidth(.5);cb.ax.tick_params(labelsize=7,length=2,pad=1)
        cb.solids.set_rasterized(False)
    export(fig,'figure_3_case_maps',refs,'Supplementary native cell maps')

if __name__=='__main__':
    targets=sys.argv[1:] or ['map','representation','glad','cases','case_maps']
    for task in targets:
        {'map':map_and_periods,'representation':representation,'glad':glad,'cases':cases,'case_maps':case_maps}[task]()
    prior=RESULT/'FIGURE_DESIGN_AND_QA.json'
    record=json.loads(prior.read_text()) if prior.exists() else {}
    record.update({'date':'2026-10-08','software':'matplotlib, SciencePlots science/nature, cmcrameri; dedicated scifig Python',
        'design_reference':['https://github.com/garrettj403/SciencePlots','https://www.nature.com/nature/for-authors/final-submission'],
        'data_unchanged':True,'figures':dict(record.get('figures',{}),**REPORTS),
        'source_hashes':dict(record.get('source_hashes',{}),**SOURCES)})
    prior.write_text(json.dumps(record,indent=2,default=lambda x:x.item()),encoding='utf-8')
    print(json.dumps({k:{'text_box_collisions':v['text_box_collisions'],'off_canvas_text':v['off_canvas_text']} for k,v in REPORTS.items()},indent=2))
