"""Computational six-cell dossiers, not human imagery verification."""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

WORK=Path(r"D:\MLWork\IUFEE_revision_20261005")
OUT=WORK/'results/revision_20261007'
QUEUE=WORK/'results/revision_case_review_queue.csv'
TEX=WORK/'manuscript/case_dossiers_table.tex'
KEY=['unit_key','grid_row','grid_column']
QA=['glofas_permanent_water_qa','glofas_spurious_depth_qa']
RP=[f'RP{x}_depth_m' for x in [10,20,50,75,100,200,500]]
GLAD=[f'glad_{x}_fraction' for x in ['new_built','stable_built','absent_both','built_loss','missing_pair']]+['glad_pair_coverage_fraction']


def sha256(path):
    digest=hashlib.sha256()
    with open(path,'rb') as stream:
        for data in iter(lambda:stream.read(1048576),b''):
            digest.update(data)
    return digest.hexdigest().upper()


def notes(row):
    statements=[
        f"Original {row.city} g*h queue order {int(row.review_order)}; cell ({int(row.grid_row)},{int(row.grid_column)}), centre ({row.center_longitude:.6f} E, {row.center_latitude:.6f} N).",
        f"GHSL positive increment g={row.added_surface_m2:.0f} m2 and released integrated modelled depth h={row.integrated_modelled_depth_m:.6f} m; neither gives a realised flood observation.",
        f"Map-specific common-grid joint fraction t={row.fine_joint_t_fraction:.6f}; fine marginal product={row.fine_product_f_fraction:.6f}, archived product={row.archived_product_a_fraction:.6f}. Archive sA={row.archive_sA_fraction:.6f}, pA={row.archive_pA_fraction:.6f}; common-grid sF={row.fine_sF_fraction:.6f}, pF={row.fine_pF_fraction:.6f}.",
        f"GLAD pair new/stable/absent={row.glad_new_built_fraction:.4%}/{row.glad_stable_built_fraction:.4%}/{row.glad_absent_both_fraction:.4%}; paired coverage={row.glad_pair_coverage_fraction:.6f}. These are broad built-up class fractions, not roof-area accuracy."]
    if row.glad_stable_built_fraction > .999 and row.glad_new_built_fraction < 1e-6:
        statements.append('Positive GHSL increment coincides with GLAD stable built-up across this cell. Review focus: densification, within-cell roof increment, differing built-up definitions, registration and temporal detection; the data do not identify which explanation holds.')
    elif row.glad_absent_both_fraction > .5:
        statements.append('More than half the cell is GLAD absent-both despite a positive GHSL increment. Review focus: native building/settlement evidence and the mismatch between roof increments and broad built-up presence. This is a cross-product disagreement, not a confirmed GHSL error.')
    else:
        statements.append('The GLAD pair is mixed. Review focus: inspect native class geometry and temporal definitions before interpreting the increment as new construction.')
    if row.glofas_permanent_water_qa > 0 or row.glofas_spurious_depth_qa > 0:
        statements.append(f'Source model QA is positive: permanent-water={row.glofas_permanent_water_qa:g}, spurious-depth={row.glofas_spurious_depth_qa:g}. Review focus: source QA mask and depth support; flag positivity does not establish an observed flood or justify silently deleting this cell.')
    else:
        statements.append('Both retained source QA values are zero; this is not an independent accuracy certificate.')
    if row.RP_depth_decrease_count > 0:
        statements.append(f'The stored RP10--RP500 depth vector has {int(row.RP_depth_decrease_count)} decreasing step(s), largest decline {row.RP_max_decrease_m:.6f} m. Review focus: source RP fields and QA; this dossier preserves the released integrated depth without correction.')
    if row.endpoint_undocumented_fraction > 0:
        statements.append(f'Undocumented endpoint fraction={row.endpoint_undocumented_fraction:.6f}; it remains outside documented settlement support.')
    statements.append('This dossier performs key/value and formula checks only. No human imagery interpretation, independent reference label, construction truth or actual inundation verification was performed.')
    return ' '.join(statements)


def latex_table(cells,coverage):
    header=r'City & Order & $ (\lambda,\phi)$ & $g$ (m$^2$) & $h$ (m) & $t$ & \shortstack{GLAD new\\(\%)} & \shortstack{GLAD stable\\(\%)} & \shortstack{QA\\PW/SP} \\'
    lines=[r'% Generated computational dossiers; requires longtable. No human image verification.',
           r'\begingroup',r'\footnotesize',r'\setlength{\tabcolsep}{3pt}',
           r'\begin{longtable}{@{}llcrrrrrc@{}}',
           r'\caption{Selected cells from the original three-city $g h$ review queue.}\label{tab:case-dossiers}\\',
           r'\hline',header,r'\hline',r'\endfirsthead',
           r'\multicolumn{9}{l}{\tablename\ \thetable\ (continued)}\\',r'\hline',header,r'\hline',r'\endhead',
           r'\hline',r'\endfoot']
    for row in cells.itertuples(index=False):
        lines.append(f"{row.city} & {int(row.review_order)} & $({row.center_longitude:.5f},{row.center_latitude:.5f})$ & {row.added_surface_m2:.0f} & {row.integrated_modelled_depth_m:.3f} & {row.fine_joint_t_fraction:.3f} & {row.glad_new_built_fraction*100:.1f} & {row.glad_stable_built_fraction*100:.1f} & {row.glofas_permanent_water_qa:g}/{row.glofas_spurious_depth_qa:g} "+r'\\')
    lines += [r'\end{longtable}',r'\endgroup',
              r'\noindent\textit{Notes.} Coordinates are cell-centre longitude and latitude in degrees. Orders are retained from the original descending $g_i h_i$ queue; Guwahati orders 9 and 10 were chosen because their source QA is positive. $g$ is positive GHSL building-surface increment, $h$ is released integrated modelled depth, and $t$ is the common-grid map-specific joint fraction. GLAD columns are pair-class presence fractions, not roof accuracy. QA entries are permanent-water (PW) and spurious-depth (SP) source values. These computational dossiers do not report manual image validation.']
    lookup=coverage.set_index('city')
    lines.append('The original top-ten $g h$ queue accounts for '+', '.join(f"{lookup.loc[city,'top10_g_h_fraction_of_city_total']*100:.3f}\\% in {city}" for city in ['Delhi','Guwahati','Sultanpur'])+r" of each city's $\sum_i g_i h_i$. These are coverage shares of a modelled depth proxy, not shares of actual flood losses or mapping accuracy.")
    return '\n'.join(lines)+'\n'


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    original=pd.read_csv(QUEUE)
    if original.duplicated(KEY).any():
        raise RuntimeError('Original review queue has duplicate cell keys')
    coverage=[]; dossiers=[]; inputs=[dict(path=str(QUEUE),sha256=sha256(QUEUE))]
    for city in ['Delhi','Guwahati','Sultanpur']:
        queue=original[original.city==city].sort_values('review_order')
        if len(queue)!=10 or queue.review_order.tolist()!=list(range(1,11)):
            raise RuntimeError(f'Expected original ten-cell queue: {city}')
        unit=queue.unit_key.unique()
        if len(unit)!=1:
            raise RuntimeError(f'Multiple units in city queue: {city}')
        path=WORK/'datasets/joint_overlay'/f'{unit[0]}_positive_cells.parquet'
        canonical=pd.read_parquet(path)
        if canonical.duplicated(KEY).any():
            raise RuntimeError(f'Duplicate canonical keys: {city}')
        inputs.append(dict(path=str(path),sha256=sha256(path)))
        joined=queue.merge(canonical,on=KEY,how='left',validate='one_to_one',suffixes=('_queue',''))
        if joined.added_surface_m2.isna().any():
            raise RuntimeError(f'Queue cell absent from canonical support: {city}')
        for column in ['added_surface_m2','integrated_modelled_depth_m','center_x_mollweide_m','center_y_mollweide_m']+QA+RP:
            if not np.allclose(joined[column+'_queue'],joined[column],rtol=1e-10,atol=1e-10):
                raise RuntimeError(f'Rounded queue/canonical value mismatch: {city}: {column}')
        glad_path=WORK/'results/glad_cell_fractions'/f'{unit[0]}.parquet'
        glad=pd.read_parquet(glad_path,columns=KEY+GLAD)
        if glad.duplicated(KEY).any():
            raise RuntimeError(f'Duplicate canonical GLAD keys: {city}')
        matched_glad=joined[KEY].merge(glad,on=KEY,how='left',validate='one_to_one')
        if matched_glad[GLAD].isna().any().any():
            raise RuntimeError(f'Missing canonical GLAD cell: {city}')
        for column in GLAD:
            if not np.allclose(joined[column],matched_glad[column],rtol=1e-10,atol=1e-10):
                raise RuntimeError(f'Rounded queue/canonical GLAD mismatch: {city}: {column}')
            joined[column]=matched_glad[column].to_numpy()
        inputs.append(dict(path=str(glad_path),sha256=sha256(glad_path)))
        exact_score=canonical.added_surface_m2.astype('float64')*canonical.integrated_modelled_depth_m.astype('float64')
        ordered=canonical.assign(exact_score=exact_score).sort_values(['exact_score']+KEY,ascending=[False,True,True,True]).head(10)
        if set(map(tuple,queue[KEY].to_numpy()))!=set(map(tuple,ordered[KEY].to_numpy())):
            raise RuntimeError(f'Original queue is not the exact top ten under g*h: {city}')
        top_mass=float((joined.added_surface_m2.astype('float64')*joined.integrated_modelled_depth_m.astype('float64')).sum())
        full_mass=float(exact_score.sum())
        existing=pd.read_csv(OUT/'diagnostics_queue_coverage.csv')
        comparison=existing[(existing.unit_key==unit[0])&(existing.budget_rule=='top10_cells')&(existing.queue=='standard_g_times_h')].iloc[0]
        share=top_mass/full_mass
        if not np.isclose(share,comparison.standard_depth_proxy_mass_coverage,rtol=1e-12,atol=1e-12):
            raise RuntimeError(f'Top-ten coverage differs from diagnostics: {city}')
        coverage.append(dict(city=city,unit_key=unit[0],original_top10_cells=10,
                             top10_g_h_proxy_m3=top_mass,city_total_g_h_proxy_m3=full_mass,
                             top10_g_h_fraction_of_city_total=share,exact_top10_cell_set_matches=True,
                             matches_existing_diagnostic_coverage=True))
        if city=='Guwahati':
            chosen=joined[(joined.glofas_permanent_water_qa>0)|(joined.glofas_spurious_depth_qa>0)].head(2)
            if len(chosen)!=2:
                raise RuntimeError('Fewer than two QA-positive Guwahati cells in original top ten')
        else:
            chosen=joined.head(2)
        selected=chosen[KEY+['city','review_order','center_longitude','center_latitude','center_x_mollweide_m','center_y_mollweide_m','added_surface_m2','integrated_modelled_depth_m','endpoint_undocumented_fraction']+QA+RP+GLAD].copy()
        selected['archive_sA_fraction']=chosen.endpoint_support_fraction.to_numpy()
        selected['archive_pA_fraction']=chosen.preexisting_detected_fraction.to_numpy()
        selected['archive_qA_conditional_settlement_fraction']=chosen.endpoint_settlement_fraction.to_numpy()
        selected['archive_documented_fraction']=chosen.endpoint_documented_fraction.to_numpy()
        selected['fine_sF_fraction']=chosen.fine_s_fraction.to_numpy()
        selected['fine_pF_fraction']=chosen.fine_p_fraction.to_numpy()
        selected['fine_uF_fraction']=chosen.fine_u_fraction.to_numpy()
        selected['fine_joint_t_fraction']=chosen.joint_overlay_fraction.to_numpy()
        selected['fine_product_f_fraction']=selected.fine_sF_fraction.astype('float64')*(1-selected.fine_pF_fraction.astype('float64'))
        selected['archived_product_a_fraction']=selected.archive_sA_fraction.astype('float64')*(1-selected.archive_pA_fraction.astype('float64'))
        selected['original_queue_review_score_m3']=chosen.review_score_m3.to_numpy()
        selected['canonical_g_h_proxy_m3']=selected.added_surface_m2.astype('float64')*selected.integrated_modelled_depth_m.astype('float64')
        decreases=-np.diff(selected[RP].to_numpy(dtype='float64'),axis=1)
        selected['RP_depth_decrease_count']=(decreases>1e-6).sum(axis=1)
        selected['RP_max_decrease_m']=np.maximum(decreases.max(axis=1),0)
        selected['selection_reason']='first two original g*h queue cells' if city!='Guwahati' else 'first two QA-positive cells among original top ten'
        selected['computational_source_review_notes']=[notes(r) for r in selected.itertuples(index=False)]
        selected['human_imagery_review_performed']=False
        selected['independent_truth_validation_performed']=False
        dossiers.append(selected)
    cells=pd.concat(dossiers,ignore_index=True)
    coverage=pd.DataFrame(coverage)
    cells.to_csv(OUT/'case_dossiers_cells.csv',index=False)
    coverage.to_csv(OUT/'case_dossiers_queue_coverage.csv',index=False)
    TEX.write_text(latex_table(cells,coverage),encoding='utf-8')
    summary=dict(completed_utc=datetime.now(timezone.utc).isoformat(),selected_cells=6,
                 input_manifest=inputs,script_sha256=sha256(Path(__file__)),
                 selection_timeline='The original three cities preceded the earlier added analyses; this six-cell dossier is a post hoc computational review. Original queue order is unchanged.',
                 all_key_value_checks_passed=True,source_notes_generated_computationally=True,
                 human_imagery_review_performed=False,independent_truth_validation_performed=False,
                 queue_coverage=json.loads(coverage.to_json(orient='records')),
                 cells=json.loads(cells.to_json(orient='records',double_precision=15)),latex_path=str(TEX),
                 coordinate_note='Existing queue cell-centre longitude/latitude retained; canonical Mollweide centres checked to match. No site visit or visual geolocation claim.')
    (OUT/'case_dossiers_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(cells[['city','review_order','added_surface_m2','integrated_modelled_depth_m','fine_joint_t_fraction','glad_new_built_fraction','glad_stable_built_fraction','glofas_permanent_water_qa','RP_depth_decrease_count','RP_max_decrease_m']].to_csv(index=False))
    print(coverage.to_csv(index=False))


if __name__=='__main__':
    main()
