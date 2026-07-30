---
kind: incident
date: 2026-07-09
topic: tcm-odd-lot-stranded-round-lot-bug
title: >-
  2026-07-09 — TCM odd-lot remainder (10cp) silently stranded forever under a misleading "WAIT_QUOTA" reason — round_lot() bug, not a DNSE restriction
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-09 — TCM odd-lot remainder (10cp) silently stranded forever under a misleading "WAIT_QUOTA" reason — round_lot() bug, not a DNSE restriction

**Hiện tượng:** user thấy 10cp TCM lẻ còn kẹt trong danh mục ZaloPay sau khi plan hôm
đó bán TCM 2.310cp (23 lô chẵn + 10 lẻ). Journal cho thấy `_place_slices` lặp lại mỗi
~20s từ 09:45:57 tới lúc phát hiện: `WAIT_QUOTA ... hết quota participation/đợi KL` —
sai lý do, vì tình trạng thật KHÔNG phải hết quota (tạm thời) mà là cổ phiếu lẻ
(vĩnh viễn với logic cũ).

**Root cause:** `round_lot(qty) = int(qty // LOT) * LOT` làm tròn XUỐNG bất kỳ số nào
<100 về 0. `_child_qty()` gọi hàm này vô điều kiện → với remaining=10, trả về 0 mọi
chu kỳ, mãi mãi (không tự thoát dù chờ bao lâu, khác hẳn hết-quota thật). `_atc_sweep`
(quét cuối phiên) có cùng bug, còn tệ hơn: `if remaining < LOT: continue` không ghi
journal gì cả — hoàn toàn im lặng.

**Điều tra sai lầm ban đầu (tự sửa sau khi user chỉ ra tiếp):** lần đầu tôi nghi ngờ
DNSE cần `orderCategory`/`marketType` riêng cho lô lẻ (đọc kỹ 2 SDK chính thức
`dnse-tech/openapi-sdk` + `dnse-tech/dnse-py` trên GitHub, tìm thấy enum
`BoardId.ODD_LOT = "G4"` nhưng chỉ dùng cho filter secdef/market-data, KHÔNG xác nhận
được cho endpoint đặt lệnh) → đã dừng lại, KHÔNG đoán tham số cho lệnh tiền thật, báo
user. **User tự đặt tay 1 lệnh test thật** (TCM sell 10cp giá 20.000, qua app DNSE) —
lệnh về với `orderCategory: "NORMAL"`, `marketType: "STOCK"` (id=172621, orderStatus
New) — **giống hệt tham số code hiện tại đang dùng**. Kết luận: DNSE không cần tham
số riêng gì cho lô lẻ qua API — bug 100% nằm ở phía `round_lot()` tự làm tròn sai,
không phải hạn chế của broker.

**Fix (commit `f7f9f52`, user ủy quyền sau khi verify bằng lệnh thật):**
1. `_child_qty()`: return `remaining` chưa làm tròn khi `0 < remaining < LOT`, TRƯỚC
   mọi logic cap-theo-giá-trị/participation-quota (đuôi lô lẻ không đáng kể, không
   cần slicing).
2. `_place_slices()`: gate đổi từ `qty < LOT` → `qty <= 0`, để qty lô lẻ chảy xuống
   `place_order()` như slice lô chẵn bình thường thay vì bị chuyển hướng vào nhánh
   "chỉ log".
3. Cap theo `sellable`: so trực tiếp với `sellable` thật khi qty là lô lẻ, không
   `round_lot(sellable)` nữa (cùng bug làm-tròn-về-0 y hệt).
4. `_atc_sweep` — CỐ Ý KHÔNG mở rộng: lệnh thật verify được là `orderType=LO`, không
   phải `ATC` — chưa xác minh ATC hoạt động với lô lẻ nên vẫn bỏ qua ở đây (journal
   `ODD_LOT_SKIP_ATC`, không còn coi là lỗi), để `_place_slices` xử lý qua LO trong
   phiên thường.

**Verify:** `test_trading_bot.py` + `ghost_order_selfcheck.py` (không hồi quy) + check
độc lập gọi thẳng `_child_qty` với đúng tình huống TCM (2310 tổng, đã bán 2300, còn
10) → trả về đúng 10; case còn nguyên 2310 vẫn làm tròn lô chẵn như cũ.

**Bài học:** đừng giả định phía broker hạn chế khi chưa xác minh — lần đầu nghi sai
hướng (nghĩ cần tham số DNSE riêng) suýt tốn công tìm tài liệu vô ích; bug thật nằm
ngay trong code tự viết. Lệnh test tay của user (đúng nguyên tắc "lệnh tiền thật phải
khớp đúng lời user, agent không tự chế tham số") là cách xác minh nhanh và chắc chắn
nhất — nhanh hơn nhiều so với đọc tài liệu API bên thứ ba.
