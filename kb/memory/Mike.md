# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-17T23:26 ICT

## Plan 08-18 — ĐÃ DUYỆT, cả 2 HOLD ALL (không đổi)
- approved_by ghi vào cả 2 file, verify qua production loader: block_reason=None cả 2 account.
  0 lệnh cả 2. TV1 đã đạt target cả 2 account (2.300cp SpaceX / DRI+TV1 ~9-10% NAV mỗi bên) —
  injector 20:30 ICT không cần chèn gì thêm, đã phản ánh đúng trong plan 08-18.

## Đã đóng đêm nay (rà lại việc còn hở từ phiên trước)
- Item "Selfcheck-masking E5 capit_lever" → XÁC NHẬN đã merge (`d73e673d`, 08-17 07:55 UTC,
  pin fill_timing_hybrid_enabled=False tại điểm dựng config, sweep 45/60 PASS, 15 fail = thiếu
  artifact worktree không phải hồi quy).
- Item "EOD daily report chưa gửi email" → XÁC NHẬN đã đóng: report_delivery_gate.py báo
  COMPLETE cho cả SpaceX_daily_report_2026-08-17.md và ZaloPay_daily_report_2026-08-17.md
  (Discord + email đều có hash-bound proof).
- Winston_20260817_122149 (VHM 1:1 corp-action ops-autofix) — job record "orphaned" (không ai
  ghi status kết thúc) nhưng ĐÃ verify việc THẬT xong: commit ced702ac, finding ops-autofix-done
  12:31Z xác nhận gate 0.78%→0.00%, shares_outstanding_live VHM đúng. reap tự động đã đóng record.

## Việc còn hở (ưu tiên giảm dần)
1. **DISPATCHED, đang chạy**: Taylor điều tra verify_account_snapshot.py trả cost-basis=0 CẢ 2
   account, mọi vị thế gắn "no fill history (legacy)" — kể cả TV1/DRI/SCL mua SAU go-live (đáng
   ngờ, có thể bug filter account_no/journal path §12, không chỉ "vị thế cũ"). Job
   `Taylor_20260817_162530`, --bg timeout 2400s, dispatch 23:25 ICT. Theo dõi qua
   `bin/jobs.sh status Taylor_20260817_162530`.
2. GDKHQ dry-run D1-D3 chưa setup — apply_exdate_gate() vẫn chưa wire vào executor thật. BID
   08-17 đã qua an toàn (áp thủ công vào sổ lô). Cần quyết trước GDKHQ tiếp theo: VIX 08-20
   (còn 3 phiên).
3. book_breakdown_current trong plan_SpaceX_2026-08-17.json ghi nhãn sai (SCL coi là ngoài
   custom30V, thực tế park_holdings phân loại LAG 3,60% active_nav) — không đổi lệnh nào, chỉ
   nhãn sai, sửa ở lần lặp plan sau.
4. plan-dd-check-string fix (commit 9a9dbb1) — cần ngày có LAG/BAL entry mới để verify đường
   code thật chạy qua nhánh đã vá.
5. Order-book Pha 0 telemetry (commit d6346efd) — kiểm probe N>0/valid>0 sau phiên có giao dịch
   thật (08-18 dự kiến 0 lệnh nên chưa test được, chờ phiên có BAL/LAG).
6. lag_entry_anchor.py:105 — đọc thẳng ticker.Price làm trần ràng buộc (bẫy stale-on-exdate),
   chưa vá, không khẩn (Winston nêu trong finding ops-autofix-done 08-17).

## Bối cảnh còn hiệu lực
- dispatch-prompt-heredoc skill; dispatch job >2 phút BẮT BUỘC --bg.
- TV1 Rule A (bản fix UPCOM) LIVE từ 08-15, an toàn, đã đạt target.
- CASH_VENDOR gate: giữ ĐÓNG. CAPIT margin: enabled=false.
- Quy trình Discord: báo nhận việc ngay, progress 1-2 phút/lần, ScheduleWakeup khi chưa xong.

