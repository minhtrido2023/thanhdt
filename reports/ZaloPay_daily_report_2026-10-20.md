📊 **EOD Trading Report — ZaloPay (2026-10-20)**
✅ HOLD — kế hoạch hôm nay không có lệnh nào (đúng thiết kế, không phải lỗi). Bot đã trực phiên đồng bộ trạng thái.

💰 **NAV 2026-10-20: 929,949,168 VND** (+7,372,831 VND, +0.80% so với hôm trước)
   Cổ phiếu 402,091,050 · Tiền mặt 12,328,876 · Nợ margin 0 · Trứng vàng 515,529,242
   Từ go-live: -57,916,399 VND (-5.86%)
🛰️ Gate DT5G: 🟢 BÌNH THƯỜNG · candidate CRISIS 10/25 (40%, còn 15 phiên để commit, base giữ từ 2026-10-07, committed NEUTRAL) · P(CRISIS xác nhận|k=10)≈48% [27–68%, n=23] ⚠ mẫu mỏng, tham khảo  [dữ liệu tới 2026-10-20]
   ↳ Nền xấu 16 phiên liền từ 29/09 (6 BEAR + 10 CRISIS, đổi qua lại 1 lần → bộ đếm reset, vẫn NEUTRAL) · VNINDEX −5,0% từ đầu đợt · ngưỡng xem lại: ≥15 phiên và VNINDEX ≤−5,0% — chưa chạm
🧭 Value Radar: 🟢 20.1 RẺ (phân vị 10 năm) · P/E 11.03 (p5) · P/B 1.84 (p17) · spread EY−CCTG 12T +1.66pp (p38)  [dữ liệu tới 2026-10-20]
  ↳ ⓘ thông tin bổ sung, CHƯA qua kiểm định đủ mạnh để dùng cho sizing (0/17 lăng kính qua đa kiểm định) — chỉ để đọc, không phải tín hiệu mua/bán.
💵 Spread định giá: 🔴 EY median 9.37% − lãi vay 12.5% = -3.13pp · chỉ hiển thị, không tác động sizing/gate  [dữ liệu tới 2026-10-20, 328/344 mã có PE>0]
🧲 CAP_SIGNAL advisory (2026-10-19): quiet | EM_dd60=-8.4% VNI_dd60=-8.8% DXY_mom60=0.8% TNX=5.14 | N_clusters=0/10 — ADVISORY THAM KHẢO, KHÔNG phải tín hiệu mua/bán tự động.

📋 **Hit Details (nội bộ, 2026-10-20)** — công thức + giá trị factor thật đằng sau mỗi tín hiệu BAL/LAG hôm nay:
# Hit Details — 2026-10-20


Nguồn: `golive_v23_recommendations_2026-10-20.csv` + raw factor fetch trực tiếp BQ (BAL) / `lag_live_schedule.live_lag_candidates()` (LAG). Công cụ audit thuần — KHÔNG đổi logic lọc/đặt lệnh. Xem `kb/coding_guidelines.md` §29.


## BAL book
_Không có mã BAL FULL/HALF_SIZE hôm nay._


## LAG book (3 mã)


### HT1 — LAG / LAG_LO (status=UPCOMING T+4 phiên tới, weight=8.00%)
Formula: `NP_R>=15.0 & prior_n_good>=4 & pa_HL3>=5.0` (pinned R3 LAG spec, entry T+5 sau Release_Date, hold 25 phiên)

| Biến | Giá trị | Ngưỡng | Khớp? |
|---|---|---|---|
| NP_R (%) | 16.00 | >= 15.0 | ✅ |
| prior_n_good | 20 | >= 4 | ✅ |
| pa_HL3 | 8.23 | >= 5.0 | ✅ |
| surprise_B_MA (→ tier) | 0.028 | tier=LAG_HI nếu >0.5 | tier=LAG_LO |
| Release_Date | 2026-10-19 | quarter=2026Q3 | |

_Ứng viên này đã qua thêm 3 gate upstream (không recompute ở đây — xem golive log ngày này): lag_filter_illiquid (ADV≥2 tỷ/phiên), lag_filter_low_rating (8L rating≤3), lag_filter_forensic_banned (không BANNED/forensic)._

### SCL — LAG / LAG_HI (status=UPCOMING T+4 phiên tới, weight=10.00%)
Formula: `NP_R>=15.0 & prior_n_good>=4 & pa_HL3>=5.0` (pinned R3 LAG spec, entry T+5 sau Release_Date, hold 25 phiên)

| Biến | Giá trị | Ngưỡng | Khớp? |
|---|---|---|---|
| NP_R (%) | 135.97 | >= 15.0 | ✅ |
| prior_n_good | 20 | >= 4 | ✅ |
| pa_HL3 | 7.78 | >= 5.0 | ✅ |
| surprise_B_MA (→ tier) | 0.591 | tier=LAG_HI nếu >0.5 | tier=LAG_HI |
| Release_Date | 2026-10-19 | quarter=2026Q3 | |

_Ứng viên này đã qua thêm 3 gate upstream (không recompute ở đây — xem golive log ngày này): lag_filter_illiquid (ADV≥2 tỷ/phiên), lag_filter_low_rating (8L rating≤3), lag_filter_forensic_banned (không BANNED/forensic)._

### VPB — LAG / LAG_LO (status=UPCOMING T+4 phiên tới, weight=8.00%)
Formula: `NP_R>=15.0 & prior_n_good>=4 & pa_HL3>=5.0` (pinned R3 LAG spec, entry T+5 sau Release_Date, hold 25 phiên)

| Biến | Giá trị | Ngưỡng | Khớp? |
|---|---|---|---|
| NP_R (%) | 18.80 | >= 15.0 | ✅ |
| prior_n_good | 23 | >= 4 | ✅ |
| pa_HL3 | 5.55 | >= 5.0 | ✅ |
| surprise_B_MA (→ tier) | 0.160 | tier=LAG_HI nếu >0.5 | tier=LAG_LO |
| Release_Date | 2026-10-19 | quarter=2026Q3 | |

_Ứng viên này đã qua thêm 3 gate upstream (không recompute ở đây — xem golive log ngày này): lag_filter_illiquid (ADV≥2 tỷ/phiên), lag_filter_low_rating (8L rating≤3), lag_filter_forensic_banned (không BANNED/forensic)._
