# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (2026-08-17T19:34Z)

## Đang chạy
- Wags_20260817_193233 (opus/high, timeout=1800s): F1+F3 bridge repo
  F1: scheduler.py _run_task — delete one_shot TRƯỚC run_claude
  F3: executed_at column atomic check — skip nếu đã chạy (defense-in-depth)
  Sau khi xong: arch-reviewer bắt buộc (scheduler là daemon dùng chung)

## Xong hôm nay 08-17
- F2+F4+F5+F6 (commit 600b9fa1): claim-reply atomic, MIKE.md §8 fix, wakeup_audit, wake_thread log
- G2 band tolerance D1-D3 (commit Taylor): max(1%, 1 tick) — VIX 08-20 sẽ PASS
- Winston UPCOM VWAP infra: script + data_registry (cron chưa install — chờ user duyệt)

## Chờ user
- Duyệt install cron UPCOM VWAP: `15 8 * * 1-5` (15:15 ICT T2-T6)

## G5 UPCOM — kế hoạch
1. [DONE] Winston data_registry + script
2. Tích ≥3 phiên avgPrice history (cron chạy T2-T6 sau khi được install)
3. Lặp lại probe ≥3 phiên
4. Giải thích 6 mã UPCOM chưa khớp (VNE/MZG/VBB/SDA/AAV/DDG) hoặc gate tường minh
5. quant-skeptic + user final → wire G5 UPCOM

## VIX ex-date 08-20
Shadow TRONG PHIÊN 09:10-14:30 ICT 08-20. G2 fix đã xong.
accept_shadow() sau PASS.

## Context
- BQ trap: bq query truncate 100 rows
- dispatch-prompt-heredoc skill cho prompt có backtick

