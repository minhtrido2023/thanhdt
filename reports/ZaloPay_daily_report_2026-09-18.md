📊 **EOD Trading Report — ZaloPay (2026-09-18)**
✅ Đối soát broker: fill thật khớp đúng state nội bộ, không lệch.

✅ Leg 3 (statement DNSE, độc lập với state/dnse_raw): số khớp trùng khớp state nội bộ, không có fill ngoài kế hoạch.
💸 Phí/thuế THẬT theo statement: 18,216đ phí + 0đ thuế trên 18.8M giá trị khớp (= 0.0970% giá trị).

Tổng lệnh: **1** (1 mua / 0 bán) | Khớp đủ: 1 | Khớp một phần: 0 | Chưa khớp: 0

• MUA VPI: 300/300 (100%) @ 62,633đ → 18.8M
   ↳ DCF: NOT_COMPUTED (CF_OA_3Y <= 0 (operating cash gate fails) — DCF not meaningful) → thay thế: 8L (fallback rộng): 8L rating 4/5, earnings yield 1.8% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
   ↳ DD VPI (data 2026-09-17): thanh khoản OK (ADV3T 107.49 tỷ/phiên) · ⚠ cờ chất lượng FLOOR_FAIL · lệnh dự kiến 19 tr = 0% ADV
   ↳ FA: ROE5Y 11.1% · ROE_Min3Y 7.6% · FSCORE 4 · D/E 1.76 · PE 55.17

ℹ️ _DCF là lăng kính THAM KHẢO (không tham gia quyết định mua/bán): mô hình gộp doanh nghiệp thành 1 dòng tiền FCFE với 1 mức tăng trưởng + 1 lãi suất chiết khấu, rất nhạy với 2 tham số này. Với doanh nghiệp ĐA NGÀNH/HOLDING (mảng khác nhau, kinh tế + rủi ro khác nhau — cần định giá sum-of-the-parts) kết quả có thể KHÔNG CÓ Ý NGHĨA dù trông chính xác; các tên đã biết được đánh dấu '⚠ đa ngành', nhưng danh sách duy trì tay nên không đầy đủ. Nhóm tài chính (ngân hàng/bảo hiểm/chứng khoán) bị loại hẳn → NOT_COMPUTED. Khi NOT_COMPUTED, report nối thêm LĂNG KÍNH THAY THẾ theo ngành (Gordon P/B ngân hàng, P/B chứng khoán, EV/EBITDA cảng-viễn thông, P/B trough vận tải biển, 8L fallback) — độ tin cậy ghi rõ trong ngoặc vuông, cũng THUẦN THAM KHẢO._
ℹ️ _Due-diligence tự động = LỚP THÔNG TIN (thanh khoản/universe/cơ học tín hiệu/cờ bất thường/FA thô/định giá). KHÔNG phải gate chặn lệnh; số từ bq_cache local (trễ tối đa 1 phiên), không dùng làm giá tham chiếu. Có 🔴 cờ đỏ mà vẫn mua → PHẢI ghi `dd_override_reason` trong plan (thiếu = WARN, vẫn thực thi)._

**Tổng giá trị giao dịch: 18.8M / kế hoạch 18.9M (99%)**

💰 **NAV 2026-09-18: 958,732,611 VND** (+5,415,535 VND, +0.57% so với hôm trước)
   Cổ phiếu 862,791,700 · Tiền mặt 88,125,046 · Nợ margin 0 · Trứng vàng 7,815,865
   Từ go-live: -41,267,389 VND (-4.13%)
🛰️ Gate DT5G: ✓ ổn định (NEUTRAL) · không có candidate đang track  [dữ liệu tới 2026-09-18]
🧭 Value Radar: 🟢 23.4 RẺ (phân vị 10 năm) · P/E 11.53 (p8) · P/B 1.94 (p31) · spread EY−tiết kiệm +1.87pp (p31)  [dữ liệu tới 2026-09-18]
  ↳ ⓘ thông tin bổ sung, CHƯA qua kiểm định đủ mạnh để dùng cho sizing (0/17 lăng kính qua đa kiểm định) — chỉ để đọc, không phải tín hiệu mua/bán.
💵 Spread định giá: 🔴 EY median 9.49% − lãi vay 12.5% = -3.01pp · chỉ hiển thị, không tác động sizing/gate  [dữ liệu tới 2026-09-18, 335/354 mã có PE>0]
🧲 CAP_SIGNAL advisory (2026-09-17): quiet | EM_dd60=-6.0% VNI_dd60=-2.9% DXY_mom60=0.1% TNX=4.95 | N_clusters=0/10 — ADVISORY THAM KHẢO, KHÔNG phải tín hiệu mua/bán tự động.

📋 **Hit Details (nội bộ, 2026-09-18)** — công thức + giá trị factor thật đằng sau mỗi tín hiệu BAL/LAG hôm nay:
# Hit Details — 2026-09-18


Nguồn: `golive_v23_recommendations_2026-09-18.csv` + raw factor fetch trực tiếp BQ (BAL) / `lag_live_schedule.live_lag_candidates()` (LAG). Công cụ audit thuần — KHÔNG đổi logic lọc/đặt lệnh. Xem `kb/coding_guidelines.md` §29.


## BAL book (1 mã)


### VPI — BAL / RE_BACKLOG_BUY (status=FULL, weight=10.00%)
ta (CSV, production) = **126.0** | ta (recomputed here) = **126**  ✓ khớp

| Điều kiện | Công thức | Điểm | Khớp? | Giá trị thật |
|---|---|---|---|---|
| RSI>0.50 | `D_RSI > 0.50` | +25 | ✅ | D_RSI=0.6226673407012446 |
| uptrend | `Close>MA50>MA200` | +25 | ✅ | Close=62900.0 MA50=58182.4 MA200=54530.9 |
| MACD>0 | `D_MACDdiff > 0` | +15 | ✅ | D_MACDdiff=174.48926870941864 |
| Close>MA20 | `Close > MA20` | +15 | ✅ | Close=62900.0 MA20=60474.0 |
| VNI-hot | `VNINDEX RSI_max3m > 0.65` | +10 | ✅ | vni_rsi_max3m=0.6764395162075593 |
| NP-surge-YoY | `NP_P0 > NP_P4*1.5 & NP_P4>0` | +8 | ✅ | NP_P0=129804009720.0 NP_P4=3904359336.0 |
| sector-favored | `sector(ICB) in (8,9)` | +5 | ✅ | sector=8 |
| MA50-rising | `MA50_T1>0 & MA50>MA50_T1` | +5 | ✅ | MA50=58182.4 MA50_T1=58043.8 |
| NP-surge-QoQ | `NP_P0 > NP_P1*1.2 & NP_P1>0` | +8 | ✅ | NP_P0=129804009720.0 NP_P1=26895380753.0 |
| FA-D-financials | `sector=8 & fa_tier='D'` | +10 | ✅ | sector=8 fa_tier=D |

_8L rating (fa_ratings_8l, để tham khảo weight-halving BEAR/CRISIS): 4_


## LAG book
_Không có entry LAG upcoming/recent hôm nay._
