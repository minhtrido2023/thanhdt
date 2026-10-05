📊 **EOD Trading Report — ZaloPay (2026-10-05)**

⚠️ portfolio_status.py: không có dữ liệu (ValueError: Unknown format code 'f' for object of type 'str')

✅ Đối soát broker: fill thật khớp đúng state nội bộ, không lệch.

✅ Leg 3 (statement DNSE, độc lập với state/dnse_raw): số khớp trùng khớp state nội bộ, không có fill ngoài kế hoạch.
💸 Phí/thuế THẬT theo statement: 6,911đ phí + 7,124đ thuế trên 7.1M giá trị khớp (= 0.0970% giá trị).

Tổng lệnh: **5** (0 mua / 5 bán) | Khớp đủ: 5 | Khớp một phần: 0 | Chưa khớp: 0

| Chiều | Lệnh | Khớp đủ | Khớp thiếu | Chưa khớp | Giá trị |
|-------|:----:|:-------:|:----------:|:---------:|--------:|
| Bán   | 5 | 5 | 0 | 0 | 7.1M |


**Tổng giá trị giao dịch: 7.1M / kế hoạch 7.1M (100%)**

💰 **NAV 2026-10-05: 948,296,456 VND** (-2,137,954 VND, -0.22% so với hôm trước)
   Cổ phiếu 627,731,550 · Tiền mặt 154,648,079 · Nợ margin 0 · Trứng vàng 165,916,827
   Từ go-live: -51,703,544 VND (-5.17%)
🛰️ Gate DT5G: 🟢 BÌNH THƯỜNG · candidate BEAR 5/10 (50%, còn 5 phiên để commit, base giữ từ 2026-09-29, committed NEUTRAL) · P(BEAR xác nhận|k=5)≈62% [50–73%, n=65]  [dữ liệu tới 2026-10-05]
🧭 Value Radar: 🟢 24.5 RẺ (phân vị 10 năm) · P/E 11.24 (p7) · P/B 1.89 (p26) · spread EY−CCTG 6T +1.50pp (p40)  [dữ liệu tới 2026-10-05]
  ↳ ⓘ thông tin bổ sung, CHƯA qua kiểm định đủ mạnh để dùng cho sizing (0/17 lăng kính qua đa kiểm định) — chỉ để đọc, không phải tín hiệu mua/bán.
💵 Spread định giá: 🔴 EY median 9.46% − lãi vay 12.5% = -3.04pp · chỉ hiển thị, không tác động sizing/gate  [dữ liệu tới 2026-10-05, 330/346 mã có PE>0]
🧲 CAP_SIGNAL advisory (2026-10-02): quiet | EM_dd60=-2.1% VNI_dd60=-6.3% DXY_mom60=1.1% TNX=5.28 | N_clusters=0/10 — ADVISORY THAM KHẢO, KHÔNG phải tín hiệu mua/bán tự động.

📋 **Hit Details (nội bộ, 2026-10-05)** — công thức + giá trị factor thật đằng sau mỗi tín hiệu BAL/LAG hôm nay:
# Hit Details — 2026-10-05


Nguồn: `golive_v23_recommendations_2026-10-05.csv` + raw factor fetch trực tiếp BQ (BAL) / `lag_live_schedule.live_lag_candidates()` (LAG). Công cụ audit thuần — KHÔNG đổi logic lọc/đặt lệnh. Xem `kb/coding_guidelines.md` §29.


## BAL book
_Không có mã BAL FULL/HALF_SIZE hôm nay._


## LAG book
_Không có entry LAG upcoming/recent hôm nay._
