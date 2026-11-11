# PRELOCK — tiêu chí khoá TRƯỚC khi thấy số (job Taylor_20261111_032615)
Ghi lúc: 2026-11-11 ~10:40 ICT, trước khi chạy build_panel.py.

Engine: dcf_valuation.fair_value, RATE_FRAME domestic_v2 (mặc định), OSHARES_SOURCE=fin (PIT), term cap_rf.
Mẫu chính (PRIMARY): mã không-tài-chính, in_universe (universe_pit) tại as-of, rating_8l<=3 as-of (merge_asof), FV ok.
As-of: phiên cuối mỗi quý 2016Q1..2025Q4. Giá as-of = Price (chưa điều chỉnh, cùng khung OShares quý).
Đường giá sau as-of (cùng khung) = Price_t * Close_{t+k}/Close_t (Close điều chỉnh).

KẾT LUẬN "KHÔNG TƯƠNG THÍCH" nếu BẤT KỲ:
 K1: tỉ lệ (mã, as-of) có giá chạm <= tâm FV trong 60 tháng (tính cả t0) < 50%  [chỉ as-of đủ 60 tháng: <= 2021Q3]
 K2: trung vị FV/giá tại as-of lệch > 25% khỏi 1 (ngoài [0.75, 1.25])
 K3: không hội tụ tại N=36: median |log(P_{t+36}/FV_t)| >= median |log(P_t/FV_t)|
     HOẶC hệ số beta của hồi quy log(P_{t+36}/P_t) ~ log(FV_t/P_t) có CI95 bootstrap cụm (theo quý) chứa 0 hoặc âm.
Ngược lại => "TƯƠNG THÍCH".
Bootstrap: cụm theo mã và theo quý, B=2000, seed=20261111. Không đổi tiêu chí sau khi thấy số.
Biến thể (e) nếu KHÔNG TƯƠNG THÍCH: lưới nhỏ khai trước — r in {10.25,11.25,12.25,13.25}, g_T cap {4.5,5.5,6.5},
GROWTH_SHRINK {0.25,0.5,0.75}, cơ sở FCFE 3Y vs 5Y; chọn trên IS (as-of 2016-2019) theo |log median FV/P| nhỏ nhất
VÀ K3 đạt, rồi đo OOS (2020+). Khai N trials = số tổ hợp chạy thật.
