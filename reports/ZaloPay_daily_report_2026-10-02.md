📊 **EOD Trading Report — ZaloPay (2026-10-02)**

─────────────────────────────────────────────────
📋 **TÌNH TRẠNG DANH MỤC — ZaloPay (2026-10-02)**
Chiến lược: **V2.4** | Regime: **NEUTRAL** (DT5G) | Park target: **0%** idle cash
⚠️ NAV hôm nay (2026-10-02) CHƯA có trong nav_history_ZaloPay.csv lúc chạy mục này — hiện NAV gần nhất (2026-10-01): **951.2M**, đổi so với ngày trước đó **-0.78%** (KHÔNG PHẢI thay đổi của hôm nay). Số NAV chính thức hôm nay xem mục 💰 NAV cuối report (daily_nav_snapshot.py, chạy sau mục này).
Gate DT5G: 🟢 BÌNH THƯỜNG · candidate BEAR 4/10 (40%, còn 6 phiên để commit, base giữ từ 2026-09-29, committed NEUTRAL) · P(BEAR xác nhận|k=4)≈57% [46–68%, n=70]  [dữ liệu tới 2026-10-02]
Value Radar: 🟢 24.4 RẺ (phân vị 10 năm) · P/E 11.18 (p6) · P/B 1.88 (p25) · spread EY−CCTG 6T +1.45pp (p42)  [dữ liệu tới 2026-10-02]
─────────────────────────────────────────────────

**Cơ cấu danh mục**

| Sleeve | Giá trị | % NAV | Lãi/Lỗ CK | Ghi chú |
|--------|--------:|------:|----------:|---------|
| BAL (1 mã) | 23.4M | 2.5% | -6.5% | Momentum V11 + yieldcombo |
| PARK custom30V (11 mã) | 371.2M | 39.0% | -10.6% | Rebal gần nhất: 2026-08-05 | kế tiếp: ~2026-12-01 (ước tính Q4) |
| CAPIT (5 mã) | 184.6M | 19.4% | +7.6% | Bear-washout overflow |
| Discretionary (2 mã) | 58.2M | 6.1% | +12.5% | Fear-buy/special situation |
| Trứng vàng | 147.3M | 15.5% | — | DNSE bond-like (off-book) |
| Cash | 43.3M | 4.6% | 0% | Idle |

**Chi tiết BAL (1 mã)**
  VPI 23.4M, -6.5%

**Chi tiết PARK custom30V (11 mã)**
  DGC 354.0M, -11.0% · VPB 7.2M, +8.8% · LPB 2.2M, -23.4% · TCB 1.8M, +3.3% · HDB 1.7M, +8.1% · CTG 1.5M, -6.8% · MBB 1.0M, -4.7% · BID 1.0M, -5.8% · MSB 0.6M, +4.9% · VIB 0.3M, -1.5% · VIX 0.1M, -8.5%

**Chi tiết CAPIT (5 mã)**
  PVT 49.2M, +37.7% — còn 9 phiên tới hạn cố định T+60 · SIP 36.9M, +4.5% — còn 9 phiên tới hạn cố định T+60 · VNM 35.2M, -0.2% — còn 9 phiên tới hạn cố định T+60 · SAB 32.2M, -2.6% — còn 9 phiên tới hạn cố định T+60 · NCT 31.1M, -3.5% — còn 9 phiên tới hạn cố định T+60

**Chi tiết Discretionary (2 mã)**
  DRI 29.8M, +28.0% — ⚠️ 35 phiên từ 2026-08-11 — chờ ý kiến PM về exit · TV1 28.4M, -0.1% — ⚠️ 33 phiên từ 2026-08-13 — chờ ý kiến PM về exit

**Corp Action — 7 ngày tới** (mã đang giữ)
Không có corp action trong 7 ngày tới trên mã đang giữ.

**Cờ theo dõi**
- PARK: rổ hiện hành chốt 2026-08-05 (chu kỳ ~quý, kế tiếp ~2026-12-01 (ước tính)).
- ⚠️ Discretionary: DRI (35p), TV1 (33p) — chờ ý kiến PM về exit
- CAPIT: 5 mã đang trong episode overflow — còn 9 phiên tới hạn cố định T+60.

✅ Đối soát broker: fill thật khớp đúng state nội bộ, không lệch.

✅ Leg 3 (statement DNSE, độc lập với state/dnse_raw): số khớp trùng khớp state nội bộ, không có fill ngoài kế hoạch.
💸 Phí/thuế THẬT theo statement: 118,889đ phí + 223,090đ thuế trên 123.1M giá trị khớp (= 0.0966% giá trị).

Tổng lệnh: **16** (0 mua / 16 bán) | Khớp đủ: 16 | Khớp một phần: 0 | Chưa khớp: 0

| Chiều | Lệnh | Khớp đủ | Khớp thiếu | Chưa khớp | Giá trị |
|-------|:----:|:-------:|:----------:|:---------:|--------:|
| Bán   | 16 | 16 | 0 | 0 | 123.1M |


**Tổng giá trị giao dịch: 123.1M / kế hoạch 123.4M (100%)**

⚠️ [2026-10-02] corp_action_gate_v2 KHÔNG xác nhận được lịch corp-action: thiếu/không đọc được corp_action_daily_2026-10-02.json — gate KHÔNG biết mã nào có sự kiện tối nay (nhánh KHỐI LƯỢNG vẫn chạy; nhánh cổ tức tiền mặt và việc gán tỉ lệ thực hiện cho phần dư KL đều TẮT).
💰 **NAV 2026-10-02: 950,434,410 VND** (-748,444 VND, -0.08% so với hôm trước)
   Cổ phiếu 637,110,200 · Tiền mặt 147,523,724 · Nợ margin 0 · Trứng vàng 165,800,486
   Từ go-live: -49,565,590 VND (-4.96%)
🛰️ Gate DT5G: 🟢 BÌNH THƯỜNG · candidate BEAR 4/10 (40%, còn 6 phiên để commit, base giữ từ 2026-09-29, committed NEUTRAL) · P(BEAR xác nhận|k=4)≈57% [46–68%, n=70]  [dữ liệu tới 2026-10-02]
🧭 Value Radar: 🟢 24.4 RẺ (phân vị 10 năm) · P/E 11.18 (p6) · P/B 1.88 (p25) · spread EY−CCTG 6T +1.45pp (p42)  [dữ liệu tới 2026-10-02]
  ↳ ⓘ thông tin bổ sung, CHƯA qua kiểm định đủ mạnh để dùng cho sizing (0/17 lăng kính qua đa kiểm định) — chỉ để đọc, không phải tín hiệu mua/bán.
💵 Spread định giá: 🔴 EY median 9.54% − lãi vay 12.5% = -2.96pp · chỉ hiển thị, không tác động sizing/gate  [dữ liệu tới 2026-10-02, 332/351 mã có PE>0]
🧲 CAP_SIGNAL advisory (2026-10-01): quiet | EM_dd60=-3.3% VNI_dd60=-5.6% DXY_mom60=1.2% TNX=5.24 | N_clusters=0/10 — ADVISORY THAM KHẢO, KHÔNG phải tín hiệu mua/bán tự động.

📋 **Hit Details (nội bộ, 2026-10-02)** — công thức + giá trị factor thật đằng sau mỗi tín hiệu BAL/LAG hôm nay:
# Hit Details — 2026-10-02


Nguồn: `golive_v23_recommendations_2026-10-02.csv` + raw factor fetch trực tiếp BQ (BAL) / `lag_live_schedule.live_lag_candidates()` (LAG). Công cụ audit thuần — KHÔNG đổi logic lọc/đặt lệnh. Xem `kb/coding_guidelines.md` §29.


## BAL book
_Không có mã BAL FULL/HALF_SIZE hôm nay._


## LAG book
_Không có entry LAG upcoming/recent hôm nay._
