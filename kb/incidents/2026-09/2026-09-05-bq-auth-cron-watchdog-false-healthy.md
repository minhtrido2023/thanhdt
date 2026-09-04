# 2026-09-05 — Watchdog money-path báo "KHỎE" GIẢ khi `bq` fail auth trong cron; `bq_monthly_pin` chết 2 tháng liền với chẩn đoán RỖNG

**Status**: fixed
**Phát hiện bởi**: weekly ops audit 2026-09-05 (mục 1 — STALE `bq_monthly_pin_cron.log` 34,2 ngày)
**Ảnh hưởng**:
- `custom30v_rebalance_watch.sh` — watchdog cho `tav2_bq.custom30v_8l` (bảng money-path, 30% idle-pool
  parking) **trả về "healthy, im lặng" mỗi khi `bq` fail auth**. Đúng chế độ hỏng mà chính nó được viết ra
  để chặn (writer mồ côi lặng lẽ 06-18→07-11). Rebalance THẬT vẫn đúng (MAX(rebal_date)=2026-08-05 =
  trigger quý tháng 8) nên **không có tổn thất**, nhưng lớp giám sát đã mù trong một khoảng chưa xác định.
- `bq_monthly_pin` — hỏng cả 2026-08-01 (exit=3) và 2026-09-01 (exit=1). **Thiếu pin 202608 + 202609**
  (audit trail vs silent restates). Thông điệp lỗi in ra log là chuỗi RỖNG.

## Root cause — 3 khiếm khuyết độc lập chồng lên nhau

**(1) Thiếu `CLOUDSDK_CONFIG` trong wrapper cron.** `wc_env.sh` là nguồn chuẩn tắc
(`CLOUDSDK_CONFIG=/home/trido/thanhdt/gcloud_dtienthanh`). `bq_monthly_pin.sh` và
`custom30v_rebalance_watch.sh` chỉ `export PATH=...google-cloud-sdk/bin`, KHÔNG source `wc_env.sh`
⇒ dưới cron gcloud rơi về `~/.config/gcloud` (scope hỏng). Tái hiện thật:

```
$ env -i HOME=/home/trido PATH=/home/trido/google-cloud-sdk/bin:/usr/bin:/bin \
    bq show --format=none --project_id=lithe-record-440915-m9 tav2_pin
BigQuery error in show operation: Error retrieving auth credentials from gcloud:
ERROR: (gcloud.auth.print-access-token) ... ('invalid_scope: Bad Request', ...)
rc=1
```
Cùng lớp với 2 commit 2026-08-28 (`fb406837` full-path bq, `490289c5` CLOUDSDK_CONFIG+PATH) — 2 file
này bị bỏ sót vì lúc đó chỉ vá file đang lỗi, không quét cả họ (đúng dạng §28 mô tả).

**(2) `bq` in lỗi ra STDOUT ⇒ guard `-z` không bao giờ nổ (lần tái diễn thứ 5).**
`custom30v_rebalance_watch.sh` cũ:
```bash
MAX_REBAL="$(bq query ... 2>/dev/null | tail -1)"
if [ -z "$MAX_REBAL" ]; then ... RED ... fi
```
`2>/dev/null` ném đi đúng bằng chứng (§29), còn thông điệp lỗi thật nằm ở stdout ⇒ `tail -1` trả
`"to select an already authenticated account to use."` — chuỗi **KHÔNG rỗng**, lọt guard. Rồi
`[ "to select…" \< "2026-08-05" ]` sai (lexical `t` > `2`) ⇒ rơi vào nhánh *"Healthy — reset streak,
im lặng"*, `exit 0`. Đây là §28 (so chuỗi mô tả tự do thay vì GIÁ TRỊ đã chuẩn hoá) + §29 cùng lúc.
`bq_monthly_pin.py::run()` mắc đúng nửa sau: `p.stderr.strip()[:2000]` ⇒ chẩn đoán rỗng.

**(3) `ensure_dataset()` là check-then-act KHÔNG idempotent.** `bq show` fail vì lý do KHÁC "chưa tồn
tại" (auth/mạng) ⇒ rơi vào nhánh `bq mk` ⇒ mk fail `already exists` ⇒ crash. §5.

## Fix
- `bin/custom30v_rebalance_watch.sh`: source `wc_env.sh`; giữ nguyên cả 2 kênh output (`2>&1`), kiểm
  `rc`, và **bắt buộc `MAX_REBAL` khớp `^[0-9]{4}-[0-9]{2}-[0-9]{2}$`** trước khi đem đi so sánh;
  thông điệp RED trích nguyên văn output thật của `bq`.
- `bin/bq_monthly_pin.sh`: source `wc_env.sh`.
- `bin/bq_monthly_pin.py`: `run()` đọc `stderr or stdout`; `ensure_dataset()` chấp nhận `already exists`.
- `bin/verify_account_snapshot.py` + `bin/compute_active_nav.py`: cùng họ (money-path), sửa chuỗi chẩn
  đoán `stderr` → `stderr or stdout`. **Không đổi luồng**, chỉ đổi chuỗi báo lỗi.

## Verify (CHẠY THẬT, A/B trong sandbox mô phỏng env cron)
`custom30v_rebalance_watch.sh`, cùng kịch bản `invalid_scope`:
```
TRƯỚC FIX: rc=0, im lặng hoàn toàn            <-- báo KHỎE giả
SAU  FIX: rc=1, NOTIFY> 🔴 ... (bq rc=1). Output thật của bq: BigQuery error in query
          operation: Error retrieving auth credentials from gcloud: ... invalid_scope ...
```
`bq_monthly_pin`:
```
run(['bq','mk',...tav2_pin]) -> RAISED, msg = "already exists."      (trước: chuỗi rỗng)
ensure_dataset()             -> OK, no crash
env -i HOME=... PATH=/usr/bin:/bin bash bin/bq_monthly_pin.sh --dry-run --no-notify -> rc=0
    (chính env cron đã làm nó chết 09-01; log ghi 11 dòng DRY + "--- exit=0 ---")
```
Selfcheck phạm vi money-path (§23): `compute_active_nav_selfcheck` ALL PASS ·
`verify_account_snapshot_corp_action` 12/0 · `..._lot_reset` 32/0 · `exrights_price_basis` 38/0 ·
`nav_scripts_2account` PASS · `snapshot_corp_action` 43/43.

## Còn mở (KHÔNG tự xử — cần người quyết)
**Thiếu pin `202608` và `202609`.** Dữ liệu tháng 8 đã trôi, không tái tạo được. Chạy pin 202609 lúc
này (09-05) sẽ tạo artifact mang nhãn tháng 9 nhưng chụp trạng thái 09-05 chứ không phải 09-01 —
đúng loại nhãn lệch mà chính job này sinh ra để phát hiện. Để user quyết có chạy bù hay bỏ qua.

## Bài học
Watchdog phải TỰ CHỨNG MINH nó đọc được dữ liệu, không chỉ "không thấy gì bất thường". Guard
`-z` trên output của một CLI in lỗi ra stdout là guard GIẢ. Luật chung đã có ở §28/§29 — ca này
là bằng chứng rằng quét theo HỌ (mọi call-site `bq` + mọi wrapper cron chạm `bq`) phải là một bước
riêng, không phải hệ quả phụ của việc vá call-site đang lỗi.
