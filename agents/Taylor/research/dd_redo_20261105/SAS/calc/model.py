"""SAS redo 05/11/2026 (job Taylor_20261105_014133). Chay: $DNA_PYEXE -B model.py > model_out.txt
Nguon BCTC: src/Q3_2026_tonghop_kemgiaitrinh.pdf (assets.sasco.com.vn, CBTT 20/10/2026; BCTC TONG HOP giua nien do Q3/2026, scan,
doc tu anh img/p07-p12 = in trang 1-6; giai trinh img/p04). Don vi ty dong.
Phuong phap: gia tri = tien thua + dau tu tai chinh dai han (gia so) + PV LN van hanh (loai thu nhap tai chinh) x ty le EPS/LNST,
2027 chuyen tiep (nua tac dong Long Thanh), tu 2028 LN = N0 x (1+Delta), Gordon g=3%."""
import sys, os, json, itertools
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', '_common'))
import liq as L
SH = 133.481310                                     # tr cp (von gop 1.334.813,1 tr / 10.000; BQ OShares 133,45 — chenh co phieu quy)
dep, dep_src = L.current_dep(); R = L.r_of(dep)
LQ = L.liq('SAS'); PX = LQ['price']; LD = LQ['disc_ref']
# --- BCTC 30/09/2026 [in tr.1-4] ---
CASH, HTM = 280.717512019, 664.486706849            # ma 110, 123
EMP_PAY, BONUS_FUND, TAX_PAY = 141.169135385, 99.711533217, 50.247155609   # ma 315, 323, 314
LT_INV = 253.830133419                              # ma 260 (LD-LK 161,4 + khac 107,2 - du phong 14,8), gia so
LT_RECV = 242.036924823                             # ma 215 phai thu dai han khac (chua doc thuyet minh) — KHONG tinh
INV, INV0 = 204.335973162, 68.911497308             # ma 140
EQ = 1878.261409822
# --- KQKD [in tr.5], LCTT [tr.6] ---
NP_9M, NP_Q3 = 539.458668050, 168.659616827
FIN_REV_9M, FIN_EXP_9M, FIN_REV_Q3 = 194.955804947, 6.671156612, 59.789348706
REV_9M, GP_9M = 2333.127223343, 1556.101376273
CFO_9M = 294.221808348
EPS_RATIO = 0.883     # EPS 2025 4.602 d / (LNST 2025 695,6 ty / 133,45 tr cp) — trich quy khen thuong (DD 26/10, DHDCD 2026)
G = 0.03
XCASH = CASH + HTM - EMP_PAY - BONUS_FUND - TAX_PAY
CORE_9M = NP_9M - (FIN_REV_9M - FIN_EXP_9M) * 0.80
N0 = CORE_9M * 4 / 3
print(f"Tien+HTM {CASH+HTM:.1f}; tien thua = tru phai tra NLD {EMP_PAY:.1f}, quy KTPL {BONUS_FUND:.1f}, thue {TAX_PAY:.1f} = {XCASH:.1f} ty ({XCASH/SH*1000:,.0f} d/cp); vay = 0")
print(f"Dau tu TC dai han gia so {LT_INV:.1f} ({LT_INV/SH*1000:,.0f} d/cp); phai thu dai han khac {LT_RECV:.1f} KHONG tinh")
print(f"LNST 9T {NP_9M:.1f}; thu nhap TC rong sau thue 9T {(FIN_REV_9M-FIN_EXP_9M)*0.8:.1f} => LN van hanh 9T {CORE_9M:.1f}, nam hoa N0 {N0:.1f}; CFO 9T {CFO_9M:.1f} ({CFO_9M/NP_9M:.2f}x LNST); HTK {INV0:.1f} -> {INV:.1f}")
print(f"Bien gop 9T {GP_9M/REV_9M:.1%}; r = {R:.2%} (dep {dep:.2%} [{dep_src}]); gia {PX:,.0f} ({LQ['price_date']})")

def val(delta, n0=N0, r=R, g=G):
    e27 = n0 * (1 + delta / 2); e28 = n0 * (1 + delta)
    pv = e27 / (1 + r) + e28 / (r - g) / (1 + r)
    return (XCASH + LT_INV + pv * EPS_RATIO) / SH * 1000

SC = {"xau (truot thau LT chinh, -50%)": dict(d=-0.50, p=0.30), "co so (thi phan LT nho hon, -25%)": dict(d=-0.25, p=0.45),
      "tot (thang thau lon LT, +5%)": dict(d=0.05, p=0.25)}
out = dict(ticker='SAS', price=PX, price_date=LQ['price_date'], r=R, dep=dep, dep_src=dep_src, liq=LQ, xcash=XCASH, n0=N0, scen={})
for k, p in SC.items():
    v = val(p['d']); out['scen'][k] = dict(pre=v, post=v * (1 - LD), **p)
    print(f"{k:36s} p={p['p']:.2f}: {v:,.0f} -> sau CK TK {v*(1-LD):,.0f}")
cpre = sum(SC[k]['p'] * out['scen'][k]['pre'] for k in SC); out['center_pre'] = cpre; out['center_post'] = cpre * (1 - LD)
print(f"TAM truoc CK {cpre:,.0f} | CK thanh khoan {LD:.2%} (5 ty) | sau {cpre*(1-LD):,.0f} | gia/tam {PX/(cpre*(1-LD))-1:+.1%}")
DS = (-0.55, -0.40, -0.25, -0.10, 0.05); WD = (0.1, 0.2, 0.4, 0.2, 0.1)
NS = (N0 * 0.9, N0, N0 * 1.1); WN = (0.25, 0.5, 0.25); RS = (R - 0.01, R, R + 0.01); WR = (0.25, 0.5, 0.25)
vals, ws = [], []
for (d, wd), (n, wn), (rr, wr) in itertools.product(zip(DS, WD), zip(NS, WN), zip(RS, WR)):
    vals.append(val(d, n, rr)); ws.append(wd * wn * wr)
qp = L.wq(vals, ws); qq = {k: v * (1 - LD) for k, v in qp.items()}
out.update(grid_pre=qp, grid_post=qq, grid_n=len(vals)); lab = L.label(PX, qq['P10'], qq['P90']); out['label'] = lab
print(f"LUOI n={len(vals)}: truoc {', '.join(f'{k} {v:,.0f}' for k,v in qp.items())} | sau {', '.join(f'{k} {v:,.0f}' for k,v in qq.items())}")
print(f"Gia {PX:,.0f}: vs tam {PX/out['center_post']-1:+.1%}, vs P10 {PX/qq['P10']-1:+.1%}, vs P90 {PX/qq['P90']-1:+.1%} => {lab}")
sens = {}
for b in (0.5, 1.0):
    for dd in (-0.01, -0.005, 0.005, 0.01):
        rr = L.r_of(dep + dd, b); c = sum(SC[k]['p'] * val(SC[k]['d'], r=rr) for k in SC)
        sens[f"b{b}_d{int(dd*1e4)}bp"] = dict(r=rr, center_pre=c, d_vnd=c - cpre, d_pct=c / cpre - 1)
out['sens_dep'] = sens
print("Do nhay lai huy dong: " + "; ".join(f"{k}: r {v['r']:.2%} -> {v['center_pre']:,.0f} ({v['d_vnd']:+,.0f}, {v['d_pct']:+.1%})" for k, v in sens.items()))
for q in ('1', '5', '10'):
    c = LQ['pos'][q]
    print(f"Vi the {q} ty: CK Y0,5/1/1,5 = {c['disc_Y05']:.1%}/{c['disc_Y1']:.1%}/{c['disc_Y15']:.1%}; {c['days_at20']:.0f}-{c['days_at10']:.0f} phien @20-10%")
print(f"ADV trung vi {LQ['adv_med_vnd']/1e9:.2f} ty ({LQ['adv_med_shares']:,.0f} cp; {LQ['window']}), sigma {LQ['sigma_d']:.2%}")
json.dump(out, open(os.path.join(HERE, 'model_out.json'), 'w'), indent=1, default=float)
