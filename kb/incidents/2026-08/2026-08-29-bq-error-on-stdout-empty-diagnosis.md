# 2026-08-29 — `bq` in lỗi ra STDOUT ⇒ `dividend_adjusted_return._bq()` báo "bq query failed: " RỖNG

**Status**: fixed
**Phát hiện bởi**: weekly ops audit 2026-08-29 (mục 1, ERRORS_FOUND trong `logs/check_report_cadence.log`)
**Ảnh hưởng**: cổng tỉ suất (`report_return_gate.py`) chặn báo cáo tháng 08/2026 nhiều ngày liền
(và `newdeals_daily_report.py` FATAL 08-27, 08-28) với thông điệp KHÔNG chứa một chữ nào về nguyên
nhân — người vận hành mù hoàn toàn.

## Root cause
```python
if out.returncode != 0:
    raise RuntimeError(f"bq query failed: {out.stderr.strip()[:500]}")
```
`bq` CLI ghi thông điệp lỗi ra **stdout**, không phải stderr. Đo thật:

```
$ bq query ... 'SELECT * FROM tav2_bq.NO_SUCH_TABLE_XYZ LIMIT 1'
rc=2
STDOUT=[BigQuery error in query operation: … Not found: Table …]
STDERR=[]
```

⇒ chuỗi chẩn đoán luôn rỗng. Đây là §29 (coding_guidelines) — "vứt bằng chứng rồi đoán", biến thể
"đọc nhầm kênh". Lần tái diễn thứ 4 của họ lỗi này.

## Fix
`bin/dividend_adjusted_return.py` + `bin/lag_entry_anchor.py`:
```python
msg = (out.stderr.strip() or out.stdout.strip())[:500]
raise RuntimeError(f"bq query failed: {msg}")
```
`agents/Taylor/insider_flags.py` ĐÃ có bản sửa này từ 2026-08-22 (commit `6df49fba`) — 2 file kia
bị bỏ sót vì lúc đó chỉ vá đúng call-site đang lỗi, không quét cả họ. Đúng dạng "vá từng call-site
không chặn được ca thứ N" mà §28 mô tả.

## Verify (chạy thật)
Gọi `_bq()` của CẢ HAI module với bảng không tồn tại → cả hai raise kèm nguyên văn
`BigQuery error in query operation: … Not found: Table …`. Trước fix: chuỗi rỗng.

## Còn mở
Nguyên nhân GỐC làm bq fail trong cron (chứ không phải chuyện thông điệp rỗng) vẫn đang xác minh
lại — 2 commit 2026-08-28 (`fb406837` full-path bq, `490289c5` CLOUDSDK_CONFIG+PATH) rất có thể đã
xử lý, nhưng cron chưa trigger lại kể từ đó. Từ lần fail kế tiếp trở đi, log sẽ tự nói ra nguyên
nhân thật thay vì để đoán.
