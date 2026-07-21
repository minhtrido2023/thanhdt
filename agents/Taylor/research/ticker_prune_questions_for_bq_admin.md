# Câu hỏi về `tav2_bq.ticker_prune` gửi bq_admin

Bối cảnh: chúng tôi đang xây dựng bộ quy tắc quản trị universe dựa trên `ticker_prune` cho hệ
thống trading/research, và trong lúc điều tra đã phát hiện vài điểm cần bq_admin xác nhận trước
khi quyết định hướng đi. Không có ý phê bình — chỉ cần hiểu đúng thiết kế để dùng bảng cho đúng.

## Những gì chúng tôi đã đo được (dữ liệu thật, 2026-07-21)

- **Pool ticker có vẻ bị đóng băng 2026-03-13 → 2026-07-06** (không có mã mới nào vào trong ~4
  tháng), rồi được mở băng bằng 1 lô 41 mã đúng ngày 2026-07-06.
- **Một số mã niêm yết mới chờ rất lâu mới vào bảng**: VPL (Vinpearl) chờ 419 ngày, SBG 948 ngày;
  24 mã niêm yết 2023-2026 tới nay vẫn chưa từng xuất hiện trong bảng.
- **So với 1 bản backup lấy ngày 2026-07-13, chúng tôi thấy 10.850 dòng lịch sử (2014-2025) mới
  xuất hiện trong bảng chỉ trong 8 ngày** (vd IVS: 0 dòng ở backup → 1.622 dòng từ năm 2012 ở bản
  hiện tại; PXL, TIS tương tự) — có vẻ như một đợt backfill lịch sử đang diễn ra.

## 10 câu hỏi cụ thể

1. Rule chính xác để một mã được đưa vào/loại khỏi `ticker_prune` là gì? Ngưỡng thanh khoản nào,
   cửa sổ đánh giá bao nhiêu phiên, tần suất đánh giá lại?
2. Có một danh sách curated thủ công ("legacy product selection") nằm trên rule thanh khoản tự
   động không? Nếu có, ai chỉnh sửa, khi nào, theo trigger gì?
3. Có đúng là pool bị đóng băng từ 2026-03-13 đến 2026-07-06 không? Lô 41 mã thêm vào ngày
   2026-07-06 là sửa lỗi thủ công (bổ sung mã bị bỏ sót) hay một thay đổi rule?
4. **ETL có ghi đè/bổ sung dòng dữ liệu lịch sử không?** Chúng tôi đo được 10.850 dòng của giai
   đoạn 2014-2025 mới xuất hiện trong 8 ngày gần đây. Đây có phải một đợt backfill có chủ đích
   không? Đang chạy dở hay đã xong? Có lịch trình để chúng tôi biết khi nào bảng ổn định lại
   không?
5. Khi một mã mới được thêm vào bảng, lịch sử của mã đó có được backfill toàn bộ về quá khứ
   không? (Chúng tôi thấy FRT đã được backfill đầy đủ, nhưng 41 mã thêm ngày 07-06 thì chưa —
   vì sao có sự khác biệt?)
6. **Membership trong quá khứ được tính theo kiểu "point-in-time"** (chỉ dùng thông tin có sẵn
   tại đúng thời điểm đó) **hay áp tiêu chí hiện tại ngược lại cho quá khứ?** Đây là câu quan
   trọng nhất đối với các mô hình backtest của chúng tôi — nếu là cách thứ hai, mọi kết quả
   backtest dùng bảng này sẽ có look-ahead bias.
7. Có versioning/changelog cho các tiêu chí lựa chọn không? Bảng hiện đang chạy phiên bản rule
   nào, lần thay đổi gần nhất là khi nào?
8. Mã niêm yết mới có một "đường tự động" để vào bảng không? Chúng tôi thấy một số mã (ABW, GDA,
   MZG, TCX, VPX) vào bảng sau khoảng ~85 ngày kể từ ngày niêm yết — nhưng nhiều mã khác (VNZ,
   QNP, AAH, DKG, SLD, và ~20 mã khác niêm yết 2023-2026) tới nay chưa từng vào, và VPL phải chờ
   419 ngày. Vì sao có sự khác biệt này?
9. Có thể cung cấp cho chúng tôi một bảng/snapshot dạng "as-of" (giữ lại membership của từng ngày,
   bất biến theo thời gian) thay vì chỉ có trạng thái hiện tại không? Nếu không, chúng tôi sẽ tự
   xây lớp này ở phía mình.
10. Khi một mã bị hủy niêm yết (delist), lịch sử giao dịch của mã đó trong bảng được giữ nguyên
    hay bị xóa?

---
*Tài liệu điều tra đầy đủ (nội bộ): `mike/agents/Taylor/research/ticker_prune_universe_governance.md`*
