---
kind: source
group: trading-bot
title: PHS FlashAPI (flashapi.phs.vn) — đánh giá go-live, CHƯA WIRE
status: EVALUATION — không phải nguồn sống, chỉ ghi lại kết quả nghiên cứu 2026-08-20
---

# PHS FlashAPI — đánh giá go-live (2026-08-20)

User báo PHS có API mới hỗ trợ cả CƠ SỞ lẫn PHÁI SINH: https://flashapi.phs.vn/docs/chao-mung
(doc site thật: `phuhungsecurities.mintlify.app`, `llms.txt` liệt kê 39 trang).

## Kết luận quan trọng nhất

**FlashAPI (`flashapi.phs.vn`) là sản phẩm KHÁC, MỚI HƠN "PHS Open API FLEX" đang có trong code
(`phs_flex_api.py`, base URL `fgateway.phs.vn`).** Khác host, khác mô hình xác thực hoàn toàn:
- FLEX cũ: OAuth2 client_credentials (`client_id`/`client_secret` PHS cấp riêng — **CHƯA CÓ**,
  đây là lý do `PHSBroker.place_order()` hiện bị chặn, comment trong `brokers.py` ghi lỗi
  `-700003`).
- FlashAPI mới: login bằng **username/password của chính tài khoản chứng khoán** (không có
  client_id/secret ở tầng API — xác nhận qua doc + probe sandbox thật, xem dưới), trả thẳng
  `access_token` + `otp_token` trong 1 lần gọi.

**`-700003` = `ERR_OD_ODTYPE_NOTFOUND`** (order type không hợp lệ) — xác nhận từ bảng mã lỗi
FlashAPI thật. KHÔNG liên quan gì tới "chưa cấp client_id/secret". Comment cũ trong `brokers.py`
mô tả đúng tình trạng của FLEX cũ, không áp dụng cho FlashAPI.

⇒ Hai API riêng biệt, không phải "FlashAPI = FLEX được tài liệu hoá đầy đủ hơn". Cần build
**adapter mới** (`PHSFlashBroker`?), không sửa `PHSBroker`/`phs_flex_api.py` hiện có.

## Đã verify THẬT bằng probe sandbox (không chỉ đọc docs — 2026-08-20, curl trực tiếp)

Sandbox base: `https://flashapi.phs.vn/sandbox/oapi/...` — dùng demo credentials CÔNG KHAI trong
docs (`022C099995` / `123456aA@`), không cần đăng ký:

- `POST /auth/gen-secret-key/underlying` → login OK thật, trả `access_token`/`refresh_token`/
  `otp_token`/`expires_in=28800`. **`otp_token` là NGẪU NHIÊN mỗi lần login** (đính chính 1 báo
  cáo con nói "cố định" — SAI, đã verify 2 lần login cho 2 giá trị khác nhau).
- `GET /priceboard/symbol-latest-data?symbolList=ACB,FPT,VIC` → 200, payload đầy đủ **CÓ**
  `ce`(ceiling)/`fl`(floor)/`re`(reference, = trung bình ce+fl đúng công thức)/`marketId`(STO)/
  `m`(HOSE) — đính chính báo cáo con nói "không thấy ceiling/floor" — SAI, có đủ. **Bid/ask chỉ
  có dạng lô lẻ 3 mức (`bbOd`/`boOd`)**, KHÔNG thấy bid/ask lô chẵn chuẩn (bid1-3/ask1-3) trong
  response này — cần endpoint khác (`symbol-statics-data`, price ladder) cho L2 lô chẵn, GAP THẬT
  cần làm rõ trước khi build lại cơ chế `_phs_l2_snapshot` tương đương.
- `GET /accounts/{id}/underlying/portfolio` → 200, field khớp đúng tài liệu (`total`, `trade`,
  `costPrice`, `pnlAmt`, `receivingT0/T1/T2`...).
- `GET /accounts/{id}/underlying/dailyOrder` → 200, field khớp tài liệu.
- `GET /accounts/{id}/derivative/openPositions` → 200, field khớp tài liệu (`position`, `qtty`,
  `vwap`, `nonrplamt`...).
- `POST /accounts/{id}/orders/underlying` (LO và ATO đều test) → 200, `{"orderid":
  "8000180326000219"}` **CỐ ĐỊNH bất kể input** — sandbox không validate order-type thật, KHÔNG
  dùng được để suy ra enum order type hợp lệ (ATO/ATC/MP...).
- `GET /accounts/{id}/underlying/balance` → 200 (**probe thật**, `underlying/buyingPower` là tên
  PRODUCTION per PHS support, sandbox dùng tên `balance`). Fields: `ppse`(sức mua an toàn),
  `ppseref`, `mrratioloan`, `mrpriceloan`(margin loan info), `maxqtty`, `trade`, `receiving`,
  `rtt`, `allbalance`, `avladvance`, `mrirate`, `blocked`, `mortage`. Response là array `[{}]`.
- `GET /accounts/{id}/derivative/balance` → 200. Fields: `cashonhand`, `pp`(purchasing power),
  `nav`, `eca`, `accountratio`, `acccountstatus`("An toàn"), `requiredmarginamt`, `vmamt`(P&L
  biến động), `nonpnlamt`, `execpnlamt`, `totalfeeamt`, DTA/CCP split cho mọi field margin.
  `accountid` trả về là sub-account fno thật (`"0104005401"`).
- `GET /accounts/{id}/underlying/assets` → 404 trong sandbox (PHS support xác nhận path đúng cho
  production là `/underlying/assets`; sandbox chưa implement hoặc dùng tên khác).
- `GET /priceboard/all-stocks` (và 3 biến thể tên khác) → 404 tất cả — path thật của
  "get_all_stocks" CHƯA XÁC ĐỊNH.
- **Quan trọng — sandbox không validate accountId/username/password** (PHS support xác nhận
  2026-08-20): có thể dùng mock data bất kỳ. Vì vậy 404 trước đây KHÔNG do sai accountId mà do
  path chưa implement trong sandbox.

## Thông tin bổ sung từ PHS support (Zalo, 2026-08-20 ~14:07 ICT)

**`accountId` trong path API = SỐ TIỂU KHOẢN, không phải số tài khoản master:**
- Tài khoản master: `022Cxxxx` (prefix 4 ký tự + số)
- Tiểu khoản cơ sở (cho API `/eqt`): `0120xxxx` (8 chữ số)
- Tiểu khoản phái sinh (cho API `/fno`): `02120xxxx` (9 chữ số)

**Hệ quả quan trọng:**
1. Sandbox demo dùng `022C099995` cho `accountId` → 404 "buying power" có thể do sandbox KHÔNG
   tự sinh tiểu khoản riêng, hoặc path thật dùng **`/eqt/`** và **`/fno/`** (không phải
   `/underlying/` và `/derivative/`). Chưa re-probe được (sandbox 503 lúc 14:12 ICT).
2. **Gap #8 ĐÃ XÁC NHẬN**: cơ sở và phái sinh dùng HAI số tiểu khoản KHÁC NHAU — adapter phải
   giữ cả hai, routing theo loại asset.
3. Tham chiếu path mới từ PHS support: "api /eqt" = underlying, "api /fno" = derivatives → gợi
   ý endpoint thật có thể là `/accounts/{eqt_subacc}/eqt/...` và `/accounts/{fno_subacc}/fno/...`
   thay vì `/underlying/...`, `/derivative/...`. **Cần verify lại sau khi sandbox online.**
4. Nếu đúng, các probe cũ (portfolio/dailyOrder/openPositions) hoạt động vì sandbox dùng path
   `/underlying/` và `/derivative/` — production có thể khác. Hỏi PHS để xác nhận.

## Gap PHẢI hỏi PHS trực tiếp trước khi build production adapter

### ĐÃ XÁC NHẬN từ PHS support (2026-08-20):
- **Gap #1 (Buying power/assets path)**: ĐÃ XÁC NHẬN production paths:
  - `GET /oapi/accounts/:accountId/underlying/buyingPower` (cơ sở)
  - `GET /oapi/accounts/:accountId/underlying/assets` (tổng tài sản cơ sở)
  - Sandbox dùng `underlying/balance` (probe 200 thật). Production dùng `buyingPower`.
- **Gap #2 (Order type enum)**: ĐÃ XÁC NHẬN:
  - HOSE: `LO`, `ATO`, `ATC`, `MP`
  - HNX & UPCOM: `LO`, `MOK`, `MAK`, `PLO`
- **Gap #3 (Margin qua API)**: XÁC NHẬN MỨC ĐỘ HỖ TRỢ:
  - **Xem margin overview**: CÓ, qua `GET /underlying/assets`
  - **Đăng ký gói margin mới / gia hạn / tất toán**: KHÔNG có API hiện tại — chỉ trên PHS Xpro
    Trading (app). "Giai đoạn sau Flash API sẽ bổ sung." → **Ràng buộc quan trọng:** nếu dùng
    margin tại PHS, phải tự quản lý vòng đời margin thủ công qua app, KHÔNG tự động hoá được qua
    bot như DNSE.
- **Gap #8 (Tiểu khoản riêng cho eqt vs fno)**: ĐÃ XÁC NHẬN — tách biệt hoàn toàn:
  - Master: `022Cxxxx`; Sub-eqt: `0120xxxx`; Sub-fno: `02120xxxx`
  - Adapter phải lưu cả hai sub-account số, routing theo asset type.

### Còn treo (5 gap):
1. `refresh_token` — trả về nhưng không có endpoint refresh được tài liệu hoá; phải re-login
   mỗi 8h nếu đúng vậy.
2. OTP thật ở production: sandbox otp_token phát ngẫu nhiên trong login response, không có bước
   verify tách rời — production có passive hoàn toàn như sandbox không, hay cần verify SMS/OTP?
3. WebSocket/streaming real-time — REST polling thuần trong probe; Registration form có mục
   "WebSocket streaming" riêng — gợi ý tồn tại nhưng tài liệu ở nhóm quyền khác.
4. Rate limit, HMAC, SLA, phí — nằm trong "Service Scope Technical Appendix" (Google Drive riêng).
5. Thời gian xét duyệt hồ sơ đăng ký.

## Quy trình đăng ký (đã đọc form, CHƯA nộp)

`resigstration-form.md` → submit `/api/api-onboarding`, 4 phần: (1) thông tin khách hàng/tài
khoản, (2) **chọn scope API** — 7 mục tick riêng gồm Auth/Trading-underlying/Trading-derivative/
Account-info/Market-data/WebSocket/Sandbox, (3) thông tin kỹ thuật (whitelist IP, stack, ngày
go-live dự kiến), (4) 5 cam kết bắt buộc. Cần thông tin công ty/tài khoản thật + IP whitelist —
**KHÔNG tự nộp form thay user**, cần user cung cấp IP + xác nhận thông tin tài khoản.

## Điểm khớp với kiến trúc hiện có

`trading_bot/brokers.py::BrokerBase` (place_order/cancel_order/get_positions/get_quote/
poll_orders) đã đủ tổng quát để cắm 1 broker mới — không cần đổi kiến trúc, chỉ cần viết
`PHSFlashBroker` (hoặc client wrapper mới `phs_flash_api.py` kiểu song song `dnse_api.py`) implement
đúng interface này. `Quote`/`OrderUpdate`/`qget()` cũng tái dùng được nguyên vẹn.

## Nguồn

- Docs: `https://phuhungsecurities.mintlify.app/*.md` (39 trang, index `llms.txt`).
- Probe thật: curl trực tiếp sandbox `flashapi.phs.vn/sandbox/oapi/*`, 2026-08-20, demo creds
  công khai trong docs.

## ĐÃ BUILD ADAPTER — phase 1 (2026-08-20, job Taylor_20260820_075059, commit `0a875d1c`)

`phs_flash_api.py` (PHSFlashClient) + `trading_bot/brokers.py::PHSFlashBroker`
(`BROKER_CLASSES["phs_flash"]`) + `secrets/phs_flash_credentials.json.sample`.
Selfcheck `phs_flash_api_selfcheck.py`: **96 assertion PASS thật trên sandbox** (chỉ ĐỌC,
không đặt lệnh), PASS lại dưới `env -u TZ` / `TZ=UTC` / `TZ=America/New_York`; 13 selfcheck
phụ thuộc `trading_bot/brokers.py` đều PASS. **VẪN CHƯA GO-LIVE** (hồ sơ đăng ký chưa nộp).

### 3 đính chính cho chính tài liệu PHS (đo thật, không suy đoán)

1. **"Fixture OTP token" của sandbox là SAI.** `trading-underlying.md` bảo sandbox nhận
   `552066a35eb30a9815afc952b14287a8` cho `x-otp-token`. Gửi đúng chuỗi đó → **401**
   `Invalid x-otp-token (use otp_token from the matching auth response)`; gửi `otp_token`
   của chính lần login → 200. ⇒ sandbox và production cùng một cơ chế, adapter không cần
   nhánh riêng.
2. **Bảng mã trạng thái lệnh cơ sở trong prompt dispatch (Mike) MÂU THUẪN với tài liệu.**
   Hai trang chính thức (`ref-order-status-codes.md` §10.2 và `api-reference/error-status.md`)
   trùng khớp nhau: `0`=Rejected by exchange, `1`=Open, `2`=Sent, **`3`=Cancelled**,
   `4`=Matched, `5`=Expired, `8`=Pending send, `12`=Fully matched. Prompt ghi `3`=Khớp hết,
   `5`=Hủy hết, `8`=Chờ cancel — map theo prompt là **báo KHỚP cho một lệnh đã HUỶ**. Bằng
   chứng độc lập nghiêng về tài liệu: bản ghi sandbox `dailyOrder` có `orstatuscode="8"` kèm
   `status="Chờ gửi"` / `orstatus="Sending pending"` = Pending send. Adapter theo TÀI LIỆU.
3. **Sandbox BỎ QUA `symbolList`** — `priceboard/symbol-latest-data` luôn trả đúng 1 fixture
   ACB, kể cả khi hỏi `FPT` hay mã không tồn tại (`ZZZ`). ⇒ khả năng hỏi NHIỀU MÃ một lần
   **chưa verify được**, phải đo lại ở production. Hệ quả thiết kế: broker lấy đúng dòng khớp
   mã, KHÔNG lấy `rows[0]` — không khớp thì trả `None` (lấy nhầm dòng = gán giá mã KHÁC cho
   lệnh, sai im lặng).

### 3 chốt FAIL-CLOSED đã cài (cố ý không đoán)

| Chốt | Vì sao |
|---|---|
| Đặt/hủy lệnh **phái sinh** → `raise` | Body chưa xác nhận với PHS; phase 1 chỉ đọc `derivative/balance` + `openPositions` |
| `get_cash()` ở **production** → `raise` | `buyingPower` bắt buộc symbol+quotePrice; field tiền của `/underlying/assets` chưa probe được (sandbox 404) ⇒ dùng `get_buying_power(symbol, price)`, không đọc bừa field nghe giống tiền (coding_guidelines §25) |
| Lệnh không có `price` → `raise` | `limitPrice` là trường bắt buộc kể cả với ATO/ATC/MP, nhưng giá trị hợp lệ cho lệnh thị trường chưa được PHS xác nhận |

`get_cash()` = `ppse` (sức mua an toàn) — thuộc vế **"tiêu được ngay"** của §25, **KHÔNG**
phải cơ sở NAV. Consumer tính NAV/mẫu số tỷ trọng không được dùng.

### Còn treo, phải làm trước khi go-live
- Verify trên production: `underlying/buyingPower`, `underlying/assets` (tên field tiền),
  tên query khi hủy lệnh (tài liệu tự mâu thuẫn `timetype` vs `timeType` — adapter theo ví
  dụ cURL `timeType`), batching nhiều mã ở priceboard.
- Bid/ask **lô chẵn**: `symbol-latest-data` chỉ có 3 mức lô LẺ (`bbOd`/`boOd`) ⇒ adapter cố ý
  KHÔNG dựng `l2_snapshot` (dựng từ lô lẻ là bịa thanh khoản). Cần endpoint L2 khác.
- Body đặt lệnh phái sinh; OTP thật ở production; rate limit/SLA.
