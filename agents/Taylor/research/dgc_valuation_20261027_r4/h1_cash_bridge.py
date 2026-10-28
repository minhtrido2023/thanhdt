"""Cầu tiền 6T/2026 từ chênh lệch bảng cân đối hợp nhất GỐC (tỷ đồng; MIKE_EXTRACT p05/p06). Xấp xỉ gián tiếp — KHÔNG phải báo cáo lưu chuyển tiền tệ."""
d = lambda a, b: a - b   # tăng tài sản = tiền ra ; ta tính dòng tiền = -(Δ tài sản) + (Δ nợ)
tien0, tien1 = 1040.5 + 12065.3, 37.3 + 10884.2
items = {
    "LNST hợp nhất 6T": 870.8,
    "khấu hao (Δ hao mòn TSCĐ HH 3.303,2−3.167,3 + vô hình 25,4−21,3)": (3303.2 - 3167.3) + (25.4 - 21.2),
    "Δ phải thu KH (651,1→470,4)": 651.1 - 470.4,
    "Δ trả trước người bán (241,9→237,9)": 241.9 - 237.9,
    "Δ phải thu khác (332,3→328,3)": 332.3 - 328.3,
    "Δ hàng tồn kho thuần (1.681,5→2.459,9)": -(2459.9 - 1681.5),
    "Δ thuế GTGT khấu trừ + TS ngắn hạn khác (119,5→215,3)": -(215.3 - 119.5),
    "Δ phải trả NB (203,8→240,8)": 240.8 - 203.8,
    "Δ người mua trả trước (31,5→70,6)": 70.6 - 31.5,
    "Δ thuế phải nộp (351,8→129,1)": 129.1 - 351.8,
    "Δ phải trả NLĐ (194,9→120,3)": 120.3 - 194.9,
    "Δ quỹ KTPL (482,5→405,7)": 405.7 - 482.5,
    "Δ dự phòng ngắn hạn mới": 100.0,
}
cfo_proxy = sum(items.values())
others = {
    "Δ phải trả khác (1.273,8→23,1) ≈ cổ tức chi H1": 23.1 - 1273.8,
    "Δ vay ngắn hạn (1.546,2→1.869,7)": 1869.7 - 1546.2,
    "Δ XDCB dở dang (804,8→1.320,9) ~ capex": -(1320.9 - 804.8),
    "cho vay ngắn hạn mới (mã 135)": -819.0,
}
tot = cfo_proxy + sum(others.values())
print(f"Tiền+tiền gửi 31/12/2025 {tien0:.1f} → 30/06/2026 {tien1:.1f}: Δ = {tien1 - tien0:.1f}")
for k, v in items.items(): print(f"  {v:9.1f}  {k}")
print(f"  => CFO xấp xỉ 6T (trước khoản cho vay) = {cfo_proxy:.1f}")
for k, v in others.items(): print(f"  {v:9.1f}  {k}")
print(f"  => Tổng dựng lại Δ = {tot:.1f} ; phần dư không giải thích = {tien1 - tien0 - tot:.1f}")
print(f"  (nếu KHÔNG có khoản cho vay 819: Δ tiền sẽ là {tien1 - tien0 + 819:.1f})")
