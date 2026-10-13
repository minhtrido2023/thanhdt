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

- [2026-10-12T16:49:28Z] ĐANG DỞ job Taylor_20261012_162001 (quỹ mở bước 2 vòng 2, wt-fundcf-1012, CHƯA COMMIT): mutant lượt 1 xong (research/.../r2/out_{rev,new,step2,ar3}.txt: rev 64/71, new 63/66, step2 83/86, ar3 71/71) | NEXT: thêm test giết N32/C59 (ghi chú rút Trứng vàng), C20/C21 (ack sai from/to), N02 (side thường), N26 (CSV xáo), X73 (ô 400 chữ số), X60 (e2e main ops_today≠ops_lines); chạy lại mutant sống; quét rộng §23 (broad_scan.sh, sandbox /tmp/ar3/WC); 3 TZ; README r2; pre-commit; commit; finding
- [2026-10-13T06:33:58Z] [2026-10-13] [TV1] SOTP 07-23 SAI (bỏ sót bậc giá PPA SB5 sau 2027): ở 500-600 đ/kWh TV1 ≈ đúng giá, biên an toàn hết; đã khuyến nghị TẠM DỪNG gom (user chưa quyết) — CHỜ: user quyết + fundamental-skeptic + phụ lục PPA hiện hành (500-600 hay ~340). Xem research/tv1_sb5_ppa_price_20261013/README.md
- [2026-10-13T08:25:25Z] ĐANG DỞ job Taylor_20261013_082516 (chuỗi 4 CCTG tier2 VPB/MB/TCB/ACB, nhánh feat/cctg-tier2-banks-series-20261013, KHÔNG merge): bắt đầu | NEXT: đọc commit b3169f92, tạo worktree, viết writer+selfcheck
- [2026-10-13T08:41:49Z] [CCTG tier2, 10-13] XONG: feat/cctg-tier2-banks-series-20261013 @7ec10026 (wt-cctgt2-1013, CHƯA merge); finding cctg-tier2-banks-series-20261013 trace Taylor_20261013_082516. Chờ Mike merge + duyệt cctg_rate_vn.md.proposed + user chạy dòng manual_verify VPB (ảnh app). (Thay dòng ĐANG DỞ job 082516.)
- [2026-10-13T09:28:39Z] [CCTG tier2 r2, 10-13] XONG: feat/cctg-tier2-banks-series-20261013 @d6c60ecd (wt-cctgt2-1013, CHƯA merge); finding cctg-tier2-banks-series-20261013-r2 trace Taylor_20261013_090057. Chờ Mike arch-review r2 + merge + duyệt cctg_rate_vn.md.proposed + xác nhận ngoại lệ PROMPT_READERS (vn_realestate_monthly_check) + user seed VPB manual_verify (file rỗng: agent bị từ chối khoá đầu). (Thay dòng 10-13T08:41)
- [2026-10-13T11:45:03Z] ĐANG DỞ job Taylor_20261013_114453 (khoá cơ học CAPIT margin hold; nhánh feat/capit-margin-hold-lock-20261013, worktree agents/Taylor/wt-capithold-1013; KHÔNG merge): bắt đầu | NEXT: đọc KB+approve_margin_day+approve_plan_simple+send_plan_report+plan.py, viết capit_margin_hold.py + selfcheck
- [2026-10-13T11:45:04Z] ĐANG DỞ job Taylor_20261013_114456 (FTSE upgrade re-validate 3 tầng DT5G breadth/custom30V/CAPIT ADV, chỉ ĐO, research/ftse_upgrade_revalidate_20261013): bắt đầu | NEXT: đọc protocol, data_registry, viết script đo, .proposed, bus finding ftse-upgrade-revalidate-20261013
- [2026-10-13T11:52:45Z] [FTSE re-validate 10-13] XONG: giữ nguyên 3 tầng (0/24 ngoài dải nhiễu); finding ftse-upgrade-revalidate-20261013; CHỜ Mike duyệt kb/projects/ftse-upgrade-structural-break-20260921.md.proposed. Mốc chạy lại research/ftse_upgrade_revalidate_20261013/measure.py: 2026-11-26, 2026-12-15, ~2027-04-12. (Thay dòng ĐANG DỞ job 114456.)
- [2026-10-13T11:59:20Z] ĐANG DỞ job Taylor_20261013_114453 (khoá CAPIT margin hold, wt-capithold-1013 nhánh feat/capit-margin-hold-lock-20261013, CHƯA COMMIT): code xong bin/capit_margin_hold.py + sửa approve_margin_day.py/approve_plan_simple.sh/send_plan_report.sh + bin/capit_margin_hold_selfcheck.py; file giữ = WC/data/CAPIT_MARGIN_HOLD.json; PHÁT HIỆN: thiếu bản duyệt thì bot gỡ cờ vay nhưng GIỮ qty 1,3x → funding gate chặn cả account hoặc mua đủ bằng tiền mặt (plan.py:1263-1271, bot_execute.py:697-701) | NEXT: chạy selfcheck A-H, nhóm F với CMH_BASELINE_DIR=bản master, 3 TZ, mutant, capit_lever_selfcheck + send_plan_report selfchecks, commit, bus finding
- [2026-10-13T12:08:57Z] [CAPIT margin hold lock, 10-13] XONG: feat/capit-margin-hold-lock-20261013 @0d0702856 (wt-capithold-1013, CHƯA merge); finding capit-margin-hold-lock-20261013 trace Taylor_20261013_114453. CHỜ Mike arch-review + user quyết: thiếu bản duyệt margin thì bot giữ qty x1,3 → funding gate chặn cả account hoặc mua đủ (đề xuất A: golive đọc file giữ ⇒ active=false). Khi bật giữ PHẢI apply capit_lever_selfcheck_pin_hold.patch (repo ngoài) kẻo L2+L4 đỏ. (Thay 2 dòng ĐANG DỞ job 114453.)
- [2026-10-13T12:36:32Z] ĐANG DỞ job Taylor_20261013_123622 (audit sẵn sàng BCTC Q3 góc tín hiệu, CHỈ ĐỌC+ĐO): bắt đầu | NEXT: đọc kb/projects/bctc-q2-readiness-audit.md, lag_live_schedule.py, đo 6 mục, bus finding bctc-q3-readiness-signal-20261013
- [2026-10-13T12:44:49Z] [BCTC Q3 readiness 10-13] XONG: finding bctc-q3-readiness-signal-20261013 trace Taylor_20261013_123622 — 0 CRIT/1 MED/4 LOW, CHƯA sửa gì. CHỜ user/Mike duyệt M1 (nới gate fa_ratings_earnings_window sang ngày ≤10 tháng 2/5/8/11 + cờ lag_rating_stale; ca thật TVN 08-05) và watcher PNJ Q3. Artifact research/bctc_q3_readiness_20261013/. (Thay dòng ĐANG DỞ job 123622.)
