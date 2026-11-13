# Luồng B vòng 2 — hoàn tất 3 việc còn nợ của dòng "so với gửi tiết kiệm" (user duyệt 13/11 01:1x ICT, quant-skeptic B CONFIRMED)
Nhánh feat/savings-row-20261112 @9246cd93e (worktree wt-savings-row-20261112). Báo cáo: agents/Taylor/research/live_gap_exec_B/REPORT.md. KHÔNG merge vào main, KHÔNG gửi báo cáo, KHÔNG sửa cron.
1. Chạy report_v2_selfcheck chạy xong (detached/timeout dài, ghi log) trên nhánh VÀ trên master; so sánh; nêu khối savings luôn-bật trong CLI có làm gãy consumer nào không.
2. Siết anchor_warning: bật khi BẤT KỲ ngày tích luỹ dùng lãi suất từ dòng neo tay DEPOSIT_EVENTS (không chỉ from_date <= last_anchor). Thêm ca selfcheck (kỳ 01/07→19/07 mang neo 06-01).
3. Thêm kiểm chéo ±0,005pp ở report_delivery_gate._check_benchmark_table cho cột tiết kiệm (excess = TWR - hurdle), cùng selfcheck dương/âm; KHÔNG đổi template báo cáo.
4. Sửa REPORT: "byte-identical" chỉ đúng với default hàm; CLI luôn phát khối savings.
Chạy lại 56 assertion + 4 selfcheck lõi dưới env -u TZ. Bus finding live-gap-exec-B2-20261112. Chờ user/Wendy duyệt câu chữ và thuế nên KHÔNG đưa vào template.
