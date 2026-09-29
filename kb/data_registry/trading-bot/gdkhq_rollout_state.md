---
kind: script-output
status: CANONICAL
source: data/gdkhq_d1d3_rollout.json + data/gdkhq_shadow_acceptance.json
group: trading-bot
note: ad-hoc, cần xác nhận cadence thật — không tìm thấy cron riêng, ghi mỗi lần bot_execute.py chạy đường có gọi gdkhq_rollout; đăng ký 2026-08-28 sau khi phát hiện chưa có entry (job Taylor_20260828_081256)
writer: trading_bot/gdkhq_rollout.py (STATE_PATH / ACCEPTANCE_STATE_PATH) — gọi từ bot_execute.py
---

# data/gdkhq_d1d3_rollout.json + data/gdkhq_shadow_acceptance.json

**Status: CANONICAL — cadence CHƯA XÁC NHẬN, ghi lại đúng theo phát hiện thật**

## Là gì
State rollout D1/D3 (thuế/phí giao dịch T+? — tên gợi ý "giao dịch không hưởng quyền"/timing) và
trạng thái shadow-acceptance đi kèm, dùng bởi `trading_bot/gdkhq_rollout.py`.

## Ai ghi / cadence
`trading_bot/gdkhq_rollout.py` ghi 2 file này (`STATE_PATH`, `ACCEPTANCE_STATE_PATH`), được gọi từ
`bot_execute.py` (đường thực thi bot chính, cron paper main T2-T6 nhiều khung giờ trong ngày — xem
`mike/kb/cron_registry.md` mục `bot_execute.py --account main`). **Không có cron RIÊNG cho
gdkhq_rollout** — nó là 1 bước trong luồng bot_execute, nên cadence thực tế = cadence của
bot_execute.py (nhiều lần/ngày các phiên giao dịch T2-T6), nhưng KHÔNG verify được liệu MỌI lần
bot_execute chạy đều update state này hay chỉ khi có điều kiện cụ thể (rollout D1/D3 kích hoạt) —
**cần Taylor/Mafee xác nhận lại điều kiện ghi cụ thể trước khi dùng mtime của 2 file này làm proxy
freshness cho toàn bộ pipeline bot_execute**.

## Bẫy
- Đây là state file production của bot thật (không phải paper/nghiên cứu) — sửa tay có rủi ro y hệt
  các state file trading_bot khác (§5 coding_guidelines: atomic write, side-effect idempotent).
- Selfcheck liên quan: `gdkhq_rollout_selfcheck.py` — chạy trước khi đổi logic file này.
