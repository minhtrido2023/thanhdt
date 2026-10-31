---
kind: script-output
status: CANONICAL
source: data/dcf_lens_history.csv
group: trading-bot
note: fresh (mtime 2026-08-28) — append-only log, KHÔNG phải nguồn cron; đăng ký 2026-08-28 sau khi phát hiện chưa có entry (job Taylor_20260828_081256)
writer: trading_bot/strategies.py::log_dcf_history() — gọi từ đường REPORT (send_plan_report / eod_trading_report / dc_book_waterfall_paper), KHÔNG từ V23Strategy
---

# data/dcf_lens_history.csv

**Status: CANONICAL (append-only log, ghi mỗi lần report tính DCF)**

## Là gì
Tích luỹ `fair_value_ps` DCF dự báo + giá thị trường tại thời điểm tính, mỗi lần MỘT REPORT chạy
`dcf_check` (user directive 2026-07-15). Mục đích: sau này đối chiếu với giá thật T+1M/3M/6M để
đánh giá lăng kính DCF có hữu ích không. Thuần là bước GHI DỮ LIỆU — không phân tích/quyết định.

## Ai ghi / cadence
`trading_bot/strategies.py::log_dcf_history()` — append mỗi lần `send_plan_report` /
`eod_trading_report` / `dc_book_waterfall_paper` tính `dcf_check` cho 1 ticker, **KHÔNG** phải cron
riêng và **KHÔNG** phải `dcf_refresh_gate.py` (script đó chỉ gate discount-rate hàng tháng ngày 11,
ghi vào `data/dcf_refresh_state.json`/`data/dcf_refresh_gate.log` — hai file này KHÁC file, đừng
nhầm 2 luồng). Fail-safe: mọi lỗi ghi bị nuốt im lặng (log warning), report không hỏng vì dòng này.

## Bẫy

- **CUTOVER KHUNG DCF 2026-10-30 12:48 ICT (`logged_at` < mốc này = `legacy`; ≥ mốc = `domestic_v2`).** CSV KHÔNG có cột frame ⇒ chuỗi lịch sử TRỘN hai khung: trước mốc r = lãi huy động (tới ~13,9%) + ERP 6,5%, g_T cap = lãi huy động; sau mốc r = 12,25% hằng, g_T cap 5,5%. FV trung vị đổi ~−1,4%, thứ hạng gần như không đổi (tương quan ≥0,9999) nhưng mức MoS tuyệt đối không so thẳng được qua mốc. Khi phân tích chuỗi, cắt tại mốc hoặc tính lại bằng `DCF_RATE_FRAME=legacy`.
- **NGUỒN SỐ CP DCF (`OSHARES_SOURCE_DEFAULT` trong `dcf_valuation.py`) — CUTOVER-MARKER: ĐÃ BẬT, CUTOVER 2026-10-31 15:2x ICT (logged_at < mốc = fin; ≥ mốc = live)**
  (R10, job `Taylor_20261031_064246`, 31/10/2026). Mọi dòng tới nay tính FV/cp bằng `fin` (OShares dòng quý
  cuối). CSV KHÔNG có cột nguồn số CP ⇒ ngày bật `live` (đổi 1 từ, cần user duyệt) PHẢI sửa dòng này thành
  `CUTOVER <YYYY-MM-DD HH:MM ICT> (logged_at < mốc = fin; ≥ mốc = live)` trong CÙNG commit bật.
  **Deploy:** `dcf_valuation.py` + `oshares_dcf.py` (+ `trading_bot/strategies.py`) cùng lúc ở repo ngoài và
  `bin/lag_dd_pack.py` (cổng DCF_RICH 2 số CP) ở mike — merge HAI repo trước, bật knob sau. **Rollback:**
  đổi `OSHARES_SOURCE_DEFAULT` về `"fin"` (1 từ) — fin trùng byte bản trước knob (R10: 4.784/4.784, 3 asof).
  Sau mốc: mã có thưởng/cổ tức-CP mà số quý chưa theo có FV/cp THẤP hơn trước mốc (đo R9/R10 2026-10-29:
  PHR/HTN/AIG CHEAP→RICH nhẹ); live < số quý luôn về số quý (R10 `LIVE_BELOW_FIN`) ⇒ không mã nào có FV/cp
  CAO hơn fin quá ~0,5% (dung sai làm tròn) vì nguồn số CP. Không phải mô hình đổi ý. Chi tiết: `kb/projects/oshares-live-dcf-20261030.md`.
- KHÔNG có consumer đọc lại file này trong pipeline sản xuất — hiện tại thuần là log tích luỹ chờ
  phân tích sau; đừng coi việc file không được ai `read_csv` là dấu hiệu file chết.
- Không refresh/tái tạo được — mỗi dòng gắn với 1 lần tính DCF thật tại đúng thời điểm đó
  (`logged_at`, `as_of`); xoá/ghi đè sẽ mất lịch sử không phục hồi được.
