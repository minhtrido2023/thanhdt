---
date: 2026-10-24
status: fixed
severity: low
area: kb-tooling
found_by: weekly-ops-audit (Mike_20261023_210300)
title: incidents_index_sync.py chèn lại cùng 1 dòng MỖI NGÀY — index.md nhân 59 bản trùng
---

# incidents_index_sync.py chèn lại cùng 1 dòng mỗi ngày — 59 bản trùng trong index.md

## Triệu chứng
Commit `chore(incidents): auto-sync index.md` (cron_health_check_daily.sh 08:25) xuất hiện 5/5 ngày
giao dịch tuần 19-23/10, mỗi lần +1 dòng `2026-08-04 ... paper-main-netted-evidence-silent-8-days.md`.
`kb/incidents/index.md` tích ~60 dòng y hệt (tái diễn từ khoảng đầu 08/2026).

## Root cause
`LINK_RE` yêu cầu cột status là MỘT token (`(\S+)`). Frontmatter incident đó có status chứa khoảng
trắng (`fixed (monitoring); production-code fix in progress (...)`) ⇒ regex không khớp chính dòng
`--fix` vừa ghi ⇒ `--check` báo THIẾU ⇒ `--fix` chèn tiếp ngày sau. Cơ chế tự sửa thành tự nhân bản;
daily commit "đã tự sửa" che mất việc nó không bao giờ hội tụ.

## Fix
- `LINK_RE` cột status đổi `(\S+)` → `([^|\n]*?)`.
- Dedupe index.md: xoá 59 dòng trùng y hệt (giữ bản đầu).
- Verify bằng chạy thật: `--check` → `OK: 107 file thật khớp đúng 107 dòng`; `--fix` lần 2 →
  "không có drift" (hội tụ, idempotent).
- Bài học: auto-fix lặp lại MỖI ngày cùng một nội dung = dấu hiệu không hội tụ, không phải "drift tự nhiên".
