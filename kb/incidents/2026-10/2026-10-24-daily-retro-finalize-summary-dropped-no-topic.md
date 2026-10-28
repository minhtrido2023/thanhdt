---
date: 2026-10-24
status: fixed
severity: low
area: notify-routing
found_by: weekly-ops-audit (Mike_20261023_210300)
---

# Tóm tắt RETRO hằng ngày thỉnh thoảng không tới Trading Daily — finalize dispatch không ghim topic

## Triệu chứng
`logs/notify_thread_errors.log`: `notify_thread: KHONG CO topic (khong ai truyen, $DISCORD_THREAD_ID rong) — TIN NHAN KHONG GUI`
với `msg=Retro ...` lúc 00:33 ICT các ngày 2026-10-12, 10-17, 10-23 (ngoài ra 10-03, 10-08 cùng
dạng). Tức ~1 lần/5 ngày tóm tắt retro bị nuốt, không ai thấy.

## Root cause
`bin/daily_retro.sh` bước 3 (finalize, `dispatch.sh Mike ... &`) KHÔNG truyền `--thread`. Chạy
từ cron ⇒ `$DISCORD_THREAD_ID` của agent con rỗng. Prompt mục 5 chỉ nói "vào Trading Daily
(topic trading_daily)" bằng văn xuôi; phần lớn ngày agent tự gõ đúng `notify_thread.sh "<msg>"
trading_daily`, nhưng thỉnh thoảng gọi thiếu tham số thứ 2 ⇒ notify_thread.sh từ chối (đúng thiết
kế, không đoán topic) ⇒ tin mất. Bước 1 (draft) đã có `--thread architecture` từ 2026-08-02; bước 3
bị sót.

## Fix
- `dispatch.sh Mike ... --thread trading_daily` cho bước finalize ⇒ env fallback luôn có topic.
- Prompt mục 5 ghi nguyên lệnh `bin/notify_thread.sh "<tóm tắt>" trading_daily`.
- Verify: `bash -n` OK; `discord_channel.sh trading_daily` phân giải được; 3 selfcheck retro
  (failcause 8/8, measured_by 48/48, retro_escalate PASS); shellcheck_gate sạch.
- CHƯA verify production: lần chạy thật đầu tiên 00:30 ICT 25/10 — kiểm `notify_thread_errors.log`
  không còn dòng `msg=Retro` mới.
