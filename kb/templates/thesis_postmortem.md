# Hậu kiểm thẻ luận điểm — <TICKER> (<ngày đóng / ngày chấm mốc>)
> Dùng khi ĐÓNG vị thế hoặc khi CHẤM một mốc của `kb/thesis_cards.json`. Mục đích: học cho QUY TRÌNH DD,
> KHÔNG phải chỉnh tham số theo kết quả một ca (N=1). Thẻ: `<ticker> rev<N>`; dd_ref: `<dd_date> rev<N>`.

## 1. Số liệu thực (đo, ghi nguồn — không ước lượng)
| | SpaceX | ZaloPay | Nguồn |
|---|---|---|---|
| Giá vốn (broker) | | | dnse_raw positions costPrice / fill |
| Giá thoát (nếu đã thoát) | | | fill thật (§27), không phải ý định plan |
| Cổ tức tiền nhận | | | `dividend_adjusted_return.py` (§21) |
| Số phiên giữ | | | đếm phiên GD từ ngày vào |
| Lãi/lỗ sau phí & cổ tức | | | |

## 2. Luận điểm đúng/sai — theo MỐC nào
| Mốc / trigger (id trong thẻ) | Hạn | Kết quả thực | checked_ok / checked_bad / waived | Nguồn |
|---|---|---|---|---|
| | | | | |
Luận điểm tổng thể: ĐÚNG / SAI / CHƯA PHÂN ĐỊNH ĐƯỢC (nêu mốc quyết định, không dùng giá làm bằng chứng duy nhất).

## 3. Điều thị trường biết mà DD chưa có
(Tin/số liệu xuất hiện sau `dd_date` giải thích biến động giá; DD có chỗ nào đã cảnh báo không? Giải thích nào còn mở?)

## 4. Quyết định thoát có đúng kỷ luật không
- Thoát do: user quyết / abandon_trigger <id> / sự kiện <…> / không thoát.
- Có theo `exit_policy` của thẻ (value_long ⇒ user quyết) không? Rà 48h khi lỗ ≥15% có được mở không (ngày, ai)?
- Thoát/giữ có dựa vào dữ kiện kiểm được tại thời điểm đó, hay vào giá/cảm giác?

## 5. Bài học cho QUY TRÌNH DD
(Mục nào của checklist DD/skeptic thiếu? mốc nào đáng khoá trước? KHÔNG ghi "đổi ngưỡng X thành Y" theo một ca.)

## 6. Việc sau hậu kiểm
- [ ] cập nhật thẻ (rev+1, status closed) · [ ] ghi `append_event.sh` finding · [ ] đề xuất sửa quy trình (nếu có)
