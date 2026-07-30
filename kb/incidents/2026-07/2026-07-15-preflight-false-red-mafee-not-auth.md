---
kind: incident
date: 2026-07-15
topic: preflight-false-red-mafee-not-auth
title: >-
  2026-07-15 — Preflight RED giả MAFEE_NOT_AUTH trên plan đã duyệt thật (tái diễn bug 07-06) — fix vĩnh viễn ở checker
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-15 — Preflight RED giả MAFEE_NOT_AUTH trên plan đã duyệt thật (tái diễn bug 07-06) — fix vĩnh viễn ở checker

**What happened.** ops_health_check 08:20 flag `Plan ZaloPay 2026-07-15: MAFEE_NOT_AUTH —
orders=2 approved=user mafee=False` dù plan (VPB trim 800cp + CTG buy 850cp) đã được user
duyệt thật 01:15 ICT (`approved_by=user` + approval_note chi tiết). SpaceX 07-15 cùng shape.
Winston ops-autofix (job `Winston_20260715_012007`) xác nhận: gate thực thi thật
(`trading_bot/plan.py approval_block_reason`, code-gate 07-13) chỉ đọc `approved_by` → bot
09:05 KHÔNG bị chặn; RED chỉ ở tầng báo cáo.

**Root cause.** Đúng bug đã ghi ở entry 2026-07-06: `mafee_authorized` là field không có
code path nào ghi — preflight fail cứng trên nó thì mọi plan duyệt thật đều RED giả. Lần
07-06 chỉ vá dữ liệu (stamp field vào 1 plan), không vá checker → tái diễn.

**Fix.** Bỏ fail-flag `MAFEE_NOT_AUTH` khỏi `mike/bin/preflight_check.sh`, giữ hiển thị
`mafee=` informational (commit `ef23190`, mike repo). Verify: preflight re-run 2 account →
GREEN; `approval_block_reason` trên 2 plan thật → RUN OK. Không đụng plan/executor/crontab.

**Lesson.** Khi một check báo động giả vì field-không-ai-ghi, fix đúng là sửa CHECKER cho
khớp gate thực thi thật (hoặc thêm writer), không phải stamp tay dữ liệu từng lần — vá dữ
liệu chỉ đẩy lần tái diễn sang plan kế tiếp.
