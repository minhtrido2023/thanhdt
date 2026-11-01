"""SIP valuation — SOTP + normalized PE. Unit: tỷ VND unless noted.
Inputs read from BCTC gốc (calc/notes_read.md). Every parameter marked EST is an estimate (ước lượng).
Run: python3 calc/valuation.py > calc/valuation_out.txt
"""
SH = 242.112943  # triệu cp
PX = 48350       # đ/cp, DNSE latest_trade 30/10/2026 14:45
MCAP = PX * SH / 1000  # tỷ

# ---- Balance sheet 30/09/2026 consolidated (read) ----
cash, deposits, loans_sc, bonds, stocks_fv = 400.8, 7187.6, 4223.4, 1792.4, 203.9
debt = 4599.3 + 894.9
infra_accrued = 3262.8          # CP phải trả DH: chi phí hoàn thành hạ tầng đất đã cho thuê
deferred_rev = 457.2 + 14620.0
equity_parent = 5744.4 - 568.4
nci_share = 100.3 / 1178.3      # 9T26 NCI / LNST
bonds_unsec_ex_vhm = 1792.4 - 363.6
loans_unsec = loans_sc * 0.6893   # phần không có TS bảo đảm của bên vay (TM4b)

# ---- Earnings 9T26 (read) → run-rate x4/3 (EST: no seasonality adj) ----
k = 4 / 3
gp = dict(util=497.0, land=235.8, kcn_svc=238.4, goods=25.9, constr=3.6, re=43.3, other=28.3)
fin_net = 602.0 - 211.4          # lãi tiền gửi+cho vay − lãi vay
sga = 33.2 + 75.2
assoc = 47.8
ttm_parent = 1322.9 - 1001.9 + 1078.0

print(f"MCAP {MCAP:,.0f} tỷ | TTM LNST mẹ {ttm_parent:,.1f} | PE {MCAP/ttm_parent:.2f} | PB(mẹ) {MCAP/equity_parent:.2f}")
gross_fin = cash + deposits + loans_sc + bonds + stocks_fv
net_fin = gross_fin - debt
print(f"Tài sản tài chính gộp {gross_fin:,.1f}; vay {debt:,.1f}; net {net_fin:,.1f}; trừ CP hạ tầng phải trả {infra_accrued:,.1f} => {net_fin-infra_accrued:,.1f}")
print(f"Phơi nhiễm tín dụng phi ngân hàng: cho vay CTCK {loans_sc:,.1f} (không TSĐB bên vay ~{loans_unsec:,.1f}) + TP DN {bonds:,.1f} = {loans_sc+bonds:,.1f} = {(loans_sc+bonds)/equity_parent:.0%} VCSH mẹ, {(loans_sc+bonds)/MCAP:.0%} vốn hoá")

# Earnings split (pre-tax run-rate, consolidated)
core_ops_pt = (sum(gp.values()) - gp['land']) * k - sga * k + assoc * k
land_amort_pt = gp['land'] * k
fin_pt = fin_net * k
print(f"Run-rate trước thuế (EST x4/3): vận hành (trừ phân bổ đất) {core_ops_pt:,.0f} | phân bổ DT đất (phi tiền mặt) {land_amort_pt:,.0f} | tài chính ròng {fin_pt:,.0f}")

TAX = 0.20
def scen(name, p, pe_core, credit_loss, gov_disc, ha_left_value_per_ha, ha_monetize_yrs, tax_def_pv, g_note):
    core = core_ops_pt * (1 - TAX) * (1 - nci_share) * pe_core
    fin = (net_fin - infra_accrued) * (1 - nci_share)
    loss = credit_loss * (loans_unsec + bonds_unsec_ex_vhm)
    # remaining 937,1 ha leasable land (AR25), net cash margin per ha after dev/compensation/tax (EST), sold evenly over N yrs, PV at 13%
    ha = 937.1
    yearly = ha / ha_monetize_yrs * ha_left_value_per_ha
    pv = sum(yearly / 1.13 ** (t + 0.5) for t in range(ha_monetize_yrs)) * (1 - nci_share)
    tot = (core + fin - loss - tax_def_pv + pv) * (1 - gov_disc)
    ps = tot / SH * 1000
    print(f"\n[{name}] P={p} | core {core:,.0f} (PE {pe_core}x) + tài chính ròng {fin:,.0f} − lỗ tín dụng {loss:,.0f} ({credit_loss:.0%}) − thuế tương lai trên DT chờ PB (PV) {tax_def_pv:,.0f} + đất còn lại {pv:,.0f} ({ha_left_value_per_ha} tỷ/ha ròng, {ha_monetize_yrs} năm) ; CK quản trị {gov_disc:.0%}")
    print(f"   = {tot:,.0f} tỷ → {ps:,.0f} đ/cp ({ps/PX-1:+.0%} vs {PX:,}) ; {g_note}")
    return p, ps

# EST: tax on future amortization of 15.077 DT chờ PB: margin ~69% (TM25/27 9T) x 20%, recognized over ~35y; PV@13% ≈ factor 0.21
tax_def_nominal = deferred_rev * 0.69 * TAX
tax_def_pv_base = tax_def_nominal / 35 * sum(1 / 1.13 ** (t + 0.5) for t in range(35))
print(f"\nThuế TNDN tương lai trên DT chờ PB: danh nghĩa {tax_def_nominal:,.0f}, PV(35 năm,13%) {tax_def_pv_base:,.0f} (EST; giả định thuế nộp theo phân bổ — không thấy TS thuế hoãn lại lớn trên BCĐ)")

# v2 (sau khi đọc Bobby sector_read_kcn_cho_thue_dat_20261101: giá chào vùng 185 USD/m²/chu kỳ ≈ 47 tỷ/ha gộp; Tây Ninh 179,6, −6,8% YoY, lấp đầy 61%;
# 72% quỹ còn lại của SIP (678/937 ha) là Phước Đông B ở Tây Ninh = vệ tinh cung thừa). v1 (pre-Bobby) dùng 12/8/4 tỷ/ha, 12/18/25 năm: calc/valuation_out_preBobby.txt
# "tỷ/ha ròng" = giá thực thu (thấp hơn giá chào; [báo] Phước Đông ~90-110 USD) − đền bù + hạ tầng − thuế (ước lượng). Tốc độ: 2025 thực 28,6 ha; KH 2026 60 ha.
res = [
    scen("Tích cực", 0.20, 10, 0.00, 0.00, 18.0, 15, tax_def_pv_base * 0.8, "thực thu ~150 USD/m², ~62 ha/năm"),
    scen("Cơ sở", 0.50, 9, 0.05, 0.10, 12.0, 22, tax_def_pv_base, "thực thu ~110-120 USD/m², ~43 ha/năm, CK quản trị 10%"),
    scen("Tiêu cực", 0.30, 7, 0.30, 0.20, 6.0, 30, tax_def_pv_base * 1.2, "thực thu ~90 USD/m² + đền bù tăng (bảng giá đất), ~31 ha/năm; lỗ 30% TD không bảo đảm"),
]
w = sum(p * v for p, v in res)
print(f"\nTRỌNG SỐ: {w:,.0f} đ/cp ({w/PX-1:+.0%}); đối xứng 25/50/25: {0.25*res[0][1]+0.5*res[1][1]+0.25*res[2][1]:,.0f}")

# Sensitivity: base with credit loss 0..50%
print("\nĐộ nhạy cơ sở theo % lỗ phần tín dụng không bảo đảm (4.340 tỷ):")
for cl in (0, 0.1, 0.2, 0.3, 0.5):
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        _, v = scen("x", 0, 9, cl, 0.10, 12.0, 22, tax_def_pv_base, "")
    print(f"  lỗ {cl:.0%}: {v:,.0f} đ/cp")

# Normalized PE cross-check: TTM parent EPS, PE range peers (BQ 30/10/2026: IDC 7.8, PHR 8.1, VGC 10.5, NTC 12.6, KBC 14.0, SZC 21.7, LHG 4.6)
eps = ttm_parent / SH * 1000
print(f"\nPE chéo: EPS TTM mẹ {eps:,.0f}; PE 7x {7*eps:,.0f} | 8x {8*eps:,.0f} | 10x {10*eps:,.0f} | 12x {12*eps:,.0f}")
print(f"Trong EPS TTM: phần tài chính ròng sau thuế ≈ {fin_pt*(1-TAX)*(1-nci_share)/SH*1000:,.0f} đ/cp; phần phân bổ DT đất (phi tiền mặt) ≈ {land_amort_pt*(1-TAX)*(1-nci_share)/SH*1000:,.0f} đ/cp")
print(f"Cổ tức: 2025 = 5.000 đ/cp (50% VĐL) ⇒ lợi suất {5000/PX:.1%} @ {PX:,}; sàn KH 2026 10% = 1.000 đ ⇒ {1000/PX:.1%}")

print("\nĐộ nhạy cơ sở theo tỷ/ha ròng (22 năm):")
import io, contextlib
for nh in (4, 8, 12, 16, 20):
    with contextlib.redirect_stdout(io.StringIO()):
        _, v = scen("x", 0, 9, 0.05, 0.10, nh, 22, tax_def_pv_base, "")
    print(f"  {nh} tỷ/ha: {v:,.0f} đ/cp")
