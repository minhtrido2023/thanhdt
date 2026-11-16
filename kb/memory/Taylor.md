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

- [2026-11-15T17:12:53Z] ĐANG DỞ: P1-ARCH-FIX vong2 job Taylor_20261115_170852 worktree agents/Taylor/wt-ai-momentum-p1 (B3 xong chua commit) | NEXT: rewrite ai_momentum_daily.py, wrapper bin/ai_momentum_cron.sh, PREREG_v3_2, selfcheck 3TZ, commit
- [2026-11-15T17:35:27Z] [ai-momentum ARCH-FIX v2 16/11] XONG job Taylor_20261115_170852: nhanh research/ai-momentum-p1-20261115 commit moi; CHO Mike smoke live --ledger-dir tam + arch-review vong 3 + quant-skeptic + user duyet cron
- [2026-11-16T01:30:38Z] [ai-momentum R3 16/11] XONG job Taylor_20261116_011145: commit 2ec32179e nhanh research/ai-momentum-p1-20261115, KHONG merge/cron — CHO Mike smoke live + arch-review vong 3 + user duyet cron
- [2026-11-16T01:33:41Z] [weekly 09-13/11 cadence rescue 16/11] job Taylor_20261116_013304: file chuan da co, CHO waiver Q9 (job 013249) roi chay report_delivery_gate cho SpaceX+ZaloPay (topic trading_report); khong dung lai
- [2026-11-16T01:36:06Z] [cq-medium 16/11] XONG job Taylor_20261116_012626: A fix/fill-lagging-qty-20261116 (60908e01a), B fix/bull-div-boost-shell-20261116 (cd723aa2e) KHONG merge — CHO Mike arch-review + merge; worktree selfcheck rong can bu env gitignored (secrets/accounts, data/trade_plans, mike)
- [2026-11-16T01:37:18Z] [q9-waiver 16/11] XONG job Taylor_20261116_013249: nhanh feat/q9-waiver-20261116 (17db40c3c) KHONG merge — CHO Mike arch-review + merge + chay gate that 2 weekly 09-13/11; waiver het han 2026-11-20
- [2026-11-16T01:58:14Z] [cq vong2 16/11] XONG job Taylor_20261116_014210: A 960c17f97, B 145b9cf92 KHONG merge — CHO Mike arch-review diff-only + merge
- [2026-11-16T03:16:01Z] ĐANG DỞ: job Taylor_20261116_031549 LAG early-exit Bayes | NEXT: buoc 0 -> research/lag_early_exit_bayes_20261116/
- [2026-11-16T03:28:43Z] [lag-early-exit 16/11] XONG job Taylor_20261116_031549: NO-GO thoat som LAG, nhanh research/lag-early-exit-20261116 (f037ad41f) KHONG merge — CHO user chot A (giu T+25) / B (canh bao display-only)
- [2026-11-16T16:21:43Z] ĐANG DỞ: job Taylor_20261116_162132 ORB futures live path (A probe..F spec) | NEXT: khao sat + worktree feat/orb-futures-live-20261116
- [2026-11-16T16:41:16Z] [orb-futures 16/11] XONG job Taylor_20261116_162132: nhanh feat/orb-futures-live-20261116 (outer e9aad9819, mike d91e49d32) KHONG merge/cron, co TAT — CHO Mike arch-review+quant-skeptic; sau do DRY>=10 phien, sua NAV phai sinh truoc khi user nop ky quy
- [2026-11-16T16:50:16Z] ĐANG DỞ: job Taylor_20261116_165006 ORB vong2 sua B1-B4,M1-3,m1-2,N1,spec | NEXT: sua orb_futures.py + selfcheck
