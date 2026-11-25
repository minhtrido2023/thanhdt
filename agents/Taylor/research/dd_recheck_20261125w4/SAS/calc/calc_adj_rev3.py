"""SAS rev3 — E17 sau skeptic r1 (PREREG_rev3_addendum_r1.md, khoá trong LOCK_adj_md5.txt TRƯỚC khi chạy).
Dùng lại base của model_sas_rev3.py (runpy; base không đổi). Dùng: python3 calc_adj_rev3.py <calc_r3 đã khôi phục>"""
import contextlib, hashlib, io, json, os, runpy, sys
HERE = os.path.dirname(os.path.abspath(__file__)); DIR = os.path.dirname(HERE)
for ln in open(os.path.join(DIR, 'LOCK_adj_md5.txt')):
    h, p = ln.split(None, 1); p = p.strip()
    assert hashlib.md5(open(os.path.join(DIR, p), 'rb').read()).hexdigest() == h, f"LOCK lệch: {p}"
with contextlib.redirect_stdout(io.StringIO()):
    M = runpy.run_path(os.path.join(HERE, 'model_sas_rev3.py'), run_name='m')
c, N0, C0, R, A3 = M['c'], M['N0'], M['C0'], M['R'], M['A3']
assert round(C0) == 27477
pct = lambda s: s['center_post'] / C0 - 1
mN0_bien = M['mN0_full']                                  # #1 N0 về biên vh 9T/25
LR = A3['lt_recv_project']['v']
tv1, tv3 = LR * (1 - 1 / (1 + R)), LR * (1 - 1 / (1 + R) ** 3)  # #2 C+ giá trị thời gian
NWC = 130.296                                             # #3 VLĐ ròng ngoài tiền (assumptions_r3 nwc_noncash)
S = {2023: 694.2 / ((567.3 + 605.6 + 714.1) / 3), 2024: 789.2 / ((680.6 + 654.4 + 782.4) / 3), 2025: 976.3 / ((764.2 + 770.2 + 804.9) / 3)}
s_avg = sum(S.values()) / 3
sea = lambda s: (3 + s) / 4 - 1                           # #4 mùa vụ Q4
items = {
  '1_N0_dinh_bien':      dict(bac='B', p=0.35, p_rng=(0.15, 0.55), kind='n0', pt=mN0_bien, rng=(mN0_bien / 2, mN0_bien)),
  '2_phai_thu_DH_du_an': dict(bac='C+', p=0.50, p_rng=(0.25, 0.75), kind='dx', pt=-tv1, rng=(-tv1, -tv3)),
  '3_thue_GTGT_VLD':     dict(bac='B', p=0.35, p_rng=(0.15, 0.55), kind='dx', pt=NWC, rng=(NWC / 2, NWC)),
  '4_mua_vu_Q4':         dict(bac='B', p=0.35, p_rng=(0.15, 0.55), kind='n0', pt=sea(s_avg), rng=(sea(min(S.values())), sea(max(S.values())))),
}
def combo(sel):  # sel {k: (p, m_raw)} — chạy MÔ HÌNH với tổ hợp
    f = 1.0; dx = 0.0
    for k, (p, m) in sel.items():
        if items[k]['kind'] == 'n0': f *= 1 + p * m
        else: dx += p * m
    return c(n0=N0 * f, dx=dx)
for k, it in items.items():
    it['m'] = pct(combo({k: (1.0, it['pt'])})); it['m_lo_hi'] = [pct(combo({k: (1.0, x)})) for x in it['rng']]
sig = sum(it['p'] * it['m'] for it in items.values())
adj = combo({k: (it['p'], it['pt']) for k, it in items.items()})
def extreme(lo):
    sel = {}
    for k, it in items.items():
        vals = [(pct(combo({k: (p, m)})), (p, m)) for p in it['p_rng'] for m in it['rng']]
        sel[k] = (min if lo else max)(vals)[1]
    return combo(sel), sel
lo, slo = extreme(True); hi, shi = extreme(False)
g27 = R - R / (1 - (1 + R) ** -27)
sens = {'C_hop_dong_thue_27_nam': pct(c(gs=((g27,), (1.0,)))),
        'C_LongThanh_Delta_-10pp': pct(c(dshift=-0.10)), 'C_LongThanh_Delta_+10pp': pct(c(dshift=0.10)),
        'C_bien_vh_10pct': pct(c(n0=N0 * (0.10 / M['mg']['9M2026']))),
        'C_co_tuc_von_hoa': M['out']['C_sens'], 'LUAT_E15_Ke12.3': M['out']['r_sens']['Ke12.3_E15'] / C0 - 1}
O = dict(center_base=C0, center_adj=adj['center_post'], range_low=lo['center_post'], range_high=hi['center_post'], sigma_linear=sig,
         center_linear=C0 * (1 + sig), seasonality=S, s_avg=s_avg, g_equiv_27y=g27, sel_lo=slo, sel_hi=shi, sens=sens,
         items={k: {kk: v for kk, v in it.items()} for k, it in items.items()})
print(f"tâm base {C0:,.0f}")
for k, it in items.items():
    print(f"  #{k} [{it['bac']}] p {it['p']} {it['p_rng']} m {it['m']:+.2%} (dải m {it['m_lo_hi'][0]:+.2%}..{it['m_lo_hi'][1]:+.2%}) p×m {it['p']*it['m']:+.2%}")
print(f"  mùa vụ s {', '.join(f'{y} {v:.3f}' for y, v in S.items())} TB {s_avg:.3f}")
print(f"Σp×m {sig:+.2%} ⇒ tuyến tính {C0*(1+sig):,.0f} | MÔ HÌNH tổ hợp {adj['center_post']:,.0f} ({adj['center_post']/C0-1:+.2%}) | dải {lo['center_post']:,.0f}–{hi['center_post']:,.0f}")
for k, v in sens.items():
    if isinstance(v, dict): print(f"  {k}: " + "; ".join(f"{a} {b:+.2%}" for a, b in v.items()))
    else: print(f"  {k}: {v:+.2%} ({C0*(1+v):,.0f})")
json.dump(O, open(os.path.join(HERE, 'calc_adj_rev3_out.json'), 'w'), indent=1, default=float, ensure_ascii=False, sort_keys=True)
