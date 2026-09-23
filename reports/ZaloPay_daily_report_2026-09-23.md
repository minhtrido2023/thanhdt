📊 **EOD Trading Report — ZaloPay (2026-09-23)**
✅ HOLD — kế hoạch hôm nay không có lệnh nào (đúng thiết kế, không phải lỗi). Bot đã trực phiên đồng bộ trạng thái.

🚨 [2026-09-23] KHỐI LƯỢNG vị thế đổi NGOÀI lệnh khớp thật cho 1 mã (1 khớp tỉ lệ sự kiện, 0 chưa giải thích được) — KHÔNG tính NAV, CẦN NGƯỜI xử lý: VPB: KL 1,200→1,512 (so với 2026-09-22), lệnh khớp thật +0 ⇒ phần dư +312 KHỚP tỉ lệ 0.2604104 của ISS ex-date 2026-09-24 (kỳ vọng 312.49) ⇒ broker ĐÃ CREDIT SỚM. [lịch: corp_action_daily asof=2026-09-23 status=OK usable=True feed_status='FRESH'] [⚠️ journal KHÔNG đọc được cho 1 ngày GIAO DỊCH trong cửa sổ (2026-09-23: thiếu exec_ZaloPay_2026-09-23_journal.csv) ⇒ 'lệnh khớp thật' phía trên có thể THIẾU; kiểm journal TRƯỚC khi nghi corp-action] Đường phục hồi cho mã ĐÃ khớp tỉ lệ: chờ corp_action_auto_confirm.py (cron 19:25) ghi _status=CONFIRMED + qty_multiplier vào data/corp_actions.json rồi chạy lại `daily_nav_snapshot.py --from-raw --date 2026-09-23` — CHỈ mã đã CONFIRMED mới được quy ngược KL. Mã 'CHƯA GIẢI THÍCH ĐƯỢC' phải có người xác minh trước.
🛰️ Gate DT5G: ✓ ổn định (NEUTRAL) · không có candidate đang track  [dữ liệu tới 2026-09-23]
🧭 Value Radar: 🟢 22.5 RẺ (phân vị 10 năm) · P/E 11.48 (p8) · P/B 1.93 (p30) · spread EY−tiết kiệm +1.91pp (p29)  [dữ liệu tới 2026-09-23]
  ↳ ⓘ thông tin bổ sung, CHƯA qua kiểm định đủ mạnh để dùng cho sizing (0/17 lăng kính qua đa kiểm định) — chỉ để đọc, không phải tín hiệu mua/bán.
💵 Spread định giá: 🔴 EY median 9.24% − lãi vay 12.5% = -3.26pp · chỉ hiển thị, không tác động sizing/gate  [dữ liệu tới 2026-09-23, 335/351 mã có PE>0]
🧲 CAP_SIGNAL advisory (2026-09-21): quiet | EM_dd60=0.0% VNI_dd60=-4.2% DXY_mom60=-0.6% TNX=4.96 | N_clusters=0/10 — ADVISORY THAM KHẢO, KHÔNG phải tín hiệu mua/bán tự động.

📋 **Hit Details (nội bộ, 2026-09-23)** — công thức + giá trị factor thật đằng sau mỗi tín hiệu BAL/LAG hôm nay:
# Hit Details — 2026-09-23


Nguồn: `golive_v23_recommendations_2026-09-23.csv` + raw factor fetch trực tiếp BQ (BAL) / `lag_live_schedule.live_lag_candidates()` (LAG). Công cụ audit thuần — KHÔNG đổi logic lọc/đặt lệnh. Xem `kb/coding_guidelines.md` §29.


## BAL book
_Không có mã BAL FULL/HALF_SIZE hôm nay._


## LAG book
_Không có entry LAG upcoming/recent hôm nay._
