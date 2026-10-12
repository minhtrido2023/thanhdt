# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Trạng thái cuối ngày 12/10 → 13/10 (đã dọn)
## SÁNG 13/10 (việc đầu)
- Kiểm log daily_refresh 18:30 ngày 13/10 (lượt thật đầu của healthcheck-trước-publish, đã merge WC main 1d489b01) theo checklist reviewer.
- Merge mike master (ngoài 18:30-19:10 và 21:00): feat/strategy-fit-tier3 @aaaf60a3b + feat/gate-source-check-publish @b1b8619d4 (cả hai arch-review APPROVED). Sau merge: sửa comment lệch 'step [14]' ở ops_health_check.sh:1855,1865 + preflight_check.sh:186; duyệt 2 file .proposed (data_registry gate_source_alert + runbook).
- Xác nhận thư EOD thật có đính strategy_fit html (sổ không ghi file kèm, chưa nhìn thư thật).
## Monitor phanh lỗ NAV — LIVE (cron 22:05 + 00:20 ICT), CHỈ CẢNH BÁO, cơ sở đo NAV toàn tài khoản
- Lượt 00:20 12/10 đạt (OK, 0 tin). Kiểm lượt 22:05 tối 13/10 phải ra session 2026-10-13.
- Sáng 14/10 nếu run_log đủ rc=0 → merge commit ops_health 3e0a9f7a7 (nhánh feat/nav-loss-brake-monitor-20261012).
- CHỜ USER duyệt Mike tự sửa F1 (monitor:1049 hậu tố |near), F2 (:664-708), F4 (:1085-1091). Còn: F8 data/loss_brake vào fleet_backup.sh; sửa dòng cảnh báo MIKE.md ~281, strategy_fit_dashboard:879-908, implement_note trading_rules khi monitor ổn; mốc 2026-11-09 xem lại cảnh báo vs BOT_STOP.
## Quỹ mở bước 2 (topic 1558282936489611354)
- Job Taylor_20261012_141756 vòng 2 dừng vì hết hạn mức; resume bị hẹn lệch → Mike sửa bus/pending_resumes/Taylor_20261012_154001.json, cron */10 dispatch lại. Tra logs/resume_pending.log 'orig_job=Taylor_20261012_154001'. Tạch nữa = redispatch tay (prompt /tmp/fund_step2_r2_prompt.3FvXS1; exit 7 thì HỎI USER). Việc Wags: resume_pending tính sai giờ reset.
- Nhánh feat/fund-cashflow-detect-20261012: xong → Mike tự kiểm → review HẸP C1/C2/S1-S9 → merge → chép 2 xác nhận user (07-03, 08-28) từ proposed_acks.json vào data/cash_identity_acks.json.
## Khác
- Job Winston_20261012_164706 (nhánh fix/sbv-policy-official-unchanged-20261012 @d912ed73, chưa merge): verify selfcheck 2 TZ + mutant → arch-reviewer 1 lần → merge. Mike tự làm chore/dd-dcf-selfcheck-cleanup-20261012 (worktree wt-1559007710136246294) — kiểm trạng thái.
- Retro 10-12: câu hỏi bus retro-pattern-recurring-claim-numbers-stated-before-measured chờ user; ZaloPay 401 21:00 chưa rõ nguyên nhân; ops-health warn_count=5 chưa kiểm; còn trình user: macro_health_contract_selfcheck gắn pre-commit, wakeup_audit loại job tự báo, bus question cq-2026-10-11-hard-boundary (cctg_rate_vn.py:129).
- CronCreate trong phiên MẤT khi restart — mốc quan trọng làm tay. pgrep dùng '[b]ot_execute'.
## Giữ nguyên
- Cutloss shadow v2, corp-action broker-primary SHADOW (xem lại 2026-12-15), 4 call-site corp-action + 3 selfcheck hardcode path chưa vá, park=0 live, tầng 3 dashboard bản hẹp.

