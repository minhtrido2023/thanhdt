# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy
  approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến review 2026-09-16 — HOLD_ALL theo VPI.
- T2 14/09 = ex-date DGC cổ tức tiền 8.000đ (ZaloPay). xcheck NAV tối 14/09 SẼ chặn theo kỳ vọng
  (46.750−8.000=38.750). Xử TAY theo kb/ops_runbook.md § PRICE_XCHECK, KHÔNG hỏi lại user.
  Cổ tức TIỀN = kỳ vọng (mark giá CUM); cổ tức CỔ PHIẾU/thưởng/tách = VẪN CHẶN, cần người.
- Cron 19:50 ICT nav_snapshot_daily.sh (đường ghi NAV thứ 2, idempotent). Tối T2 14/09 lần đầu
  chạy thật — ca DGC ex-date sẽ rc=4 → marker ⏳, KHÔNG phải lỗi.

## ⏰ VIỆC CỦA MIKE CHIỀU T2 14/09 ≥15:00 ICT — KHÔNG CÓ SCHEDULER, PHẢI TỰ NHỚ
Checklist đầy đủ theo thứ tự (mọi patch đã arch-review APPROVE, apply tuần tự, mỗi bước selfcheck
+ commit riêng theo header patch):
1. v2 batch1-item1: `git -C /home/trido/thanhdt apply agents/Taylor/research/cq20260913_batch1_item1_v2.patch`
   (thay v1). Selfcheck loan_package_multi_account 44/44 + quét §23 50 file. Commit ghi rõ:
   dnse_order_test.py nay gửi 1841 cho SpaceX thay vì 1258 (đổi hành vi đường tiền, đúng).
   ⚠️ v2 KHÔNG đóng hết lỗ hổng loan_package_id (xem retro-2026-09-13 sự cố #2 — fix
   `_account_default_lp()` tra theo account_id CHƯA áp dụng, còn hở, chờ riêng).
2. remove_v23: `git -C /home/trido/thanhdt apply --index agents/Taylor/research/cq20260913_remove_v23.patch`
   (BẮT BUỘC --index, có rename). + mike docs patch (DollarBill/CLAUDE.md,
   MIKE_ext.md, coding_guidelines_ext.md — chỉ text). + production_manifest.py để hết WARN.
3. plan_funding_gate fee sync: `agents/Taylor/research/aria_H_20260913/plan_funding_gate_fee.patch`.
   Selfcheck plan_funding_gate 103/0 + plan_cash_commitment 65/0. Copy
   plan_funding_gate_fee_sync_selfcheck.py vào mike/bin sau khi land.
4. executor ATC post-close: `agents/Taylor/research/aria_K_20260913/executor_atc_postclose.patch`.
   Selfcheck 46/46 + quét §23. ⚠️ **GAP MỚI (Wags verify retro 09-13, bus question
   `aria-K-heartbeat-once-dependency` CÒN MỞ)**: patch chỉ có tác dụng khi bot vào phase CLOSED,
   nhưng `run_bot.sh` luôn chạy `--once` (từ 08-18) trong khi patch cần bot chạy KHÔNG `--once`
   (`_restart_bot` của heartbeat mới thoả). TRƯỚC KHI coi patch "đã bảo vệ production", xác nhận
   đường chạy thật nào đang active (`--once` hay không) — nếu không rõ, hỏi Taylor/tự kiểm
   `crontab -l` + `run_bot.sh` xem có truyền `--once` hay không, và trả lời câu hỏi bus đó.
   Sau đó chạy tay `backfill_vhc_0710.py --apply` 1 lần (verify_account_snapshot ZaloPay 07-10
   sẽ rc 0→1 tạm thời do raw 1200 vs journal 1800 cho tới khi backfill).
5. dispatch Wags quét ~28 file bin/*.py dirname×3 → wc_paths (còn treo từ trước).

## Retro 09-13 đóng (c74dfbee). Pattern "code-quality-weekly/review chủ động = kênh phát hiện
chính cho bug latent money-adjacent" tái diễn lần 2 (lần 1: retro-09-06) — chưa escalate,
theo dõi tiếp 09-14.
## Sự cố #3 retro-09-13 (executor ATC post-close, mất 34,5tr VND VHC 07-10) — patch sẵn sàng
nhưng CHƯA land, và hiệu lực thật phụ thuộc câu hỏi bus còn mở ở trên (mục 4).
## Sự cố #2 retro-09-13 (loan_package_id fallback 1258 latent, SpaceX) — CÒN HỞ có chủ đích,
chưa land, chưa ai bị mất tiền vì nó.
## Còn mở không khẩn: ~28 file bin/*.py dirname-x3; job_cancel_guard nhánh systemd luôn đỏ
dưới cron; append_event.sh JSON isolation (pattern đã biết, không escalate).
## Sát ngưỡng OKF: kb/coding_guidelines.md ~40KB — §-mới PHẢI tách _ext.md.

