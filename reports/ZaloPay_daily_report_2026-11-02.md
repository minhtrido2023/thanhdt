📊 **EOD Trading Report — ZaloPay (2026-11-02)**
✅ HOLD — kế hoạch hôm nay không có lệnh nào (đúng thiết kế, không phải lỗi). Bot đã trực phiên đồng bộ trạng thái.

⏳ [2026-11-02] NAV tạm hoãn — giá vị thế broker đang tự đồng bộ (thường xong trong ~90'), sẽ tự cập nhật, không cần kiểm tra tay.
🛰️ Gate DT5G: ✓ ổn định (NEUTRAL) · không có candidate đang track  [dữ liệu tới 2026-11-02]
🧭 Value Radar: 🟢 5.7 RẺ (phân vị 10 năm) · P/E 9.84 (p0) · P/B 1.74 (p9) · spread EY−CCTG 12T +2.76pp (p8)  [dữ liệu tới 2026-11-02]
  ↳ ⓘ thông tin bổ sung, CHƯA qua kiểm định đủ mạnh để dùng cho sizing (0/17 lăng kính qua đa kiểm định) — chỉ để đọc, không phải tín hiệu mua/bán.
💵 Spread định giá: 🔴 EY median 10.08% − lãi vay 12.5% = -2.42pp · chỉ hiển thị, không tác động sizing/gate  [dữ liệu tới 2026-11-02, 318/336 mã có PE>0]
🧲 CAP_SIGNAL advisory (2026-10-30): quiet | EM_dd60=-11.7% VNI_dd60=-6.0% DXY_mom60=1.9% TNX=4.93 | N_clusters=0/10 — ADVISORY THAM KHẢO, KHÔNG phải tín hiệu mua/bán tự động.

📋 **Hit Details (nội bộ, 2026-11-02)** — công thức + giá trị factor thật đằng sau mỗi tín hiệu BAL/LAG hôm nay:
# Hit Details — 2026-11-02


Nguồn: `golive_v23_recommendations_2026-11-02.csv` + raw factor fetch trực tiếp BQ (BAL) / `lag_live_schedule.live_lag_candidates()` (LAG). Công cụ audit thuần — KHÔNG đổi logic lọc/đặt lệnh. Xem `kb/coding_guidelines.md` §29.


## BAL book (1 mã)


### TCH — BAL / RE_BACKLOG_BUY (status=FULL, weight=10.00%)
ta (CSV, production) = **121.0** | ta (recomputed here) = **121**  ✓ khớp

| Điều kiện | Công thức | Điểm | Khớp? | Giá trị thật |
|---|---|---|---|---|
| RSI>0.50 | `D_RSI > 0.50` | +25 | ✅ | D_RSI=0.5652696769380174 |
| MACD>0 | `D_MACDdiff > 0` | +15 | ✅ | D_MACDdiff=73.19146337976537 |
| Close>MA20 | `Close > MA20` | +15 | ✅ | Close=11850.0 MA20=11422.5 |
| PE-cheap-vs-5Y | `PE>0 & PE_MA5Y>0 & PE < PE_MA5Y-0.5*PE_SD5Y` | +15 | ✅ | PE=14.934055611171404 PE_MA5Y=25.5486243750188 PE_SD5Y=12.766911375519973 |
| VNI-hot | `VNINDEX RSI_max3m > 0.65` | +10 | ✅ | vni_rsi_max3m=0.6764395162075593 |
| RSI1W>0.65 | `D_RSI_Max1W > 0.65` | +5 | ✅ | D_RSI_Max1W=0.6668596512496274 |
| NP-surge-YoY | `NP_P0 > NP_P4*1.5 & NP_P4>0` | +8 | ✅ | NP_P0=537726548424.0 NP_P4=40214422757.0 |
| sector-favored | `sector(ICB) in (8,9)` | +5 | ✅ | sector=8 |
| MA50-rising | `MA50_T1>0 & MA50>MA50_T1` | +5 | ✅ | MA50=11576.4 MA50_T1=11550.4 |
| NP-surge-QoQ | `NP_P0 > NP_P1*1.2 & NP_P1>0` | +8 | ✅ | NP_P0=537726548424.0 NP_P1=125416921400.0 |
| FA-D-financials | `sector=8 & fa_tier='D'` | +10 | ✅ | sector=8 fa_tier=D |

_8L rating (fa_ratings_8l, để tham khảo weight-halving BEAR/CRISIS): 4_


## LAG book (12 mã)


### BSR — LAG / LAG_HI (status=UPCOMING T+5 phiên tới, weight=10.00%)
Formula: `NP_R>=15.0 & prior_n_good>=4 & pa_HL3>=5.0` (pinned R3 LAG spec, entry T+5 sau Release_Date, hold 25 phiên)

| Biến | Giá trị | Ngưỡng | Khớp? |
|---|---|---|---|
| NP_R (%) | 888.16 | >= 15.0 | ✅ |
| prior_n_good | 8 | >= 4 | ✅ |
| pa_HL3 | 9.28 | >= 5.0 | ✅ |
| surprise_B_MA (→ tier) | 0.803 | tier=LAG_HI nếu >0.5 | tier=LAG_HI |
| Release_Date | 2026-11-02 | quarter=2026Q3 | |

_Ứng viên này đã qua thêm 3 gate upstream (không recompute ở đây — xem golive log ngày này): lag_filter_illiquid (ADV≥2 tỷ/phiên), lag_filter_low_rating (8L rating≤3), lag_filter_forensic_banned (không BANNED/forensic)._

### CSV — LAG / LAG_LO (status=UPCOMING T+5 phiên tới, weight=8.00%)
Formula: `NP_R>=15.0 & prior_n_good>=4 & pa_HL3>=5.0` (pinned R3 LAG spec, entry T+5 sau Release_Date, hold 25 phiên)

| Biến | Giá trị | Ngưỡng | Khớp? |
|---|---|---|---|
| NP_R (%) | 47.89 | >= 15.0 | ✅ |
| prior_n_good | 13 | >= 4 | ✅ |
| pa_HL3 | 5.53 | >= 5.0 | ✅ |
| surprise_B_MA (→ tier) | 0.280 | tier=LAG_HI nếu >0.5 | tier=LAG_LO |
| Release_Date | 2026-11-02 | quarter=2026Q3 | |

_Ứng viên này đã qua thêm 3 gate upstream (không recompute ở đây — xem golive log ngày này): lag_filter_illiquid (ADV≥2 tỷ/phiên), lag_filter_low_rating (8L rating≤3), lag_filter_forensic_banned (không BANNED/forensic)._

### DCM — LAG / LAG_LO (status=UPCOMING T+3 phiên tới, weight=8.00%)
Formula: `NP_R>=15.0 & prior_n_good>=4 & pa_HL3>=5.0` (pinned R3 LAG spec, entry T+5 sau Release_Date, hold 25 phiên)

| Biến | Giá trị | Ngưỡng | Khớp? |
|---|---|---|---|
| NP_R (%) | 31.10 | >= 15.0 | ✅ |
| prior_n_good | 25 | >= 4 | ✅ |
| pa_HL3 | 5.95 | >= 5.0 | ✅ |
| surprise_B_MA (→ tier) | -0.343 | tier=LAG_HI nếu >0.5 | tier=LAG_LO |
| Release_Date | 2026-10-29 | quarter=2026Q3 | |

_Ứng viên này đã qua thêm 3 gate upstream (không recompute ở đây — xem golive log ngày này): lag_filter_illiquid (ADV≥2 tỷ/phiên), lag_filter_low_rating (8L rating≤3), lag_filter_forensic_banned (không BANNED/forensic)._

### GAS — LAG / LAG_LO (status=UPCOMING T+5 phiên tới, weight=8.00%)
Formula: `NP_R>=15.0 & prior_n_good>=4 & pa_HL3>=5.0` (pinned R3 LAG spec, entry T+5 sau Release_Date, hold 25 phiên)

| Biến | Giá trị | Ngưỡng | Khớp? |
|---|---|---|---|
| NP_R (%) | 79.53 | >= 15.0 | ✅ |
| prior_n_good | 22 | >= 4 | ✅ |
| pa_HL3 | 5.13 | >= 5.0 | ✅ |
| surprise_B_MA (→ tier) | 0.440 | tier=LAG_HI nếu >0.5 | tier=LAG_LO |
| Release_Date | 2026-11-02 | quarter=2026Q3 | |

_Ứng viên này đã qua thêm 3 gate upstream (không recompute ở đây — xem golive log ngày này): lag_filter_illiquid (ADV≥2 tỷ/phiên), lag_filter_low_rating (8L rating≤3), lag_filter_forensic_banned (không BANNED/forensic)._

### GVR — LAG / LAG_HI (status=UPCOMING T+5 phiên tới, weight=10.00%)
Formula: `NP_R>=15.0 & prior_n_good>=4 & pa_HL3>=5.0` (pinned R3 LAG spec, entry T+5 sau Release_Date, hold 25 phiên)

| Biến | Giá trị | Ngưỡng | Khớp? |
|---|---|---|---|
| NP_R (%) | 75.83 | >= 15.0 | ✅ |
| prior_n_good | 16 | >= 4 | ✅ |
| pa_HL3 | 6.23 | >= 5.0 | ✅ |
| surprise_B_MA (→ tier) | 0.905 | tier=LAG_HI nếu >0.5 | tier=LAG_HI |
| Release_Date | 2026-11-02 | quarter=2026Q3 | |

_Ứng viên này đã qua thêm 3 gate upstream (không recompute ở đây — xem golive log ngày này): lag_filter_illiquid (ADV≥2 tỷ/phiên), lag_filter_low_rating (8L rating≤3), lag_filter_forensic_banned (không BANNED/forensic)._

### MSB — LAG / LAG_LO (status=UPCOMING T+5 phiên tới, weight=8.00%)
Formula: `NP_R>=15.0 & prior_n_good>=4 & pa_HL3>=5.0` (pinned R3 LAG spec, entry T+5 sau Release_Date, hold 25 phiên)

| Biến | Giá trị | Ngưỡng | Khớp? |
|---|---|---|---|
| NP_R (%) | 29.43 | >= 15.0 | ✅ |
| prior_n_good | 8 | >= 4 | ✅ |
| pa_HL3 | 6.14 | >= 5.0 | ✅ |
| surprise_B_MA (→ tier) | 0.120 | tier=LAG_HI nếu >0.5 | tier=LAG_LO |
| Release_Date | 2026-11-02 | quarter=2026Q3 | |

_Ứng viên này đã qua thêm 3 gate upstream (không recompute ở đây — xem golive log ngày này): lag_filter_illiquid (ADV≥2 tỷ/phiên), lag_filter_low_rating (8L rating≤3), lag_filter_forensic_banned (không BANNED/forensic)._

### PHP — LAG / LAG_LO (status=UPCOMING T+3 phiên tới, weight=8.00%)
Formula: `NP_R>=15.0 & prior_n_good>=4 & pa_HL3>=5.0` (pinned R3 LAG spec, entry T+5 sau Release_Date, hold 25 phiên)

| Biến | Giá trị | Ngưỡng | Khớp? |
|---|---|---|---|
| NP_R (%) | 55.83 | >= 15.0 | ✅ |
| prior_n_good | 16 | >= 4 | ✅ |
| pa_HL3 | 5.29 | >= 5.0 | ✅ |
| surprise_B_MA (→ tier) | 0.329 | tier=LAG_HI nếu >0.5 | tier=LAG_LO |
| Release_Date | 2026-10-29 | quarter=2026Q3 | |

_Ứng viên này đã qua thêm 3 gate upstream (không recompute ở đây — xem golive log ngày này): lag_filter_illiquid (ADV≥2 tỷ/phiên), lag_filter_low_rating (8L rating≤3), lag_filter_forensic_banned (không BANNED/forensic)._

### PVT — LAG / LAG_LO (status=UPCOMING T+3 phiên tới, weight=8.00%)
Formula: `NP_R>=15.0 & prior_n_good>=4 & pa_HL3>=5.0` (pinned R3 LAG spec, entry T+5 sau Release_Date, hold 25 phiên)

| Biến | Giá trị | Ngưỡng | Khớp? |
|---|---|---|---|
| NP_R (%) | 42.43 | >= 15.0 | ✅ |
| prior_n_good | 29 | >= 4 | ✅ |
| pa_HL3 | 6.91 | >= 5.0 | ✅ |
| surprise_B_MA (→ tier) | 0.051 | tier=LAG_HI nếu >0.5 | tier=LAG_LO |
| Release_Date | 2026-10-29 | quarter=2026Q3 | |

_Ứng viên này đã qua thêm 3 gate upstream (không recompute ở đây — xem golive log ngày này): lag_filter_illiquid (ADV≥2 tỷ/phiên), lag_filter_low_rating (8L rating≤3), lag_filter_forensic_banned (không BANNED/forensic)._

### TV2 — LAG / LAG_LO (status=UPCOMING T+2 phiên tới, weight=8.00%)
Formula: `NP_R>=15.0 & prior_n_good>=4 & pa_HL3>=5.0` (pinned R3 LAG spec, entry T+5 sau Release_Date, hold 25 phiên)

| Biến | Giá trị | Ngưỡng | Khớp? |
|---|---|---|---|
| NP_R (%) | 360.09 | >= 15.0 | ✅ |
| prior_n_good | 34 | >= 4 | ✅ |
| pa_HL3 | 5.01 | >= 5.0 | ✅ |
| surprise_B_MA (→ tier) | 0.486 | tier=LAG_HI nếu >0.5 | tier=LAG_LO |
| Release_Date | 2026-10-28 | quarter=2026Q3 | |

_Ứng viên này đã qua thêm 3 gate upstream (không recompute ở đây — xem golive log ngày này): lag_filter_illiquid (ADV≥2 tỷ/phiên), lag_filter_low_rating (8L rating≤3), lag_filter_forensic_banned (không BANNED/forensic)._

### YEG — LAG / LAG_LO (status=UPCOMING T+5 phiên tới, weight=8.00%)
Formula: `NP_R>=15.0 & prior_n_good>=4 & pa_HL3>=5.0` (pinned R3 LAG spec, entry T+5 sau Release_Date, hold 25 phiên)

| Biến | Giá trị | Ngưỡng | Khớp? |
|---|---|---|---|
| NP_R (%) | 35.12 | >= 15.0 | ✅ |
| prior_n_good | 11 | >= 4 | ✅ |
| pa_HL3 | 5.93 | >= 5.0 | ✅ |
| surprise_B_MA (→ tier) | 0.201 | tier=LAG_HI nếu >0.5 | tier=LAG_LO |
| Release_Date | 2026-11-02 | quarter=2026Q3 | |

_Ứng viên này đã qua thêm 3 gate upstream (không recompute ở đây — xem golive log ngày này): lag_filter_illiquid (ADV≥2 tỷ/phiên), lag_filter_low_rating (8L rating≤3), lag_filter_forensic_banned (không BANNED/forensic)._

### MCH — LAG / LAG_LO (status=WINDOW_PASSED 2026-10-29, weight=8.00%)
Formula: `NP_R>=15.0 & prior_n_good>=4 & pa_HL3>=5.0` (pinned R3 LAG spec, entry T+5 sau Release_Date, hold 25 phiên)

| Biến | Giá trị | Ngưỡng | Khớp? |
|---|---|---|---|
| NP_R (%) | 15.06 | >= 15.0 | ✅ |
| prior_n_good | 14 | >= 4 | ✅ |
| pa_HL3 | 10.82 | >= 5.0 | ✅ |
| surprise_B_MA (→ tier) | 0.101 | tier=LAG_HI nếu >0.5 | tier=LAG_LO |
| Release_Date | 2026-10-22 | quarter=2026Q3 | |

_Ứng viên này đã qua thêm 3 gate upstream (không recompute ở đây — xem golive log ngày này): lag_filter_illiquid (ADV≥2 tỷ/phiên), lag_filter_low_rating (8L rating≤3), lag_filter_forensic_banned (không BANNED/forensic)._

### MSR — LAG / LAG_HI (status=WINDOW_PASSED 2026-10-29, weight=10.00%)
Formula: `NP_R>=15.0 & prior_n_good>=4 & pa_HL3>=5.0` (pinned R3 LAG spec, entry T+5 sau Release_Date, hold 25 phiên)

| Biến | Giá trị | Ngưỡng | Khớp? |
|---|---|---|---|
| NP_R (%) | 41509.73 | >= 15.0 | ✅ |
| prior_n_good | 13 | >= 4 | ✅ |
| pa_HL3 | 8.19 | >= 5.0 | ✅ |
| surprise_B_MA (→ tier) | 2.536 | tier=LAG_HI nếu >0.5 | tier=LAG_HI |
| Release_Date | 2026-10-22 | quarter=2026Q3 | |

_Ứng viên này đã qua thêm 3 gate upstream (không recompute ở đây — xem golive log ngày này): lag_filter_illiquid (ADV≥2 tỷ/phiên), lag_filter_low_rating (8L rating≤3), lag_filter_forensic_banned (không BANNED/forensic)._
