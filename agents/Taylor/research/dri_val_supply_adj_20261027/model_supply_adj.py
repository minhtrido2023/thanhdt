"""Định giá lại DRI có điều chỉnh theo cung cao su (job Taylor_20261027_084046). Lưới khai trước: PREREG.md (commit abefa2578).
Không sửa model.py/model_q3.py. Chạy: python3 model_supply_adj.py   (data/ = snapshot BQ 27/10/2026)."""
import csv, os, statistics as st, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
FEED = '/home/trido/thanhdt/WorkingClaude/data/rubber_monthly.csv'
SH, PX = 73.2e6, 14700                                            # [BCTN] / [BQ Price 26/10]
rows = [(m, float(p)) for m, p in csv.reader(open(FEED)) if m != 'month']
RSS = dict(rows)
med10 = st.median([p for m, p in rows if m >= '2016-10']); med5 = st.median([p for m, p in rows if m >= '2021-10'])
rss25 = st.mean([p for m, p in rows if m.startswith('2025')]); rssq3 = st.mean([RSS[m] for m in ('2026-07', '2026-08', '2026-09')])
# ---------- hằng số model_q3 [BCTC3/SX/SXKD] ----------
SGA3, FIN3, TAX3 = 5.093+12.131, 6.345-3.562, (5.279+0.503)/31.650
V, OTHER_GP = 14000, 10
SGA, FIN = SGA3*4, FIN3*4*0.83
NETC = 72.571+271.809 - 87.039-20.598 - 73.922; DKR = 40*0.5
P25 = 47.24                                                        # giá bán 2025 [BCTN]
def price(rss): return P25*rss/rss25
def lnst(P, C, sga=SGA): return (V*(P-C)/1e3 + OTHER_GP - sga + FIN)*(1-TAX3)
def pre(V_, P, C, sga, fin, oth): return V_*(P-C)/1e3 + oth - sga + fin
Q4 = {"Bear": (3500, 52.0, 36.5, 25), "Base": (4200, 56.0, 35.0, 15), "Bull": (4900, 59.0, 34.0, 0)}
def q4_npat(k, dV=0): V_, P, C, b = Q4[k]; return pre(V_+dV, P, C, SGA3+b, FIN3, 2.0)*(1-TAX3)

# ================= 0. SELFCHECK: tái lập REPORT_Q3_UPDATE §6.2 =================
def old_fv():
    RUN = 167.44 + q4_npat("Base"); out = []
    for rss, c, r_, peak, w in [(med10, 32.0, .14, .5, .25), ((med10+med5)/2, 32.5, .13, 1.0, .5), (med5, 33.0, .12, 2.0, .25)]:
        ni = lnst(price(rss), c, SGA*0.9); core = ni - NETC*0.05*0.8; ann = (1-(1+r_)**-28)/r_
        exc = sum((RUN-ni)*0.9/(1+r_)**(t+0.5) for t in range(int(peak))) + (peak % 1)*(RUN-ni)*0.9/(1+r_)**(int(peak)+0.5)
        out.append(((core*0.9*ann + exc + NETC + DKR)*1e9/SH, w))
    return out, sum(f*w for f, w in out)
S_old, ev_old = old_fv()
print(f"0) SELFCHECK tái lập: Bear {S_old[0][0]:,.0f} Base {S_old[1][0]:,.0f} Bull {S_old[2][0]:,.0f} | kỳ vọng {ev_old:,.0f}")
assert abs(round(S_old[1][0]) - 10878) <= 1 and abs(round(ev_old) - 11031) <= 1, "KHÔNG tái lập được 10.878/11.031 — dừng"
print("   PASS (10.878 / 11.031)")

# ================= 1. model mới =================
T_Q4, T27, T_INV, END = 0.17, 0.67, 0.4, 2054
def path(scn, mid):
    half = mid + 0.5*(rssq3 - mid)
    return {2027: half, 2028: mid} if scn == "PEAK" else {2027: rssq3, 2028: half}
def ceff(P, C, wage): return C + (0.30*(P - P25) if wage == "b" else 0.0)
HIST = None   # POST-HOC (mục 12, KHÔNG thuộc PREREG): (a, b) ⇒ LNST = a + b×RSS3 theo OLS lịch sử
def ni_y(P, C, wage):
    if HIST: return HIST[0] + HIST[1]*P*rss25/P25
    return lnst(P, ceff(P, C, wage), SGA*0.9)
def fv(scn, mid, r, life="L0", C=34.0, wage="a", q4="Base", X=1717, inv_shock=0.0, parts=False):
    pth = path(scn, mid); pv = 0.0
    dV = -(X-1717) if X > 1717 else 0                       # ca 8.000 t: bớt tấn bán Q4 (PREREG §4)
    q4v = 0.9*q4_npat(q4, dV)/(1+r)**T_Q4
    for y in range(2027, END+1):
        P = price(pth.get(y, mid)); ni = ni_y(P, C, wage)
        pv += 0.9*(ni - NETC*0.05*0.8)/(1+r)**(T27 + y-2027)
    Pn = price(mid); fcf_n = 0.9*(ni_y(Pn, C, wage) - NETC*0.05*0.8)
    pi = {"L0": 0, "L1": .5, "L2": 1}[life]; tv = pi*fcf_n/r/(1+r)**(END+1-2026.83)
    P27 = price(pth[2027])*(1+inv_shock); inv = X*(P27 - TAX3*(P27-36.54))/1e3/(1+r)**T_INV
    eq = q4v + pv + tv + inv + NETC + DKR
    v = eq*1e9/SH
    return (v, dict(q4=q4v, ops=pv, tv=tv, inv=inv, cash=NETC+DKR, ni_norm=ni_y(Pn, C, wage))) if parts else v
MIDS = {"PEAK": [1.865, 1.97, 2.075], "MID": [2.18, 2.30]}
def coupled(r, w_peak, **kw):
    a = st.mean([fv("PEAK", m, r, **kw) for m in MIDS["PEAK"]]); b = st.mean([fv("MID", m, r, **kw) for m in MIDS["MID"]])
    return w_peak*a + (1-w_peak)*b, a, b
W = [(.8, "80/20"), (.6, "60/40"), (.4, "40/60")]; R = [.10, .12, .13]; LIFE = ["L0", "L1", "L2"]
print(f"\n1) Đầu vào: RSS3 TB2025 {rss25:.3f} · Q3/26 {rssq3:.3f} · med10 {med10:.3f} · med5 {med5:.3f} [FEED] | net cash {NETC:.1f} tỷ")
for m in [1.865, 1.97, 2.075, 2.18, 2.30, rssq3]:
    P = price(m); print(f"   RSS3 {m:.3f} ⇒ P {P:5.2f} tr/t ⇒ LNST năm (C=34,a) {lnst(P,34,SGA*.9):6.1f} | (C=34,b) {lnst(P,ceff(P,34,'b'),SGA*.9):6.1f} tỷ")
print("   Q4/26 LNST: " + " · ".join(f"{k} {q4_npat(k):.1f}" for k in Q4))

print("\n2) BẢNG CHÍNH — FV kỳ vọng (đ/cp), ghép mid↔kịch bản; C=34, lương (a), Q4 Base, X=1.717 t")
print("   r    life | " + " | ".join(f"{n:>17s}" for _, n in W) + " |  PEAK-only  MID-only")
GRID = {}
for r in R:
    for L in LIFE:
        cells = [coupled(r, w, life=L) for w, _ in W]
        for (w, n), c in zip(W, cells): GRID[(r, L, n)] = c[0]
        print(f"   {r:.0%}  {L} | " + " | ".join(f"{c[0]:7,.0f} ({PX/c[0]-1:+5.0%})" for c in cells) + f" | {cells[0][1]:9,.0f} {cells[0][2]:9,.0f}")
print("   (ngoặc = giá 14.700 cao hơn FV bao nhiêu %)")
vals = list(GRID.values()); print(f"   Toàn bảng: {min(vals):,.0f} – {max(vals):,.0f}; chỉ L0: {min(v for k,v in GRID.items() if k[1]=='L0'):,.0f} – {max(v for k,v in GRID.items() if k[1]=='L0'):,.0f}")

print("\n3) BẢNG PHỤ — ma trận 5 mid × 2 đường giá (r 12%, L0, C 34, a)")
for m in [1.865, 1.97, 2.075, 2.18, 2.30]:
    print(f"   mid {m:.3f}: PEAK {fv('PEAK', m, .12):7,.0f} | MID {fv('MID', m, .12):7,.0f}")
v, p = fv("PEAK", 1.97, .12, parts=True)
print("   phân rã PEAK mid 1,97 (tỷ): " + " ".join(f"{k} {x:.1f}" for k, x in p.items()) + f" ⇒ {v:,.0f} đ")
v, p = fv("MID", 2.18, .12, parts=True)
print("   phân rã MID  mid 2,18 (tỷ): " + " ".join(f"{k} {x:.1f}" for k, x in p.items()) + f" ⇒ {v:,.0f} đ")

print("\n4) ĐỘ NHẠY một-trục-một-lần quanh tâm (60/40, r 12%, L0, C 34, lương a, Q4 Base, X 1.717)")
c0 = coupled(.12, .6)[0]; print(f"   tâm = {c0:,.0f}")
def dec(scn_mid_val, **kw):  # mid cố định cho cả 2 đường giá (tách khỏi ghép)
    return .6*fv("PEAK", scn_mid_val, kw.pop('r', .12), **kw) + .4*fv("MID", scn_mid_val, .12, **kw)
axes = {
  "(a) RSS3 mid [1,865…2,30], 2 đường cùng mid": [dec(m) for m in [1.865, 1.97, 2.075, 2.18, 2.30]],
  "(b) r [10/12/13%]": [coupled(r, .6)[0] for r in R],
  "(c) đời khai thác [L0/L1/L2]": [coupled(.12, .6, life=L)[0] for L in LIFE],
  "giá vốn/t [32/34/36]": [coupled(.12, .6, C=c)[0] for c in (32, 34, 36)],
  "quỹ lương [a/b]": [coupled(.12, .6, wage=w)[0] for w in "ab"],
  "trọng số [80/20…40/60]": [coupled(.12, w)[0] for w, _ in W],
  "Q4/26 [Bear/Base/Bull]": [coupled(.12, .6, q4=k)[0] for k in Q4],
  "tồn kho X [0/1.717/3.370]": [coupled(.12, .6, X=x)[0] for x in (0, 1717, 3370)],
}
for k, xs in sorted(axes.items(), key=lambda kv: -(max(kv[1])-min(kv[1]))):
    print(f"   {k:42s} biên độ {max(xs)-min(xs):6,.0f} đ | " + " / ".join(f"{x:,.0f}" for x in xs))
print("   tổ hợp xấu nhất/tốt nhất toàn lưới (5 mid×2 đường đã ghép, 3 r, 3 life, 3 C, 2 lương, 3 trọng số, Q4 Base, X 1.717):")
allv = [coupled(r, w, life=L, C=c, wage=wg)[0] for r in R for w, _ in W for L in LIFE for c in (32, 34, 36) for wg in "ab"]
print(f"   {min(allv):,.0f} – {max(allv):,.0f} (n={len(allv)}); trung vị {st.median(allv):,.0f}; tỷ lệ ô FV ≥ 14.700: {sum(x>=PX for x in allv)/len(allv):.0%}")

print("\n5) TỒN KHO — giá trị phần vượt mức (tỷ, r 12%)")
for scn, m in [("PEAK", 1.97), ("MID", 2.18)]:
    P27 = price(path(scn, m)[2027])
    for X in (1717, 3370):
        for sh in (0, -.3):
            Ps = P27*(1+sh); val = X*(Ps - TAX3*(Ps-36.54))/1e3
            print(f"   {scn} P2027 {Ps:5.2f} tr/t X {X} sốc {sh:+.0%}: {val:6.1f} tỷ ({val*1e9/SH:5,.0f} đ/cp) | NRV {'CÓ' if Ps<36.54 else 'không'}")
P_nrv = 36.54*rss25/P25; print(f"   NRV chạm khi RSS3 ≈ {P_nrv:.2f} $/kg (−{1-P_nrv/rssq3:.0%} so Q3/26)")
print(f"   ca 3.370 t trừ Q4 base: LNST Q4 {q4_npat('Base', -1653):.1f} (vs {q4_npat('Base'):.1f})")

print("\n6) KIỂM r, TỶ GIÁ, LẠM PHÁT, HIỆU CHỈNH")
for r in R: print(f"   r {r:.0%}: bù trên tiền gửi 6,8% [FEED] = {r-.068:+.1%}; trên 7,4% [DISPATCH] = {r-.074:+.1%}")
fx = {}
for d, x in csv.reader(open('/home/trido/thanhdt/WorkingClaude/data/macro_usdvnd.csv')):
    if d != 'time': fx.setdefault(d[:4], []).append(float(x))
print(f"   USD/VND TB 2016 {st.mean(fx['2016']):,.0f} → 2025 {st.mean(fx['2025']):,.0f} → 2026 {st.mean(fx['2026']):,.0f} [FEED] "
      f"(+{st.mean(fx['2026'])/st.mean(fx['2016'])-1:.0%}); P=47,24×RSS3/2,183 dùng tỷ giá 2025 cho mọi mid ⇒ danh nghĩa, nhất quán chi phí 2025-26")
CPI = {2016: 240.0, 2017: 245.1, 2018: 251.1, 2019: 255.7, 2020: 258.8, 2021: 271.0, 2022: 292.7, 2023: 304.7, 2024: 313.7, 2025: 322.0, 2026: 330.0}  # [NỀN, UL]
real = [p*CPI[2026]/CPI[int(m[:4])] for m, p in rows if m >= '2016-10']
print(f"   trung vị RSS3 10 năm: danh nghĩa {med10:.3f}; USD thực 2026 {st.median(real):.3f} [CPI Mỹ NỀN/UL]")
C_imp = 47.24 - ((157.4/(1-TAX3) - OTHER_GP + SGA - FIN)*1e3/V)
print(f"   giá vốn ngầm định để tái lập LNST 2025 157,4 [BQ] ở giá 47,24 với SGA/FIN/thuế Q3×4: {C_imp:.2f} tr/t (BCTN 33,11)")

print("\n7) KIỂM CHÉO (i) PE/PB theo pha (pha = phân vị RSS3 tháng m−1 trong ≤120 tháng trước, tối thiểu 60)")
months = [m for m, _ in rows]
def phase(m):
    y, mo = int(m[:4]), int(m[5:]); prev = f"{y-(mo==1)}-{12 if mo==1 else mo-1:02d}"
    if prev not in RSS: return None
    i = months.index(prev); win = [RSS[x] for x in months[max(0, i-119):i+1]]
    if len(win) < 60: return None
    pct = sum(x <= RSS[prev] for x in win)/len(win)*100
    return "PEAK" if pct >= 80 else ("MID" if pct >= 40 else "TROUGH")
px = list(csv.DictReader(open(os.path.join(HERE, 'data/dri_peers_px.csv'))))
BVPS = 729.862154663e9/SH
res = {}
for tk in ["DRI", "TRC", "DPR", "PHR"]:
    for ph in ["PEAK", "MID", "TROUGH"]:
        sel = [x for x in px if x['ticker'] == tk and phase(x['m']) == ph]
        pbs = [float(x['pb']) for x in sel if x['pb']]; pes = [float(x['pe']) for x in sel if x['pe'] and 0 < float(x['pe']) <= 50]
        res[(tk, ph)] = (len(sel), st.median(pbs) if pbs else None, st.median(pes) if pes else None)
    print(f"   {tk}: " + " | ".join(f"{ph} n={res[(tk,ph)][0]:3d} PB {res[(tk,ph)][1] or 0:4.2f} PE {res[(tk,ph)][2] or 0:5.1f}" for ph in ["PEAK", "MID", "TROUGH"]))
print(f"   BVPS DRI 30/09 = {BVPS:,.0f} đ [BCTC3]; PB hiện tại = {PX/BVPS:.2f}x; pha tháng 10/2026 = {phase('2026-10')}")
for tk in ["DRI", "TRC"]:
    for ph in ["PEAK", "MID"]:
        n, pb, pe = res[(tk, ph)]
        if pb: print(f"   giá ngầm định theo PB {tk}-{ph} {pb:.2f}x: {pb*BVPS:,.0f} đ")
for ph in ["PEAK", "MID"]:
    pe = res[("DRI", ph)][2]
    for scn, m in [("PEAK", 1.97), ("MID", 2.18)]:
        ni = lnst(price(m), 34, SGA*.9); print(f"   PE DRI-{ph} {pe:.1f}x × LNST chuẩn {scn} mid {m} ({ni:.1f} tỷ) + net cash: {(pe*ni+NETC+DKR)*1e9/SH:,.0f} đ")

print("\n8) KIỂM CHÉO (ii) cổ tức")
fin = list(csv.DictReader(open(os.path.join(HERE, 'data/dri_peers_fin.csv'))))
npy, div = {}, {}
for x in fin:
    if x['ticker'] != 'DRI': continue
    y = x['quarter'][:4]; npy[y] = npy.get(y, 0) + float(x['NP_P0'])/1e9
    if x['quarter'].endswith('Q4'): div[y] = float(x['Dividend_1Y'] or 0)
pay = {y: div[y]/(npy[y]*1e9/SH) for y in div if '2018' <= y <= '2025' and npy[y] > 0}
po = st.median(pay.values())
print("   chi trả/EPS năm: " + " ".join(f"{y}:{v:.0%}" for y, v in sorted(pay.items())) + f" ⇒ trung vị {po:.0%} [BQ Dividend_1Y Q4 / ΣNP_P0]")
for scn, m in [("PEAK", 1.865), ("PEAK", 1.97), ("PEAK", 2.075), ("MID", 2.18), ("MID", 2.30)]:
    ni = lnst(price(m), 34, SGA*.9); eps = ni*1e9/SH; D = min(1000, po*eps)
    print(f"   mid {m}: LNST {ni:5.1f} EPS {eps:5,.0f} ⇒ D bền {D:4,.0f} đ (cổ tức 1.000 = {73.2/ni:.0%} LNST) | D/r: " +
          " ".join(f"{r:.0%}:{D/r:6,.0f}" for r in R) + f" | D×niên kim28@12%: {D*(1-1.12**-28)/.12:6,.0f}")
print(f"   lợi suất ở 14.700 với 1.000 đ: {1000/PX:.1%}; LNST riêng mẹ Q2 55,70 / Q3 0,15 tỷ [GT/BCTC3]")

print("\n9) VÙNG MUA 21/10 [DISPATCH]: tỷ lệ ô bảng chính có FV ≥ ngưỡng")
for thr in (13000, 11500):
    for L in LIFE:
        ok = [n for (r, L2, n), v in GRID.items() if L2 == L and v >= thr]
        print(f"   ≤{thr:,} {L}: {len(ok)}/9 ô FV ≥ ngưỡng ({', '.join(sorted(set(f'{r:.0%}/{n}' for (r,L2,n),v in GRID.items() if L2==L and v>=thr))) or '—'})")
    print(f"   ≤{thr:,} toàn lưới mở rộng (n={len(allv)}): {sum(x>=thr for x in allv)/len(allv):.0%} ô FV ≥ ngưỡng")

print("\n10) CẦU NỐI từ Base cũ 10.878 (chỉ đổi từng bước, cộng dồn)")
steps = [("đường giá PEAK thay 'đỉnh 1 năm', mid 1,97, r13, C32,5, X0", dict(scn="PEAK", mid=1.97, r=.13, C=32.5, X=0)),
         ("+ tồn kho X 1.717", dict(X=1717)), ("+ C 34", dict(C=34.0)), ("+ r 12%", dict(r=.12))]
cur = {}; last = S_old[1][0]
for name, ch in steps:
    cur.update(ch); v = fv(cur["scn"], cur["mid"], cur["r"], C=cur["C"], X=cur["X"])
    print(f"   {name:58s} {v-last:+7,.0f} → {v:7,.0f}"); last = v
pk = coupled(.12, 1.0)[0]; print(f"   {'+ PEAK trung bình mid {1,865;1,97;2,075}':58s} {pk-last:+7,.0f} → {pk:7,.0f}")
c6 = coupled(.12, .6)[0]; print(f"   {'+ 40% MID-tiếp diễn (mid {2,18;2,30})':58s} {c6-pk:+7,.0f} → {c6:7,.0f}")

print("\n11) BACKCAST hàm LNST (C 34, lương a, SGA/FIN/thuế Q3/26×4) vs LNST thật [BQ ΣNP_P0]")
for y in ['2021', '2022', '2023', '2024', '2025']:
    rs = st.mean([p for m, p in rows if m.startswith(y)])
    print(f"   {y}: RSS3 {rs:.3f} ⇒ model {lnst(price(rs), 34, SGA*.9):6.1f} | (C 32) {lnst(price(rs), 32, SGA*.9):6.1f} | thật {npy[y]:6.1f}")

print("\n12) POST-HOC (ngoài PREREG, chỉ để đo rủi ro mô hình): thay hàm LNST bằng OLS LNST thật ~ RSS3 năm [BQ, FEED]")
for y0 in ('2017', '2021'):
    ys = [y for y in sorted(npy) if y0 <= y <= '2025']; xs = [st.mean([p for m, p in rows if m.startswith(y)]) for y in ys]; zs = [npy[y] for y in ys]
    mx, mz = st.mean(xs), st.mean(zs); b = sum((x-mx)*(z-mz) for x, z in zip(xs, zs))/sum((x-mx)**2 for x in xs); a = mz - b*mx
    HIST = (a, b)
    print(f"   {y0}–2025 (n={len(ys)}): LNST = {a:6.1f} + {b:5.1f}×RSS3 (model PREREG dốc {14000*P25/rss25/1e3*(1-TAX3):.0f}) | LNST@1,97 {a+b*1.97:5.1f} @2,18 {a+b*2.18:5.1f}"
          f" | FV tâm 60/40 r12 L0: {coupled(.12, .6)[0]:,.0f} | 80/20 r13: {coupled(.13, .8)[0]:,.0f} | 40/60 r10: {coupled(.10, .4)[0]:,.0f}")
HIST = None
