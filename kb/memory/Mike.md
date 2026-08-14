# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-14T05:07Z

## Đang chờ (job nền)
- Wags_20260814_050658 (--bg, opus/high, max-turns 160): 3 việc rẻ arch-reviewer đề xuất thay
  problem_key/supersession — (1) sửa 2 chỗ nuốt exit code trong wags_autofix.sh, (2) miễn cắt
  aged_q digest cho lớp wags-fix-not-confirmed (đang bị cắt khúc giữa khi backlog >10), (3)
  mirror quyết định off-bus (Discord dispatch) về lại bus event. User: "đồng ý làm 3 việc rẻ
  rồi quay lại problem_key" — SAU KHI xong 3 việc này, hỏi lại user có muốn tiếp tục thiết kế
  problem_key/supersession không (đã bị arch-reviewer NEEDS_CHANGES ở dạng gốc, cần thiết kế
  lại đáng kể — xem agents/Wags/research/cross_topic_closure_architecture_20260814.md +
  verdict arch-reviewer trong bus/inbox/arch-reviewer.jsonl 2026-08-14T~04:5x).

## Việc vừa xong trong phiên này (2026-08-14, mạch "warning vận hành lặp lại")
- kb/coding_guidelines.md tách OKF → coding_guidelines_ext.md (Taylor, commit 13ca74bd),
  48.7KB→33.4KB, fact-check 0 mất. Bus context-bloat-same-day đã đóng.
- dt5g_writer_watch KAFFA_WINDOW false-alarm: code đã đúng từ 08-06 (2c77cf07), Winston verify
  lại + đóng bus retro-pattern-recurring-dt5g-live-writer-la-3 (decided_by=user).
- 3/4 mục wags-fix-not-confirmed cũ (coord-08-07/08-10/08-11) — Wags fix THẬT (không phải chỉ
  đóng loop), Mike verify artifact + tự post 3 decision đóng bus (job Wags gốc timeout trước
  khi kịp tự ghi).
- notify_thread.sh mất tin nhắn — đã tự fix từ 08-12 (swap-arg detection, commit 6226c411),
  15/15 selfcheck PASS, không cần làm gì thêm.

## Bối cảnh còn hiệu lực
- TV1 mới đạt 61%(SpaceX)/50%(ZaloPay) kế hoạch 08-13 — chưa quyết mua nốt hay coi đã đóng.
- `merge_park_orders.py` cron schedule — Taylor đề xuất C-rồi-A, chưa cài chính thức.
- corp_action_daily.py SANITY_FACTOR WARN (phương án C) đã đóng 08-14, quant-skeptic CONFIRMED.

