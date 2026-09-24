📊 **EOD Trading Report — ZaloPay (2026-09-24)**
✅ HOLD — kế hoạch hôm nay không có lệnh nào (đúng thiết kế, không phải lỗi). Bot đã trực phiên đồng bộ trạng thái.

❌ [2026-09-24] Balance record (2026-09-24T19:10:06) trả về TOÀN SỐ 0 (totalCash=0, totalDebt=0, và mọi field số khác =0) — đây là lỗi API tạm thời của DNSE, KHÔNG phải NAV thật về 0. KHÔNG tính NAV để tránh ghi số sai vào nav_history. Chạy lại script để lấy bản đọc balance tươi; nếu cuối ngày vẫn toàn 0, lấy bản đọc đầu phiên hôm sau (TRƯỚC cú khớp đầu tiên) và điền tay sau khi đối chiếu.
🛰️ Gate DT5G: ✓ ổn định (NEUTRAL) · không có candidate đang track  [dữ liệu tới 2026-09-24]
🧭 Value Radar: 🟢 20.0 RẺ (phân vị 10 năm) · P/E 11.28 (p7) · P/B 1.90 (p28) · spread EY−tiết kiệm +2.06pp (p25)  [dữ liệu tới 2026-09-24]
  ↳ ⓘ thông tin bổ sung, CHƯA qua kiểm định đủ mạnh để dùng cho sizing (0/17 lăng kính qua đa kiểm định) — chỉ để đọc, không phải tín hiệu mua/bán.
💵 Spread định giá: 🔴 EY median 9.24% − lãi vay 12.5% = -3.26pp · chỉ hiển thị, không tác động sizing/gate  [dữ liệu tới 2026-09-24, 334/350 mã có PE>0]
🧲 CAP_SIGNAL advisory (2026-09-23): quiet | EM_dd60=-1.6% VNI_dd60=-4.1% DXY_mom60=-0.3% TNX=5.11 | N_clusters=0/10 — ADVISORY THAM KHẢO, KHÔNG phải tín hiệu mua/bán tự động.

📋 **Hit Details (nội bộ, 2026-09-24)** — công thức + giá trị factor thật đằng sau mỗi tín hiệu BAL/LAG hôm nay:
# Hit Details — 2026-09-24


Nguồn: `golive_v23_recommendations_2026-09-24.csv` + raw factor fetch trực tiếp BQ (BAL) / `lag_live_schedule.live_lag_candidates()` (LAG). Công cụ audit thuần — KHÔNG đổi logic lọc/đặt lệnh. Xem `kb/coding_guidelines.md` §29.


## BAL book
_Không có mã BAL FULL/HALF_SIZE hôm nay._


## LAG book
_Không có entry LAG upcoming/recent hôm nay._
