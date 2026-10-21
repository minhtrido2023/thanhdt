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
