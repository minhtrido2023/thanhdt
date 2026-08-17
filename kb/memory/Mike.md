# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (2026-08-17T19:13Z)

## Đang chạy — batch
- Wags_20260817_191153 (opus/high): F2+F4+F5+F6 — claim-reply atomic, MIKE.md §8 fix, wakeup_audit fix, wake_thread log
- Taylor_20260817_191228 (sonnet/high): G2 band tolerance fix D1-D3 (VIX 08-20 cần trước 08-20 09:10)
- Winston_20260817_190446 (running): UPCOM VWAP data_registry entry + EOD capture cron

## Bridge F1+F3 — chờ F2 xong
Wags làm F2 (claim-reply) trước, rồi dispatch Wags bridge job riêng cho F1+F3.
Bridge repo: /workspace/claude-code-discord-bridge
F1: scheduler.py _run_task — delete one_shot TRƯỚC run_claude_with_config
F3: dedup_key column migration + scheduler check + wake_thread.sh integration

## G5 UPCOM implementation plan (user duyệt)
1. [RUNNING] Winston data_registry + EOD cron
2. Tích ≥3 phiên history (tự động)
3. Lặp lại probe ≥3 lần
4. Giải thích 6 mã chưa rõ hoặc gate tường minh
5. quant-skeptic + user final → wire G5 UPCOM

## VIX ex-date 08-20
Shadow TRONG PHIÊN 09:10-14:30 ICT. G2 fix (Taylor_20260817_191228) cần xong trước đó.
accept_shadow() sau khi shadow PASS.

## Context
- BQ trap: bq query truncate 100 rows
- dispatch-prompt-heredoc skill cho prompt có backtick

