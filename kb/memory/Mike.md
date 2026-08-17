# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-17T21:18 ICT (2 plan 08-18 ĐÃ DUYỆT)

## Plan 08-18 — ĐÃ DUYỆT, cả 2 HOLD ALL
- approved_by ghi vào cả 2 file (John Dinh qua Discord, Mike ghi hộ 21:18 ICT). Verify qua
  production loader: block_reason=None cả 2 account. 0 lệnh cả 2 — chỉ theo dõi injector TV1
  20:30 ICT tối nay như thường lệ.

## Việc còn hở (chưa xử lý, không khẩn)
1. GDKHQ dry-run D1-D3 chưa setup (BID GDKHQ đã qua 08-17 an toàn, apply_exdate_gate() vẫn
   chưa wire vào executor thật) — cần quyết trước GDKHQ tiếp theo (VIX 08-20).
2. verify_account_snapshot.py trả cost-basis 0 cho CẢ 2 account ("no fill history legacy") —
   pipeline §6 gap thật, cần điều tra.
3. book_breakdown_current trong plan file ghi nhãn sai (SCL không phải LAG, thật ra LÀ LAG).
4. Selfcheck-masking E5 capit_lever — Taylor báo đã vá xong (merge d73e673d 08-17), xác nhận.
5. plan-dd-check-string fix (commit 9a9dbb1) — cần ngày có LAG/BAL để verify đường code thật.
6. Order-book Pha 0 telemetry (commit d6346efd) — kiểm probe N>0/valid>0 sau phiên 08-18.
7. EOD daily report chưa bao giờ gửi email.
8. lag_entry_anchor.py:105 — chưa vá, không khẩn.

## Bối cảnh còn hiệu lực
- dispatch-prompt-heredoc skill; dispatch job >2 phút BẮT BUỘC --bg.
- TV1 Rule A (bản fix UPCOM) đang LIVE từ 08-15, an toàn. TV1 đã đạt target (2.300cp, fill
  09:15 08-17), DRI đã đạt 5% NAV cả 2 account.
- CASH_VENDOR gate: giữ ĐÓNG. CAPIT margin: enabled=false.
- Quy trình Discord: báo nhận việc ngay, progress 1-2 phút/lần, ScheduleWakeup khi chưa xong.

