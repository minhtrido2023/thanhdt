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

**Field thứ 4, dễ bị bỏ sót vì nó KHÔNG nằm trong block `stock`** (thêm 2026-08-19, sự cố TRIM
giả cùng ngày — `mike/kb/coding_guidelines.md` §25): `egg.totalValue` — số dư sản phẩm "Trứng
vàng" của DNSE, một SIBLING riêng của `stock` trong payload `balances`
(`{"stock": {...}, "derivative": {...}, "bond": {...}, "egg": {"totalValue": ...}}`), KHÔNG
cộng vào `totalCash`/`availableCash`. Vốn CHỦ SỞ HỮU thật (đưa vào mọi phép tính "sở hữu bao
nhiêu" — NAV, mẫu số pool rebalance) nhưng cần lệnh RÚT + về tài khoản T+1 mới thành sức mua
(KHÔNG đưa vào bất kỳ phép tính "tiêu được ngay" nào — buying-power/funding-gate). Đọc field
bằng `(bal.get("egg") or {}).get("totalValue")` (payload gốc, TRƯỚC khi thu hẹp về block
`stock`) — xem `mike/bin/park_holdings.py::read_broker_snapshot()` làm ví dụ tham chiếu.

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

**Loan-package margin ratios — `GET /accounts/{acc}/loan-packages?symbol=X`, verified LIVE
2026-08-23** (SpaceX `0002023347`, symbol MBB; job `Mafee_20260823_083327`): response trả trực
tiếp đủ 3 ratio, không cần đoán/tra biểu phí ngoài:
```json
{"id": 1840, "name": "RocketX", "initialRate": 0.5, "interestRate": 0.125,
 "liquidRate": 0.3, "maintenanceRate": 0.4, "type": "M", ...}
```
- `initialRate` = tỷ lệ ký quỹ BAN ĐẦU (0,5 cho 1840/RocketX ⇒ khớp đúng qmaxBuy gấp 2x gói
  1841/GD Tiền mặt `initialRate=1.0`, đã đo 2026-08-03 `spacex_pp0buy_capit_20260803.md`).
- **`maintenanceRate` = 0,4 = tỷ lệ ký quỹ DUY TRÌ (maintenance margin ratio)** — đây là số Phase 1
  margin-valuation-spread cần. Equity ratio (vốn CSH / giá trị TS) rơi dưới ngưỡng này ⇒ cảnh báo
  margin call.
- `liquidRate` = 0,3 = ngưỡng XỬ LÝ BẮT BUỘC (force-sell/liquidation threshold) — thấp hơn
  maintenance đúng logic bậc thang VN (initial 0,5 > maintenance 0,4 > liquid 0,3).
- `interestRate` = 0,125 = lãi vay margin 12,5%/năm, khớp con số đã biết ở `trading_rules.json`.
- Cùng field set cho gói 1841 (cash) — `initialRate=1.0`, `maintenanceRate=0.4`,
  `liquidRate=0.3` — hai gói maintenance/liquid GIỐNG NHAU, chỉ initial khác (đúng vì maintenance/
  liquid là ràng buộc của BROKER trên tài khoản, không phải của từng gói vay).
- **Cảnh báo (warning) DNSE dùng gần đúng `maintenanceRate` làm mốc gọi margin call** — DNSE
  không trả riêng field "warning threshold" khác `maintenanceRate` qua endpoint này; nếu cần số
  chính xác hơn cho ngưỡng CẢNH BÁO SỚM (trước cả maintenance) phải xác nhận qua tổng đài DNSE
  hoặc hợp đồng margin ký — **KHÔNG suy đoán thêm** một tầng ngưỡng thứ 4 không có trong response.
- Field KHÔNG phải per-symbol thật (cùng response y hệt cho mọi mã trong custom30V, đã probe
  28/28 mã 2026-08-04 `probe_margin2_result.json`) — ratio là thuộc tính của GÓI VAY, không phải
  của cổ phiếu thế chấp cụ thể.

**Liên quan / không thay thế:**
- [`../price-volume/dnse_api_live.md`](../price-volume/dnse_api_live.md) — entry registry cho
  DNSE làm nguồn giá/khối lượng/vị thế TRONG NGÀY (bright-line rule `coding_guidelines.md` §6:
  BQ không bao giờ dùng cho số cùng ngày). File này (guideline) là **cách gọi đúng** API đó;
  `dnse_api_live.md` là **khi nào dùng nguồn nào**.
- `coding_guidelines.md` §12 (lọc `account_no` khi đọc file dùng chung nhiều account) áp dụng y
  hệt nếu dashboard fan-out nhiều sub-account.
