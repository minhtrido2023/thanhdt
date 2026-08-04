# Test lệnh THẬT gói vay 1840 (RocketX) — SpaceX · MBB · 100cp

**Job**: `Mafee_20260804_021040` · **Ngày**: 2026-08-04 · **Tài khoản**: SpaceX `0002023347`

## KẾT LUẬN NGẮN

**CHƯA KẾT LUẬN ĐƯỢC — lệnh mua KHÔNG được đặt.** Bị **lớp phân quyền của harness Claude Code
chặn** (`Permission for this action was denied by the Claude Code auto mode classifier`) đúng ở
bước gọi script đặt lệnh. KHÔNG phải DNSE từ chối, KHÔNG phải thiếu trading-token, KHÔNG phải
thiếu tiền, KHÔNG phải thị trường đóng — toàn bộ tiền đề kỹ thuật đã sẵn sàng và đã kiểm chứng
bằng API thật (bên dưới).

**Trạng thái tài khoản: KHÔNG THAY ĐỔI.** Đã verify sau khi bị chặn:
- Sổ lệnh hôm nay: `so lenh trong so hom nay: 0` (rows = `null`)
- File state chống-đặt-trùng: `ls: cannot access '.../probe_1840_state.json': No such file or directory`
→ **Không có lệnh nào được gửi đi.** Không cần dọn dẹp, không có vị thế mở thêm, không có nợ mới.

Tôi **KHÔNG tìm cách lách** lớp chặn này (đúng kỷ luật: đây là guardrail cho hành động tiền thật
không đảo ngược). Cần user/Mike cấp quyền chạy lệnh này thì mới test tiếp được.

---

## Điều CÒN LẠI chưa kiểm chứng (mục đích gốc của job)

DNSE có **thực sự nhận** `loanPackageId=1840` trên 1 lệnh ĐẶT THẬT và **ghi đúng nợ margin** hay
không — **vẫn chưa có bằng chứng**. Bằng chứng gián tiếp thu được hôm nay (mục 3) mạnh hơn trước
nhưng vẫn là số DNSE *tính trước*, không phải nợ DNSE *ghi sổ sau khi khớp*.

---

## 1. Tiền đề đã kiểm chứng — RAW LOG

Thời điểm: 2026-08-04 09:11–09:16 ICT (phiên sáng mở, `data/BOT_STOP` không tồn tại).
Script recon read-only: `mike/agents/Mafee/probe_live_lever_recon_20260804.py`
Log đầy đủ: `mike/agents/Mafee/recon_20260804.log`

### 1a. Trading-token — CÓ THẬT (khác lần 2026-08-03)

```
[dnse] kết nối OK [SpaceX_probe1840] tiểu khoản 0002023347

[recon] has_trading_token = True
[recon] client.loan_package_id (default account) = 1841
```

Lần đo 2026-08-03 KHÔNG có token nên chỉ đọc được. Lần này token thật đã có
(`data/dnse_trading_token.json`, mtime 09:05 hôm nay) → điều kiện đặt lệnh đã đủ về phía DNSE.

### 1b. Balances TRƯỚC — mốc so sánh nợ margin sạch

```json
{
  "stock": {
    "totalCash": 14596244,
    "availableCash": 4821143,
    "depositInterest": 101,
    "totalDebt": 0,
    "depositFeeAmount": 762,
    "secureAmount": 0,
    "orderSecured": 0,
    "withdrawableCash": 4820381,
    "cashDividendReceiving": 9775000
  },
  "derivative": {
    "pendingDepositWithdraw": 0, "remainSecure": 0, "usedSecure": 0,
    "pendingSecure": 0, "holdTaxAndFee": 0, "totalLoanDebt": 0
  }
}
```

**`totalDebt = 0`** — mốc lý tưởng: bất kỳ khoản nợ nào xuất hiện sau lệnh mua đều là do gói 1840.

### 1c. Vị thế MBB TRƯỚC — giải được ràng buộc T+2

```json
{
  "id": 2674328, "marketType": "STOCK", "symbol": "MBB",
  "accountNo": "0002023347", "status": "OPEN",
  "loanPackageId": 1841, "side": "NB",
  "accumulateQuantity": 5800, "tradeQuantity": 2400,
  "closedQuantity": 3400, "openQuantity": 2400,
  "costPrice": 24850, "marketPrice": 24000,
  "breakEvenPrice": 24950.2963, "averageClosePrice": 25650,
  "createdDate": "2026-07-02T02:15:12.372253Z",
  "modifiedDate": "2026-08-03T11:23:33.056207Z"
}
```

Parsed: `"MBB": {"total": 2400, "sellable": 2400}`.

**Quan trọng**: SpaceX đã sẵn có **2400 MBB, sellable 2400**. Nếu không có tồn kho này thì yêu
cầu "bán lại ngay trong cùng phiên" của job **BẤT KHẢ THI** — cổ mua hôm nay chỉ sellable từ phiên
chiều T+2 (`kb/context_execution_mini.md`). Nhờ tồn kho sẵn có, lệnh bán 100 cp là hợp lệ và đưa
vị thế ròng cuối ngày về đúng 2400 = trạng thái ban đầu (không giữ thêm vị thế qua đêm).
Lưu ý ghi rõ để không hiểu nhầm: ở tầng lot của broker, 100 cp bán ra lấy từ hàng đã settle, còn
100 cp mua mới vẫn nằm trong `accumulateQuantity` — **exposure ròng bằng 0 thay đổi**, không phải
"đóng đúng lot vừa mua".

### 1d. Vị thế MBB hiện đang gắn `loanPackageId: 1841`

Đây là chi tiết làm cho phép thử có giá trị: nếu lệnh mua bằng gói 1840 khớp, ta xem được DNSE
tạo **lot riêng gắn 1840** hay gộp vào lot 1841 — bằng chứng trực tiếp nhất về việc gói có được
ghi nhận hay không.

---

## 2. Gói vay 1840 HỢP LỆ cho MBB — RAW

`GET /accounts/0002023347/loan-packages?symbol=MBB`:

```json
{
  "symbol": "MBB", "marketType": "STOCK",
  "loanPackages": [
    { "id": 1841, "name": "GD Tiền mặt", "initialRate": 1.0, "interestRate": 0.125,
      "liquidRate": 0.3, "maintenanceRate": 0.4, "type": "M",
      "brokerFirmBuyingFeeRate": 0.0007, "brokerFirmSellingFeeRate": 0.0007 },
    { "id": 1840, "name": "RocketX", "initialRate": 0.5, "interestRate": 0.125,
      "liquidRate": 0.3, "maintenanceRate": 0.4, "type": "M",
      "brokerFirmBuyingFeeRate": 0.0007, "brokerFirmSellingFeeRate": 0.0007 }
  ]
}
```

→ `_validate_lever_package("MBB", 1840)` sẽ trả `(1840, True, "")`: gói 1840 nằm trong danh sách
hợp lệ, KHÔNG rơi về fail-safe gói default. `initialRate = 0.5` đúng như `_v25_margin_prep` ghi
trong `secrets/trading_bot_accounts.json`.

---

## 3. BẰNG CHỨNG GIÁN TIẾP MỚI (mạnh nhất hiện có): `ppse` phân biệt 2 gói

`GET /accounts/0002023347/ppse?symbol=MBB&price=24200`, chạy 2 lần với 2 gói khác nhau:

```
===== ppse MBB @24200 gói 1841 (RAW) =====
{ "qmaxBuy": 17553, "qmaxSell": 2400, "price": 24200, "pp0Buy": 425209429 }

===== ppse MBB @24200 gói 1840 (RAW) =====
{ "qmaxBuy": 35073, "qmaxSell": 0,    "price": 24200, "pp0Buy": 425209429 }
```

**Đọc số thật, không suy diễn:**
- `qmaxBuy` gói 1840 / gói 1841 = 35073 / 17553 = **1,998×** — khớp gần như chính xác tỉ lệ
  `initialRate` 1,0 → 0,5. DNSE **có phân biệt** tham số `loanPackageId` truyền vào và tính sức
  mua theo đúng đòn bẩy của gói.
- `pp0Buy` **giống hệt nhau** (425.209.429) ở cả 2 gói — tức `pp0Buy` KHÔNG phản ánh đòn bẩy gói,
  chỉ `qmaxBuy` mới phản ánh. *Đây là cảnh báo cho bất kỳ code nào định dùng `pp0Buy` để đo sức
  mua có-đòn-bẩy — nó sẽ under-report gói 1840. Ghi lại vì hôm 2026-08-03 tôi đọc chính `pp0Buy`
  này.*
- `qmaxSell` gói 1840 = **0** trong khi gói 1841 = 2400 — hợp lý: 2400 cp đang nằm ở lot 1841,
  không phải lot 1840. Củng cố suy đoán DNSE quản lý tồn kho **theo từng gói vay**.

**Giới hạn của bằng chứng này**: `ppse` là API *tính trước* (pre-trade sizing). Nó chứng minh DNSE
**đọc** tham số `loanPackageId=1840`, **không** chứng minh DNSE **ghi nợ margin** đúng sau khi
lệnh khớp. Đó chính xác là khoảng trống mà job này sinh ra để lấp và **vẫn chưa lấp được**.

---

## 4. Lệnh đã chuẩn bị (chưa gửi)

Script: `mike/agents/Mafee/probe_live_lever_order_20260804.py` (standalone, import thẳng
`DNSEBroker`; KHÔNG đụng `bot_execute`/`Executor`/`apply_capit_lever`/`trading_rules.json`).
Có guard chống đặt trùng: order_id ghi atomic vào `probe_1840_state.json` NGAY sau khi API trả,
chạy lại mà state đã có id thì từ chối đặt tiếp (§5 coding_guidelines).

Request lẽ ra sẽ gửi (giá theo quote thật lúc 09:15, ask1 = 24.200):

```
[BUY] REQUEST: account=0002023347 symbol=MBB qty=100 side=buy
      order_type=LO price=24200 loan_package_id=1840
```

Giá trị lệnh 2.420.000đ · `availableCash` 4.821.143đ (đủ tiền kể cả không vay) ·
nợ margin kỳ vọng nếu 1840 được áp đúng ≈ 1.210.000đ (50% × 2,42tr).

> **Rủi ro đã lường trước, cần nói rõ trước khi chạy lại**: vì tài khoản **đủ tiền mặt** cho toàn
> bộ 2,42tr, hoàn toàn có khả năng DNSE trừ tiền mặt trước và **`totalDebt` vẫn = 0** dù gói 1840
> được nhận đúng. Nếu vậy thì kết quả "không thấy nợ" **KHÔNG** đồng nghĩa "gói 1840 bị bỏ qua" —
> phải đọc `loanPackageId` trên lot vị thế mới (mục 1d) mới phân biệt được 2 khả năng. Nếu muốn
> ép nợ margin xuất hiện chắc chắn thì phải đặt lệnh có giá trị **lớn hơn `availableCash`**
> (>4,82tr, tức ≥200 cp) — việc đó **vượt phạm vi đã duyệt (100 cp)** nên tôi KHÔNG tự làm.

## 5. Quote MBB tại thời điểm đo (RAW)

```json
{ "symbol": "MBB", "boardId": "G1", "basicPrice": 24, "ceilingPrice": 25.65,
  "floorPrice": 22.35, "securityStatus": "NO_HALT", "time": "2026-08-03 14:45:03.015",
  "matchPrice": 24, "matchQtty": 30, "avgPrice": 23.631, "totalVolumeTraded": 2273510,
  "highestPrice": 24.05, "lowestPrice": 22.75, "openPrice": 22.75,
  "bidPrice1": 24.15, "offerPrice1": 24.2 }
```
`Quote.last=24000.0 bid=24150.0 ask=24200.0 ref=24000.0 ceil=25650.0 floor=22350.0`

---

## 6. Ranh giới cứng — đã tuân thủ đủ

| Ràng buộc | Trạng thái |
|---|---|
| Không chạm `data/trading_rules.json` | ✅ không đọc, không sửa |
| Không dùng `apply_capit_lever` / `bot_execute` / `Executor` cascade | ✅ script standalone, chỉ import `DNSEBroker` |
| Không đổi `secrets/trading_bot_accounts.json` | ✅ **verify**: SpaceX `loan_package_id` vẫn = **1841**; 1840 chỉ truyền per-order trong script |
| Không đặt lệnh lặp | ✅ 0 lệnh được đặt |
| Không giữ vị thế qua đêm | ✅ không có vị thế mới nào |
| Không giả lập / mô tả kết quả mong đợi thay kết quả thật | ✅ báo đúng: **bị chặn, chưa test được** |

## 7. Cần gì để chạy tiếp

1. **User/Mike cấp quyền** cho lệnh Bash chạy script đặt lệnh này (harness chặn, không phải DNSE).
2. Chạy tuần tự: `buy` → `watch` → `balances` → `sell` → `balances` (script đã tách sẵn subcommand
   để mỗi bước dừng lại kiểm tra được, không chạy liền một mạch).
3. Cửa sổ thời gian: còn phiên sáng tới 11:30 hoặc phiên chiều 13:00–14:30 ICT hôm nay. Token
   DNSE hạn 8h từ 09:05 → còn hiệu lực cả ngày.
4. Quyết định cần user chốt trước (mục 4): giữ đúng **100 cp** (chấp nhận khả năng `totalDebt` vẫn
   = 0 do đủ tiền mặt, kết luận phải dựa vào `loanPackageId` của lot vị thế), hay **nâng lên ≥200
   cp** để ép nợ margin hiện ra rõ ràng. Tôi KHÔNG tự nâng quy mô.
