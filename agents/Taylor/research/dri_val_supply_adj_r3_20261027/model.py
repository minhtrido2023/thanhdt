"""Định giá lại DRI lần 3 (job Taylor_20261027_100801). Lưới khai trước: PREREG.md (commit ee77a6821).
Không sửa file cũ; đọc snapshot BQ của r1 ở ../dri_val_supply_adj_20261027/data/. Chạy: python3 model.py"""
import csv, os, itertools, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__))
PREV = os.path.join(HERE, '..', 'dri_val_supply_adj_20261027', 'data')
WC = '/home/trido/thanhdt/WorkingClaude/data'
SH, PX, PX27 = 73.2e6, 14700, 14400                               # [BCTN] / [BQ 26/10] / giá đóng 27/10 [dispatch]
rows = [(m, float(p)) for m, p in csv.reader(open(f'{WC}/rubber_monthly.csv')) if m != 'month']
RSS = dict(rows)
med10 = st.median([p for m, p in rows if '2016-10' <= m <= '2026-09']); med5 = st.median([p for m, p in rows if '2021-10' <= m <= '2026-09'])
def ymean(y): return st.mean([p for m, p in rows if m.startswith(y)])
rss25 = ymean('2025'); rssq3 = st.mean([RSS[m] for m in ('2026-07', '2026-08', '2026-09')])
fx = {}
for d, x in csv.reader(open(f'{WC}/macro_usdvnd.csv')):
    if d != 'time': fx.setdefault(d[:4], []).append(float(x))
FX = {y: st.mean(v) for y, v in fx.items()}
# ---------- hằng số [BCTC3] ----------
SGA3, FIN3, TAX3 = 5.093+12.131, 6.345-3.562, (5.279+0.503)/31.650
TAX9 = (39.496122365+1.277267554)/208.213296385                     # thuế hiệu dụng 9T/26 [BCTC3 KQKD 9T]
V0, OTHER_GP = 14000, 10
SGA, FIN = SGA3*4, FIN3*4*0.83
NETC = 72.571+271.809 - 87.039-20.598 - 73.922; DKR = 40*0.5
LAO_CASH = 154.66 + 30.551 + 11.515                               # tiền gửi tại NH Lào 30/09 [BCTC3]
TDND = 70.0                                                       # tiền gửi Quỹ TDND Cao su ĐL 30/09, nằm trong 271,8 [BCTC3 hn_18]
BVPS = 729.862154663e9/SH
KTPL = 16.680422396/157.4                                         # trích KTPL 9T/26 / LNST 2025 [BCTC3 hn_29; BQ]
KTPL24 = 11.554363921/108.8                                       # kiểm chéo năm trước
TAU = 12.304334157/157.4                                          # quỹ dự phòng tài chính Lào / LNST 2025 [BCTC3]
WHT_OBS = (11.073900741/157.4, 9.028985800/108.8)                 # khấu trừ tại nguồn / LNST năm trước (quan sát)
PI = 0.03                                                         # lạm phát VN [NỀN]
P25 = 47.24
def price(rss): return P25*rss/rss25
def pre(V_, P, C, sga, fin, oth): return V_*(P-C)/1e3 + oth - sga + fin
Q4 = {"Bear": (3500, 52.0, 36.5, 25), "Base": (4200, 56.0, 35.0, 15), "Bull": (4900, 59.0, 34.0, 0)}
def q4_npat(k, dV=0): V_, P, C, b = Q4[k]; return pre(V_+dV, P, C, SGA3+b, FIN3, 2.0)*(1-TAX3)
def lnst_old(P, C, sga=SGA): return (V0*(P-C)/1e3 + OTHER_GP - sga + FIN)*(1-TAX3)

# ================= 0a. SELFCHECK model_q3 =================
RUN = 167.44 + q4_npat("Base"); S_old = []
for rss, c, r_, peak, w in [(med10, 32.0, .14, .5, .25), ((med10+med5)/2, 32.5, .13, 1.0, .5), (med5, 33.0, .12, 2.0, .25)]:
    ni_ = lnst_old(price(rss), c, SGA*0.9); core = ni_ - NETC*0.05*0.8; ann = (1-(1+r_)**-28)/r_
    exc = sum((RUN-ni_)*0.9/(1+r_)**(t+0.5) for t in range(int(peak))) + (peak % 1)*(RUN-ni_)*0.9/(1+r_)**(int(peak)+0.5)
    S_old.append(((core*0.9*ann + exc + NETC + DKR)*1e9/SH, w))
ev_old = sum(f*w for f, w in S_old)
print(f"0a) SELFCHECK model_q3: Base {S_old[1][0]:,.0f} | kỳ vọng {ev_old:,.0f}")
assert abs(round(S_old[1][0]) - 10878) <= 1 and abs(round(ev_old) - 11031) <= 1, "KHÔNG tái lập 10.878/11.031"

# ================= 1. model tổng quát (r2 là trường hợp riêng) =================
T_Q4, T27, T_INV, END = 0.17, 0.67, 0.4, 2054
def path(scn, mid, T=1.60):
    half = mid + 0.5*(rssq3 - mid)
    if scn == "PEAK": return {2027: half, 2028: mid}
    if scn == "MID": return {2027: rssq3, 2028: half}
    return {2027: T, 2028: T}                                       # TROUGH
def vol(y, d, d0): return V0 if y < d0 else V0*(1-d)**(y-d0+1)
def cost(P, V, Cref, k, f): return (Cref + k*(P-P25))*((1-f) + f*V0/V)
def ni(P, V, Cref, k, f, tax=TAX3, cm=1.0):
    return (V*(P-cm*cost(P, V, Cref, k, f))/1e3 + OTHER_GP - SGA*0.9 + FIN)*(1-tax)
R2 = dict(r=.12, life="L0", Cref=32.0, k=0.3, f=.5, d=.02, d0=2035, wht=.10, h=.15, X=1717, q4="Base", h_all=False,
          tax=TAX3, ktpl=0.0, trap="free", frame="mix", g=0.0, tdnd=0.0, T=1.60, leak_all=False, floor=False)
def fv1(scn, mid, r, life, Cref, k, f, d, d0, wht, h, X, q4, h_all, tax, ktpl, trap, frame, g, tdnd, T, leak_all, floor=False, parts=False):
    rr = r if frame == "mix" else (1+r)/(1+PI) - 1
    pth = path(scn, mid, T); pv = 0.0; trapped = 0.0
    tau = TAU if trap in ("2054", "lost") else 0.0
    lk = (1-wht-ktpl-tau)*((1-h) if h_all else 1)
    lk_q4 = (1-wht-ktpl-tau) if leak_all else 1.0
    dV = -(X-1717) if X > 1717 else 0
    q4v = lk_q4*0.9*q4_npat(q4, dV)/(1+rr)**T_Q4
    for y in range(2027, END+1):
        P = price(pth.get(y, mid)); cm = (1+g)**(y-2026)
        core = ni(P, vol(y, d, d0), Cref, k, f, tax, cm) - NETC*0.05*0.8
        if floor: core = max(core, 0.0)
        pv += lk*0.9*core/(1+rr)**(T27+y-2027); trapped += tau*0.9*core
    trapv = trapped/(1+rr)**(T27+END+1-2027) if trap == "2054" else 0.0
    fcf_n = lk*0.9*(ni(price(mid), vol(END, d, d0), Cref, k, f, tax) - NETC*0.05*0.8)
    pi = {"L0": 0, "L1": .5, "L2": 1}[life]; tv = pi*fcf_n/rr/(1+rr)**(END+1-2026.83)
    P27 = price(pth[2027]); gain = (P27-36.54)*(1-tax)
    inv = X*(P27 - tax*(P27-36.54) - ((wht+ktpl+tau)*gain if leak_all else 0))/1e3/(1+rr)**T_INV
    cash = NETC + DKR - h*LAO_CASH - tdnd*TDND
    v = (q4v + pv + trapv + tv + inv + cash)*1e9/SH
    return (v, dict(q4=q4v, ops=pv, trap=trapv, tv=tv, inv=inv, cash=cash)) if parts else v

# ================= 0b/0c. SELFCHECK r1 14.301 và r2 12.481 =================
OLD = {**R2, 'Cref': 34.0, 'k': 0.0, 'f': 0.0, 'd': 0.0, 'wht': 0.0, 'h': 0.0}
def prev_coupled(wp=.6):
    pk = st.mean([fv1("PEAK", m, **OLD) for m in (1.865, 1.97, 2.075)]); md = st.mean([fv1("MID", m, **OLD) for m in (2.18, 2.30)])
    return wp*pk + (1-wp)*md
p0 = prev_coupled(); print(f"0b) SELFCHECK r1 (ghép mid, C34, k0, V phẳng): {p0:,.0f}")
assert abs(round(p0) - 14301) <= 1, "KHÔNG tái lập 14.301"
MIDS = [1.865, 1.97, 2.075, 2.18]
def fvw(mid, wp=.6, base=None, **kw):
    a = {**(base or R2), **kw}
    return wp*fv1("PEAK", mid, **a) + (1-wp)*fv1("MID", mid, **a)
r2row = [fvw(m) for m in MIDS]
print("0c) SELFCHECK r2 tâm 60/40: " + " / ".join(f"{v:,.0f}" for v in r2row))
assert [round(v) for v in r2row] == [11061, 12481, 13901, 15321], "KHÔNG tái lập hàng r2"
print("   PASS (10.878 / 11.031 / 14.301 / r2 11.061-12.481-13.901-15.321)")

# ================= 2. kiểm số đầu vào =================
print(f"\n1) ĐẦU VÀO ĐO: thuế 9T/26 {TAX9:.2%} (Q3 {TAX3:.2%}) · KTPL/LNST năm trước {KTPL:.2%} (2024→9T/25: {KTPL24:.2%})"
      f" · quỹ Lào {TAU:.2%} · khấu trừ tại nguồn/LNST năm trước {WHT_OBS[0]:.1%} / {WHT_OBS[1]:.1%} (model dùng w 10%)")
print(f"   RSS3 [FEED]: TB2025 {rss25:.3f} · Q3/26 {rssq3:.3f} · trung vị danh nghĩa 10 năm {med10:.3f} · 5 năm {med5:.3f} · TB2023 {ymean('2023'):.3f}")
print(f"   FY26E GVHB/t (377,4+145,9)/16.157 = {(377.401+145.9)*1e3/16157:.2f} @ P 53,71 ⇒ C_ref k0,3 = {(377.401+145.9)*1e3/16157-0.3*(53.71-P25):.2f}")
npy = {}
for x in csv.DictReader(open(os.path.join(PREV, 'dri_peers_fin.csv'))):
    if x['ticker'] == 'DRI': npy[x['quarter'][:4]] = npy.get(x['quarter'][:4], 0) + float(x['NP_P0'])/1e9
VY = {'2021': 14000, '2022': 14000, '2023': 10108.24/(1-.3003), '2024': 10108.24, '2025': 14007.76}
def Py(y): return P25*ymean(y)/rss25*FX[y]/FX['2025']
def ccal(tax, f=.5):
    V = VY['2025']; C = 47.24 - ((157.4/(1-tax) - OTHER_GP + SGA*0.9 - FIN)*1e3/V)
    return C/((1-f) + f*V0/V)
CCAL = ccal(TAX9)
print(f"   C_cal (khớp LNST 2025 157,4): thuế Q3 {ccal(TAX3):.2f} → thuế 9T {CCAL:.2f} tr/t")
rmse = {}
for k in (0, .3, .6):
    rmse[k] = st.mean([(ni(Py(y), VY[y], CCAL, k, .5, TAX9) - npy[y])**2 for y in ('2021', '2022', '2023', '2024')])**.5
K = min(rmse, key=rmse.get)
print("   BACKCAST RMSE 2021–24 (thuế 9T): " + " · ".join(f"k={k}: {v:.1f}" for k, v in rmse.items()) + f" ⇒ k chọn {K}")

# ================= 3. FV r3 =================
CEN = {**R2, 'Cref': CCAL, 'k': K, 'd0': 2030, 'tax': TAX9, 'ktpl': KTPL, 'trap': "2054", 'frame': "real", 'leak_all': True}
def fv(mid, wp=.6, **kw): return fvw(mid, wp, CEN, **kw)
def row(lab, vals): print(f"   {lab:34s} | " + " | ".join(f"{v:7,.0f} ({PX/v-1:+4.0%}/{PX27/v-1:+4.0%})" for v in vals))
print(f"\n2) FV r3 THEO MID (đ/cp; ngoặc = 14.700/14.400 so FV). Tâm: khung thực r_dn 12% (r thực {(1.12/1.03-1):.2%}), C_ref {CCAL:.2f}, k {K},"
      f" f 0,5, sản lượng −2%/năm từ 2030, thuế {TAX9:.2%}, KTPL {KTPL:.1%}, w 10%, quỹ Lào giữ tới 2054, h 15%, TDND 0, X 1.717, Q4 Base")
print("   " + " "*34 + " | " + " | ".join(f"mid {m:.3f}            " for m in MIDS))
row("TÂM 60/40", [fv(m) for m in MIDS])
row("TDND haircut 50%", [fv(m, tdnd=.5) for m in MIDS]); row("TDND haircut 100%", [fv(m, tdnd=1.0) for m in MIDS])
row("trọng số 80/20", [fv(m, .8) for m in MIDS]); row("trọng số 40/60", [fv(m, .4) for m in MIDS])
row("g trôi chi phí thực 1%/năm", [fv(m, g=.01) for m in MIDS])
row("khung TRỘN r2 (r 12% danh nghĩa)", [fv(m, frame="mix") for m in MIDS])
for m in (1.97, 2.075):
    v, p = fv1("PEAK", m, **CEN, parts=True); print(f"   phân rã PEAK mid {m} (tỷ): " + " ".join(f"{a} {b:.1f}" for a, b in p.items()) + f" ⇒ {v:,.0f}")

def pct(xs, q): xs = sorted(xs); return xs[int(round(q*(len(xs)-1)))]
AXES = dict(Cref=[30.0, CCAL, 31.5, 32.0], k=sorted({K, 0.0}), f=[.3, .5, .7], dd=[(a, b) for a in (2028, 2030, 2035) for b in (.02, .03)],
            r=[.10, .12, .13], g=[0, .01], trap=["free", "2054", "lost"], h=[0, .15, .30])
print(f"\n3) KHOẢNG FV TRÊN LƯỚI KHAI TRƯỚC mỗi mid (n = 69.984 ô; phân vị lưới KHÔNG phải xác suất)")
GRIDBASE = {}
for m in MIDS:
    base = []
    for C, k, f, (d0, d), r, g, tr, h in itertools.product(*AXES.values()):
        a = {**CEN, 'Cref': C, 'k': k, 'f': f, 'd0': d0, 'd': d, 'r': r, 'g': g, 'trap': tr, 'h': h}
        base.append((fv1("PEAK", m, **a), fv1("MID", m, **a), a))
    GRIDBASE[m] = base
    xs = [wp*pk + (1-wp)*md - t*TDND*1e9/SH for pk, md, _ in base for wp in (.8, .6, .4) for t in (0, .5, 1.0)]
    print(f"   mid {m:.3f}: min {min(xs):7,.0f} P10 {pct(xs,.1):7,.0f} trung vị {pct(xs,.5):7,.0f} P90 {pct(xs,.9):7,.0f} max {max(xs):7,.0f}"
          f" | ô ≥ 14.700: {sum(v >= PX for v in xs)/len(xs):4.0%} · ≥ 14.400: {sum(v >= PX27 for v in xs)/len(xs):4.0%}")

print("\n4) ĐỘ NHẠY MỘT TRỤC quanh tâm (60/40), cả bốn mid — biên độ (max−min) đ/cp")
AX1 = [("C_ref [30/C_cal/31,5/32]", 'Cref', AXES['Cref']), ("k [chọn/0]", 'k', AXES['k']), ("f [0,3/0,5/0,7]", 'f', AXES['f']),
       ("r_dn [10/12/13%]", 'r', AXES['r']), ("g trôi C thực [0/1%]", 'g', AXES['g']), ("quỹ Lào [tự do/2054/mất]", 'trap', AXES['trap']),
       ("h tiền Lào [0/15/30%]", 'h', AXES['h']), ("TDND [0/50/100%]", 'tdnd', [0, .5, 1.0]), ("tồn kho X [0/1.717/3.370]", 'X', [0, 1717, 3370]),
       ("Q4 [Bear/Base/Bull]", 'q4', list(Q4))]
res = {}
for m in MIDS:
    out = []
    for lab, key, vals in AX1: xs = [fv(m, **{key: v}) for v in vals]; out.append((lab, xs))
    xs = [fv(m, d0=a, d=b) for a, b in AXES['dd']]; out.append(("sản lượng d0×d [28/30/35 × 2/3%]", xs))
    xs = [fv(m, wp) for wp in (.8, .6, .4)]; out.append(("trọng số đường [80/20…40/60]", xs))
    res[m] = out
for i, (lab, _) in enumerate(res[MIDS[0]]):
    print(f"   {lab:34s} " + " | ".join(f"mid {m}: {max(res[m][i][1])-min(res[m][i][1]):5,.0f}" for m in MIDS)
          + f"  [{' / '.join(f'{x:,.0f}' for x in res[1.97][i][1])} @1,97]")
xs = [fv(m) for m in MIDS]; print(f"   mid [1,865…2,18] ở tâm: biên độ {max(xs)-min(xs):,.0f}")

print("\n5) CẦU NỐI r2 tâm → r3 tâm (cộng dồn, 60/40)")
for m in MIDS:
    cur = dict(R2); last = fvw(m, .6, cur); s = f"   mid {m}: r2 {last:,.0f}"
    for lab, ch in [("thuế 19,6%", dict(tax=TAX9)), (f"C_ref 32→{CCAL:.2f}", dict(Cref=CCAL)), (f"k→{K}", dict(k=K)),
                    ("KTPL+rò rỉ Q4/tồn kho", dict(ktpl=KTPL, leak_all=True)), ("quỹ Lào giữ 2054", dict(trap="2054")),
                    ("khung thực", dict(frame="real")), ("sản lượng 2035→2030", dict(d0=2030))]:
        cur.update(ch); v = fvw(m, .6, cur); s += f" | {lab} {v-last:+,.0f}"; last = v
    print(s + f" ⇒ {last:,.0f}")

print("\n6) VÙNG MUA trên ĐƯỜNG ĐÁY: RSS3 2027 = 2028 = T, 2029+ = mid; biên = FV_TROUGH/ngưỡng − 1 (✓ = ≥15%)")
THR = [9000, 10000, 11500, 13000]
for T in (1.60, 1.70):
    for lab, kw in (("tâm", {}), ("TDND 100%", dict(tdnd=1.0))):
        fvt = {m: fv1("TROUGH", m, **{**CEN, 'T': T, **kw}) for m in MIDS}
        print(f"   T {T:.2f} {lab:10s} FV: " + " · ".join(f"mid {m}: {fvt[m]:,.0f}" for m in MIDS))
        for thr in THR:
            print(f"      ≤{thr:6,} (PB {thr/BVPS:.2f}x): " + " ".join(f"mid {m}: {fvt[m]/thr-1:+5.0%}{'✓' if fvt[m] >= 1.15*thr else ' '}" for m in MIDS))
    # P10 lưới trên đường đáy (TDND 0)
    p10 = {}
    for m in MIDS:
        xs = [fv1("TROUGH", m, **{**a, 'T': T}) for _, _, a in GRIDBASE[m]]
        p10[m] = (pct(xs, .1), pct(xs, .5))
    print(f"   T {T:.2f} lưới (TDND 0): P10/trung vị " + " · ".join(f"mid {m}: {p10[m][0]:,.0f}/{p10[m][1]:,.0f}" for m in MIDS))
    print("      ngưỡng có biên ≥15% ở P10 lưới: " + " · ".join(f"mid {m}: {max([t for t in THR if p10[m][0] >= 1.15*t], default='không'):}" for m in MIDS))

print("\n7) §2.5 #3/#4")
gp = {}
for x in csv.DictReader(open(os.path.join(PREV, 'dri_peers_fin.csv'))):
    if '2021' <= x['quarter'][:4] <= '2025' and x['GPM_P0']: gp.setdefault(x['ticker'], []).append(float(x['GPM_P0']))
print("   #3 GPM TB quý 2021–25 [BQ]: " + " · ".join(f"{t} {st.mean(v):.1%} (n={len(v)})" for t, v in sorted(gp.items())))
hard = 72.571 + 271.809 + 40.0 + 183.867 + 2.452 + 4.711 - 280.910
print(f"   #4 sổ sách cứng (tiền+ĐT đáo hạn NH/DH+tồn kho+phải thu−tổng nợ) [BCTC3] = {hard:.1f} tỷ = {hard*1e9/SH:,.0f} đ/cp;"
      f" bỏ TDND 70: {(hard-70)*1e9/SH:,.0f} đ/cp · BVPS {BVPS:,.0f} · phần còn lại (TSCĐ 333,7 + XDCB 72,7 trên đất tô nhượng Lào): {BVPS-hard*1e9/SH:,.0f} đ/cp")

print("\n8) ĐỐI CHIẾU SAU (không chỉnh tham số): skeptic r2 trên đường đáy 1,60 = 9.334/10.424/11.514/12.604")
sk = {**R2, 'Cref': ccal(TAX3), 'ktpl': 0.105}
print("   tái dựng thô (khung trộn r2, C_cal thuế Q3, KTPL 10,5%, sản lượng 2035, T 1,60): " +
      " / ".join(f"{fv1('TROUGH', m, **sk):,.0f}" for m in MIDS))

print("\n9) POST-HOC (ngoài PREREG, không đổi tâm/lưới): đuôi dưới lưới có năm LN lõi ÂM (không có quyền dừng/thanh lý)."
      " Chẩn đoán: sàn LN lõi từng năm ở 0")
print("   tâm có sàn: " + " / ".join(f"{fv(m, floor=True):,.0f}" for m in MIDS) + " (tâm không đổi nếu không có năm âm)")
for m in MIDS:
    xs = [.6*fv1("PEAK", m, **{**a, 'floor': True}) + .4*fv1("MID", m, **{**a, 'floor': True}) for _, _, a in GRIDBASE[m]]
    neg = sum(1 for pk, md, _ in GRIDBASE[m] if .6*pk+.4*md < 0)
    print(f"   mid {m}: lưới 60/40 TDND 0 có sàn: P10 {pct(xs,.1):,.0f} trung vị {pct(xs,.5):,.0f} P90 {pct(xs,.9):,.0f} | ô FV<0 không sàn: {neg}/{len(xs)}")
    xs = [fv1("TROUGH", m, **{**a, 'T': 1.60, 'floor': True}) for _, _, a in GRIDBASE[m]]
    print(f"      đường đáy 1,60 có sàn: P10 {pct(xs,.1):,.0f} trung vị {pct(xs,.5):,.0f}")
for lab, kw in (("g 0", dict(g=0)), ("g 1%", dict(g=.01))):
    print(f"   trung vị lưới 60/40 TDND 0 theo {lab}: " + " · ".join(
        f"mid {m}: {pct([.6*pk+.4*md for pk, md, a in GRIDBASE[m] if a['g'] == kw['g']], .5):,.0f}" for m in MIDS))
