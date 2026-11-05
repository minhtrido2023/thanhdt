"""SZL redo 05/11/2026 (job Taylor_20261105_014133). Chay: $DNA_PYEXE -B model.py > model_out.txt
Nguon BCTC: src/Q3_2026_hopnhat.pdf (szl.com.vn, ky 20/10/2026; BCTC mau B01a-DN — SZL khong co cty con: dau tu con = 0) — scan, doc tu anh
img/p02 (giai trinh 186/6/SZL-TCKT 15/10/2026), img/p04-p08 (BS in tr.1-4, KQKD in tr.4). Co cau dau tu dai han: ABS 30/03/2026 (src cu
dd_SZL_20261026/src/abs_szl_260330.txt dong 392-394) khop tong 398,05 BCTC. Gia SZC/SZB + OShares: BQ 04/11/2026 (calc/bq_*.csv).
SOTP = LN loi (loai thu nhap tai chinh) / (r-g) + co phan SZC/SZB theo thi gia - thue TNDN 20% tren lai von chua thuc hien
+ dau tu chua niem yet gia so - no vay rong (sau co tuc phai tra). Long Phuoc (XDCB 407) = NPV 0 (luat du an moi 03/11)."""
import sys, os, csv, json, itertools
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', '_common'))
import liq as L
SH = 48.198884                                      # tr cp sau co tuc CP 70% (BQ OShares 2026Q3)
dep, dep_src = L.current_dep(); R = L.r_of(dep)
LQ = L.liq('SZL'); PX = LQ['price']; LD = LQ['disc_ref']
# --- BCTC 30/09/2026 ---
CASH = 171.220813690; DIV_PAY = 70.360021125        # ma 110; ma 313 (co tuc tien tra 07/10/2026)
LOAN_ST, LOAN_LT = 110.030903581, 196.337026604     # ma 321, 339
UNEARNED = 42.901784203 + 719.254313326             # ma 319 + 337 doanh thu chua thuc hien (KHONG phai no vay)
CIP = 407.037010429; EQ = 784.151356245
INV_BOOK = {"SZC": 221.8, "SZB": 63.0, "An Binh": 24.5, "Binh Thuan": 80.0, "Dich vu": 8.75}   # tong 398,05 = ma 260
OWN = {"SZC": 0.1008, "SZB": 0.084}
# --- KQKD 9T ---
NP_9M, NP_Q3 = 132.589359502, 69.896721750
FIN_REV_9M, FIN_EXP_9M = 37.740263110, 4.326469728
REV_9M, GP_9M = 449.387721455, 170.901193998
px = {r['ticker']: float(r['Close']) for r in csv.DictReader(open(os.path.join(HERE, 'bq_szc_szb_20261104.csv')))}
osh = {r['ticker']: float(r['OShares']) for r in csv.DictReader(open(os.path.join(HERE, 'bq_oshares_szc_szb.csv')))}
mkt = {k: OWN[k] * osh[k] * px[k] / 1e9 for k in OWN}
gain_tax = sum(max(mkt[k] - INV_BOOK[k], 0) for k in OWN) * 0.20
unlisted = sum(v for k, v in INV_BOOK.items() if k not in OWN)
NET_DEBT = LOAN_ST + LOAN_LT - CASH + DIV_PAY
CORE_9M = NP_9M - FIN_REV_9M + FIN_EXP_9M * 0.80    # co tuc nhan (phan lon FIN_REV) mien thue; lai vay duoc khau tru
N0 = CORE_9M * 4 / 3
print(f"Bien gop 9T {GP_9M/REV_9M:.1%}; LNST 9T {NP_9M:.1f} (Q3 {NP_Q3:.1f}); DT TC 9T {FIN_REV_9M:.1f}; LN loi 9T {CORE_9M:.1f} -> nam hoa N0 {N0:.1f}")
print(f"No vay {LOAN_ST+LOAN_LT:.1f} - tien {CASH:.1f} + co tuc phai tra {DIV_PAY:.1f} = no rong {NET_DEBT:.1f} ty ({NET_DEBT/SH*1000:,.0f} d/cp); DT chua thuc hien {UNEARNED:.1f} (khong tinh la no)")
print("Co phan niem yet theo thi gia 04/11: " + ", ".join(f"{k} {OWN[k]:.2%} x {osh[k]/1e6:.2f} tr cp x {px[k]:,.0f} = {mkt[k]:.1f} (so {INV_BOOK[k]})" for k in OWN) +
      f"; thue TNDN 20% lai von chua thuc hien {gain_tax:.1f}; chua niem yet gia so {unlisted:.2f}")
print(f"r = {R:.2%} (dep {dep:.2%} [{dep_src}]); gia {PX:,.0f} ({LQ['price_date']}); Long Phuoc XDCB {CIP:.1f} = NPV 0")

YRS_LEFT = 27      # (uoc luong) thoi han con lai thue dat KCN Long Thanh ~den 2053 — CHUA doi chieu giay phep
NC_REF = UNEARNED / YRS_LEFT * 0.80 / N0          # phan LN loi phi tien mat (phan bo DT chua thuc hien, sau thue, coi bien 100% — can tren)
print(f"Phi tien mat: DT chua thuc hien {UNEARNED:.1f} / {YRS_LEFT} nam x 0,8 = {UNEARNED/YRS_LEFT*0.8:.1f}/nam = {NC_REF:.0%} N0 (can tren; base dung 10%)")

def val(n0=N0, g=0.03, r=R, hold=0.0, nc=0.10):
    core = n0 * (1 - nc) / (r - g)
    inv = (sum(mkt.values()) - gain_tax) * (1 - hold) + unlisted
    return (core + inv - NET_DEBT) / SH * 1000

SC = {"xau": dict(n=N0 * 0.88, g=0.02, nc=0.20, p=0.25), "co so": dict(n=N0, g=0.03, nc=0.10, p=0.50), "tot": dict(n=N0 * 1.12, g=0.04, nc=0.0, p=0.25)}
out = dict(ticker='SZL', price=PX, price_date=LQ['price_date'], r=R, dep=dep, dep_src=dep_src, liq=LQ, n0=N0, net_debt=NET_DEBT, inv_mkt=mkt, gain_tax=gain_tax, scen={})
for k, p in SC.items():
    v = val(p['n'], p['g'], nc=p['nc']); out['scen'][k] = dict(pre=v, post=v * (1 - LD), **p)
    print(f"{k:7s} p={p['p']:.2f} LN loi {p['n']:.1f} g {p['g']:.0%} phi-tien-mat {p['nc']:.0%} (PE loi {1/(R-p['g']):.1f}x): {v:,.0f} -> sau CK TK {v*(1-LD):,.0f}")
cpre = sum(SC[k]['p'] * out['scen'][k]['pre'] for k in SC); out['center_pre'] = cpre; out['center_post'] = cpre * (1 - LD)
print(f"TAM truoc CK {cpre:,.0f} | CK thanh khoan {LD:.2%} (5 ty) | sau {cpre*(1-LD):,.0f} | gia/tam {PX/(cpre*(1-LD))-1:+.1%}")
NS = (N0 * 0.88, N0 * 0.94, N0, N0 * 1.06, N0 * 1.12); WN = (0.1, 0.2, 0.4, 0.2, 0.1)
GS = (0.02, 0.03, 0.04); WG = (0.25, 0.5, 0.25); RS = (R - 0.01, R, R + 0.01); WR = (0.25, 0.5, 0.25)
NCS = (0.20, 0.10, 0.0); WNC = (0.25, 0.5, 0.25)
vals, ws = [], []
for (n, wn), (g, wg), (rr, wr), (nc, wc) in itertools.product(zip(NS, WN), zip(GS, WG), zip(RS, WR), zip(NCS, WNC)):
    vals.append(val(n, g, rr, nc=nc)); ws.append(wn * wg * wr * wc)
qp = L.wq(vals, ws); qq = {k: v * (1 - LD) for k, v in qp.items()}
out.update(grid_pre=qp, grid_post=qq, grid_n=len(vals)); lab = L.label(PX, qq['P10'], qq['P90']); out['label'] = lab
print(f"LUOI n={len(vals)}: truoc {', '.join(f'{k} {v:,.0f}' for k,v in qp.items())} | sau {', '.join(f'{k} {v:,.0f}' for k,v in qq.items())}")
print(f"Gia {PX:,.0f}: vs tam {PX/out['center_post']-1:+.1%}, vs P10 {PX/qq['P10']-1:+.1%}, vs P90 {PX/qq['P90']-1:+.1%} => {lab}")
sens = {}
for b in (0.5, 1.0):
    for dd in (-0.01, -0.005, 0.005, 0.01):
        rr = L.r_of(dep + dd, b); c = sum(SC[k]['p'] * val(SC[k]['n'], SC[k]['g'], rr, nc=SC[k]['nc']) for k in SC)
        sens[f"b{b}_d{int(dd*1e4)}bp"] = dict(r=rr, center_pre=c, d_vnd=c - cpre, d_pct=c / cpre - 1)
out['sens_dep'] = sens
print("Do nhay lai huy dong: " + "; ".join(f"{k}: r {v['r']:.2%} -> {v['center_pre']:,.0f} ({v['d_vnd']:+,.0f}, {v['d_pct']:+.1%})" for k, v in sens.items()))
hs = {f"hold{int(h*100)}": sum(SC[k]['p'] * val(SC[k]['n'], SC[k]['g'], hold=h, nc=SC[k]['nc']) for k in SC) * (1 - LD) for h in (0.10, 0.25)}
out['sens_holdco_post'] = hs
print("Do nhay CK holdco tren co phan niem yet (KHONG trong base, chua co co so du lieu): " + ", ".join(f"{k} {v:,.0f}" for k, v in hs.items()))
for q in ('1', '5', '10'):
    c = LQ['pos'][q]
    print(f"Vi the {q} ty: CK Y0,5/1/1,5 = {c['disc_Y05']:.1%}/{c['disc_Y1']:.1%}/{c['disc_Y15']:.1%}; {c['days_at20']:.0f}-{c['days_at10']:.0f} phien @20-10%")
print(f"ADV trung vi {LQ['adv_med_vnd']/1e9:.2f} ty ({LQ['adv_med_shares']:,.0f} cp; {LQ['window']}; {LQ['zero_vol_days']} phien KL=0), sigma {LQ['sigma_d']:.2%}")
json.dump(out, open(os.path.join(HERE, 'model_out.json'), 'w'), indent=1, default=float)
