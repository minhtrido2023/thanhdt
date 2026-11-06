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

- [2026-11-05T09:43:22Z] ĐANG DỞ job Taylor_20261105_093502 GĐ3 clearing: worktree /home/trido/thanhdt/WorkingClaude/wt-clearing-g3-20261105 (nhánh session/clearing-g3-20261105); xong config/book_clearing.json + bin/book_clearing.py | NEXT apply_book_transfers.py, clear_books --apply, merge revert, preflight, send_plan_report, run_bot, selfcheck
- [2026-11-05T09:56:44Z] ĐANG DỞ job Taylor_20261105_093502 GĐ3: code+selfcheck book_clearing_g3_selfcheck PASS ở worktree wt-clearing-g3-20261105 | NEXT §23 quét rộng 2 TZ, byte-compare park_holdings, commit, bus finding
- [2026-11-05T10:28:27Z] [clearing GĐ3 05/11] XONG build job Taylor_20261105_093502 commit 9acbe593e nhánh session/clearing-g3-20261105 (wt-clearing-g3-20261105); CHỜ Mike arch-review + quant-skeptic; cờ apply_to_plan=false, cron chưa cài
- [2026-11-05T12:00:49Z] [clearing GĐ3 r2 05/11] XONG commit db490ba1d; CHỜ Mike re-review; manifest md chưa tái sinh (nợ master)
- [2026-11-05T17:11:13Z] ĐANG DỞ: TA model ±5% job Taylor_20261105_171103 → agents/Taylor/research/ta_model_5pct_20261106/ | NEXT: tra NO-GO, data_registry universe_pit, lấy data, backtest
- [2026-11-05T17:20:36Z] [ta-model-5pct 06/11] XONG job Taylor_20261105_171103 NO-GO (research/ta_model_5pct_20261106); CHỜ Mike quant-skeptic
- [2026-11-06T01:30:15Z] ĐANG DỞ: crisis-DD DRI ngày5 job Taylor_20261106_013001 | NEXT: đọc DOSSIER, tin mới, dd-note
- [2026-11-06T01:31:23Z] [crisis-dd HT1 06/11] FINAL NOISE ghi xong (notes/final.json), GIỮ, đề xuất đóng hồ sơ; user quyết
- [2026-11-06T01:33:20Z] [crisis-dd DRI 06/11] XONG ngày5 (không cờ, GIỮ) — mới: NQ25 Dakruco soi GCN đầu tư Lào của DRI; Dakmoruco lệch vốn 79+48,1 tỷ; chờ SXKD T10 ~10/11
- [2026-11-06T07:21:05Z] ĐANG DỞ job Taylor_20261106_072056: nhánh DISCRETIONARY auto_exit (FPT/NNC ±10%/25 phiên) | NEXT: worktree, code, selfcheck
- [2026-11-06T07:33:39Z] [disc-exit 06/11] XONG job Taylor_20261106_072056: outer ead44c734 + mike 984d998d4 (nhánh session/disc-exit-20261106); CHỜ Mike arch-review; merge repo ngoài trước; chưa latch phần dư TARGET
- [2026-11-06T07:45:30Z] [disc-exit r2 06/11] XONG job Taylor_20261106_074239: outer 0a93c22e4 + mike 1f6660397; CHỜ Mike re-review; chưa merge/cron; mixed-book=block, floor tắt
