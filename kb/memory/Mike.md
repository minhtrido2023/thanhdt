# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Cuối ngày 14/10 → 15/10 (đã dọn, 00:35 ICT)
## VIỆC CẤP BÁCH SÁNG 15/10 (trước 09:05 ICT)
- plan_SpaceX/ZaloPay_2026-10-15.json CHƯA có lúc 00:30 (chỉ park_trim). 4 câu bus plan-t1-not-ready-* (14:00Z/16:00Z) chưa đóng. Tra log DollarBill/send_plan_report tìm nguyên nhân; KHÔNG retry tự động; escalate Telegram+Discord; đóng câu hỏi bằng answer kèm artifact.
## Chờ user quyết
- Hàng đợi đính chính số đã công bố (Taylor, fund-history-lock): benchmark ZaloPay neo 03/07 vs 06/07; vol tháng 8 ZaloPay 25,58% vs 18,27% (>0,5 điểm %); tin EOD SpaceX 08-07 % ngày sai (+0,12 vs +1,098). Mốc CORR_STEP 23/10.
## Nhánh chưa merge (kéo merge)
- feat/finding-measured-by-20261013 (G/H prevention, đã verify, 2 retro liên tiếp chưa merge → nếu 15/10 chưa merge thì escalate), feat/gate-source-check-publish, dcf-rf-slow, cctg-tier2 phần còn lại, feat/fund-cashflow-detect-20261012 (review hẹp → merge → chép 2 xác nhận user 07-03, 08-28 vào data/cash_identity_acks.json), feat/nav-loss-brake-monitor-20261012 (merge ops_health 3e0a9f7a7 khi run_log đủ rc=0; mốc 2026-11-09).
## Đề xuất prevention (cần user duyệt, chạm code NAV)
- nav_history: cổng "đủ phiên" giữa 2 dòng liền kề; chụp balances+positions cùng ngưỡng thời gian; selfcheck chạm nav_history chạy trên bản sao/flock.
## Chưa điều tra
- ZaloPay 401 10-12; adjfactor-drift-scan drift=4; log daily_refresh 18:30 13/10; xác nhận BCTC-Q3 M1 gate lượt 19:00 14/10; wakeup_audit nên loại job tự báo khỏi mẫu số.
## Quyết định đang hiệu lực
- CAPIT margin lever TẮT (chỉ user bật lại). Park NEUTRAL 0%. PNJ EXCLUDED (review khi có BCTC Q3/2026).
- CronCreate trong phiên MẤT khi restart; pgrep dùng '[b]ot_execute'.

