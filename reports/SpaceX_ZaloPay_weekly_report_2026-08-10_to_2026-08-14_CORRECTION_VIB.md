# ĐÍNH CHÍNH BÁO CÁO TUẦN — VIB / ZALOPAY
## Kỳ báo cáo: 10/08/2026 – 14/08/2026

**Phát hành:** 15/08/2026  
**Phạm vi:** Đính chính giá vốn và P&L cấp mã VIB của tài khoản ZaloPay trong báo cáo tuần đã
phát hành. Các số NAV tổng và tỷ suất NAV trong báo cáo gốc không thay đổi.

## 1. Số đúng

| Mã | KL | Giá vốn thật | Giá cuối kỳ | Giá trị vốn | Giá trị cuối kỳ | Lãi/lỗ | % |
|---|---:|---:|---:|---:|---:|---:|---:|
| VIB | 200 | 14.900 | 14.400 | 2.980.000 | 2.880.000 | **−100.000** | **−3,36%** |

Ba bằng chứng độc lập khớp nhau:

- Broker order `44891`, account ZaloPay `0001743768`: mua 200 cp, `averagePrice=14.900`, ngày
  11/08/2026.
- Broker position `2766562` cuối ngày 14/08: `openQuantity=200`, `costPrice=14.900`,
  `marketPrice=14.400`.
- Journal FILL cùng account/ngày: 200 cp tại 14.900.

## 2. Các chỉ tiêu bị ảnh hưởng

| Chỉ tiêu ZaloPay | Bản đã gửi | Số đính chính | Chênh lệch |
|---|---:|---:|---:|
| Giá vốn sổ bot theo dõi được | 427.071.692 | **430.051.692** | +2.980.000 |
| Giá trị thị trường sổ bot theo dõi được | 426.131.900 | **429.011.900** | +2.880.000 |
| P&L chưa thực hiện sổ bot theo dõi được | −939.792 | **−1.039.792** | **−100.000** |
| Tỷ trọng ngân hàng trong sổ bot theo dõi được | 27,3% | **27,8%** | +0,5 điểm % |
| Phân loại số mã cuối kỳ | 24 bot + 3 legacy | **25 bot + 2 legacy** | VIB là lô bot, không phải legacy |

**Không đổi:** NAV ZaloPay cuối kỳ **939.887.091**, thay đổi NAV tuần **−1,14%**, tổng giá trị
cổ phiếu **894.668.650**, tiền mặt **45.218.441**. Các số này lấy trực tiếp từ toàn bộ vị thế
broker và đã bao gồm VIB; lỗi chỉ nằm ở tầng tái dựng cost-basis/P&L attribution.

## 3. Nguyên nhân gốc

`verify_account_snapshot.py` cộng net quantity trên toàn cửa sổ fill. VIB có lô legacy 9.200 cp
được bán sạch ngày 13/07 nhưng không có buy-history trước khi bot quản lý; sau đó bot mua lô mới
200 cp ngày 11/08. State cũ tính `−9.200 + 200 = −9.000`, nên loại VIB khỏi P&L dù broker đang
giữ 200 cp. Cảnh báo trong báo cáo gốc đã nhận diện việc bị loại, nhưng kết luận “không ảnh hưởng
P&L chi tiết” là sai: nó làm thiếu khoản lỗ chưa thực hiện 100.000 đồng và làm sai exposure ngành.

## 4. Khắc phục cơ học

- CostBook nay dựng một candidate lô mới khi có lệnh mua ở ngày sau legacy-oversell.
- Candidate chỉ được promote vào P&L nếu khối lượng khớp **chính xác** snapshot broker đúng ngày;
  bán dở legacy rồi mua thêm sẽ bị loại fail-closed, không được tự nhận là coverage đầy đủ.
- Regression fixture khóa ca VIB và ca phản chứng snapshot không khớp; các ca LPB/corporate-action
  hiện hữu vẫn phải cùng PASS.

Đây là bản đính chính chính thức và phải được đọc kèm báo cáo tuần gốc.
