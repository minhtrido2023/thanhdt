# Template điền nhanh — tình trạng tài khoản PHS

Copy khối dưới, điền số từ app PHS (màn hình tổng quan tài khoản / margin), gửi lại cho Mike.
Không cần chụp ảnh — điền số trực tiếp là đủ để cập nhật `snapshot_history.csv`.

Điền được bao nhiêu tài khoản cũng được (không bắt buộc đủ cả 5 mỗi lần).
Để trống ô nào không có/không rõ — đừng bịa số.

---

```
Ngày: 2026-09-15
Tài khoản: 093399   (một trong: 093399 / 078901 / 111282 / 193399 / 393399)
NAV (tỷ):
RTT (%):
Sức mua / ppse (tỷ, có thể âm):
Nợ margin (tỷ):
Tổng thị giá danh mục (tỷ):
Tiền mặt khả dụng (tỷ):
Ghi chú:
```

---

## Giải thích từng ô (đối chiếu đúng tên trên app PHS)

| Ô trong template | Tên trên app PHS |
|---|---|
| NAV | NAV / Tổng tài sản ròng |
| RTT | RTT % (tỷ lệ ký quỹ hiện tại) — dưới 100% là vùng cảnh báo |
| Sức mua / ppse | Sức mua |
| Nợ margin | Dư nợ margin |
| Tổng thị giá danh mục | Tổng giá trị chứng khoán / Thị giá |
| Tiền mặt khả dụng | Số dư khả dụng |

## Sub-account ID (điền 1 LẦN DUY NHẤT nếu tìm thấy, không cần điền lại mỗi lần)

3 tài khoản 111282/193399/393399 API không đọc được vì thiếu ID kỹ thuật này (không phải NAV/RTT
— field khác, thường nằm ở mục Cài đặt / Thông tin tài khoản trên app PHS, dạng 10 chữ số).
Nếu tìm thấy, ghi vào đây một lần, khỏi lặp lại:

```
022C111282 → sub-account ID: ____________
022C193399 → sub-account ID: ____________
022C393399 → sub-account ID: ____________
```
