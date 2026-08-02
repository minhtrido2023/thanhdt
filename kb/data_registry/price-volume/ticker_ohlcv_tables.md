---
kind: bigquery-table
status: CANONICAL
source: tav2_bq.ticker / ticker_1m / ticker_prune
group: price-volume
scope: lịch sử (backtest/nghiên cứu) — TRAP nếu dùng cho dữ liệu TRONG NGÀY
writer: Ingest ETL
---

# tav2_bq.ticker / ticker_1m / ticker_prune

**Status: CANONICAL cho lịch sử**

## Là gì
OHLCV + chỉ báo, backtest/nghiên cứu.

## Ai ghi / cadence
Ingest ETL (đã xác nhận 2026-07-10: `ticker`/`ticker_prune` của HÔM NAY đã đầy đủ trước 18:45 ICT,
không cần đợi tới đêm).

## Universe size — thay đổi pipeline từ T6/2026

**Xác minh 2026-08-02 (Winston, job Winston_20260802_015657):**

`tav2_bq.ticker` thu hẹp từ **~1252 ticker/ngày → ~820-900 ticker/ngày** bắt đầu từ T6/2026 (2 bước):
- **2026-06-19**: drop ~100 mã (1252 → 1149) — loại batch ticker suspended/0-volume kéo dài
- **2026-06-25**: drop thêm ~300 mã (1140 → 838) — loại thêm ticker ít thanh khoản

**Nguyên nhân (xác minh qua BQ trực tiếp):** pipeline upstream (Ingest ETL, quản lý bởi owner BQ)
đổi từ "carry-forward mọi ticker đã biết" sang "chỉ include ticker có data thật cho ngày đó" — nghĩa
là ticker không giao dịch hoặc không có data fetch được từ sàn sẽ không xuất hiện trong bảng ngày đó.
Bằng chứng: BVB (3-4M vol/ngày) biến mất 9-20/7 rồi tái xuất 21/7 → đây là upstream data gap, không
phải filter cứng theo thanh khoản. ACE xuất hiện đúng ngày có Volume > 0. BCG (0 vol liên tục, bị
suspend) biến mất vĩnh viễn.

**Tác động đến fleet (THẤP — không cần action):**
- Taylor đã confirm (job Taylor_20260802_014330): 401 mã biến mất khỏi snapshot 2026-05-15 vs 2026-07-31,
  thanh khoản cao nhất chỉ 0.28 tỷ/ngày → **LIQ_MIN 3B và investment universe KHÔNG BỊ ẢNH HƯỞNG**.
- `ticker_prune` (~216 mã quality) **hoàn toàn ổn định** qua giai đoạn này.
- DT5G pipeline đọc từ `vnindex_5state_dt5g_live` → **KHÔNG ẢNH HƯỞNG**.
- Cẩn thận: nghiên cứu dùng `COUNT(DISTINCT ticker)` trên `tav2_bq.ticker` làm proxy breadth sẽ thấy
  con số thấp hơn thật từ T6/2026 — dùng `universe_pit` hoặc `ticker_prune` làm breadth universe thay thế.

## Bẫy
**TRAP nếu dùng cho dữ liệu TRONG NGÀY**: BQ cache local (`data/bq_cache`) chỉ sync 23:45 ICT — script
chạy trước giờ đó đọc cache sẽ luôn trễ 1 ngày (sự cố thật 2026-07-09, DollarBill BID/MBB lệch +5.7%).
BQ TABLE gốc (không qua cache) có thể fresh sớm hơn nhiều — đừng lẫn 2 khái niệm "BQ" và "BQ cache
local".
