---
kind: bigquery-table
status: CANONICAL
source: lithe-record-440915-m9.tav2_mike.corporate_action_snapshots
group: price-volume
scope: point-in-time provenance cho tav2_bq.corporate_action — "bảng nguồn trông như thế nào vào ngày D"
writer: mike/bin/snapshot_corp_action_daily.py (Taylor) — cron ĐỀ XUẤT 23:50 ICT hằng ngày, CHƯA CÀI tính đến 2026-08-17
first_snapshot: 2026-08-17
---

# `tav2_mike.corporate_action_snapshots`

**Status: CANONICAL** — nguồn **duy nhất** trả lời được "bảng `corporate_action` trông như thế nào
vào ngày D". Bảng nguồn không trả lời được câu đó (bị upsert in-place).

## Là gì

Append-only, mỗi ngày ghi TOÀN BỘ `tav2_bq.corporate_action` kèm `snapshot_date` (ICT) và
`row_sha256`. 37 cột = 35 cột nguồn nguyên vẹn (đúng thứ tự) + 2 cột meta.
Partition `snapshot_date` (DAY), cluster `ticker, id`, **không có partition expiration** (cố ý).

| Cột meta | Nghĩa |
|---|---|
| `snapshot_date` DATE | Ngày **ICT quan sát** trạng thái bảng nguồn — KHÔNG phải ngày sự kiện, KHÔNG phải ngày vendor ghi |
| `row_sha256` STRING | `TO_HEX(SHA256(TO_JSON_STRING(STRUCT(<34 cột nguồn TRỪ ingested_at>))))` — hash đổi ⟺ nội dung đổi |

## Vì sao tồn tại

`tav2_bq.corporate_action` là snapshot trạng thái, không phải event-log: khi sự kiện lật
`announced` → `executed`, vendor **ghi đè `public_date` tại chỗ** ⇒ ngày công bố ý định mất vĩnh
viễn. Đo thật 2026-08-17: batch ingest gần nhất rewrite 1.331 dòng, trong đó **1.185 dòng (89%) có
`public_date` cũ hơn 2026-08-01** (cũ nhất 2024-09-13) ⇒ vendor sửa dòng LỊCH SỬ mỗi lần chạy.
Đây là lý do Sprint 1 (`corp_action_program_20260815`) CẤM announcement study.

## Bẫy (1) — `snapshot_date` KHÔNG phải "ngày có sự kiện". Vendor refresh KHÔNG đều.

Đo thật: `corporate_action` chỉ có ingest ở 08-12 (34.841 dòng), 08-13 (4), 08-15 (1.331) — khoảng
trống 3-5 ngày là bình thường. ⇒ **"hash không đổi giữa 2 snapshot_date" KHÔNG có nghĩa "không có
sự kiện thật"** — rất có thể vendor đơn giản không chạy. Muốn phân biệt: đọc `MAX(ingested_at)`
của chính snapshot đó, đừng suy từ lịch.

## Bẫy (2) — CENSORING BÊN TRÁI: sự kiện treo từ trước 2026-08-17 không có vintage đăng ký thật

Snapshot đầu tiên bắt được 869 dòng đang ở `event_status='announced'`. Với những dòng này,
`MIN(snapshot_date)` = 2026-08-17 KHÔNG phải ngày công bố — chỉ là ngày ta bắt đầu chụp. Dùng chúng
trong event study sẽ trộn sự kiện tồn đọng vào mẫu. **Lọc bỏ mọi dòng có
`first_seen = MIN(snapshot_date) toàn bảng`** trước khi đo bất cứ thứ gì liên quan tới thời điểm
công bố.

## Bẫy (3) — `ingested_at` CỐ Ý không nằm trong `row_sha256`

Nó là dấu vết pipeline, không phải nội dung sự kiện. Nếu đưa vào hash, một lần vendor rewrite dòng
với nội dung y hệt sẽ báo **amendment giả**. Cột vẫn được LƯU nguyên trong bảng ⇒ không mất thông
tin, chỉ đổi vai trò từ "tín hiệu" sang "metadata". Ai tự viết lại công thức hash phải giữ đúng
điều này, nếu không mọi so sánh xuyên vintage sẽ lệch.

## Bẫy (4) — schema drift làm DỪNG pipeline, cố ý, không được "sửa" bằng auto-evolve

Thêm/bớt cột nguồn ⇒ đổi tập cột vào hash ⇒ ở snapshot kế tiếp *mọi dòng* trông như vừa bị amend.
Script fail-closed (`RuntimeError: SCHEMA LECH`) và cron sẽ đỏ mỗi ngày cho tới khi có người xử lý.
Xử lý đúng = thêm cột vào bảng snapshot **và ghi vintage đổi hash vào file này**, để phân tích sau
biết chỗ đứt.

## Truy vấn tiêu chuẩn

```sql
-- Dòng bị vendor sửa nội dung, kèm public_date trước/sau
WITH v AS (
  SELECT id, ticker, snapshot_date, row_sha256, public_date, event_status,
         LAG(row_sha256)  OVER w AS prev_sha,
         LAG(public_date) OVER w AS prev_public_date,
         LAG(event_status) OVER w AS prev_status
  FROM `lithe-record-440915-m9.tav2_mike.corporate_action_snapshots`
  WINDOW w AS (PARTITION BY id ORDER BY snapshot_date)
)
SELECT * FROM v WHERE prev_sha IS NOT NULL AND row_sha256 != prev_sha;

-- "Bảng trông như thế nào ngày D" — một WHERE, không cần window function
SELECT * FROM `...corporate_action_snapshots` WHERE snapshot_date = DATE '2026-08-17';
```

## Chi phí

14,6 MB/ngày logical ⇒ ~5,33 GB/năm ⇒ **~$0,64/năm** storage. Quét mỗi lần ghi ~$0,00009. Quét cả
năm cho amendment report ~$0,03. Không phải yếu tố cần tối ưu — đã cân nhắc và BỎ phương án lưu
delta (tiết kiệm 99% storage nhưng làm mọi truy vấn "trạng thái ngày D" phức tạp hơn).

## Vì sao ở `tav2_mike` chứ không phải `tav2_bq`

`tav2_bq` là dataset của bq_admin và **đã có tiền lệ WRITE_TRUNCATE + rebuild xoá lịch sử**
([`ticker_prune.md`](ticker_prune.md) §2026-07-29: 58 mã biến mất khỏi TOÀN BỘ lịch sử). Bảng này
**không tái tạo được** — mất một lần là mất toàn bộ tích luỹ. `tav2_mike` được dựng chính xác để
nằm ngoài tầm truncate đó (xem [`universe_pit.md`](universe_pit.md)). Đổi được bằng env
`SNAPSHOT_DATASET`, nhưng cần user/Mike quyết.

## Trạng thái

- Vintage đầu tiên: **2026-08-17**, 36.176 dòng, 36.176 hash phân biệt, 0 NULL. Chạy tay, verify
  độc lập bằng query riêng (không đọc self-report của script).
- Cron **CHƯA CÀI** (đề xuất `50 23 * * *` ICT, cần user/Mike duyệt — §11 coding_guidelines).
- Selfcheck: `mike/bin/snapshot_corp_action_selfcheck.py`, **41/41 PASS** 2026-08-17.
- Thiết kế đầy đủ + hạn chế + runway mở lại announcement study:
  `mike/agents/Taylor/research/corp_action_snapshot_pipeline_design_20260817.md`.

## Liên quan
[`corporate_action_bq.md`](corporate_action_bq.md) (bảng nguồn, status TRAP) ·
[`../fundamentals/insider_transaction_snapshots.md`](../fundamentals/insider_transaction_snapshots.md)
(bảng anh em, cùng script) · [`universe_pit.md`](universe_pit.md) (cùng dataset `tav2_mike`)

↩ [Về index nhóm](index.md)
