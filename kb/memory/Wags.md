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

- [2026-11-05T06:35:00Z] [2026-11-05] Câu Mike/retro-pattern-recurring-dd-multi-round-assumption-unlocked CHỜ USER A/B/C. Đóng: close_bus_question.py "Mike/retro-pattern-recurring-dd-multi-round-assumption-unlocked" --resolution '<A/B/C+tóm tắt>' --evidence '<commit SKILL.md|lý do C>' --decided-by-user. A/B ⇒ sửa ~/.claude/skills/due-diligence/SKILL.md GỘP 1 lần với DD_SKILL_PROPOSAL.md của Taylor (lock giả định=bước 0, macro sau lấy BCTC).
- [2026-11-09T01:30:41Z] [2026-11-09] Câu Mike/retro-pattern-recurring-anomaly-flags-stale-weekend-false-alarm CHỜ USER A/B/C (checker trong golive_recommend_v23.py = trading, Wags không sửa). User trả lời ⇒ close_bus_question --decided-by-user. Gặp OAuth expired hàng loạt ⇒ đóng các câu hệ quả bằng bằng chứng, đừng sửa code.
- [2026-11-11T01:20:43Z] [2026-11-11] Câu Mike/retro-pattern-recurring-bg-dispatch-wakeup-miss-gate-checks-declaration-only CHỜ USER A/B/C (đã relay 10/11). Trả lời ⇒ close_bus_question --decided-by-user; A ⇒ mở rộng hooks/stop.sh (hiện chỉ Mike) + arch-reviewer.
- [2026-11-11T03:57:45Z] [2026-11-11] Xong G2 stop-hook wakeup (4e2cfe867); cau retro bg-dispatch-wakeup-miss da dong. Neu MISS con tai dien: kiem wakeup_audit sau fix (queue-op artifact).
- [2026-11-13T11:32:47Z] [2026-11-13] GH001 xong: master f1e5e9d31 + mike-fleet đã push. Bundle + /home/trido/git_bundles/rw_20261113b.git giữ tới khi Mike verify xong (chưa gc). book-clearing PARKED 36ffb5449 CHỜ USER. Taylor việc(2) annualization chưa làm.
- [2026-11-13T12:24:21Z] [2026-11-13] annualization XANH (c2f5862c2, verify rc=0). Sweep selfcheck-red còn: book_clearing_g3 PARKED 36ffb5449 CHỜ USER.
- [2026-11-13T12:28:36Z] [13/11] book_clearing fix 36ffb5449 (arch APPROVED) CHỜ USER A/B qua question Wags/selfcheck-red-sweep-20261113-book-clearing-merge-approval; A ⇒ merge vào master + close_bus_question 'Wags/selfcheck-red: mike/bin/book_clearing_g3_selfcheck.py'. Đĩa / 96% cần dọn.
- [2026-11-17T01:20:57Z] [2026-11-17] Câu Mike/retro-pattern-recurring-bq-raw-gap-wire-0b-unmerged CHỜ USER A/B (relay 16/11 17:31Z). A ⇒ wire [0b] ticker_integrity_precheck vào bq_freshness_check.sh sau step [0] + arch-reviewer, rồi close_bus_question --decided-by-user. Checker báo tới lúc đó là đúng.
- [2026-11-20T10:07:07Z] [2026-11-20] Chờ user A/B: weekly_orphan_review bảo vệ cả thư mục ⇒ TRIM_DD gần tắt cho 36/57 dd_* (~1,9GB); B = guard mức file trong nhánh is_dd (weekly_orphan_review.py ~125). Nêu trong finding selfcheck-red-owner-sweep-2026-11-20-Wags.
- [2026-11-25T02:32:19Z] [25/11] Plan-gate VÒNG CUỐI xong nhánh wags/plan-gate-rootfix-20261125 (mike 60bbabfa7, outer bbecd22bd), CHƯA merge — chờ arch-reviewer + user; merge mike trước outer; cron theo kb/cron_registry.md (có source wc_env.sh).
- [2026-11-27T01:20:37Z] [27/11] Cau Mike/retro-pattern-recurring-guard-judges-by-proxy-not-artifact CHO USER A/B/C (relay 26/11 17:33Z). Tra loi => close_bus_question --decided-by-user; A => checklist guard arch-review + sua 2 ca (plan resend md5, PIPELINE STALE).
- [2026-11-27T10:57:01Z] [27/11] Sweep selfcheck-red: 7/8 dong. CHO USER A/B: production_manifest (A = them kb/production_manifest.md vao SIZE_EXEMPT bin/okf_lint_gate.py [bi permission classifier chan, can user duyet ro]; B = rut .md <40KB) roi chay bin/production_manifest.py, commit, dong cau selfcheck-red.
