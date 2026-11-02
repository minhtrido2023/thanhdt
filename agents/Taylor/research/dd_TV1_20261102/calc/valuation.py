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
# r3 (B2): hai cách hạch toán LOẠI TRỪ NHAU cho hoàn nhập phải thu 19,2 — tách trường hợp, không trộn.
h1_ql = n9['ql'] - q3['ql']                 # QLDN H1 = 9T − Q3
ql_gross_A = q3['ql'] + rev_ar              # (A) hoàn nhập đã làm giảm QLDN ⇒ QLDN gộp trước hoàn nhập
fin_q3 = q3['dttc'] - q3['cptc']
core_hi = (q3['gp'] - q325['ql'] + fin_q3) * 0.8                    # chung: QLDN gấp đôi là một lần (về mức Q3/25), giữ biên báo cáo
core_A_lo = (q3['gp'] - rev_inv - q3['ql'] - rev_ar + fin_q3) * 0.8  # (A) bỏ hoàn nhập khỏi QLDN + giá vốn
core_B_lo = (q3['gp'] - rev_inv - q3['ql'] + fin_q3) * 0.8           # (B) phải thu đã vào thu nhập khác ⇒ QLDN báo cáo là lõi; chỉ bỏ HTK khỏi giá vốn
mid = (q3['gp'] - q3['ql'] + fin_q3) * 0.8
oth = q3['tnk'] - q3['cpk']; phitien = -(Q3B['lctt03_9t'] - H1R['lctt03'])
print(f"LNST lõi Q3 [UL, thuế 20%] — 'như báo cáo, chỉ bỏ khác ròng' {mid:.1f}; cận trên chung {core_hi:.1f} (QLDN về Q3/25 {q325['ql']})")
print(f"  (A) hoàn nhập phải thu {rev_ar:.1f} vào QLDN: lõi {core_A_lo:.1f}–{core_hi:.1f}; QLDN gộp Q3 = {ql_gross_A:.1f} = {ql_gross_A/(h1_ql/2):.1f}× bình quân quý H1 ({h1_ql/2:.1f}); "
      f"khác ròng {oth:.1f} KHÔNG giải thích được (cả {oth:.1f})")
print(f"  (B) hoàn nhập phải thu vào thu nhập khác: lõi {core_B_lo:.1f}–{core_hi:.1f}; phần khác ròng không xác định = {oth:.1f} − (phi tiền {phitien:.1f} − HTK {rev_inv:.1f}) = {oth-(phitien-rev_inv):.1f}")
for lab, lo in (("A", core_A_lo), ("B", core_B_lo)):
    print(f"  9T lõi ({lab}) = H1 soát xét {h1_lnst} + Q3 lõi ⇒ {h1_lnst+lo:.1f}–{h1_lnst+core_hi:.1f} (9T/25 lõi 88,9) ⇒ YoY {(h1_lnst+lo)/88.9-1:+.0%} … {(h1_lnst+core_hi)/88.9-1:+.0%}")
    print(f"     phần không lặp lại/chưa giải thích của LNST Q3 {q3['lnst']}: {q3['lnst']-core_hi:.1f}–{q3['lnst']-lo:.1f} ({(q3['lnst']-core_hi)/q3['lnst']:.0%}–{(q3['lnst']-lo)/q3['lnst']:.0%})")
print(f"  Nghiêng A: H1 TM28 trích dự phòng phải thu ròng 0,88 nằm trong QLDN [H1 TM28]. Nghiêng B: TM VI.9c Q3 trống; QLDN gộp {ql_gross_A:.1f} khó tin.")
q3_core_lo, q3_core_hi, q3_core_B_lo = core_A_lo, core_hi, core_B_lo

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
AR_PROV_FY25 = 16.751 + 73.180   # 31/12/2025 BCTC KIỂM TOÁN A&C [FY25 tr.in 21 TM6]: bên liên quan 16,75 + KH khác 73,18
print(f"Phải thu KH gộp {ar_gross:.1f} (30/6 378,7; 1/1 408,2), dự phòng {ar_prov:.1f} (1/1 {AR_PROV_FY25:.2f} theo BCTC 2025 kiểm toán) ⇒ ròng {ar_gross-ar_prov:.1f}; ứng trước {adv:.1f}")
print(f"  Đường dự phòng KH: {AR_PROV_FY25:.1f} → 90,8 (30/6, H1 đi ngang) → {ar_prov:.1f} (Q3 giảm {ar_prov-90.814:.1f}). CỜ: cột đầu năm thuyết minh Q3 ghi 63,23 ⇒ lệch {AR_PROV_FY25-63.23:.1f} tỷ so BCTC kiểm toán")
print(f"Dự phòng phải thu NH (mã 136): 1/1 113,10 → 30/6 {H1R['m136']:.2f} [H1 tr.5, SOÁT XÉT] → 30/9 {Q3B['m136']:.2f}; HTK: 59,56 → {H1R['m142']:.2f} → {Q3B['m142']:.2f} [Q3 tr.1]")
print(f"  (mốc 107,73 của BCTC Q2 CHƯA soát xét KHÔNG còn dùng: soát xét H1 đã điều chỉnh)")
print(f"P/B {mcap/equity:.2f} (VCSH Q3 chưa soát xét, gồm khoản một lần) | P/B theo VCSH soát xét 30/6 {mcap/H1R['vcsh']:.2f} | EV (vốn hoá − net điều chỉnh) {mcap-net_adj:.1f}")
ttm = 63.85 + n9['lnst']                       # Q4/25 [BQ ticker_financial] + 9T/26
ttm_core = ttm - (q3['tnk'] - q3['cpk'])        # r2: loại CẢ khoản khác ròng 31,9 (không trừ thuế — nhất quán: khoản này gần như không chịu thuế)
print(f"LNST TTM {ttm:.1f} ⇒ P/E {mcap/ttm:.2f}; bỏ cả khác ròng Q3 31,9 ⇒ {ttm_core:.1f} ⇒ P/E {mcap/ttm_core:.2f}")
ttm_core_lo = ttm - q3['lnst'] + q3_core_lo; ttm_core_hi = ttm - q3['lnst'] + q3_core_hi
print(f"  TTM lõi (A, Q3 lõi {q3_core_lo:.0f}–{q3_core_hi:.0f}): {ttm_core_lo:.1f}–{ttm_core_hi:.1f} ⇒ P/E {mcap/ttm_core_hi:.2f}–{mcap/ttm_core_lo:.2f}")
ttm_B_lo = ttm - q3['lnst'] + q3_core_B_lo
print(f"  TTM lõi (B, Q3 lõi {q3_core_B_lo:.0f}–{q3_core_hi:.0f}): {ttm_B_lo:.1f}–{ttm_core_hi:.1f} ⇒ P/E {mcap/ttm_core_hi:.2f}–{mcap/ttm_B_lo:.2f}")
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
need = [PX*k for k in (0.123, 0.134)]
print(f"  Cổ tức cần có để biện minh giá {PX}: {need[0]:,.0f}–{need[1]:,.0f} đ/năm = {need[0]*SH/1e9:.1f}–{need[1]*SH/1e9:.1f} tỷ ⇒ payout {need[0]*SH/1e9/150.198:.0%} (LNST 2025 150,2) … {need[1]*SH/1e9/134:.0%} (LNST bền cơ sở giữa 134)")

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
eq_r = H1R['vcsh']   # N3: VCSH SOÁT XÉT 30/6 (không gồm khoản một lần Q3 chưa soát xét)
print(f"  Xấu trên VCSH soát xét {eq_r}: P/B 0,5–0,7 ⇒ {ps(eq_r*0.5):,.0f}–{ps(eq_r*0.7):,.0f} (tâm {ps(eq_r*0.6):,.0f}); trên VCSH Q3 {equity}: {ps(equity*0.5):,.0f}–{ps(equity*0.7):,.0f}")
print("Kịch bản (tỷ ⇒ đ/cp) — giá trị tại ~2027-28:")
ev = 0
for k, s_ in sc.items():
    ln = "" if s_['lnst'] is None else f" LNST bền {s_['lnst'][0]:.0f}/{s_['lnst'][1]:.0f}/{s_['lnst'][2]:.0f} |"
    print(f"  {k:6s} P={s_['p']:.2f}:{ln} {ps(s_['lo']):7,.0f} – {ps(s_['hi']):7,.0f} (tâm {ps(s_['mid']):,.0f})")
    ev += s_['p'] * ps(s_['mid'])
print(f"Kỳ vọng có trọng số (giá trị 2027-28, CHƯA chiết khấu): {ev:,.0f} đ/cp; giá {PX:,} so kỳ vọng {PX/ev-1:+.1%}")
def ev_w(w, scale_pe=1.0, eq=None):
    m = [sc['Tốt']['mid']*scale_pe, sc['Cơ sở']['mid']*scale_pe, (eq*0.6 if eq else sc['Xấu']['mid'])]
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
    frac = T - int(T)                       # r3 (N6): cổ tức tích luỹ phần lẻ năm, nằm trong giá tại T
    if frac > 1e-9:
        pv += dps * frac / (1 + ke) ** T
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
# r3 (B1+N2+N3+N5): bảng PV đầy đủ theo bộ trọng số × cơ sở VCSH kịch bản Xấu; T 1–2, Ke 12,3–13,4%
print("\nr3 — PV hôm nay (min–max trên T∈{1;1,5;2}, Ke∈{12,3%;13,4%}); giá so PV:")
WS = {"25/50/25": (0.25,0.5,0.25), "20/45/35 (nhất quán)": (0.2,0.45,0.35), "15/50/35": (0.15,0.5,0.35), "30/50/20": (0.3,0.5,0.2)}
for wl, w in WS.items():
    for eql, eq in (("VCSH Q3 574,7", None), ("VCSH soát xét 507,8", eq_r)):
        e = ev_w(w, eq=eq)
        v = [pv_scn(e, T, k) for T in (1.0,1.5,2.0) for k in (0.123,0.134)]
        print(f"  {wl:22s} | {eql:20s} | EV chưa CK {e:,.0f} | PV {min(v):,.0f}–{max(v):,.0f} | giá {PX/max(v)-1:+.1%}…{PX/min(v)-1:+.1%}")
    e = ev_w(w); v = [pv_scn(e, T, 0.151) for T in (1.0,1.5,2.0)]
    print(f"      nhạy Ke = r* thị trường 15,1% (VCSH Q3): PV {min(v):,.0f}–{max(v):,.0f} | giá {PX/max(v)-1:+.1%}…{PX/min(v)-1:+.1%}")
# PV riêng từng kịch bản T=1,5 Ke 12,85% để đọc đáy vùng cơ sở
ke_m = 0.1285
print("  PV từng kịch bản (T=1,5; Ke 12,85%): " + "; ".join(f"{k} tâm {pv_scn(ps(s_['mid']),1.5,ke_m):,.0f} (đáy {pv_scn(ps(s_['lo']),1.5,ke_m):,.0f}, trần {pv_scn(ps(s_['hi']),1.5,ke_m):,.0f})" for k, s_ in sc.items()))
print(f"Giá {PX} ngầm định: P/E 4,0 ⇒ LNST bền {mcap/4:.0f}; P/E 3,5 ⇒ {mcap/3.5:.0f}; P/B {mcap/equity:.2f}")
print("Độ nhạy LNST × P/E (đ/cp):")
pes = (3, 3.5, 4, 4.5, 5, 6)
print("  LNST\\PE " + " ".join(f"{p:>7}" for p in pes))
for l in (80, 100, 125, 140, 155, 170):
    print(f"  {l:7d} " + " ".join(f"{ps(l*p):7,.0f}" for p in pes))

# =====================================================================================================
# ---------- r4 (job Taylor_20261102_094407): DỰNG LẠI — TRỤC CHÍNH = GIÁ PPA SÔNG BUNG 5 SAU MỐC HẠ BẬC ----------
# Mọi khối r3 ở trên (kịch bản Tốt/Cơ sở/Xấu dựng trên "giá điện giữ ~912–950 đ/kWh") BỊ THAY bởi khối này.
# Chứng cứ giá: ../../tv1_sb5_ppa_price_20261013/README.md (PECC1 PA bán SB5 8/2018 tr.13: 569,36 → 243,66 đ/kWh từ 2022 theo
# dự thảo HĐ sửa đổi 05; BCTN 2025 tr.38 "giá điện của nhà máy TĐ Sông Bung 5 sụt giảm"; KBSV 17/04/2026 tr.4 lời lãnh đạo:
# từ 2027 xuống 500–600 đ/kWh chưa thuế TN/phí DVMTR).
# Hiệu chuẩn hàm chi phí bằng BÁO CÁO BỘ PHẬN BCTC 2025 KIỂM TOÁN [FY25 tr.34]: thuỷ điện DT 261,600 / KQ bộ phận 165,055 /
# khấu hao 38,143; 2024 [FY25 tr.35]: DT 215,941 / KQ 130,108 / KH 37,542; chi phí không phân bổ 44,08 (2025), 74,88 (2024).
# =====================================================================================================
print("\n" + "=" * 100 + "\nr4 — ĐỊNH GIÁ DỰNG LẠI THEO KỊCH BẢN GIÁ PPA SÔNG BUNG 5 (thay toàn bộ khối kịch bản r3)\n" + "=" * 100)
Q25, DT25, KQ25, DA25 = 236.6, 261.600, 165.055, 38.143      # sản lượng 2025 [BCTN 2025 tr.7, qua README 13/10]; [FY25 tr.34]
TN25 = 28.66                                                 # thuế tài nguyên phát sinh 2025 [BCTN 2025 tr.24, qua README 13/10]
DVMTR = 36.0                                                 # phí DVMTR đ/kWh [UL]
pass25 = TN25 + Q25 * DVMTR / 1000
p_net25 = (DT25 - pass25) / Q25 * 1000
cash_om25 = (DT25 - KQ25) - pass25 - DA25
print(f"Hiệu chuẩn 2025: thuế TN+phí ≈{pass25:.1f} (pass-through, EVN trả thêm ngoài giá) ⇒ giá ròng {p_net25:.0f} đ/kWh; "
      f"chi phí tiền mặt bộ phận ≈{cash_om25:.1f} tỷ (DT − KQ − pass − KH)")
print(f"  (đồng nhất theo cấu tạo: Q {Q25} × {p_net25:.0f} − O&M {cash_om25:.1f} − KH {DA25:.1f} = {Q25*p_net25/1000-cash_om25-DA25:.1f} = KQ bộ phận {KQ25}); r4 dùng O&M 2027 = 25 [UL] > 21,2 (trượt + tiền cấp quyền)")
CASH_OM, DA4, OVH4 = 25.0, 38.0, 8.0     # [UL] O&M 2027 (21,4×1,025² + tiền cấp quyền), khấu hao (đến ~2039), chi phí chung phân bổ
PRICE_SC = {"a_giu_975": 975.0, "b_600": 600.0, "c_500": 500.0, "d_340": 340.0}
P_PRICE = {"a_giu_975": 0.10, "b_600": 0.35, "c_500": 0.35, "d_340": 0.20}    # [UL] căn cứ: §B REPORT
QS = (175.0, 210.0)                       # sản lượng: bình quân 2013–23 (175,3) / 2021–25 (KBSV 210)
def hyd_np(p, q):                         # LNST thuỷ điện năm bền 2027+ (tỷ); lỗ được bù trừ thuế ở cấp công ty
    return (q * p / 1000 - CASH_OM - DA4 - OVH4) * (1 - TAX)
print("\nLNST thuỷ điện 2027+ theo giá ròng × sản lượng (tỷ):")
for k, p in PRICE_SC.items():
    print(f"  {k:10s} {p:5.0f} đ/kWh: Q175 DT {175*p/1000:6.1f} ⇒ LNST {hyd_np(p,175):6.1f} | Q210 DT {210*p/1000:6.1f} ⇒ LNST {hyd_np(p,210):6.1f}")
print(f"  (2025 thực: giá ròng ≈{p_net25:.0f}, Q {Q25} ⇒ LNST thuỷ điện ≈{hyd_np(p_net25,Q25):.1f})")
# Tư vấn: 2025 KQ bộ phận 80,84 − (chung 44,08 − 8 phân bổ thuỷ điện) = 44,8 EBIT ⇒ ×0,8 = 35,8; 2024: 85,73 − 66,88 = 18,8 ⇒ 15,1
cons25 = (80.841 - (44.084 - OVH4)) * 0.8; cons24 = (85.728 - (74.878 - OVH4)) * 0.8
print(f"\nLNST tư vấn tham chiếu [FY25 tr.34-35, UL phân bổ chung]: 2025 ≈{cons25:.1f}; 2024 ≈{cons24:.1f}")
CONS_OK, CONS_BAD = (30.0, 40.0, 50.0), (10.0, 15.0, 20.0)      # [UL] pháp lý ổn / cấm thầu EVN (về mức 2024 hoặc thấp hơn)
TC4 = 0.0   # r4: TC ròng 9T/26 = −1,3 (lãi tiền gửi 5,7 trừ lãi vay cá nhân) ⇒ 0 [UL]; r3 dùng +5 là lạc quan
P_LEGAL_BAD = 0.35                                               # giữ như r3 (hợp M4/M5)
PE_OK, PE_BAD = (5.0, 5.5, 6.0), (3.0, 3.5, 4.0)                 # [UL] OK: trần = trung vị 2025 (6,0) trước vụ án; BAD: ≤ 2026 YTD 4,0
def firm_np(p, q, cons): return hyd_np(p, q) + cons + TC4
print("\nLNST bền cả công ty 2027+ (tỷ) — lo (Q175, tư vấn thấp) / mid (Q192,5, giữa) / hi (Q210, tư vấn cao):")
NP = {}
for k, p in PRICE_SC.items():
    for lg, cons in (("ok", CONS_OK), ("bad", CONS_BAD)):
        lo, mid, hi = firm_np(p, 175, cons[0]), firm_np(p, 192.5, cons[1]), firm_np(p, 210, cons[2])
        NP[(k, lg)] = (lo, mid, hi)
    print(f"  {k:10s}: pháp lý ổn {NP[(k,'ok')][0]:6.1f} / {NP[(k,'ok')][1]:6.1f} / {NP[(k,'ok')][2]:6.1f} | cấm thầu {NP[(k,'bad')][0]:6.1f} / {NP[(k,'bad')][1]:6.1f} / {NP[(k,'bad')][2]:6.1f}")
print(f"  So: r3 'LNST bền cơ sở' 103–172 (giá cũ); KH ĐHĐCĐ 2026 LNST 104,2 (baodauthau 30/04/2026); LNST 2025 150,2")

# ---- (i) P/E trên LNST bền 2027+ ----
# Giá trị tại ~01/2028 (khi LNST 2027 công bố) = P/E × LNST; người giữ nhận cổ tức FY2026 (trả ~Q3/2027, t≈1). PV về 11/2026 với T=1,25.
DPS26 = (1000, 1500)      # FY2026: KH ĐHĐCĐ 2026 = 10% (baodauthau 30/04/2026) … mức FY2025 15%
T_PE = 1.25
def pv_pe(v_ps, ke, dps26): return v_ps / (1 + ke) ** T_PE + dps26 / (1 + ke) ** 0.9
print("\n(i) P/E — giá trị/cp (PV về 11/2026; Ke 12,3–13,4%; cổ tức FY2026 1.000–1.500 cộng tại t≈0,9):")
PE_RES = {}
for k in PRICE_SC:
    out = []
    for lg, pe in (("ok", PE_OK), ("bad", PE_BAD)):
        n = NP[(k, lg)]
        lo = pv_pe(ps(n[0] * pe[0]), 0.134, DPS26[0]); mid = pv_pe(ps(n[1] * pe[1]), 0.1285, sum(DPS26) / 2); hi = pv_pe(ps(n[2] * pe[2]), 0.123, DPS26[1])
        PE_RES[(k, lg)] = (lo, mid, hi); out.append(f"{lg}: {lo:7,.0f} / {mid:7,.0f} / {hi:7,.0f}")
    print(f"  {k:10s} " + " | ".join(out))

# ---- (ii) DDM / FCFE phân phối được cho cổ đông thiểu số ----
# DPS_t: t=1 (FY2026, trả 2027) = 1.000–1.500; t=2..10 = payout × LNST bền / SH; BV_{t+1} = BV_t + LNST × (1 − payout − 0,20 quỹ KTPL)
# Terminal năm 10 = min(0,6 ; ROE/Ke) × BV_10 [UL bảo thủ: thanh khoản thấp, cổ đông thiểu số không quyết phân phối]
PAYOUTS = (0.27, 0.40, 0.60)   # 27% = FY2025 thực [H1 tr.30]; 60% ≈ trần thực tế khi còn trích KTPL 20% + một phần ĐTPT
KTPL = 0.20
def ddm(np_, payout, ke, bv0, dps1, n=10, pb_cap=0.6):
    pv = dps1 / (1 + ke) ** 0.9
    bv = bv0
    for t in range(2, n + 1):
        pv += ps(np_ * payout) / (1 + ke) ** (t - 0.1)
        bv += np_ * (1 - payout - KTPL)
    roe = np_ / bv if bv > 0 else 0
    pb = max(0.0, min(pb_cap, roe / ke))
    term = ps(pb * bv) / (1 + ke) ** (n - 0.1)
    return pv + term, pv, term, pb
BV0 = (507.8, 574.7)   # VCSH soát xét 30/6 / Q3 chưa soát xét
print("\n(ii) DDM 10 năm + terminal min(0,6; ROE/Ke)×BV — giá trị/cp (mid: Ke 12,85%, BV 541, DPS26 1.250):")
DDM_RES = {}
for k in PRICE_SC:
    row = []
    for lg in ("ok", "bad"):
        n = NP[(k, lg)]
        vals = {}
        for po in PAYOUTS:
            lo = ddm(n[0], po, 0.134, BV0[0], DPS26[0])[0]; mid = ddm(n[1], po, 0.1285, sum(BV0) / 2, sum(DPS26) / 2)[0]; hi = ddm(n[2], po, 0.123, BV0[1], DPS26[1])[0]
            vals[po] = (lo, mid, hi)
        DDM_RES[(k, lg)] = vals
        row.append(f"{lg}: " + " ".join(f"p{int(po*100)} {vals[po][1]:6,.0f}" for po in PAYOUTS))
    print(f"  {k:10s} " + " | ".join(row))
_, d_pv, d_term, d_pb = ddm(NP[("c_500", "ok")][1], 0.27, 0.1285, 541.25, 1250)
print(f"  ví dụ c_500/ok/payout 27%: PV cổ tức {d_pv:,.0f} + terminal {d_term:,.0f} (P/B term {d_pb:.2f})")

# ---- Cổ tức cần có vs cổ tức bền ----
need_lo, need_hi = PX * 0.123, PX * 0.134
print(f"\nCổ tức cần có để biện minh {PX:,} (Gordon g=0, Ke 12,3–13,4%): {need_lo:,.0f}–{need_hi:,.0f} đ/cp/năm = {need_lo*SH/1e9:.1f}–{need_hi*SH/1e9:.1f} tỷ")
print("Cổ tức bền 2028+ (đ/cp) theo kịch bản giá × payout (pháp lý ổn, LNST mid):")
DIVTAB = {}
for k in PRICE_SC:
    n = NP[(k, "ok")][1]
    DIVTAB[k] = {po: ps(n * po) for po in PAYOUTS}
    need_po = need_lo * SH / 1e9 / n if n > 0 else float('inf')
    print(f"  {k:10s} LNST {n:6.1f}: " + "  ".join(f"payout {int(po*100)}% ⇒ {DIVTAB[k][po]:6,.0f}" for po in PAYOUTS) + f"  | payout cần ≥{need_po:.0%}")
print(f"  Thực trả: FY2025 1.500 (27%); KH FY2026 1.000 (10%)")

# ---- Tổng hợp xác suất ----
def wavg(res, idx):
    s = 0.0
    for k, pp in P_PRICE.items():
        s += pp * ((1 - P_LEGAL_BAD) * res[(k, "ok")][idx] + P_LEGAL_BAD * res[(k, "bad")][idx])
    return s
pe_w = [wavg(PE_RES, i) for i in range(3)]
ddm_w = {po: [sum(pp * ((1 - P_LEGAL_BAD) * DDM_RES[(k, 'ok')][po][i] + P_LEGAL_BAD * DDM_RES[(k, 'bad')][po][i]) for k, pp in P_PRICE.items()) for i in range(3)] for po in PAYOUTS}
print(f"\nKỳ vọng có trọng số (giá {P_PRICE}; P(pháp lý xấu) {P_LEGAL_BAD}):")
print(f"  (i) P/E: lo {pe_w[0]:,.0f} / mid {pe_w[1]:,.0f} / hi {pe_w[2]:,.0f}")
for po in PAYOUTS:
    print(f"  (ii) DDM payout {int(po*100)}%: lo {ddm_w[po][0]:,.0f} / mid {ddm_w[po][1]:,.0f} / hi {ddm_w[po][2]:,.0f}")
# Vùng hợp lý: (i) mid và (ii) mid với payout 27–40% (nâng lên 60% chỉ là điều kiện đổi nhận định, không phải kịch bản trung tâm)
zone_lo = min(pe_w[1], ddm_w[0.27][1]); zone_hi = max(pe_w[1], ddm_w[0.40][1])
center = (pe_w[1] + (ddm_w[0.27][1] + ddm_w[0.40][1]) / 2) / 2
print(f"VÙNG GIÁ TRỊ HỢP LÝ r4 = [min(P/E mid, DDM27 mid); max(P/E mid, DDM40 mid)] = {zone_lo:,.0f}–{zone_hi:,.0f}; tâm (TB hai phương pháp) {center:,.0f}")
print(f"  Giá {PX:,} so vùng: {PX/zone_hi-1:+.0%} … {PX/zone_lo-1:+.0%}; so tâm {PX/center-1:+.0%}")
print(f"  Nhạy: trọng số giá a/b/c/d = 0,20/0,40/0,30/0,10 (lạc quan) ⇒ P/E mid " +
      f"{sum(w*((1-P_LEGAL_BAD)*PE_RES[(k,'ok')][1]+P_LEGAL_BAD*PE_RES[(k,'bad')][1]) for k,w in zip(PRICE_SC,(0.2,0.4,0.3,0.1))):,.0f}; " +
      f"DDM40 mid {sum(w*((1-P_LEGAL_BAD)*DDM_RES[(k,'ok')][0.40][1]+P_LEGAL_BAD*DDM_RES[(k,'bad')][0.40][1]) for k,w in zip(PRICE_SC,(0.2,0.4,0.3,0.1))):,.0f}")
for k in PRICE_SC:
    print(f"  Theo kịch bản {k:10s} (pháp lý ổn, mid): P/E {PE_RES[(k,'ok')][1]:7,.0f} | DDM27 {DDM_RES[(k,'ok')][0.27][1]:7,.0f} | DDM40 {DDM_RES[(k,'ok')][0.40][1]:7,.0f} | DDM60 {DDM_RES[(k,'ok')][0.60][1]:7,.0f}")
# Mốc trễ hạ bậc: mỗi năm giữ giá cũ thêm = chênh LNST (a − kịch bản) × payout, PV
for k in ("b_600", "c_500"):
    extra = (NP[("a_giu_975", "ok")][1] - NP[(k, "ok")][1])
    print(f"  Nếu hạ bậc trễ 2 năm (2029) ở {k}: +LNST {extra:.0f} tỷ/năm × 2 ⇒ +{ps(extra*2)/1.13:,.0f} đ/cp nếu giữ lại hết trong VCSH (P/B≈1) / +{ps(extra*2*0.27)/1.13:,.0f} qua cổ tức 27%")

# ---- SOTP trần (giá trị tài sản, mô hình 13/10 + net điều chỉnh −38,7 + tư vấn) ----
OM_TAR, ESC4, CAPEX4 = 95.0, 0.025, 5.0
def hydro_ev4(p0, q, r, life=33):
    ev = 0.0
    for t in range(1, life + 1):
        g = (1 + ESC4) ** (t - 1)
        rev = q * (p0 + OM_TAR * (g - 1)) / 1000.0
        om = CASH_OM * g; dep = DA4 if t <= 13 else 0.0
        tax = max(0.0, TAX * (rev - om - dep - OVH4))
        ev += (rev - om - OVH4 - CAPEX4 * g - tax) / (1 + r) ** t
    return ev
print("\nSOTP trần (EV thuỷ điện 2027–2059 + tư vấn 40×6 + net điều chỉnh) đ/cp, Q 192,5, r 11–13%:")
SOTP4 = {}
for k, p in PRICE_SC.items():
    v = [ps(hydro_ev4(p, 192.5, r) + 240 + net_adj) for r in (0.13, 0.11)]
    v0 = [ps(hydro_ev4(p, 192.5, r) + net_adj) for r in (0.13, 0.11)]
    SOTP4[k] = (v0[0], v[1])
    print(f"  {k:10s}: tư vấn 0 ⇒ {v0[0]:7,.0f}–{v0[1]:7,.0f} | tư vấn 240 ⇒ {v[0]:7,.0f}–{v[1]:7,.0f}")
sotp_w = sum(P_PRICE[k] * ps(hydro_ev4(PRICE_SC[k], 192.5, 0.12) + 240 + net_adj) for k in PRICE_SC)
print(f"  SOTP kỳ vọng theo trọng số giá (r 12%, tư vấn 240): {sotp_w:,.0f} — TRẦN tham chiếu, cổ đông thiểu số không tiếp cận trực tiếp")
print(f"Giá {PX:,} ngầm định: P/E 4 ⇒ LNST bền {mcap/4:.0f}; P/E 5 ⇒ {mcap/5:.0f}; P/E 6 ⇒ {mcap/6:.0f} — so LNST bền r4 b/c mid ok {NP[('b_600','ok')][1]:.0f}/{NP[('c_500','ok')][1]:.0f}")

# ---- Nhạy: kết luận có phụ thuộc giả định khắt không? ----
def wsum(res_fn, pw=P_PRICE, plb=P_LEGAL_BAD):
    return sum(pp * ((1 - plb) * res_fn(k, "ok") + plb * res_fn(k, "bad")) for k, pp in pw.items())
print("\nNhạy kết luận (mid):")
print(f"  Bỏ hẳn rủi ro pháp lý (P xấu = 0): P/E {wsum(lambda k,l: PE_RES[(k,l)][1], plb=0):,.0f} | DDM40 {wsum(lambda k,l: DDM_RES[(k,l)][0.40][1], plb=0):,.0f} | DDM60 {wsum(lambda k,l: DDM_RES[(k,l)][0.60][1], plb=0):,.0f}")
OPT = {"a_giu_975": 0.25, "b_600": 0.45, "c_500": 0.25, "d_340": 0.05}
print(f"  Trọng số giá rất lạc quan {OPT} + P xấu 0: P/E {wsum(lambda k,l: PE_RES[(k,l)][1], OPT, 0):,.0f} | DDM40 {wsum(lambda k,l: DDM_RES[(k,l)][0.40][1], OPT, 0):,.0f}")
pe_hi = {k: pv_pe(ps(NP[(k,'ok')][1]*7.0), 0.1285, 1250) for k in PRICE_SC}
print(f"  P/E 7 (≈2024 trước vụ án 7,9) cho mọi kịch bản pháp lý ổn: kỳ vọng {sum(P_PRICE[k]*pe_hi[k] for k in PRICE_SC):,.0f}; riêng b_600 {pe_hi['b_600']:,.0f}")
ke151 = sum(P_PRICE[k]*((1-P_LEGAL_BAD)*ddm(NP[(k,'ok')][1],0.40,0.151,541.25,1250)[0]+P_LEGAL_BAD*ddm(NP[(k,'bad')][1],0.40,0.151,541.25,1250)[0]) for k in PRICE_SC)
print(f"  DDM40 với Ke = r* thị trường 15,1%: {ke151:,.0f}")
# Giá 19.800 cần gì: P/E 5,5 pháp lý ổn ⇒ LNST bền cần
need_np = (PX - 1250) * SH / 1e9 * 1.1285 ** T_PE / 5.5
print(f"  Để P/E 5,5 (pháp lý ổn) ra 19.800 cần LNST bền ≈{need_np:.0f} tỷ ⇒ thuỷ điện ≈{need_np-40:.0f} (tư vấn 40) ⇔ giá ròng ≈{((need_np-40)/0.8+CASH_OM+DA4+OVH4)/192.5*1000:.0f} đ/kWh ở Q 192,5")
print("\nr4 — Lưới LNST bền × P/E (đ/cp, chưa chiết khấu) cho báo cáo NĐT Phụ lục A:")
for l in (40, 60, 75, 95, 130):
    print(f"  {l:4d} tỷ: " + "  ".join(f"P/E{p}: {round(ps(l*p),-2):,.0f}" for p in (3, 4, 5, 6)))

# =====================================================================================================
# ---------- r5 (job Taylor_20261102_100630): sửa theo phản biện vòng 3 (SKEPTIC3: B1–B3, N1–N12) ----------
# Khối r4 ở trên giữ để đối chiếu; VÙNG/KẾT LUẬN r4 BỊ THAY bởi khối này. Thay đổi:
#  B1 DDM: tiền tích luỹ hưởng lãi I_PRE (trước thuế) và cộng THEO MỆNH GIÁ ở terminal; P/B chỉ áp VCSH HOẠT ĐỘNG (VCSH − tiền ròng).
#  B2 P/E 6,5–7 cho LNST bền SAU hạ bậc (rủi ro PPA đã nằm trong LNST ⇒ không chiết khấu lần hai); căn cứ: trung vị P/E thuỷ điện niêm yết
#     [BQ calc/bq_hydro_peer_pe.csv, 23 mã]: 2024 14,2 / 2025 12,8 / 2026 YTD 10,9 (p25 9,1) ⇒ 6,5–7 = chiết khấu ~35–40% so trung vị 2026
#     cho UPCOM thanh khoản thấp, quy mô nhỏ, mảng tư vấn chu kỳ [UL]. Cùng P/E cho cả hai trạng thái pháp lý (N4).
#  N4 cấm thầu = tư vấn 10/15/20 + khoản buộc nộp/bồi thường MỘT LẦN ONEOFF [UL], không hạ P/E thuỷ điện.
#  N1 P(d) 0,20→0,10 (chuyển sang b). N5 P pháp lý xấu 0,30 (= 1 − M5 0,70 = R1). N6 Q giữa 205 (bình quân năm có số 2015–2025).
#  N7 P/E cộng tiền ròng cuối 2027 (gồm −38,7 hôm nay, LN Q4/2026 ở giá cũ, trừ cổ tức FY2026 + quỹ KTPL).
#  N3 cổ tức FY2026 1.000/1.500/2.000 (KH 10%; tiền lệ KH 6% → thực 15%; KH LNST 104,2 < 9T 124,6).
#  N5b mốc: với P 0,15 [UL] (có điều kiện hạ bậc) mốc lùi 2 năm ⇒ 2027–28 còn giá cũ.
# =====================================================================================================
print("\n" + "=" * 100 + "\nr5 — SỬA THEO PHẢN BIỆN VÒNG 3 (thay vùng/kết luận r4)\n" + "=" * 100)
P5 = {"a_giu_975": 0.10, "b_600": 0.45, "c_500": 0.35, "d_340": 0.10}
PLB5 = 0.30
P_DELAY = 0.15
Q_HIST = {2015: 151.71, 2016: 169.50, 2017: 250.02, 2021: 197.37, 2022: 258.89, 2023: 187.0, 2025: 236.6}   # [../tv1_sb5_ppa_price_20261013/sb5_price_series.csv; 2021 có dấu ?]
q_avg = sum(Q_HIST.values()) / len(Q_HIST)
print(f"Sản lượng các năm có số 2015–2025 (thiếu 2018–20, 2024): bình quân {q_avg:.1f} tr kWh (bỏ 2021 nghi vấn: {(sum(Q_HIST.values())-197.37)/6:.1f}); 2013–23 công ty 175,3")
Q5 = (175.0, 205.0, 210.0)
I_PRE = 0.05; I_AT = I_PRE * (1 - TAX)
ONEOFF = 30.0          # [UL] buộc nộp lợi bất chính/bồi thường một lần nếu pháp lý xấu (LEGAL_VN không có số; ~1 năm LNST tư vấn)
NP_Q4_26 = 40.0        # [UL] LNST Q4/2026 ở giá điện cũ (M1: 25–45)
NP26 = n9['lnst'] + NP_Q4_26
DANET = DA4 - 5.0      # khấu hao − capex = tiền thu hồi/năm
DPS26_5 = (1000.0, 1500.0, 2000.0)
PE5 = (5.9, 6.15, 6.4)   # r6 B1: chiết khấu 35–40% so trung vị 9,81 (thuỷ điện, 20 mã, 2026 YTD) [UL]; 6,5–7 chuyển sang độ nhạy
KE3 = (0.134, 0.1285, 0.123)
BV3 = (507.8, 541.25, 574.7)
NC0 = net_adj
def nc_start(dps26, lg):
    """Tiền ròng đầu 2027 (tỷ): 30/9 −38,7 + LN Q4/26 + KH−capex quý − cổ tức FY2026 − quỹ KTPL FY2026 − khoản một lần (nếu xấu)."""
    return NC0 + NP_Q4_26 + DANET / 4 - dps26 * SH / 1e9 - KTPL * NP26 - (ONEOFF if lg == "bad" else 0.0)
def npop(k, lg, i, q=None):
    return hyd_np(PRICE_SC[k], q if q else Q5[i]) + (CONS_OK if lg == "ok" else CONS_BAD)[i]
def path(k, lg, i, delay, q=None, n=9):
    base = npop(k, lg, i, q)
    return [npop("a_giu_975", lg, i, q)] * 2 + [base] * (n - 2) if delay else [base] * n
def ddm5(pth, payout, ke, bv0, dps26, nc, i_at=I_AT, pb_cap=0.6):
    pv = dps26 / (1 + ke) ** 0.9
    bvop = bv0 - NC0
    for y, op in enumerate(pth, start=1):
        np_ = op + i_at * nc
        div = payout * max(np_, 0.0)
        pv += ps(div) / (1 + ke) ** (y + 0.9)
        nc += np_ + DANET - div - KTPL * max(np_, 0.0)
        bvop -= DANET
    roe = pth[-1] / bvop if bvop > 0 else 0.0
    pb = max(0.0, min(pb_cap, roe / ke))
    term_op, term_cash = ps(pb * bvop) / (1 + ke) ** 9.9, ps(nc) / (1 + ke) ** 9.9
    return pv + term_op + term_cash, pv, term_op, term_cash, pb, nc
def pe5(pth, pe, ke, dps26, nc, i_at=I_AT):
    np27 = pth[0] + i_at * nc
    nc27 = nc + np27 + DANET - KTPL * max(np27, 0.0)
    extra28 = (pth[1] - pth[-1]) * (1 - KTPL) / (1 + ke)     # mốc lùi: năm 2028 còn giá cũ, giữ lại
    v = ps(pe * pth[-1] + nc27 + extra28)
    return v / (1 + ke) ** T_PE + dps26 / (1 + ke) ** 0.9
def val(k, lg, i, delay, method, payout=0.40, pe=None, i_at=I_AT, q=None, pb_cap=0.6, ke=None):
    ke = ke if ke else KE3[i]
    nc = nc_start(DPS26_5[i], lg); pth = path(k, lg, i, delay, q)
    if method == "pe":
        return pe5(pth, pe if pe else PE5[i], ke, DPS26_5[i], nc, i_at)
    return ddm5(pth, payout, ke, BV3[i], DPS26_5[i], nc, i_at, pb_cap)[0]
def expv(method, i=1, pw=P5, plb=PLB5, pdel=P_DELAY, **kw):
    s = 0.0
    for k, pp in pw.items():
        for lg, pl in (("ok", 1 - plb), ("bad", plb)):
            if k == "a_giu_975":
                v = val(k, lg, i, False, method, **kw)
            else:
                v = (1 - pdel) * val(k, lg, i, False, method, **kw) + pdel * val(k, lg, i, True, method, **kw)
            s += pp * pl * v
    return s
print(f"Giả định r5: P giá {P5}; P pháp lý xấu {PLB5}; P mốc lùi 2 năm|hạ bậc {P_DELAY}; Q lo/mid/hi {Q5}; lãi tiền {I_PRE:.0%} trước thuế; "
      f"một lần nếu xấu {ONEOFF}; LNST Q4/26 {NP_Q4_26}; LNST FY26 ≈{NP26:.1f}; tiền ròng đầu 2027 (mid, ổn) {nc_start(1500,'ok'):+.1f}")
print("\nLNST hoạt động bền 2027+ (tỷ, chưa gồm lãi tiền) lo/mid/hi:")
for k in PRICE_SC:
    print(f"  {k:10s} ổn " + " / ".join(f"{npop(k,'ok',i):6.1f}" for i in range(3)) + " | xấu " + " / ".join(f"{npop(k,'bad',i):6.1f}" for i in range(3)))
print("\nTheo kịch bản (mid; không mốc lùi) — đ/cp:")
print(f"  {'':10s} {'P/E mid ổn':>11} {'xấu':>8} {'DDM27 ổn':>9} {'DDM40 ổn':>9} {'DDM40 xấu':>9} {'DDM60 ổn':>9}")
SC5 = {}
for k in PRICE_SC:
    r = (val(k,'ok',1,False,'pe'), val(k,'bad',1,False,'pe'), val(k,'ok',1,False,'ddm',0.27), val(k,'ok',1,False,'ddm',0.40), val(k,'bad',1,False,'ddm',0.40), val(k,'ok',1,False,'ddm',0.60))
    SC5[k] = r
    print(f"  {k:10s} " + " ".join(f"{x:9,.0f}" for x in r))
_, dpv, dto, dtc, dpb, dnc = ddm5(path('c_500','ok',1,False), 0.27, 0.1285, 541.25, 1500, nc_start(1500,'ok'))
print(f"  B1 phân rã (c)/ổn/27%: PV cổ tức {dpv:,.0f} + terminal hoạt động {dto:,.0f} (P/B {dpb:.2f} trên VCSH HĐ) + tiền ròng năm 10 {dnc:.0f} tỷ theo mệnh giá {dtc:,.0f}")
_, a, b_, c_, pbx, ncx = ddm5(path('c_500','ok',1,False), 0.27, 0.1285, 541.25, 1500, nc_start(1500,'ok'), i_at=0.0)
print(f"     cùng ca, tiền KHÔNG hưởng lãi: tổng {a+b_+c_:,.0f}")
E = {"pe": [expv("pe", i) for i in range(3)], "ddm27": [expv("ddm", i, payout=0.27) for i in range(3)],
     "ddm40": [expv("ddm", i, payout=0.40) for i in range(3)], "ddm60": [expv("ddm", i, payout=0.60) for i in range(3)]}
pe65 = expv("pe", 1, pe=PE5[0]); pe7 = expv("pe", 1, pe=PE5[2]); pe_old = (expv("pe", 1, pe=6.5), expv("pe", 1, pe=6.75), expv("pe", 1, pe=7.0))
print("\nKỳ vọng có trọng số r5 (lo / mid / hi):")
for m, v in E.items():
    print(f"  {m:6s}: {v[0]:7,.0f} / {v[1]:7,.0f} / {v[2]:7,.0f}")
print(f"  P/E mid ở {PE5[0]} / {PE5[2]}: {pe65:,.0f} / {pe7:,.0f}; ở 6,5/6,75/7 (r5): " + " / ".join(f"{x:,.0f}" for x in pe_old))
z_lo = min(pe65, E['ddm27'][1]); z_hi = max(pe7, E['ddm40'][1])
ctr = (E['pe'][1] + (E['ddm27'][1] + E['ddm40'][1]) / 2) / 2
print(f"VÙNG GIÁ TRỊ r6 = [min(P/E lo, DDM27); max(P/E hi, DDM40)] (mid) = {z_lo:,.0f}–{z_hi:,.0f}; tâm {ctr:,.0f}")
print(f"  Giá {PX:,} so vùng {PX/z_hi-1:+.0%}…{PX/z_lo-1:+.0%}; so tâm {PX/ctr-1:+.0%}")
print("\nNhạy (mid; P/E trung tâm 6,15 | DDM40):")
def both(**kw): return f"P/E {expv('pe', **{k:v for k,v in kw.items() if k not in ('payout','pb_cap')}):7,.0f} | DDM40 {expv('ddm', payout=0.40, **{k:v for k,v in kw.items() if k!='pe'}):7,.0f}"
for ia in (0.0, 0.03, 0.065):
    print(f"  lãi tiền {ia:.1%} trước thuế: {both(i_at=ia*(1-TAX))}")
for pe_ in (5.5, 6.0, 6.5, 6.75, 7.0, 8.0, 9.0):
    print(f"  P/E {pe_}: P/E {expv('pe', pe=pe_):,.0f}")
for q in (175.0, 190.0, 236.6):
    print(f"  Q giữa {q}: {both(q=q)}")
print(f"  Trọng số giá r4 (10/35/35/20) + P xấu 0,35: {both(pw=P_PRICE, plb=0.35)}")
print(f"  P xấu 0: {both(plb=0.0)} · P xấu 0,40: {both(plb=0.40)}")
print(f"  Không mốc lùi: {both(pdel=0.0)} · P mốc lùi 0,30: {both(pdel=0.30)}")
print(f"  Lạc quan a/b/c/d 25/45/25/5 + P xấu 0: {both(pw=OPT, plb=0.0)}")
print(f"  Bi quan a/b/c/d 5/30/40/25 + P xấu 0,40: {both(pw={'a_giu_975':0.05,'b_600':0.30,'c_500':0.40,'d_340':0.25}, plb=0.40)}")
print(f"  Terminal P/B trần 1,0 (DDM): {expv('ddm', payout=0.40, pb_cap=1.0):,.0f}")
print(f"  Ke = r* thị trường 15,1%: {both(ke=0.151)}")
# B3: tổ hợp nào ≥ 19.800 trong P/E/DDM?
print("\nTổ hợp đạt ≥19.800 (mid inputs, P/E hi / DDM40 / DDM60):")
for k in PRICE_SC:
    for lg in ("ok", "bad"):
        for dl in ((False, True) if k != "a_giu_975" else (False,)):
            r = (val(k, lg, 1, dl, 'pe', pe=PE5[2]), val(k, lg, 1, dl, 'ddm', 0.40), val(k, lg, 1, dl, 'ddm', 0.60))
            if max(r) >= PX:
                print(f"  {k}/{lg}/{'mốc lùi' if dl else 'đúng mốc'}: P/E hi {r[0]:,.0f} DDM40 {r[1]:,.0f} DDM60 {r[2]:,.0f}")
# giá PPA hoà vốn cho P/E 6,75 = 19.800 (ổn, mid, đúng mốc)
lo_p, hi_p = 300.0, 1100.0
for _ in range(60):
    m = (lo_p + hi_p) / 2; PRICE_SC["_x"] = m
    v = pe5(path("_x", "ok", 1, False), PE5[1], 0.1285, 1500, nc_start(1500, "ok"))
    lo_p, hi_p = (m, hi_p) if v < PX else (lo_p, m)
del PRICE_SC["_x"]
print(f"  Giá PPA ròng để P/E mid (pháp lý ổn, Q205, đúng mốc) = 19.800: ≈{m:.0f} đ/kWh")
# SOTP + chiết khấu tiếp cận ngầm định
s_ok = sum(P5[k] * ps(hydro_ev4(PRICE_SC[k], 205.0, 0.12) + 240 + NC0) for k in PRICE_SC)
s_mix = sum(P5[k] * ps(hydro_ev4(PRICE_SC[k], 205.0, 0.12) + (1 - PLB5) * 240 + PLB5 * (15 * 6 - ONEOFF) + NC0) for k in PRICE_SC)
print(f"\nSOTP r5 (Q205, r12%): tư vấn 240 ⇒ {s_ok:,.0f}; trộn pháp lý (xấu: tư vấn 15×6 − {ONEOFF:.0f}) ⇒ {s_mix:,.0f}")
for k in PRICE_SC:
    print(f"  {k:10s} r13–11%: " + "–".join(f"{ps(hydro_ev4(PRICE_SC[k], 205.0, r) + 240 + NC0):,.0f}" for r in (0.13, 0.11)))
print(f"  Chiết khấu tiếp cận ngầm định = 1 − tâm/SOTP: {1-ctr/s_ok:.0%} (SOTP 240) / {1-ctr/s_mix:.0%} (trộn) — thông lệ holding/thiểu số 20–40% ⇒ SOTP×(0,6–0,8) = {s_mix*0.6:,.0f}–{s_mix*0.8:,.0f}")
print(f"  Giá {PX:,} = SOTP trộn × {PX/s_mix:.2f} (chiết khấu {1-PX/s_mix:.0%})")
print("\nCổ tức bền 2028+ r5 (đ/cp, ổn, mid, gồm lãi tiền năm 2) payout 27/40/60%:")
for k in PRICE_SC:
    nc = nc_start(1500, 'ok'); op = npop(k, 'ok', 1)
    np27 = op + I_AT * nc; nc2 = nc + np27 + DANET - KTPL * np27 - 0.4 * np27
    np28 = op + I_AT * nc2
    print(f"  {k:10s} LNST 2028 ≈{np28:6.1f}: " + " / ".join(f"{ps(np28*po):,.0f}" for po in PAYOUTS) + f" | payout cần cho 2.435: {2435*SH/1e9/np28:.0%}")
print(f"N7 tách: LN Q4/26 giữ lại ≈{ps(NP_Q4_26+DANET/4):,.0f} đ/cp; tiền ròng hôm nay {ps(NC0):,.0f} đ/cp; cổ tức FY26+KTPL ra ≈{ps(1500*SH/1e9+KTPL*NP26):,.0f}")
# N2: nếu 500–600 là GIÁ CỐ ĐỊNH chưa gồm O&M (~95 đ/kWh 2027) ⇒ giá ròng 595–695
for p in (650.0, 695.0):
    PRICE_SC["_n2"] = p
    print(f"N2 giá ròng {p:.0f} (pháp lý ổn, mid, đúng mốc): P/E mid {val('_n2','ok',1,False,'pe'):,.0f} | DDM40 {val('_n2','ok',1,False,'ddm',0.40):,.0f}")
    del PRICE_SC["_n2"]
# N9: quy mô đuôi truy thu nếu biểu giá 2018 (bậc sau ≈340 ròng) bị áp hồi tố 2022–2026 [UL — chưa có văn bản; tiền lệ SB4A: ký lại giá + "xác định tiền lãi", chưa xác nhận truy thu]
excess = (p_net25 - 340.0) * (258.89 + 187.0 + 236.6) / 1000
print(f"N9 đuôi: chênh (giá ròng 2025 {p_net25:.0f} − 340) × sản lượng 2022+2023+2025 (682,5 tr kWh, thiếu 2024/2026) ≈ {excess:.0f} tỷ trước thuế ≈ {ps(excess*0.8):,.0f} đ/cp sau thuế — CHỈ là quy mô, không đưa vào kỳ vọng")

# =====================================================================================================
# ---------- r6 (job Taylor_20261102_102919): sửa theo SKEPTIC4 (B1 B2 N1) ----------
# B1: P/E trung vị thuỷ điện (20 mã, loại PPC/QTP/KHP/TV1; calc/hydro_peer_pe.sql) 2026 YTD 9,81 (p25 8,90), tháng 10 9,35.
#     Trung tâm chọn 6,15 (lo 5,9 / hi 6,4) = chiết khấu 37% (40%/35%) so 9,81 — phán đoán [UL]; 6,5–7 ở độ nhạy.
# =====================================================================================================
print("\n" + "=" * 100 + "\nr6 — HOÀ VỐN HAI KHUNG + TERMINAL DDM\n" + "=" * 100)
PE_MED_YTD, PE_MED_OCT = 9.81, 9.35
print(f"Chiết khấu so trung vị thuỷ điện 2026 YTD {PE_MED_YTD} / tháng 10 {PE_MED_OCT}:")
for pe_ in (5.9, 6.15, 6.4, 6.5, 6.75, 7.0):
    print(f"  P/E {pe_:5.2f}: {1-pe_/PE_MED_YTD:.0%} / {1-pe_/PE_MED_OCT:.0%}")
def center_x(price):
    PRICE_SC["_x"] = price
    try:
        pe_ = pe5(path("_x", "ok", 1, False), PE5[1], 0.1285, 1500, nc_start(1500, "ok"))
        d27 = val("_x", "ok", 1, False, "ddm", 0.27); d40 = val("_x", "ok", 1, False, "ddm", 0.40)
    finally:
        del PRICE_SC["_x"]
    return pe_, d27, d40
def solve(fn, lo=300.0, hi=1500.0):
    for _ in range(60):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if fn(m) < PX else (lo, m)
    return m
be_pe = solve(lambda p: center_x(p)[0])
be_ctr = solve(lambda p: (center_x(p)[0] + (center_x(p)[1] + center_x(p)[2]) / 2) / 2)
be_ddm40 = solve(lambda p: center_x(p)[2])
print(f"HOÀ VỐN PPA (pháp lý ổn, Q205, đúng mốc, đầu vào giữa; giá {PX:,}):")
print(f"  (1) chân P/E (bội số trung tâm {PE5[1]}): ≈{be_pe:.0f} đ/kWh")
print(f"  (2) tâm hai phương pháp ((P/E + TB(DDM27,DDM40))/2): ≈{be_ctr:.0f} đ/kWh")
print(f"  (3) riêng DDM40: ≈{be_ddm40:.0f} đ/kWh")
for pe_ in (6.5, 7.0):
    print(f"  chân P/E {pe_}: ≈{solve(lambda p: pe5(path(chr(95)+'x' if False else '_x','ok',1,False), pe_, 0.1285, 1500, nc_start(1500,'ok')) if False else (PRICE_SC.__setitem__('_x', p), pe5(path('_x','ok',1,False), pe_, 0.1285, 1500, nc_start(1500,'ok')))[1]):.0f}")
PRICE_SC.pop("_x", None)

# N1: P/E ngầm định của terminal DDM = (P/B×VCSH hoạt động + tiền ròng năm 10) / LNST hoạt động năm 10
def ddm_term(k, lg, payout, term_pe=None, i=1):
    ke = KE3[i]; pth = path(k, lg, i, False); nc = nc_start(DPS26_5[i], lg)
    tot, pv, to, tc, pb, ncT = ddm5(pth, payout, ke, BV3[i], DPS26_5[i], nc)
    bvop = BV3[i] - NC0 - 9 * DANET
    impl = (pb * bvop + ncT) / pth[-1]
    global IMPL_OP; IMPL_OP = pb * bvop / pth[-1]
    if term_pe is None:
        return tot, impl
    return pv + ps(term_pe * pth[-1] + ncT) / (1 + ke) ** 9.9, impl
print("\nN1 P/E ngầm định của terminal DDM (năm 10; mid, ổn) theo kịch bản và payout 27/40:")
for k in PRICE_SC:
    print(f"  {k:10s}: " + " | ".join(f"payout {int(po*100)}% ⇒ {ddm_term(k,'ok',po)[1]:.1f}x" for po in (0.27, 0.40)))
print("  Riêng phần HOẠT ĐỘNG (P/B×VCSH HĐ / LNST HĐ năm 10, không tính tiền ròng): " + " | ".join(f"{k} {(ddm_term(k,'ok',0.27), IMPL_OP)[1]:.1f}x" for k in PRICE_SC))
print("N1 độ nhạy: terminal = P/E × LNST HĐ năm 10 + tiền ròng (mệnh giá); kỳ vọng có trọng số mid:")
def exp_term(tp, po):
    s = 0.0
    for k, pp in P5.items():
        for lg, pl in (("ok", 1 - PLB5), ("bad", PLB5)):
            if k == "a_giu_975":
                v = ddm_term(k, lg, po, tp)[0]
            else:
                dl = ddm_term_delay(k, lg, po, tp)
                v = (1 - P_DELAY) * ddm_term(k, lg, po, tp)[0] + P_DELAY * dl
            s += pp * pl * v
    return s
def ddm_term_delay(k, lg, po, tp):
    ke = KE3[1]; pth = path(k, lg, 1, True); nc = nc_start(DPS26_5[1], lg)
    tot, pv, to, tc, pb, ncT = ddm5(pth, po, ke, BV3[1], DPS26_5[1], nc)
    return pv + ps(tp * pth[-1] + ncT) / (1 + ke) ** 9.9
base27, base40 = E["ddm27"][1], E["ddm40"][1]
print(f"  gốc (P/B ≤0,6): DDM27 {base27:,.0f} · DDM40 {base40:,.0f}")
for tp in (6.15, 6.4, 6.75):
    a, b = exp_term(tp, 0.27), exp_term(tp, 0.40)
    pe_mid = E["pe"][1]
    c = (pe_mid + (a + b) / 2) / 2
    print(f"  terminal P/E {tp}: DDM27 {a:,.0f} · DDM40 {b:,.0f}; tâm hai PP {c:,.0f} (giá {PX/c-1:+.0%})")
a, b = exp_term(6.15, 0.27), exp_term(6.75, 0.40)
print(f"  khoảng DDM {min(a, exp_term(6.15,0.40)):,.0f}–{max(exp_term(6.75,0.27), b):,.0f}")
# Chiết khấu thiểu số ngầm: terminal gốc vs terminal P/E 6,15 (cùng LNST + tiền)
print("\nr6 Tóm tắt trung tâm:")
print(f"  P/E mid (6,15) {E['pe'][1]:,.0f} | DDM27 {E['ddm27'][1]:,.0f} | DDM40 {E['ddm40'][1]:,.0f} | vùng {z_lo:,.0f}–{z_hi:,.0f} | tâm {ctr:,.0f} | giá so tâm {PX/ctr-1:+.0%}")
