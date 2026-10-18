**Gửi bq_admin — nạp lại dữ liệu `tav2_bq.ticker` ngày 14/10/2026**

Anh/chị bq_admin,

**Vấn đề:** bảng `tav2_bq.ticker` ngày giao dịch 2026-10-14 thiếu dòng của 100 mã. Các mã này đều có dòng ngày 13/10 nhưng KHÔNG có dòng nào ngày 14/10.

**Số liệu đo (count dòng `ticker` theo ngày):**
| Ngày | Số dòng |
|---|---|
| 12/10 | 798 |
| 13/10 | 777 |
| **14/10** | **756** |
| 15/10 | 784 |
| 16/10 | 821 |

- 100 mã có dòng 13/10 nhưng không có dòng 14/10 (danh sách kèm file `missing_tickers_2026-10-14.csv`, có khối lượng 12–16/10 để đối chiếu). 97/100 mã có khối lượng giao dịch ngày 13/10, và 71/100 mã có khối lượng ngày 15 hoặc 16/10 ⇒ không phải mã ngừng giao dịch hàng loạt (29 mã còn lại là mã rất kém thanh khoản, nhiều ngày không khớp lệnh).
- Trong 100 mã có 26 mã thuộc rổ HOSE: AAM, ACG, AST, C32, DAT, DBT, DSN, ECO, GHC, GMH, HTL, ICT, L10, LAF, NAV, NVT, QNP, SPM, SSC, STG, TNC, VCA, VCF, VDP, VNG, VTB.
- Phía chúng tôi chỉ đọc bảng, không có đường ghi/backfill `ticker`, nên không tự lấp được. Nguyên nhân nhiều khả năng ở khâu nạp EOD upstream (không trả đủ mã kém thanh khoản ngày 14/10).

**Tác động:** số mã trong rổ tính chỉ số VN-Index có cổ tức của chúng tôi tụt 351 → 333 mã ngày 14/10 (rồi 337, 346 ở 15–16/10), làm cổng kiểm soát báo cáo tuần chặn gửi. Chúng tôi đã xử lý tạm bằng xác nhận thủ công của người dùng (18/10) và báo cáo tuần đã gửi; ngày 14/10 vẫn thiếu dữ liệu trong BQ nên cần nạp lại để chuỗi sạch và các kỳ sau không bị lệch.

**Đề nghị:**
1. Cho biết nguyên nhân thiếu 100 mã ngày 14/10 (vendor không trả hay lỗi nạp).
2. Nạp lại (backfill) các dòng ngày 2026-10-14 cho 100 mã trong file đính kèm, giữ cơ chế như các ngày thường (Price/Close/OShares…), không ghi đè dòng đang có.
3. Báo lại khi xong để chúng tôi dựng lại chuỗi (sẽ không cần ack thủ công nữa).

Nếu mã nào ngày 14/10 thực sự không có phiên (ngừng/tạm dừng giao dịch) xin cho biết để chúng tôi loại khỏi danh sách.

Cảm ơn.
