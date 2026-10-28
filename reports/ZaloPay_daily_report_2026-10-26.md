📊 **EOD Trading Report — ZaloPay (2026-10-26)**

─────────────────────────────────────────────────
📋 **TÌNH TRẠNG DANH MỤC — ZaloPay (2026-10-26)**
Chiến lược: **V2.4** | Regime: **NEUTRAL** (DT5G) | Park target: **0%** idle cash
⚠️ NAV hôm nay (2026-10-26) CHƯA có trong nav_history_ZaloPay.csv lúc chạy mục này — hiện NAV gần nhất (2026-10-23): **929.0M**, đổi so với ngày trước đó **-0.14%** (KHÔNG PHẢI thay đổi của hôm nay). Số NAV chính thức hôm nay xem mục 💰 NAV cuối report (daily_nav_snapshot.py, chạy sau mục này).
Gate DT5G: 🟢 BÌNH THƯỜNG · candidate CRISIS 14/25 (56%, còn 11 phiên để commit, base giữ từ 2026-10-07, committed NEUTRAL) · P(CRISIS xác nhận|k=14)≈73% [50–93%, n=15] ⚠ mẫu mỏng, tham khảo  [dữ liệu tới 2026-10-26]
   ↳ Nền xấu 20 phiên liền từ 29/09 (6 BEAR + 14 CRISIS, đổi qua lại 1 lần → bộ đếm reset, vẫn NEUTRAL) · VNINDEX −1,0% từ đầu đợt · ngưỡng xem lại: ≥15 phiên và VNINDEX ≤−5,0% — chưa chạm
Value Radar: 🟢 23.2 RẺ (phân vị 10 năm) · P/E 11.19 (p7) · P/B 1.87 (p23) · spread EY−CCTG 12T +1.54pp (p40)  [dữ liệu tới 2026-10-26]
─────────────────────────────────────────────────

**Cơ cấu danh mục**

| Sleeve | Giá trị | % NAV | Lãi/Lỗ CK | Ghi chú |
|--------|--------:|------:|----------:|---------|
| Trứng vàng | 535.3M | 57.6% | — | DNSE bond-like (off-book) |
| Cash | 2.1M | 0.2% | 0% | Idle |

**Corp Action — 7 ngày tới** (mã đang giữ)
Không có corp action trong 7 ngày tới trên mã đang giữ.

**Cờ theo dõi**
- PARK: rổ hiện hành chốt 2026-08-05 (chu kỳ ~quý, kế tiếp ~2026-12-01 (ước tính)).
- LAG: 2 candidate đang trong cửa sổ upcoming (chưa vào lệnh).

✅ Đối soát broker: fill thật khớp đúng state nội bộ, không lệch.

✅ Leg 3 (statement DNSE, độc lập với state/dnse_raw): số khớp trùng khớp state nội bộ, không có fill ngoài kế hoạch.
📉 **Broker xác nhận KHỚP THIẾU so với kế hoạch** — chưa đạt mục tiêu, KHÔNG được đọc là "đã mua đủ" (§27):
  • SCL (mua): chỉ khớp 500/700 đặt (71%) — phần thiếu 200cp
  • VPB (mua): chỉ khớp 700/900 đặt (78%) — phần thiếu 200cp
💸 Phí/thuế THẬT theo statement: 51,346đ phí + 0đ thuế trên 54.4M giá trị khớp (= 0.0943% giá trị).

Tổng lệnh: **3** (3 mua / 0 bán) | Khớp đủ: 1 | Khớp một phần: 2 | Chưa khớp: 0

| Chiều | Lệnh | Khớp đủ | Khớp thiếu | Chưa khớp | Giá trị |
|-------|:----:|:-------:|:----------:|:---------:|--------:|
| Mua   | 3 | 1 | 2 | 0 | 54.4M |

**Chi tiết đáng chú ý:**
  • MUA HT1: 1,600/1,600 (100%) @ 13,469đ → 21.6M
     ↳ 🟢 DCF: CHEAP (giá trị hợp lý ~25,652đ vs giá 13,550đ, MoS +47.2%, robust)
     ↳ DD HT1 (data 2026-10-23): thanh khoản OK (ADV3T 3.04 tỷ/phiên) · lệnh dự kiến 22 tr = 1% ADV
     ↳ FA: ROE5Y 4.0% · ROE_Min3Y 0.3% · FSCORE 8 · D/E 0.46 · PE 12.91
  • MUA VPB: 700/900 (78%) @ 23,914đ → 16.7M
     ↳ DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 Gordon P/B (ngân hàng): P/B 1.20 vs hợp lý 1.22 (ROE5Y 14.8%, COE 13%/g 5%) — CHEAP [đã validate (bank_compounder_screen)]
     ↳ DD VPB (data 2026-10-23): thanh khoản OK (ADV3T 369.60 tỷ/phiên) · lệnh dự kiến 22 tr = 0% ADV · ⚠ cờ bất thường H [IDIOCRASH] ngày 2026-09-18
     ↳ FA: ROE5Y 14.8% · ROE_Min3Y 8.4% · FSCORE 4 · D/E 7.05 · PE 7.73
  • MUA SCL: 500/700 (71%) @ 32,280đ → 16.1M
     ↳ DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 8L (fallback rộng): 8L rating 2/5, earnings yield 9.8% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
     ↳ DD SCL (data 2026-10-23): thanh khoản OK (ADV3T 4.06 tỷ/phiên) · lệnh dự kiến 22 tr = 1% ADV
     ↳ FA: ROE5Y 13.8% · ROE_Min3Y 10.1% · FSCORE 8 · D/E 0.99 · PE 10.26

ℹ️ _DCF là lăng kính THAM KHẢO (không tham gia quyết định mua/bán): mô hình gộp doanh nghiệp thành 1 dòng tiền FCFE với 1 mức tăng trưởng + 1 lãi suất chiết khấu, rất nhạy với 2 tham số này. Với doanh nghiệp ĐA NGÀNH/HOLDING (mảng khác nhau, kinh tế + rủi ro khác nhau — cần định giá sum-of-the-parts) kết quả có thể KHÔNG CÓ Ý NGHĨA dù trông chính xác; các tên đã biết được đánh dấu '⚠ đa ngành', nhưng danh sách duy trì tay nên không đầy đủ. Nhóm tài chính (ngân hàng/bảo hiểm/chứng khoán) bị loại hẳn → NOT_COMPUTED. Khi NOT_COMPUTED, report nối thêm LĂNG KÍNH THAY THẾ theo ngành (Gordon P/B ngân hàng, P/B chứng khoán, EV/EBITDA cảng-viễn thông, P/B trough vận tải biển, 8L fallback) — độ tin cậy ghi rõ trong ngoặc vuông, cũng THUẦN THAM KHẢO._
ℹ️ _Due-diligence tự động = LỚP THÔNG TIN (thanh khoản/universe/cơ học tín hiệu/cờ bất thường/FA thô/định giá). KHÔNG phải gate chặn lệnh; số từ bq_cache local (trễ tối đa 1 phiên), không dùng làm giá tham chiếu. Có 🔴 cờ đỏ mà vẫn mua → PHẢI ghi `dd_override_reason` trong plan (thiếu = WARN, vẫn thực thi)._

**Tổng giá trị giao dịch: 54.4M / kế hoạch 65.1M (84%)**

⚠️ Không đọc được positions broker (ZaloPay): HTTP 500: authentication failed
❌ [2026-10-26] Không lấy được vị thế broker — KHÔNG tính NAV (tránh đăng số thiếu vị thế).
🛰️ Gate DT5G: 🟢 BÌNH THƯỜNG · candidate CRISIS 14/25 (56%, còn 11 phiên để commit, base giữ từ 2026-10-07, committed NEUTRAL) · P(CRISIS xác nhận|k=14)≈73% [50–93%, n=15] ⚠ mẫu mỏng, tham khảo  [dữ liệu tới 2026-10-26]
   ↳ Nền xấu 20 phiên liền từ 29/09 (6 BEAR + 14 CRISIS, đổi qua lại 1 lần → bộ đếm reset, vẫn NEUTRAL) · VNINDEX −1,0% từ đầu đợt · ngưỡng xem lại: ≥15 phiên và VNINDEX ≤−5,0% — chưa chạm
🧭 Value Radar: 🟢 23.2 RẺ (phân vị 10 năm) · P/E 11.19 (p7) · P/B 1.87 (p23) · spread EY−CCTG 12T +1.54pp (p40)  [dữ liệu tới 2026-10-26]
  ↳ ⓘ thông tin bổ sung, CHƯA qua kiểm định đủ mạnh để dùng cho sizing (0/17 lăng kính qua đa kiểm định) — chỉ để đọc, không phải tín hiệu mua/bán.
💵 Spread định giá: 🔴 EY median 9.27% − lãi vay 12.5% = -3.23pp · chỉ hiển thị, không tác động sizing/gate  [dữ liệu tới 2026-10-26, 323/340 mã có PE>0]
🧲 CAP_SIGNAL advisory (2026-10-23): quiet | EM_dd60=-10.3% VNI_dd60=-4.3% DXY_mom60=0.3% TNX=4.99 | N_clusters=0/10 — ADVISORY THAM KHẢO, KHÔNG phải tín hiệu mua/bán tự động.

📋 **Hit Details (nội bộ, 2026-10-26)** — công thức + giá trị factor thật đằng sau mỗi tín hiệu BAL/LAG hôm nay:
# Hit Details — 2026-10-26


Nguồn: `golive_v23_recommendations_2026-10-26.csv` + raw factor fetch trực tiếp BQ (BAL) / `lag_live_schedule.live_lag_candidates()` (LAG). Công cụ audit thuần — KHÔNG đổi logic lọc/đặt lệnh. Xem `kb/coding_guidelines.md` §29.


## BAL book
_Không có mã BAL FULL/HALF_SIZE hôm nay._


## LAG book (5 mã)


### MCH — LAG / LAG_LO (status=UPCOMING T+3 phiên tới, weight=8.00%)
Formula: `NP_R>=15.0 & prior_n_good>=4 & pa_HL3>=5.0` (pinned R3 LAG spec, entry T+5 sau Release_Date, hold 25 phiên)

| Biến | Giá trị | Ngưỡng | Khớp? |
|---|---|---|---|
| NP_R (%) | 15.06 | >= 15.0 | ✅ |
| prior_n_good | 14 | >= 4 | ✅ |
| pa_HL3 | 10.82 | >= 5.0 | ✅ |
| surprise_B_MA (→ tier) | 0.101 | tier=LAG_HI nếu >0.5 | tier=LAG_LO |
| Release_Date | 2026-10-22 | quarter=2026Q3 | |

_Ứng viên này đã qua thêm 3 gate upstream (không recompute ở đây — xem golive log ngày này): lag_filter_illiquid (ADV≥2 tỷ/phiên), lag_filter_low_rating (8L rating≤3), lag_filter_forensic_banned (không BANNED/forensic)._

### MSR — LAG / LAG_HI (status=UPCOMING T+3 phiên tới, weight=10.00%)
Formula: `NP_R>=15.0 & prior_n_good>=4 & pa_HL3>=5.0` (pinned R3 LAG spec, entry T+5 sau Release_Date, hold 25 phiên)

| Biến | Giá trị | Ngưỡng | Khớp? |
|---|---|---|---|
| NP_R (%) | 41509.73 | >= 15.0 | ✅ |
| prior_n_good | 13 | >= 4 | ✅ |
| pa_HL3 | 8.19 | >= 5.0 | ✅ |
| surprise_B_MA (→ tier) | 2.536 | tier=LAG_HI nếu >0.5 | tier=LAG_HI |
| Release_Date | 2026-10-22 | quarter=2026Q3 | |

_Ứng viên này đã qua thêm 3 gate upstream (không recompute ở đây — xem golive log ngày này): lag_filter_illiquid (ADV≥2 tỷ/phiên), lag_filter_low_rating (8L rating≤3), lag_filter_forensic_banned (không BANNED/forensic)._

### HT1 — LAG / LAG_LO (status=WINDOW_PASSED 2026-10-26, weight=8.00%)
Formula: `NP_R>=15.0 & prior_n_good>=4 & pa_HL3>=5.0` (pinned R3 LAG spec, entry T+5 sau Release_Date, hold 25 phiên)

| Biến | Giá trị | Ngưỡng | Khớp? |
|---|---|---|---|
| NP_R (%) | 16.00 | >= 15.0 | ✅ |
| prior_n_good | 20 | >= 4 | ✅ |
| pa_HL3 | 8.23 | >= 5.0 | ✅ |
| surprise_B_MA (→ tier) | 0.028 | tier=LAG_HI nếu >0.5 | tier=LAG_LO |
| Release_Date | 2026-10-19 | quarter=2026Q3 | |

_Ứng viên này đã qua thêm 3 gate upstream (không recompute ở đây — xem golive log ngày này): lag_filter_illiquid (ADV≥2 tỷ/phiên), lag_filter_low_rating (8L rating≤3), lag_filter_forensic_banned (không BANNED/forensic)._

### SCL — LAG / LAG_HI (status=WINDOW_PASSED 2026-10-26, weight=10.00%)
Formula: `NP_R>=15.0 & prior_n_good>=4 & pa_HL3>=5.0` (pinned R3 LAG spec, entry T+5 sau Release_Date, hold 25 phiên)

| Biến | Giá trị | Ngưỡng | Khớp? |
|---|---|---|---|
| NP_R (%) | 135.97 | >= 15.0 | ✅ |
| prior_n_good | 20 | >= 4 | ✅ |
| pa_HL3 | 7.78 | >= 5.0 | ✅ |
| surprise_B_MA (→ tier) | 0.591 | tier=LAG_HI nếu >0.5 | tier=LAG_HI |
| Release_Date | 2026-10-19 | quarter=2026Q3 | |

_Ứng viên này đã qua thêm 3 gate upstream (không recompute ở đây — xem golive log ngày này): lag_filter_illiquid (ADV≥2 tỷ/phiên), lag_filter_low_rating (8L rating≤3), lag_filter_forensic_banned (không BANNED/forensic)._

### VPB — LAG / LAG_LO (status=WINDOW_PASSED 2026-10-26, weight=8.00%)
Formula: `NP_R>=15.0 & prior_n_good>=4 & pa_HL3>=5.0` (pinned R3 LAG spec, entry T+5 sau Release_Date, hold 25 phiên)

| Biến | Giá trị | Ngưỡng | Khớp? |
|---|---|---|---|
| NP_R (%) | 18.80 | >= 15.0 | ✅ |
| prior_n_good | 23 | >= 4 | ✅ |
| pa_HL3 | 5.55 | >= 5.0 | ✅ |
| surprise_B_MA (→ tier) | 0.160 | tier=LAG_HI nếu >0.5 | tier=LAG_LO |
| Release_Date | 2026-10-19 | quarter=2026Q3 | |

_Ứng viên này đã qua thêm 3 gate upstream (không recompute ở đây — xem golive log ngày này): lag_filter_illiquid (ADV≥2 tỷ/phiên), lag_filter_low_rating (8L rating≤3), lag_filter_forensic_banned (không BANNED/forensic)._
