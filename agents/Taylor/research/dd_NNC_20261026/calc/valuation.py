"""DD NNC 2026-10-26 — định giá kịch bản. Số đầu vào: BCTC Q3/2026 (src/NNC_Baocaotaichinh_Q3_2026.pdf),
BQ tav2_bq.ticker 2026-10-23 (giá NNC/MVC). Giả định kịch bản = ƯỚC LƯỢNG (ghi rõ trong REPORT §5)."""
SH = 21.92e6
PX = 47_600
cash, htm = 25.474, 322.440            # tỷ, BCTC 30/9/2026 mã 110, 123
debt = 4.999 + 69.890                   # vay NH (321) + DH (338+... dòng 'Vay và nợ thuê TC dài hạn')
mvc_mv = 10.3e6 * 14_300 / 1e9          # 10,3tr cp MVC x giá 23/10 (BQ)
nhc_bv = 0.710242e6 * 19_893 / 1e9      # NHC không giao dịch 23/10 -> BVPS Q2/26 (BQ)
netcash = cash + htm - debt
nonop = netcash + mvc_mv + nhc_bv
mcap = SH * PX / 1e9
print(f"mcap {mcap:.1f} | netcash {netcash:.1f} | MVC MV {mvc_mv:.1f} | NHC BV {nhc_bv:.1f} | nonop {nonop:.1f} ({nonop*1e9/SH:,.0f} d/cp)")
ttm_np = 53.9 + 39.6 + 51.2 + 69.3     # BQ NP_P0 Q4/25..Q3/26 (khớp BCTC 9T 160,08 + FY25-9T25 = 53,88)
print(f"TTM NP {ttm_np:.1f} | PE {mcap/ttm_np:.2f} | core implied {mcap-nonop:.1f} -> core PE {(mcap-nonop)/ttm_np:.2f}")

def annuity(r, n): return (1 - (1 + r) ** -n) / r
YEARS = 17                               # 2027..2043 (GP Mũi Tàu hết hạn 2043)
SGA = {"deep": 22, "bear": 22, "base": 24, "bull": 26}
sc = {  # doanh thu năm ở công suất cấp phép (tỷ), biên gộp, xác suất (chủ quan)
    "deep": (360, 0.35, 0.20),   # giá đá về mặt bằng 2023-24 (~0,67x TTM)
    "bear": (400, 0.42, 0.25),   # ~ mặt bằng 2025
    "base": (470, 0.50, 0.40),   # giá giảm ~12% từ TTM
    "bull": (560, 0.56, 0.15),   # giữ mặt bằng Q3/26
}
for r in (0.13, 0.14, 0.16):
    ev_w = 0; rows = []
    for k, (rev, gpm, p) in sc.items():
        np_ = (rev * gpm - SGA[k]) * 0.8     # thuế 20%; KHÔNG tính lãi tiền gửi (đã nằm trong net cash)
        v = (np_ * annuity(r, YEARS) + nonop) * 1e9 / SH
        ev_w += p * v; rows.append(f"{k}: NP {np_:.0f} -> {v:,.0f}")
    print(f"r={r:.0%} | " + " | ".join(rows) + f" | weighted {ev_w:,.0f} ({ev_w/PX-1:+.0%})")
# Tam Lập 1 khu II (option, ước lượng): 1tr m3/năm từ 2028, NP = 60% base Mũi Tàu, đầu tư ~150 tỷ 2026-27
tl_np = 0.6 * (470 * 0.50 - 24) * 0.8
for r in (0.14,):
    pv = tl_np * annuity(r, 15) / (1 + r) ** 2 - 150
    print(f"Tam Lap option r={r:.0%}: NP/yr {tl_np:.0f}, PV {pv:.0f} ty = {pv*1e9/SH:,.0f} d/cp (UOC LUONG, khong vao weighted)")
# breakeven: NP chuẩn hoá mà giá hiện tại hàm ý (r=14%)
be = (mcap - nonop) / annuity(0.14, YEARS)
print(f"Implied steady NP at 47.600 (r=14%, 17y): {be:.0f} ty/nam vs TTM {ttm_np:.0f}")
