---
name: Auto-run simulation with email profile
description: Khi user nói "chạy simulation", tự động dùng profile email từ config.json với order_point weights, không hỏi lại setup
type: feedback
originSessionId: afd1283e-9ed8-4ec5-8a51-488c813fe806
---
Khi user nói "chạy simulation" (hoặc tương tự), tự động submit simulation với toàn bộ thiết lập từ profile `email` trong `config.json` — không cần hỏi lại cấu hình.

**Why:** User đã xác nhận đây là thiết lập chuẩn. Chỉ cần user cho biết giai đoạn thời gian (Init date range) là chạy ngay.

**How to apply:**
- Profile: `email` trong `config.json`
- `combine_type`: `order_point`
- `combine_weight`: `{"w_1":14,"w_2":12,"w_3":13,"w_4":2,"w_5":12,"w_6":8,"w_7":4,"w_8":0,"w_9":11,"w_10":2,"w_11":5,"w_12":0,"w_13":0,"w_14":0,"w_15":10,"w_16":0}`
- `cutloss`: 0.15
- `initial_amount`: 50000000000
- `ratio_deal`: 0.1
- `enable_market_eval`: true
- `dict_filter`: đọc từ `config.json` → key `email` → field `filter` (parse JSON string), sau đó **thay `Init`** bằng date range user yêu cầu
- Nếu user không nói giai đoạn → hỏi giai đoạn nào cần chạy
- Poll status đến khi `completed` rồi lấy result và trình bày kết quả
