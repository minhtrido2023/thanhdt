# Vòng plan Chủ nhật mùa BCTC (2026-10-19, Taylor_20261018_173105)

**Vấn đề:** re-rate 8L chạy mỗi ngày trong cửa sổ BCTC, chuỗi plan chỉ T2-T6 ⇒ BCTC công bố T7/CN không vào plan thứ Hai.
**Giải pháp:** `bin/sunday_plan_round.sh` (+ `_lib.py`, `_selfcheck.sh`) — chạy MỘT lần CN 19:00 ICT, KHÔNG sửa chuỗi T2-T6
(dùng env opt-in `MIKE_MORNING_RUN=1 MIKE_MORNING_FORCE=1` đã có trong `bq_freshness_check.sh`).

## Quyết định (a)/(b)/(c) mỗi account
- (a) tập lệnh (ticker, side, qty, loại, giá/trần làm tròn bước giá) giống thứ Sáu → khôi phục NGUYÊN file thứ Sáu (giữ duyệt).
- (b) khác → giữ plan mới, gỡ `approv*`/`mafee*`, `requires_user_approval=true`, tự gọi `send_plan_report.sh --account` (CN không có cron 21:00), post diff.
- (c) job fail/timeout/plan hỏng/không đổi byte/freshness fail/injector fail → khôi phục thứ Sáu + bus `error` + notify lý do thật.
- Kill giữa chừng: manifest `state/sunday_plan_round/<ngày đích>/manifest.json` phase=running → lần sau (hoặc trap TERM/INT/EXIT) khôi phục từ stash.

## Cổng cuối tuần đã phát hiện
1. **`data/macro_health.json` (BLOCK thật):** `macro_state_live.get_gated_state(max_health_age_min=1440)` fail-closed về DT4_only khi file >24h; file do `daily_refresh_v34b_linux.sh` [11c] ghi T2-T6 ⇒ CN 19:00 đã ~48h. Wrapper chạy lại `macro_healthcheck.py` (tự đo độ tươi 4 nguồn, không nới ngưỡng).
2. `expected_session.py --morning`: CN → phiên=thứ Sáu, đích=thứ Hai; rào 08:30 chỉ áp khi đích=hôm nay ⇒ không vướng.
3. DollarBill prompt ghi `data/plan_<ACCT>_<ngày>.json` nhưng loader/bot đọc `data/trade_plans/…` (có file lạc `data/plan_ZaloPay_2026-10-14.json`). Wrapper chỉ nhìn `data/trade_plans/`; plan viết sai chỗ ⇒ (c) "file không đổi byte".
4. `plan_position_drift_check.py`: CN trả SKIP (không phải phiên) — chỉ cờ, không chặn; vị thế đổi do corp-action credit CN không được kiểm.
Chưa kiểm được (không chạy thật): `publish_gated_state` frozen-state guard ngày CN, giá DNSE cuối tuần trong `compute_active_nav`, hành vi dedupe ledger của `discretionary_accumulation_inject` khi chèn lại lần 2 cùng plan_date.
