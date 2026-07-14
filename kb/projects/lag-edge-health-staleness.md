# lag_edge_health.csv staleness
> Dự án đã đóng — tách khỏi context_pack 2026-07-12. Chi tiết gốc từ kb/current_ops.md.
> Status: CLOSED. KHÔNG phải bug — mtime-tươi/content-cũ đọc nhầm; falsifiable check ~08-25.

## `lag_edge_health.csv` staleness — KHÔNG PHẢI BUG, đã đóng hoàn toàn (2026-07-12, đính chính lần 3)
Chuỗi tiền đề sai liên tiếp, mỗi lần đào sâu hơn lại lộ ra tiền đề TRƯỚC đó cũng sai:
1. Ban đầu: "KHÔNG có lịch refresh tự động" — SAI, `Winston_20260712_114800`/`_121456` xác nhận cron có.
2. Sau đó: "cron có nhưng `--refresh` không catch-up chuỗi LAG edge, bug nằm trong script" — CŨNG SAI.
   Dispatch `Taylor_20260712_155038` (yêu cầu fix logic) trả về: **premise sai, không có bug, KHÔNG
   sửa code** (đúng kỷ luật báo cáo lại thay vì tự mở rộng khi thực tế khác dự kiến). Bằng chứng:
   `lag_edge_health()` chạy VÔ ĐIỀU KIỆN mỗi lần invoke (không phụ thuộc flag `--refresh`), rebuild
   toàn bộ series từ cache daily mỗi lần. Input tươi (`earnings_px.pkl` tới 07-10, `earnings_events_
   classified.csv` rebuild daily). BQ live xác nhận **zero** sự kiện NP_R từ 05-05→07-07 (khoảng trống
   giữa 2 mùa BCTC — có thật, không phải lỗi). Sự kiện kế tiếp (MBS Q2, rel 07-08) cần hold 25 phiên
   mới đủ điều kiện vào series, hoàn tất **~08-19**. Pattern mùa vụ 2012-2025 xác nhận: mọi năm series
   đều dừng ~05-09..05-11 rồi nhảy tiếp ~07-15..07-26 — dừng ở 05-11 ngày 07-12 là ĐÚNG lịch sử. Chạy
   thử thật: CSV ghi đè (mtime advance) nhưng md5 byte-identical — đây chính là "mtime tươi/content cũ"
   bị 2 lần trước đọc nhầm thành staleness.
3. **Kết luận cuối cùng: verdict TROUGH hiện tại (mean12 +0.45%, n=631) là số đúng và tươi nhất có thể
   có — w_LAG gate đọc đúng dữ liệu, KHÔNG có gap production.** Probe WARN-only mtime-check (commit
   `f67e09a`) vẫn giữ nguyên, vô hại (chỉ cảnh báo khi mtime quá cũ so ngưỡng, không liên quan gì tới
   nhầm lẫn content này). Không cần action nào thêm.
4. **Falsifiable check cho tương lai** (Taylor đề xuất, chưa cần làm gì bây giờ): nếu đến ~2026-08-25
   mà `lag_edge_health.csv` VẪN dừng ở 05-11 trong khi `earnings_events_classified.csv` đã có sự kiện
   Q2 đủ điều kiện hold-window — LÚC ĐÓ mới là bug thật, cần dispatch lại kiểm tra.
