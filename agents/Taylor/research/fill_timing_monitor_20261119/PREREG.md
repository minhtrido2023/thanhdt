# PREREG — fill_timing_monitor (job Taylor_20261119_055805) — khoá trước khi chạy monitor lần đầu
Read-only production. Không đổi config/cờ/plan/lệnh.
- HYBRID_ON_DATE = 2026-08-26 (commit 9be375a44 "flip fill_timing_live_gate+hybrid_live_gate -> False", user duyệt 2026-08-26).
- Mẫu: lệnh có fill (fillQuantity>0) của SpaceX 0002023347 + ZaloPay 0001743768 (lọc accountNo, §12), dedupe (account,id), transDate >= HYBRID_ON_DATE và < ngày chạy (ICT); join journal PLACE theo child_oid; nhãn HYB_IN_BLOCK = note chứa "hyb:blk" (cùng luật build.py job 052911).
- Open chưa điều chỉnh = tav2_bq.ticker.Open*Price/Close. Chỉ tính (mã,ngày) đã CÓ dòng trong BQ và ngày < ngày chạy; còn lại = "chờ giá", không tính.
- bps = (avg_fill/open_unadj - 1)*1e4 mỗi lệnh; đơn vị = (account,date,sym,side) trọng số qty; tuần = ISO (%G-W%V).
- ĐỦ N (mỗi chiều BUY/SELL riêng) = >=30 đơn vị mã-ngày VÀ >=8 tuần. Chưa đủ N => chỉ báo tiến độ "N=x/30, y/8 tuần", KHÔNG báo mean, KHÔNG kết luận.
- Đủ N => CI95 bootstrap khối tuần (5000 lần, seed 20261119).
- Luật cảnh báo (CHỈ BUY HYB_IN_BLOCK, đủ N): mean > +22 bps (ngưỡng rollback đã duyệt) => cảnh báo "đề xuất rollback — user quyết". Monitor không tự đổi cờ. SELL chỉ báo mô tả, không có luật rollback.
- Ex-post ngày giảm/tăng (Price/open_unadj-1 <0) chỉ nêu kèm cảnh báo, KHÔNG dùng làm bộ lọc live.
- Đầu ra: tiến độ 1 dòng thứ Hai (ICT) -> trading_daily; cảnh báo ngay (1 lần/tuần ISO khi luật còn chạm); lỗi -> "monitor không chạy được vì <lý do đọc được>"; còn lại im lặng.
