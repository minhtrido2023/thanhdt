"""NT2 redo 05/11/2026 (job Taylor_20261105_014133). Chay: $DNA_PYEXE -B model.py > model_out.txt
Nguon BCTC: src/Q3_2026_hopnhat_va_giaitrinh.pdf (CBTT 1394/CPNT2-TCKT 19/10/2026; BCTC RIENG mau B01a-DN — NT2 khong co cong ty con),
doc tu anh img/p06-p09 (in tr.2-5). Don vi ty dong.
Phuong phap (giu tu DD 26/10, dung lai so): SOTP = net cash that + PV dong tien van hanh co thoi han (PPA/GSA ~10/2036).
LNST van hanh = LNST chuan hoa - thu nhap tai chinh rong sau thue (tranh dem 2 lan voi net cash). FCF van hanh ~ LNST van hanh
(khau hao con ~153/nam ~ capex duy tri)."""
import sys, os, json, itertools
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', '_common'))
import liq as L
SH = 287.876029                                     # tr cp (von gop 2.878,76 ty / 10.000)
dep, dep_src = L.current_dep(); R = L.r_of(dep)
LQ = L.liq('NT2'); PX = LQ['price']; LD = LQ['disc_ref']
# --- BCTC 30/09/2026 [tr.2-3] ---
CASH, HTM_ST = 11.835947084, 5362.324001394          # ma 110, 123
LOAN = 1795.772639513                                # ma 321 (vay ngan han; no dai han = 0)
DIV_PAY = 297.125837477                              # ma 313: co tuc phai tra (GDKHQ 29/10/2026 — gia 04/11 da tru)
AR, AP, ACCR = 4252.014358468, 2637.441833617, 777.396880480
EQ = 5421.366757659
# --- KQKD 9T/2026 [tr.4] ---
FIN_REV_9M, FIN_EXP_9M = 226.366187841, 68.448729333
NP_9M, NP_Q3 = 906.356157027, 418.613274776
DA_9M = 114.824628961; CFO_9M = 1256.214442787      # LCTT tr.5
NET_CASH = CASH + HTM_ST - LOAN - DIV_PAY
FIN_NET_AT = (FIN_REV_9M - FIN_EXP_9M) * 4 / 3 * 0.80   # thu nhap tai chinh rong sau thue nam hoa (thue 20%)
print(f"Net cash that = tien {CASH:.1f} + HTM {HTM_ST:.1f} - vay {LOAN:.1f} - co tuc phai tra {DIV_PAY:.1f} = {NET_CASH:,.1f} ty = {NET_CASH/SH*1000:,.0f} d/cp")
print(f"Von luu dong: phai thu KH {AR:,.1f} - phai tra NB {AP:,.1f} - CP phai tra {ACCR:,.1f} = {AR-AP-ACCR:,.1f} (KHONG cong vao gia tri)")
print(f"Thu nhap TC rong sau thue nam hoa {FIN_NET_AT:.0f}; LNST 9T {NP_9M:.1f} (Q3 {NP_Q3:.1f}); KH 9T {DA_9M:.1f}; CFO 9T {CFO_9M:.1f} (CFO/LNST {CFO_9M/NP_9M:.2f})")
print(f"r = {R:.2%} (dep {dep:.2%} [{dep_src}], neo {L.DEP_ANCHOR:.2%}); gia {PX:,.0f} ({LQ['price_date']})")

def val(np_norm, yrs=10.0, r=R, tv_mult=0.0):
    op = np_norm - FIN_NET_AT
    n = int(yrs); frac = yrs - n
    pv = sum(op / (1 + r) ** t for t in range(1, n + 1)) + (op * frac / (1 + r) ** (n + 1) if frac else 0)
    return (NET_CASH + pv) / SH * 1000

# kich ban LNST chuan hoa/nam (uoc luong; neo: nam xau 2024 LN 83 + bu khau hao da het ~+320 => ~400; BSC 2027 767 / VDSC; lap lai 2026)
SC = {"xau": dict(np=400, p=0.25), "co so": dict(np=800, p=0.50), "tot": dict(np=1150, p=0.25)}
out = dict(ticker='NT2', price=PX, price_date=LQ['price_date'], r=R, dep=dep, dep_src=dep_src, liq=LQ, net_cash=NET_CASH, fin_net_at=FIN_NET_AT, scen={})
for k, p in SC.items():
    v = val(p['np']); out['scen'][k] = dict(pre=v, post=v * (1 - LD), **p)
    print(f"{k:7s} p={p['p']:.2f} LNST chuan hoa {p['np']} (van hanh {p['np']-FIN_NET_AT:.0f}), PPA 10 nam: {v:,.0f} -> sau CK TK {v*(1-LD):,.0f}")
cpre = sum(SC[k]['p'] * out['scen'][k]['pre'] for k in SC); out['center_pre'] = cpre; out['center_post'] = cpre * (1 - LD)
print(f"TAM truoc CK {cpre:,.0f} | CK thanh khoan {LD:.2%} | sau {cpre*(1-LD):,.0f} | gia/tam {PX/(cpre*(1-LD))-1:+.1%}")
# LUOI: LNST chuan hoa {400,600,800,1000,1150}? -> doi xung quanh 800: {450,625,800,975,1150} x thoi han con lai {8,10,12} x r ±100bp
NPS = (450, 625, 800, 975, 1150); WNP = (0.1, 0.2, 0.4, 0.2, 0.1)
YRS = (8, 10, 12); WY = (0.25, 0.5, 0.25); RS = (R - 0.01, R, R + 0.01); WR = (0.25, 0.5, 0.25)
vals, ws = [], []
for (a, wa), (y, wy), (rr, wr) in itertools.product(zip(NPS, WNP), zip(YRS, WY), zip(RS, WR)):
    vals.append(val(a, y, rr)); ws.append(wa * wy * wr)
qp = L.wq(vals, ws); qq = {k: v * (1 - LD) for k, v in qp.items()}
out.update(grid_pre=qp, grid_post=qq, grid_n=len(vals)); lab = L.label(PX, qq['P10'], qq['P90']); out['label'] = lab
print(f"LUOI n={len(vals)}: truoc {', '.join(f'{k} {v:,.0f}' for k,v in qp.items())} | sau {', '.join(f'{k} {v:,.0f}' for k,v in qq.items())}")
print(f"Gia {PX:,.0f}: vs tam {PX/out['center_post']-1:+.1%}, vs P10 {PX/qq['P10']-1:+.1%}, vs P90 {PX/qq['P90']-1:+.1%} => {lab}")
sens = {}
for b in (0.5, 1.0):
    for d in (-0.01, -0.005, 0.005, 0.01):
        rr = L.r_of(dep + d, b); c = sum(SC[k]['p'] * val(SC[k]['np'], r=rr) for k in SC)
        sens[f"b{b}_d{int(d*1e4)}bp"] = dict(r=rr, center_pre=c, d_vnd=c - cpre, d_pct=c / cpre - 1)
out['sens_dep'] = sens
print("Do nhay lai huy dong: " + "; ".join(f"{k}: r {v['r']:.2%} -> {v['center_pre']:,.0f} ({v['d_vnd']:+,.0f}, {v['d_pct']:+.1%})" for k, v in sens.items()))
ext = {f"PPA_{y}y": sum(SC[k]['p'] * val(SC[k]['np'], y) for k in SC) * (1 - LD) for y in (8, 12, 15)}
out['sens_ppa_post'] = ext
print("Do nhay thoi han dong tien (tam sau CK): " + ", ".join(f"{k} {v:,.0f}" for k, v in ext.items()))
print(f"PE ngam dinh: gia {PX:,.0f} - net cash {NET_CASH/SH*1000:,.0f} = {PX-NET_CASH/SH*1000:,.0f} d/cp tren LNST van hanh co so {(800-FIN_NET_AT)/SH*1000:,.0f} d/cp = {(PX-NET_CASH/SH*1000)/((800-FIN_NET_AT)/SH*1000):.1f}x")
print(f"Thanh khoan: ADV {LQ['adv_med_vnd']/1e9:.1f} ty ({LQ['window']}), sigma {LQ['sigma_d']:.2%}; CK 1/5/10 ty = " + "/".join(f"{LQ['pos'][q]['disc_Y1']:.1%}" for q in ('1','5','10')) + f"; 5 ty = {LQ['pos']['5']['days_at20']:.1f}-{LQ['pos']['5']['days_at10']:.1f} phien @20-10%")
json.dump(out, open(os.path.join(HERE, 'model_out.json'), 'w'), indent=1, default=float)
