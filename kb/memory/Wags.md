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

- [2026-10-03T06:54:54Z] Chờ Mike merge branch fix/report-prompt-port-20261003 (1b9d4d46); sau merge: git worktree remove agents/Wags/wt-reportport-1003
- [2026-10-03T08:28:35Z] [2026-10-03] Chờ Mike merge fix/report-prompt-r2-20261003 (1afc0c59, worktree agents/Wags/wt-reportr2-1003); sau merge: git worktree remove wt-reportr2-1003 (và wt-reportport-1003 nếu port đã merge)
- [2026-10-04T02:52:44Z] [2026-10-04] Cho Mike merge fix/exdate-forecast-feed-status-20261004 (agents/Wags/wt-exdate-feed-1004) TRUOC 05/10 19:00 ICT; sau merge: git worktree remove wt-exdate-feed-1004
- [2026-10-05T01:21:21Z] [2026-10-05] coord-2026-10-05: Q polish-chain-review-rounds-cost CHO USER (A cap cung dispatch.sh / B do retro / C arch-review gop cuoi). Da post architecture, ack suppress 3d. Neu chon A: Wags lam + arch-reviewer bat buoc. files_changed=[].
- [2026-10-07T01:21:49Z] [2026-10-07] coord-2026-10-07: CHO USER — (1) polish-chain override a/b/c (post architecture; neu (b) Wags lam + arch-reviewer); (2) duyet merge fix/sell-split-by-loan-package-20261006 @8a669a9a (post trading_daily). Ack suppress 3d. files_changed=[].
- [2026-10-08T01:22:15Z] [2026-10-08] coord-2026-10-08: CHO USER A/B/C chu so huu backlog selfcheck-red (17 do that; de xuat Wags=mike/bin 8 file, Taylor=file goc 9). Neu chon A: Wags ra 8 file mike/bin moi thu 6. Ack suppress 3d. Da sua wags_autofix_postq (24b6dfee).
- [2026-10-08T13:38:23Z] ĐANG DỞ job Wags_20261008_133633 token telemetry: worktree agents/Wags/wt-tokentel-1008 branch feat/dispatch-token-telemetry-20261008 | thiet ke --session-id + cost-state transcript | NEXT: code+selfcheck+arch-review
- [2026-10-08T13:55:19Z] [2026-10-08] context-pack-trim DUNG o NEEDS_CHANGES: branch chore/context-pack-trim-20261008 @f10b0326 (worktree agents/Wags/wt-ctxtrim-1008) CHUA merge. Cho user/Mike chon vong 2 (8 required_change trong bus finding context-pack-trim) hoac bo. Neu bo: git worktree remove + xoa branch.
- [2026-10-08T14:06:19Z] [2026-10-08] dispatch-token-telemetry (job 133633) DUNG o NEEDS_CHANGES: branch feat/dispatch-token-telemetry-20261008 @bba411f3 (worktree agents/Wags/wt-tokentel-1008) CHUA merge; cho Mike/user cho vong 2 (S1 trap-window sync, S2 whitelist/tach job_telemetry.py, S3 union-find chain). Bus finding co du danh sach.
- [2026-10-08T14:33:34Z] ĐANG DỞ job Wags_20261008_143324 tokentel VÒNG 2: worktree agents/Wags/wt-tokentel-1008 | NEXT: S1 trap/telemetry-after-terminal, S2 job_telemetry.py whitelist, S3 chain union-find, 2 test, rebase, arch-review 1 lần
- [2026-10-08T14:42:20Z] [2026-10-08] context-pack-trim R2 DUNG NEEDS_CHANGES: branch chore/context-pack-trim-20261008 @e143a7cb (wt-ctxtrim-1008) CHUA merge. 1 blocker (V2.5 NO-GO mat khoi hot path) + 4 should-fix, bus finding context-pack-trim. Cho user/Mike cho 1 luot sua nho hoac bo; bo thi git worktree remove + xoa branch.
- [2026-10-08T15:00:48Z] [2026-10-08] dispatch-token-telemetry R2 DUNG o NEEDS_CHANGES: branch feat/dispatch-token-telemetry-20261008 @eacd6dfb (wt-tokentel-1008) CHUA merge; con SF1 round_cap selfcheck do (docstring spend_report:244) + nit. Cho Mike/user cho vong 3 hoac bo.
