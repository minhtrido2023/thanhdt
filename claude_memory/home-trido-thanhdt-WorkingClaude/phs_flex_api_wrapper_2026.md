---
name: phs-flex-api-wrapper-2026
description: "Wrapper PHS Open API FLEX (REST + streaming socket.io v2) — phs_flex_api.py, đã kết nối tài khoản thật [REDACTED]12"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5517a2be-d1db-46af-922f-e134464226d1
---

**phs_flex_api.py** (workdir root) — wrapper Open API FLEX của chứng khoán PHS (`https://fgateway.phs.vn`), xây [REDACTED]12 từ 2 tài liệu PDF→md trong Downloads (đặc tả REST v0.1 + streaming).

- `FlexClient` (REST): `login()` (OAuth password, client_id/secret mặc định trong doc), `verify_smart_otp()`, `place_order/modify_order/cancel_order` (cần header x-otp-token), inquiry: `sub_accounts/cash_balance/account_summary/portfolio/buying_power/daily_orders/order_history/instruments`. Tự unwrap `{"s":"ok","d":...}`, tự refresh token + retry 401. Token cache `data/phs_flex_token.json` (hạn 8h).
- `FlexStream` (websocket): room `instrument:`/`trade:`/`account:` (account cần access_token); tự resubscribe khi reconnect. ⚠️ Server chạy **socket.io v2** → bắt buộc `python-socketio 4.6.1 + python-engineio 3.14.2` (đã cài, KHÔNG upgrade lên 5.x).
- Credentials: `data/phs_credentials.json` (user đã điền) hoặc env `PHS_USERNAME/PHS_PASSWORD`. Test script: `phs_connect_test.py` (chỉ API đọc; `--stream` test room account).
- **Đã verify tài khoản thật [REDACTED]12**: TK [REDACTED] (ĐINH THỊ KIM LIÊN), 2 tiểu khoản — margin `0101002896` (NAV ~27.4 tỷ, CK 62.45 tỷ, nợ margin 35 tỷ, RTT 81%, DGC 1.01M cp là vị thế lớn nhất) + thường `0101002895` (4.1M cash; BSA/HWS/NTC).
- **ĐẶT LỆNH [REDACTED]12 = BLOCKED chờ PHS**: Smart OTP verify OK nhưng place_order trả `-700003 Could not find sub account type` trên CẢ 2 tiểu khoản. Đã loại trừ format (accountId tiểu khoản đúng — custodycd báo FO20010; side=buy đúng — NB báo -10006; type=LO trong command list — 'limit' báo -900056; timetype required). KẾT LUẬN (user xác nhận): cặp client_id/secret mặc định trong tài liệu ([REDACTED]) chỉ có quyền inquiry+market data; **đặt lệnh cần client_id/client_secret PHS cấp riêng từng khách** — user đã liên hệ PHS [REDACTED]12, chờ cấp. Khi có: điền vào data/phs_credentials.json (đã có sẵn 2 field), XÓA data/phs_flex_token.json (token cũ gắn client cũ), dùng `FlexClient.from_credentials_file()` rồi test lại vòng đặt→hủy (mua 100 TTA giá sàn trên TK thường).
- Bug đã vá: server trả lỗi `{"s":"500"}` (không phải "error") — _parse giờ raise với mọi s != "ok".
- Datafeed `instruments` không cần đăng nhập; streaming instrument/trade cũng không.
