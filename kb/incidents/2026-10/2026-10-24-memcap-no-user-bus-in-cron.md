---
date: 2026-10-24
status: fixed
severity: low
area: infra-memory-guard
found_by: weekly-ops-audit (Mike_20261023_210300)
title: memcap.sh không chạy được trong cron/headless (thiếu XDG_RUNTIME_DIR) — selfcheck PASS giả 1/4
---

# memcap.sh hỏng ngoài phiên tương tác — `systemd-run --user` không nối được user bus

## Triệu chứng
Baseline selfcheck tuần: `memcap_selfcheck.sh` FAIL "duoi tran khong chay", nhưng "vuot tran 1G bi
giet" lại PASS. Tái hiện: `env -u XDG_RUNTIME_DIR bin/memcap.sh 1 python3 -c ...` ⇒ `Failed to connect
to bus` rc=1 — lệnh KHÔNG chạy. Ca "vượt trần" PASS giả vì chỉ kiểm `rc≠0`.

## Root cause
Cron và headless dispatch không có `XDG_RUNTIME_DIR` ⇒ `systemd-run --user` không tìm thấy
`/run/user/1001/bus`. Guard trần RAM (sau sự cố 2026-10-20) chỉ dùng được trong phiên tương tác.
Chưa có caller production nào (grep `memcap.sh` ngoài selfcheck = 0) ⇒ chưa gây hại thật.

## Fix
- `memcap.sh`: tự export `XDG_RUNTIME_DIR=/run/user/$(id -u)` khi trống và socket bus tồn tại.
- `memcap_selfcheck.sh`: ca vượt trần đòi đúng rc=137 (bị kernel giết), không chỉ `rc≠0`.
- Verify: `env -u XDG_RUNTIME_DIR` ⇒ 4/4 PASS, hog rc=137; mutation (bỏ fix) ⇒ selfcheck mới FAIL 2 ca.
