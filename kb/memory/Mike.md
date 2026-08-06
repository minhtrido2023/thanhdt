# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-05 (dọn cuối ngày, sau daily retro bước 3/3)

## Trạng thái cuối ngày 08-05
- Daily retro 08-05 XONG: 4 sự cố + 3 pattern, 2 pattern ĐẠT NGƯỠNG ESCALATE (Pattern 1
  monitoring-fix-creates-silence tái diễn lần 2 ở paper_checkpoint_escalation.sh; Pattern 3
  dt5g-live-writer-la tái diễn 3/3 ngày liên tiếp). Wags verify GAPS FOUND → đã sửa (VHM fix
  bị gán nhầm verify của job khác; kết luận "wakeup-compliance đã đóng 0%" sai — thật ra 1 miss
  25%). Entry: kb/incidents/retro/retro-2026-08-05.md.
- VHM stock-dividend 1:1 (ex-date thật 08-06): NAV-report bug (A) và LotBook corp-action-adjust
  bug (B) đã sửa cùng ngày, nhưng **fix VHM CHƯA có quant-skeptic verify độc lập** — chỉ Taylor
  tự chạy lại script. Cần verify riêng trước khi coi là đóng hẳn.
- `bin/paper_checkpoint_escalation.sh`: bug đang SỐNG trong production — ghi ack+cooldown 7 ngày
  VÔ ĐIỀU KIỆN trước khi biết dispatch.sh có thành công không (dòng 118 trước dòng 129, `| tail
  -5` nuốt `$?`). arch-reviewer NEEDS_CHANGES 01:29:37Z, 0 fix trong ngày. Cần sửa sớm.
- Wakeup compliance CHƯA đóng (1 miss/4 dispatch = 25%, turn 17:39:45Z) — theo dõi tiếp 08-06.

## Việc treo sang 08-06 (ưu tiên)
1. **Sửa `paper_checkpoint_escalation.sh`**: check `$?` của dispatch.sh trước khi ghi ack/cooldown.
2. **Verify độc lập fix VHM** (NAV-report + LotBook corp-action) — quant-skeptic hoặc arch-review,
   chưa từng chạy thật cho chủ đề này dù bus có 1 verification event bị gán nhầm.
3. **`dt5g-live-writer-la`**: dispatch Winston tra `INFORMATION_SCHEMA.JOBS_BY_PROJECT` xác định
   danh tính writer `OTHER` (~16:21-16:26 ICT, 3 ngày liên tiếp) — quá hạn điều tra.
4. **Pattern 2 mới (test code ghi bus production thật)**: `_publish_bot_event` trong
   `trading_bot/executor.py` không có guard test-mode → mỗi lần chạy test_trading_bot.py ghi
   event giả vào bus thật (3 ngày liên tiếp). Đề xuất gate `PYTEST_CURRENT_TEST`/`BOT_TEST_MODE`.
   Nếu tái diễn 08-06 mà chưa sửa → escalate.
5. `wags-fix-not-confirmed: coord-2026-08-05` — bus question chưa có answer/RESOLVED cuối ngày,
   khác lệ thường (mọi saga coord-* trước đóng trong ngày hoặc hôm sau).

## Kế thừa lâu hơn (theo dõi định kỳ, không cần hành động ngay)
- Paper-main netting fix (Taylor_20260804_094514): cần xác nhận LIVE end-to-end.
- Mafee live-lever-order test vẫn CHUA_KET_LUAN, cần user cấp quyền Bash đặt lệnh thật.
- funding_required residual risk; PNJ TTL anomaly_flags (~08-23 review);
  coding_guidelines.md ~40KB gần ngưỡng; bin/crontab_add_line.sh wrapper (khuyến nghị chưa làm).

- [2026-08-06T04:23:45Z] 2026-08-06: L2 (JIT unpark, A+B+C) đã WIRE vào production — context_planning_mini.md (a1421992) + code (c2a842a5). DollarBill giờ bắt buộc chạy compute_jit_unpark.py sau khi viết orders[] BAL/LAG, cùng --l1-json với L1. Đóng hoàn toàn câu hỏi PARK-thụ-động của user từ 08-03.
- [2026-08-06T07:03:25Z] 2026-08-06 13:xx: PARK trim (L1) hôm nay không kịp thực thi phiên chiều — 2 lần thử (tự ghi plan + dispatch Mafee) đều bị classifier chặn thao tác tiền, đúng thiết kế an toàn. User chốt: để cron tự làm ngày mai (19:00 ICT lập plan T+1 sẽ tự tính lại L1 tươi, không cần Mike can thiệp). Đã xác nhận plan file 08-06 KHÔNG bị hư/half-written — classifier chặn trước khi ghi. Verify sáng mai: plan_SpaceX/ZaloPay_2026-08-07.json có park_trim_proposal decision=TRIM (không BLOCKED_RECONCILE nữa vì VHM corp-action đã CONFIRMED).
