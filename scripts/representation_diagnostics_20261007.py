"""Deterministic post hoc diagnostics of representation and modelled depth.

Reads only the frozen 91-city J/F/A and GLAD derived products. No accuracy,
construction-truth, flood-realisation or inferential-significance claim is made.
"""
from __future__ import annotations
import hashlib
import json
import math
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

WORK = Path(r"D:\MLWork\IUFEE_revision_20261005")
OUT = WORK / "results" / "revision_20261007"
JOINT = WORK / "datasets" / "joint_overlay"
GLAD = WORK / "results" / "glad_cell_fractions"
SCHEMES = ["G", "J", "F", "A"]
CLASSES = ["new_built", "stable_built", "absent_both", "built_loss", "missing_pair"]
KEY = ["unit_key", "grid_row", "grid_column"]
COV_TOL = 1e-7


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def number(x):
    return None if not np.isfinite(x) else float(x)


def markdown_table(frame):
    columns=frame.columns.tolist()
    lines=['| '+' | '.join(columns)+' |','| '+' | '.join(['---']*len(columns))+' |']
    for row in frame.itertuples(index=False,name=None):
        lines.append('| '+' | '.join(f'{value:.6g}' if isinstance(value,(float,np.floating)) else str(value) for value in row)+' |')
    return '\n'.join(lines)


def allocation_components(unit, name, g, h, fractions):
    rows = []
    for scheme, fraction in fractions.items():
        w = g*fraction
        W = float(w.sum())
        positive = float(w[h > 0].sum())
        N = float(np.dot(w,h))
        E = N/W if W else np.nan
        pp = positive/W if W else np.nan
        mu = N/positive if positive else np.nan
        residual = E-pp*mu if positive and W else np.nan
        rows.append(dict(unit_key=unit,eFUA_name=name,scheme=scheme,
                         allocated_surface_m2=W,allocated_surface_on_model_nonzero_depth_support_m2=positive,
                         depth_weighted_proxy_m3=N,model_nonzero_depth_support_share=number(pp),
                         conditional_model_nonzero_mean_depth_m=number(mu),normalized_mean_depth_m=number(E),
                         conditional_mean_defined=positive > 0,product_identity_residual_m=number(residual),
                         product_identity_defined=positive > 0 and W > 0,
                         zero_support_mean_check_passed=(N == 0 and E == 0) if W > 0 and positive == 0 else None,
                         zero_support_handling="conditional mean undefined; E=0 if W>0 and Wplus=0"))
    return rows


def symmetric_depth_decomposition(components):
    lookup = {x["scheme"]:x for x in components}
    j,f = lookup["J"],lookup["F"]
    usable = j["conditional_mean_defined"] and f["conditional_mean_defined"]
    delta = j["normalized_mean_depth_m"]-f["normalized_mean_depth_m"]
    if usable:
        pj,pf = j["model_nonzero_depth_support_share"],f["model_nonzero_depth_support_share"]
        mj,mf = j["conditional_model_nonzero_mean_depth_m"],f["conditional_model_nonzero_mean_depth_m"]
        support = (pj-pf)*(mj+mf)/2
        conditional = (mj-mf)*(pj+pf)/2
        error = delta-support-conditional
    else:
        support = conditional = error = None
    return dict(unit_key=j["unit_key"],eFUA_name=j["eFUA_name"],difference_J_minus_F_m=delta,
                model_nonzero_support_share_term_m=support,conditional_model_depth_term_m=conditional,
                symmetric_identity_residual_m=error,decomposition_defined_both_nonzero=usable,
                p_J=j["model_nonzero_depth_support_share"],p_F=f["model_nonzero_depth_support_share"],
                mu_J_m=j["conditional_model_nonzero_mean_depth_m"],mu_F_m=f["conditional_model_nonzero_mean_depth_m"])


def queue_diagnostics(unit, name, cells, contribution):
    """Fixed cell budgets; deterministic sorting resolves ties by cell key."""
    effect = np.abs(contribution)
    standard = cells.g.to_numpy()*cells.h.to_numpy()
    total_effect,total_standard = float(effect.sum()),float(standard.sum())
    # cells have already been sorted by key; stable sort preserves that tie order.
    effect_order = np.argsort(-effect,kind="stable")
    standard_order = np.argsort(-standard,kind="stable")
    rows = []
    for label,k in [("top10_cells",min(10,len(cells))),("top1pct_cells",max(1,math.ceil(len(cells)*.01))),("top10pct_cells",max(1,math.ceil(len(cells)*.10)))]:
        queues = {"representation_absolute_effect":effect_order[:k],"standard_g_times_h":standard_order[:k]}
        overlap = len(np.intersect1d(queues["representation_absolute_effect"],queues["standard_g_times_h"]))
        for queue,chosen in queues.items():
            rows.append(dict(unit_key=unit,eFUA_name=name,budget_rule=label,queue=queue,
                             eligible_positive_increment_cells=len(cells),selected_cells=k,
                             absolute_representation_effect_coverage=float(effect[chosen].sum()/total_effect) if total_effect else None,
                             standard_depth_proxy_mass_coverage=float(standard[chosen].sum()/total_standard) if total_standard else None,
                             signed_representation_effect_selected_m=float(contribution[chosen].sum()),
                             queue_overlap_cells=overlap,queue_overlap_fraction=overlap/k))
    top = cells.iloc[effect_order[:min(10,len(cells))]][["unit_key","eFUA_name","grid_row","grid_column","g","h","t","s","p","cov_SP","cell_difference_t_minus_f"]].copy()
    top["signed_representation_effect_contribution_m"] = contribution[effect_order[:len(top)]]
    top["absolute_representation_effect_rank"] = np.arange(1,len(top)+1)
    top["diagnostic_scope"] = unit
    return rows,top


def decompose(unit, name, cells):
    g,h,t,f,cov = [cells[k].to_numpy(dtype="float64") for k in ["g","h","t","f","cov_SP"]]
    Aj,Af = float(np.dot(g,t)),float(np.dot(g,f))
    Nj,Nf = float(np.dot(g*h,t)),float(np.dot(g*h,f))
    Ej,Ef = Nj/Aj,Nf/Af
    contribution = g*(t-f)*(h-Ef)/Aj
    cov_contribution = -g*cov*(h-Ef)/Aj
    signed = float(contribution.sum())
    positive = float(contribution[contribution > 0].sum())
    negative = float(contribution[contribution < 0].sum())
    absolute = float(np.abs(contribution).sum())
    queues,top = queue_diagnostics(unit,name,cells,contribution)
    result = dict(unit_key=unit,eFUA_name=name,cells=len(cells),g_total_m2=float(g.sum()),A_J_m2=Aj,A_F_m2=Af,
                  N_J_m3=Nj,N_F_m3=Nf,E_J_m=Ej,E_F_m=Ef,observed_EJ_minus_EF_m=Ej-Ef,
                  centered_contribution_sum_m=signed,normalized_difference_identity_residual_m=Ej-Ef-signed,
                  covariance_contribution_sum_m=float(cov_contribution.sum()),
                  covariance_identity_max_cell_error=float(np.max(np.abs((t-f)+cov))),
                  positive_contributions_sum_m=positive,negative_contributions_sum_m=negative,
                  absolute_contributions_sum_m=absolute,cancellation_fraction=1-abs(signed)/absolute if absolute else 0,
                  g_weighted_covariance_SP=float(np.dot(g,cov)/g.sum()),
                  covariance_positive_cells=int((cov > COV_TOL).sum()),covariance_negative_cells=int((cov < -COV_TOL).sum()),
                  covariance_near_zero_cells=int((np.abs(cov) <= COV_TOL).sum()))
    for budget in ["top10_cells","top1pct_cells","top10pct_cells"]:
        row = next(x for x in queues if x["budget_rule"] == budget and x["queue"] == "representation_absolute_effect")
        result[f"absolute_contribution_concentration_{budget}"] = row["absolute_representation_effect_coverage"]
    quadrants = []
    for label,mask in [
        ("positive_cov_above_F_mean",(cov > COV_TOL)&(h > Ef)),
        ("positive_cov_below_F_mean",(cov > COV_TOL)&(h < Ef)),
        ("negative_cov_above_F_mean",(cov < -COV_TOL)&(h > Ef)),
        ("negative_cov_below_F_mean",(cov < -COV_TOL)&(h < Ef)),
        ("near_zero_cov_or_equal_depth",(np.abs(cov) <= COV_TOL)|(h == Ef))]:
        quadrants.append(dict(unit_key=unit,eFUA_name=name,category=label,cells=int(mask.sum()),
                              signed_contribution_m=float(contribution[mask].sum()),
                              absolute_contribution_m=float(np.abs(contribution[mask]).sum()),
                              absolute_contribution_share=float(np.abs(contribution[mask]).sum()/absolute) if absolute else None))
    return result,contribution,queues,top,quadrants


def glad_allocations(unit,name,cells,fractions):
    rows = []
    g,h,coverage = [cells[k].to_numpy(dtype="float64") for k in ["g","h","glad_pair_coverage_fraction"]]
    for scheme,weight in fractions.items():
        w = g*weight
        mass,paired = float(w.sum()),float(np.dot(w,coverage))
        numerator = float(np.dot(w,h))
        for cls in CLASSES:
            frac = cells[f"glad_{cls}_fraction"].to_numpy(dtype="float64")
            allocated = float(np.dot(w,frac))
            depth = float(np.dot(w*h,frac))
            rows.append(dict(unit_key=unit,eFUA_name=name,scheme=scheme,glad_pair_class=cls,
                             total_allocated_surface_m2=mass,paired_covered_allocated_surface_m2=paired,
                             allocated_surface_times_glad_class_fraction_m2=allocated,
                             glad_class_share_of_allocation=allocated/mass if mass else None,
                             glad_class_share_on_paired_coverage=allocated/paired if paired and cls != "missing_pair" else None,
                             depth_proxy_times_glad_class_fraction_m3=depth,
                             glad_class_share_of_depth_proxy=depth/numerator if numerator else None))
    return rows


def main():
    start=time.perf_counter()
    OUT.mkdir(parents=True,exist_ok=True)
    frozen = {}
    for label,file in [("JFA","joint_overlay_verification.json"),("GLAD","glad_verification.json")]:
        path = WORK / "results" / file
        data=json.loads(path.read_text(encoding="utf-8"))
        if not data["all_passed"]:
            raise RuntimeError(f"Input freeze not passed: {label}")
        frozen[label]=dict(path=str(path),sha256=sha256(path),all_passed=True)
    frozen_cities=pd.read_csv(WORK/'results/joint_overlay_city_summary.csv').set_index('unit_key')
    names=frozen_cities.eFUA_name.to_dict()
    joint_paths=sorted(JOINT.glob('*_positive_cells.parquet'))
    if len(joint_paths) != 91 or len(list(GLAD.glob('*.parquet'))) != 91:
        raise RuntimeError('Expected exactly 91 city files in each input product')
    alignment=[]; decomposition=[]; queue=[]; tops=[]; quadrants=[]; exposures=[]; exposure_decomp=[]; glads=[]; all_cells=[]; sources=[]
    for path in joint_paths:
        unit=path.name.removesuffix('_positive_cells.parquet')
        other=GLAD/f'{unit}.parquet'
        j=pd.read_parquet(path).sort_values(KEY).reset_index(drop=True)
        z=pd.read_parquet(other).sort_values(KEY).reset_index(drop=True)
        if j.duplicated(KEY).any() or z.duplicated(KEY).any() or not j[KEY].equals(z[KEY]):
            raise RuntimeError(f'Cell support mismatch or duplicate: {unit}')
        for column in ['added_surface_m2','integrated_modelled_depth_m','center_x_mollweide_m','center_y_mollweide_m']:
            if not np.array_equal(j[column].to_numpy(),z[column].to_numpy()):
                raise RuntimeError(f'Shared cell values differ: {unit}: {column}')
        s,p,t=[j[c].to_numpy(dtype='float64') for c in ['fine_s_fraction','fine_p_fraction','joint_overlay_fraction']]
        f=s*(1-p)
        a=j.endpoint_support_fraction.to_numpy(dtype='float64')*(1-j.preexisting_detected_fraction.to_numpy(dtype='float64'))
        cov=s-t-s*p
        gladcols=[f'glad_{cls}_fraction' for cls in CLASSES]+['glad_pair_coverage_fraction']
        cells=j[KEY].copy()
        cells['eFUA_name']=names[unit]
        cells['g']=j.added_surface_m2.to_numpy(dtype='float64')
        cells['h']=j.integrated_modelled_depth_m.to_numpy(dtype='float64')
        for column in ['center_x_mollweide_m','center_y_mollweide_m']:
            cells[column]=j[column].to_numpy(dtype='float64')
        for label,value in [('t',t),('s',s),('p',p),('f',f),('a',a),('cov_SP',cov),('cell_difference_t_minus_f',t-f)]:
            cells[label]=value
        for column in gladcols:
            cells[column]=z[column].to_numpy(dtype='float64')
        if not np.isfinite(cells.select_dtypes('number').to_numpy()).all() or (cells.g <= 0).any() or (cells.h < 0).any():
            raise RuntimeError(f'Invalid numerical support: {unit}')
        for values in [s,p,t,a]+[cells[c].to_numpy() for c in gladcols]:
            if np.min(values) < -1e-7 or np.max(values) > 1+1e-7:
                raise RuntimeError(f'Fraction outside [0,1]: {unit}')
        partition=float(np.max(np.abs(cells[[f'glad_{cls}_fraction' for cls in CLASSES]].sum(axis=1)-1)))
        missing_coverage=float(np.max(np.abs(1-cells.glad_missing_pair_fraction-cells.glad_pair_coverage_fraction)))
        bounds=max(float(np.max(np.maximum(0,s-p)-t)),float(np.max(t-np.minimum(s,1-p))),0.)
        if partition > 1e-6 or missing_coverage > 1e-6 or bounds > 1e-6:
            raise RuntimeError(f'Fraction partition, coverage or bound failure: {unit}')
        alignment.append(dict(unit_key=unit,cells=len(cells),same_unique_cell_keys=True,same_g_h_and_centers=True,
                              glad_five_class_partition_max_error=partition,glad_missing_plus_coverage_max_error=missing_coverage,
                              glad_missing_cells=int((cells.glad_missing_pair_fraction > 0).sum()),
                              glad_pair_coverage_minimum=float(cells.glad_pair_coverage_fraction.min()),
                              fine_frechet_max_violation=bounds,
                              stored_F_recomputed_max_error=float(np.max(np.abs(j.fine_product_fraction-f))),
                              stored_A_recomputed_max_error=float(np.max(np.abs(j.archived_product_fraction-a)))))
        d,c,q,top,quad=decompose(unit,names[unit],cells)
        cells['city_normalized_difference_contribution_m']=c
        fractions=dict(G=np.ones(len(cells)),J=t,F=f,A=a)
        ex=allocation_components(unit,names[unit],cells.g.to_numpy(),cells.h.to_numpy(),fractions)
        for record in ex:
            if record['scheme'] == 'G':
                continue
            prefix={'J':'joint_overlay','F':'fine_product','A':'archived_product'}[record['scheme']]
            for current,previous in [('allocated_surface_m2',f'{prefix}_allocated_surface_m2'),('depth_weighted_proxy_m3',f'{prefix}_depth_weighted_proxy_m3'),('normalized_mean_depth_m',f'{prefix}_normalized_city_depth_m')]:
                if not np.isclose(record[current],frozen_cities.loc[unit,previous],rtol=1e-12,atol=1e-9):
                    raise RuntimeError(f'Derived allocation differs from frozen summary: {unit} {record["scheme"]} {current}')
        decomposition.append(d); queue.extend(q); tops.append(top); quadrants.extend(quad)
        exposures.extend(ex); exposure_decomp.append(symmetric_depth_decomposition(ex))
        glads.extend(glad_allocations(unit,names[unit],cells,fractions)); all_cells.append(cells)
        for label,src in [('JFA',path),('GLAD',other)]:
            sources.append(dict(product=label,unit_key=unit,path=str(src),sha256=sha256(src),bytes=src.stat().st_size))
        print(f'DIAGNOSTIC_CITY {unit} n={len(cells)} delta_m={d["observed_EJ_minus_EF_m"]:.8f}',flush=True)
    all_cells=pd.concat(all_cells,ignore_index=True).sort_values(KEY).reset_index(drop=True)
    pooled,contribution,q,top,quad=decompose('ALL91_POOLED','Pooled 91-city allocation',all_cells)
    all_cells['pooled_normalized_difference_contribution_m']=contribution
    queue.extend(q); tops.append(top); quadrants.extend(quad)
    fractions=dict(G=np.ones(len(all_cells)),J=all_cells.t.to_numpy(),F=all_cells.f.to_numpy(),A=all_cells.a.to_numpy())
    ex=allocation_components('ALL91_POOLED','Pooled 91-city allocation',all_cells.g.to_numpy(),all_cells.h.to_numpy(),fractions)
    exposures.extend(ex); exposure_decomp.append(symmetric_depth_decomposition(ex))
    glads.extend(glad_allocations('ALL91_POOLED','Pooled 91-city allocation',all_cells,fractions))
    frames={
        'city_decomposition':pd.DataFrame(decomposition),
        'queue_coverage':pd.DataFrame(queue),'top_effect_cells':pd.concat(tops,ignore_index=True),
        'covariance_depth_quadrants':pd.DataFrame(quadrants),'exposure_components':pd.DataFrame(exposures),
        'exposure_JF_symmetric_decomposition':pd.DataFrame(exposure_decomp),
        'glad_class_allocation':pd.DataFrame(glads),'cell_alignment_checks':pd.DataFrame(alignment)}
    original_names=['Delhi [New Delhi]','Guwahati','Sultanpur']
    original_ex=[row for name in original_names for scheme in SCHEMES for row in exposures if row['eFUA_name']==name and row['scheme']==scheme]
    frames['original_three_case_exposure_components']=pd.DataFrame(original_ex)
    base_mass=frames['glad_class_allocation'].query('scheme == "G"')[['unit_key','glad_pair_class','allocated_surface_times_glad_class_fraction_m2']].rename(columns={'allocated_surface_times_glad_class_fraction_m2':'G_glad_class_mass_m2'})
    retained=frames['glad_class_allocation'].merge(base_mass,on=['unit_key','glad_pair_class'],validate='many_to_one')
    retained['absolute_G_class_mass_retention_fraction']=retained.allocated_surface_times_glad_class_fraction_m2/retained.G_glad_class_mass_m2.replace(0,np.nan)
    pooled_retained=retained[(retained.unit_key=='ALL91_POOLED') & retained.scheme.isin(['J','F','A']) & retained.glad_pair_class.isin(['new_built','stable_built','absent_both'])].copy()
    frames['glad_pooled_class_mass_retention']=pooled_retained[['scheme','glad_pair_class','G_glad_class_mass_m2','allocated_surface_times_glad_class_fraction_m2','absolute_G_class_mass_retention_fraction']]
    for label,frame in frames.items():
        frame.to_csv(OUT/f'diagnostics_{label}.csv',index=False)
    all_cells.to_parquet(OUT/'diagnostics_cell_contributions.parquet',index=False,compression='zstd')
    case_names=['Delhi [New Delhi]','Guwahati','Sultanpur','Srinagar','Nashik']
    caseframe=frames['city_decomposition'][frames['city_decomposition'].eFUA_name.isin(case_names)].copy()
    caseframe.to_csv(OUT/'diagnostics_posthoc_five_cases.csv',index=False)
    verification=dict(all_passed=True,cities=len(decomposition),cells=len(all_cells),
        max_city_normalized_identity_error_m=float(frames['city_decomposition'].normalized_difference_identity_residual_m.abs().max()),
        pooled_normalized_identity_error_m=abs(pooled['normalized_difference_identity_residual_m']),
        max_cell_covariance_identity_error=float(frames['city_decomposition'].covariance_identity_max_cell_error.max()),
        max_exposure_product_identity_error_m=float(frames['exposure_components'].product_identity_residual_m.abs().max()),
        max_symmetric_exposure_identity_error_m=float(frames['exposure_JF_symmetric_decomposition'].symmetric_identity_residual_m.abs().max()),
        all_exact_unique_aligned_keys=True,all_same_g_h_and_centers=True,
        all_JFA_allocations_match_frozen_city_summary=True,
        glad_missing_cells=int(frames['cell_alignment_checks'].glad_missing_cells.sum()),
        glad_minimum_pair_coverage=float(frames['cell_alignment_checks'].glad_pair_coverage_minimum.min()),
        glad_partition_max_error=float(frames['cell_alignment_checks'].glad_five_class_partition_max_error.max()),
        symmetric_decomposition_undefined_scopes=int((~frames['exposure_JF_symmetric_decomposition'].decomposition_defined_both_nonzero).sum()))
    verification['undefined_conditional_mean_scope_schemes']=int((~frames['exposure_components'].conditional_mean_defined).sum())
    zero_checks=frames['exposure_components'].zero_support_mean_check_passed.dropna()
    verification['all_zero_support_means_checked_as_zero']=bool(zero_checks.all())
    if any(verification[k] > 1e-10 for k in ['max_city_normalized_identity_error_m','pooled_normalized_identity_error_m','max_cell_covariance_identity_error','max_exposure_product_identity_error_m','max_symmetric_exposure_identity_error_m']):
        verification['all_passed']=False
    summary=dict(completed_utc=datetime.now(timezone.utc).isoformat(),version='representation_diagnostics_20261007_v1',
                 elapsed_seconds=round(time.perf_counter()-start,3),verification=verification,pooled_decomposition=pooled,
                 pooled_exposure_components=ex,pooled_exposure_JF_symmetric_decomposition=exposure_decomp[-1],
                 pooled_queue_coverage=q,
                 pooled_glad_class_allocation=[x for x in glads if x['unit_key']=='ALL91_POOLED'],
                 original_three_case_exposure_components=original_ex,
                 original_three_case_symmetric_decomposition=[x for x in exposure_decomp if x['eFUA_name'] in original_names],
                 pooled_glad_class_mass_retention=json.loads(frames['glad_pooled_class_mass_retention'].to_json(orient='records')),
                 posthoc_five_cases=json.loads(caseframe.to_json(orient='records')),
                 covariance_note='Cov(S,P)=E[SP]-sp, with E[SP]=s-t reconstructed from stored map-specific joint fractions. This is an algebraic audit, not an independent native reread.',
                 queue_rules='All g>0 cells eligible, including h=0. Budgets min(10,n), ceil(.01*n), ceil(.10*n). Stable descending sort by absolute normalized difference contribution or g*h; ties by unit_key,row,column. Pooled queue uses pooled EF and AJ; city queue uses its own EF and AJ.',
                 scope_note='The original three cities were selected before the preceding added analyses. The present five-city mechanism illustrations are post hoc diagnostic interpretations, with Srinagar and Nashik added because of observed differences. This does not change the earlier selection timeline. All 91 cities remain reported. GLAD allocation is cross-product consistency and has no accuracy interpretation.',
                 model_nonzero_note='h>0 means support with nonzero modelled integrated depth, not observed inundation, actual flooded area, or event probability.')
    (OUT/'diagnostics_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    manifest=dict(script=str(Path(__file__)),script_sha256=sha256(Path(__file__)),frozen_input_audits=frozen,
                  inputs=sources,runtime=dict(python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__),
                  no_original_source_reads=True,no_new_raw_downloads=True,outputs_directory=str(OUT))
    (OUT/'diagnostics_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    report=f'''# Representation diagnostics, 2026-10-07

All 91 cities and {len(all_cells):,} positive GHSL-increment cells are included. All J/F/A and GLAD cell keys are unique and match exactly, as do g, integrated modelled depth h and cell centres. GLAD five-class partition maximum error is {verification['glad_partition_max_error']:.3g}; missing cells={verification['glad_missing_cells']}, minimum pair coverage={verification['glad_minimum_pair_coverage']}. No new raw material was downloaded or read.

For the retained fine-grid map conventions, t=E[S(1-P)], so E[SP]=s-t and t-s(1-p)=-(E[SP]-sp)=-Cov(S,P). Covariance is reconstructed from stored t/s/p, so this identity check is algebraic rather than an independent native overlay validation. The independent native overlay audit remains the prior frozen input.

With f=s(1-p), A_J=sum(gt), E_J=sum(gth)/A_J and E_F=sum(gfh)/sum(gf), the exact centered decomposition is E_J-E_F=sum[g(t-f)(h-E_F)]/A_J. Each cell contributes c_i=g_i(t_i-f_i)(h_i-E_F)/A_J, in metres. City and pooled normalizers are kept separate. Maximum city identity residual={verification['max_city_normalized_identity_error_m']:.3g} m; pooled residual={verification['pooled_normalized_identity_error_m']:.3g} m.

The pooled J-F shift is {pooled['observed_EJ_minus_EF_m']:.9f} m, comprising positive contributions {pooled['positive_contributions_sum_m']:.9f} m and negative contributions {pooled['negative_contributions_sum_m']:.9f} m. Absolute-contribution mass is {pooled['absolute_contributions_sum_m']:.9f} m; cancellation fraction={pooled['cancellation_fraction']:.6f}. A small signed aggregate therefore need not mean small local representation differences.

Cell-budget queues use top 10 cells, top 1% cells (ceiling), and top 10% cells (ceiling), all drawn from g>0 cells including h=0. The representation queue sorts |c_i|; the standard queue sorts g_i*h_i. Ties are resolved by unit_key/grid_row/grid_column. Each queue reports the fraction of total |c| and total g*h it covers, plus queue overlap. These answer different deterministic auditing questions; the representation queue is not validated as a better hazard-monitoring queue. Pooled queues centre on pooled E_F; city queues centre on their city E_F.

Exposure is also decomposed into scale W=sum(w), model-nonzero-depth-supported allocation Wplus=sum(w*1[h>0]), depth numerator N=sum(wh), support share pplus=Wplus/W, conditional modelled depth muplus=N/Wplus, and E=N/W=pplus*muplus. Here w is g, gt, gf or g*a. h>0 denotes nonzero modelled integrated depth support, not actual inundation area or event risk. If Wplus=0, conditional depth is undefined; E is zero when W>0 and N=0. The symmetric J-F identity is deltaE=(pJ-pF)*(muJ+muF)/2+(muJ-muF)*(pJ+pF)/2, computed only where both conditional means exist. Undefined scopes={verification['symmetric_decomposition_undefined_scopes']}; maximum identity residual={verification['max_symmetric_exposure_identity_error_m']:.3g} m.

GLAD allocations multiply the same g/J/F/A weights by native-pair class fractions on precisely the same positive-cell support. They are product-consistency associations, not true-positive rates, roof-accuracy measures, construction-date validation or source independence. Both allocated-surface and depth-proxy class shares are reported; paired-coverage shares explicitly retain their denominator, and missing is shown as its own class.

Delhi, Guwahati and Sultanpur were selected before the preceding added analyses. The present five-city mechanism illustrations are diagnostic post hoc interpretations, with Srinagar and Nashik added because of observed differences. These are distinct selection timelines; the current diagnostic interpretation does not change the earlier selection record. Their full rows and all remaining cities are retained. Covariance/depth quadrant counts use covariance tolerance {COV_TOL:g}; near-zero cases remain in exact contribution totals.

## Compact results

Across the pooled allocation, nonzero model-depth support shares are J={ex[1]['model_nonzero_depth_support_share']:.8f}, F={ex[2]['model_nonzero_depth_support_share']:.8f}, and conditional depths are J={ex[1]['conditional_model_nonzero_mean_depth_m']:.8f} m, F={ex[2]['conditional_model_nonzero_mean_depth_m']:.8f} m. The symmetric difference comprises a support-share term {exposure_decomp[-1]['model_nonzero_support_share_term_m']:.9f} m and a conditional-depth term {exposure_decomp[-1]['conditional_model_depth_term_m']:.9f} m. In the six cities without nonzero J/F model-depth support, both means E are zero and both conditional depths remain undefined; the symmetric conditional-mean decomposition is omitted.

The pooled top1% representation queue covers {q[2]['absolute_representation_effect_coverage']:.4%} of absolute centered effects and {q[2]['standard_depth_proxy_mass_coverage']:.4%} of standard g*h mass. The same-budget standard queue covers {q[3]['absolute_representation_effect_coverage']:.4%} of those effects and {q[3]['standard_depth_proxy_mass_coverage']:.4%} of g*h mass; queue overlap is {q[2]['queue_overlap_fraction']:.4%}. This follows from their different sorting objectives and is not evidence of a superior hazard queue.

Post hoc five-case centered differences and concentrations:

{markdown_table(caseframe[['eFUA_name','observed_EJ_minus_EF_m','positive_contributions_sum_m','negative_contributions_sum_m','absolute_contribution_concentration_top1pct_cells']])}

Original three-case scale, support and depth components (Cplus is the model-nonzero support share; Dplus is the conditional modelled depth):

{markdown_table(frames['original_three_case_exposure_components'][['eFUA_name','scheme','allocated_surface_m2','allocated_surface_on_model_nonzero_depth_support_m2','model_nonzero_depth_support_share','conditional_model_nonzero_mean_depth_m','normalized_mean_depth_m']].rename(columns={'allocated_surface_m2':'W_m2','allocated_surface_on_model_nonzero_depth_support_m2':'Wplus_m2','model_nonzero_depth_support_share':'Cplus','conditional_model_nonzero_mean_depth_m':'Dplus_m','normalized_mean_depth_m':'E_m'}))}

GLAD class absolute mass retained by J/F/A relative to the unscreened g-weighted mass in that same class:

{markdown_table(frames['glad_pooled_class_mass_retention'])}

A larger GLAD-new composition share does not imply larger retained absolute class mass, and neither measure is mapping accuracy. Denominators and absolute masses are therefore reported together.

Outputs: diagnostics_city_decomposition.csv; diagnostics_queue_coverage.csv; diagnostics_top_effect_cells.csv; diagnostics_covariance_depth_quadrants.csv; diagnostics_exposure_components.csv; diagnostics_exposure_JF_symmetric_decomposition.csv; diagnostics_glad_class_allocation.csv; diagnostics_posthoc_five_cases.csv; diagnostics_cell_contributions.parquet; diagnostics_cell_alignment_checks.csv; diagnostics_summary.json; diagnostics_manifest.json.

Reproduce: `python -u "{Path(__file__)}"`. All computations and outputs are on D:. Source input SHA256 values are retained in the manifest.
'''
    (OUT/'diagnostics_report.md').write_text(report,encoding='utf-8')
    if not verification['all_passed']:
        raise RuntimeError('Diagnostic algebra audit failed')
    print('DIAGNOSTICS_ALL_DONE '+json.dumps(verification),flush=True)


if __name__ == '__main__':
    main()
