# Hit Details — 2026-08-12


Nguồn: `golive_v23_recommendations_2026-08-12.csv` + raw factor fetch trực tiếp BQ (BAL) / `lag_live_schedule.live_lag_candidates()` (LAG). Công cụ audit thuần — KHÔNG đổi logic lọc/đặt lệnh. Xem `kb/coding_guidelines.md` §29.


## BAL book
_Không có mã BAL FULL/HALF_SIZE hôm nay._


## LAG book (2 mã)


### PHR — LAG / LAG_HI (status=WINDOW_PASSED 2026-08-07, weight=10.00%)
Formula: `NP_R>=15.0 & prior_n_good>=4 & pa_HL3>=5.0` (pinned R3 LAG spec, entry T+5 sau Release_Date, hold 25 phiên)

| Biến | Giá trị | Ngưỡng | Khớp? |
|---|---|---|---|
| NP_R (%) | 300.26 | >= 15.0 | ✅ |
| prior_n_good | 25 | >= 4 | ✅ |
| pa_HL3 | 5.73 | >= 5.0 | ✅ |
| surprise_B_MA (→ tier) | 1.200 | tier=LAG_HI nếu >0.5 | tier=LAG_HI |
| Release_Date | 2026-07-31 | quarter=2026Q2 | |

_Ứng viên này đã qua thêm 3 gate upstream (không recompute ở đây — xem golive log ngày này): lag_filter_illiquid (ADV≥2 tỷ/phiên), lag_filter_low_rating (8L rating≤3), lag_filter_forensic_banned (không BANNED/forensic)._

### SSI — LAG / LAG_LO (status=WINDOW_PASSED 2026-08-07, weight=8.00%)
Formula: `NP_R>=15.0 & prior_n_good>=4 & pa_HL3>=5.0` (pinned R3 LAG spec, entry T+5 sau Release_Date, hold 25 phiên)

| Biến | Giá trị | Ngưỡng | Khớp? |
|---|---|---|---|
| NP_R (%) | 26.98 | >= 15.0 | ✅ |
| prior_n_good | 30 | >= 4 | ✅ |
| pa_HL3 | 5.87 | >= 5.0 | ✅ |
| surprise_B_MA (→ tier) | 0.085 | tier=LAG_HI nếu >0.5 | tier=LAG_LO |
| Release_Date | 2026-07-31 | quarter=2026Q2 | |

_Ứng viên này đã qua thêm 3 gate upstream (không recompute ở đây — xem golive log ngày này): lag_filter_illiquid (ADV≥2 tỷ/phiên), lag_filter_low_rating (8L rating≤3), lag_filter_forensic_banned (không BANNED/forensic)._
