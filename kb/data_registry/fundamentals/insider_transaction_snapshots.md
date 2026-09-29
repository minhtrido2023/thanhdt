---
kind: bigquery-table
status: CANONICAL
source: lithe-record-440915-m9.tav2_mike.insider_transaction_snapshots
group: fundamentals
scope: point-in-time provenance cho tav2_bq.insider_transaction — phục hồi cửa sổ pre-trade (ngày công bố ĐĂNG KÝ) từ 2026-08-17 trở đi
writer: mike/bin/snapshot_corp_action_daily.py (Taylor) — cron ĐỀ XUẤT 23:50 ICT hằng ngày, CHƯA CÀI tính đến 2026-08-17
first_snapshot: 2026-08-17
---

# `tav2_mike.insider_transaction_snapshots`

**Status: CANONICAL** — đây là **con đường duy nhất** để lấy lại cửa sổ pre-trade của giao dịch nội
bộ. [`insider_transaction.md`](insider_transaction.md) §Bẫy(1) kết luận thẳng: tự snapshot hàng
ngày từ giờ trở đi là cách DUY NHẤT, không có cách nào phục hồi lịch sử. Đây là script làm việc đó.

## Là gì

Append-only, mỗi ngày ghi TOÀN BỘ `tav2_bq.insider_transaction` kèm `snapshot_date` (ICT) và
`row_sha256`. 27 cột = 25 cột nguồn nguyên vẹn (đúng thứ tự) + 2 cột meta.
Partition `snapshot_date` (DAY), cluster `ticker, id`, **không có partition expiration** (cố ý).

| Cột meta | Nghĩa |
|---|---|
| `snapshot_date` DATE | Ngày **ICT quan sát** trạng thái bảng nguồn — KHÔNG phải ngày sự kiện, KHÔNG phải ngày vendor ghi |
| `row_sha256` STRING | `TO_HEX(SHA256(TO_JSON_STRING(STRUCT(<24 cột nguồn TRỪ ingested_at>))))` — hash đổi ⟺ nội dung đổi |

## Vì sao tồn tại — vấn đề đã xác nhận ở tầng nguồn

Bảng nguồn là snapshot trạng thái. Khi một `id` lật `Đăng ký` → `Đã thực hiện xong`, `public_date`
bị ghi đè từ *ngày công bố Ý ĐỊNH* (trung vị −3 ngày so với `start_date`) thành *ngày báo cáo KẾT
QUẢ* (trung vị +5 ngày so với `end_date`). bq_admin đã đọc source ETL (2026-07-29) và xác nhận cơ
chế: `publicDate` là field VCI tự maintain, bước `_merge_prefer_done` cho dòng Done luôn thắng
not-Done, **kể cả khi lần sync trước đã bắt được dòng lúc còn Đăng ký**. Với 51.090 sự kiện đã hoàn
tất, ngày đăng ký gốc **đã mất vĩnh viễn**.

Đo thật 2026-08-17: batch ingest gần nhất rewrite 1.332 dòng, trong đó **1.154 dòng (87%) có
`public_date` cũ hơn 2026-08-01** ⇒ vendor sửa dòng LỊCH SỬ mỗi lần chạy, không chỉ append.

## Dùng đúng — lấy ngày công bố ĐĂNG KÝ thật

```sql
-- Cận trên của ngày công bố đăng ký thật (độ phân giải 1 ngày)
SELECT id, ticker, MIN(snapshot_date) AS first_seen_registered
FROM `lithe-record-440915-m9.tav2_mike.insider_transaction_snapshots`
WHERE trade_status = 'Đăng ký'
GROUP BY 1, 2
HAVING first_seen_registered > (SELECT MIN(snapshot_date) FROM `...insider_transaction_snapshots`);
--      ^^^ BẮT BUỘC: loại nhóm censored bên trái, xem Bẫy (2)
```

Ghép với vintage kết quả để có cặp (đăng ký, thực hiện) — thứ Sprint 1 thiếu:

```sql
WITH v AS (
  SELECT id, ticker, snapshot_date, row_sha256, trade_status, public_date, share_acquire,
         LAG(row_sha256)   OVER w AS prev_sha,
         LAG(trade_status) OVER w AS prev_status
  FROM `...insider_transaction_snapshots`
  WINDOW w AS (PARTITION BY id ORDER BY snapshot_date)
)
SELECT * FROM v WHERE prev_status = 'Đăng ký' AND trade_status = 'Đã thực hiện xong';
```

## Bẫy (1) — `snapshot_date` KHÔNG phải "ngày có sự kiện". Vendor refresh KHÔNG đều.

Đo thật, số dòng theo `DATE(ingested_at)`: 07-27 → 50.942 · 08-01 → 69 · 08-03 → 1 · 08-04 → 6 ·
08-08 → 94 · 08-10 → 12 · 08-15 → 1.332. Khoảng trống 3-5 ngày là bình thường ⇒ **"hash không đổi
giữa 2 snapshot_date" KHÔNG có nghĩa "không có sự kiện thật"**. Phân biệt bằng `MAX(ingested_at)`
trong chính snapshot đó, đừng suy từ lịch.

## Bẫy (2) — CENSORING BÊN TRÁI: 1.364 sự kiện `Đăng ký` treo sẵn ở vintage đầu tiên

Snapshot 2026-08-17 bắt được 1.364 dòng đang ở `trade_status='Đăng ký'` (2,6% bảng). Đây là giá trị
tức thời — chúng sẽ cho cặp (đăng ký, kết quả) khi lật. **Nhưng `MIN(snapshot_date)` của chúng =
2026-08-17 KHÔNG phải ngày công bố** — chỉ là ngày ta bắt đầu chụp; chúng đã đăng ký từ trước. Dùng
thẳng trong event study = trộn sự kiện tồn đọng vào mẫu và làm lệch mọi ước lượng thời điểm. Luôn
lọc `first_seen > MIN(snapshot_date) toàn bảng`.

## Bẫy (3) — `ingested_at` CỐ Ý không nằm trong `row_sha256`

Dấu vết pipeline, không phải nội dung sự kiện; đưa vào hash sẽ sinh **amendment giả** khi vendor
rewrite dòng với nội dung y hệt. Cột vẫn được LƯU nguyên ⇒ không mất thông tin. Ai viết lại công
thức hash phải giữ đúng điều này.

## Bẫy (4) — mọi bẫy của BẢNG NGUỒN vẫn áp dụng nguyên vẹn

Snapshot không sửa dữ liệu, chỉ thêm chiều thời gian. 4 bẫy trong
[`insider_transaction.md`](insider_transaction.md) — `share_acquire` **không tin được dấu sẵn có**;
`Không thực hiện được` gần như không dùng (tỷ lệ không-khớp thật nằm ở `share_acquire`);
`share_before`/`share_after` không đáng tin ở dòng `Đăng ký`; cụm nhiều người MUA cùng ngày là dấu
vân tay ESOP chứ không phải mua chủ động — **vẫn đúng y nguyên** trên bảng này. Đọc file đó trước
khi dùng làm tín hiệu.

## Bẫy (5) — schema drift làm DỪNG pipeline, cố ý

Thêm/bớt cột nguồn ⇒ đổi tập cột vào hash ⇒ snapshot kế tiếp mọi dòng trông như vừa bị amend. Script
fail-closed (`RuntimeError: SCHEMA LECH`). Xử lý đúng = thêm cột vào bảng snapshot **và ghi vintage
đổi hash vào file này**.

## Chi phí

19,5 MB/ngày logical ⇒ ~7,13 GB/năm ⇒ **~$0,86/năm** storage. Quét mỗi lần ghi ~$0,00012. Không
phải yếu tố cần tối ưu.

## Runway — khi nào mở lại được announcement study

Tốc độ tích luỹ ≈ tốc độ sự kiện mới: 52.456 dòng / ~11,6 năm ≈ **~4.500 sự kiện/năm**. ⇒ 12 tháng
cho ~4,5k cặp đăng-ký→kết-quả có ngày công bố THẬT; 18 tháng ~6,7k. Khớp ước lượng 12-18 tháng,
nhưng **phải đo lại bằng dữ liệu thật lúc review, không trích lại con số này**.

## Vì sao ở `tav2_mike` chứ không phải `tav2_bq`

`tav2_bq` là dataset của bq_admin, đã có tiền lệ WRITE_TRUNCATE + rebuild xoá lịch sử
([`../price-volume/ticker_prune.md`](../price-volume/ticker_prune.md) §2026-07-29). Bảng này
**không tái tạo được**. `tav2_mike` được dựng để nằm ngoài tầm truncate đó. Đổi được bằng env
`SNAPSHOT_DATASET`, cần user/Mike quyết.

## Trạng thái

- Vintage đầu tiên: **2026-08-17**, 52.456 dòng, 52.456 hash phân biệt, 0 NULL, 52.456 `id` phân
  biệt. Chạy tay, verify độc lập bằng query riêng.
- Cron **CHƯA CÀI** (đề xuất `50 23 * * *` ICT, cần user/Mike duyệt — §11 coding_guidelines).
- Selfcheck: `mike/bin/snapshot_corp_action_selfcheck.py`, **41/41 PASS** 2026-08-17.
- Thiết kế đầy đủ: `mike/agents/Taylor/research/corp_action_snapshot_pipeline_design_20260817.md`.

## Liên quan
[`insider_transaction.md`](insider_transaction.md) (bảng nguồn) ·
[`../price-volume/corporate_action_snapshots.md`](../price-volume/corporate_action_snapshots.md)
(bảng anh em, cùng script) · [`../market-state/insider_flags.md`](../market-state/insider_flags.md)
(consumer WATCH-only của bảng nguồn)

↩ [Về index nhóm](index.md)
