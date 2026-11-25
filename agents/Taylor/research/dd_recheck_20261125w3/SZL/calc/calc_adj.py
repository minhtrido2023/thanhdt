"""E17 SZL — tam ky vong dieu chinh, chay QUA mo hinh rev5 (ADJ_PREREG_SZL.md khoa truoc, commit rieng).
Chay: /home/trido/thanhdt/wc_venv/bin/python calc_adj.py <worktree>/agents/Taylor/research/dd_redo_20261105/SZL/rev5/calc
S1/S2/S3: cfg add_extra (ty, t=0). S4: dich truc NCS cua mo hinh +x (giu trong so 0,25/0,5/0,25)."""
import sys, os, io, json, hashlib, contextlib, importlib.util
HERE = os.path.abspath(sys.argv[1]); OUT = os.path.dirname(os.path.abspath(__file__))
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
assert md5(os.path.join(OUT, '..', 'ADJ_PREREG_SZL.md')) == 'c43c1873805cb9c7386a4e535964c2bd'
assert md5(os.path.join(HERE, 'assumptions_rev5.json')) == '35165d4a511c5987a8f8f3a21046fb1d'
spec = importlib.util.spec_from_file_location('model_rev5', os.path.join(HERE, 'model_rev5.py')); M = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()) as b: spec.loader.exec_module(M)
assert hashlib.md5(b.getvalue().encode()).hexdigest() == md5(os.path.join(HERE, 'model_rev5_out.txt')), 'CONTROL lech'
NCS0 = M.NCS
def center(t0=0.0, nc=0.0):
    M.NCS = tuple(x + nc for x in NCS0)
    try: s5, _ = M.run(dict(add_extra=t0))
    finally: M.NCS = NCS0
    return s5['center_post']
C0 = center(); assert round(C0) == 26183, C0
IT = {'S1_ton_kho_BDS_Tam_An': ('t0', 116.58, 116.58, 116.58, .75, .50, .90, 'A'),
      'S2_tra_truoc_nha_thau_capex': ('t0', 58.39, 58.39, 72.61, .50, .25, .75, 'B'),
      'S3_co_tuc_du_thu': ('t0', 23.264, 23.264, 23.264, .90, .75, 1.00, 'A'),
      'S4_nc_phan_bo_DTCTH': ('nc', .07, .07, .13, .35, .15, .55, 'C+')}
def run(sel):
    a = dict(t0=0.0, nc=0.0)
    for k, x in sel.items(): a[IT[k][0]] += x
    return center(**a)
items = {}
for k, (kind, m, lo, hi, p, plo, phi, bac) in IT.items():
    ext = [run({k: pp * mm}) / C0 - 1 for pp in (plo, phi) for mm in (lo, hi)]
    items[k] = dict(bac=bac, input=m, input_range=[lo, hi], m_pct=round(run({k: m}) / C0 - 1, 5), p=p, p_range=[plo, phi],
                    pm_pct=round(run({k: p * m}) / C0 - 1, 5), pm_min=round(min(ext), 5), pm_max=round(max(ext), 5))
P = {k: IT[k][4] * IT[k][1] for k in IT}
adj = run(P)
def pick(fn):
    return {k: fn([pp * mm for pp in (v[5], v[6]) for mm in (v[2], v[3])], key=lambda x, k=k: run({k: x})) for k, v in IT.items()}
low, high = run(pick(min)), run(pick(max))
def alt(**ch):  # doi p*m cua 1 hang muc, giu cac hang muc khac o tam
    s = dict(P); s.update(ch); return run(s) / adj - 1
trig = {'S1_nguoi_mua_tra_truoc_bang_0_p0.90': alt(S1_ton_kho_BDS_Tam_An=.9 * 116.58),
        'S1_suy_giam_50pct': alt(S1_ton_kho_BDS_Tam_An=.75 * 58.29),
        'S2_TM_xac_nhan_capex_A_p0.90': alt(S2_tra_truoc_nha_thau_capex=.9 * 58.39),
        'S2_la_von_luu_dong_van_hanh_0': alt(S2_tra_truoc_nha_thau_capex=0.0),
        'S4_TM19_phan_bo_thuc_17pct_p0.90': alt(S4_nc_phan_bo_DTCTH=.9 * .07),
        'S4_TM19_phan_bo_thuc_23pct_p0.90': alt(S4_nc_phan_bo_DTCTH=.9 * .13),
        'S4_dong_nc_giu_10pct': alt(S4_nc_phan_bo_DTCTH=0.0)}
res = dict(center_base=round(C0), center_adj=round(adj), adj_pct=round(adj / C0 - 1, 5), range_low=round(low), range_high=round(high),
           sum_pm_linear_pct=round(sum(v['pm_pct'] for v in items.values()), 5), items=items, triggers={k: round(v, 5) for k, v in trig.items()},
           sh_mn=M.SH, d_ref=M.D_REF)
print(json.dumps(res, ensure_ascii=False, indent=1))
json.dump(res, open(os.path.join(OUT, 'calc_adj_out.json'), 'w'), ensure_ascii=False, indent=1, sort_keys=True)
