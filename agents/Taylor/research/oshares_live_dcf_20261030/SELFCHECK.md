# oshares_live cho dcf_valuation + quy tắc lọc OShares DIV/ISS — job Taylor_20261030_094435

Nhánh: outer `session/oshares-live-20261030` (worktree `/home/trido/wt-oshares-live-20261030`),
mike `session/oshares-live-ops-20261030` (worktree `WorkingClaude/wt-oshares-live-ops-20261030`). CHƯA merge.
Mọi số dưới đây đo trong phiên 30/10; file nguồn ghi cạnh từng mục.

## 0. Sửa tiền đề của dispatch: TCB KHÔNG đi qua DCF
`fair_value` loại BANK/INSURANCE/SECURITIES (`is_financial`) TRƯỚC khi đọc OShares ⇒ FV của TCB không đổi
ở cả hai nguồn (NOT_COMPUTED). Phần TCB làm được: `oshares_dcf.oshares_for("TCB", "2026-10-30")` =
**10.629.360.621** (= 7.086.240.414 × 1,5, ISS_ESTIMATE) ⇒ nếu DCF tính được thì FV/cp nhân **0,6667**.
Nguồn: `run_impact_stdout.txt` (khối `== TCB`).
Vì sao `oshares_live` nguyên bản KHÔNG thấy TCB: ISS 50% ex 2026-10-29 vẫn `event_status="announced"`,
`issue_volumn=0` (BQ 30/10 16:5x ICT), mà `oshares_live._fetch` chỉ đọc `executed`. NED y hệt (ISS 14% ex 10-29).

## 1. Call-site cùng lớp (giá × OShares / FV/cp chia OShares)
| Call-site | Loại | Bị knob ảnh hưởng? |
|---|---|---|
| `trading_bot/strategies.py:56` `_dcf_check_for_order` → `fair_value(tk, asof, price)` | ĐƯỜNG TIỀN (dcf_check trên lệnh BUY, cờ RICH sâu) | CÓ (khi bật `live`) |
| `mike/bin/lag_dd_pack.py:247` → `_dcf_check_for_order` | ĐƯỜNG TIỀN (DD pack LAG, cờ `_rich_deep`) | CÓ (gián tiếp) |
| `custom_basket.py:900` `dcf_at` → `fair_value(tk, d, price=px)` | ĐƯỜNG TIỀN (custom30V selector, chỉ khi DCF gate ON) | CÓ |
| `custom_basket.py` trọng số `Price × OShares` (mcapw) | ĐƯỜNG TIỀN — cùng lớp nhưng KHÔNG qua fair_value | KHÔNG (đã có cơ chế ex-date riêng, `oshares_weight_exdate_20260927`) |
| `rating_8l.py:442` `_reconcile_oshares` → `oshares_reconciled` | ĐƯỜNG TIỀN (burn-in, trung tính có chủ đích) | KHÔNG |
| `mike/bin/lag_dd_pack.py:195` cờ lớp A đọc chuỗi OShares | ĐƯỜNG TIỀN (pha loãng, không nhân giá) | KHÔNG |
| `dcf_backtest.py:139`, `dcf_fv_sens_cache.py:44` (`price=None`) | NGHIÊN CỨU | CÓ nếu env bật |
| `erp_domestic_20261030/erp_domestic.py:26` `mcap = Price*OShares` (E/P tổng hợp) | NGHIÊN CỨU (đã ghim) | KHÔNG — TCB thiếu ~33% trọng số ở asof 10-29; không sửa kết quả đã ghim |
| `dcf_rich_outlook*/build_panel.py` (truyền `oshares=` tường minh) | NGHIÊN CỨU | KHÔNG (caller tự cấp oshares) |
`custom30_yield_labels.py`: không đọc OShares (grep 0 hit) — ngoài lớp này.
Danh sách tìm bằng `grep -rlnE "\bfair_value\s*\("` + `grep -rlnE "OShares"` (bỏ `wt-*`, `archive`).

## 2. Cài đặt (outer)
- `oshares_dcf.py` (mới): `oshares_for` = chính sách `oshares_pit.oshares_pit` (PIT, ưu tiên oshares_live,
  rơi về số quý, cổng ×SANITY_FACTOR) + ISS cổ tức-CP/thưởng `announced` đã ex đưa vào `_cache`
  (`exright<=asof`, `public_date<=asof`, ex trong 45 ngày; quyền mua KHÔNG nhận). `oshares_live.py` KHÔNG sửa.
- `dcf_valuation.py` (+18 dòng): `DCF_OSHARES_SOURCE` ∈ {`fin` MẶC ĐỊNH, `live`}; giá trị lạ ⇒ `fin` + shout.
  `live` chỉ chạy khi caller không truyền `oshares=` VÀ có OShares quý > 0 (không đổi độ phủ).
  Không chạm RATE_FRAME_DEFAULT / r / g_T.
- Hạn chế đã biết: chế độ `live` trong `_dcf_check_for_order` thêm 3 truy vấn BQ/lệnh (chưa prime); lỗi ⇒ số quý.

## 3. Mặc định = byte-identical
`byte_identical.py` canonical vs nhánh, env trống, universe_pit có giá tại 2026-10-29 + 2025-10-29:
**774 kết quả fair_value, 0 khác `repr`** (`run_byte_identical_stdout.txt`).

## 4. Ảnh hưởng `fin → live` trên universe_pit (`run_impact_stdout.txt`, `out_impact_<asof>.csv`)
| asof | DCF ok | FV đổi | >1% | >5% | lật status | đổi robust |
|---|---|---|---|---|---|---|
| 2026-10-29 | 145 | 9 | 7 | 6 | 3 (PHR, HTN, AIG: CHEAP→RICH) | 1 (HTN) |
| 2026-07-29 | 157 | 13 | 11 | 9 | 1 (REE CHEAP→RICH) | 0 |
| 2025-10-29 | 184 | 7 | 6 | 4 | 1 (BSR CHEAP→RICH) | 1 (BSR) |
| 2024-10-29 | 149 | 4 | 2 | 1 | 1 (GAS CHEAP→RICH) | 0 |
2026-10-29, 6 mã >5% đối chiếu `corporate_action`: PHR thưởng 80% ex 09-11 (FV×0,5556), HTN thưởng 50%
ex 09-10 (×0,6667), AIG thưởng 15% ex 08-04, TDP CP 10% ex 09-17, FPT thưởng 10% ex 09-21, DIG 6% — đều là
sự kiện CP thật mà OShares quý trong `data/bq_cache/ticker_financial.parquet` chưa theo.
Ngược chiều: DGW ×1,0092 (AIS 10-12 = 221.320.169 < quý 223.361.000; ESOP 2,2tr ex 08-26 không lăn vì
ex trước AIS) — giới hạn đã biết của `oshares_live`, lệch <1%. MST 2025-10-29 ×1,3588: quý 113,6tr vs AIS
83,6tr — PIT bỏ được số quý restated (look-ahead).
`ok_fin != ok_live`: 0 ở cả 4 asof (sau khi chặn nhánh live khi thiếu OShares quý — bản đầu cho KCB/ODE
NOT_COMPUTED→ok, đã bỏ).

## 5. Quy tắc lọc OShares mới (`classify_oshares_gap`, `oshares_gap_check`)
Kỳ vọng tỉ lệ OShares = Π(1+ratio) chỉ của ISS cổ tức-CP/thưởng trong cửa sổ (DIV không tạo CP; quyền mua
⇒ RIGHTS_PENDING; dedup theo (ex, code, phương thức, ratio)). Cùng dữ liệu quy tắc cũ
(`erp_domestic_v2_20261030/data/oshares_check.csv`, cửa sổ (06-30, 10-29], 581 mã): cờ cũ **30** → cờ mới
OSHARES_LAG **2 (TCB, NED)**; 30 cờ cũ = 26 CASH_DIV + 2 ISS_REFLECTED (HUB, KSV) + 2 LAG.
Nguồn: `run_reclassify_stdout.txt`, `out_reclassify_flags.csv`.

## 6. Selfcheck (theo phạm vi: dcf_valuation là lõi)
Lệnh chạy từ `/home/trido/wt-oshares-live-20261030/WorkingClaude`, mỗi lệnh ở `TZ=UTC` và `env -u TZ`:
- `oshares_dcf_selfcheck.py` — 34 check offline PASS (`env -u TZ`: `run_oshares_dcf_selfcheck_noTZ.txt`), 41 với `--bq` ở TZ=UTC (`run_oshares_dcf_selfcheck_bq_UTC.txt`); mutation 6/6 KILLED
  (M1 DIV coi như ISS, M2 quyền mua tạo CP, M3 bỏ dedup, M4 tol=0, M5 bỏ trần 45 ngày, M6 bỏ lọc public_date).
- `dcf_rate_frame_selfcheck.py`, `dcf_check_selfcheck.py`, `dcf_selector_selfcheck.py`,
  `dcf_refresh_gate_selfcheck.py`, `dcf_earning_power_test.py`, `tz_asof_ict_dd_dcf_selfcheck.py` — rc=0 cả 2 TZ
  (`run_dcf_selfchecks.txt`). Các file này import `dcf_valuation` của worktree (sys.path[0]=HERE).
- Phụ thuộc môi trường: BQ (C5 + đo ảnh hưởng), parquet canonical `data/bq_cache` (WORKDIR cứng trong dcf_valuation).

## 7. Lệnh merge (CHỈ sau arch-review + quant-skeptic + user duyệt)
```bash
git -C /home/trido/thanhdt merge --no-ff session/oshares-live-20261030
git -C /home/trido/thanhdt/WorkingClaude/mike merge --no-ff session/oshares-live-ops-20261030
# BẬT (quyết định riêng, sau merge): export DCF_OSHARES_SOURCE=live trong môi trường bot/report;
# rollback = bỏ biến (mặc định fin).
```
