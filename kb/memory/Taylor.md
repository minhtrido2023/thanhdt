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

- [2026-10-21T15:50:09Z] [lag-dd-gate vòng 2 10-21] XONG job Taylor_20261021_154311: nhánh feat/lag-dd-gate-20261021 @9969df217 chờ Mike arch-review vòng 3; VPB pilot đổi FLAG->CLEARED (anomaly quá TTL)
- [2026-10-21T16:54:22Z] ĐANG DỞ job Taylor_20261021_165411: vá cổng khối lượng compute_active_nav đọc thêm dnse_khoplenh_broker_confirm | NEXT: worktree fix/active-nav-broker-fills-20261021
- [2026-10-21T16:55:22Z] ĐANG DỞ job Taylor_20261021_165512: VIỆC A (EQ_PHAI_THU_TANG tách trả trước) + B (audit quyền mua) | NEXT: worktree wt-lag-rights-20261022, tra ticker_financial cột AR
- [2026-10-21T16:55:24Z] ĐANG DỞ job Taylor_20261021_165514: LAG per-share surprise + rủi ro quyền mua (paper) | out mike/agents/Taylor/research/lag_per_share_surprise_rights_20261022 | NEXT: PREREG rồi Q1-Q4
- [2026-10-21T16:59:36Z] [active-nav-broker-fills 10-21] XONG job Taylor_20261021_165411: nhánh fix/active-nav-broker-fills-20261021 @2f956fb2f (wt-active-nav-broker-fills-20261021) chờ Mike arch-review/merge; sau merge cần chạy compute_active_nav thật để làm mới active_nav. (Thay dòng ĐANG DỞ 165411.)
- [2026-10-21T17:17:55Z] [lag-per-share-rights 10-22] XONG job Taylor_20261021_165514 (commit 21c10df2f): PS2 HI->LO -4.6pp (N=60) chờ Mike quant-skeptic; mở: full-engine test tầng PS2 nếu duyệt
- [2026-10-21T17:19:01Z] [lag-rights-audit 10-22] XONG job Taylor_20261021_165512: nhánh feat/lag-rights-audit-20261022 (wt-lag-rights-20261022) chờ Mike arch-review; mở: N1-N4/X1-X3 cần user duyệt, rights_issue_alert chưa wire
- [2026-10-22T02:29:51Z] ĐANG DỞ job Taylor_20261022_022942: áp patch quyền mua X1,X2,X3,N2,N3 (user duyệt 22/10) | NEXT: đọc REPORT audit, tạo worktree
- [2026-10-22T02:38:30Z] ĐANG DỞ job Taylor_20261022_022942: X1 commit 5ef72c1f7 (nhánh feat/lag-rights-patches-20261022, wt-lag-rights-patches-20261022) | NEXT: X3 corp_actions.load_all, X2, N3, N2, REPORT
- [2026-10-22T02:40:31Z] [rights-alert-wire fix 10-22] XONG job Taylor_20261022_023548: feat/rights-alert-wire-20261022 @f3602417a chờ Mike arch-review/merge
- [2026-10-22T02:48:06Z] ĐANG DỞ job Taylor_20261022_022942 (attempt2): X1,X3,X2,N3 commit tới fee92d83a | NEXT: N2 cổng TERP daily_nav_snapshot, REPORT
- [2026-10-22T02:57:31Z] [lag-rights-patches 10-22] XONG job Taylor_20261022_022942: feat/lag-rights-patches-20261022 @6840c070c (X1,X3,X2,N3,N2) chờ Mike arch-review/merge; N1/N4 còn treo (user/legal)
