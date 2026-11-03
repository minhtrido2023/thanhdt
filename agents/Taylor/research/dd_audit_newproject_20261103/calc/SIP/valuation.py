"""SIP valuation v2 (sau phản biện 01/11/2026) — SOTP + PE chéo. Đơn vị: tỷ VND trừ khi ghi khác.
Số đọc từ BCTC gốc: calc/notes_read.md (+ tự kiểm ảnh img/q3hn p07 BCĐ mã 323, p12 TM1, p43 TM36, p45 TM40).
Mọi tham số kịch bản là ƯỚC LƯỢNG. v1 giữ ở calc/valuation_v1.py -> calc/valuation_out_v1.txt.
Run: python3 calc/valuation.py > calc/valuation_out.txt
Thay đổi v2:
 F1  trừ trích quỹ KTPL khỏi dòng lãi (TM36: 97,53/1.077,99 = 9,05% 9T26 ước tính; 9T25 trình bày lại 72,65/1.001,85 = 7,25%)
     + trừ số dư quỹ KTPL 638,8 (BCĐ mã 323, nợ ngắn hạn) khỏi tài sản tài chính ròng.
 F3  "tỷ/ha ròng" = TOÀN PHẦN (giá thực thu − đền bù − hạ tầng − thuế) ⇒ phần chi phí ĐÃ CHI cho quỹ đất còn lại
     (tạm ứng đền bù + XDCB dự án KCN) được cộng lại khi thu hồi qua tiền thuê (tỷ lệ thu hồi theo kịch bản).
 F4  NCI: mẹ (net 781,1 sau nghĩa vụ hạ tầng, BCTC riêng) 0% NCI; phần ở con (4.270,0) chịu NCI hiệu dụng theo kịch bản
     (8,5% = tỷ trọng lãi NCI; 20%; 31% = VRG Long Thành 69%). Không có BCTC từng con ⇒ khai vào GAPS G14.
 F6  bỏ thuế 20% trên LDLK (số LDLK đã sau thuế).
"""
import io, contextlib
SH = 242.112943  # triệu cp
PX = 48350       # đ/cp, DNSE latest_trade khớp cuối 30/10/2026 14:45:06
MCAP = PX * SH / 1000

cash, deposits, loans_sc, bonds, stocks_fv = 400.8, 7187.6, 4223.4, 1792.4, 203.9
debt = 4599.3 + 894.9
infra_accrued = 3262.8
ktpl_fund = 638.8                 # BCĐ mã 323 30/09/2026 (Q3HN tr.6)
deferred_rev = 457.2 + 14620.0
equity_parent = 5744.4 - 568.4
nci_profit = 100.3 / 1178.3       # 8,5%
bonds_unsec_ex_vhm = 1792.4 - 363.6
loans_unsec = loans_sc * 0.6893
# BCTC riêng mẹ 30/09/2026: tiền 221,2 + TP 1.792,4 + HTM 6.912,2 − vay 5.491,9 − CP hạ tầng phải trả 2.652,8
parent_net = 221.2 + 1792.4 + 6912.2 - 5491.9 - 2652.8
# Chi phí đã chi cho quỹ đất KCN còn lại (Q3HN TM7, TM10): tạm ứng đền bù NH 2.529,6 (PĐ-Bời Lời 2.421,1; Long Đức 2 108,5)
# + DH 290,6 (LMX3 198,1; Đông Nam 92,5) + XDCB PĐ-Bời Lời 1.268,9 + Đông Nam 204,7 + Lộc An-Bình Sơn 163,5. LOẠI LMX3 nhà xưởng 474,5, cảng 78,1.
spent_land = 2529.6 + 290.6 + 1268.9 + 204.7 + 163.5

k = 4 / 3
gp = dict(util=497.0, land=235.8, kcn_svc=238.4, goods=25.9, constr=3.6, re=43.3, other=28.3)
fin_net = 602.0 - 211.4
sga = 33.2 + 75.2
assoc = 47.8
TAX = 0.20
KTPL_BASE = 97.5 / 1078.0

ttm_parent = 1322.9 - 1001.9 + 1078.0
eps_raw = ttm_parent / SH * 1000
eps_bctc = 4972 - 3838 + 4050      # EPS kiểm toán 2025 − EPS 9T25 trình bày lại + EPS 9T26 (TM36, đã trừ KTPL)
gross_fin = cash + deposits + loans_sc + bonds + stocks_fv
net_fin = gross_fin - debt
net_after = net_fin - infra_accrued
subs_net = net_after - parent_net

print(f"MCAP {MCAP:,.0f} tỷ | LNST mẹ TTM {ttm_parent:,.1f}")
print(f"EPS TTM chưa trừ KTPL {eps_raw:,.0f} (PE {PX/eps_raw:.2f}) | EPS TTM theo BCTC (đã trừ KTPL) {eps_bctc:,} (PE {PX/eps_bctc:.2f})")
print(f"Tỷ lệ trích KTPL: 9T26 ước tính {KTPL_BASE:.2%} | 9T25 trình bày lại {72.65/1001.85:.2%}")
print(f"EPS 9T: 4.050 vs 3.838 (trình bày lại) = {4050/3838-1:+.1%} | LNST mẹ 9T {1078.0/1001.9-1:+.1%}")
print(f"Tài sản TC gộp {gross_fin:,.1f} − vay {debt:,.1f} = {net_fin:,.1f}; − CP hạ tầng phải trả {infra_accrued:,.1f} = {net_after:,.1f}; − quỹ KTPL {ktpl_fund} = {net_after-ktpl_fund:,.1f}")
print(f"  trong đó mẹ {parent_net:,.1f} | con (suy) {subs_net:,.1f}")
print(f"Chi phí đã chi cho quỹ đất KCN còn lại (ước, loại nhà xưởng/cảng): {spent_land:,.1f}")
print(f"Phơi nhiễm tín dụng phi NH {loans_sc+bonds:,.1f} = {(loans_sc+bonds)/equity_parent:.0%} VCSH mẹ; không bảo đảm {loans_unsec+bonds_unsec_ex_vhm:,.1f}")

core_ops_pt = (sum(gp.values()) - gp['land']) * k - sga * k
print(f"Run-rate trước thuế vận hành (trừ phân bổ đất, ×4/3, ước lượng) {core_ops_pt:,.0f}; LDLK sau thuế {assoc*k:,.0f}")

def pv_even(total, yrs, r=0.13):
    return sum(total / yrs / (1 + r) ** (t + 0.5) for t in range(yrs))

tax_def_nominal = deferred_rev * 0.69 * TAX
tax_def_pv_base = pv_even(tax_def_nominal, 35)

def scen(name, p, pe_core, credit_loss, gov_disc, perha, yrs, tax_def_pv, nci_sub, recover, ktpl=KTPL_BASE, note="", show=True):
    core = (core_ops_pt * (1 - TAX) + assoc * k) * (1 - nci_profit) * (1 - ktpl) * pe_core
    fin = parent_net + subs_net * (1 - nci_sub) - ktpl_fund
    loss = credit_loss * (loans_unsec + bonds_unsec_ex_vhm)
    land = pv_even(937.1 * perha, yrs) * (1 - nci_profit) * (1 - ktpl)
    sunk = pv_even(spent_land * recover, yrs) * (1 - nci_profit)
    tot = (core + fin - loss - tax_def_pv + land + sunk) * (1 - gov_disc)
    ps = tot / SH * 1000
    if show:
        print(f"\n[{name}] P={p} | core {core:,.0f} (PE {pe_core}x, KTPL {ktpl:.1%}) + TC ròng {fin:,.0f} (NCI con {nci_sub:.1%}, đã trừ quỹ KTPL) − lỗ TD {loss:,.0f} ({credit_loss:.0%})"
              f" − thuế tương lai DT chờ PB {tax_def_pv:,.0f} + đất còn lại {land:,.0f} ({perha} tỷ/ha toàn phần, {yrs} năm) + thu hồi chi phí đã chi {sunk:,.0f} ({recover:.0%}) ; CK quản trị {gov_disc:.0%}")
        print(f"   = {tot:,.0f} tỷ → {ps:,.0f} đ/cp ({PX/ps-1:+.1%} giá so với giá trị) ; {note}")
    return p, ps

BASE = dict(pe_core=9, credit_loss=0.05, gov_disc=0.10, perha=12.0, yrs=22, tax_def_pv=tax_def_pv_base, nci_sub=0.20, recover=1.0)
res = [
    scen("Tích cực", 0.20, 10, 0.00, 0.00, 18.0, 15, tax_def_pv_base * 0.8, 0.085, 0.9, note="thực thu ~150 USD/m², ~62 ha/năm"),
    scen("Cơ sở", 0.50, note="thực thu ~110-120 USD/m², ~43 ha/năm", **BASE),
    scen("Tiêu cực", 0.30, 7, 0.30, 0.20, 6.0, 30, tax_def_pv_base * 1.2, 0.31, 0.3, note="~90 USD/m² + đền bù tăng, ~31 ha/năm; lỗ 30% TD không bảo đảm"),
]
w = sum(p * v for p, v in res)
sym = 0.25 * res[0][1] + 0.5 * res[1][1] + 0.25 * res[2][1]
print(f"\nTRỌNG SỐ 20/50/30: {w:,.0f} đ/cp (giá {PX/w-1:+.1%} so với tâm) ; đối xứng 25/50/25: {sym:,.0f} (giá {PX/sym-1:+.1%})")

def base_with(**kw):
    a = dict(BASE); a.update(kw)
    return scen("x", 0, show=False, **a)[1]

print("\nĐộ nhạy CƠ SỞ (một biến, còn lại giữ nguyên):")
print("  lỗ TD không bảo đảm: " + " | ".join(f"{c:.0%}: {base_with(credit_loss=c):,.0f}" for c in (0, .1, .2, .3, .5, .6)))
print("  tỷ/ha toàn phần: " + " | ".join(f"{h}: {base_with(perha=h):,.0f}" for h in (4, 8, 12, 16, 20)))
print("  NCI con: " + " | ".join(f"{n:.1%}: {base_with(nci_sub=n):,.0f}" for n in (0.085, 0.20, 0.31)))
print("  thu hồi chi phí đã chi: " + " | ".join(f"{r:.0%}: {base_with(recover=r):,.0f}" for r in (0, 0.3, 0.6, 0.9)))
print("  tỷ lệ KTPL: " + " | ".join(f"{t:.2%}: {base_with(ktpl=t):,.0f}" for t in (0.0, 0.0725, KTPL_BASE)))
print(f"  thuế đã nộp (không trừ thuế tương lai): {base_with(tax_def_pv=0):,.0f}")
lo = base_with(credit_loss=0.5, perha=8.0, nci_sub=0.31, recover=0.3)
hi = base_with(credit_loss=0.0, perha=16.0, nci_sub=0.085, recover=0.9)
print(f"  Hộp sai số mô hình cơ sở (TD 50%/0%, tỷ/ha 8/16, NCI 31/8,5%, thu hồi 30/90%): {lo:,.0f} – {hi:,.0f}")

print(f"\nPE chéo (EPS TTM theo BCTC {eps_bctc:,}): " + " | ".join(f"{m}x {m*eps_bctc:,.0f}" for m in (7, 8, 9, 10, 12)))
print(f"Trong EPS: tài chính ròng sau thuế ≈ {fin_net*k*(1-TAX)*(1-nci_profit)*(1-KTPL_BASE)/SH*1000:,.0f} đ/cp; phân bổ DT đất (phi tiền mặt) ≈ {gp['land']*k*(1-TAX)*(1-nci_profit)*(1-KTPL_BASE)/SH*1000:,.0f} đ/cp")
print(f"Cổ tức 2025 5.000 đ/cp ⇒ {5000/PX:.1%} (quá khứ; payout 111% LN riêng, có hoàn nhập quỹ ĐTPT 542,8→213,8 = {542.8-213.8:.1f}); sàn KH 2026 1.000 đ ⇒ {1000/PX:.1%}")
