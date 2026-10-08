"""Control-point registration for city overlays; official boundaries stay unchanged."""
from pathlib import Path
import json,numpy as np
from scipy.optimize import least_squares
from pyproj import Proj

ROOT=Path(r'D:\MLWork\IUFEE_revision_20261005')
gcp=np.array([
[60,0,472.639984,1105.540039],[60,15,501.148010,925.322021],
[60,30,546.152039,743.468018],[60,45,606.169006,563.117004],
[75,0,666.215027,1144.890015],[75,15,680.195007,965.831055],
[75,30,702.565002,782.265991],[75,45,732.666992,597.209045],
[90,0,864.580994,1157.969971],[90,15,864.580994,979.307007],
[90,30,864.580994,795.205994],[90,45,864.580994,608.619019],
[105,0,1062.950073,1144.890015],[105,15,1048.970093,965.831055],
[105,30,1026.599976,782.265991],[105,45,996.495056,597.209045]])
uv=(gcp[:,:2]-[90,22.5])/15
terms=[(i,j) for i in range(4) for j in range(4-i)]
matrix=np.array([uv[:,0]**i*uv[:,1]**j for i,j in terms]).T
coef=np.linalg.lstsq(matrix,gcp[:,2:],rcond=None)[0]
err=np.linalg.norm(matrix@coef-gcp[:,2:],axis=1)
loo=[]
for k in range(len(gcp)):
    select=np.arange(len(gcp))!=k
    c=np.linalg.lstsq(matrix[select],gcp[select,2:],rcond=None)[0]
    loo.append(float(np.linalg.norm(matrix[k]@c-gcp[k,2:])))
results=[]
for name in ['bonne','poly','aeqd','laea','stere','eqdc','lcc']:
    def residual(par):
        try:
            if name=='bonne': spec=f'+proj=bonne +lat_1={par[0]} +lon_0=90 +ellps=WGS84'
            elif name in ['lcc','eqdc']: spec=f'+proj={name} +lat_1={par[0]} +lat_2={par[1]} +lon_0=90 +lat_0=0 +ellps=WGS84'
            else: spec=f'+proj={name} +lat_0={par[0]} +lon_0=90 +ellps=WGS84'
            pr=Proj(spec); x,y=pr(gcp[:,0],gcp[:,1])
            a=np.column_stack([x,-np.array(y),np.ones(len(x))])
            # Isotropic scale, x/y translation. Separate coordinates in one solve.
            design=np.zeros((len(x)*2,3)); design[:len(x),0]=x; design[:len(x),1]=1
            design[len(x):,0]=-np.array(y);design[len(x):,2]=1
            obs=np.r_[gcp[:,2],gcp[:,3]]
            c=np.linalg.lstsq(design,obs,rcond=None)[0]
            return design@c-obs
        except Exception: return np.ones(32)*1e6
    start=[45,60] if name in ['lcc','eqdc'] else [45]
    opt=least_squares(residual,start,bounds=([1]*len(start),[85]*len(start)),max_nfev=100)
    er=residual(opt.x).reshape(2,-1).T
    results.append(dict(projection=name,parameters=opt.x.tolist(),rmse_pt=float(np.sqrt(np.mean(np.sum(er**2,axis=1)))),max_error_pt=float(np.linalg.norm(er,axis=1).max())))
def registration(select):
    points=gcp[select]
    def solve(latitude):
        projection=Proj(f'+proj=laea +lat_0={latitude} +lon_0=90 +ellps=WGS84')
        x,y=projection(points[:,0],points[:,1])
        design=np.zeros((len(points)*2,3))
        design[:len(points),0]=x;design[:len(points),1]=1
        design[len(points):,0]=-np.asarray(y);design[len(points):,2]=1
        observation=np.r_[points[:,2],points[:,3]]
        fitted=np.linalg.lstsq(design,observation,rcond=None)[0]
        return fitted,design@fitted-observation
    fitted=least_squares(lambda z:solve(z[0])[1],[40.],bounds=([1.],[85.]))
    scale,origin_x,origin_y=solve(fitted.x[0])[0]
    return dict(latitude_origin=float(fitted.x[0]),longitude_origin=90,
                scale_pdf_points_per_metre=float(scale),origin_x_pt=float(origin_x),origin_y_pt=float(origin_y))
def apply_registration(model,points):
    projection=Proj(f"+proj=laea +lat_0={model['latitude_origin']} +lon_0=90 +ellps=WGS84")
    x,y=projection(points[:,0],points[:,1]);scale=model['scale_pdf_points_per_metre']
    return np.column_stack([model['origin_x_pt']+scale*x,model['origin_y_pt']-scale*y])
model=registration(np.ones(16,dtype=bool))
fit_error=np.linalg.norm(apply_registration(model,gcp)-gcp[:,2:],axis=1)
holdout_indices=[0,5,10,15]
train=~np.isin(np.arange(16),holdout_indices)
holdout_model=registration(train)
holdout_error=np.linalg.norm(apply_registration(holdout_model,gcp[~train])-gcp[~train,2:],axis=1)
loo_error=[]
for k in range(16):
    m=registration(np.arange(16)!=k)
    loo_error.append(float(np.linalg.norm(apply_registration(m,gcp[k:k+1])[0]-gcp[k,2:])))
assert fit_error.max()<.01 and holdout_error.max()<.02 and max(loo_error)<.02
record=dict(parent_map='MNR Asia GS(2023)2761 EPS converted by local Ghostscript without reprojection',
            pdf_coordinate_origin='top left, points',gcp=gcp.tolist(),
            method='Empirical Lambert azimuthal equal-area fit to the official graticule; transforms study-point coordinates only. This is an inferred display registration, not an officially declared CRS.',
            registration=model,fit_rmse_pt=float(np.sqrt(np.mean(fit_error**2))),fit_max_error_pt=float(fit_error.max()),
            holdout_indices=holdout_indices,holdout_max_error_pt=float(holdout_error.max()),
            leave_one_control_out_rmse_pt=float(np.sqrt(np.mean(np.array(loo_error)**2))),leave_one_control_out_max_error_pt=max(loo_error),
            candidate_projection_fits=results,
            use_boundary='Official national-boundary and coastline vector paths are extracted and rendered with new cartographic styling; original line/Bezier control vertices are retained without basemap reprojection. Registration uncertainty concerns the overlay only; not a map-accuracy estimate or a scientific calculation.',
            coordinate_domain=dict(lon=[60,105],lat=[0,45]))
(ROOT/'results/OFFICIAL_MAP_REGISTRATION.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({k:record[k] for k in ['registration','fit_rmse_pt','fit_max_error_pt','holdout_max_error_pt','leave_one_control_out_max_error_pt']},indent=2))
