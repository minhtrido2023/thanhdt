# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Cuối ngày 13/10 → 14/10 (đã dọn)
## SÁNG 14/10 (việc đầu)
- Kiểm chuỗi 19:00 ngày 14/10 = lượt thật ĐẦU của BCTC-Q3 M1 gate (merge 13/10 21:15: WC main@866d549a + mike master 885eaaf36). Re-rate 8L crontab đã dời 20:00→17:30 ICT (backup state/crontab_backups/).
- Monitor phanh lỗ NAV (cron 22:05 + 00:20 ICT, CHỈ CẢNH BÁO): kiểm lượt 22:05 ngày 13/10 ra session 2026-10-13; nếu run_log đủ rc=0 → merge commit ops_health 3e0a9f7a7 (nhánh feat/nav-loss-brake-monitor-20261012). CHỜ USER duyệt Mike tự sửa F1/F2/F4; còn F8 data/loss_brake vào fleet_backup.sh. Mốc xem lại 2026-11-09.
- Log daily_refresh 18:30 ngày 13/10 chưa đọc; xác nhận thư EOD đính strategy_fit html (user 13/10 22:51 chốt: giữ HTML làm bản hằng ngày, Claude Docs chỉ là lớp xem).
- Xác nhận race backup/consolidate 00:00 ICT 15/10 (backup_freshness báo giả 13/10 — backup thực ra đã chạy, xem retro-2026-10-13).
## Quyết định hôm nay
- CAPIT margin lever TẮT (capit_margin_lever.enabled=false, user duyệt 19:30); chỉ user bật lại.
- G/H prevention (feat/finding-measured-by-20261013) user duyệt A+B; Mike verify đạt 10:32 — CHƯA merge (kiểm).
## Nhánh DONE_ON_BRANCH_NOT_MERGED cần kéo merge
- feat/finding-measured-by, feat/gate-source-check-publish, dcf-rf-slow (VIỆC 2), cctg-tier2 phần còn lại, feat/fund-cashflow-detect-20261012 (review HẸP C1/C2/S1-S9 → merge → chép 2 xác nhận user 07-03, 08-28 vào data/cash_identity_acks.json).
## Khác
- Quỹ mở bước 2 (topic 1558282936489611354): job Taylor_20261012_141756 resume — tra logs/resume_pending.log; Wags: resume_pending tính sai giờ reset.
- Chưa rõ: ZaloPay 401 10-12; adjfactor-drift-scan drift=4.
- CronCreate trong phiên MẤT khi restart — mốc quan trọng làm tay. pgrep dùng '[b]ot_execute'.
## Giữ nguyên
- Cutloss shadow v2; corp-action broker-primary SHADOW (xem lại 2026-12-15); 4 call-site corp-action + 3 selfcheck hardcode path chưa vá; park=0 live; PNJ excluded tới BCTC Q3.

