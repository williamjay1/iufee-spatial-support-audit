"""Figures from recorded revision outputs; no empirical labels are generated."""
from pathlib import Path
import json, hashlib, fitz, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pyproj import Transformer, Proj
from official_boundary_layers import extract_layers, add_layers, save_reusable_layers

ROOT=Path(r'D:\MLWork\IUFEE_revision_20261005')
DATA=Path(r'E:\science\India_Flood_Remote_Sensing_IEEE\data')
OUT=ROOT/'manuscript'/'figures'
OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.labelsize':8,
                     'xtick.labelsize':7,'ytick.labelsize':7,'pdf.fonttype':42,
                     'axes.spines.top':False,'axes.spines.right':False})
roster=pd.read_csv(DATA/'derived'/'roster'/'study_unit_roster.csv')
roster=roster.loc[roster.Cntry_name.eq('India')].copy()
assert len(roster)==91
registration=json.loads((ROOT/'results'/'OFFICIAL_MAP_REGISTRATION.json').read_text())
model=registration['registration']
proj=Proj(f"+proj=laea +lat_0={model['latitude_origin']} +lon_0=90 +ellps=WGS84")
point_x,point_y=proj(roster.centroid_lon.to_numpy(),roster.centroid_lat.to_numpy())
roster['map_x']=model['origin_x_pt']+model['scale_pdf_points_per_metre']*point_x
roster['map_y']=model['origin_y_pt']-model['scale_pdf_points_per_metre']*point_y
official_pdf=ROOT/'temp'/'MNR_Asia_GS2023_2761.pdf'
assert official_pdf.is_file(), 'Convert the recorded official EPS to PDF before plotting.'
map_crop=fitz.Rect(610,680,985,1110)
assert roster.map_x.between(map_crop.x0,map_crop.x1).all() and roster.map_y.between(map_crop.y0,map_crop.y1).all()
fig,(ax,tx)=plt.subplots(1,2,figsize=(7.12,2.65),gridspec_kw={'width_ratios':[1.2,1.6]})
layers=extract_layers(tuple(map_crop))
layer_audit=save_reusable_layers(layers,tuple(map_crop))
ax.scatter(roster.map_x,roster.map_y,s=8,c='#236e87',zorder=3,edgecolors='white',linewidth=.25)
for key,label,dx,dy in [('IND_FUA_07466','Delhi',-85,-30),('IND_FUA_10496','Guwahati',-90,90),('IND_FUA_09258','Sultanpur',10,-55)]:
    r=roster.set_index('unit_key').loc[key]
    ax.scatter([r.map_x],[r.map_y],s=18,c='#c05732',edgecolors='white',linewidth=.5,zorder=4)
    ax.annotate(label,(r.map_x,r.map_y),(r.map_x+dx,r.map_y+dy),
                fontsize=7,color='#923b20',arrowprops={'arrowstyle':'-','lw':.5,'color':'#923b20'},ha='left')
ax.set_xlim(map_crop.x0,map_crop.x1);ax.set_ylim(map_crop.y1,map_crop.y0);ax.set_aspect('equal');ax.set_axis_off()
ax.set_title('(a) Fixed frame: 91 Indian FUAs',loc='left',fontsize=8)
ax.text(.5,-.055,'Boundary source: MNR China, GS(2023)2761',transform=ax.transAxes,fontsize=5.7,ha='center')
ax.text(838,743,'China',fontsize=7,color='#79888e',ha='center',zorder=2)
ax.text(752,913,'India',fontsize=7,color='#79888e',ha='center',zorder=2)
tx.set_xlim(2013.5,2021.5);tx.set_ylim(-.7,4.5)
rows=[(4,'GHSL built surface',2015,2020,'#236e87'),(3,'WSF Evolution',2014,2015,'#749648'),
      (2,'WSF 2019',2019,2019,'#bb8134'),(1,'GLAD v2',2015,2020,'#985985')]
for y,label,l,u,color in rows:
    tx.hlines(y,l,u,color=color,lw=3)
    tx.scatter([l,u],[y,y],color=color,s=18,zorder=3)
    tx.text(2013.6,y+.23,label,fontsize=7)
tx.annotate('1985 to 2015 detections',xy=(2014,3),xytext=(2013.6,2.6),fontsize=6.5,
            arrowprops={'arrowstyle':'->','lw':.5})
tx.text(2015.7,4.18,'modelled epochs',fontsize=6.5)
tx.text(2015.3,1.18,'paired land-cover classes',fontsize=6.5)
tx.text(2013.6,0.10,'GloFAS: static fluvial depth\nRP10, 20, 50, 75, 100, 200, 500',fontsize=7)
tx.set_xticks([2015,2019,2020]);tx.set_yticks([]);tx.set_xlabel('Product epoch or endpoint (year)')
tx.set_title('(b) Source periods and roles',loc='left',fontsize=8)
fig.tight_layout(pad=.8,w_pad=1.7)
fig.canvas.draw()
position=ax.get_position()
width,height=fig.get_size_inches()*72
target=fitz.Rect(position.x0*width,(1-position.y1)*height,position.x1*width,(1-position.y0)*height)
add_layers(ax,layers)
fig.savefig(OUT/'figure_1_frame.pdf');fig.savefig(OUT/'figure_1_frame.svg');fig.savefig(OUT/'figure_1_frame.png',dpi=900);plt.close(fig)
source=json.loads((ROOT/'results'/'OFFICIAL_MAP_SOURCE.json').read_text(encoding='utf-8'))
map_audit=dict(source_authority=source['source_authority'],parent_approval_number=source['approval_number'],
    parent_official_detail_url=source['official_detail_url'],
    boundary_method='Official national-boundary/coastline paths extracted and drawn as clean vector layers; exact line and Bezier control vertices retained. No printed basemap is embedded, no raster tracing, smoothing, substitute outlines or basemap reprojection.',
    crop_parent_pdf_points=list(map_crop),embedded_rect_figure_pdf_points=list(target),
    displayed_study_points=len(roster),all_points_in_crop=True,
    registration_fit_max_error_pt=registration['fit_max_error_pt'],registration_holdout_max_error_pt=registration['holdout_max_error_pt'],
    official_pdf_sha256=hashlib.sha256(official_pdf.read_bytes()).hexdigest(),
    figure_pdf_sha256=hashlib.sha256((OUT/'figure_1_frame.pdf').read_bytes()).hexdigest(),
    original_study_frame='91 India-labelled GHS-FUA study units; the display boundary does not redefine the frozen analytical units.',
    layer_extraction=layer_audit,
    derivative_approval='Parent GS number identifies the source map. This research-point overlay has not been separately submitted for map review.')
(ROOT/'results'/'OFFICIAL_MAP_FIGURE_AUDIT.json').write_text(json.dumps(map_audit,indent=2),encoding='utf-8')
if '--figure-one-only' in sys.argv:
    print('Updated clean vector Figure 1 and reusable official-source boundary layers.')
    raise SystemExit(0)

b=pd.read_csv(ROOT/'results'/'revision_frechet_city.csv')
cases=[('IND_FUA_07466','Delhi'),('IND_FUA_10496','Guwahati'),('IND_FUA_09258','Sultanpur')]
app=pd.read_csv(ROOT/'results'/'revision_application_cities.csv')
app=app.loc[app.hazard_metric.eq('normalized_exceedance_trapezoid')]
jbase=pd.read_csv(ROOT/'results'/'joint_overlay_city_summary.csv').set_index('unit_key')
assert len(jbase)==91
fig,(ax,bx)=plt.subplots(1,2,figsize=(7.12,3.0),gridspec_kw={'width_ratios':[1,1.35]})
colors=['#96589d','#286f86','#aaa996','#d39045','#dedede']
class_names=['new_built','stable_built','absent_both','built_loss','missing_pair']
for j,(key,name) in enumerate(cases):
    br=b.set_index('unit_key').loc[key]
    ar=app.loc[app.unit_key.eq(key)].set_index('scenario')
    lo=br.feasible_intersection_min_depth_m;hi=br.feasible_intersection_max_depth_m
    ax.hlines(j,lo,hi,color='#a7a7a7',lw=4,zorder=1)
    ax.plot(ar.loc['ghsl_only','depth_m'],j+.09,'o',ms=4,color='#286f86',label='GHSL weight' if j==0 else None)
    ax.plot(ar.loc['joint_supported_screened','depth_m'],j-.09,'D',ms=4,color='#c05732',label='Archived product' if j==0 else None)
    ax.plot(jbase.loc[key,'joint_overlay_normalized_city_depth_m'],j,'^',ms=4,color='#749648',label='Joint-preserving overlay' if j==0 else None)
    ax.text(hi+.015,j,f'{lo:.3f}–{hi:.3f}',fontsize=6,va='center')
    d=json.loads((ROOT/'results'/f'glad_{key}_summary.json').read_text())
    assert d['formula_version']=='GLADpair_v2_joint_s_endpoint_support'
    for k,weight in enumerate(['g','joint']):
        left=0
        for c,col in zip(class_names,colors):
            value=100*d[f'{weight}_weighted_{c}_fraction']
            bx.barh(2*j+k,value,left=left,color=col,height=.7,
                    label=c.replace('_',' ') if j==0 and k==0 else None)
            if value>=6: bx.text(left+value/2,2*j+k,f'{value:.1f}',ha='center',va='center',fontsize=6,color='white' if c in class_names[:2] else '#222')
            left+=value
        assert abs(left-100)<.0001
ax.set_yticks(range(3),[n for _,n in cases]);ax.invert_yaxis()
ax.set_xlim(0,1.53);ax.set_xlabel('Finite probability-coordinate mean depth (m)')
ax.set_title('(a) Conditional overlap bounds',loc='left',fontsize=8)
ax.legend(loc='upper center',bbox_to_anchor=(.5,-.27),fontsize=6,frameon=False)
bx.set_yticks(range(6),[f'{n}: {w}' for _,n in cases for w in ['GHSL','archived']]);bx.invert_yaxis()
bx.set_xlim(0,100);bx.set_xlabel('Allocation of arithmetic weight (%)')
bx.set_title('(b) Paired GLAD classes',loc='left',fontsize=8)
bx.legend(ncol=3,loc='upper center',bbox_to_anchor=(.5,-.27),fontsize=6,frameon=False)
fig.tight_layout(pad=.8,w_pad=1.8)
fig.subplots_adjust(bottom=.32)
fig.savefig(OUT/'figure_2_cases.pdf');fig.savefig(OUT/'figure_2_cases.png',dpi=900);plt.close(fig)

# Maps use only frozen positive GHSL cells; white areas are not zero hazard.
# A review queue is an illustrative prioritization rule, never a truth label.
fig,axes=plt.subplots(3,3,figsize=(7.12,6.6),layout='constrained')
to_lonlat=Transformer.from_crs('ESRI:54009','EPSG:4326',always_xy=True)
queue=[]
spec=[('added_surface_m2','GHSL positive difference (m²)','viridis',0,2000),
      ('integrated_modelled_depth_m','Finite depth summary (m)','cividis',0,4),
      ('glad_new_built_fraction','GLAD new-built fraction','magma',0,1)]
for row,(key,name) in enumerate(cases):
    cells=pd.read_parquet(ROOT/'results'/'glad_cell_fractions'/f'{key}.parquet')
    cells['center_longitude'],cells['center_latitude']=to_lonlat.transform(cells.center_x_mollweide_m.to_numpy(),cells.center_y_mollweide_m.to_numpy())
    cells['review_score_m3']=cells.added_surface_m2*cells.integrated_modelled_depth_m
    selected=cells.sort_values(['review_score_m3','grid_row','grid_column'],ascending=[False,True,True]).head(10).copy()
    selected['review_order']=np.arange(1,11);selected['city']=name
    selected['selection_rule']='descending g*h; illustrative review queue, not risk or accuracy'
    queue.append(selected)
    cx=(cells.center_x_mollweide_m.max()+cells.center_x_mollweide_m.min())/2
    cy=(cells.center_y_mollweide_m.max()+cells.center_y_mollweide_m.min())/2
    x=(cells.center_x_mollweide_m-cx)/1000;y=(cells.center_y_mollweide_m-cy)/1000
    row_min,row_max=int(cells.grid_row.min()),int(cells.grid_row.max())
    col_min,col_max=int(cells.grid_column.min()),int(cells.grid_column.max())
    map_extent=[x.min()-.05,x.max()+.05,y.min()-.05,y.max()+.05]
    for col,(field,title,cmap,vmin,vmax) in enumerate(spec):
        a=axes[row,col]
        pixels=np.full((row_max-row_min+1,col_max-col_min+1),np.nan)
        pixels[cells.grid_row.to_numpy()-row_min,cells.grid_column.to_numpy()-col_min]=cells[field].to_numpy()
        sc=a.imshow(pixels,origin='upper',extent=map_extent,cmap=cmap,vmin=vmin,vmax=vmax,
                    interpolation='none',rasterized=True)
        a.scatter((selected.center_x_mollweide_m-cx)/1000,(selected.center_y_mollweide_m-cy)/1000,
                  s=12,marker='o',facecolors='none',edgecolors='#35a7a3',linewidths=.5)
        a.set_aspect('equal');a.set_xlabel('Grid offset x (km)',fontsize=7)
        a.set_ylabel(f'{name}\nGrid offset y (km)',fontsize=7)
        a.tick_params(labelsize=7)
        if row==0:
            a.set_title(['GHSL positive difference\n(m²; colour clipped at 2,000)',
                         'Finite depth summary\n(m; colour clipped at 4)',
                         'GLAD new-built fraction\n(0–1)'][col],fontsize=7.5,loc='left')
        cb=fig.colorbar(sc,ax=a,shrink=.68,pad=.02);cb.ax.tick_params(labelsize=7)
fig.savefig(OUT/'figure_3_case_maps.pdf',dpi=900);fig.savefig(OUT/'figure_3_case_maps.png',dpi=900);plt.close(fig)
pd.concat(queue).to_csv(ROOT/'results'/'revision_case_review_queue.csv',index=False,float_format='%.12g')
print('Created three figure PDFs/PNGs and a 30-cell illustrative review queue.')
