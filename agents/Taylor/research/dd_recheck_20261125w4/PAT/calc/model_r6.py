"""PAT rev6 (sổ rev4) — chạy SAU khoá ../lock_rev6.txt (assumptions_rev6.md md5 5207e413…). MÙ GIÁ.
Bọc model_r5.py (md5 assert, không sửa): (1) D4 terminal RONIC=Ke; (2) cell='D'. Chạy: python3 -I model_r6.py (cwd bất kỳ)."""
import hashlib, json, os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
R5 = os.path.normpath(os.path.join(HERE, '../../../dd_PAT_rebuttal_20261117/C/r5/calc_r5'))
LOCK = os.path.join(HERE, '../assumptions_rev6.md')
assert hashlib.md5(open(os.path.join(R5, 'model_r5.py'), 'rb').read()).hexdigest() == 'f6cd2e0ea89322b092b2e6a2bd4518b9'
assert hashlib.md5(open(LOCK, 'rb').read()).hexdigest() == '5207e413eb10404ccdf3aa47c7af9916'
sys.path.insert(0, R5)
import model_r5 as M
CK = 0.90
QL = (('P10', .10), ('P25', .25), ('P50', .50), ('P75', .75), ('P90', .90))
out = {}
ctrl = M.run_mix()['center']; assert abs(ctrl - 66470.1) < 0.1, ctrl; out['control_r5'] = ctrl
_v = M.value
def value_d4(path, f, p, s_exp, elec, freight=M.FREIGHT_R4, r=0.135, g=0.02, **kw):
    kw.pop('detail', None)
    d = _v(path, f, p, s_exp, elec, freight, r, g, detail=True, **kw)
    eq = d['equity'] - d['pv_tv'] + d['pv_tv'] * (r - g) / r
    return eq / M.SH * 1000
M.value = value_d4
def mix(**kw):
    kw.setdefault('cell', 'D'); return M.run_mix(**kw)
B = mix(); base = B['center']; L = B['leaves']
out['base_pre_ck'] = base; out['base_post_ck'] = base * CK; out['per_q'] = {str(k): v for k, v in B['per_q'].items()}
out['quantiles_post_ck'] = {k: M.wq(L, q) * CK for k, q in QL}
out['quantiles_pre_ck'] = {k: M.wq(L, q) for k, q in QL}
out['sum_p'] = B['tot']; out['n_leaves'] = len(L)
out['d4_O2_w3'] = mix(cell='O2')['center']          # = w3 probe 65.510
out['r_sens'] = {}
for r in (0.123, 0.125, 0.13, 0.134, 0.14, 0.145):
    out['r_sens'][str(r)] = mix(r=r)['center']
# tỉ trọng TV (đường cơ sở, D4)
M.value = _v
R = M.run(cell='D'); d = M.base_path(R, detail=True)
out['tv_share_base_path_d4'] = d['pv_tv'] * (0.135 - 0.02) / 0.135 / (d['equity'] - d['pv_tv'] + d['pv_tv'] * (0.135 - 0.02) / 0.135)
M.value = value_d4
# E17 hạng mục lên (#1 cell O2, #2 tồn kho) — tổ hợp 4 ô
combo = {}
for cell in ('D', 'O2'):
    for inv in (0.0, M.INV_EXCESS):
        combo[f'{cell}|inv{inv:.2f}'] = mix(cell=cell, inv=inv)['center']
out['combo'] = combo
def e17(p1, p2):
    return sum((p1 if c == 'O2' else 1 - p1) * (p2 if i > 0 else 1 - p2) * v
               for k, v in combo.items() for c, i in [(k.split('|')[0], float(k.split('inv')[1]))])
out['e17'] = {'p_mid': e17(0.5, 0.5), 'p_low': e17(0.25, 0.25), 'p_high': e17(0.75, 0.75)}
out['e17_linear_check'] = base * (1 + 0.5 * (combo['O2|inv0.00'] / base - 1) + 0.5 * (combo['D|inv44.44'] / base - 1))
# hạng mục C (độ nhạy, không vào tâm)
out['sens_C'] = {
  'bao_dam_cheo_42.6': mix(oneoff=-42.6)['center'],
  '70ty_menh_gia': mix(oneoff=M.LOCKED70)['center'],
}
M.value = _v
def value_lease(end, restore=0.0):
    def f(path, ff, p, s_exp, elec, freight=M.FREIGHT_R4, r=0.135, g=0.02, lr_mult=1.0, oneoff=0.0, cash=None, transfer=0.0, vol27=1.0, inv_pv=0.0, detail=False):
        fx = ff * (1 - 0.65 * transfer)
        e27 = M.ebit(path[2027], fx, p, s_exp, elec, freight)
        if vol27 != 1.0:
            n, v, vn = path[2027]; e27 = 0.5 * e27 + 0.5 * M.ebit((n, v * vol27, vn * vol27), fx, p, s_exp, elec, freight)
        pv = 53.844 * 0.95 * 0.94 / (1 + r) ** 0.13 + e27 * 0.95 * 0.94 / (1 + r) ** 0.63
        for y in range(2028, end + 1):
            el = M.ebit(path[y], fx, p, s_exp, elec, freight) * lr_mult * (1 + g) ** (y - 2028)
            pv += el * (1 - M.TAX[y]) * 0.94 / (1 + r) ** (1.63 + y - 2028)
        pv -= restore / (1 + r) ** (1.63 + end - 2028)
        # thả khoá 70 tỷ khi hết thuê (bảo lãnh tiền điện chấm dứt)
        pv += M.LOCKED70 / (1 + r) ** (1.63 + end - 2028)
        return (pv + (M.NET_CASH if cash is None else cash) + oneoff + inv_pv) / M.SH * 1000
    return f
for end in (2034, 2042):
    for rs in (0.0, 50.0):
        M.value = value_lease(end, rs); out['sens_C'][f'thue_dat_het_{end}_hoannguyen{int(rs)}'] = mix()['center']
M.value = _v
rel = lambda v: v / base - 1
print(f"CONTROL r5 {ctrl:,.1f}")
print(f"BASE rev6 (D4 + ô D) truoc CK {base:,.1f}  sau CK {base*CK:,.1f}  sum_p {B['tot']:.10f} leaves {len(L)}")
print("per_q", {k: round(v) for k, v in out['per_q'].items()})
print("quantiles sau CK", {k: round(v) for k, v in out['quantiles_post_ck'].items()})
print(f"D4+O2 (w3) {out['d4_O2_w3']:,.0f}  tv_share {out['tv_share_base_path_d4']:.3f}")
for k, v in out['r_sens'].items(): print(f"r {k}: {v:,.0f} ({rel(v):+.2%}) sau CK {v*CK:,.0f}")
for k, v in combo.items(): print(f"combo {k}: {v:,.0f} ({rel(v):+.2%})")
for k, v in out['e17'].items(): print(f"E17 {k}: {v:,.0f} ({rel(v):+.2%}) sau CK {v*CK:,.0f}")
print(f"E17 tuyen tinh {out['e17_linear_check']:,.0f}")
for k, v in out['sens_C'].items(): print(f"C {k}: {v:,.0f} ({rel(v):+.2%}) sau CK {v*CK:,.0f}")
json.dump(out, open(os.path.join(HERE, 'model_r6_out.json'), 'w'), indent=1, default=float)
