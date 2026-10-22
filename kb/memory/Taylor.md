# Working memory — Taylor
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Taylor.

> Sổ tay việc ĐANG MỞ. File này bơm vào đầu MỌI phiên/dispatch của Taylor ⇒ mỗi dòng thừa là
> context phải trả tiền lại từ đầu, mỗi lần.

## Ghi gì vào đây (đọc 1 lần)
- Chỉ 2 loại: (a) việc CÒN TREO — đang chờ ai, chờ gì; (b) chốt làm ĐỔI CÁCH LÀM về sau.
- KHÔNG ghi "job X XONG, commit Y". git log + bus + `agents/Taylor/research/` đã giữ đủ; chép lại
  vào đây chỉ làm mọi phiên sau phải đọc lại một lần nữa.
- Mỗi entry ≤ 2 dòng: KẾT LUẬN trước, bỏ quá trình.
- Việc treo mà xong rồi thì XOÁ dòng đó, đừng ghi đè một dòng "đã xong" lên trên.
- Quy tắc dùng cho CẢ ĐỘI ⇒ đề xuất vào `kb/coding_guidelines.md` (§13: ghi ra `.proposed`),
  không nuôi riêng trong file này.
- Quá 12 entry thì phần cũ tự sang `kb/memory/archive/Taylor_history.md` — không mất, không auto-load.

- [2026-10-21T16:59:36Z] [active-nav-broker-fills 10-21] XONG job Taylor_20261021_165411: nhánh fix/active-nav-broker-fills-20261021 @2f956fb2f (wt-active-nav-broker-fills-20261021) chờ Mike arch-review/merge; sau merge cần chạy compute_active_nav thật để làm mới active_nav. (Thay dòng ĐANG DỞ 165411.)
- [2026-10-21T17:17:55Z] [lag-per-share-rights 10-22] XONG job Taylor_20261021_165514 (commit 21c10df2f): PS2 HI->LO -4.6pp (N=60) chờ Mike quant-skeptic; mở: full-engine test tầng PS2 nếu duyệt
- [2026-10-21T17:19:01Z] [lag-rights-audit 10-22] XONG job Taylor_20261021_165512: nhánh feat/lag-rights-audit-20261022 (wt-lag-rights-20261022) chờ Mike arch-review; mở: N1-N4/X1-X3 cần user duyệt, rights_issue_alert chưa wire
- [2026-10-22T02:29:51Z] ĐANG DỞ job Taylor_20261022_022942: áp patch quyền mua X1,X2,X3,N2,N3 (user duyệt 22/10) | NEXT: đọc REPORT audit, tạo worktree
- [2026-10-22T02:38:30Z] ĐANG DỞ job Taylor_20261022_022942: X1 commit 5ef72c1f7 (nhánh feat/lag-rights-patches-20261022, wt-lag-rights-patches-20261022) | NEXT: X3 corp_actions.load_all, X2, N3, N2, REPORT
- [2026-10-22T02:40:31Z] [rights-alert-wire fix 10-22] XONG job Taylor_20261022_023548: feat/rights-alert-wire-20261022 @f3602417a chờ Mike arch-review/merge
- [2026-10-22T02:48:06Z] ĐANG DỞ job Taylor_20261022_022942 (attempt2): X1,X3,X2,N3 commit tới fee92d83a | NEXT: N2 cổng TERP daily_nav_snapshot, REPORT
- [2026-10-22T02:57:31Z] [lag-rights-patches 10-22] XONG job Taylor_20261022_022942: feat/lag-rights-patches-20261022 @6840c070c (X1,X3,X2,N3,N2) chờ Mike arch-review/merge; N1/N4 còn treo (user/legal)
- [2026-10-22T03:21:59Z] ĐANG DỞ job Taylor_20261022_032141: N1 sổ lô quyền mua (phương án A) + N4 expected_qty | NEXT: đọc audit lag_rights_audit_20261022, tạo worktree wt-lag-rights-n1-20261022
- [2026-10-22T03:52:03Z] [lag-rights-n1 10-22] XONG job Taylor_20261022_032141: feat/lag-rights-n1-20261022 @63e0c11d3 (N1 9c0aa2a34 + N4) chờ Mike arch-review/merge; escalate dòng rác nav_history 10-22 10:00 (race nav_scripts_2account_selfcheck)
- [2026-10-22T04:12:44Z] ĐANG DỞ job Taylor_20261022_041232: vòng 2 arch-review N1/N4 (B1 rights_locked hạn+alert, B2 broker_statement fills) trên feat/lag-rights-n1-20261022 | NEXT: đọc _rights_locked_split, net_fills_journal_and_broker
- [2026-10-22T04:31:50Z] [lag-rights-n1 vòng 2 10-22] XONG job Taylor_20261022_041232: feat/lag-rights-n1-20261022 @fa376eda0 (B1 d25a54510, B2 7941ada71, NB1-3) chờ Mike arch-review/merge; còn treo NB2-reconcile/NB4
