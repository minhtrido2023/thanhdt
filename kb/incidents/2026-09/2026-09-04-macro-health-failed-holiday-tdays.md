# 2026-09-04 — `macro_health=FAILED` (SEV1) giả: `tdays()` của macro_healthcheck.py không trừ nghỉ lễ VN ⇒ DT5G rơi về DT4_only cả đêm

**Phát hiện:** `ops_health_check.sh --account ZaloPay` (01:20Z) báo `macro_health=FAILED (SEV1)
— DT5G chạy DT4_only`. Dispatch tới Winston qua `ops_autofix` (job `Winston_20260904_012008`).

## Đây là báo động THẬT của một FAILED GIẢ

`data/macro_health.json` ghi lúc 2026-09-03T18:37:36 (step [14] của `daily_refresh_v34b_linux.sh`):

```
local_v34b_state_csv  as_of=2026-08-28 age=4td (max 3)  ok=false
bq_ticker_vnindex     as_of=2026-08-28 age=4td (max 3)  ok=false
status=FAILED sev=SEV1 recommended_state_source=DT4_only
```

Nhưng dữ liệu KHÔNG thiếu phiên nào: nghỉ Quốc khánh 2026 đóng cửa 31/08+01/09+02/09
(`trading_bot.vn_market._VARIABLE_HOLIDAYS`), nên **28/08 chính là phiên hoàn chỉnh gần nhất**
tại thời điểm 18:37 ngày 03/09 (BQ ingest ~17:2x của chính 03/09 chưa vào bản cache mà
`simulate_holistic_nav.bq` đọc — cache sync 23:45). Tuổi thật = **1 phiên**.

**Nguyên nhân:** `macro_healthcheck.py::tdays()` dùng `np.busday_count` trần — docstring cũ tự
khai *"holidays ignored = slightly conservative"*. 28/08 → 03/09 có 4 ngày Mon-Fri (31/08, 01/09,
02/09, 03/09) ⇒ `age=4 > STATE_MAX_TDAYS=TICKER_MAX_TDAYS=3` ⇒ FAILED. Vì `get_gated_state()`
fail CLOSED khi macro_health không tươi/không tin được, DT5G bị tắt và hệ chạy DT4 từ 18:37
03/09 tới 08:23 04/09. Hôm đó `state == state_dt4 == 3` (NEUTRAL) nên **không có thiệt hại thực
tế** — nhưng nếu macro cap đang ACTIVE thì đây là mất lớp bảo hiểm.

## Call-site thứ BA của cùng một lớp lỗi

| Ngày | File | Cách đo sai | Commit vá |
|---|---|---|---|
| 2026-09-03 | `bin/preflight_check.sh` (BQ ticker_prune) | lag theo NGÀY LỊCH, hardcode 1 ngoại lệ thứ Hai | `0b83f507` |
| 2026-09-03 | `bin/preflight_check.sh` (tuổi file macro_health) | ngưỡng giờ theo ngày lịch | `81cc0428` |
| 2026-09-04 | `macro_healthcheck.py::tdays()` | `np.busday_count` không trừ lễ | `96ebd124` |

Hai bản vá trước nằm trong `mike/bin/`, bản này nằm ở repo NGOÀI (`WorkingClaude/`) — nên grep
theo file cũ không chạm tới. **Bài học: khi vá một cách-đo-tuổi-dữ-liệu, quét CẢ HAI repo** cho
mọi nơi đếm ngày/phiên mà không đi qua `vn_market.is_holiday`.

## Bản vá (`96ebd124`)

- `tdays(asof, ref, vn_holidays=False)` — khi `vn_holidays=True` trừ ngày lễ VN qua
  `trading_bot.vn_market.is_holiday` (cùng nguồn `preflight_check.sh`/`bq_freshness_check.sh`).
- `add_source(..., kind="trading_vn")` cho 2 nguồn theo lịch HOSE + `missed_runs`.
  **`data/us_market_history.csv` CỐ Ý giữ `kind="trading"` (Mon-Fri)** — trừ lễ VN ở đó chỉ NỚI
  ngưỡng và che được một feed Mỹ chết thật.
- Không import được `vn_market` → quay về đếm Mon-Fri (chặt hơn, fail-safe) VÀ in kèm lỗi thật
  vào `detail` của source (§29 — không đoán nguyên nhân).

**Verify:** chạy thật `$DNA_PYEXE macro_healthcheck.py` → `STATUS = HEALTHY`, `USE STATE SOURCE:
DT5G_macro`, cả 2 nguồn VN `age=1td`. Harness 7 ca `tdays`: ca hỏng thật 28/08→03/09 VN = **1**
(cũ 4) · lịch Mỹ cùng khoảng vẫn = 4 · cuối tuần = 1 · cùng ngày = 0 · tương lai = 0 · stale
thật 20/08→03/09 = **7** (nhánh báo động thật không bị làm cùn).

## Việc phát sinh, chưa xử lý trong job này

- `universe_pit` **KHÔNG có trong BQ local cache** (`data/bq_cache/` chỉ có `universe_pit_q`) ⇒
  breadth-decoupling guard (§4 DT5G) báo `inactive → US pillar ungated (fail-safe)` mỗi lần
  `macro_healthcheck` chạy qua cache. Fail-safe đúng chiều (không chặn cap) nhưng guard đang
  KHÔNG hoạt động trên đường đọc cache — cần bổ sung bảng vào `sync_bq_cache_daily.sh` hoặc
  buộc đường này đọc live BQ. Chưa sửa: chạm cấu hình sync + logic DT5G, ngoài phạm vi autofix.
- `deposit_rate_vn` 46 ngày chưa refresh **không phải sự cố pipeline**: cron ngày 3 hàng tháng
  chạy đúng cả 03/08 lẫn 03/09, và cả hai lần đều **escalate đúng thiết kế** (nguồn mâu thuẫn
  thật về VCB/VietinBank: 6,8% theo cụm VCCorp vs 5,9% theo 24hMoney/topi). Bus question
  `Winston/deposit-rate-refresh-question` đang treo, **chờ user phân xử** — không được tự ghi số.
