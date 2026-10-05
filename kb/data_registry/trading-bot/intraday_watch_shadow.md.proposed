---
kind: local-dir
status: SHADOW (chưa có consumer production)
source: "data/intraday_watch/ (gitignored) — state_<ngày>.json, shadow_<ngày>.jsonl, verdicts/<ngày>_<MÃ>.json, no_rebuy_shadow.json, watchlist.json (tay, tuỳ chọn)"
group: trading-bot
role: cổng giá trong phiên + điều tra + cutloss 4 chế độ — CHẾ ĐỘ SHADOW (chỉ ghi lệnh dự định)
writer: mike/bin/intraday_price_watch.py (cron mỗi phút 09:00-14:59 + 08:30 ICT T2-T6, ĐỀ XUẤT — chưa cài, dòng ở kb/cron_registry.md.proposed); verdicts/ do Taylor ghi qua `intraday_price_watch.py verdict`
reader: chính nó; đánh giá sau 5 phiên shadow (người/Taylor đọc shadow_*.jsonl)
---

# data/intraday_watch/ — log shadow cổng giá trong phiên

Đặc tả: `kb/projects/discretionary-8l-candidate-funnel-plan-20261006.md` (Q1 + 4 chế độ, user duyệt
01:12/01:54 ICT 06/10). Job dựng: Taylor_20261005_185546.

- `state_<ngày>.json` — ca theo mã (T0, trigger, holdings, phán quyết, quyết định, execution/ TK). Ghi
  nguyên tử. Ca chưa xong (không phải DONE/HOLD/NO_POSITION) tự carry sang phiên kế.
- `shadow_<ngày>.jsonl` — mọi sự kiện: SCAN/TRIGGER/DISPATCH/VERDICT/USER_REPLY/DEFAULT_APPLIED/
  CUTLOSS_TICK (snapshot giá + sổ lệnh + intents + events). Nguồn để chấm 5 phiên shadow.
- `no_rebuy_shadow.json` — sổ cấm mua lại 10 phiên. **CHƯA có consumer** (plan T+1 không đọc).
- `state_<ngày>.json` còn chứa `outbox` (hộp thư đi bền — tin chưa gửi xong mang sang lượt/phiên
  sau), `stats` (đếm cho tóm tắt 14:50), `market_wide`, `health_alerts`, `dispatch_halted`.
- `crash_<init|crash>_<ngày>.flag` — cờ "đã báo lỗi cấp cao nhất hôm nay" (1 lần/ngày).
- `restricted.json` (TAY, tuỳ chọn) `{"tickers": [...]}` — mã đang hạn chế giao dịch ⇒ chỉ báo +
  điều tra, KHÔNG tự bán (chưa có field DNSE nào đã xác minh cho trạng thái hạn chế).
- Phán quyết có `source`: `agent` | `timeout` (đã dispatch, hết giờ) | `no_dispatch` (dispatch hỏng /
  bị trần / dừng) — chỉ `agent` mới áp bảng mặc định GÃY/CHƯA RÕ/NHIỄU; còn lại ⇒ GIỮ + cảnh báo.

## Bẫy
- `sold`/`avg` trong state là **MÔ PHỎNG** (mô hình khớp giả định: lệnh chờ ăn 30% KL mới, hàng đợi
  sàn ăn 10% KL tại sàn) — KHÔNG phải khớp thật, KHÔNG được đưa vào báo cáo NAV/P&L (§6, §27).
- Giá same-day từ DNSE (ReadOnlyDNSE), KHÔNG ghi vào `dnse_raw_*.jsonl`.
- Trên HOSE (biên 7%), giảm −5% đã cách sàn ≤2% ⇒ mọi kích hoạt HOSE vào chế độ RÚT GỌN (10'/15') và
  chế độ bán ≥2 ngay — đó là hệ quả của ngưỡng đã duyệt, không phải lỗi dữ liệu. Log
  `ALT_THRESHOLD` ghi song song ngưỡng tương đối theo biên độ (HOSE −3%, HNX −4,5%, UPCOM −7%, idio
  −3%) — CHỈ để so, không hành động.
- Lệnh trả lời trong shadow PHẢI có tiền tố `SHADOW` — "BÁN PNJ" trần bị BỎ QUA (để phiên Mike sống
  trong Trading Daily không nhầm thành lệnh thật và ngược lại).
