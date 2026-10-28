📊 **EOD Trading Report — ZaloPay (2026-10-28)**

─────────────────────────────────────────────────
📋 **TÌNH TRẠNG DANH MỤC — ZaloPay (2026-10-28)**
Chiến lược: **V2.4** | Regime: **NEUTRAL** (DT5G) | Park target: **0%** idle cash
⚠️ NAV hôm nay (2026-10-28) CHƯA có trong nav_history_ZaloPay.csv lúc chạy mục này — hiện NAV gần nhất (2026-10-27): **919.9M**, đổi so với ngày trước đó **+0.85%** (KHÔNG PHẢI thay đổi của hôm nay). Số NAV chính thức hôm nay xem mục 💰 NAV cuối report (daily_nav_snapshot.py, chạy sau mục này).
Gate DT5G: ✓ ổn định (NEUTRAL) · không có candidate đang track  [dữ liệu tới 2026-10-28]
Value Radar: 🟢 22.3 RẺ (phân vị 10 năm) · P/E 11.16 (p6) · P/B 1.86 (p21) · spread EY−CCTG 12T +1.56pp (p40)  [dữ liệu tới 2026-10-28]
─────────────────────────────────────────────────

**Cơ cấu danh mục**

| Sleeve | Giá trị | % NAV | Lãi/Lỗ CK | Ghi chú |
|--------|--------:|------:|----------:|---------|
| PARK custom30V (3 mã) | 330.3M | 35.9% | -15.2% | Rebal gần nhất: 2026-08-05 | kế tiếp: ~2026-12-01 (ước tính Q4) |
| LAG (3 mã) | 73.0M | 7.9% | -0.1% | PEAD/earnings drift |
| Discretionary (2 mã) | 35.2M | 3.8% | +3.8% | Fear-buy/special situation |
| Trứng vàng | 469.1M | 51.0% | — | DNSE bond-like (off-book) |
| Cash | 9.5M | 1.0% | 0% | Idle |

ⓘ Tỉ suất từng mã tính trên giá đóng cửa của phiên, đã cộng cổ tức tiền mặt sau thuế; cột giá trị tính trên giá do công ty chứng khoán ghi cuối ngày. Hai giá có thể lệch nhau ở mã giao dịch trên UPCOM, nên giá trị và tỉ suất của cùng một mã không quy đổi trực tiếp sang nhau.

**Chi tiết PARK custom30V (3 mã)**
  DGC 329.0M, -15.23% · MBB 1.0M, -3.95% · VIB 0.3M, +3.99%

**Chi tiết LAG (3 mã)**
  VPB 27.9M, +1.68% — vào 2026-10-26, còn 23 phiên tới hạn cố định T+25 · SCL 22.8M, -3.93% — ĐÃ QUA hạn cố định T+25 (54 phiên từ 2026-08-10) — tới hạn thoát · HT1 22.4M, +1.72% — vào 2026-10-26, còn 23 phiên tới hạn cố định T+25

**Chi tiết Discretionary (2 mã)**
  TV1 25.9M, -0.02% — ⚠️ 51 phiên từ 2026-08-13 — chờ ý kiến PM về exit · DRI 9.3M, +16.49% — ⚠️ 53 phiên từ 2026-08-11 — chờ ý kiến PM về exit

**Corp Action — 7 ngày tới** (mã đang giữ)
Không có corp action trong 7 ngày tới trên mã đang giữ.

**Cờ theo dõi**
- PARK: rổ hiện hành chốt 2026-08-05 (chu kỳ ~quý, kế tiếp ~2026-12-01 (ước tính)).
- LAG: đang giữ 3 mã PEAD/earnings-drift, theo dõi cửa sổ thoát.
- ⚠️ Discretionary: DRI (53p), TV1 (51p) — chờ ý kiến PM về exit
- LAG: 2 candidate đang trong cửa sổ upcoming (chưa vào lệnh).

✅ Đối soát broker: fill thật khớp đúng state nội bộ, không lệch.

✅ Leg 3 (statement DNSE, độc lập với state/dnse_raw): số khớp trùng khớp state nội bộ, không có fill ngoài kế hoạch.
💸 Phí/thuế THẬT theo statement: 13,978đ phí + 9,365đ thuế trên 15.9M giá trị khớp (= 0.0880% giá trị).

Tổng lệnh: **2** (1 mua / 1 bán) | Khớp đủ: 2 | Khớp một phần: 0 | Chưa khớp: 0

| Chiều | Lệnh | Khớp đủ | Khớp thiếu | Chưa khớp | Giá trị |
|-------|:----:|:-------:|:----------:|:---------:|--------:|
| Mua   | 1 | 1 | 0 | 0 | 6.5M |
| Bán   | 1 | 1 | 0 | 0 | 9.4M |

**Chi tiết đáng chú ý:**
  • MUA SCL: 200/200 (100%) @ 32,600đ → 6.5M
     ↳ DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 8L (fallback rộng): 8L rating 2/5, earnings yield 9.1% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
     ↳ DD SCL (data 2026-10-27): thanh khoản OK (ADV3T 4.43 tỷ/phiên) · lệnh dự kiến 7 tr = 0% ADV
     ↳ FA: ROE5Y 13.8% · ROE_Min3Y 10.1% · FSCORE 8 · D/E 0.99 · PE 10.99

ℹ️ _DCF là lăng kính THAM KHẢO (không tham gia quyết định mua/bán): mô hình gộp doanh nghiệp thành 1 dòng tiền FCFE với 1 mức tăng trưởng + 1 lãi suất chiết khấu, rất nhạy với 2 tham số này. Với doanh nghiệp ĐA NGÀNH/HOLDING (mảng khác nhau, kinh tế + rủi ro khác nhau — cần định giá sum-of-the-parts) kết quả có thể KHÔNG CÓ Ý NGHĨA dù trông chính xác; các tên đã biết được đánh dấu '⚠ đa ngành', nhưng danh sách duy trì tay nên không đầy đủ. Nhóm tài chính (ngân hàng/bảo hiểm/chứng khoán) bị loại hẳn → NOT_COMPUTED. Khi NOT_COMPUTED, report nối thêm LĂNG KÍNH THAY THẾ theo ngành (Gordon P/B ngân hàng, P/B chứng khoán, EV/EBITDA cảng-viễn thông, P/B trough vận tải biển, 8L fallback) — độ tin cậy ghi rõ trong ngoặc vuông, cũng THUẦN THAM KHẢO._
ℹ️ _Due-diligence tự động = LỚP THÔNG TIN (thanh khoản/universe/cơ học tín hiệu/cờ bất thường/FA thô/định giá). KHÔNG phải gate chặn lệnh; số từ bq_cache local (trễ tối đa 1 phiên), không dùng làm giá tham chiếu. Có 🔴 cờ đỏ mà vẫn mua → PHẢI ghi `dd_override_reason` trong plan (thiếu = WARN, vẫn thực thi)._

**Tổng giá trị giao dịch: 15.9M / kế hoạch 16.0M (99%)**

💰 **NAV 2026-10-28: 919,931,021 VND** (+3,121 VND, +0.00% so với hôm trước)
   Cổ phiếu 438,350,250 · Tiền mặt 12,340,297 · Nợ margin 0 · Trứng vàng 469,240,474
   Từ go-live: -67,934,546 VND (-6.88%)
   ℹ️ Có 1 khoản biến động tiền chưa đối chiếu xong (lớn nhất 9.360.000 đ); tỉ suất kỳ chứa ngày đó có thể được điều chỉnh.
🛰️ Gate DT5G: ✓ ổn định (NEUTRAL) · không có candidate đang track  [dữ liệu tới 2026-10-28]
🧭 Value Radar: 🟢 22.3 RẺ (phân vị 10 năm) · P/E 11.16 (p6) · P/B 1.86 (p21) · spread EY−CCTG 12T +1.56pp (p40)  [dữ liệu tới 2026-10-28]
  ↳ ⓘ thông tin bổ sung, CHƯA qua kiểm định đủ mạnh để dùng cho sizing (0/17 lăng kính qua đa kiểm định) — chỉ để đọc, không phải tín hiệu mua/bán.
💵 Spread định giá: 🔴 EY median 9.22% − lãi vay 12.5% = -3.28pp · chỉ hiển thị, không tác động sizing/gate  [dữ liệu tới 2026-10-28, 320/338 mã có PE>0]
🧲 CAP_SIGNAL advisory (2026-10-27): quiet | EM_dd60=-9.5% VNI_dd60=-4.9% DXY_mom60=1.5% TNX=4.99 | N_clusters=0/10 — ADVISORY THAM KHẢO, KHÔNG phải tín hiệu mua/bán tự động.

📋 **Hit Details (nội bộ, 2026-10-28)** — công thức + giá trị factor thật đằng sau mỗi tín hiệu BAL/LAG hôm nay:
# Hit Details — 2026-10-28


Nguồn: `golive_v23_recommendations_2026-10-28.csv` + raw factor fetch trực tiếp BQ (BAL) / `lag_live_schedule.live_lag_candidates()` (LAG). Công cụ audit thuần — KHÔNG đổi logic lọc/đặt lệnh. Xem `kb/coding_guidelines.md` §29.


## BAL book
_Không có mã BAL FULL/HALF_SIZE hôm nay._


## LAG book (5 mã)


### MCH — LAG / LAG_LO (status=UPCOMING T+1 phiên tới, weight=8.00%)
Formula: `NP_R>=15.0 & prior_n_good>=4 & pa_HL3>=5.0` (pinned R3 LAG spec, entry T+5 sau Release_Date, hold 25 phiên)

| Biến | Giá trị | Ngưỡng | Khớp? |
|---|---|---|---|
| NP_R (%) | 15.06 | >= 15.0 | ✅ |
| prior_n_good | 14 | >= 4 | ✅ |
| pa_HL3 | 10.82 | >= 5.0 | ✅ |
| surprise_B_MA (→ tier) | 0.101 | tier=LAG_HI nếu >0.5 | tier=LAG_LO |
| Release_Date | 2026-10-22 | quarter=2026Q3 | |

_Ứng viên này đã qua thêm 3 gate upstream (không recompute ở đây — xem golive log ngày này): lag_filter_illiquid (ADV≥2 tỷ/phiên), lag_filter_low_rating (8L rating≤3), lag_filter_forensic_banned (không BANNED/forensic)._

### MSR — LAG / LAG_HI (status=UPCOMING T+1 phiên tới, weight=10.00%)
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
