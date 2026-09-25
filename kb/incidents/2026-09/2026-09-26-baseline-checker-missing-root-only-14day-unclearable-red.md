# 2026-09-26 — `report_return_gate_selfcheck.py` đỏ 14 ngày KHÔNG AI gỡ được: 2 runner chạy 2 thứ khác nhau

**status**: fixed
**severity**: medium (không phải lỗi production — là lỗi CƠ CHẾ giám sát: một ca đỏ vĩnh viễn làm mục rữa baseline)
**phát hiện bởi**: weekly-ops-audit 2026-09-26 (job `Mike_20260925_204425`), mục 8b (chống mục rữa baseline)

## Triệu chứng
`kb/selfcheck_baseline.json` giữ `mike/bin/report_return_gate_selfcheck.py` ở `known_red` với
`auto: true`, `since: 2026-09-12` — **14 ngày**, quá xa ngưỡng 7 ngày của mục 8b. Log nhật ký
`kb_nightly.log` mỗi đêm in `--- TIMEOUT: mike/bin/report_return_gate_selfcheck.py (rc=124) ---`.
Nhưng chạy tay qua `bin/run_selfchecks.sh` thì file này **PASS**.

## Nguyên nhân gốc
Hai runner gọi CÙNG một file với THAM SỐ khác nhau:

| Runner | Lệnh | Trần | Kết quả |
|---|---|---|---|
| `bin/run_selfchecks.sh` | `... report_return_gate_selfcheck.py **--root-only**` | 120s | PASS ~0,8s |
| `bin/selfcheck_weekly_baseline_check.sh` | `... report_return_gate_selfcheck.py` (KHÔNG cờ) | `default_timeout_s` = **150s** | rc=124 **chắc chắn** |

File tự khai trong docstring: bộ 4 test đầy đủ chạm BQ, **~8-10 phút**. Bản vá ngày 2026-09-19
(cũng từ một weekly ops audit) đã xử đúng ca này — nhưng **chỉ trong `run_selfchecks.sh`**.
`selfcheck_weekly_baseline_check.sh` — runner thực sự sinh ra `known_red` và bắn bus question —
không được vá cùng, và nó không nằm trong `slow_files` nên rơi về trần mặc định 150s.

Hệ quả: một ca đỏ mà **không hành động nào của người có thể làm nó xanh** — đúng kiểu "mục rữa
baseline" mà cơ chế 8b sinh ra để chống. Nó cũng che lấp: một FAIL thật ở cùng file sẽ trông
giống hệt tình trạng đã "biết rồi".

## Bản vá
`bin/selfcheck_weekly_baseline_check.sh` — thêm bảng `SC_ARGS` theo file, **khớp đúng chính sách
của `run_selfchecks.sh`**: `report_return_gate_selfcheck.py` ⇒ `--root-only`. 4 assertion chạy ở
chế độ này CHÍNH LÀ 4 assertion phủ sự cố gốc (ROOT sai trong worktree + RED control bản cũ).
2 test chạm BQ vẫn chạy ở `run_selfchecks.sh --live` (budget 720s) ⇒ **không mất coverage**.

## Verify bằng CHẠY THẬT
- `$DNA_PYEXE mike/bin/report_return_gate_selfcheck.py --root-only` ⇒ `✅ SELFCHECK PASS`, **0,8s**
  (trần 150s, biên 187×).
- `bash -n` sạch; `SC_ARGS` rỗng an toàn dưới `set -u` (đã thử cả 2 nhánh rỗng/có cờ).
- Entry `known_red` sẽ tự được gỡ ở lần chạy 21:30 kế tiếp qua nhánh `BASELINE_UPDATED` có sẵn
  (đã chứng kiến nó hoạt động với `universe_pit_p4_selfcheck.py` ngày 2026-09-25) — **không** sửa
  tay `kb/selfcheck_baseline.json`.

## Bài học
Khi vá "file này cần tham số/ngân sách riêng", phải hỏi **mọi runner nào gọi file đó**, không chỉ
runner đang đứng trước mặt. Hai runner + một chính sách chỉ ghi ở một chỗ = chính sách đó sai ở
chỗ còn lại, âm thầm. Cùng họ với bài học "cùng lớp lỗi còn N call-site chưa vá" của chuỗi
corp-action 09-22→09-24.
