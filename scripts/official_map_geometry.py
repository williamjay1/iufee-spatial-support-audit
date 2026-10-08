"""Read the official EPS-derived PDF geometry without changing its boundary paths."""
from pathlib import Path
import fitz,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(r'D:\MLWork\IUFEE_revision_20261005')
doc=fitz.open(ROOT/'temp/MNR_Asia_GS2023_2761.pdf')
page=doc[0]
draws=page.get_drawings()

def flatten(items):
    chains=[]; current=[]
    for item in items:
        if item[0]=='l': pts=np.array([list(item[1]),list(item[2])])
        elif item[0]=='c':
            p=np.array([list(x) for x in item[1:]])
            t=np.linspace(0,1,40)[:,None]
            pts=(1-t)**3*p[0]+3*(1-t)**2*t*p[1]+3*(1-t)*t**2*p[2]+t**3*p[3]
        else: continue
        if current and np.linalg.norm(np.array(current[-1])-pts[0])>.05:
            chains.append(np.array(current));current=[]
        current.extend(pts.tolist())
    if current: chains.append(np.array(current))
    return chains

chains=[]
for i in [1911,1912]:
    chains.extend(flatten(draws[i]['items']))
fig,ax=plt.subplots(figsize=(12,9))
records=[]
for i,pts in enumerate(chains):
    length=np.linalg.norm(np.diff(pts,axis=0),axis=1).sum()
    if length<100: continue
    ax.plot(pts[:,0],pts[:,1],lw=.6)
    pos=pts[int(len(pts)*.8)]
    ax.text(*pos,str(i),fontsize=7,color='black')
    records.append(dict(id=i,length=length,points=pts.tolist()))
ax.invert_yaxis();ax.set_aspect('equal');ax.grid();fig.tight_layout()
fig.savefig(ROOT/'temp/official_graticule_paths.png',dpi=140)
(ROOT/'results/OFFICIAL_GRATICULE_PATHS.json').write_text(json.dumps(records),encoding='utf-8')
print(json.dumps([dict(id=x['id'],length=round(x['length'],1),start=x['points'][0],end=x['points'][-1]) for x in records],indent=2))
