"""TV1 DD 02/11/2026 — mọi phép tính của REPORT.md. Tái lập: python3 -I calc/valuation.py > calc/valuation_out.txt
Nhãn: [Q3 tr.X] = trang PDF src/hn_q3_2026.pdf; [H1 tr.X] = trang in của hn_h1_2026.pdf; [UL] = giả định/ước lượng.
Đơn vị: tỷ đồng (trừ khi ghi khác)."""
SH = 26_691_319            # cp lưu hành [Q3 tr.5: vốn góp 266.913.190.000 / 10.000]
PX = 19_800                # đóng cửa 30/10/2026 [DNSE ohlc, calc/dnse_px_out.txt]
mcap = SH * PX / 1e9
def ps(x): return x * 1e9 / SH          # tỷ -> đ/cp
print(f"Vốn hoá @{PX}: {mcap:.1f} tỷ")

# ---------- 1. KQKD Q3 & 9T [Q3 tr.6] ----------
q3 = dict(dt=168.095, gv=102.652, gp=65.443, dttc=2.533, cptc=1.466, ql=21.486, tnk=33.802, cpk=1.870, lntt=76.956, thue=10.080, lnst=66.877)
q325 = dict(dt=149.309, gv=97.941, gp=51.368, dttc=0.268, cptc=2.652, ql=10.585, tnk=0.099, cpk=4.463, lntt=34.035, thue=7.278, lnst=26.757)
n9 = dict(dt=446.884, gp=162.555, dttc=7.109, cptc=8.458, ql=42.413, tnk=33.802, cpk=2.145, lntt=150.451, thue=25.815, lnst=124.636)
n925 = dict(dt=390.587, gp=146.152, dttc=1.160, cptc=8.688, ql=27.545, tnk=0.220, cpk=4.785, lntt=106.514, thue=20.162, lnst=86.352)
for k, d in [("Q3/26", q3), ("Q3/25", q325), ("9T/26", n9), ("9T/25", n925)]:
    ebit = d['gp'] - d['ql']; fin = d['dttc'] - d['cptc']; oth = d['tnk'] - d['cpk']
    core_lnst = (ebit + fin) * 0.8   # [UL] thuế 20% trên phần lõi
    print(f"{k}: DT {d['dt']:.1f} | biên gộp {d['gp']/d['dt']*100:.2f}% | EBIT lõi {ebit:.1f} | TC ròng {fin:+.1f} | khác ròng {oth:+.1f} | "
          f"LNTT {d['lntt']:.1f} | thuế hiệu dụng {d['thue']/d['lntt']*100:.1f}% | LNST {d['lnst']:.1f} | LNST lõi[UL,20%] {core_lnst:.1f}")
print(f"LNST Q3 YoY {q3['lnst']/q325['lnst']-1:+.1%} | 9T YoY {n9['lnst']/n925['lnst']-1:+.1%} | DT Q3 YoY {q3['dt']/q325['dt']-1:+.1%}")
print(f"QLDN Q3 YoY {q3['ql']/q325['ql']-1:+.1%}; 9T {n9['ql']/n925['ql']-1:+.1%}")
# đối chiếu H1 soát xét: 9T - H1 = Q3
h1_lnst = 57.759  # [explanation_yoy_en / giaitrinh_soatxet: H1 sau soát xét]
print(f"Kiểm: 9T LNST {n9['lnst']:.3f} - H1 soát xét {h1_lnst} = {n9['lnst']-h1_lnst:.3f} (Q3 báo cáo {q3['lnst']})")

# ---------- 1b. LNST lõi Q3 DẠNG KHOẢNG HAI CHIỀU (r2: phản biện #5) ----------
# Hoàn nhập dự phòng Q3 dựng trên H1 SOÁT XÉT [H1 tr.5: mã136 105,081; mã142 59,293] vs Q3 [Q3 tr.1: 85,908; 53,571]
H1R = dict(m136=105.081, m142=59.293, lctt03=-1.149, cfo=47.026, vcsh=507.847)
Q3B = dict(m136=85.908, m142=53.571, lctt03_9t=-22.612)
rev_ar  = H1R['m136'] - Q3B['m136']        # giảm dự phòng phải thu (mã 136) trong Q3
rev_inv = H1R['m142'] - Q3B['m142']        # giảm dự phòng HTK (mã 142)
print(f"\nDự phòng giảm Q3 (H1 soát xét → 30/9): mã136 {rev_ar:.2f} + HTK {rev_inv:.2f} = {rev_ar+rev_inv:.2f}; "
      f"LCTT dòng 03: 9T {Q3B['lctt03_9t']} − H1 soát xét {H1R['lctt03']} = {Q3B['lctt03_9t']-H1R['lctt03']:.2f} (phi tiền Q3)")
print(f"  Phi tiền Q3 21,5 vs khác ròng 31,9 ⇒ ~{q3['tnk']-q3['cpk']-(-(Q3B['lctt03_9t']-H1R['lctt03'])):.1f} tỷ không xác định bằng LCTT")
print(f"  TM10 [H1 tr.21] 30/6: KH 90,814 + khác 4,777 + trả trước NB 9,491 = {90.814+4.777+9.491:.3f}; Q3 [Q3 tr.12] KH 68,361 ⇒ dự phòng KH Q3 {68.361-90.814:+.2f} (GIẢM)")
# biên gộp bỏ hoàn nhập HTK (VAS: hoàn nhập dự phòng HTK giảm giá vốn)
print(f"  Biên gộp Q3 bỏ hoàn nhập HTK {rev_inv:.2f}: {(q3['gp']-rev_inv)/q3['dt']*100:.2f}% (báo cáo 38,93%)")
# Cận trên: coi hoàn nhập là lặp lại + QLDN lõi = như Q3/25 (QLDN gấp đôi là một lần)
core_hi_a = (q3['gp'] - q3['ql'] + q3['dttc'] - q3['cptc']) * 0.8
core_hi_b = (q3['gp'] - q325['ql'] + q3['dttc'] - q3['cptc']) * 0.8
# Cận dưới: bỏ HẾT hoàn nhập (HTK khỏi giá vốn, mã136 khỏi QLDN), giữ QLDN như báo cáo
core_lo = (q3['gp'] - rev_inv - q3['ql'] - rev_ar + q3['dttc'] - q3['cptc']) * 0.8
print(f"LNST lõi Q3 [UL, thuế 20%]: cận dưới {core_lo:.1f} (bỏ hoàn nhập {rev_ar+rev_inv:.1f}) | giữa {core_hi_a:.1f} (như báo cáo, bỏ khác ròng) | cận trên {core_hi_b:.1f} (QLDN về mức Q3/25 {q325['ql']})")
q3_core_lo, q3_core_hi = core_lo, core_hi_b
print(f"  9T lõi ≈ H1 soát xét {h1_lnst} + Q3 lõi ⇒ {h1_lnst+q3_core_lo:.1f} – {h1_lnst+q3_core_hi:.1f} (9T/25 lõi {(n925['gp']-n925['ql']+n925['dttc']-n925['cptc'])*0.8:.1f}) ⇒ YoY {(h1_lnst+q3_core_lo)/88.9-1:+.0%} … {(h1_lnst+q3_core_hi)/88.9-1:+.0%}")

# ---------- 2. Tách mảng (proxy thuế tài nguyên) ----------
tn_h1, tn_9t = 8.776, 13.227        # thuế tài nguyên phải nộp trong kỳ [H1 tr.27 TM18; Q3 tr.23 TM19]
hyd_h1_dt, hyd_h1_gp = 81.20, 42.95  # thuỷ điện H1/26 DT 81,20, biên 52,9% [CYCLE_BLOCK A, BCTC bán niên TM32]
con_h1_dt, con_h1_gp = 197.59, 54.14
ratio = (tn_9t - tn_h1) / tn_h1
hyd_q3 = hyd_h1_dt * ratio            # [UL] giả định thuế TN tỷ lệ thuận DT thuỷ điện cùng năm
FIX_Q, VAR = 15.2, 0.10               # hàm chi phí thuỷ điện [UL, CYCLE_BLOCK B — khớp 2 kỳ]
hyd_q3_gp = hyd_q3 * (1 - VAR) - FIX_Q
con_q3_dt = q3['dt'] - hyd_q3; con_q3_gp = q3['gp'] - hyd_q3_gp
print(f"\nThuỷ điện Q3/26 [UL proxy thuế TN, x{ratio:.3f}]: DT ~{hyd_q3:.1f} (Q3/25 ~41,6 [UL]) | LN gộp ~{hyd_q3_gp:.1f}")
print(f"Tư vấn Q3/26 [UL phần dư]: DT ~{con_q3_dt:.1f} (Q3/25 ~107,7) | LN gộp ~{con_q3_gp:.1f} | biên {con_q3_gp/con_q3_dt*100:.1f}%")
for alt in (38.0, 45.0):   # độ nhạy proxy
    g = alt*(1-VAR)-FIX_Q; print(f"  nhạy: thuỷ điện {alt} ⇒ tư vấn DT {q3['dt']-alt:.1f}, biên gộp {(q3['gp']-g)/(q3['dt']-alt)*100:.1f}%")
hyd_9t = hyd_h1_dt + hyd_q3; hyd_9t_gp = hyd_h1_gp + hyd_q3_gp
print(f"Thuỷ điện 9T/26 ~DT {hyd_9t:.1f} vs 9T/25 138,3 ({hyd_9t/138.3-1:+.1%}); LN gộp 9T ~{hyd_9t_gp:.1f} = {hyd_9t_gp/80*100:.0f}% của 80 tỷ")
print(f"  (mùa vụ 2025: Q4 thuỷ điện ~123,3/261,6 = {123.3/261.6:.0%} DT năm ⇒ mốc 75% sau 9T KHÔNG phải đường đi đúng)")
con_9t_dt = con_h1_dt + con_q3_dt; con_9t_gp = con_h1_gp + con_q3_gp
print(f"Tư vấn 9T/26 ~DT {con_9t_dt:.1f} (9T/25 ~252,3) | LN gộp ~{con_9t_gp:.1f} | trừ toàn bộ QLDN 9T ⇒ EBIT ~{con_9t_gp-n9['ql']:.1f}")

# ---------- 3. Bảng cân đối 30/09/2026 [Q3 tr.1-5] ----------
cash, htm = 30.735, 167.815
loans = 129.880          # vay NH 129,469 + DH 0,411 [Q3 tr.4, tr.21]
div_pay = 43.154         # cổ tức phải trả (đã chi 29/10/2026) [Q3 tr.4]
int_pay = 64.253         # lãi vay phải trả cá nhân (Long 42,1; Ngãi 6,6; khác 15,6) tại 30/06 [H1 tr.27 TM20] — Q3 không tách [UL dùng số 30/6]
ar_gross, ar_prov = 387.489, 68.361   # [Q3 tr.12]
adv = 138.718            # người mua trả trước [Q3 tr.4]
equity = 574.723
net_cash_raw = cash + htm - loans
net_adj = net_cash_raw - div_pay - int_pay
print(f"\nNet cash thô (tiền+HTM−vay) {net_cash_raw:+.1f}; trừ cổ tức phải trả & lãi vay cá nhân phải trả ⇒ {net_adj:+.1f}")
print(f"Phải thu KH gộp {ar_gross:.1f} (30/6 378,7; 1/1 408,2), dự phòng {ar_prov:.1f} (1/1 63,2) ⇒ ròng {ar_gross-ar_prov:.1f}; ứng trước {adv:.1f}")
print(f"Dự phòng phải thu NH (mã 136): 1/1 113,10 → 30/6 {H1R['m136']:.2f} [H1 tr.5, SOÁT XÉT] → 30/9 {Q3B['m136']:.2f}; HTK: 59,56 → {H1R['m142']:.2f} → {Q3B['m142']:.2f} [Q3 tr.1]")
print(f"  (mốc 107,73 của BCTC Q2 CHƯA soát xét KHÔNG còn dùng: soát xét H1 đã điều chỉnh)")
print(f"P/B {mcap/equity:.2f} (VCSH Q3 chưa soát xét, gồm khoản một lần) | P/B theo VCSH soát xét 30/6 {mcap/H1R['vcsh']:.2f} | EV (vốn hoá − net điều chỉnh) {mcap-net_adj:.1f}")
ttm = 63.85 + n9['lnst']                       # Q4/25 [BQ ticker_financial] + 9T/26
ttm_core = ttm - (q3['tnk'] - q3['cpk'])        # r2: loại CẢ khoản khác ròng 31,9 (không trừ thuế — nhất quán: khoản này gần như không chịu thuế)
print(f"LNST TTM {ttm:.1f} ⇒ P/E {mcap/ttm:.2f}; bỏ cả khác ròng Q3 31,9 ⇒ {ttm_core:.1f} ⇒ P/E {mcap/ttm_core:.2f}")
ttm_core_lo = ttm - q3['lnst'] + q3_core_lo; ttm_core_hi = ttm - q3['lnst'] + q3_core_hi
print(f"  TTM lõi hai chiều (Q3 lõi {q3_core_lo:.0f}–{q3_core_hi:.0f}): {ttm_core_lo:.1f}–{ttm_core_hi:.1f} ⇒ P/E {mcap/ttm_core_hi:.2f}–{mcap/ttm_core_lo:.2f}")
print(f"Cổ tức 2025 1.500đ/cp (CBTT 23/09/2026, trả 29/10) ⇒ lợi suất {1500/PX:.1%}; payout trên LNST 2025 150,2: {40.037/150.198:.0%}")
cfo9 = 116.845
print(f"CFO 9T {cfo9:.1f} (9T/25 137,6) vs LNST 9T {n9['lnst']:.1f}: CFO/LNST {cfo9/n9['lnst']:.2f}; /(LNST − khác ròng 31,9 = {n9['lnst']-31.9:.1f}) = {cfo9/(n9['lnst']-31.9):.2f}")
print(f"  Q3 CFO = 9T − H1 SOÁT XÉT {H1R['cfo']} [H1 tr.8 mã 20] = {cfo9-H1R['cfo']:.1f} (bản cũ dùng 54,38 chưa soát xét ⇒ 62,5 SAI)")
print(f"  Phân phối LNST 2025 [H1 tr.30]: cổ tức 40,037 ({40.037/150.198:.0%}) · khen thưởng phúc lợi 30,1 ({30.1/150.198:.0%}) · đầu tư phát triển 54,15 ({54.15/150.198:.0%}) · còn lại {150.198-40.037-30.1-54.15:.1f} ({(150.198-40.037-30.1-54.15)/150.198:.0%})")

# ---------- 4. DCF thuỷ điện có thời hạn (thuê đất đến 08/2059) ----------
# r2 (#11): khấu hao 38/năm chỉ kéo dài tới khi TSCĐ ròng hết: 506,3 [H1 tr.5 mã 221 30/6/26]; ~487 cuối 2026 ⇒ 487/38 ≈ 12,8 ⇒ 13 năm (2027–2039).
# Chi phí cố định 60,8 CHỨA khấu hao ⇒ sau 2039 EBIT +38, thuế +7,6 ⇒ FCF thấp hơn 7,6/năm (không phải mất 38).
DA, DA_YEARS, TAX = 38.0, 13, 0.2
def hydro_fcf(rev, with_da=True):
    gp = rev * (1 - VAR) - FIX_Q * 4          # [UL]
    ebit = gp - 8.0                           # [UL] chi phí chung phân bổ
    if with_da:
        return ebit * (1 - TAX) + DA - 5.0    # còn khấu hao: lá chắn thuế
    return (ebit + DA) * (1 - TAX) - 5.0      # hết khấu hao: EBIT cao hơn, nộp thuế nhiều hơn; capex 5 [UL]
def annuity(r, n): return (1 - (1 + r) ** -n) / r
N = 33   # 2027..2059
def hydro_pv(rev, r, cut=0.0, y_cut=7):
    """PV 2027..2059; cut = % DT mất từ năm y_cut+1 (rủi ro PPA [UL])."""
    pv = 0.0
    for t in range(1, N + 1):
        rv = rev * (1 - cut) if t > y_cut else rev
        f = hydro_fcf(rv, with_da=(t <= DA_YEARS))
        pv += f / (1 + r) ** t
    return pv
print("\nDCF thuỷ điện (DT/năm × lãi suất), khấu hao 38 chỉ 13 năm đầu, giá trị tỷ đồng:")
for rev, lab in [(171, "thiết kế 187 GWh × ~912 đ/kWh"), (200, "giữa"), (239, "TB 2024-25")]:
    f = hydro_fcf(rev)
    row = "  ".join(f"r{r*100:.0f}%:{hydro_pv(rev, r):6.0f}" for r in (0.10, 0.11, 0.12, 0.13))
    old = "  ".join(f"r{r*100:.0f}%:{f*annuity(r,N):6.0f}" for r in (0.10, 0.11, 0.12, 0.13))
    print(f"  DT {rev} ({lab}) FCF {f:5.1f} (sau 2039: {hydro_fcf(rev, False):5.1f}) | {row}")
    print(f"      [bản r1, khấu hao 33 năm: {old}]")
print(f"  PPA cắt −20% từ 2034: DT200 r12% = {hydro_pv(200,0.12,0.2):.0f}; DT171 r13% = {hydro_pv(171,0.13,0.2):.0f}")
hyd_base = hydro_pv(200, 0.12)
sotp_lo = hydro_pv(171, 0.13, 0.2) + 0 + net_adj
sotp_mid = hyd_base + 40 * 6 + net_adj
print(f"SOTP giá trị TÀI SẢN: thấp (thuỷ điện DT171 r13% cắt PPA, tư vấn 0) {sotp_lo:.0f} tỷ = {ps(sotp_lo):,.0f} đ/cp; "
      f"giữa (DT200 r12%, tư vấn 40×6) {sotp_mid:.0f} tỷ = {ps(sotp_mid):,.0f} đ/cp")
print(f"  [bản r1: thấp 24.273, giữa 44.713 đ/cp]")
print(f"  So SOTP 23/07: bảo thủ 883 tỷ = 33.100 đ/cp (net debt −117 cũ; nay net điều chỉnh {net_adj:+.0f})")

# ---------- 5. Giá trị cổ đông thiểu số tiếp cận được: cổ tức ----------
print("\nGiá trị theo dòng cổ tức (Gordon g=0) Ke 12,3–13,4%:")
for dps in (1500, 2000, 2800):
    print(f"  DPS {dps}: " + "  ".join(f"Ke{k*100:.1f}%:{dps/k:,.0f}" for k in (0.123, 0.13, 0.134)))

# ---------- 6. Ba kịch bản — LNST bền DỰNG TỪ KHỐI (r2: #7 tái lập được) ----------
def hyd_lnst(rev): return (rev * (1 - VAR) - FIX_Q * 4 - 8.0) * (1 - TAX)   # LNST thuỷ điện (đã trừ KH trong chi phí cố định)
TC = 5.0   # TC ròng sau thuế [UL]
print("\nLNST thuỷ điện theo DT:", {r: round(hyd_lnst(r), 1) for r in (171, 200, 239)})
CONS = (30.0, 40.0, 50.0)   # LNST tư vấn lo/mid/hi [UL]
blk = {   # (DT thuỷ điện lo/mid/hi), (P/E lo/mid/hi)
 "Tốt":   dict(p=0.25, hy=(239, 239, 239), pe=(5.0, 5.5, 6.0)),
 "Cơ sở": dict(p=0.50, hy=(171, 200, 239), pe=(3.5, 4.0, 4.5)),
}
sc = {}
for k, b in blk.items():
    l = [hyd_lnst(h) + c + TC for h, c in zip(b['hy'], CONS)]
    sc[k] = dict(p=b['p'], lnst=l, lo=l[0]*b['pe'][0], mid=l[1]*b['pe'][1], hi=l[2]*b['pe'][2])
sc["Xấu"] = dict(p=0.25, lnst=None, lo=equity*0.5, hi=equity*0.7, mid=equity*0.6)
print("Kịch bản (tỷ ⇒ đ/cp) — giá trị tại ~2027-28:")
ev = 0
for k, s_ in sc.items():
    ln = "" if s_['lnst'] is None else f" LNST bền {s_['lnst'][0]:.0f}/{s_['lnst'][1]:.0f}/{s_['lnst'][2]:.0f} |"
    print(f"  {k:6s} P={s_['p']:.2f}:{ln} {ps(s_['lo']):7,.0f} – {ps(s_['hi']):7,.0f} (tâm {ps(s_['mid']):,.0f})")
    ev += s_['p'] * ps(s_['mid'])
print(f"Kỳ vọng có trọng số (giá trị 2027-28, CHƯA chiết khấu): {ev:,.0f} đ/cp; giá {PX:,} so kỳ vọng {PX/ev-1:+.1%}")
def ev_w(w, scale_pe=1.0):
    m = [sc['Tốt']['mid']*scale_pe, sc['Cơ sở']['mid']*scale_pe, sc['Xấu']['mid']]
    return sum(wi*ps(mi) for wi, mi in zip(w, m))
for w in [(0.25,0.5,0.25),(0.2,0.5,0.3),(0.15,0.45,0.40),(0.3,0.5,0.2)]:
    print(f"  trọng số {w}: {ev_w(w):,.0f} (giá {PX/ev_w(w)-1:+.1%})")
for s_ in (0.85, 1.15):
    print(f"  P/E tốt+cơ sở ×{s_}: {ev_w((0.25,0.5,0.25), s_):,.0f}")

# ---------- 6b. CHIẾT KHẤU THỜI GIAN (r2: #8) ----------
# Giá trị kịch bản là giá TẠI T năm tới; người giữ nhận thêm cổ tức DPS/năm (1.500 = mức 2025; [UL] không đổi) — dòng t=1.. ≤ T.
DPS = 1500
def pv_scn(v, T, ke, dps=DPS):
    pv = v / (1 + ke) ** T
    t = 1
    while t <= T + 1e-9:
        pv += dps / (1 + ke) ** t; t += 1
    return pv
print(f"\nPV hôm nay của kỳ vọng (EV chưa chiết khấu {ev:,.0f}; DPS {DPS}/năm ghi nhận tại t=1,2…≤T):")
res = {}
for T in (1.0, 1.5, 2.0):
    row = []
    for ke in (0.123, 0.134):
        v = pv_scn(ev, T, ke); res[(T, ke)] = v; row.append(f"Ke{ke*100:.1f}%: {v:,.0f} (giá {PX/v-1:+.1%})")
    print(f"  T={T}: " + " | ".join(row))
for w in [(0.2,0.5,0.3),(0.15,0.45,0.40)]:
    e = ev_w(w)
    print(f"  trọng số {w} (EV {e:,.0f}): " + " | ".join(f"T={T}: {pv_scn(e,T,0.123):,.0f}–{pv_scn(e,T,0.134):,.0f}" for T in (1.0,1.5,2.0)))
# PV riêng từng kịch bản T=1,5 Ke 12,85% để đọc đáy vùng cơ sở
ke_m = 0.1285
print("  PV từng kịch bản (T=1,5; Ke 12,85%): " + "; ".join(f"{k} tâm {pv_scn(ps(s_['mid']),1.5,ke_m):,.0f} (đáy {pv_scn(ps(s_['lo']),1.5,ke_m):,.0f}, trần {pv_scn(ps(s_['hi']),1.5,ke_m):,.0f})" for k, s_ in sc.items()))
print(f"Giá {PX} ngầm định: P/E 4,0 ⇒ LNST bền {mcap/4:.0f}; P/E 3,5 ⇒ {mcap/3.5:.0f}; P/B {mcap/equity:.2f}")
print("Độ nhạy LNST × P/E (đ/cp):")
pes = (3, 3.5, 4, 4.5, 5, 6)
print("  LNST\\PE " + " ".join(f"{p:>7}" for p in pes))
for l in (80, 100, 125, 140, 155, 170):
    print(f"  {l:7d} " + " ".join(f"{ps(l*p):7,.0f}" for p in pes))
