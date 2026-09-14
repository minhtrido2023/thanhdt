# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy
  approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến review 2026-09-16 — HOLD_ALL theo VPI.

## ✅ CHIỀU T2 14/09 — LANDING XONG 15:30 ICT (6 commit + 1 finding)
1. loan-package v2 (WC 99fd8f6d): SpaceX resolve theo account_id. Selfcheck 44/44.
2. remove v23 (WC e802c08c, mike 06913f1c+652f5bd0): archive bot_prepare_plan/capit_exit_floor.
   Sweep 48 file: 47/48 rc=0, 1 FAIL có sẵn tái hiện y hệt (không do patch).
3. fee gate 0,097% (WC 90053064, mike 3484a8af khoá đồng bộ): plan_funding_gate 103/0,
   plan_cash_commitment 65/0, sync-lock 3/3.
4. ATC post-close (executor.py) — KHÔNG có commit mới: nội dung ĐÃ CÓ SẴN trong auto-backup
   003c5717 (00:03 ICT 14/09), TRƯỚC KHI user duyệt task này chiều nay. Nguyên nhân: Taylor job
   091014 test/apply patch trực tiếp trên working tree thật (không qua worktree riêng) rồi không
   revert; cron auto-backup quét vào. Đã xác minh: đúng bản v2 arch-APPROVE (plan_date+is_holiday
   gate, await_atc, ATC_POSTCLOSE_ERROR wrapper), selfcheck 46/46 PASS, sweep 22 file executor-dep
   rc=0. Bus finding "aria-K-landing-2026-09-14". CẢNH BÁO QUY TRÌNH: nhắc Taylor không test/apply
   patch trên working tree thật ngoài worktree riêng.
5. backfill_vhc_0710.py: VẪN dry-run, CHƯA --apply (đúng khuyến nghị — verify_account_snapshot sẽ
   rc 0→1 nếu apply, cần việc nhỏ khác trước).
Dispatch Wags_20260914_082709 (bg): quét 28 file dirname-x3 → wc_paths (việc treo cũ, không khẩn).

## Retro 09-13 đóng (c74dfbee). Sự cố #2 (loan_package fallback 1258) + #3 (ATC post-close) NAY ĐÃ
LAND — đóng cả 2 mục "CÒN HỞ/chưa land" trong retro đó.
## Còn mở không khẩn: job_cancel_guard nhánh systemd luôn đỏ dưới cron; append_event.sh JSON
isolation (pattern đã biết, không escalate).
## Sát ngưỡng OKF: kb/coding_guidelines.md ~40KB — §-mới PHẢI tách _ext.md.

