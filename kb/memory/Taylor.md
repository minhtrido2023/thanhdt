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

- [2026-10-25T02:00:28Z] [spend-routing-review 10-25] XONG job Taylor_20261025_020009: no_action (opus 48/135 job, giam so voi 59/110)
- [2026-10-25T03:12:57Z] [cq-2026-10-25 autodispatch] XONG job Taylor_20261025_030917: 817eafc1b, 3 fix + 1 skip, arch APPROVED
- [2026-10-25T03:58:28Z] ĐANG DỞ job Taylor_20261025_035815: cq hard-boundary 10-18+10-25 (cpi_vn look-ahead, publish_gated_state atomic, NAV §25 4 nơi, bot_execute docstring, dcf status) | NEXT: đọc report, worktree
- [2026-10-25T04:07:39Z] [retro-prevention a+b 10-25] XONG job Taylor_20261025_035810: nhanh fix/prevent-nav-selfcheck-bg-wakeup-20261025 @215709652, arch NEEDS_CHANGES đã sửa 3 mục, CHƯA merge — chờ Mike merge/re-review
- [2026-10-25T04:18:30Z] [cq-hard-boundary 10-25] job Taylor_20261025_035815: 4 commit đã merge main; CHỜ user duyệt merge cpi_vn pit (nhánh fix/cq-hard-boundary-20261025 d9f60d264+0fe24ff04) — khi duyệt: cherry-pick + ghi chú results_registry macro_confidence + data_registry/macro/cpi_vn.md
- [2026-10-25T04:27:02Z] ĐANG DỞ job Taylor_20261025_042649: coord-2026-10-19/20 — verify injector discretionary giá vượt biên độ (TV1 19.900 plan 19/10) + gap relay retro | NEXT: đọc Wags.jsonl round2, discretionary_accumulation_inject.py
- [2026-10-25T04:30:19Z] [coord-2026-10-19/20] XONG job Taylor_20261025_042649: injector bien do = FALSE (TV1 UPCOM), no fix; gap relay retro->user con mo, cho Mike/user chon kenh
- [2026-10-25T04:37:52Z] ĐANG DỞ job Taylor_20261025_043744: V1 prompt DollarBill đọc lag_dd ack (hạn merge 18:30) + V2 dt5g_publish_runs.log | NEXT: worktree, đọc bq_freshness_check.sh khối LAG
- [2026-10-25T04:46:55Z] ĐANG DỞ job Taylor_20261025_043744: V1 MERGED 591e52563; question mch-entry-date-26-vs-29 chờ Mike | NEXT V2: dt5g_publish_runs.log trong publish_gated_state.py (outer repo) + dt5g_writer_watch.py
- [2026-10-25T04:57:34Z] [job Taylor_20261025_043744] XONG V1 (591e52563) + V2 (outer 5780167fd, mike 182a19f5e), arch CONFIRMED; CHỜ Mike: question mch-entry-date-26-vs-29, duyệt .proposed dt5g_publish_runs_log
- [2026-10-25T06:13:00Z] ĐANG DỞ job Taylor_20261025_061240: commodity-cycle PREREG (DRI/MSR/PVT) → agents/Taylor/research/commodity_cycle_prereg_20261025/ | NEXT: data_registry feeds, map CSV, PREREG, chạy
- [2026-10-25T06:20:21Z] [commodity-cycle 10-25] XONG job Taylor_20261025_061240: PREREG FAIL 6/6 (de76e7964); post-hoc 1.05/3M chỉ giả thuyết; CHỜ quant-skeptic (Mike) + user quyết feed APT/BDTI cho Winston
- [2026-10-25T06:37:17Z] [commodity PREREG-2 10-25] XONG job Taylor_20261025_062825: nhanh research/commodity-prereg2-20261025 @c124266de, CHUA merge/cron — CHO Mike review + user; N=0 luc dong bang, ket qua kha di nhat 'khong phan biet duoc'
- [2026-10-25T09:22:42Z] ĐANG DỞ job Taylor_20261025_092232: 4 cảnh báo rights alert NB (auto_exit_inject >=, send_plan_report rights, reconcile credit≠payment, N4 dividend_adjusted_return) | NEXT: tìm nguồn NB, worktree
- [2026-10-25T09:22:49Z] ĐANG DỞ job Taylor_20261025_092234: Livermore REPORT_BLOCK cho weekly/monthly (worktree riêng, không merge) | NEXT: đọc livermore_run.sh/common.py/reads.md, check_report_cadence.sh
- [2026-10-25T09:43:50Z] [rights-alerts-nb 10-25] job Taylor_20261025_092232 XONG: nhanh fix/rights-alerts-nb-20261025 @52d0804af, arch APPROVED, CHUA merge — cho Mike merge
- [2026-10-25T09:51:18Z] [livermore-report-block 10-25] XONG job Taylor_20261025_092234: nhanh feat/livermore-report-block-20261025 @323e39b21, arch APPROVED r2, CHUA merge — CHO Mike/user: merge + chap nhan mau doc theo lich + xac nhan LVR-2026-10-21 mu
- [2026-10-25T09:51:31Z] [livermore-report-block 10-25] XONG job Taylor_20261025_092234: nhanh feat/livermore-report-block-20261025 @323e39b21, arch APPROVED r2, CHUA merge — CHO Mike/user: merge + chap nhan mau doc theo lich + xac nhan LVR-2026-10-21 mu
- [2026-10-25T11:49:41Z] ĐANG DỞ job Taylor_20261025_114929: A=LAG capacity floor (Volume cap p 10%/5%) → agents/Taylor/research/lag_capacity_floor_20261025/; B=fix f3_particip.py Price NaN + nhãn median_part_by_value | NEXT: đọc REPORT_F1_F3/PREREG_F3/f3_particip.py
- [2026-10-25T11:54:16Z] ĐANG DỞ job Taylor_20261025_114929: batch 20 run đang chạy nền (wt-lag-capacity-floor-20261025, logs/run_batch.log) | NEXT: verify ctl md5 537e349b/a6ba34d8, metrics, rồi việc B f3_particip
- [2026-10-25T12:00:02Z] [ta-schools 10-25] XONG job Taylor_20261025_115318: da so TA khong edge, chi ho xu huong (A2/C2b/F3) hon F1 nhung khong hon F2; REPORT.md trong research/ta_schools_vn_20261025/, chua commit
- [2026-10-25T12:15:35Z] ĐANG DỞ job Taylor_20261025_121521: ta-trend-entry-filter (A2/F3/F2 x LAG/BAL trên ledger R3 park=0) → agents/Taylor/research/ta_trend_entry_filter_20261025/ | NEXT: PINS.jsonl, ledger, engine.py job trước, PREREG
- [2026-10-25T12:21:35Z] [ta-trend-entry-filter 10-25] XONG job Taylor_20261025_121521: 0/6 dat, co xu huong khong loc duoc LAG/BAL (2e965250e); BAL×F3 chi la gia thuyet
- [2026-10-25T12:31:27Z] ĐANG DỞ job Taylor_20261025_123115: lag-bal-discriminators (PREREG ~25 chỉ báo fundamental x LAG/BAL, tertile+Spearman, cluster bootstrap) → agents/Taylor/research/lag_bal_discriminators_20261025/ | NEXT: đọc positions.csv/analyze.py job ta_trend, PREREG
- [2026-10-25T12:39:16Z] [lag-bal-discriminators 10-25] XONG job Taylor_20261025_123115 (db19fd74d): 4/50 đạt = value; payout không đạt; ứng viên GĐ2 duy nhất BAL×1/PCF,1/EVEB — CHỜ user duyệt + quant-skeptic
- [2026-10-25T12:52:56Z] [lag-capacity-floor 10-25] XONG job Taylor_20261025_114929: A+B tren nhanh research/lag-capacity-floor-20261025 @6724d841e, CHUA merge; CHO Mike/user: co ghi khoi registry 'can duoi' (no_ledger, de xuat trong REPORT_A) hay khong
