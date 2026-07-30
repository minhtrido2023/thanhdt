---
kind: incident
date: 2026-07-13
topic: dt5g-refresh-missed-cron-time-change
title: >-
  2026-07-13 — DT5G refresh thứ Sáu 07-10 KHÔNG chạy: dời giờ cron cùng ngày rơi đúng khe hở giữa slot cũ và slot mới
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-13 — DT5G refresh thứ Sáu 07-10 KHÔNG chạy: dời giờ cron cùng ngày rơi đúng khe hở giữa slot cũ và slot mới

**What happened.** Checker `ops_health_check` (11:52 ICT thứ Hai 07-13) cảnh báo
`macro_health.json` cũ 68.4h. Truy vết: file dừng ở thứ Sáu 07-10 15:30 ICT (writer =
`papertrade_daily.sh` step [4]); KHÔNG tồn tại `data/refresh_v34b_linux_2026-07-10.log`
(mọi ngày 07-01→07-09 đều có); BQ `vnindex_5state_dt5g_live` MAX(time)=2026-07-09 —
tức chuỗi daily_refresh **thứ Sáu 07-10 không hề chạy**, dt5g_live thiếu phiên 07-10
suốt cuối tuần.

**Root cause.** Commit `1a3ea5c` (dời cron 23:15→18:30 ICT, entry 2026-07-10 bên dưới)
được cài vào crontab lúc **18:55 ICT thứ Sáu** — slot MỚI 18:30 vừa trôi qua 25 phút,
slot CŨ 23:15 bị xoá trước khi tới giờ → ngày đổi lịch không có slot nào fire. Không ai
nhận ra ngay vì thứ Bảy/Chủ nhật không có phiên; chỉ lộ ra qua audit cron C1b
(`Winston_20260712_142100`) và checker sáng thứ Hai.

**Fix.** Không cần fix code — không có bug. Taylor đã backfill thủ công EW-leg tối CN
(`refresh_v34b_linux_2026-07-12_*manual*.log`, job `Taylor_20260712_151135`); full chain
tự hồi phục qua cron 18:30 ICT thứ Hai 07-13 (recompute toàn cửa sổ → dt5g_live có cả
07-10 lẫn 07-13, `macro_health.json` tươi lại). Trong lúc stale, `get_gated_state()`
fail-closed về DT4-only đúng thiết kế (DT4 == DT5G == NEUTRAL, không lệch hành vi).
Verify chốt: mục "Còn treo, chờ cron thứ Hai 07-13" trong Current Operations.

**Lesson.** Khi dời giờ cron sang slot SỚM HƠN trong cùng ngày, nếu cài sau khi slot mới
đã trôi qua thì ngày đó mất chạy — phải chạy tay 1 lần ngay sau khi cài, hoặc cài trước
giờ slot mới. Checker freshness (preflight `macro_health` age + `ops_health_check`) đã
bắt đúng hệ quả — giữ nguyên, đừng nới ngưỡng.
