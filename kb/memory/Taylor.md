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

- [2026-10-21T04:31:09Z] [survivorship-volzero F1-F3 10-21] XONG commit c7cef9792, chờ Mike/skeptic. Mở: phần dư OOS F2 (+39..+64 tỷ lô khớp được) chưa phân rã; F2F1 hậu kỳ cần prereg nếu dùng.
- [2026-10-21T05:35:39Z] [vnindex-tr vòng 2 10-21] XONG job Taylor_20261021_052419: nhánh fix/vnindex-tr-restate-sealed-20261021 @577d605cd chờ Mike arch-review/merge; chuỗi thật đã đính chính 12-13/10 (md5 51cd88f4), không cần ack 14/10. (Thay dòng ĐANG DỞ 052419 + dòng mở 022501.)
- [2026-10-21T05:49:29Z] [vnindex-tr vòng 2 arch-review 10-21] XONG job Taylor_20261021_054437, nhánh fix/vnindex-tr-restate-sealed-20261021 chờ Mike merge; hết vòng 2 — còn NEEDS_CHANGES thì dừng báo user
- [2026-10-21T10:41:15Z] [lag-entry-window-width 10-21] XONG job Taylor_20261021_102832: giữ 3 phiên; lỗ hổng = vận hành phiên chuẩn (WAIT_CASH 58%, lỗi lịch 21%). Mở: chạy lại audit_live.py sau mùa Q3 (~11-15) — mẫu đầu tiên dưới Luật A.
- [2026-10-21T11:51:40Z] [lag-calendar-dd 10-21] XONG job Taylor_20261021_114050: nhanh fix/lag-calendar-dd-checker-20261021 @d3020f553 (worktree wt-lag-cal-dd-20261021) cho Mike arch-review/merge truoc 24/10; mo: checker chi co, chua chan.
- [2026-10-21T15:13:13Z] ĐANG DỞ job Taylor_20261021_151302: cổng DD LAG (lag_dd_pack.py + ack + checker) + thí điểm HT1/SCL/VPB | NEXT: đọc due_diligence.py, consistency_check, context_planning_mini
- [2026-10-21T15:28:14Z] ĐANG DỞ job Taylor_20261021_151302: pilot XONG (HT1 CLEARED, SCL/VPB FLAG; commit 9ea37eaaa, nhánh feat/lag-dd-gate-20261021, worktree wt-lag-dd-gate-20261021) | NEXT: hợp đồng context_planning_mini + đề xuất cron/hook + finding 2
- [2026-10-21T15:32:46Z] [lag-dd-gate 10-21] XONG job Taylor_20261021_151302: nhánh feat/lag-dd-gate-20261021 @a97873036 (worktree wt-lag-dd-gate-20261021) chờ Mike arch-review/merge trước 24/10; mở: hook 19:00 + chặn cứng tầng order chờ user duyệt
- [2026-10-21T15:42:39Z] [vnindex-tr polish 10-21] XONG job Taylor_20261021_153755: nhánh fix/vnindex-tr-polish-20261021 @f0645f5e1 (wt_vnindex_tr_polish_20261021) chờ Mike arch-review/merge + áp runbook.proposed
- [2026-10-21T15:50:09Z] [lag-dd-gate vòng 2 10-21] XONG job Taylor_20261021_154311: nhánh feat/lag-dd-gate-20261021 @9969df217 chờ Mike arch-review vòng 3; VPB pilot đổi FLAG->CLEARED (anomaly quá TTL)
- [2026-10-21T16:54:22Z] ĐANG DỞ job Taylor_20261021_165411: vá cổng khối lượng compute_active_nav đọc thêm dnse_khoplenh_broker_confirm | NEXT: worktree fix/active-nav-broker-fills-20261021
- [2026-10-21T16:55:22Z] ĐANG DỞ job Taylor_20261021_165512: VIỆC A (EQ_PHAI_THU_TANG tách trả trước) + B (audit quyền mua) | NEXT: worktree wt-lag-rights-20261022, tra ticker_financial cột AR
- [2026-10-21T16:55:24Z] ĐANG DỞ job Taylor_20261021_165514: LAG per-share surprise + rủi ro quyền mua (paper) | out mike/agents/Taylor/research/lag_per_share_surprise_rights_20261022 | NEXT: PREREG rồi Q1-Q4
- [2026-10-21T16:59:36Z] [active-nav-broker-fills 10-21] XONG job Taylor_20261021_165411: nhánh fix/active-nav-broker-fills-20261021 @2f956fb2f (wt-active-nav-broker-fills-20261021) chờ Mike arch-review/merge; sau merge cần chạy compute_active_nav thật để làm mới active_nav. (Thay dòng ĐANG DỞ 165411.)
- [2026-10-21T17:17:55Z] [lag-per-share-rights 10-22] XONG job Taylor_20261021_165514 (commit 21c10df2f): PS2 HI->LO -4.6pp (N=60) chờ Mike quant-skeptic; mở: full-engine test tầng PS2 nếu duyệt
