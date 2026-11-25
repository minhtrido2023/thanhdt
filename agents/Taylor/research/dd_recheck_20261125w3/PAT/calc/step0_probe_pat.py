"""PAT recheck đợt 3 — Bước 0 probe (25/11/2026, job Taylor_20261125_032448). Chạy từ dd_PAT_rebuttal_20261117/C/r5/calc_r5: python3 -I <đường dẫn file này>. Không sửa model_r5.py (ghi đè hàm trong bộ nhớ). MÙ GIÁ."""
import hashlib; assert hashlib.md5(open('model_r5.py','rb').read()).hexdigest() == 'f6cd2e0ea89322b092b2e6a2bd4518b9'
import sys, os; sys.path.insert(0, os.getcwd())
import model_r5 as M
base = M.run_mix()['center']; print(f"CONTROL mix {base:,.1f} (r5 66.470,1)")
for r in (0.123, 0.134):
    v = M.run_mix(r=r)['center']; print(f"r {r}: {v:,.0f} ({v/base-1:+.2%}) sau CK {v*0.9:,.0f}")
_v = M.value
def value_d4(path, f, p, s_exp, elec, freight=M.FREIGHT_R4, r=0.135, g=0.02, **kw):
    d = _v(path, f, p, s_exp, elec, freight, r, g, detail=True, **{k: v for k, v in kw.items() if k != 'detail'})
    tv_d4 = d['pv_tv'] * (r - g) / r          # RONIC = Ke: TV = NOPAT_{T+1}(1 - g/r)/(r-g) = NOPAT_{T+1}/r
    eq = d['equity'] - d['pv_tv'] + tv_d4
    return eq / M.SH * 1000
M.value = value_d4
d4 = M.run_mix()['center']; print(f"D4 RONIC=Ke terminal: {d4:,.0f} ({d4/base-1:+.2%}) sau CK {d4*0.9:,.0f}")
d4_123 = M.run_mix(r=0.123)['center']; print(f"D4 + r 12,3%: {d4_123:,.0f} ({d4_123/d4-1:+.2%} vs D4) sau CK {d4_123*0.9:,.0f}")
d4D = M.run_mix(cell='D')['center']; print(f"D4 + ô theo D (skeptic killer): {d4D:,.0f} ({d4D/d4-1:+.2%} vs D4) sau CK {d4D*0.9:,.0f}")
M.value = _v
R = M.run(); dd = M.base_path(R, detail=True); print('tv_share (base path)', round(dd['tv_share'], 3))
M.value = value_d4
L = M.run_mix()['leaves']
q = {k: M.wq(L, v) * 0.9 for k, v in (('P10', .1), ('P25', .25), ('P50', .5), ('P75', .75), ('P90', .9))}
print('D4 quantiles sau CK', {k: round(v) for k, v in q.items()})
M.value = _v
# hạn thuê đất 2034/2042 không gia hạn: dòng tiền tới năm hết hạn, không TV (đối chiếu, chiều xuống)
def value_lease(end):
    def f(path, ff, p, s_exp, elec, freight=M.FREIGHT_R4, r=0.135, g=0.02, lr_mult=1.0, oneoff=0.0, cash=None, transfer=0.0, vol27=1.0, inv_pv=0.0, detail=False):
        fx = ff * (1 - 0.65 * transfer)
        e27 = M.ebit(path[2027], fx, p, s_exp, elec, freight)
        if vol27 != 1.0:
            n, v, vn = path[2027]; e27 = 0.5 * e27 + 0.5 * M.ebit((n, v * vol27, vn * vol27), fx, p, s_exp, elec, freight)
        pv = 53.844 * 0.95 * 0.94 / (1 + r) ** 0.13 + e27 * 0.95 * 0.94 / (1 + r) ** 0.63
        for y in range(2028, end + 1):
            el = M.ebit(path[y], fx, p, s_exp, elec, freight) * lr_mult * (1 + g) ** (y - 2028)
            pv += el * (1 - M.TAX[y]) * 0.94 / (1 + r) ** (1.63 + y - 2028)
        return (pv + (M.NET_CASH if cash is None else cash) + oneoff + inv_pv) / M.SH * 1000
    return f
for end in (2034, 2042):
    M.value = value_lease(end); v = M.run_mix()['center']; print(f"thuê đất hết {end}, không gia hạn, không TV: {v:,.0f} ({v/d4-1:+.2%} vs D4)")
M.value = _v
