---
kind: script
status: REAL-STALE
source: deploy_v11/fundamental_rating.py
group: rating-8l
note: external deploy package snapshot — GIỮ NGUYÊN (không archive), sync tay
writer: con người, ad-hoc mỗi lần đóng gói zip (lần cuối commit 10ae395, reorg 06-21)
---

# `deploy_v11/fundamental_rating.py`

**Status: REAL nhưng STALE snapshot — external deploy package**

## Là gì
Bản copy `fundamental_rating.py` bên trong `deploy_v11/` (gói triển khai BA-System V11 để đóng zip gửi
ra ngoài, xem `deploy_v11/README.md`/`DEPLOY.md`) — KHÔNG phải research variant, là artifact deploy
thật.

## Ai ghi / cadence
Con người, ad-hoc mỗi lần đóng gói zip mới để giao (lần cuối commit `10ae395`, reorg 06-21) — KHÔNG có
cron/script nào trong repo này tự sync.

## Bẫy
**2026-07-11 (Winston, job Winston_20260711_160905)**: xác nhận `crontab -l` + grep repo KHÔNG có gì
gọi thư mục `deploy_v11/` — không phải dead code, chỉ là bản đóng gói ngoài, nên GIỮ NGUYÊN (không
archive). Đã lệch khỏi bản canonical repo-root: thiếu pandas-3 date-parse fix + `FA_OUT_*` env override
(thêm hôm nay 07-11) + POSIX `cat` (còn Windows `type` cứng). Cần đồng bộ tay lần đóng gói zip tiếp
theo, không tự động.
