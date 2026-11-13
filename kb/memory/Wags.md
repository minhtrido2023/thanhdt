# Working memory — Wags
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Wags.

# Working memory — Wags
> Sổ tay việc ĐANG MỞ. File này bơm vào đầu MỌI phiên/dispatch của Wags ⇒ mỗi dòng thừa là
> context phải trả tiền lại từ đầu, mỗi lần.

## Ghi gì vào đây (đọc 1 lần)
- Chỉ 2 loại: (a) việc CÒN TREO — đang chờ ai, chờ gì; (b) chốt làm ĐỔI CÁCH LÀM về sau.
- KHÔNG ghi "job X XONG, commit Y". git log + bus + `agents/Wags/research/` đã giữ đủ; chép lại
  vào đây chỉ làm mọi phiên sau phải đọc lại một lần nữa.
- Mỗi entry ≤ 2 dòng: KẾT LUẬN trước, bỏ quá trình.
- Việc treo mà xong rồi thì XOÁ dòng đó, đừng ghi đè một dòng "đã xong" lên trên.
- Quy tắc dùng cho CẢ ĐỘI ⇒ đề xuất vào `kb/coding_guidelines.md` (§13: ghi ra `.proposed`),
  không nuôi riêng trong file này.
- Quá 12 entry thì phần cũ tự sang `kb/memory/archive/Wags_history.md` — không mất, không auto-load.

- [2026-10-26T01:21:37Z] [2026-10-26] Câu Mike/retro-pattern-recurring-wakeup-warning-nonblocking-still-missed CHỜ USER A/B/C (đã relay); trả lời => close_bus_question --decided-by-user. Checker sẽ còn báo tới khi user trả lời — không phải bug.
- [2026-10-30T01:20:36Z] [2026-10-30] Câu Mike/retro-pattern-recurring-drift-checker-runs-before-evidence CHỜ USER A/B (đã relay 29/10 17:31Z); trả lời => close_bus_question --decided-by-user; A => sửa plan_position_drift_check + dời cron (cần duyệt).
- [2026-11-03T01:20:42Z] [2026-11-03] Câu Taylor/pnj-bctc-q3-review-trigger CHỜ USER A/B (đã relay Discord 02/11 qua pnj_q3_review_watch). User trả lời ⇒ close_bus_question --decided-by-user; checker báo tới lúc đó là đúng, không phải bug.
- [2026-11-05T06:35:00Z] [2026-11-05] Câu Mike/retro-pattern-recurring-dd-multi-round-assumption-unlocked CHỜ USER A/B/C. Đóng: close_bus_question.py "Mike/retro-pattern-recurring-dd-multi-round-assumption-unlocked" --resolution '<A/B/C+tóm tắt>' --evidence '<commit SKILL.md|lý do C>' --decided-by-user. A/B ⇒ sửa ~/.claude/skills/due-diligence/SKILL.md GỘP 1 lần với DD_SKILL_PROPOSAL.md của Taylor (lock giả định=bước 0, macro sau lấy BCTC).
- [2026-11-09T01:30:41Z] [2026-11-09] Câu Mike/retro-pattern-recurring-anomaly-flags-stale-weekend-false-alarm CHỜ USER A/B/C (checker trong golive_recommend_v23.py = trading, Wags không sửa). User trả lời ⇒ close_bus_question --decided-by-user. Gặp OAuth expired hàng loạt ⇒ đóng các câu hệ quả bằng bằng chứng, đừng sửa code.
- [2026-11-11T01:20:43Z] [2026-11-11] Câu Mike/retro-pattern-recurring-bg-dispatch-wakeup-miss-gate-checks-declaration-only CHỜ USER A/B/C (đã relay 10/11). Trả lời ⇒ close_bus_question --decided-by-user; A ⇒ mở rộng hooks/stop.sh (hiện chỉ Mike) + arch-reviewer.
- [2026-11-11T03:57:45Z] [2026-11-11] Xong G2 stop-hook wakeup (4e2cfe867); cau retro bg-dispatch-wakeup-miss da dong. Neu MISS con tai dien: kiem wakeup_audit sau fix (queue-op artifact).
- [2026-11-13T11:32:47Z] [2026-11-13] GH001 xong: master f1e5e9d31 + mike-fleet đã push. Bundle + /home/trido/git_bundles/rw_20261113b.git giữ tới khi Mike verify xong (chưa gc). book-clearing PARKED 36ffb5449 CHỜ USER. Taylor việc(2) annualization chưa làm.
- [2026-11-13T12:24:21Z] [2026-11-13] annualization XANH (c2f5862c2, verify rc=0). Sweep selfcheck-red còn: book_clearing_g3 PARKED 36ffb5449 CHỜ USER.
- [2026-11-13T12:28:36Z] [13/11] book_clearing fix 36ffb5449 (arch APPROVED) CHỜ USER A/B qua question Wags/selfcheck-red-sweep-20261113-book-clearing-merge-approval; A ⇒ merge vào master + close_bus_question 'Wags/selfcheck-red: mike/bin/book_clearing_g3_selfcheck.py'. Đĩa / 96% cần dọn.
