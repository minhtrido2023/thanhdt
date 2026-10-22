📊 **EOD Trading Report — ZaloPay (2026-10-21)**
✅ HOLD — kế hoạch hôm nay không có lệnh nào (đúng thiết kế, không phải lỗi). Bot đã trực phiên đồng bộ trạng thái.

🚨 [2026-10-21] KHỐI LƯỢNG vị thế đổi NGOÀI lệnh khớp thật cho 1 mã (0 khớp tỉ lệ sự kiện, 1 chưa giải thích được) — KHÔNG tính NAV, CẦN NGƯỜI xử lý: DRI: KL 1,900→1,300 (so với 2026-10-20), lệnh khớp thật +0 ⇒ phần dư -600 CHƯA GIẢI THÍCH ĐƯỢC — lịch corp-action KHÔNG có sự kiện nào cho mã này vào phiên kế tiếp. [lịch: corp_action_daily asof=2026-10-21 status=OK usable=True feed_status='FRESH'] [⚠️ journal KHÔNG đọc được cho 1 ngày GIAO DỊCH trong cửa sổ (2026-10-21: thiếu exec_ZaloPay_2026-10-21_journal.csv) ⇒ 'lệnh khớp thật' phía trên có thể THIẾU; kiểm journal TRƯỚC khi nghi corp-action] Đường phục hồi cho mã ĐÃ khớp tỉ lệ: chờ corp_action_auto_confirm.py (cron 19:25) ghi _status=CONFIRMED + qty_multiplier vào data/corp_actions.json rồi chạy lại `daily_nav_snapshot.py --from-raw --date 2026-10-21` — CHỈ mã đã CONFIRMED mới được quy ngược KL. Mã 'CHƯA GIẢI THÍCH ĐƯỢC' phải có người xác minh trước.
🛰️ Gate DT5G: 🟢 BÌNH THƯỜNG · candidate CRISIS 11/25 (44%, còn 14 phiên để commit, base giữ từ 2026-10-07, committed NEUTRAL) · P(CRISIS xác nhận|k=11)≈55% [32–77%, n=20] ⚠ mẫu mỏng, tham khảo  [dữ liệu tới 2026-10-21]
   ↳ Nền xấu 17 phiên liền từ 29/09 (6 BEAR + 11 CRISIS, đổi qua lại 1 lần → bộ đếm reset, vẫn NEUTRAL) · VNINDEX −2,4% từ đầu đợt · ngưỡng xem lại: ≥15 phiên và VNINDEX ≤−5,0% — chưa chạm
🧭 Value Radar: 🟢 24.5 RẺ (phân vị 10 năm) · P/E 11.20 (p7) · P/B 1.89 (p27) · spread EY−CCTG 12T +1.53pp (p40)  [dữ liệu tới 2026-10-21]
  ↳ ⓘ thông tin bổ sung, CHƯA qua kiểm định đủ mạnh để dùng cho sizing (0/17 lăng kính qua đa kiểm định) — chỉ để đọc, không phải tín hiệu mua/bán.
💵 Spread định giá: 🔴 EY median 9.32% − lãi vay 12.5% = -3.18pp · chỉ hiển thị, không tác động sizing/gate  [dữ liệu tới 2026-10-21, 322/341 mã có PE>0]
🧲 CAP_SIGNAL advisory (2026-10-20): quiet | EM_dd60=-8.4% VNI_dd60=-8.7% DXY_mom60=0.6% TNX=5.12 | N_clusters=0/10 — ADVISORY THAM KHẢO, KHÔNG phải tín hiệu mua/bán tự động.

📋 **Hit Details (nội bộ, 2026-10-21)** — công thức + giá trị factor thật đằng sau mỗi tín hiệu BAL/LAG hôm nay:
# Hit Details — 2026-10-21


Nguồn: `golive_v23_recommendations_2026-10-21.csv` + raw factor fetch trực tiếp BQ (BAL) / `lag_live_schedule.live_lag_candidates()` (LAG). Công cụ audit thuần — KHÔNG đổi logic lọc/đặt lệnh. Xem `kb/coding_guidelines.md` §29.


## BAL book
_Không có mã BAL FULL/HALF_SIZE hôm nay._


## LAG book (3 mã)


### HT1 — LAG / LAG_LO (status=UPCOMING T+3 phiên tới, weight=8.00%)
Formula: `NP_R>=15.0 & prior_n_good>=4 & pa_HL3>=5.0` (pinned R3 LAG spec, entry T+5 sau Release_Date, hold 25 phiên)

| Biến | Giá trị | Ngưỡng | Khớp? |
|---|---|---|---|
| NP_R (%) | 16.00 | >= 15.0 | ✅ |
| prior_n_good | 20 | >= 4 | ✅ |
| pa_HL3 | 8.23 | >= 5.0 | ✅ |
| surprise_B_MA (→ tier) | 0.028 | tier=LAG_HI nếu >0.5 | tier=LAG_LO |
| Release_Date | 2026-10-19 | quarter=2026Q3 | |

_Ứng viên này đã qua thêm 3 gate upstream (không recompute ở đây — xem golive log ngày này): lag_filter_illiquid (ADV≥2 tỷ/phiên), lag_filter_low_rating (8L rating≤3), lag_filter_forensic_banned (không BANNED/forensic)._

### SCL — LAG / LAG_HI (status=UPCOMING T+3 phiên tới, weight=10.00%)
Formula: `NP_R>=15.0 & prior_n_good>=4 & pa_HL3>=5.0` (pinned R3 LAG spec, entry T+5 sau Release_Date, hold 25 phiên)

| Biến | Giá trị | Ngưỡng | Khớp? |
|---|---|---|---|
| NP_R (%) | 135.97 | >= 15.0 | ✅ |
| prior_n_good | 20 | >= 4 | ✅ |
| pa_HL3 | 7.78 | >= 5.0 | ✅ |
| surprise_B_MA (→ tier) | 0.591 | tier=LAG_HI nếu >0.5 | tier=LAG_HI |
| Release_Date | 2026-10-19 | quarter=2026Q3 | |

_Ứng viên này đã qua thêm 3 gate upstream (không recompute ở đây — xem golive log ngày này): lag_filter_illiquid (ADV≥2 tỷ/phiên), lag_filter_low_rating (8L rating≤3), lag_filter_forensic_banned (không BANNED/forensic)._

### VPB — LAG / LAG_LO (status=UPCOMING T+3 phiên tới, weight=8.00%)
Formula: `NP_R>=15.0 & prior_n_good>=4 & pa_HL3>=5.0` (pinned R3 LAG spec, entry T+5 sau Release_Date, hold 25 phiên)

| Biến | Giá trị | Ngưỡng | Khớp? |
|---|---|---|---|
| NP_R (%) | 18.80 | >= 15.0 | ✅ |
| prior_n_good | 23 | >= 4 | ✅ |
| pa_HL3 | 5.55 | >= 5.0 | ✅ |
| surprise_B_MA (→ tier) | 0.160 | tier=LAG_HI nếu >0.5 | tier=LAG_LO |
| Release_Date | 2026-10-19 | quarter=2026Q3 | |

_Ứng viên này đã qua thêm 3 gate upstream (không recompute ở đây — xem golive log ngày này): lag_filter_illiquid (ADV≥2 tỷ/phiên), lag_filter_low_rating (8L rating≤3), lag_filter_forensic_banned (không BANNED/forensic)._
