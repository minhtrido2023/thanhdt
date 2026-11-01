# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Trạng thái cuối ngày 01/11 (sang 02/11)
- Retro 01/11 đã ghi (retro-2026-11-01.md, Wags CONFIRMED). Theo dõi: wakeup MISS 6/26=23,1% (0→15→23,1%); nếu 02/11 ≥15% → escalate (cổng cơ học kiểm hành động ScheduleWakeup thật, không dựa --wakeup-ack). anomaly-flags-stale báo giả Chủ nhật/lễ tái diễn (checker so ngày lịch thay vì phiên) — chưa có fix.
- Đã xong & merge master 01/11: oshares_live cutover; report-v2; DD HHS/TV2/SIP/FPT (đã email); work-tree dashboard LIVE (tunnel cloudflared quick, URL đổi khi restart: state/work_tree/public_url.txt; bản tin 08:00 02/11 cần có dòng Cây việc); cutloss→DD khủng hoảng 7 ngày (e38fbc058, user quyết, mặc định giữ); funnel DD v2 (ae875940a; cap ≤2 DD/tuần ngoài mùa, mùa 1/ngày; mốc đo 2027-04-06).
- Cron T2 fearbuy đã TẮT (crontab comment); còn cập nhật kb/cron_registry.md dòng Mon 08:00 nếu chưa.
- CẦN KIỂM: job C Taylor_20261101_140715 (cảnh báo KHẨN pháp lý/ngành + cẩm nang bán tay) và D Taylor_20261101_140717 (DD đã làm sau BCTC không đề xuất lại; DD user chỉ định không tính trần) báo done nhưng chưa xác nhận arch-review/merge ⇒ git branch --no-merged, arch-review 1 lần mỗi nhánh → merge → báo user.
- Còn mở: nối --claim vào skill dd-investor-report/due-diligence; report-v2 flaky md5 monthly + builder thiếu env BQ (Taylor fail-loud); drift CANNOT_CHECK theo dõi tới 04/11; plan T+1 02/11 kiểm không dính ANOMALY_NA từ file 30/10.
- Chờ user: DGC vòng 6, TV2 watchlist, nguồn Tampa/CFR NH3 vào BQ?, tunnel tên cố định (cần Cloudflare+domain).
- Mốc: clear_books_daily lần đầu T2 02/11 20:45; nav-loss-brake 11-09; DT CRISIS ~11/10; Livermore ~19/11; commodity 11-25; BĐS 11-26; LAG 12-15; measurement audit ~12-27.

- [2026-11-01T17:43:07Z] 02/11 00:45 DCF-VN: skeptic REFUTED g_T 4,5% (OShares stable→3,0% / unstable→6,5%; hiệu chuẩn trên fin-OShares, prod dùng live). Lens kỳ vọng (Taylor_20261101_165940, commit 29ac97b3b): KHÔNG xây DCF nhẹ. Chờ user chốt: rerun level grid OShares live + tách nhóm ổn định (Sonnet) rồi mới quyết vn_v3; lịch 4 mùa BCTC user đã duyệt, chưa cài cron.
- [2026-11-01T17:57:42Z] 02/11 00:57 user DUYỆT giữ domestic_v2; giao Sonnet Taylor_20261101_175734 rerun level grid OShares live + tách ổn định/nhảy → agents/Taylor/research/dcf_level_rerun_20261102/. Lịch 4 mùa BCTC user đã duyệt, cron CHƯA cài (gộp sau rerun).
- [2026-11-01T18:10:18Z] 02/11 01:12 DCF level rerun xong: g_T không hội tụ (phân cách 3,5pp), GIỮ domestic_v2; s=0 thắng MAE (CI loại 0) nhưng mức g_T không chốt được. Dispatch Taylor (Sonnet) cài lịch 4 mùa BCTC + cờ STALE>105d (nhánh worktree, chưa cron) → arch-review → Mike cài cron.
- [2026-11-01T18:58:27Z] 02/11 02:00 arch-review nhánh feat/dcf-bctc-season-20261102: NEEDS_CHANGES (cron thưa→daily, selfcheck 7/8 mutant sống, season_error im lặng); STALE trong đường echo plan/LAG CHƯA nối — chờ user quyết. Vòng 2 Sonnet Taylor dispatch 02:00.
