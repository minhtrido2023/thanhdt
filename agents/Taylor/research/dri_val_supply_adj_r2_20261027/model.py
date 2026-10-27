"""Định giá lại DRI lần 2 (job Taylor_20261027_093047). Lưới khai trước: PREREG.md (commit eb3be59b0).
Không sửa file cũ; đọc snapshot BQ của bản trước ở ../dri_val_supply_adj_20261027/data/. Chạy: python3 model.py"""
import csv, os, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__))
PREV = os.path.join(HERE, '..', 'dri_val_supply_adj_20261027', 'data')
WC = '/home/trido/thanhdt/WorkingClaude/data'
SH, PX = 73.2e6, 14700                                            # [BCTN] / [BQ Price 26/10]
rows = [(m, float(p)) for m, p in csv.reader(open(f'{WC}/rubber_monthly.csv')) if m != 'month']
RSS = dict(rows)
med10 = st.median([p for m, p in rows if '2016-10' <= m <= '2026-09']); med5 = st.median([p for m, p in rows if '2021-10' <= m <= '2026-09'])
def ymean(y): return st.mean([p for m, p in rows if m.startswith(y)])
rss25 = ymean('2025'); rssq3 = st.mean([RSS[m] for m in ('2026-07', '2026-08', '2026-09')])
fx = {}
for d, x in csv.reader(open(f'{WC}/macro_usdvnd.csv')):
    if d != 'time': fx.setdefault(d[:4], []).append(float(x))
FX = {y: st.mean(v) for y, v in fx.items()}
# ---------- hằng số model_q3 [BCTC3] ----------
SGA3, FIN3, TAX3 = 5.093+12.131, 6.345-3.562, (5.279+0.503)/31.650
V0, OTHER_GP = 14000, 10
SGA, FIN = SGA3*4, FIN3*4*0.83
NETC = 72.571+271.809 - 87.039-20.598 - 73.922; DKR = 40*0.5
LAO_CASH = 154.66 + 30.551 + 11.515                               # tiền gửi tại NH Lào 30/09 [BCTC3]
BVPS = 729.862154663e9/SH                                         # VCSH mẹ 30/09 sau cổ tức phải trả [BCTC3]
P25 = 47.24
def price(rss): return P25*rss/rss25
def pre(V_, P, C, sga, fin, oth): return V_*(P-C)/1e3 + oth - sga + fin
Q4 = {"Bear": (3500, 52.0, 36.5, 25), "Base": (4200, 56.0, 35.0, 15), "Bull": (4900, 59.0, 34.0, 0)}
def q4_npat(k, dV=0): V_, P, C, b = Q4[k]; return pre(V_+dV, P, C, SGA3+b, FIN3, 2.0)*(1-TAX3)
def lnst_old(P, C, sga=SGA): return (V0*(P-C)/1e3 + OTHER_GP - sga + FIN)*(1-TAX3)

# ================= 0a. SELFCHECK: REPORT_Q3_UPDATE §6.2 =================
RUN = 167.44 + q4_npat("Base"); S_old = []
for rss, c, r_, peak, w in [(med10, 32.0, .14, .5, .25), ((med10+med5)/2, 32.5, .13, 1.0, .5), (med5, 33.0, .12, 2.0, .25)]:
    ni = lnst_old(price(rss), c, SGA*0.9); core = ni - NETC*0.05*0.8; ann = (1-(1+r_)**-28)/r_
    exc = sum((RUN-ni)*0.9/(1+r_)**(t+0.5) for t in range(int(peak))) + (peak % 1)*(RUN-ni)*0.9/(1+r_)**(int(peak)+0.5)
    S_old.append(((core*0.9*ann + exc + NETC + DKR)*1e9/SH, w))
ev_old = sum(f*w for f, w in S_old)
print(f"0a) SELFCHECK model_q3: Base {S_old[1][0]:,.0f} | kỳ vọng {ev_old:,.0f}")
assert abs(round(S_old[1][0]) - 10878) <= 1 and abs(round(ev_old) - 11031) <= 1, "KHÔNG tái lập 10.878/11.031"

# ================= 1. model mới =================
T_Q4, T27, T_INV, END = 0.17, 0.67, 0.4, 2054
def path(scn, mid):
    half = mid + 0.5*(rssq3 - mid)
    return {2027: half, 2028: mid} if scn == "PEAK" else {2027: rssq3, 2028: half}
def vol(y, d, d0): return V0 if y < d0 else V0*(1-d)**(y-d0+1)
def cost(P, V, Cref, k, f): return (Cref + k*(P-P25))*((1-f) + f*V0/V)
def ni(P, V, Cref, k, f): return (V*(P-cost(P, V, Cref, k, f))/1e3 + OTHER_GP - SGA*0.9 + FIN)*(1-TAX3)
CEN = dict(r=.12, life="L0", Cref=32.0, k=None, f=.5, d=.02, d0=2035, wht=.10, h=.15, X=1717, q4="Base", h_all=False)
def fv1(scn, mid, r, life, Cref, k, f, d, d0, wht, h, X, q4, h_all, parts=False):
    pth = path(scn, mid); pv = 0.0
    dV = -(X-1717) if X > 1717 else 0
    q4v = 0.9*q4_npat(q4, dV)/(1+r)**T_Q4
    lk = (1-wht)*((1-h) if h_all else 1)
    for y in range(2027, END+1):
        P = price(pth.get(y, mid)); pv += lk*0.9*(ni(P, vol(y, d, d0), Cref, k, f) - NETC*0.05*0.8)/(1+r)**(T27+y-2027)
    fcf_n = lk*0.9*(ni(price(mid), vol(END, d, d0), Cref, k, f) - NETC*0.05*0.8)
    pi = {"L0": 0, "L1": .5, "L2": 1}[life]; tv = pi*fcf_n/r/(1+r)**(END+1-2026.83)
    P27 = price(pth[2027]); inv = X*(P27 - TAX3*(P27-36.54))/1e3/(1+r)**T_INV
    cash = NETC + DKR - h*LAO_CASH
    v = (q4v + pv + tv + inv + cash)*1e9/SH
    return (v, dict(q4=q4v, ops=pv, tv=tv, inv=inv, cash=cash)) if parts else v
def fv(mid, wp=.6, **kw):
    a = {**CEN, **kw}
    return wp*fv1("PEAK", mid, **a) + (1-wp)*fv1("MID", mid, **a)

# ================= 0b. SELFCHECK: tái lập 14.301 của bản trước =================
OLD = dict(r=.12, life="L0", Cref=34.0, k=0.0, f=0.0, d=0.0, d0=2035, wht=0.0, h=0.0, X=1717, q4="Base", h_all=False)
def prev_coupled(wp=.6, **kw):
    a = {**OLD, **kw}
    pk = st.mean([fv1("PEAK", m, **a) for m in (1.865, 1.97, 2.075)]); md = st.mean([fv1("MID", m, **a) for m in (2.18, 2.30)])
    return wp*pk + (1-wp)*md
p0 = prev_coupled(); print(f"0b) SELFCHECK bản trước (ghép mid, C34, k0, V phẳng): {p0:,.0f}")
assert abs(round(p0) - 14301) <= 1, "KHÔNG tái lập 14.301"
print("   PASS cả hai (10.878 / 11.031 / 14.301)")

# ================= 2. đầu vào & đối chiếu định nghĩa giá vốn =================
print(f"\n1) RSS3 [FEED]: TB2025 {rss25:.3f} · Q3/26 {rssq3:.3f} · trung vị danh nghĩa 10 năm {med10:.3f} · 5 năm {med5:.3f}")
CPI = {2016: 240.0, 2017: 245.1, 2018: 251.1, 2019: 255.7, 2020: 258.8, 2021: 271.0, 2022: 292.7, 2023: 304.7, 2024: 313.7, 2025: 322.0, 2026: 330.0}  # [NỀN, UL]
for lab, m0 in (("10 năm", '2016-10'), ("5 năm", '2021-10')):
    real = [p*CPI[2025]/CPI[int(m[:4])] for m, p in rows if m0 <= m <= '2026-09']
    print(f"   trung vị {lab} quy USD 2025 thực [CPI NỀN/UL]: {st.median(real):.3f}")
print("   GVHB/t (định nghĩa model) vs 'giá vốn/t' BCTN [BCTN24/25, BCTC3]:")
for y, cogs, t, bctn in (("2024", 281.493, 10108.24, 31.980), ("2025", 422.039, 14007.76, 33.11), ("9T/26", 377.401, 11989.49, None)):
    c = cogs*1e3/t; s = f"   {y}: GVHB {cogs:.1f} tỷ / {t:,.0f} t = {c:.2f} tr/t"
    if bctn: s += f" | BCTN {bctn:.2f} | chênh × tấn = {(bctn-c)*t/1e3:.1f} tỷ (BH {30.531 if y=='2024' else 30.626:.1f})"
    print(s)
print(f"   giá bán/t: 2024 {444.566e3/10108.24:.2f} · 2025 {661.70e3/14007.76:.2f} · 9T/26 (DT 9T/tấn) {622.002e3/11989.49:.2f} tr/t")

# ================= 3. backcast & chọn k =================
npy = {}
for x in csv.DictReader(open(os.path.join(PREV, 'dri_peers_fin.csv'))):
    if x['ticker'] == 'DRI': npy[x['quarter'][:4]] = npy.get(x['quarter'][:4], 0) + float(x['NP_P0'])/1e9
VY = {'2021': 14000, '2022': 14000, '2023': 10108.24/(1-.3003), '2024': 10108.24, '2025': 14007.76}
USD = {'2024': 1788.19, '2025': 1857.01}                             # giá USD/t thực DRI [BCTN]
def Py(y, actual=False):
    if actual and y in USD: return P25*USD[y]/USD['2025']*FX[y]/FX['2025']
    return P25*ymean(y)/rss25*FX[y]/FX['2025']
def ccal(k, f=.5):
    V = VY['2025']; C = 47.24 - ((157.4/(1-TAX3) - OTHER_GP + SGA*0.9 - FIN)*1e3/V)
    return C/((1-f) + f*V0/V)                                          # P_2025 = 47,24 ⇒ k không ảnh hưởng
print(f"\n2) BACKCAST LNST (f 0,5; C_ref = C_cal; SGA/FIN/thuế model) vs thật [BQ ΣNP_P0]; FX TB năm [FEED]")
print("   năm  RSS3   FX     P_y   V_y    thật | " + " | ".join(f"k={k:.1f}: model (sai)" for k in (0, .3, .6)))
rmse = {}
for k in (0, .3, .6):
    cr = ccal(k); rmse[k] = (st.mean([(ni(Py(y), VY[y], cr, k, .5) - npy[y])**2 for y in ('2021', '2022', '2023', '2024')]))**.5
for y in ('2021', '2022', '2023', '2024', '2025'):
    print(f"   {y} {ymean(y):.3f} {FX[y]:6,.0f} {Py(y):5.2f} {VY[y]:6,.0f} {npy[y]:6.1f} | " +
          " | ".join(f"{ni(Py(y), VY[y], ccal(k), k, .5):6.1f} ({ni(Py(y), VY[y], ccal(k), k, .5)-npy[y]:+6.1f})" for k in (0, .3, .6)))
print("   RMSE 2021–2024: " + " · ".join(f"k={k:.1f}: {v:.1f}" for k, v in rmse.items()) + f" | C_cal = {ccal(0):.2f} tr/t")
K = min(rmse, key=rmse.get); CEN['k'] = K
print(f"   ⇒ k chọn theo luật PREREG = {K}")
print("   chẩn đoán (không dùng để chọn): giá USD thực DRI 2024/2025: " +
      " · ".join(f"k={k:.1f}: 2024 {ni(Py('2024', True), VY['2024'], ccal(k), k, .5):.1f} (thật {npy['2024']:.1f})" for k in (0, .3, .6)))
for k in (0, .3, .6):
    print(f"   dốc LNST theo RSS3 ở V 14.000, k={k}: {(ni(price(2.2), V0, 32, k, .5)-ni(price(2.1), V0, 32, k, .5))*10:.0f} tỷ/($/kg)")

# ================= 4. FV theo từng mid =================
MIDS = [1.865, 1.97, 2.075, 2.18]; W = [(.8, "80/20"), (.6, "60/40"), (.4, "40/60")]
def table(title, **kw):
    print(f"\n{title}")
    print("   trọng số | " + " | ".join(f"mid {m:.3f}      " for m in MIDS))
    for wp, n in W:
        print(f"   {n:8s} | " + " | ".join(f"{fv(m, wp, **kw):7,.0f} ({PX/fv(m, wp, **kw)-1:+4.0%})" for m in MIDS))
table(f"3) FV TÂM (k {K}, C_ref 32, f 0,5, d 2%/2035, w 10%, h 15%, r 12%, L0, X 1.717, Q4 Base); ngoặc = 14.700 so FV")
table("3b) cùng tâm nhưng k = 0 (hàm cũ, dốc ~248)", k=0.0)
for m in (1.97, 2.075):
    v, p = fv1("PEAK", m, **CEN, parts=True); print(f"   phân rã PEAK mid {m} (tỷ): " + " ".join(f"{a} {b:.1f}" for a, b in p.items()) + f" ⇒ {v:,.0f}")

print("\n4) KHOẢNG FV TRÊN LƯỚI KHAI TRƯỚC mỗi mid (r×C_ref{31,32,33}×k{chọn,0}×f×d×w×h×trọng số; X, Q4, L0 ở tâm)")
def pct(xs, q): xs = sorted(xs); return xs[int(round(q*(len(xs)-1)))]
GRID = {}
for m in MIDS:
    xs = []
    for r in (.10, .12, .13):
        for C in (31, 32, 33):
            for k in sorted({K, 0.0}):
                for f in (.3, .5, .7):
                    for d in (0, .02, .03):
                        for w in (0, .10):
                            for h in (0, .15, .30):
                                a = {**CEN, 'r': r, 'Cref': C, 'k': k, 'f': f, 'd': d, 'wht': w, 'h': h}
                                pk, md = fv1("PEAK", m, **a), fv1("MID", m, **a)
                                for wp, _ in W: xs.append((k, wp*pk + (1-wp)*md))
    GRID[m] = xs
    for lab, sel in (("k chọn", [v for k, v in xs if k == K]), ("k 0", [v for k, v in xs if k == 0.0])):
        print(f"   mid {m:.3f} {lab:6s} n={len(sel)}: min {min(sel):7,.0f} P10 {pct(sel,.1):7,.0f} trung vị {pct(sel,.5):7,.0f} P90 {pct(sel,.9):7,.0f} max {max(sel):7,.0f}"
              f" | tỷ lệ ô ≥ 14.700: {sum(v >= PX for v in sel)/len(sel):4.0%}")
print("   đối chứng (tâm, 60/40): " + " | ".join(f"mid {m}: C34 {fv(m, Cref=34):,.0f} C_cal({ccal(K):.2f}) {fv(m, Cref=ccal(K)):,.0f}" for m in MIDS))

print("\n5) ĐỘ NHẠY MỘT TRỤC quanh tâm (60/40), ở mid 1,97 và 2,075")
AX = [("C_ref [31/32/33 | 34]", 'Cref', [31, 32, 33, 34]), ("k [0/0,3/0,6]", 'k', [0, .3, .6]), ("r [10/12/13%]", 'r', [.10, .12, .13]),
      ("f [0,3/0,5/0,7]", 'f', [.3, .5, .7]), ("d từ 2035 [0/2/3%]", 'd', [0, .02, .03]), ("w Lào [0/10%]", 'wht', [0, .10]),
      ("h tiền Lào [0/15/30%]", 'h', [0, .15, .30]), ("tồn kho X [0/1.717/3.370]", 'X', [0, 1717, 3370]),
      ("Q4 [Bear/Base/Bull]", 'q4', list(Q4)), ("đời khai thác [L0/L1/L2]", 'life', ["L0", "L1", "L2"])]
for m in (1.97, 2.075):
    c0 = fv(m); res = []
    for lab, key, vals in AX: xs = [fv(m, **{key: v}) for v in vals]; res.append((max(xs)-min(xs), lab, xs))
    xs = [fv(m, wp) for wp, _ in W]; res.append((max(xs)-min(xs), "trọng số đường [80/20…40/60]", xs))
    print(f"   mid {m}: tâm {c0:,.0f}")
    for rng, lab, xs in sorted(res, key=lambda t: -t[0]):
        print(f"     {lab:30s} biên độ {rng:6,.0f} | " + " / ".join(f"{x:,.0f}" for x in xs))
xs = [fv(m) for m in MIDS]; print(f"   mid [1,865…2,18] ở tâm: biên độ {max(xs)-min(xs):,.0f} | " + " / ".join(f"{x:,.0f}" for x in xs))
print("   STRESS ngoài lưới: " + " | ".join(f"mid {m}: d 3%/2030 {fv(m, d=.03, d0=2030):,.0f}; h 30% cả FCF {fv(m, h=.30, h_all=True):,.0f}" for m in (1.97, 2.075)))

print("\n6) CẦU NỐI 14.301 → tâm mới (cộng dồn)")
cur = dict(OLD); last = p0
def stepv(m, a): return .6*fv1("PEAK", m, **a) + .4*fv1("MID", m, **a)
for m in (1.97, 2.075):
    cur = dict(OLD); last = p0; print(f"   đích mid {m}: xuất phát {p0:,.0f}")
    for lab, ch in [("bỏ ghép: mid chung", {}), ("C_ref 34 → 32", dict(Cref=32.0)), (f"k 0 → {K}", dict(k=K)),
                    ("sản lượng d 2%/2035 + f 0,5", dict(d=.02, f=.5)), ("phí chuyển LN Lào 10%", dict(wht=.10)), ("haircut tiền Lào 15%", dict(h=.15))]:
        cur.update(ch); v = stepv(m, cur); print(f"     {lab:30s} {v-last:+7,.0f} → {v:7,.0f}"); last = v

print(f"\n7) VÙNG MUA — biên an toàn = FV/ngưỡng − 1 (BVPS {BVPS:,.0f} đ [BCTC3]; PB ở 14.700 = {PX/BVPS:.2f}x)")
for thr, lab in ((13000, "≤13.000"), (11500, "≤11.500"), (round(BVPS), "PB≤1 (~9.971)")):
    print(f"   {lab:14s} PB {thr/BVPS:.2f}x | tâm 60/40: " + " ".join(f"mid {m}: {fv(m)/thr-1:+5.0%}" for m in MIDS))
    print(f"   {'':14s} lưới (k chọn) tỷ lệ ô FV ≥ ngưỡng: " + " ".join(f"mid {m}: {sum(v >= thr for k, v in GRID[m] if k == K)/sum(1 for k, _ in GRID[m] if k == K):4.0%}" for m in MIDS))
print("   PB trung vị theo pha [BQ, out.txt bản trước mục 7]: DRI PEAK 1,49 · MID 1,25 · TROUGH 0,65 ⇒ PB≤1 lịch sử chủ yếu ở TROUGH")

print("\n8) POST-HOC (ngoài PREREG, không đổi tâm/lưới): backcast với f = 0 (2024: V −28% mà GVHB/t 27,85 < 2025 30,13)")
for k in (0, .3, .6):
    cr = ccal(k, 0.0); e = {y: ni(Py(y), VY[y], cr, k, 0.0) - npy[y] for y in ('2021', '2022', '2023', '2024')}
    print(f"   k={k}: " + " ".join(f"{y} {v:+6.1f}" for y, v in e.items()) + f" | RMSE {st.mean([v*v for v in e.values()])**.5:.1f}")
print(f"   C_ref tương đương số đo 9T/26 (31,48 @ P 51,88) theo k chọn {K}: {31.48 - K*(51.88-P25):.2f}; theo k 0: 31,48")
