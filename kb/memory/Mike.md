# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (cập nhật 2026-10-03 10:40 ICT)
- User duyệt 10-03 10:34: (1) corp-action phương án B broker-làm-nguồn → Taylor_20261003_033512 (opus/high, cần user duyệt trước khi BẬT THẬT); (2) NAV SpaceX 10-01 đã backfill (estimate); (3) audit merge 9311ac03 → Wags_20261003_033514.
- Định nghĩa XU HƯỚNG HẠ lãi suất (user chốt 10-03): Big-4 12M HOẶC CCTG 6M thấp hơn tuần thống kê trước → chỉ CẢNH BÁO, không tự khôi phục park. Code deposit_cctg_trend_check.py so 2 anchor gần nhất mỗi chuỗi (tương đương).
- rating_8l/DCF dùng effective rate: user DUYỆT 10-03 (đã LIVE từ 10-01).
## Đang chờ
- Taylor_20261003_033512 (broker corp-action), Wags_20261003_033514 (audit merge) — kết quả tự báo vào thread 1555778271369494598; Mike ScheduleWakeup poll.
- Cron mới 08:00 ICT daily_decision_topic.py: lần chạy thật đầu 10-04 — kiểm log/ topic 04.10 có tạo không.
## Chờ user
- Discretionary DRI/TV1.
- Trứng vàng vượt trần đề xuất legal-vn (sleeve ≤10% NAV) — chưa chốt.
- Cổ tức TPB: BQ 531.300đ lệch tiền thật 100.000đ — cần người kiểm nguyên nhân.
## Backlog
- 9 topic selfcheck-red; VNM exright note cho Winston; ack SCL bán tay 09-30; production_manifest ROOT_TIER thiếu 3 cron; context_pack/current_ops phình (trim).

- [2026-10-03T05:31:20Z] 10-03 12:35: Taylor broker-corp-action DONE ở round-3 cap (branch feat/broker-corp-action-source-20261003, 9ab1cf5f, shadow mặc định). CHỜ USER: (a) merge shadow? (b) dispatch Sonnet-medium sửa N9 + 11 đột biến sống trước live; (c) 4 dòng quote_unmapped ZZZ/AAA/BBB/CCC trong dnse_raw_2026-10-03.jsonl dòng 21-24 — giữ hay xoá. Wags audit merge: chờ duyệt port prompt investor-grade + dọn 2 test mồ côi.
- [2026-10-03T06:49:06Z] 10-03 13:50 USER DUYỆT: merge broker-corp-action ở SHADOW (sau vòng verify), giao vòng verify Sonnet (Taylor_20261003_064854), giữ 4 dòng quote_unmapped, duyệt port prompt investor-grade+dọn 2 test (Wags_20261003_064857, branch fix/report-prompt-port-20261003, arch-review bắt buộc). Mike MERGE cả 2 sau khi đọc kết quả; poll ScheduleWakeup.
