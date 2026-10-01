📊 **EOD Trading Report — ZaloPay (2026-10-01)**

─────────────────────────────────────────────────
📋 **TÌNH TRẠNG DANH MỤC — ZaloPay (2026-10-01)**
Chiến lược: **V2.4** | Regime: **NEUTRAL** (DT5G) | Park target: **0%** idle cash
⚠️ NAV hôm nay (2026-10-01) CHƯA có trong nav_history_ZaloPay.csv lúc chạy mục này — hiện NAV gần nhất (2026-09-30): **958.7M**, đổi so với ngày trước đó **-0.68%** (KHÔNG PHẢI thay đổi của hôm nay). Số NAV chính thức hôm nay xem mục 💰 NAV cuối report (daily_nav_snapshot.py, chạy sau mục này).
Gate DT5G: 🟢 BÌNH THƯỜNG · candidate BEAR 3/10 (30%, còn 7 phiên để commit, base giữ từ 2026-09-29, committed NEUTRAL) · P(BEAR xác nhận|k=3)≈49% [39–60%, n=81]  [dữ liệu tới 2026-10-01]
Value Radar: 🟢 26.1 RẺ (phân vị 10 năm) · P/E 11.29 (p7) · P/B 1.91 (p28) · spread EY−CCTG 6T +1.36pp (p43)  [dữ liệu tới 2026-10-01]
─────────────────────────────────────────────────

**Cơ cấu danh mục**

| Sleeve | Giá trị | % NAV | Lãi/Lỗ CK | Ghi chú |
|--------|--------:|------:|----------:|---------|
| BAL (2 mã) | 43.3M | 4.5% | -3.2% | Momentum V11 + yieldcombo |
| PARK custom30V (16 mã) | 469.0M | 48.9% | -8.9% | Rebal gần nhất: 2026-08-05 | kế tiếp: ~2026-12-01 (ước tính Q4) |
| LAG (1 mã) | 5.8M | 0.6% | +22.5% | PEAD/earnings drift |
| CAPIT (5 mã) | 184.6M | 19.3% | +7.6% | Bear-washout overflow |
| Discretionary (2 mã) | 58.2M | 6.1% | +12.5% | Fear-buy/special situation |
| Trứng vàng | 102.2M | 10.7% | — | DNSE bond-like (off-book) |
| Cash | 65.4M | 6.8% | 0% | Idle |

**Chi tiết BAL (2 mã)**
  VPI 23.4M, -6.5% · CSV 19.9M, +1.0%

**Chi tiết PARK custom30V (16 mã)**
  DGC 354.0M, -11.0% · VPB 28.2M, +9.8% · VHM 13.7M, -8.0% · BID 11.6M, -5.5% · VCB 11.5M, -4.8% · CTG 10.5M, -6.5% · TCB 8.4M, +4.4% · MBB 6.9M, -4.8% · HPG 6.0M, -9.7% · HDB 4.5M, +8.1% · ACB 4.2M, -7.0% · VIB 2.9M, -1.5% · SHB 2.3M, -6.2% · LPB 2.2M, -23.4% · MSB 2.0M, +4.9% · VIX 0.1M, -8.5%

**Chi tiết LAG (1 mã)**
  SCL 5.8M, +22.5% — ĐÃ QUA hạn cố định T+25 (35 phiên từ 2026-08-10) — tới hạn thoát

**Chi tiết CAPIT (5 mã)**
  PVT 49.2M, +37.7% — còn 10 phiên tới hạn cố định T+60 · SIP 36.9M, +4.5% — còn 10 phiên tới hạn cố định T+60 · VNM 35.2M, -0.2% — còn 10 phiên tới hạn cố định T+60 · SAB 32.2M, -2.6% — còn 10 phiên tới hạn cố định T+60 · NCT 31.1M, -3.5% — còn 10 phiên tới hạn cố định T+60

**Chi tiết Discretionary (2 mã)**
  DRI 29.8M, +28.0% — ⚠️ 34 phiên từ 2026-08-11 — chờ ý kiến PM về exit · TV1 28.4M, -0.1% — ⚠️ 32 phiên từ 2026-08-13 — chờ ý kiến PM về exit

**Corp Action — 7 ngày tới** (mã đang giữ)
| Mã | Sự kiện | Ngày | Tác động dự kiến |
|----|---------|------|-------------------|
| BID | AIS | 2026-10-05 | BID - Niêm yết bổ sung 498.164.263 cổ phiếu |

**Cờ theo dõi**
- PARK: rổ hiện hành chốt 2026-08-05 (chu kỳ ~quý, kế tiếp ~2026-12-01 (ước tính)).
- LAG: đang giữ 1 mã PEAD/earnings-drift, theo dõi cửa sổ thoát.
- ⚠️ Discretionary: DRI (34p), TV1 (32p) — chờ ý kiến PM về exit
- CAPIT: 5 mã đang trong episode overflow — còn 10 phiên tới hạn cố định T+60.

✅ Đối soát broker: fill thật khớp đúng state nội bộ, không lệch.

✅ Leg 3 (statement DNSE, độc lập với state/dnse_raw): số khớp trùng khớp state nội bộ, không có fill ngoài kế hoạch.
📉 **Broker xác nhận KHỚP THIẾU so với kế hoạch** — chưa đạt mục tiêu, KHÔNG được đọc là "đã bán đủ" (§27):
  • SCL (bán): chỉ khớp 800/1,000 đặt (80%) — phần thiếu 200cp
💸 Phí/thuế THẬT theo statement: 20,169đ phí + 22,920đ thuế trên 22.9M giá trị khớp (= 0.0880% giá trị).

Tổng lệnh: **1** (0 mua / 1 bán) | Khớp đủ: 0 | Khớp một phần: 1 | Chưa khớp: 0

| Chiều | Lệnh | Khớp đủ | Khớp thiếu | Chưa khớp | Giá trị |
|-------|:----:|:-------:|:----------:|:---------:|--------:|
| Bán   | 1 | 0 | 1 | 0 | 22.9M |

**Chi tiết đáng chú ý:**
  • BÁN SCL: 800/1,000 (80%) @ 28,650đ → 22.9M


**Tổng giá trị giao dịch: 22.9M / kế hoạch 28.9M (79%)**

💰 **NAV 2026-10-01: 951,182,854 VND** (-7,483,425 VND, -0.78% so với hôm trước)
   Cổ phiếu 760,639,700 · Tiền mặt 43,287,349 · Nợ margin 0 · Trứng vàng 147,255,805
   Từ go-live: -48,817,146 VND (-4.88%)
🛰️ Gate DT5G: 🟢 BÌNH THƯỜNG · candidate BEAR 3/10 (30%, còn 7 phiên để commit, base giữ từ 2026-09-29, committed NEUTRAL) · P(BEAR xác nhận|k=3)≈49% [39–60%, n=81]  [dữ liệu tới 2026-10-01]
🧭 Value Radar: 🟢 26.1 RẺ (phân vị 10 năm) · P/E 11.29 (p7) · P/B 1.91 (p28) · spread EY−CCTG 6T +1.36pp (p43)  [dữ liệu tới 2026-10-01]
  ↳ ⓘ thông tin bổ sung, CHƯA qua kiểm định đủ mạnh để dùng cho sizing (0/17 lăng kính qua đa kiểm định) — chỉ để đọc, không phải tín hiệu mua/bán.
💵 Spread định giá: 🔴 EY median 9.37% − lãi vay 12.5% = -3.13pp · chỉ hiển thị, không tác động sizing/gate  [dữ liệu tới 2026-10-01, 332/349 mã có PE>0]
🧲 CAP_SIGNAL advisory (2026-09-30): quiet | EM_dd60=-3.3% VNI_dd60=-5.2% DXY_mom60=0.1% TNX=5.29 | N_clusters=0/10 — ADVISORY THAM KHẢO, KHÔNG phải tín hiệu mua/bán tự động.

📋 **Hit Details (nội bộ, 2026-10-01)** — công thức + giá trị factor thật đằng sau mỗi tín hiệu BAL/LAG hôm nay:
# Hit Details — 2026-10-01


Nguồn: `golive_v23_recommendations_2026-10-01.csv` + raw factor fetch trực tiếp BQ (BAL) / `lag_live_schedule.live_lag_candidates()` (LAG). Công cụ audit thuần — KHÔNG đổi logic lọc/đặt lệnh. Xem `kb/coding_guidelines.md` §29.


## BAL book
_Không có mã BAL FULL/HALF_SIZE hôm nay._


## LAG book
_Không có entry LAG upcoming/recent hôm nay._
