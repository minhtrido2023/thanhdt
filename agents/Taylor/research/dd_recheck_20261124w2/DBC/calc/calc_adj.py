"""E17 tâm kỳ vọng điều chỉnh DBC — PREREG_adj.md (ef5157cb…) + PREREG_adj_v2.md (835dfc1e…). MÙ GIÁ.
Mô hình = rev4/calc_rev4.py (khoá md5 ee3e09b5…, assumptions 57b36d63…), nạp bằng runpy; thêm tỷ lệ vốn chủ tài trợ TÁCH RIÊNG cho
XDCB (f_c) và BĐS dở dang (f_r) + tuỳ chọn cộng lại lãi vay chi phí (khi nợ CHUNG tài trợ và lãi KHÔNG vốn hoá).
Chạy: /home/trido/thanhdt/wc_venv/bin/python -I calc_adj.py <worktree>"""
import sys, os, io, json, hashlib, runpy, contextlib
WT = os.path.abspath(sys.argv[1]); HERE = os.path.dirname(os.path.abspath(__file__))
def md5(p): return hashlib.md5(open(p, 'rb').read()).hexdigest()
PR = os.path.join(WT, 'agents/Taylor/research/dd_adjcenter_20261124'); R4 = os.path.join(WT, 'agents/Taylor/research/dd_DBC_20261118/rev4')
assert md5(os.path.join(PR, 'PREREG_adj.md')) == 'ef5157cb3f762d58623ed550ebc214c7'
assert md5(os.path.join(PR, 'PREREG_adj_v2.md')) == '835dfc1e07f9c67ac7f6c3028b529d13'
assert md5(os.path.join(R4, 'calc_rev4.py')) == 'ee3e09b523303a0c839bfabfe021eefd'
assert md5(os.path.join(R4, 'assumptions_DBC_rev4.json')) == '57b36d63e05ad2e2c209f2ce34fda8c9'
with contextlib.redirect_stdout(io.StringIO()): G = runpy.run_path(os.path.join(R4, 'calc_rev4.py'), run_name='__main__')
np_series, keys, EQ, W, E, CIP, REW, S, L = (G[k] for k in ('np_series', 'keys', 'EQ', 'W', 'E', 'CIP', 'REW', 'S', 'L'))
cip_lin, re_lin, val, SP, HC, k0, r0, g, DTA = (G[k] for k in ('cip_lin', 're_lin', 'val', 'SP', 'HC', 'k0', 'r0', 'g', 'DTA'))
C0 = 17673
# --- dữ kiện tài trợ (A: KT25 TM 'Capitalised borrowing costs' p34 OCR; LCTT p12 lãi vay; BQ ticker_financial StDebt_P0+LtDebt_P0) ---
CAP = {'2024': 21.7, '2025': 9.5}; INT = {'2024': 263.669, '2025': 261.109}
DEBT = {'2023Q4': 4840.721 + 1026.415, '2024Q4': 4928.462 + 764.297, '2025Q4': 4770.218 + 1106.441}
CIPK = G['A']['cip_known_bn']
rate = {y: INT[y] / ((DEBT[f'{int(y)-1}Q4'] + DEBT[f'{y}Q4']) / 2) for y in CAP}
avgcip = {y: (CIPK[f'{int(y)-1}Q4'] + CIPK[f'{y}Q4']) / 2 for y in CAP}
def debt_share(spec_rate=None): return {y: CAP[y] / (spec_rate or rate[y]) / avgcip[y] for y in CAP}
ds = debt_share(); ds8 = debt_share(0.08)
fc_pt = 1 - (ds['2024'] + ds['2025']) / 2; fc_lo = 1 - ds['2024']; fc_hi = 1 - ds8['2025']
TAXI = 0.10  # thuế hiệu dụng ~7–10% (KT25 TM31) cho lãi cộng lại — chỉ dùng ở bản leverage-neutral

def center(fc=1.0, fr=1.0, addback=False, re_hc=0.0, dta_all=False, wt=(.25, .5, .25)):
    q = np_series(False)
    def den(k): return EQ[k] - fc * cip_lin(k) - fr * re_lin(k)
    def num(k):
        x = q[k]
        if addback: x += ((1 - fc) * cip_lin(k) + (1 - fr) * re_lin(k)) * rate['2025'] * (1 - TAXI) / 4
        return x
    Rw = [sum(4 * num(k) / den(k) for k in keys if W[n][0] <= k <= W[n][1]) / len([k for k in keys if W[n][0] <= k <= W[n][1]]) for n in ('W12', 'W15', 'W20')]
    ro = sum(Rw) / 3; book = fc * CIP + fr * REW; Eop = E - book; sc = E / Eop
    ex = -re_hc * fr * REW
    v = {'bad': val(ro - SP * sc, Eop, book, k0, r0, g, HC, ex + (DTA if dta_all else 0)), 'base': val(ro, Eop, book, k0, r0, g, extra=ex + (DTA if dta_all else 0)),
         'good': val(ro + SP * sc, Eop, book, k0, r0, g, extra=DTA + ex)}
    return sum(w * v[x] for w, x in zip(wt, ('bad', 'base', 'good'))) * (1 - L)
c0 = center(); assert round(c0) == C0, c0
assert round(center(fc=.5, fr=.5)) == 13767   # tái lập độ nhạy 50% của rev4
def pct(x): return round((x / c0 - 1) * 100, 3)
CASES = {'FUND_pt': dict(fc=fc_pt), 'FUND_lo': dict(fc=fc_lo), 'FUND_hi': dict(fc=fc_hi),
         'RE_hc33': dict(re_hc=.33), 'RE_hc20': dict(re_hc=.20), 'RE_hc40': dict(re_hc=.40), 'DTA_all': dict(dta_all=True),
         'S_levneutral53_both': dict(fc=.53, fr=.53), 'S_levneutral53_both_addback': dict(fc=.53, fr=.53, addback=True),
         }
K = {n: dict(center=round(center(**kw)), d_pct=pct(center(**kw))) for n, kw in CASES.items()}
IT = [('FUND_pt', 'FUND_lo', 'FUND_hi', .5, .25, .75), ('RE_hc33', 'RE_hc40', 'RE_hc20', .65, .40, .90), ('DTA_all', 'DTA_all', 'DTA_all', .5, .25, .75)]
lin = sum(p * K[a]['d_pct'] for a, _, _, p, _, _ in IT)
# TỔ HỢP chạy lại mô hình: tham số = kỳ vọng theo p (fc nội suy, haircut × p, DTA bật với trọng số p)
def combo(pf, fcv, ph, hv, pd):
    fc = 1 - pf * (1 - fcv)
    a = center(fc=fc, re_hc=ph * hv); b = center(fc=fc, re_hc=ph * hv, dta_all=True)
    return a * (1 - pd) + b * pd
cc = combo(.5, fc_pt, .65, .33, .5)
cands = [combo(pf, fv, ph, hv, pd) for pf in (.25, .75) for fv in (fc_lo, fc_hi) for ph in (.40, .90) for hv in (.20, .40) for pd in (.25, .75)]
out = dict(control_center=round(c0), funding=dict(rate=rate, avg_cip=avgcip, debt_share=ds, debt_share_at8pct=ds8, fc_point=fc_pt, fc_low=fc_lo, fc_high=fc_hi),
           cases=K, sum_lin_pct=round(lin, 3), combo=dict(center=round(cc), d_pct=pct(cc), low=round(min(cands)), high=round(max(cands))))
print(json.dumps(out, ensure_ascii=False, indent=1))
json.dump(out, open(os.path.join(HERE, 'calc_adj_out.json'), 'w'), ensure_ascii=False, indent=1, sort_keys=True)
