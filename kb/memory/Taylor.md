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

- [2026-10-12] [fearbuy] CỔNG ĐANG TREO từ quét 10-12: SHB AMBIGUOUS-yếu (cổng = NHNN ghi nhận vốn điều lệ 53.442 tỷ + niêm yết bổ sung, "trong tháng 10"; trượt không giải thích ⇒ nghiêng NON) · DHC không-phải-case (mở lại ở BCTC Q3) · PNJ ĐHĐCĐ bất thường 21/10. Đối chiếu ở lượt quét kế.
- [2026-10-12T01:19:22Z] ĐANG DỞ job Taylor_20261012_011913 (dọn quanh cổng DT5G: atomic write macro_health.json + 2 ca ghim 5 phút + đọc signal_v11_sql s5_ff + custom30V mode; nhánh fix/dt5g-gate-followups-20261012 từ main, KHÔNG merge): bắt đầu | NEXT: worktree, sửa, selfcheck 3 TZ + mutation, bus finding dt5g-gate-followups-20261012
- [2026-10-12T01:19:43Z] ĐANG DỞ job Taylor_20261012_011934 (4 việc dọn: send_report_email gửi trùng, staleness_watch tz, autodispatch hard-boundary macro_healthcheck, ops_health_check check DT4_only; worktree agents/Taylor/wt-dt5gfollow2-1012 nhánh fix/dashboard-dt5g-followups-20261012 từ master, KHÔNG merge): bắt đầu | NEXT: đọc 4 file, sửa, selfcheck 2 TZ, pre-commit, bus finding dashboard-dt5g-followups-20261012
- [2026-10-12T01:20:51Z] ĐANG DỞ job Taylor_20261012_011913: ĐÃ COMMIT 69cfcf62 trên fix/dt5g-gate-followups-20261012 (worktree wt-dt5gfollow-1012, CHƯA merge); selfcheck 128/128 (4 TZ), mutation 5→4/6/10/1 đỏ, byte-proof PASS; bằng chứng research/dt5g_gate_followups_20261012/ | NEXT: việc 3 (signal_v11_sql s5_ff.state caller) + việc 4 (custom30V mode live) chỉ đọc, rồi bus finding dt5g-gate-followups-20261012
- [2026-10-12T01:22:46Z] [asof ICT fix 10-12] XONG: nhánh fix/cctg-deposit-asof-ict-20261012 @2b679283 (wt-asofict-1012, CHƯA merge). Chờ Mike→arch-reviewer→merge; Mike đóng cq-2026-10-11-hard-boundary.
- [2026-10-12T01:23:10Z] [dọn quanh cổng DT5G, 10-12] XONG phần Taylor: nhánh fix/dt5g-gate-followups-20261012 @69cfcf62 (worktree wt-dt5gfollow-1012, CHƯA merge), finding dt5g-gate-followups-20261012 trace Taylor_20261012_011913, bằng chứng research/dt5g_gate_followups_20261012/. Chờ Mike review/merge. Nợ nêu trong finding: build_snapshot.py + pt_v12_macro dùng SIGNAL_V11 thô (state BASE, ngoài live); đường bán park cũ chưa truy.
- [2026-10-12T01:36:33Z] [dọn dashboard+cổng DT5G, job Taylor_20261012_011934] XONG phần Taylor: nhánh fix/dashboard-dt5g-followups-20261012 @f40409246 (worktree wt-dashfollow-1012, CHƯA merge), finding dashboard-dt5g-followups-20261012 trên bus. Chờ Mike review/merge + trình user phát hiện (b): cửa sổ DT4 theo lịch T7 18:37→T2 15:30 và biên 1 phút do [12] publish chạy trước [14] ghi health. Sau merge: chạy lại tz-anchor-gate trên canonical; nhìn dòng 'check 13' ở ops_health 08:20.
- [2026-10-12T01:36:54Z] [dt5g followups r2, 10-12] XONG: fix/dt5g-gate-followups-20261012 @d295da79 (wt-dt5gfollow-1012, CHƯA merge); finding dt5g-gate-followups-20261012-r2. Chờ Mike merge.
- [2026-10-12T01:44:11Z] [asof ICT r2, 10-12] XONG: fix/cctg-deposit-asof-ict-20261012 @e9c991fd (wt-asofict-1012, CHƯA merge); finding cq-2026-10-11-hard-boundary-fix-r2. Chờ Mike merge + hạ tz_anchor_baseline (append_deposit_rate bớt 1 date.today).
- [2026-10-12T02:02:05Z] [dashboard followups r2, 10-12] XONG: fix/dashboard-dt5g-followups-20261012 @d2f846c92 (wt-dashfollow-1012, CHƯA merge); finding dashboard-dt5g-followups-20261012-r2. Chờ Mike merge.
- [2026-10-12T02:22:59Z] [selfcheck followups 10-12] XONG: fix/cctg-selfcheck-followups-20261012 @c95836b4 (wt-selfcheckfu-1012, CHƯA merge); chờ Mike merge.
- [2026-10-12T04:02:54Z] ĐANG DỞ job Taylor_20261012_040245 (kiểm NGUỒN CỔNG sau publish trong bq_freshness_check.sh khối publisher-evidence; worktree agents/Taylor/wt-gatesrc-1012 nhánh feat/gate-source-check-publish-20261012 từ master, KHÔNG merge/crontab/notify thật): bắt đầu | NEXT: đọc khối 423-470 + consumer, sửa, selfcheck 3 TZ + mutation, bus finding gate-source-check-publish-20261012
- [2026-10-12T04:03:01Z] ĐANG DỞ job Taylor_20261012_040250 (dashboard tầng 3: drawdown live vs neo −25,2% + trượt giá vs +22bps; worktree agents/Taylor/wt-stratfit3-1012 nhánh feat/strategy-fit-tier3-20261012 từ master, KHÔNG merge): bắt đầu | NEXT: đọc strategy_fit_dashboard.py, nav_period_returns/nav_unit_ledger, execution_quality_review
- [2026-10-12T04:05:12Z] ĐANG DỞ job Taylor_20261012_040502 (neo ICT asof mặc định: due_diligence.py x2, dcf_valuation.py CLI, dcf_refresh_gate._now_ict_date; worktree nhánh fix/tz-asof-ict-dd-dcf-20261012 từ main repo /home/trido/thanhdt, KHÔNG merge): bắt đầu | NEXT: worktree, test đỏ, sửa, mutation 16 ô, bus finding tz-asof-ict-dd-dcf-20261012
- [2026-10-12T04:11:39Z] [healthcheck trước publish, 10-12] XONG: fix/healthcheck-before-publish-20261012 @1f5af0f4 (wt-hcpub-1012, repo ngoài, CHƯA merge); finding healthcheck-before-publish-20261012 trace Taylor_20261012_040247. Chờ Mike review/merge; sau merge sửa 4 chỗ chữ 'step [14]' trong repo mike + nhìn log lượt cron đầu ([11c] trước [12], 1 lượt healthcheck).
