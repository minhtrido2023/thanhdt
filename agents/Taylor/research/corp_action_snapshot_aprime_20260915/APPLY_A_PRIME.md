# APPLY A′ — snapshot_corp_action_daily sau khi vendor thêm 2 cột (2026-09-15)

> Chuẩn bị bởi Taylor (job `Taylor_20260914_175556`), **CHƯA áp dụng**. Chưa chạy DDL, chưa ghi BQ,
> chưa merge. Bus question: `corp-action-snapshot-schema-drift-20260914`.
> Branch `fix/corp-action-snapshot-schema-aprime`, worktree `mike/agents/wt-corp-snapshot-aprime`.

## Hạn chót
Cron `50 23 * * *` (giờ UTC trên server) = **06:50 ICT 15/09**. Run đó sẽ gắn nhãn `snapshot_date=2026-09-15`.
Nếu cron chạy trên code cũ hoặc trước khi DDL chạy, **corporate_action fail lần nữa**. Với code cũ,
**insider_transaction cũng chết theo** (vintage 09-14 của CẢ HAI bảng đã mất: snapshot gần nhất của
insider là 2026-09-13).

## Thay đổi trong branch (1 commit)
| # | Đổi gì | Vì sao |
|---|---|---|
| 1 | `schema_problems` so cột theo TÊN→KIỂU, bỏ qua thứ tự. Vẫn báo thiếu cột, thừa cột, lệch kiểu, thiếu cột meta | `ALTER ADD COLUMN` chỉ nối được vào cuối bảng, còn vendor chèn cột ở vị trí 34-35. Nếu vẫn so thứ tự thì không câu DDL nào qua được cổng. `insert_sql` gọi tên cột tường minh, còn hash lấy thứ tự từ bảng NGUỒN |
| 2 | `HASH_EXCLUDE` += `source_news_id`, `first_disclosure_datetime` | Để `row_sha256` so được liên tục qua mốc schema đổi. Revision của 2 cột này vẫn dò được bằng `LAG()` trên cột đã lưu |
| 3 | Mỗi bảng chạy trong try riêng. rc=1 nếu có bảng lỗi. Không phải `--dry-run` thì post Discord topic `architecture` kèm exception thật | Lỗi 1 bảng không còn giết bảng kia. Trước đây lỗi chỉ nằm trong log cron |
| 4 | Selfcheck thêm T8 (schema A′), T9 (cô lập + notify), T10 (hash liên tục, chạy BQ thật, 0 byte) | |

## Bằng chứng đã đo (không phải suy luận)
- **Selfcheck**: `68` assertion, `67/68 PASS` dưới cả `env -u TZ` lẫn `TZ=America/Los_Angeles`. FAIL duy nhất
  là T3.7 corporate_action live, kỳ vọng vì DDL chưa chạy (`THIEU ['source_news_id', 'first_disclosure_datetime']`).
- **Mutation**: đưa 6 mutation vào, cả 6 đều bị selfcheck bắt:
  - revert `HASH_EXCLUDE` → T10.1 + T10.3 FAIL
  - so thứ tự nghiêm ngặt trở lại → T8.1 + T8.2 + T8.5 FAIL
  - bỏ check kiểu → T8.3 FAIL
  - bảng lỗi `break` vòng lặp (tái hiện list-comprehension cũ) → T9.2 + T9.4 FAIL
  - notify cả khi dry-run → T9.6 FAIL
  - nuốt lỗi notify → T9.8 FAIL
- **`--dry-run` branch mới trên BQ thật** (`dryrun_branch_live_20260915.log`, rc=1):
  - corporate_action chỉ còn báo `cot CO o nguon nhung THIEU o snapshot: ['source_news_id', 'first_disclosure_datetime']`, không còn lỗi thứ tự
  - insider_transaction `schema KHOP` → `se append 52,922 dong`, quét 19,7 MB
  - không post Discord
- **Hash liên tục trên DỮ LIỆU THẬT**: tính hash mới (37 cột nguồn, loại 3 cột) cho `tav2_bq.corporate_action`
  hiện tại rồi JOIN theo `id` với vintage `2026-09-13`:
  - 36.336 id chung. Vendor đã rewrite `ingested_at` của **100%** dòng (lần nạp lại 22:46 ICT 14/09)
  - **36.290 dòng (99,87%) có hash BẰNG hash cũ**
  - 46 dòng lệch đều là thay đổi nội dung thật: `event_status` 20, `organ_code` 15, `icb_code_lv1` 9, bộ ngày `public_date/display_date1/2/exright/record/payout` + `source_url` 2
  - ⇒ không sinh amendment giả qua mốc
- **Phần SELECT của câu INSERT mới**: `--dry_run` trên BQ thật validate OK (37 cột, quét 14,97 MB).
- **DDL `--dry_run`**: `Query successfully validated ... 0 bytes`.

## Thứ tự áp dụng (cần user duyệt — DDL là ghi BQ)
```bash
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
cd /home/trido/thanhdt/WorkingClaude

# 0) (tuỳ chọn) validate lại DDL — 0 byte, không đổi gì
bq query --use_legacy_sql=false --dry_run --project_id=lithe-record-440915-m9 \
  'ALTER TABLE `lithe-record-440915-m9.tav2_mike.corporate_action_snapshots` ADD COLUMN source_news_id STRING, ADD COLUMN first_disclosure_datetime TIMESTAMP'

# 1) DDL THẬT (chỉ nối 2 cột NULLABLE; các dòng vintage cũ nhận NULL; không đụng dữ liệu)
bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 \
  'ALTER TABLE `lithe-record-440915-m9.tav2_mike.corporate_action_snapshots` ADD COLUMN source_news_id STRING, ADD COLUMN first_disclosure_datetime TIMESTAMP'

# 2) merge branch vào mike master
cd /home/trido/thanhdt/WorkingClaude/mike
git merge --no-ff fix/corp-action-snapshot-schema-aprime

# 3) dry-run script (KHÔNG --date) — kỳ vọng: CẢ 2 bảng "schema : KHOP" + "[dry-run] se append", rc=0
cd /home/trido/thanhdt/WorkingClaude && python3 mike/bin/snapshot_corp_action_daily.py --dry-run; echo rc=$?

# 4) selfcheck — kỳ vọng 68/68 PASS (T3.7 hết đỏ sau DDL)
python3 mike/bin/snapshot_corp_action_selfcheck.py

# 5) để cron 06:50 ICT tự chạy
```
Nếu bước 3 vẫn báo lệch thì **dừng**, đừng chạy ghi thật. Đọc nguyên văn problem list (ví dụ vendor lại đổi schema).

## Verify sau run 06:50
```bash
tail -40 /home/trido/thanhdt/WorkingClaude/mike/logs/snapshot_corp_action_$(date +%Y%m).log

bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 '
SELECT "corporate_action" AS t, COUNT(*) n, COUNTIF(source_news_id IS NOT NULL) n_news,
       COUNTIF(first_disclosure_datetime IS NOT NULL) n_first_disc,
       MIN(first_disclosure_datetime) min_fd, MAX(first_disclosure_datetime) max_fd
FROM `lithe-record-440915-m9.tav2_mike.corporate_action_snapshots` WHERE snapshot_date = DATE "2026-09-15"
UNION ALL
SELECT "insider_transaction", COUNT(*), NULL, NULL, NULL, NULL
FROM `lithe-record-440915-m9.tav2_mike.insider_transaction_snapshots` WHERE snapshot_date = DATE "2026-09-15"'
```
Kỳ vọng:
- corporate_action `n` = số dòng nguồn lúc chạy (~36.352), `n_first_disc` ≈ 15.8k (đo trước: 15.823), `min_fd` ≈ 2015-03-02
- insider_transaction `n` ≈ 52.922

Kiểm tra liên tục của hash (kỳ vọng `same_hash/n_join` ≈ 99%+, KHÔNG phải ~0%):
```sql
SELECT COUNT(*) n_join, COUNTIF(a.row_sha256 = b.row_sha256) same_hash
FROM `lithe-record-440915-m9.tav2_mike.corporate_action_snapshots` a
JOIN `lithe-record-440915-m9.tav2_mike.corporate_action_snapshots` b USING (id)
WHERE a.snapshot_date = DATE '2026-09-13' AND b.snapshot_date = DATE '2026-09-15'
```

## Nếu trễ 06:50 (DDL/merge chưa xong khi cron chạy)
- Cron fail corporate_action. Nếu đã merge thì Discord `architecture` báo lỗi và insider_transaction VẪN ghi 09-15.
  Chưa merge thì cả 2 bảng fail như 09-14.
- Làm xong bước 1-3 **trong ngày ICT 15/09**, rồi chạy tay **KHÔNG kèm `--date`**:
  `python3 mike/bin/snapshot_corp_action_daily.py`.
  Script tự gắn nhãn hôm nay theo ICT = 15/09 và idempotent (bảng nào đã có 09-15 thì SKIP).
- **TUYỆT ĐỐI KHÔNG `--date 2026-09-14`** (hay bất kỳ ngày cũ nào). Bảng nguồn đã nạp lại lúc 22:46 ICT 14/09,
  nên làm vậy sẽ đóng dấu trạng thái HIỆN TẠI với nhãn ngày cũ ⇒ lịch sử point-in-time sai vĩnh viễn.
  Vintage 09-14 coi như mất.

## Việc kèm theo (không chặn 06:50)
- Registry `kb/data_registry/` cho `corporate_action_snapshots` (qua Mike/§13 `.proposed`) cần ghi 3 điểm:
  - 2 cột mới có từ vintage 2026-09-15; mọi vintage ≤ 09-13 mang NULL (không phải "vendor không có dữ liệu")
  - vintage 09-14 bị thiếu ở CẢ 2 bảng
  - `row_sha256` loại thêm 2 cột từ 09-15, hash vẫn so được liên tục
- `kb/cron_registry.md` đang ghi giờ 23:50 ICT; giờ thật là 06:50 ICT (Mike đã nêu).
