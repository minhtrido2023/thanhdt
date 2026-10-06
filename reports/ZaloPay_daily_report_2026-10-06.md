📊 **EOD Trading Report — ZaloPay (2026-10-06)**

⚠️ portfolio_status.py: không có dữ liệu (ValueError: Unknown format code 'f' for object of type 'str')

✅ Đối soát broker: fill thật khớp đúng state nội bộ, không lệch.

✅ Leg 3 (statement DNSE, độc lập với state/dnse_raw): số khớp trùng khớp state nội bộ, không có fill ngoài kế hoạch.
💸 Phí/thuế THẬT theo statement: 895đ phí + 14,422đ thuế trên 0.9M giá trị khớp (= 0.0971% giá trị).

Tổng lệnh: **1** (0 mua / 1 bán) | Khớp đủ: 1 | Khớp một phần: 0 | Chưa khớp: 0

| Chiều | Lệnh | Khớp đủ | Khớp thiếu | Chưa khớp | Giá trị |
|-------|:----:|:-------:|:----------:|:---------:|--------:|
| Bán   | 1 | 1 | 0 | 0 | 0.9M |


**Tổng giá trị giao dịch: 0.9M / kế hoạch 0.9M (98%)**

💰 **NAV 2026-10-06: 941,824,936 VND** (-6,471,520 VND, -0.68% so với hôm trước)
   Cổ phiếu 620,314,400 · Tiền mặt 155,554,930 · Nợ margin 0 · Trứng vàng 165,955,606
   Từ go-live: -58,175,064 VND (-5.82%)
🛰️ Gate DT5G: 🟢 BÌNH THƯỜNG · candidate BEAR 6/10 (60%, còn 4 phiên để commit, base giữ từ 2026-09-29, committed NEUTRAL) · P(BEAR xác nhận|k=6)≈68% [56–79%, n=59]  [dữ liệu tới 2026-10-06]
🧭 Value Radar: 🟢 24.8 RẺ (phân vị 10 năm) · P/E 11.28 (p7) · P/B 1.89 (p26) · spread EY−CCTG 6T +1.47pp (p41)  [dữ liệu tới 2026-10-06]
  ↳ ⓘ thông tin bổ sung, CHƯA qua kiểm định đủ mạnh để dùng cho sizing (0/17 lăng kính qua đa kiểm định) — chỉ để đọc, không phải tín hiệu mua/bán.
💵 Spread định giá: 🔴 EY median 9.47% − lãi vay 12.5% = -3.03pp · chỉ hiển thị, không tác động sizing/gate  [dữ liệu tới 2026-10-06, 330/346 mã có PE>0]
🧲 CAP_SIGNAL advisory (2026-10-05): quiet | EM_dd60=-0.5% VNI_dd60=-5.4% DXY_mom60=1.0% TNX=5.31 | N_clusters=0/10 — ADVISORY THAM KHẢO, KHÔNG phải tín hiệu mua/bán tự động.

📋 **Hit Details (nội bộ, 2026-10-06)** — công thức + giá trị factor thật đằng sau mỗi tín hiệu BAL/LAG hôm nay:
# Hit Details — 2026-10-06


Nguồn: `golive_v23_recommendations_2026-10-06.csv` + raw factor fetch trực tiếp BQ (BAL) / `lag_live_schedule.live_lag_candidates()` (LAG). Công cụ audit thuần — KHÔNG đổi logic lọc/đặt lệnh. Xem `kb/coding_guidelines.md` §29.


## BAL book
_Không có mã BAL FULL/HALF_SIZE hôm nay._


## LAG book
_Không có entry LAG upcoming/recent hôm nay._
