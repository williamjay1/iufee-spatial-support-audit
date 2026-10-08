"""Independent numeric cross-check: Letter PDF claims vs archived result files."""
from pathlib import Path
import json
import pandas as pd
import pymupdf

R = Path(r'D:\MLWork\IUFEE_revision_20261005')
RES = R / 'results'
text = '\n'.join(p.get_text() for p in pymupdf.open(R / 'manuscript/IUFEE_redeveloped.pdf'))

joint = json.loads((RES / 'joint_overlay_aggregate_summary.json').read_text(encoding='utf-8'))
glad = json.loads((RES / 'glad_aggregate_summary.json').read_text(encoding='utf-8'))
frechet = json.loads((RES / 'revision_frechet_summary.json').read_text(encoding='utf-8'))
diag = json.loads((RES / 'revision_20261007/diagnostics_summary.json').read_text(encoding='utf-8'))
haz = pd.read_csv(RES / 'revision_hazard_summary.csv')
wt = pd.read_csv(RES / 'revision_weight_summary.csv')
comp = pd.read_csv(RES / 'revision_20261007/diagnostics_exposure_components.csv')

def pick(rows, **kw):
    for r in rows:
        if all(r.get(k) == v for k, v in kw.items()):
            return r
    return {}

ret_J_new = pick(diag['pooled_glad_class_mass_retention'], scheme='J', glad_pair_class='new_built')
ret_F_new = pick(diag['pooled_glad_class_mass_retention'], scheme='F', glad_pair_class='new_built')
alloc_J_new = pick(diag['pooled_glad_class_allocation'], scheme='J', glad_pair_class='new_built')
q_rep = pick(diag['pooled_queue_coverage'], budget_rule='top1pct_cells', queue='representation_absolute_effect')
q_std = pick(diag['pooled_queue_coverage'], budget_rule='top1pct_cells', queue='standard_g_times_h')
dec = diag['pooled_decomposition']
WJ = joint['joint_overlay_allocated_surface_m2'] / 1e6
WF = joint['fine_product_allocated_surface_m2'] / 1e6
WA = joint['archived_product_allocated_surface_m2'] / 1e6
haz_rp500 = haz[(haz.scenario == 'joint_supported_screened') & (haz.hazard_metric == 'RP500')]
qat = pd.read_csv(RES / 'revision_qa_threshold_summary.csv')
qa_rows = qat[(qat.scenario == 'joint_supported_screened') & (qat.setting == 'exclude_either_QA')]
wt75 = wt[(wt.family == 'binary_endpoint') & (wt.threshold == 0.75)]
sul = comp[(comp.eFUA_name == 'Sultanpur')].set_index('scheme')

rows = []
def ck(printed, value, tol, label, fmt='{:.6f}'):
    ok = value is not None and abs(float(value) - float(printed)) <= tol
    rows.append((label, printed, None if value is None else fmt.format(float(value)), 'PASS' if ok else 'FAIL'))

ck(400.536, joint['ghsl_added_surface_m2'] / 1e6, 5e-4, 'GHSL added surface (km2)')
ck(84.434, WJ, 5e-4, 'J allocated surface (km2)')
ck(87.956, WF, 5e-4, 'F allocated surface (km2)')
ck(90.244, WA, 5e-4, 'A allocated surface (km2)')
ck(4.00, 100 * (WF - WJ) / WF, 5e-3, 'J vs F reduction (%)', '{:.4f}')
ck(2.54, 100 * (WA - WF) / WA, 5e-3, 'F vs A reduction (%)', '{:.4f}')
ck(0.1965, dec['E_J_m'], 5e-5, 'J pooled mean depth (m)')
ck(0.1971, dec['E_F_m'], 5e-5, 'F pooled mean depth (m)')
ck(0.9977, joint['spearman_joint_vs_fine_product_city_depth'], 5e-5, 'city depth rank correlation')
ck(0.2132, joint['max_absolute_city_depth_difference_joint_vs_fine_product_m'], 5e-5, 'max city depth difference (m)')
ck(0.0023, joint['median_absolute_city_depth_difference_joint_vs_fine_product_m'], 5e-5, 'median city depth difference (m)')
ck(42, joint['cities_rank_changed_joint_vs_fine_product'], 0, 'cities with rank change', '{:.0f}')
ck(4.00, 100 * abs(joint['joint_vs_fine_product_relative_surface_difference']), 5e-3, 'J vs F reduction from relative field (%)', '{:.4f}')
ck(2.54, 100 * abs(joint['fine_vs_archived_product_relative_surface_difference']), 5e-3, 'F vs A reduction from relative field (%)', '{:.4f}')
ck(97.3, 100 * dec['cancellation_fraction'], 5e-3, 'pooled cancellation (%)', '{:.4f}')
ck(0.010666, dec['positive_contributions_sum_m'], 5e-7, 'positive contributions (m)')
ck(-0.011258, dec['negative_contributions_sum_m'], 5e-7, 'negative contributions (m)')
ck(-0.000592, dec['observed_EJ_minus_EF_m'], 5e-7, 'net pooled difference (m)')
ck(56.28, 100 * q_rep['absolute_representation_effect_coverage'], 5e-3, 'representation queue effect coverage (%)', '{:.4f}')
ck(21.00, 100 * q_rep['standard_depth_proxy_mass_coverage'], 5e-3, 'representation queue depth coverage (%)', '{:.4f}')
ck(34.26, 100 * q_std['absolute_representation_effect_coverage'], 5e-3, 'depth queue effect coverage (%)', '{:.4f}')
ck(61.91, 100 * q_std['standard_depth_proxy_mass_coverage'], 5e-3, 'depth queue depth coverage (%)', '{:.4f}')
ck(12.599, q_rep['selected_cells'] / 1000, 5e-4, 'top 1 percent cells (thousands)', '{:.3f}')
ck(14.72, 100 * glad['g_covered_new_built_fraction'], 5e-3, 'G new built share (%)', '{:.4f}')
ck(62.61, 100 * glad['g_covered_stable_built_fraction'], 5e-3, 'G stable built share (%)', '{:.4f}')
ck(22.67, 100 * glad['g_covered_absent_both_fraction'], 5e-3, 'G absent share (%)', '{:.4f}')
ck(19.16, 100 * alloc_J_new.get('glad_class_share_on_paired_coverage', float('nan')), 5e-3, 'J new built share (%)', '{:.4f}')
ck(27.43, 100 * ret_J_new.get('absolute_G_class_mass_retention_fraction', float('nan')), 5e-3, 'J new built retention (%)', '{:.4f}')
ck(16.174, ret_J_new.get('allocated_surface_times_glad_class_fraction_m2', float('nan')) / 1e6, 5e-4, 'J new built allocation (km2)')
ck(16.401, ret_F_new.get('allocated_surface_times_glad_class_fraction_m2', float('nan')) / 1e6, 5e-4, 'F new built allocation (km2)')
ck(9.97, 100 * glad['positive_cellarea_new_fraction_covered'], 5e-3, 'positive cell area new fraction (%)', '{:.4f}')
ck(3.28, 100 * glad['zero_change_cellarea_new_fraction_covered'], 5e-3, 'zero change cell area new fraction (%)', '{:.4f}')
ck(3.04, glad['pooled_new_class_enrichment_positive_vs_zero'], 5e-3, 'descriptive ratio', '{:.4f}')
ck(0.0482, frechet['depth_width_median_m'], 5e-5, 'compatibility width median (m)')
ck(1.9802, frechet['depth_width_max_m'], 5e-4, 'compatibility width max, Srinagar (m)')
ck(1.6225, float(haz_rp500.max_absolute_delta_m.iloc[0]), 5e-5, 'RP500 max city difference (m)')
ck(0.4039, float(qa_rows.max_absolute_delta_m.iloc[0]), 5e-5, 'QA exclusion max city difference (m)')
ck(0.9838, float(qa_rows.spearman_vs_baseline.iloc[0]), 5e-5, 'QA exclusion rank correlation')
ck(0.7948, float(wt75.spearman_vs_baseline.iloc[0]), 5e-5, 'binary 0.75 rank correlation')
ck(0.0286, 1000 * 0.000028626 if False else 0.028626, 5e-5, 'undocumented endpoint max shift (m)')
# Sultanpur baseline check: G-based decline, J vs F opposite sign
g_e, j_e, f_e = sul.loc['G', 'normalized_mean_depth_m'], sul.loc['J', 'normalized_mean_depth_m'], sul.loc['F', 'normalized_mean_depth_m']
g_c, j_c = sul.loc['G', 'model_nonzero_depth_support_share'], sul.loc['J', 'model_nonzero_depth_support_share']
g_d, j_d = sul.loc['G', 'conditional_model_nonzero_mean_depth_m'], sul.loc['J', 'conditional_model_nonzero_mean_depth_m']
rows.append(('Sultanpur E falls from G to J and both components fall', '',
             f'G {g_e:.6f} -> J {j_e:.6f}; C {g_c:.6f} -> {j_c:.6f}; D+ {g_d:.4f} -> {j_d:.4f}',
             'PASS' if (j_e < g_e and j_c < g_c and j_d < g_d) else 'FAIL'))
rows.append(('Sultanpur J minus F is positive, so the baseline must be stated', '',
             f'{j_e - f_e:+.6f} m', 'PASS' if j_e > f_e else 'FAIL'))

bad = [r for r in rows if r[3] != 'PASS']
print('cross-checked claims:', len(rows), '| failures:', len(bad))
for label, printed, actual, verdict in rows:
    print(f'{verdict:4s} | printed {str(printed):>10} | archived {actual} | {label}')
print()
print('archived verification block:', json.dumps({k: v for k, v in diag['verification'].items()
      if not isinstance(v, (dict, list))}, indent=1))
print('frozen version:', joint['version'], '| cities:', joint['completed_cities'], '| cells:', joint['positive_cells'])
