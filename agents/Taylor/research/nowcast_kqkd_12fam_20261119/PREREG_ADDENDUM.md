# PREREG ADDENDUM (19/11/2026, TRƯỚC khi tính bất kỳ IC nào — chỉ mới chạy `a4_nowcast.py --counts`)

A1. Ngưỡng quan sát giá heo: PREREG §1 ghi "≥ 20/quý" ⇒ đổi thành **≥ 10 ngày/quý**. Lý do (đo, không phải kết quả):
`data/hog_price_vn.csv` là dữ liệu TUẦN 2019Q1–2023Q4 (11–14 ngày/quý), ngày từ 2024 (69–91). Ngưỡng 20 cắt họ 2
còn 7 họ×quý (2025Q1→) do lỗi khai báo tần suất, không phải do chất lượng. Lệnh: groupby quý `date.nunique()`.

A2. Số họ×quý (`--counts`, c và np_d đều có): h1 36, h2 7 (trước A1), h3 31, h4 8, h5 16, h6 36, h7 56, h8 51, h9 40,
h10 56, h11 43, h12 55. Họ 7/8/10/12 bắt đầu 2012Q4–2014Q1 (lịch sử ticker cache từ 2013): IS/OOS không dùng cho GO,
GO dùng hai nửa như PREREG §2. Không đổi điều gì khác.
