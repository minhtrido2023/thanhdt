---
name: Liquidity filter dùng median, không dùng mean
description: Khi filter thanh khoản cổ phiếu VN, dùng Volume_3M_P50 (hoặc Volume_1M_P50 nếu có) × Close, không dùng Volume_1M (mean) — outlier 1-2 ngày volume cao có thể che giấu cổ phiếu illiquid
type: feedback
originSessionId: 83f7db02-996e-45e7-8368-3e4ec45d6182
---
Khi filter universe theo thanh khoản, dùng **median** không dùng **mean**:
- `Volume_3M_P50 * Close` (có trên `tav2_bq.ticker`) — dùng được full history
- `Volume_1M_P50 * Close` (chỉ có trên `tav2_bq.ticker_1m` và `ticker_prune`) — dùng cho live screening

**Why:**
- Volume_1M (mean daily 1M) bị skew bởi 1-2 ngày volume cực lớn (ví dụ block trade, news event) → false positive cho illiquid stocks
- Ví dụ: SMB(0.51B P50 vs 0.73B mean), VGR(0.08B P50 vs 0.92B mean) — mean cho thấy "qualified" nhưng median thực tế không trade được 1B/ngày

**How to apply:**
- SQL filter: `t.Volume_3M_P50 * t.Close >= 1e9` (1 tỷ VND/ngày median)
- Cho live screening hôm nay, query thêm current Volume_3M_P50 × Close để loại tickers đã giảm thanh khoản từ thời điểm rating
- Threshold 1B là minimum acceptable; có thể lên 2-5B cho danh mục lớn
