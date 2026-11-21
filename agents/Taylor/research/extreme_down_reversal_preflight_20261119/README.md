# Pre-flight #5 — đảo chiều sau ngày giảm cực đoan / đóng sát sàn (daily 2014+)
**Verdict: NO-GO. DỪNG, không viết backtest.** (Job Taylor_20261119_052908; chưa qua quant-skeptic.)

## Lý do
1. **Không dựng được sàn đáng tin.** Không có cột sàn/exchange (`new_listings.csv` cột exchange rỗng). Băng suy từ max|r| 250 phiên: chỉ ~38–47% mã-ngày rơi vào băng ~7% (HOSE-like) mỗi năm, ~15–20% rơi vùng 7–9,5%/10–14,5% (mơ hồ). Trong các ngày r≤−6%, chỉ 24–59% nằm trong ±0,4pp của −7%. Bậc giá (tick) và mốc đổi biên độ HOSE theo thời kỳ **không tra được offline và chưa đối chiếu** — tôi không dám khẳng định. "≤3 tick trên sàn" vì thế chỉ xấp xỉ bằng ngưỡng % trên băng suy ra.
2. **Thiếu N độc lập.** D1 (đóng ≤−6,4%, băng 7%, ngày broad ≥10 mã): IS **14 cụm**, OOS 49 cụm. Tiêu chí ≥30/era trượt ở IS. Nới k=1 (không còn là "bán tháo diện rộng") thì IS 60/OOS 45 nhưng vẫn không đủ DSR.
3. **Power** (`rnd_preflight_power.py --n-rule per-event`, mean 150 bps, 6 trial, history ≤12,9 năm; SD cụm lấy từ mẫu):

| Cấu hình | Era | Cụm | Sự kiện | SD cụm (bps) | DSR hiện tại | N cần cho DSR .95 | Verdict |
|---|---|---|---|---|---|---|---|
| D1, k≥10 | IS | 14 | 351 | 499 | 0,43 | 99 | **NO-GO** |
| D1, k≥10 | OOS | 49 | 4408 | 447 | 0,84 | 80 | MARGINAL |
| D1, k≥10 | gộp | 63 | 4759 | 460 | 0,89 | 85 (trần 63) | **NO-GO** |
| D1, k≥1 | IS | 60 | 1481 | 582 | 0,75 | 134 (trần 129) | NO-GO |
| D1, k≥1 | OOS | 45 | 5963 | 444 | 0,82 | 79 | MARGINAL |
| D3, k≥20 | IS | 13 | 508 | 470 | 0,44 | 89 | NO-GO |
Sharpe/cụm hiệu dụng quá thấp: SD cụm ~450–580 bps so với đích 150 bps ⇒ cần ≥~70–100 cụm, IS chỉ có 14 (hoặc 60 nếu bỏ điều kiện diện rộng). MDE hiện tại: Sharpe năm ≥1,34 (IS D1 k≥10).

## Caveat
- PREREG viết sau thăm dò đếm (đã ghi trong PREREG.md); chỉ lấy đếm + SD, không đọc mean excess.
- Cụm theo ngày lịch ≤7 ngày chồng với episode CAPIT; chưa chạy cổng biodiversity (không cần vì NO-GO).
- Universe_pit + GTGD>2 tỷ là lọc sơ bộ; ex-date có thể làm r sai ở vài sự kiện (Price chưa điều chỉnh).
- Prior ta-schools NO-GO ("bắt đáy") không bị đảo; không có lý do dựng phép thử.
Files: pf_probe.py (nạp + phân phối r), pf2.py (băng suy), pf3.py (cụm), pf_counts.json (đếm thô), PREREG.md(+md5).
