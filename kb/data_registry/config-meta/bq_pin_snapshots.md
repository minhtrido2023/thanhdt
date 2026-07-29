---
kind: bigquery-dataset
status: CANONICAL
source: lithe-record-440915-m9.tav2_pin
group: config-meta
writer: mike/bin/bq_monthly_pin.sh (cron 22:00 ICT ngày 1 hàng tháng) — KHÔNG ai khác được ghi
purpose: audit trail vintage + phát hiện restate âm thầm
created: 2026-07-29 (job Winston_20260729_152037)
---

# `tav2_pin` — kho PIN (BQ snapshot) hàng tháng

**Status: CANONICAL** — đây là nơi DUY NHẤT lưu vintage cũ của các bảng production.

## Là gì
Mỗi tháng một bản **BigQuery table SNAPSHOT** (read-only, `bq cp --snapshot`) của 11 bảng dễ bị
restate, đặt tên `<table>_pin_YYYYMM` với `YYYYMM` = tháng ICT lúc CHỤP. Cron chạy ngày 1 lúc
22:00, nên `ticker_pin_202608` = "trạng thái `ticker` đầu tháng 2026-08" = đúng thứ mà mọi phân
tích chạy trong tháng 8 đang đọc.

Bảng được pin: `ticker`, `ticker_prune`, `ticker_financial`, `ticker_1m`, `universe_pit`,
`universe_pit_quality`, `vnindex_5state_dt5g_live`, `vnindex_5state`,
`vnindex_5state_tam_quan_v34b_clean`, `fa_ratings_8l`, `fa_ratings`.

## Vì sao tồn tại
BQ time-travel của project này **bị xoá mỗi sáng**, nên một vintage cũ KHÔNG thể lấy lại sau khi
bảng bị ghi đè. Ngày 2026-07-29 phát hiện ba lần restate âm thầm chỉ trong một ngày — `ticker_prune`
bị TRUNCATE+rebuild lúc 07:27 (58 mã biến mất khỏi TOÀN BỘ lịch sử), `VNINDEX_PE` backfill ngược
tới 2006, corp-action restate ~2-3%/tuần trên `ticker`/`ticker_financial` — **cả ba đều do tình cờ
thấy**. Mọi kết quả backtest đã "pin" (R3, DT5G audit…) neo vào một snapshot không ai tái tạo được.
Dataset này chấm dứt cả hai vấn đề: có bản sao thật để tra, và có diff tự động thay vì trông chờ may rủi.

## Cách dùng
Truy vấn y như bảng thường, giữ nguyên schema/kiểu dữ liệu:
```sql
SELECT * FROM `lithe-record-440915-m9.tav2_pin.ticker_pin_202607` WHERE ticker = 'VNM'
```
Muốn tái tạo một kết quả cũ → đọc pin của đúng tháng đã chạy, KHÔNG đọc bảng live.

## Cảnh báo tự động
Mỗi lần pin, script diff pin mới vs pin tháng trước **theo từng `ticker`** (theo năm với các bảng
state không có cột ticker), chỉ trên cửa sổ chồng lấn `time <= MAX(time)` của pin cũ (dòng mới hơn
là tăng trưởng hợp lệ, không phải restate). Fingerprint = `BIT_XOR(FARM_FINGERPRINT(TO_JSON_STRING(
STRUCT(<cột chung>))))` — chỉ tính trên cột có ở CẢ HAI pin, để một cột MỚI thêm không làm mọi dòng
bị gắn nhãn "restate" giả; cột thêm/xoá báo riêng như schema drift.
- **CRITICAL**: >5% nhóm biến mất khỏi lịch sử, >5% dòng dịch trong cửa sổ chồng lấn, `MIN(time)`
  tiến lên (lịch sử bị cắt đầu), cột bị xoá, hoặc bảng nguồn biến mất.
- **WARN**: 1-5% nhóm biến mất, >25% nhóm bị restate, hoặc cột mới thêm.
- **OK**: restate thường lệ / tăng trưởng thuần.
Báo cáo: `mike/logs/bq_pin/pin_YYYYMM.md` + `.json`; Discord Trading Daily nhận 1 dòng MỖI THÁNG kể
cả khi sạch (im lặng = không phân biệt được với cron chết), `notify.sh` chỉ bị đánh thức khi WARN/CRITICAL.

## Bẫy
- **KHÔNG bao giờ ghi/xoá thủ công trong dataset này.** Snapshot là bằng chứng audit; xoá một pin =
  huỷ bản sao DUY NHẤT của một vintage (BQ time-travel không cứu được).
- `ticker_1m_pin_*` được chụp nhưng **cố ý KHÔNG diff** — bảng rolling ~1 tháng, "dòng biến mất"
  là hành vi bình thường của nó, diff sẽ chỉ tạo tiếng ồn.
- Pin là ảnh chụp một THỜI ĐIỂM. `ticker_prune` bị rebuild lúc ~07:27 hàng ngày, nên cron cố ý chạy
  22:00 chứ không phải buổi sáng — pin rơi giữa `TRUNCATE...INSERT` sẽ chụp bảng rỗng.
- Retention hiện tại = **giữ tất cả** (11 pin = 6,27 GB, snapshot chỉ tính phí phần byte lệch so
  bảng gốc). Chỉ xét lại khi `bq_monthly_pin.py --cost` báo vượt ~100 GB — và khi đó phải hỏi
  user/Mike, không tự xoá.

## Liên quan
[`../price-volume/ticker_prune.md`](../price-volume/ticker_prune.md) (silent drift — chính là lớp lỗi
pin này canh), [`../price-volume/vnindex_pe_mirror_col.md`](../price-volume/vnindex_pe_mirror_col.md)
(backfill 2006), [`../price-volume/corp_action_pending.md`](../price-volume/corp_action_pending.md).

↩ [Về index nhóm](index.md) · [index tổng](../index.md)
