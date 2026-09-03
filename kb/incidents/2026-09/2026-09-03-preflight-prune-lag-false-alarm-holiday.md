# 2026-09-03 — Preflight cảnh báo giả "BQ ticker_prune lag=6d" vì ngưỡng đếm NGÀY LỊCH, không biết lịch nghỉ lễ

**What happened.** `ops_health_check`/`preflight_check.sh` 08:20 ICT (ZaloPay) WARN:
`BQ ticker_prune: lag=6d — giá ref_price trong plan có thể cũ`. Không có phiên nào bị thiếu.

**Bằng chứng (3 nguồn độc lập).**
1. BQ live: `MAX(time)` = **2026-08-28** trên CẢ 3 bảng (`ticker`, `ticker_prune`, `ticker_1m`),
   depth ngày đó **214 mã** (bình thường 208–214 tuần trước) ⇒ không phải corruption/moi ruột
   (khác hẳn sự cố 2026-07-15).
2. `trading_bot/vn_market.py::_VARIABLE_HOLIDAYS` khai **2026-08-31 + 2026-09-01** (nghỉ bù Quốc
   khánh theo thông báo DNSE email 25/08/2026), cộng `02-09` đã có trong `_FIXED_HOLIDAYS`
   ⇒ **28/08 (T6) chính là phiên giao dịch gần nhất**.
3. Broker DNSE: `marketPrice` mọi mã trong `data/execution_logs/dnse_raw_*.jsonl` **giống hệt
   nhau** từ 08-28 đến 09-03; số lần poll 08-28 = 60 (ngày giao dịch) vs 12/12/16 cho
   08-31/09-01/09-02 (nhịp ngày nghỉ). Không có phiên nào diễn ra mà BQ bỏ sót.

**Root cause.** `preflight_check.sh` đo lag bằng **ngày lịch** với đúng một ngoại lệ hardcode cho
thứ Hai (`_max_prune_lag=2; [ "$DOW_ICT" = "1" ] && _max_prune_lag=3`). Bất kỳ kỳ nghỉ lễ dài nào
cũng làm nó WARN oan — trong khi `bq_freshness_check.sh` đã dùng `trading_bot.vn_market.is_holiday`
từ trước cho đúng bài toán này. Hai checker cùng hỏi "dữ liệu có thiếu phiên không" nhưng chỉ một
cái biết lịch nghỉ.

**Fix** (`mike/bin/preflight_check.sh`): so `MAX(time)` của ngày hoàn chỉnh gần nhất với **phiên
giao dịch gần nhất** tính qua `is_holiday` (cùng nguồn `bq_freshness_check.sh` dùng), thay cho
ngưỡng ngày lịch. Cửa sổ SQL nới 14→21 ngày để kỳ nghỉ Tết không làm `MAX()` rỗng. Có nhánh
fallback về ngưỡng cũ khi không import được `vn_market`, và **in kèm lỗi thật đọc được**
(§29 — không đoán nguyên nhân). Ngưỡng depth `<200 mã` giữ nguyên, không đụng.

**Verify.** Preflight chạy thật cả 2 account → `✅ BQ ticker_prune: 2026-08-28 = phiên gần nhất,
214 mã ✓`. Harness chạy **verbatim** khối rẽ nhánh (sed lines 251–270) với 5 ca:
fresh / stale-thật / thin-depth / fallback-ok / fallback-stale → cả 5 ra đúng nhánh. `bash -n` +
`shellcheck -S warning` sạch.

**Lesson.** Checker "dữ liệu có mới không" phải đo bằng **phiên giao dịch**, không phải ngày lịch;
ngoại lệ hardcode cho thứ Hai chỉ vá được cuối tuần, không vá được ngày lễ. Đã có sẵn
`trading_bot.vn_market.is_holiday` — dùng lại, đừng dựng ngưỡng xấp xỉ mới.
