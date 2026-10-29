# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## 29/10 cuối ngày 28/10 — trạng thái
- Vá auto-exit theo lô XONG (merge 310b317be); plan ZaloPay 29/10 có SELL VPB 282. Retro 28/10 ghi: kb/incidents/retro/retro-2026-10-28.md.
- CHỜ USER: duyệt plan 29/10 cả 2 TK trước 08:45; chuyển Trứng vàng trước 09:05 (SpaceX ≥19,4tr theo DollarBill).
- Kiểm sau 09:05: bot_execute đặt ZaloPay SELL VPB 282 + MUA MCH 200 cả 2 TK; SpaceX park-merge SELL VPB 200.
- Nợ (chi tiết: kb/incidents/2026-10/2026-10-29-auto-exit-lot-level-entry-date.md): N1-N3 + N4 disc_entry_dates TV1 + N5 SpaceX VPB LAG dưới PARK; `send_plan_report --plan-date`.
- Đề xuất escalate (chưa làm, cần user/bước sau): drift-checker-runs-before-evidence (3 retro liên tiếp) — phương án A dời giờ + thoát im khi thiếu dnse_raw.
- Chờ USER: Wags/wags-fix-not-confirmed; DRI ghi KB r4 + Taylor sửa REPORT (BCTC Q3 30/10); DDV tái trọng số; TV2 watchlist.
- Mốc: nav-loss-brake 11-09; DT CRISIS ~11/10; Livermore ~19/11; BĐS 11-26; commodity 11-25; LAG 12-15; measurement audit ~12-27.

- [2026-10-28T17:34:46Z] 29/10 00:35 user DUYỆT plan T+1 29/10 cả 2 TK (SpaceX: SELL VPB 200 park-merge + MUA MCH 200; ZaloPay: SELL VPB 282 auto-exit + MUA MCH 200). Egg: SpaceX FUNDED; ZaloPay cần chuyển egg ≥17,8tr trước 09:05. Sau 09:05 kiểm fill.
- [2026-10-28T17:41:49Z] 29/10 00:4x: user chọn A (giữ plan, bán PARK VPB 200) + giao Taylor clearing GĐ1 SHADOW (design kb/projects/book-clearing-plan-20261029.md; nhánh session/clearing-shadow-20261029). Xong → arch-review (Opus high, đụng park_holdings lõi) → báo user; KHÔNG wire cron/execute tới khi user duyệt GĐ3.
- [2026-10-28T18:25:40Z] 29/10 01:2x: clearing G1 arch-review vòng 1 NEEDS_CHANGES (parser BOOK_TRANSFER fail-closed + mutant sống + --asof guard). Vòng 2 Taylor_job mới (sonnet medium) trên session/clearing-shadow-20261029. Xong → verify inert byte-cmp + selfcheck → báo user, xin duyệt MERGE shadow (không wire cron); checklist G3: gate_block_question mtime journal, portfolio_status:189-197 map sổ.
- [2026-10-28T18:37:37Z] 29/10 01:4x: clearing G1 vòng 2 verified (inert byte-cmp OK, selfcheck 2TZ OK) @eb786f0fe. CHỜ USER duyệt MERGE shadow (không wire cron). Rồi: sau 09:05 kiểm fill plan 29/10.
- [2026-10-29T01:27:39Z] 29/10 08:3x: clearing G1 shadow ĐÃ MERGE master mike 6939d704b (user duyệt 08:27), chưa wire cron. Việc kế: sau 09:05 kiểm fill plan 29/10; GĐ3 chờ user.
- [2026-10-29T01:38:25Z] 29/10 08:4x: cron shadow clear_books_daily.sh: wrapper commit b8467a627, CRON CHƯA CÀI (classifier chặn crontab) — chờ user cài tay dòng trong kb/cron_registry. Vệ sinh GĐ3 giao Taylor (gate_block_question mtime→event thực thi; sleeve_map từ sổ lô, sửa luôn N5) nhánh session/g3-hygiene-20261029 → arch-review (Opus medium) → merge cần user. Sau 09:05 kiểm fill plan 29/10.
