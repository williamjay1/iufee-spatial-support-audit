"""Publication figures for the frozen 91-city representation diagnostics."""
from pathlib import Path
import sys,json
import numpy as np
import pandas as pd
sys.path.insert(0,r'C:\Users\Administrator\.agents\skills\sci-figures')
from figstyle import apply_house_style,save,audit,mm,panel_label
plt=apply_house_style(fontsize=8)
ROOT=Path(r'D:\MLWork\IUFEE_revision_20261005')
R=ROOT/'results/revision_20261007'; OUT=ROOT/'manuscript/figures'
d=pd.read_csv(R/'diagnostics_city_decomposition.csv')
d=d[d.unit_key!='ALL91_POOLED'].copy()
s=json.loads((R/'diagnostics_summary.json').read_text())
c=pd.read_csv(R/'diagnostics_exposure_JF_symmetric_decomposition.csv')
g=pd.read_csv(R/'diagnostics_glad_class_allocation.csv')
q=pd.read_csv(R/'diagnostics_queue_coverage.csv')
reports={}
blue='#0072B2'; orange='#D55E00'; green='#009E73'
fig,axs=plt.subplots(2,2,figsize=(mm(178),mm(119)),layout='constrained')
ax=axs[0,0]; panel_label(ax,'a'); z=d.sort_values('observed_EJ_minus_EF_m')
ax.plot(np.arange(1,92),z.observed_EJ_minus_EF_m,'o',ms=2.8,color=blue)
ax.axhline(0,color='.4',lw=.6);ax.set(xlabel='Cities ordered by signed difference',ylabel='$E_J-E_F$ (m)')
for key,name,offset in [('IND_FUA_02091','Srinagar',(5,9)),('IND_FUA_10496','Guwahati',(-45,6))]:
    zz=z.reset_index(drop=True); ix=int(np.flatnonzero(zz.unit_key==key)[0]);v=zz.iloc[ix].observed_EJ_minus_EF_m
    ax.annotate(name,(ix+1,v),xytext=offset,textcoords='offset points',fontsize=7)
ax=axs[0,1];panel_label(ax,'b')
names=['Srinagar','Guwahati','Delhi','Sultanpur','Nashik']
keys=['IND_FUA_02091','IND_FUA_10496','IND_FUA_07466','IND_FUA_09258','IND_FUA_07499']
cs=c.set_index('unit_key').loc[keys]
x=np.arange(5)
ax.barh(x-.17,cs.model_nonzero_support_share_term_m,height=.31,label='Nonzero-support share',color=blue)
ax.barh(x+.17,cs.conditional_model_depth_term_m,height=.31,label='Conditional depth',color=orange)
ax.axvline(0,color='.4',lw=.6);ax.set(yticks=x,yticklabels=names,xlabel='Symmetric contribution to $E_J-E_F$ (m)');ax.invert_yaxis()
ax.legend(loc='lower left',fontsize=6.3)
ax=axs[1,0];panel_label(ax,'c');p=s['pooled_decomposition']
vals=[p['positive_contributions_sum_m'],p['negative_contributions_sum_m'],p['observed_EJ_minus_EF_m']]
ax.bar(['Positive','Negative','Net'],vals,color=[blue,orange,'.3'],width=.6)
ax.axhline(0,color='.4',lw=.6);ax.set(ylabel='Pooled centered contribution (m)',ylim=(-.015,.015))
for i,v in enumerate(vals): ax.text(i,v+(.0008 if v>=0 else -.0008),f'{v:+.5f}',ha='center',va='bottom' if v>=0 else 'top',fontsize=7)
ax.text(.5,.94,f"{100*p['cancellation_fraction']:.1f}% cancellation",transform=ax.transAxes,ha='center',va='top',fontsize=7)
ax=axs[1,1];panel_label(ax,'d')
qq=q[(q.unit_key=='ALL91_POOLED')&(q.budget_rule=='top1pct_cells')].set_index('queue')
labels=['Representation effect','Standard $g h$']; xx=np.arange(2)
aa=[qq.loc[k,'absolute_representation_effect_coverage']*100 for k in ['representation_absolute_effect','standard_g_times_h']]
bb=[qq.loc[k,'standard_depth_proxy_mass_coverage']*100 for k in ['representation_absolute_effect','standard_g_times_h']]
ax.bar(xx-.18,aa,width=.34,color=blue,label='Absolute representation effect')
ax.bar(xx+.18,bb,width=.34,color=orange,label='Standard depth numerator')
ax.set(xticks=xx,xticklabels=labels,ylabel='Share covered by top 1% of cells (%)',ylim=(0,85))
for i in range(2):
    ax.text(i-.18,aa[i]+1,f'{aa[i]:.1f}',ha='center',fontsize=7)
    ax.text(i+.18,bb[i]+1,f'{bb[i]:.1f}',ha='center',fontsize=7)
ax.legend(loc='upper center',fontsize=6.3)
reports['representation']=audit(fig,max_width_mm=183)
assert reports['representation']['ok']
save(fig,str(OUT/'figure_4_representation'),dpi=900)
fig.savefig(ROOT/'temp/representation_preview.png',dpi=150,bbox_inches='tight');plt.close(fig)

fig,axs=plt.subplots(1,3,figsize=(mm(178),mm(61)),layout='constrained',gridspec_kw={'width_ratios':[1,1,1.12]})
gp=g[g.unit_key=='ALL91_POOLED'];cl=['new_built','stable_built','absent_both','built_loss'];color=[green,blue,'#BBBBBB',orange]
labels=['New built','Stable built','Absent both','Built loss'];schemes=['G','J','F','A']
ax=axs[0];panel_label(ax,'a');left=np.zeros(4)
for cat,col,label in zip(cl,color,labels):
    v=np.array([gp[(gp.scheme==z)&(gp.glad_pair_class==cat)].glad_class_share_of_allocation.iloc[0]*100 for z in schemes])
    ax.barh(schemes,v,left=left,color=col,label=label);left+=v
ax.set(xlabel='GLAD class share of allocation (%)',xlim=(0,100));ax.invert_yaxis()
ax.legend(loc='lower center',bbox_to_anchor=(.5,-.56),ncol=2,fontsize=6.3)
ax=axs[1];panel_label(ax,'b');xx=np.arange(3)
for j,(scheme,col,mark) in enumerate(zip(['J','F','A'],[green,blue,orange],['o','s','^'])):
    v=[]
    for cat in cl[:3]:
        gg=gp[(gp.scheme=='G')&(gp.glad_pair_class==cat)].allocated_surface_times_glad_class_fraction_m2.iloc[0]
        vv=gp[(gp.scheme==scheme)&(gp.glad_pair_class==cat)].allocated_surface_times_glad_class_fraction_m2.iloc[0]
        v.append(100*vv/gg)
    ax.plot(xx,v,marker=mark,color=col,lw=.8,label=scheme)
ax.set(xticks=xx,xticklabels=['New','Stable','Absent'],ylabel='Retained share of G class allocation (%)',ylim=(0,40));ax.legend(ncol=3,loc='upper right',fontsize=6.3)
ax=axs[2];panel_label(ax,'c');cities=pd.read_csv(ROOT/'results/glad_city_summary.csv')
x=cities.zero_change_cellarea_new_fraction_covered.to_numpy()*100;y=cities.positive_cellarea_new_fraction_covered.to_numpy()*100
ax.scatter(x,y,s=9,c=blue,alpha=.75,linewidths=0);lim=max(x.max(),y.max())*1.07
ax.plot([0,lim],[0,lim],ls='--',color='.5',lw=.6);ax.set(xlim=(0,lim),ylim=(0,lim),xlabel='New-class fraction in zero-change cells (%)',ylabel='New-class fraction in positive-change cells (%)')
ax.text(.04,.96,'One point per city',transform=ax.transAxes,va='top',fontsize=7)
reports['glad']=audit(fig,max_width_mm=183);assert reports['glad']['ok']
save(fig,str(OUT/'figure_5_glad'),dpi=900)
fig.savefig(ROOT/'temp/glad_preview.png',dpi=150,bbox_inches='tight');plt.close(fig)
(R/'FIGURE_AUDIT.json').write_text(json.dumps(reports,indent=2,default=lambda x:x.item()),encoding='utf-8')
print(json.dumps({'cities':len(d),'figures':list(reports)}))
