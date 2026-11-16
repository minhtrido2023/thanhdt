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

- [2026-11-15T14:49:54Z] [ai-momentum plan 15/11] XONG job Taylor_20261115_144310: kb/projects/ai-momentum-research-plan-20261115.md (md5 d72baef6), chua code/chua cron — CHO user tra 4 cau F (muc tieu G-proc vs G-fcst, vu tru, M2, topic) roi moi P0; INDEX.md chua them dong (Mike/consolidator)
- [2026-11-15T15:19:23Z] [ai-momentum P0 15/11] XONG job Taylor_20261115_150627: kb/projects/ai-momentum-p0-result-20261115.md (md5 5101c9cb), PREREG 5d3284d0b — CHO Mike quant-skeptic + user chot (2 nam hay noi nguong) + deepseek provider dang loi
- [2026-11-15T15:58:58Z] [ai-momentum P1 15/11] XONG job Taylor_20261115_154607: nhanh research/ai-momentum-p1-20261115 (b07a773b0) KHONG merge; kb/projects/ai-momentum-p1-build-20261115.md — CHO Mike arch-review/quant-skeptic + user quyet noi nguong x2 (PREREG v3) + Wags xong M2
- [2026-11-15T16:29:29Z] [ai-momentum P1-V3 15/11] XONG job Taylor_20261115_162439: nhanh research/ai-momentum-p1-20261115 (a09b71d5e) KHONG merge; kb/projects/ai-momentum-p1-v3-20261115.md; PREREG_v3 md5 d07ffcfd — CHO Mike arch-review/quant-skeptic + Wags xong M2 truoc khi cron
- [2026-11-15T16:46:25Z] [ai-momentum P1-M2-WIRE 15/11] XONG job Taylor_20261115_163050: nhanh research/ai-momentum-p1-20261115 (efd12cbcd, da merge wags/m2-wrapper) KHONG merge master/cron; M2 OK 2/2 retro that; kb/projects/ai-momentum-p1-v3-20261115.md muc M2 — CHO Mike arch-review + user duyet cron
- [2026-11-15T17:12:53Z] ĐANG DỞ: P1-ARCH-FIX vong2 job Taylor_20261115_170852 worktree agents/Taylor/wt-ai-momentum-p1 (B3 xong chua commit) | NEXT: rewrite ai_momentum_daily.py, wrapper bin/ai_momentum_cron.sh, PREREG_v3_2, selfcheck 3TZ, commit
- [2026-11-15T17:35:27Z] [ai-momentum ARCH-FIX v2 16/11] XONG job Taylor_20261115_170852: nhanh research/ai-momentum-p1-20261115 commit moi; CHO Mike smoke live --ledger-dir tam + arch-review vong 3 + quant-skeptic + user duyet cron
- [2026-11-16T01:30:38Z] [ai-momentum R3 16/11] XONG job Taylor_20261116_011145: commit 2ec32179e nhanh research/ai-momentum-p1-20261115, KHONG merge/cron — CHO Mike smoke live + arch-review vong 3 + user duyet cron
- [2026-11-16T01:33:41Z] [weekly 09-13/11 cadence rescue 16/11] job Taylor_20261116_013304: file chuan da co, CHO waiver Q9 (job 013249) roi chay report_delivery_gate cho SpaceX+ZaloPay (topic trading_report); khong dung lai
- [2026-11-16T01:36:06Z] [cq-medium 16/11] XONG job Taylor_20261116_012626: A fix/fill-lagging-qty-20261116 (60908e01a), B fix/bull-div-boost-shell-20261116 (cd723aa2e) KHONG merge — CHO Mike arch-review + merge; worktree selfcheck rong can bu env gitignored (secrets/accounts, data/trade_plans, mike)
- [2026-11-16T01:37:18Z] [q9-waiver 16/11] XONG job Taylor_20261116_013249: nhanh feat/q9-waiver-20261116 (17db40c3c) KHONG merge — CHO Mike arch-review + merge + chay gate that 2 weekly 09-13/11; waiver het han 2026-11-20
- [2026-11-16T01:58:14Z] [cq vong2 16/11] XONG job Taylor_20261116_014210: A 960c17f97, B 145b9cf92 KHONG merge — CHO Mike arch-review diff-only + merge
