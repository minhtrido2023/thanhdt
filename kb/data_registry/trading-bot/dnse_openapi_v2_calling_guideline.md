---
kind: reference-doc
status: CANONICAL
source: mike/agents/Mike/dnse_api_guideline_for_dashboard_bot.md
group: trading-bot
scope: calling convention / gotchas for DNSE OpenAPI v2 (all endpoints, not one data table)
---

# DNSE OpenAPI v2 — Calling Guideline (full doc: `agents/Mike/dnse_api_guideline_for_dashboard_bot.md`)

**Là gì:** hướng dẫn gọi DNSE OpenAPI v2 đầy đủ — auth/HMAC signing, trading-token OTP flow,
endpoint reference cho dashboard (balances/positions/orders/NAV/quotes), và 10+ "gotcha" đã gây
sự cố thật trên 2 tài khoản DNSE sống (SpaceX margin + ZaloPay cash-only) từ 2026-07-01. Biên
soạn 2026-08-03 từ `dnse_api.py` + `trading_bot/brokers.py` (`DNSEBroker`) + incident postmortems
2026-07-06→07-28.

**Dùng để làm gì:** nguồn tham chiếu bắt buộc khi build **dashboard quản lý danh mục DNSE**
(portfolio management — hiển thị NAV/balance/position/order, không đặt lệnh) — task mới, tách
biệt khỏi `trading_bot` hiện có. Đọc trước khi viết bất kỳ code nào gọi DNSE OpenAPI cho mục đích
này.

**Điểm quan trọng nhất (đọc trước khi hiển thị BẤT KỲ số "cash" nào):** 3 field cash khác nhau —
`availableCash` (tiền đã settle), `totalCash` (dùng cho NAV), `pp0Buy`/`qmaxBuy` từ `ppse` (sức
mua thật NGAY bây giờ, gate mua duy nhất đáng tin). Nhầm 3 field này từng gây incident thật
(bot tưởng hết tiền, ngồi im cả buổi sáng dù thực ra có sức mua).

**Các điểm khác đáng chú ý** (chi tiết đầy đủ trong file gốc):
- HMAC signing ký trên PATH THÔI (không kèm query string); clock skew >±1 phút → 401/403 dù
  HMAC đúng.
- Trading-token (OTP) chỉ cần cho đặt/sửa/huỷ lệnh — dashboard thuần đọc không bao giờ cần.
  Nhiều sub-account CHUNG 1 login → CHUNG 1 OTP channel/token, dễ race (`INVALID_OTP`) nếu 2
  process cùng xin OTP một lúc.
- `balances` JSON không đồng nhất shape (object/list/nested `stock`/`derivative`), field case
  lộn xộn (`availablecash`/`availableCash`) → parse phòng thủ, thử nhiều cách viết.
- Positions: `total` (đang giữ) ≠ `sellable`/`tradeQuantity` (bán được HÔM NAY) — lệch nhau tới
  chiều T+2 (settlement chuyển sang bán được từ **buổi CHIỀU** T+2, không phải từ đầu phiên).
- Quote/trade theo board (`G1`=lô chẵn, `G4`=lô lẻ, `T*`=thoả thuận) — phải chọn đúng `G1`, không
  lấy đại `rows[0]`.
- `loanPackageId` bắt buộc trên MỌI lệnh kể cả cash-only (không phải field riêng cho margin).
- Đặt lệnh: broker's live order book là nguồn sự thật duy nhất, không tái tạo state từ log cục bộ.

**Liên quan / không thay thế:**
- [`../price-volume/dnse_api_live.md`](../price-volume/dnse_api_live.md) — entry registry cho
  DNSE làm nguồn giá/khối lượng/vị thế TRONG NGÀY (bright-line rule `coding_guidelines.md` §6:
  BQ không bao giờ dùng cho số cùng ngày). File này (guideline) là **cách gọi đúng** API đó;
  `dnse_api_live.md` là **khi nào dùng nguồn nào**.
- `coding_guidelines.md` §12 (lọc `account_no` khi đọc file dùng chung nhiều account) áp dụng y
  hệt nếu dashboard fan-out nhiều sub-account.
