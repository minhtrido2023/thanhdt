# Audit dữ liệu 8L (mùa BCTC Q2)
> Dự án đã đóng — tách khỏi context_pack 2026-07-13. Chi tiết gốc từ kb/current_ops.md.
> Status: CLOSED. XONG — 8L đầy đủ; 3 fix cache/cadence/doc dispatch (Winston_20260713_103213).

## Audit dữ liệu 8L XONG (Winston_20260713_100733) — 3 fix đang dispatch (2026-07-13)
User lo ngại dữ liệu 8L có phản ánh đầy đủ thông tin hệ thống hay không (mùa BCTC Q2 đang bắt đầu).
Audit xác nhận: **hôm nay dữ liệu 8L ĐẦY ĐỦ** — chỉ 1 mã (MBS) đã công bố Q2, đã có mặt đúng ở cả
3 lớp rating. Phát hiện 2 vấn đề kỹ thuật:
- Cron `fa_ratings_8l` thứ Bảy 07-11 chưa từng chạy tự động (bảng tươi nhờ ghi tay 07-12); lần
  scheduled đầu tiên = thứ Bảy 07-18, cần để mắt xác nhận.
- Cache local (research/backtest, KHÔNG phải đường tiền thật) lệch do sync mode `--delta` không
  tương thích cách refresh mới → tối nay 23:45 sẽ tự bắn 1 cảnh báo ĐÚNG NHƯNG không phải sự cố
  thật (by design), sẽ lặp mỗi tuần nếu không sửa.
- Điểm cần lưu ý: rebalance quý ~08-05, mã công bố 08-02..08-04 sẽ chưa kịp có rating Q2.

User duyệt cả 3 đề xuất Winston: (1) sửa cache sync sang full-download cho 2 bảng rating; (2) tăng
tần suất refresh 2x/tuần trong mùa BCTC cao điểm (~4-6 tuần, tới ~08-05); (3) cập nhật 3 chỗ tài
liệu lỗi thời trong `data_registry.md`. Dispatch job `Winston_20260713_103213`.
