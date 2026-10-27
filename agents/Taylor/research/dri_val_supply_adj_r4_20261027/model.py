"""Định giá DRI vòng 4 (job Taylor_20261027_123420). Lưới khai trước: PREREG.md (commit fe9e49391).
Thay đường sản lượng r3 bằng đường dựng từ diện tích/năng suất công bố + lịch thanh lý/tái canh; giữ nguyên mọi trục khác tâm r3.
Hàm r1–r3 lấy NGUYÊN VĂN từ ../dri_val_supply_adj_r3_20261027/model.py (exec phần đầu, không sửa file cũ). Chạy: python3 model.py"""
import os, csv, statistics as st, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
R3 = os.path.join(HERE, '..', 'dri_val_supply_adj_r3_20261027', 'model.py')
_src = open(R3, encoding='utf-8').read().split("# ================= 2. kiểm số đầu vào")[0]
exec(compile(_src, R3, 'exec'))          # in 0a/0b/0c selfcheck của r3 và assert 10.878/11.031/14.301/hàng r2

# ---- C_cal, k: chép đúng công thức r3 mục 2 ----
npy = {}
for x in csv.DictReader(open(os.path.join(PREV, 'dri_peers_fin.csv'))):
    if x['ticker'] == 'DRI': npy[x['quarter'][:4]] = npy.get(x['quarter'][:4], 0) + float(x['NP_P0'])/1e9
VY = {'2021': 14000, '2022': 14000, '2023': 10108.24/(1-.3003), '2024': 10108.24, '2025': 14007.76}
def Py(y): return P25*ymean(y)/rss25*FX[y]/FX['2025']
def ccal(tax, f=.5):
    V = VY['2025']; C = 47.24 - ((157.4/(1-tax) - OTHER_GP + SGA*0.9 - FIN)*1e3/V)
    return C/((1-f) + f*V0/V)
CCAL = ccal(TAX9)
rmse = {k: st.mean([(ni(Py(y), VY[y], CCAL, k, .5, TAX9) - npy[y])**2 for y in ('2021', '2022', '2023', '2024')])**.5 for k in (0, .3, .6)}
K = min(rmse, key=rmse.get)
CEN = {**R2, 'Cref': CCAL, 'k': K, 'd0': 2030, 'tax': TAX9, 'ktpl': KTPL, 'trap': "2054", 'frame': "real", 'leak_all': True}
MIDS = [1.865, 1.97, 2.075, 2.18]
R3ROW = [10521, 11863, 13206, 14548]

# ================= dữ liệu công bố r4 =================
KH26_V, KH26_Y = 13800, 1.69                                       # [BCTN25 tr.46]
A0 = KH26_V/KH26_Y                                                 # diện tích cạo 2026 [SL]
R_TOTAL, R_DONE = 4081.64, {2025: 94.56, 2026: 37.77}              # [BCTN25 tr.57; BCTN24 tr.55; BCTN25 tr.46]
R_LEFT = R_TOTAL - sum(R_DONE.values())                            # [UL] 132,33 ha 2025–26 thuộc dự án
CARE = 9542.65/387.04                                              # tr/ha/năm KTCB cao su KH2025 [BCTN24 tr.57]
QDTPT = 96.968992285                                               # quỹ ĐTPT 30/09/26, tỷ [BCTC3 418]
COH = [(t, .8/5) for t in range(2011, 2016)] + [(t, .2/3) for t in range(2016, 2019)]   # năm bắt đầu cạo [SL §2]
YNG = [0.9, 1.2, 1.5]                                              # năng suất mở cạo năm 1–3 [UL/NỀN], sau đó KH26_Y
WIN = 8; KTCB = 7
PATHS = {"NHANH": 2027, "TRUNG BÌNH": 2029, "CHẬM": 2031}
LTAPS, MS = [22, 27, 32], [4, 7, 10]

def yold(y, d=.02, d0=2030): return KH26_Y if y < d0 else KH26_Y*(1-d)**(y-d0+1)
def alive(y, Ltap): return sum(fr for ts, fr in COH if y < ts+Ltap)
def plantings(s, R_on=True):
    p = dict(R_DONE)
    if R_on:
        for L in range(s, s+WIN): p[L] = p.get(L, 0) + R_LEFT/WIN
    return p
def build(s, Ltap, R_on=True, new_on=True):
    """trả {năm: (V tấn, diện tích cạo ha)} 2026..2054"""
    out = {}
    for y in range(2026, END+1):
        oldR = R_LEFT - (sum(R_LEFT/WIN for L in range(s, s+WIN) if L <= y) if R_on else 0)
        a_old = (oldR + A0 - R_LEFT)*(alive(y, Ltap) if y > 2026 else 1.0)
        v = a_old*yold(y); a = a_old
        if new_on:
            for L, ha in plantings(s, R_on).items():
                i = y - (L+KTCB)
                if i >= 0: v += ha*(YNG[i] if i < 3 else KH26_Y); a += ha
        out[y] = (v, a)
    return out
def capex(s, m, R_on=True):
    """tỷ đồng thực 2025 theo năm ≥2027"""
    cx = {}
    for L, ha in plantings(s, R_on).items():
        for y in range(L, L+KTCB):
            if 2027 <= y <= END: cx[y] = cx.get(y, 0) + ha*m*CARE/KTCB/1e3
    return cx

# ================= fv4: bản sao fv1 r3 + đường V tuỳ ý + capex + biến thể =================
def fv4(scn, mid, a, V=None, cx=None, reinv=0.9, farea=False, qcash=0.0, qcx=0.0, addD=0.0, wood=None):
    r, Cref, k, f, tax, ktpl, wht, h = a['r'], a['Cref'], a['k'], a['f'], a['tax'], a['ktpl'], a['wht'], a['h']
    rr = r if a['frame'] == "mix" else (1+r)/(1+PI) - 1
    pth = path(scn, mid, a['T']); tau = TAU if a['trap'] in ("2054", "lost") else 0.0
    lk = (1-wht-ktpl-tau)*((1-h) if a['h_all'] else 1); lk_q4 = (1-wht-ktpl-tau) if a['leak_all'] else 1.0
    X = a['X']; dV = -(X-1717) if X > 1717 else 0
    q4v = lk_q4*0.9*q4_npat(a['q4'], dV)/(1+rr)**T_Q4
    pv = trapped = pcx = 0.0; left = qcx
    for y in range(2027, END+1):
        P = price(pth.get(y, mid)); cm = (1+a['g'])**(y-2026)
        if V is None: Vy = vol(y, a['d'], a['d0'])
        else:
            Vy, Ay = V[y]
        if V is None: core = ni(P, Vy, Cref, k, f, tax, cm) - NETC*0.05*0.8
        else:   # ≡ ni() r3 viết dạng V×cost = C×((1−f)V + f·V0·[A/A0]) để không chia 0 khi V → 0
            C = Cref + k*(P-P25); fixed = f*V0*(Ay/A0 if farea else 1.0)
            core = ((Vy*P - cm*C*((1-f)*Vy + fixed))/1e3 + OTHER_GP - SGA*0.9 + FIN)*(1-tax) - NETC*0.05*0.8
            core += addD*(Ay/A0 if farea else 1.0)          # POST-HOC: cộng lại khấu hao vườn (phi tiền mặt) khi capex đã tường minh
        disc = (1+rr)**(T27+y-2027)
        pv += lk*reinv*core/disc; trapped += tau*reinv*core
        if cx and y in cx:
            c = cx[y]; use = min(left, c); left -= use
            pcx += (c-use)*(1-wht)/disc
        if wood and y in wood: pcx -= wood[y]*(1-wht)/disc
    trapv = trapped/(1+rr)**(T27+END+1-2027) if a['trap'] == "2054" else 0.0
    P27 = price(pth[2027]); gain = (P27-36.54)*(1-tax)
    inv = X*(P27 - tax*(P27-36.54) - ((wht+ktpl+tau)*gain if a['leak_all'] else 0))/1e3/(1+rr)**T_INV
    cash = NETC + DKR - h*LAO_CASH - a['tdnd']*TDND - qcash
    return (q4v + pv + trapv + inv + cash - pcx)*1e9/SH
def fvw4(mid, a=CEN, wp=.6, **kw): return wp*fv4("PEAK", mid, a, **kw) + (1-wp)*fv4("MID", mid, a, **kw)

# ================= 0d. SELFCHECK r3 tâm =================
r3row = [fvw4(m) for m in MIDS]
print("0d) SELFCHECK r3 tâm 60/40 (fv4 với hàm sản lượng r3): " + " / ".join(f"{v:,.0f}" for v in r3row))
assert [round(v) for v in r3row] == R3ROW, "KHÔNG tái lập r3 tâm"
assert all(abs(fvw4(m) - (.6*fv1("PEAK", m, **CEN) + .4*fv1("MID", m, **CEN))) < 1e-6 for m in MIDS)
FLAT = {y: (V0, A0) for y in range(2026, END+1)}
print("   mốc đường PHẲNG 14.000 t tới 2054 (không lão hoá): " + " / ".join(f"{fvw4(m, V=FLAT):,.0f}" for m in MIDS))
print("   PASS (r1–r3 tái lập; fv4 ≡ fv1 r3)")

print(f"\n1) ĐỐI CHIẾU DIỆN TÍCH (ha) — chỉ in, không chỉnh tham số")
for lab, v in [("KH26 13.800/1,69 [BCTN25 tr.46]", A0), ("2025 15.152,83/1,81 [BCTN25 tr.40]", 15152.83/1.81),
               ("2024 11.116/1,34 [BCTN24]", 11116/1.34), ("FSC 6.148,03/0,7407 [BCTN25 tr.6]", 6148.03/.7407),
               ("kinh doanh EUDR [BCTN24 tr.32]", 8299.83), ("khai thác KH25 [BCTN24 tr.56]", 8201.66), ("tổng cao su [BCTN25 tr.20]", 8592.3)]:
    print(f"   {lab:38s} {v:9,.1f}")
print(f"   ⇒ không cạo trong tổng 8.592,3: {8592.3-A0:,.1f} ha (KTCB 2025–26 132,33 + phần khác)")
print(f"   tái canh còn lại R = 4.081,64 − 94,56 − 37,77 = {R_LEFT:,.2f} ha = {R_LEFT/A0:.1%} diện tích cạo; khối không tái canh {A0-R_LEFT:,.1f} ha")
gtcl, ng, hm, kh9 = 250.744137728, 567.430420960, 316.686283232, 26.201458930
print(f"   vườn cây [BCTC3 5.8]: HMLK/NG {hm/ng:.1%}; KH năm hoá {kh9/.75:.1f} tỷ = {kh9/.75/ng:.1%} NG/năm ⇒ GTCL {gtcl:.1f} hết sau ~{gtcl/(kh9/.75):.1f} năm (~{2026.75+gtcl/(kh9/.75):.0f}) ở tốc độ hiện tại [SL]")
print(f"   capex KTCB [BCTN24 tr.57] {CARE:.3f} tr/ha/năm ⇒ m 4/7/10: " + " / ".join(f"{m*CARE:.1f}" for m in MS) + " tr/ha")

print("\n2) ĐƯỜNG SẢN LƯỢNG tự khai thác (tấn; L_tap 27) — so r3 tâm")
YS = [2026, 2027, 2028, 2030, 2032, 2034, 2036, 2038, 2040, 2042, 2045, 2048, 2051, 2054]
print("   năm        " + "".join(f"{y:>7}" for y in YS) + "  Σ2027–54")
r3v = {y: (V0 if y < 2030 else V0*.98**(y-2029)) for y in range(2026, END+1)}
print("   r3 tâm     " + "".join(f"{r3v[y]:7,.0f}" for y in YS) + f"  {sum(r3v[y] for y in range(2027, END+1)):9,.0f}")
PV = {}
for lab, s in PATHS.items():
    PV[lab] = build(s, 27)
    print(f"   {lab:10s} " + "".join(f"{PV[lab][y][0]:7,.0f}" for y in YS) + f"  {sum(PV[lab][y][0] for y in range(2027, END+1)):9,.0f}")
for L in (22, 32):
    b = build(PATHS["TRUNG BÌNH"], L)
    print(f"   TB L_tap{L} " + "".join(f"{b[y][0]:7,.0f}" for y in YS) + f"  {sum(b[y][0] for y in range(2027, END+1)):9,.0f}")
for lab, s in PATHS.items():
    cx = capex(s, 7); print(f"   capex m7 {lab:10s}: tổng {sum(cx.values()):6.1f} tỷ; đỉnh {max(cx.values()):5.1f} tỷ/năm ({max(cx, key=cx.get)})")
c27 = ni(price(1.97), PV["TRUNG BÌNH"][2030][0], CCAL, K, .5, TAX9) - NETC*0.05*0.8
print(f"   so sánh: 10% 'tái đầu tư' r3 ở LN lõi 2030 (mid 1,97, đường TB) = {0.1*c27:.1f} tỷ/năm")

def tab(lab, fn):
    vals = [fn(m) for m in MIDS]
    print(f"   {lab:40s} | " + " | ".join((f"{v:7,.0f} ({PX/v-1:+4.0%}/{PX27/v-1:+4.0%})" if v > 1000 else f"{v:7,.0f} (FV<1.000)     ") for v in vals)); return vals
print("\n3) FV r4 (đ/cp, 60/40; ngoặc = 14.700/14.400 so FV). Tâm: L_tap 27, capex m 7, các trục khác = tâm r3")
print("   " + " "*40 + " | " + " | ".join(f"mid {m:.3f}            " for m in MIDS))
tab("r3 tâm (đối chiếu)", lambda m: fvw4(m))
CENTER = {}
for lab, s in PATHS.items():
    CENTER[lab] = tab(f"r4 {lab} (s {s})", lambda m, s=s: fvw4(m, V=build(s, 27), cx=capex(s, 7)))

print("\n4) LƯỚI 3 đường × L_tap {22,27,32} × capex m {4,7,10} (27 ô/mid; phân vị lưới KHÔNG phải xác suất)")
G = {}
for m in MIDS:
    xs = []
    for (lab, s), L, mm in itertools.product(PATHS.items(), LTAPS, MS):
        xs.append(fvw4(m, V=build(s, L), cx=capex(s, mm)))
    G[m] = xs
    print(f"   mid {m:.3f}: min {min(xs):7,.0f} trung vị {st.median(xs):7,.0f} max {max(xs):7,.0f} | ô ≥ 14.700: {sum(v >= PX for v in xs)}/27 · ≥ 14.400: {sum(v >= PX27 for v in xs)}/27")
print("   một trục quanh tâm (TB, L27, m7) — biên độ @ mỗi mid:")
for lab, fn in [("đường s 2027/2029/2031", lambda m: [fvw4(m, V=build(s, 27), cx=capex(s, 7)) for s in PATHS.values()]),
                ("L_tap 22/27/32", lambda m: [fvw4(m, V=build(2029, L), cx=capex(2029, 7)) for L in LTAPS]),
                ("capex m 4/7/10", lambda m: [fvw4(m, V=build(2029, 27), cx=capex(2029, mm)) for mm in MS])]:
    res = {m: fn(m) for m in MIDS}
    print(f"     {lab:24s} " + " | ".join(f"{m}: {max(v)-min(v):5,.0f} [{'/'.join(f'{x:,.0f}' for x in v)}]" for m, v in res.items()))

print("\n5) CẦU NỐI r3 tâm → r4 tâm (đường TRUNG BÌNH; cộng dồn, mỗi mid riêng, 60/40)")
s = PATHS["TRUNG BÌNH"]
LVL = {y: (KH26_V if y < 2030 else KH26_V*.98**(y-2029), A0) for y in range(2026, END+1)}
steps = [("mức 14.000→13.800 (dạng r3)", dict(V=LVL)),
         ("hết chu kỳ 1 theo cohort L27, chưa tái canh", dict(V=build(s, 27, R_on=False, new_on=False))),
         ("thanh lý khối tái canh 2029–36", dict(V=build(s, 27, R_on=True, new_on=False))),
         ("sản lượng cây tái canh", dict(V=build(s, 27))),
         ("capex tái canh m7", dict(V=build(s, 27), cx=capex(s, 7)))]
for m in MIDS:
    last = fvw4(m); out = f"   mid {m}: r3 {last:,.0f}"
    for lab, kw in steps:
        v = fvw4(m, **kw); out += f" | {lab} {v-last:+,.0f}"; last = v
    print(out + f" ⇒ r4 {last:,.0f}")

print("\n6) BIẾN THỂ quanh tâm TB (không vào tâm)")
VT, CT = build(s, 27), capex(s, 7)
tab("tâm TB", lambda m: fvw4(m, V=VT, cx=CT))
tab("quỹ ĐTPT tự tài trợ (−96,97 tiền, −96,97 capex)", lambda m: fvw4(m, V=VT, cx=CT, qcash=QDTPT, qcx=QDTPT))
tab("quỹ ĐTPT trừ thẳng [ĐẾM HAI LẦN]", lambda m: fvw4(m, V=VT, cx=CT, qcash=QDTPT))
tab("capex THAY 10% tái đầu tư (0,9→1,0)", lambda m: fvw4(m, V=VT, cx=CT, reinv=1.0))
tab("chi phí cố định co theo diện tích", lambda m: fvw4(m, V=VT, cx=CT, farea=True))

print("\n7) DÒNG RIÊNG — KHÔNG cộng vào FV")
def pv_stream(cf, a=CEN, scn="PEAK", mid=1.97):
    rr = (1+a['r'])/(1+PI) - 1; tau = TAU; lk = 1-a['wht']-a['ktpl']-tau
    return sum(lk*0.9*v*(1-a['tax'])/(1+rr)**(T27+y-2027) for y, v in cf.items())*1e9/SH
for mb in (0, 1.5, 3.0):
    print(f"   mua ngoài 2.000 t/năm 2027–54, biên {mb} tr/t [UL]: +{pv_stream({y: 2000*mb/1e3 for y in range(2027, END+1)}):,.0f} đ/cp")
# sầu riêng: 30,48 (2025) + 60,66 (2026) + 146,98 rải đều 2027–30 [UL]; năng suất CNC 2026 KH 760/142,17 [SL]; biên KH26 CNC [BCTN25 tr.46]
DUR = {2025: 30.48, 2026: 60.66, **{y: (238.12-30.48-60.66)/4 for y in range(2027, 2031)}}
YD, MD, CXD = 760/142.17, (40000-31419)/1e3, 178.520867   # t/ha; tr/t; tr/ha năm trồng [BCTN24 tr.57]
cf = {}
for L, ha in DUR.items():
    for y in range(max(L+5, 2027), END+1):
        cf[y] = cf.get(y, 0) + ha*YD*min(1.0, .3*(y-L-4) if y-L < 7 else 1.0)*MD/1e3
cxd = {L: ha*CXD/1e3 for L, ha in DUR.items() if L >= 2027}
rr = (1+CEN['r'])/(1+PI) - 1
pcxd = sum(v*(1-CEN['wht'])/(1+rr)**(T27+y-2027) for y, v in cxd.items())*1e9/SH
print(f"   sầu riêng Lào 238,12 ha [UL: NS {YD:.2f} t/ha từ CNC, biên {MD:.3f} tr/t, ra quả năm 5–7]: LN gộp đỉnh {max(cf.values()):.1f} tỷ/năm;"
      f" PV +{pv_stream(cf):,.0f} đ/cp; trừ capex trồng 2027–30 (178,5 tr/ha, CHƯA gồm chăm sóc KTCB) −{pcxd:,.0f} ⇒ ròng {pv_stream(cf)-pcxd:+,.0f} đ/cp")

print("\n8) NGƯỠNG GIÁ biên an toàn ≥15% = FV/1,15 (tâm từng đường; và min lưới 27 ô)")
for lab in PATHS:
    print(f"   {lab:10s}: " + " · ".join(f"mid {m}: ≤{v/1.15:,.0f}" for m, v in zip(MIDS, CENTER[lab])))
print("   min lưới : " + " · ".join(f"mid {m}: ≤{min(G[m])/1.15:,.0f}" for m in MIDS))
print("   ĐƯỜNG ĐÁY r3 (RSS3 2027=2028=1,60) trên đường TB tâm: " + " · ".join(
    f"mid {m}: FV {fv4('TROUGH', m, CEN, V=VT, cx=CT):,.0f} ⇒ ≤{fv4('TROUGH', m, CEN, V=VT, cx=CT)/1.15:,.0f}" for m in MIDS))

print("\n9) POST-HOC (ngoài PREREG; KHÔNG đổi tâm): chi phí cố định CO THEO DIỆN TÍCH cho cả 3 đường + lưới + ngưỡng")
print("   Lý do: hàm r3 giữ f·C_ref·14.000 t ≈ " + f"{.5*CCAL*V0/1e3:.0f}" + " tỷ/năm cố định cả khi diện tích rời sổ; SGA đã tách riêng ⇒ phần cố định trong GVHB chủ yếu là chi phí/ha")
CF = {}
for lab, s_ in PATHS.items():
    CF[lab] = tab(f"farea {lab}", lambda m, s_=s_: fvw4(m, V=build(s_, 27), cx=capex(s_, 7), farea=True))
for m in MIDS:
    xs = [fvw4(m, V=build(s_, L), cx=capex(s_, mm), farea=True) for s_, L, mm in itertools.product(PATHS.values(), LTAPS, MS)]
    print(f"   lưới farea mid {m:.3f}: min {min(xs):7,.0f} trung vị {st.median(xs):7,.0f} max {max(xs):7,.0f} | ô ≥ 14.400: {sum(v >= PX27 for v in xs)}/27 | ngưỡng FV/1,15 min lưới ≤{min(xs)/1.15:,.0f}")
for lab in PATHS:
    print(f"   ngưỡng farea {lab:10s}: " + " · ".join(f"mid {m}: ≤{v/1.15:,.0f}" for m, v in zip(MIDS, CF[lab])))
print("   farea + capex THAY 10% (cận trên hợp lý): " + " / ".join(f"{fvw4(m, V=VT, cx=CT, farea=True, reinv=1.0):,.0f}" for m in MIDS))
print("   farea đường đáy 1,60 (TB): " + " / ".join(f"{fv4('TROUGH', m, CEN, V=VT, cx=CT, farea=True):,.0f}" for m in MIDS))

print("\n10) POST-HOC (ngoài PREREG; KHÔNG đổi tâm): hai sai lệch do CHÍNH r4 tạo ra khi thêm capex tường minh")
D_V = 26.201458930/.75                                             # KH vườn năm hoá [BCTC3 5.8]
ng_ha = 567.430420960/8592.3; ha_liq = 3.582756986/ng_ha; wood_ha = 1.132185334/ha_liq*1e3   # tr/ha; [BCTC3 5.8, hn_04; SL]
print(f"   (a) khấu hao vườn {D_V:.1f} tỷ/năm nằm trong C_ref như chi phí tiền mặt; capex tái canh nay trừ riêng ⇒ cộng lại (cận trên: giả định KH chu kỳ 2 thay thế lá chắn thuế)")
print(f"   (b) tiền thu gỗ thanh lý 9T/26: {1.132185334:.3f} tỷ / ~{ha_liq:.0f} ha [SL: NG thanh lý 3,58 tỷ ÷ NG BQ {ng_ha*1e3:.1f} tr/ha] ≈ {wood_ha:.1f} tr/ha ước lượng; áp cho mọi ha thanh lý")
def woodf(s_, L):
    w = {}; b = build(s_, L, new_on=False)
    for y in range(2027, END+1):
        da = b[y-1][1] - b[y][1] if y > 2027 else (A0 - b[y][1])
        if da > 0: w[y] = da*wood_ha/1e3
    return w
for lab_, kw_ in [("(a) cộng KH, chi phí công ty", dict(addD=D_V)), ("(a) cộng KH + farea", dict(addD=D_V, farea=True)),
                  ("(a)+(b) + farea", dict(addD=D_V, farea=True, wood=woodf(2029, 27)))]:
    tab(lab_ + " — TB", lambda m: fvw4(m, V=VT, cx=CT, **kw_))
print("   ba đường với (a)+(b)+farea:")
PH = {}
for lab, s_ in PATHS.items():
    PH[lab] = tab(f"PH {lab}", lambda m, s_=s_: fvw4(m, V=build(s_, 27), cx=capex(s_, 7), farea=True, addD=D_V, wood=woodf(s_, 27)))
for m in MIDS:
    xs = [fvw4(m, V=build(s_, L), cx=capex(s_, mm), farea=True, addD=D_V, wood=woodf(s_, L)) for s_, L, mm in itertools.product(PATHS.values(), LTAPS, MS)]
    print(f"   lưới PH mid {m:.3f}: min {min(xs):7,.0f} trung vị {st.median(xs):7,.0f} max {max(xs):7,.0f} | ô ≥ 14.400: {sum(v >= PX27 for v in xs)}/27 | min/1,15 ≤{min(xs)/1.15:,.0f}")
for lab in PATHS:
    print(f"   ngưỡng PH {lab:10s}: " + " · ".join(f"mid {m}: ≤{v/1.15:,.0f}" for m, v in zip(MIDS, PH[lab])))
print("   PH đường đáy 1,60 (TB): " + " / ".join(f"{fv4('TROUGH', m, CEN, V=VT, cx=CT, farea=True, addD=D_V, wood=woodf(2029, 27)):,.0f}" for m in MIDS))
print("   PH không capex (chỉ để thấy cỡ capex): " + " / ".join(f"{fvw4(m, V=VT, farea=True, addD=D_V, wood=woodf(2029, 27)):,.0f}" for m in MIDS))
