"""SZL 3c r3: do nhay moat tren LUOI r2 (270 o, trong so giu nguyen). Chay: $DNA_PYEXE -B 5F/szl_moat_sens.py > 5F/szl_moat_sens_out.txt
Tai dung NGUYEN phan khai bao cua calc/model_r2.py (exec den truoc 'def val', KHONG chay phan ghi file) => khong sua model/SUMMARY cu.
Hai kenh 3c:
 (R) RONIC=Ke [SUA r3]: tang truong tai dau tu o RONIC=Ke co NPV 0 => gia tri = dong tien ban dau KHONG tang truong:
     vinh vien cf0/r; nhanh huu han 27 nam = annuity khong tang truong cf0*(1-(1+r)^-T)/r. (r2 nhan (1-g/r) vao annuity 27n
     => von tai dau tu mat loi suat o 2053 (khong thu hoi) => NPV am, dem hai lan voi dong ho 2053 — SAI.) Ap doi xung moi o g, r.
     g_free: phan g <= g_free coi la gia (khong can tai dau tu) => tang truong g_free khong tai dau tu, phan vuot NPV 0.
 (M) bien ve TB chu ky: N0 hien hanh = LN loi 9T/2026 x4/3 ung voi GPM TTM > TB chu ky RIENG SZL.
     N0_cyc = N0 - (GPM_TTM - GPM_cyc) x DT_TTM x (1-20% thue) [UL: chi phi BH/QLDN khong doi]. 5 muc N0 +-12% quanh N0_cyc.
     Headline giu dau vao GPM cua r2 (TTM 39,0% / TB nam 2017-25 33,6%, theo chi dao Mike 07/11). Do nhay cua so bien + bien
     theo quy tac GPM 07/11 19:50 (GPM_P0 la TTM: TTM = GPM_P0 2026Q3, nam = GPM_P0 Q4)."""
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
    cf = n0 * (1 - nc)
    ge = min(g, g_free) if ronic_ke else g  # RONIC=Ke: phan tang truong vuot g_free NPV 0 => bo
    core = cf / (r - ge) if T is None else cf * (1 - ((1 + ge) / (1 + r)) ** T) / (r - ge)
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

# --- do nhay cua so bien chu ky (r3) ---
import csv as _csv
_rows = [r for r in _csv.DictReader(open(os.path.join(H, 'bq_fin_peers_20261107.csv'))) if r['ticker'] == 'SZL']
_by = {r['quarter']: r for r in _rows}
def _yr_w(y):  # cach r2: TB trong so DT cua GPM_P0 4 quy trong nam
    q = [_by[f"{y}Q{i}"] for i in range(1, 5)]; return sum(float(x['gpm']) * float(x['rev']) for x in q) / sum(float(x['rev']) for x in q), sum(float(x['rev']) for x in q)
_yw = {y: _yr_w(y) for y in range(2017, 2026)}
WIN = {
 'r2_TBnam_2017_25': (GPM_TTM, sum(v[0] for v in _yw.values()) / 9),
 'r2_trongsoDT_2017_25': (GPM_TTM, sum(v[0] * v[1] for v in _yw.values()) / sum(v[1] for v in _yw.values())),
 'r2_TBnam_2021_25': (GPM_TTM, sum(_yw[y][0] for y in range(2021, 2026)) / 5),
 'quytac0711_Q4_2017_25': (float(_by['2026Q3']['gpm']), sum(float(_by[f"{y}Q4"]['gpm']) for y in range(2017, 2026)) / 9),
 'quytac0711_Q4_2021_25': (float(_by['2026Q3']['gpm']), sum(float(_by[f"{y}Q4"]['gpm']) for y in range(2021, 2026)) / 5),
}
print("Chuoi GPM nam (cach r2, TB trong so DT 4 quy): " + " ".join(f"{y}:{v[0]:.3f}" for y, v in _yw.items()) + f" | TTM {GPM_TTM:.3f}")
print("Chuoi GPM_P0 Q4 (quy tac 07/11): " + " ".join(f"{y}:{float(_by[f'{y}Q4']['gpm']):.3f}" for y in range(2017, 2026)) + f" | 2026Q3 {float(_by['2026Q3']['gpm']):.3f}")
O['WIN'] = {}
for k, (tt, cy) in WIN.items():
    n0c = N0 - (tt - cy) * REV_TTM * 0.8
    O['WIN'][k] = row(f"chat-3c cua so {k}: TTM {tt:.4f} cyc {cy:.4f} N0_cyc {n0c:.1f}", base=n0c, ronic_ke=True)
    O['WIN'][k].update(gpm_ttm=tt, gpm_cyc=cy, n0_cyc=n0c)
json.dump(dict(N0=N0, N0_cyc=N0_CYC, gpm_ttm=GPM_TTM, gpm_cyc=GPM_CYC, rev_ttm=REV_TTM, d40=d40, rows=O), open(os.path.join(H, 'szl_moat_sens_out.json'), 'w'), indent=1, default=float, sort_keys=True)
