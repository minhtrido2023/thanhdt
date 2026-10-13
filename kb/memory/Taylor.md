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

- [2026-10-12T06:15:22Z] [strategy-fit tier3 r2, 10-12] XONG: feat/strategy-fit-tier3-20261012 @aaaf60a3b (wt-stratfit3-1012, CHƯA merge); finding strategy-fit-tier3-20261012-r2 trace Taylor_20261012_061001. Chờ Mike merge. (Thay 2 dòng ĐANG DỞ job 040250/044300.)
- [2026-10-12T07:08:26Z] ĐANG DỞ job Taylor_20261012_070816 (vòng 2 gate-source-check: B1 bỏ pipe tee + R0 curl timeout + N1-N5,N7 trong 1 commit trên feat/gate-source-check-publish-20261012, wt-gatesrc-1012, KHÔNG merge): bắt đầu | NEXT: đọc bq_freshness_check.sh:660-700, gate_source_check.py, notify_discord.sh, sửa, selfcheck 3 TZ + mutation, bus finding gate-source-check-publish-20261012-r2
- [2026-10-12T07:21:54Z] [gate-source check r2, 10-12] XONG: feat/gate-source-check-publish-20261012 @b1b8619d4 (wt-gatesrc-1012, CHƯA merge); finding gate-source-check-publish-20261012-r2 trace Taylor_20261012_070816. Chờ Mike merge + duyệt 2 file .proposed (registry gate_source_alert, runbook). Mở: notify_discord.sh vẫn exit 0 khi hết trần (giữ hợp đồng) — Mike/user quyết có cần mã lỗi. (Thay dòng ĐANG DỞ job 070816 và dòng 04:27 gate-source.)
- [2026-10-12T12:34:39Z] [loss-brake] r2 XONG, nhánh feat/nav-loss-brake-monitor-20261012 @e650f7ce0 (ops_health là commit cuối; bản tuyến tính cũ ở backup/nav-loss-brake-r2-linear-20261012) CHỜ Mike/arch-review + user: duyệt 27 bản khai market_only máy sinh khi seed, tên khoá số ngưỡng episode, luật đẩy tin nav_is_estimate. Chưa merge/cài cron.
- [2026-10-12T13:43:12Z] [quỹ mở bước 2] nhánh feat/fund-cashflow-detect-20261012 @ea9d6969a CHỜ Mike arch-review + merge (finding fund-cashflow-detect-20261012). Sau merge: SpaceX mang 2 cảnh báo CHỜ KHAI (07-03, 08-28) tới khi user chép market_only — đề xuất ở research/fund_cashflow_detect_20261012/proposed_acks.json
- [2026-10-12T14:18:05Z] ĐANG DỞ job Taylor_20261012_141756 (quỹ mở bước 2 VÒNG 2: sửa C1,C2,S1-S9,G3,G6,G7,G8 theo arch_review_ea9d6969a/REVIEW.md; nhánh feat/fund-cashflow-detect-20261012, worktree agents/Taylor/wt-fundcf-1012; KHÔNG merge): bắt đầu | NEXT: đọc REVIEW.md, sửa, selfcheck 3 TZ + mutant, bus finding
- [2026-10-12T16:20:14Z] ĐANG DỞ job Taylor_20261012_162001 (resume #3 quỹ mở bước 2 vòng 2): wt-fundcf-1012 có bin/cash_identity.py viết lại CHƯA COMMIT | NEXT: kiểm file compile, sửa tiếp consumer (nav_period_returns, daily_nav_snapshot, report gate), selfcheck, mutant, finding
- [2026-10-12T16:26:49Z] ĐANG DỞ job Taylor_20261012_162001 (quỹ mở bước 2 vòng 2, wt-fundcf-1012, CHƯA COMMIT): code xong cash_identity.py (acks file riêng, đối chiếu SL mọi cửa sổ, trôi, --notify-snapshot), daily_nav_snapshot (1 dòng trung tính + cash_flow_ops), nav_period_returns, report_delivery_gate (S4/S5/G6), eod_trading_report.sh + nav_sync_retry.sh; repro reviewer R1-R13 đạt (research/.../r2/repro_r2.txt) | NEXT: viết lại cash_identity_selfcheck.py + sửa ca ở nav_unit_ledger_selfcheck/e2e, proposed_acks.json (SpaceX 07-03, 08-28 + ZaloPay 08-28), .proposed docs, mutant reviewer + 157, nghiệm thu 1-6, commit, finding
- [2026-10-12T16:44:30Z] ĐANG DỞ job Taylor_20261012_162001 (quỹ mở bước 2 vòng 2, wt-fundcf-1012, CHƯA COMMIT): code + selfcheck xong (cash_identity_selfcheck 327, e2e 67, ledger 4736), repro reviewer đạt, nghiệm thu 1+4 đạt (research/.../r2/acceptance/), proposed_acks.json đã viết lại (3 bản ghi) | ĐANG: mutant r2/run_r2.py {rev,new,step2,ar3} → r2/out_*.txt | NEXT: giết mutant sống, docs .proposed (cash_identity.md + policy), nghiệm thu 5/6 trích từ selfcheck, 3 TZ, pre-commit, commit, finding
- [2026-10-12T16:49:28Z] ĐANG DỞ job Taylor_20261012_162001 (quỹ mở bước 2 vòng 2, wt-fundcf-1012, CHƯA COMMIT): mutant lượt 1 xong (research/.../r2/out_{rev,new,step2,ar3}.txt: rev 64/71, new 63/66, step2 83/86, ar3 71/71) | NEXT: thêm test giết N32/C59 (ghi chú rút Trứng vàng), C20/C21 (ack sai from/to), N02 (side thường), N26 (CSV xáo), X73 (ô 400 chữ số), X60 (e2e main ops_today≠ops_lines); chạy lại mutant sống; quét rộng §23 (broad_scan.sh, sandbox /tmp/ar3/WC); 3 TZ; README r2; pre-commit; commit; finding
- [2026-10-13T06:33:58Z] [2026-10-13] [TV1] SOTP 07-23 SAI (bỏ sót bậc giá PPA SB5 sau 2027): ở 500-600 đ/kWh TV1 ≈ đúng giá, biên an toàn hết; đã khuyến nghị TẠM DỪNG gom (user chưa quyết) — CHỜ: user quyết + fundamental-skeptic + phụ lục PPA hiện hành (500-600 hay ~340). Xem research/tv1_sb5_ppa_price_20261013/README.md
