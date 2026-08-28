---
kind: script-output
status: CANONICAL
source: data/power_lens.csv
group: rating-8l
note: refreshed 2026-08-28 (job Taylor_20260828_081256) — was stale ~3 months (mtime 05-31), no registry entry, no cron; đăng ký lần đầu sau audit phát hiện lỗ hổng
writer: power_lens.py (repo root) — pull vnstock finance.ratio per ticker, ad-hoc chạy tay
---

# data/power_lens.csv (+ power_lens.md — cùng builder, cùng lần chạy)

**Status: CANONICAL (quant proxy sector lens, refresh THỦ CÔNG)**

## Là gì
Sector lens ICB 7535 (điện/power/utility, universe 49 mã) — debt-paydown lifecycle: gate
PRE_INFLECTION (D/E giảm, CFO covering) / MID_CYCLE / MATURE_YIELD dựa trên D/E, CFO, PB, ROE.
Feed vào `rating_8l.py` (route POWER, dòng ~534) làm sector lens override cho ROIC-based scoring
(power là ngành vốn nặng, ROIC thô không phản ánh đúng chu kỳ trả nợ).

## Ai ghi / cadence
`power_lens.py` (repo root, executable) — kéo `finance.ratio(period="quarter")` từ **vnstock/VCI**
(nguồn ngoài, KHÔNG phải BQ `ticker_financial`) cho từng mã trong danh sách 49 mã hardcode trong
script. **Ad-hoc, không cron** — refresh bằng tay khi cần, không có lịch tự động.

## Bẫy
- Nguồn dữ liệu là **vnstock/VCI qua API guest, rate-limit 20 req/phút** — script tự retry+sleep
  nhưng vẫn có thể fail hàng loạt nếu vnstock đổi schema (xem `bank_lens_v3.md` — CÙNG thư viện,
  đang BLOCKED-STALE vì lỗi này ngày 2026-08-28).
- Không có cron ⇒ **im lặng trở nên stale** nếu không ai chủ động chạy lại — đây chính là lỗ hổng
  đã cắn thật (3 tháng không refresh, không ai biết) trước khi entry này được tạo. Kiểm mtime
  trước khi trích dẫn số trong report/backtest.
- `rating_8l.py` fail-safe khi thiếu file (route vẫn chạy, chỉ mất sector lens override) — KHÔNG
  crash, nên staleness không tự lộ ra qua lỗi chạy — phải tự kiểm bằng `data_registry_audit.sh`
  Section E hoặc B.
