"""SZL 3c: do nhay moat tren LUOI r2 (270 o, trong so giu nguyen). Chay: $DNA_PYEXE -B 5F/szl_moat_sens.py > 5F/szl_moat_sens_out.txt
Tai dung NGUYEN phan khai bao cua calc/model_r2.py (exec den truoc 'def val', KHONG chay phan ghi file) => khong sua model/SUMMARY cu.
Hai kenh 3c:
 (R) RONIC=Ke: dong tien nam 1 = n0*(1-nc)*(1-g/r) (tai dau tu g/Ke de tang truong g) — model hien hanh ngam RONIC=vo cung (g 2-4% khong tai dau tu).
     Doi xung: ap moi o g {2,3,4}% va moi o r; quy uoc nam 1 giu nhu model_r2 (cf nam 1 khong nhan (1+g), annuity T=27 / Gordon).
 (M) bien ve TB chu ky: N0 hien hanh = LN loi 9T/2026 x4/3, ung voi GPM TTM 39,0% (Q4/25-Q3/26, trong so DT) > TB chu ky RIENG SZL 2017-25 33,6%.
     N0_cyc = N0 - (GPM_TTM - GPM_cyc) x DT_TTM x (1-20% thue) [UL: gia dinh chi phi BH/QLDN khong doi]. Ca 5 muc N0 +-12% doi xung quanh N0_cyc.
     TB peer KCN (trung vi 49,1%) KHONG dung: SZL co mang xang dau/nuoc/dich vu bien thap => GPM khong cung dinh nghia; dung peer se NANG N0 (khong co co so)."""
import os, sys, json, itertools
H = os.path.dirname(os.path.abspath(__file__)); C = os.path.join(H, '..', 'calc')
src = open(os.path.join(C, 'model_r2.py')).read(); head = src[:src.index('def val(')]
ns = {'__file__': os.path.join(C, 'model_r2.py'), '__name__': 'r2head'}
exec(compile(head, 'model_r2_head', 'exec'), ns)
R2 = ns['R2']; N0 = ns['N0']; R = ns['R']; PX = ns['PX']; LD = ns['LD']; SH = ns['SH']; Q = ns['Q']
st = json.load(open(os.path.join(H, 'szl_5f_stats_out.json')))
GPM_TTM = st['table']['SZL']['ttm']; GPM_CYC = st['table']['SZL']['cyc']
REV_TTM = (132.5 + 138.9 + 157.9 + 152.5)  # ty, BQ Revenue_P0 Q4/25..Q3/26 (5F/bq_fin_peers_20261107.csv)
N0_CYC = N0 - (GPM_TTM - GPM_CYC) * REV_TTM * 0.8
print(f"N0 {N0:.1f}; GPM TTM {GPM_TTM:.3%} vs TB chu ky SZL 2017-25 {GPM_CYC:.3%}; DT TTM {REV_TTM:.1f} => N0_cyc {N0_CYC:.1f} ({N0_CYC/N0-1:+.1%})")
inv = (sum(ns['mkt'].values()) - ns['gain_tax']) + ns['unlisted']
def val(n0, g, r, nc, T, ronic_ke=False, g_free=0.0):
    cf = n0 * (1 - nc) * ((1 - max(g - g_free, 0.0) / r) if ronic_ke else 1.0)
    core = cf / (r - g) if T is None else cf * (1 - ((1 + g) / (1 + r)) ** T) / (r - g)
    return (core + inv + ns['CIP'] - ns['OTHER_LIAB'] - ns['NET_DEBT']) / SH * 1000
# trục/trọng số chép nguyên văn calc/model_r2.py (sau 'def val')
GS = (0.02, 0.03, 0.04); WG = (0.25, 0.5, 0.25); RS = (R - 0.01, R, R + 0.01); WR = (0.25, 0.5, 0.25)
NCS = (0.20, 0.10, 0.0); WNC = (0.25, 0.5, 0.25)
MULT = (0.88, 0.94, 1.0, 1.06, 1.12); WN = (0.1, 0.2, 0.4, 0.2, 0.1)
def grid(base=N0, ronic_ke=False, ts=((27, None), (0.75, 0.25)), g_free=0.0):
    v, w = [], []
    for (m, wn), (g, wg), (rr, wr), (nc, wc), (T, wt) in itertools.product(zip(MULT, WN), zip(GS, WG), zip(RS, WR), zip(NCS, WNC), zip(*ts)):
        v.append(val(base * m, g, rr, nc, T, ronic_ke, g_free)); w.append(wn * wg * wr * wc * wt)
    return v, w
d40 = Q['disc_sleeve_max']
def row(name, **kw):
    v, w = grid(**kw); S = R2.stats(v, w, PX, LD); lab = R2.label(PX, S)
    p10s, p90s = S['p10_pre'] * (1 - d40), S['p90_pre'] * (1 - d40)
    lab40 = 'DUOI' if PX < p10s else ('TREN' if PX > p90s else 'TRONG')
    d10 = Q['adv250']['sizes']['0.01']['disc'] if '0.01' in Q['adv250']['sizes'] else None
    print(f"{name}: " + R2.fmt(S, PX) + f" | sleeve40tr P10/P90 {p10s:,.0f}/{p90s:,.0f} -> {lab40}")
    return dict(S=S, label=lab, label40=lab40, p10_40=p10s, p90_40=p90s)
O = {}
O['current'] = row("HIEN HANH (tai lap REPORT_r2)")
O['WIDE_perp'] = row("WIDE (khong dong ho: chi vinh vien, bien TTM, RONIC tu do)", ts=((None,), (1.0,)))
O['R_only'] = row("chi RONIC=Ke (bien TTM)", ronic_ke=True)
O['M_only'] = row("chi bien ve TB chu ky SZL (RONIC tu do)", base=N0_CYC)
O['STRICT'] = row("BAN CHAT-3C NARROW (RONIC=Ke + bien TB chu ky, giu dong ho 27n/vv 3/4-1/4)", base=N0_CYC, ronic_ke=True)
O['STRICT_gfree2'] = row("(do nhay) chat-3c nhung g<=2% coi la gia lam phat khong can tai dau tu", base=N0_CYC, ronic_ke=True, g_free=0.02)
O['NONE'] = row("NONE (chat-3c + chi 27 nam, khong gia han)", base=N0_CYC, ronic_ke=True, ts=((27,), (1.0,)))
json.dump(dict(N0=N0, N0_cyc=N0_CYC, gpm_ttm=GPM_TTM, gpm_cyc=GPM_CYC, rev_ttm=REV_TTM, d40=d40, rows=O), open(os.path.join(H, 'szl_moat_sens_out.json'), 'w'), indent=1, default=float, sort_keys=True)
