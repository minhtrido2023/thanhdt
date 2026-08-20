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
- **404 "Cannot GET"** cho mọi biến thể path đã thử của "buying power"/"assets" cơ sở
  (`underlying/assets`, `underlying/buyingPower`, `assets/underlying`) và **derivative/assets**,
  **derivative/portfolio** — path thật KHÁC những gì tài liệu/agent suy ra, hoặc endpoint này cần
  tham số path khác (accountId không phải "022C099995"?). **CHƯA XÁC ĐỊNH ĐƯỢC PATH ĐÚNG** — việc
  còn treo, không đoán thêm.
- `GET /priceboard/all-stocks` (và 3 biến thể tên khác) → 404 tất cả — path thật của
  "get_all_stocks" CHƯA XÁC ĐỊNH.

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

1. Path chính xác của "buying power"/"assets" (cơ sở + phái sinh) và "all-stocks" — probe thật
   404 hết; gợi ý path production dùng `/eqt/` và `/fno/` thay vì `/underlying/`/`/derivative/`.
   **Cần xác nhận path đầy đủ cho assets/buying-power với tiểu khoản thật.**
2. Enum đầy đủ `type` lệnh (ATO/ATC/MP/GTC...) — sandbox chấp nhận bất kỳ giá trị nào nên không
   verify được bằng probe.
3. Cơ chế vay/margin ở tầng đặt lệnh CƠ SỞ — không thấy field tương đương `loan_package_id`
   (DNSE) trong body đặt lệnh; PHS có hỗ trợ đòn bẩy qua API này không, nếu có thì field nào.
4. `refresh_token` — trả về nhưng KHÔNG có endpoint refresh nào được tài liệu hoá; phải re-login
   mỗi 8h nếu đúng vậy.
5. OTP thật ở production: sandbox otp_token phát ngẫu nhiên NGAY trong login response, không có
   bước verify OTP tách rời lộ ra trong tài liệu — production có giống vậy không, hay cần 1 bước
   verify OTP qua SMS/Smart OTP như FLEX cũ (`verify_smart_otp`)? Nếu passive hoàn toàn thì khác
   hẳn mô hình DNSE (`--auto-otp` phải tự nhập OTP nhận qua email).
6. WebSocket/streaming real-time — toàn bộ market-data endpoint đã thấy là REST GET polling
   thuần, marketing text nói "real-time" nhưng chưa có bằng chứng push. Registration form CÓ 1
   mục "WebSocket streaming" riêng để xin cấp — gợi ý có tồn tại nhưng ở nhóm quyền/tài liệu khác
   chưa đọc.
7. Rate limit, HMAC/chữ ký request, SLA, phí — không công khai trên docs, PHS ghi rõ các mục này
   nằm trong "Service Scope Technical Appendix" dạng file rời (Google Drive), chưa mở được qua
   WebFetch.
8. ~~Tài khoản phái sinh có tách biệt số tài khoản với cơ sở không~~ — **ĐÃ XÁC NHẬN (PHS support
   2026-08-20)**: tách biệt, tiểu khoản eqt ≠ tiểu khoản fno, cả hai khác master account.
9. Thời gian xét duyệt hồ sơ đăng ký (không công khai số ngày cụ thể).

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
