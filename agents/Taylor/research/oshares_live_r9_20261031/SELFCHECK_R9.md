# oshares_live R9 — SELFCHECK (job Taylor_20261031_042224, 31/10/2026)

Nhánh (CHƯA merge, knob `OSHARES_SOURCE_DEFAULT` VẪN `"fin"`, C6 kiểm):
- WC `session/oshares-r9-20261031` (worktree `/home/trido/wt-oshares-r9-20261031`, gốc `f442ed0b2`):
  `custom_basket.py` +4/−0, `dcf_valuation.py` +126/−31, `oshares_dcf.py` +27/−7,
  `oshares_dcf_selfcheck.py` +365/−8, `trading_bot/strategies.py` +23/−1 (`git diff --numstat` trước commit).
- mike `session/oshares-r9-ops-20261031` (worktree `/home/trido/wt-oshares-r9-ops-20261031`, gốc `640485297`):
  `bin/lag_dd_pack.py` +10/−0, `bin/ops_health_check.sh` +19/−1, KB + thư mục này.
Interpreter: `/home/trido/thanhdt/wc_venv/bin/python`.

## Từng việc
| # | Việc | Sửa | Check | Mutant (KILLED) | Kết quả |
|---|---|---|---|---|---|
| 1 | Khe H1: ISS announced ex TRƯỚC price_date | `oshares_dcf.unexecuted_events` (ISS dời khung giá ex ∈ [asof−90 ngày, asof], status ≠ `executed`) ⇒ `_live_oshares` FRAME_FALLBACK + kêu, MỌI ca (kể cả không giá); lỗi đọc ⇒ fallback | C13 (9 check) | M25 luôn rỗng · M26 lookback 0 · M27 tính cả executed · M28 nuốt lỗi | PASS |
| 2 | MST ×0,7359 phải hiện | `fair_value` thêm `oshares_divergence` + kêu stderr 1 lần/mã/asof khi \|lệch\| > `OSHARES_DIVERGENCE_WARN`=0,10; `_dcf_check_for_order` chuyển `oshares/oshares_fin/oshares_source/oshares_method/oshares_divergence` (CHỈ khi live); `format_dcf_check` nối `⚠ OShares live 83,6tr vs quy 113,6tr (-26%)`; `lag_dd_pack.soft_warnings` WARNING `OSHARES_LIVE_LECH` | C15 (8 check, gồm biên 10% vs 10,1% và fin không thêm khoá) | M30 ngưỡng 1000% · M31 format không in · M32 không kêu stderr | PASS |
| 3 | `oshares_for` gọi trước kiểm price_date | `_live_oshares`: có giá mà price_date None/hỏng/> asof ⇒ số quý NGAY, trước mọi `oshares_for` | C14 (3 check, đếm 0 lời gọi oshares_for/fetch_cache/pricing_events/_fetch) | M29 thứ tự R8 | PASS; đo thật bên dưới |
| 4 | custom_basket | **Chọn (a)**: `_dcfv.pin_oshares_source_fin(__file__)` ngay sau import trong nhánh `BASKET_DCF_MODE` | C17 | M33 bỏ pin | PASS |
| 5 | Vendor lặp Price cũ qua ex | `_price_run_start`: Price phiên price_date lặp lại các phiên trước (chữ ký ffill, cùng nguyên lý `close_repair._lift_neighbour`) ⇒ khung khoá mở về ĐẦU chuỗi; chuỗi > `PRICE_RUN_MAX`=20 phiên hoặc lỗi đọc ⇒ fallback | C16 (8 check, ca tổng hợp) | M34 bỏ guard · M35 bỏ trần · M36 nuốt lỗi đọc | PASS |
| 6 | H6 settings JSON + /proc research | `.json`: `json.load` + CHỈ khoá `env`; JSON hỏng ⇒ WARN "không đọc được". /proc: VẪN WARN, gắn `[research override]` khi comm `python*` và cmdline chứa `/research/`, `_selfcheck.py`, `/exp_`; khác ⇒ `[LAUNCHER]` | C8 +4 check | M37 JSON đọc như văn bản · M38 không gắn cờ | PASS |
| 7 | M22 equivalent trên canonical | `PIN` thành template theo cây; C18 dựng cây TẠM (symlink `*.py` + `trading_bot`) ≠ PROD rồi probe trên đó | C18 | M22 | PASS; canonical bên dưới |

Ca tổng hợp việc 5 (C16): ISS thưởng 50% ex 2026-10-28 (executed); Price 60.000 đứng từ 10-27 đến 10-29; caller
khai price_date=10-29, asof=10-30. Không guard: số CP 10-29 = 10-30 (cùng sau ex), [10-29, 10-30] không có ex ⇒
khoá OK SAI (giá trước ex × số CP sau ex). Có guard: khung mở về 10-27 ⇒ số CP 10-27 ≠ 10-30 ⇒ số quý + kêu
`Price 60000 lap lai tu 2026-10-27 den 2026-10-29`.

Quyết định việc 6: override nghiên cứu KHÔNG được hạ xuống OK — biến trong env tiến trình có thể rò sang tiến
trình con ghi output tên không hậu tố nguồn; cờ chỉ để người/autofix không coi là launcher production. Phân loại
theo cmdline là heuristic (không chứng minh được ý định).

Quyết định việc 4 (a) thay (b): output basket (CSV/registry) không mang hậu tố nguồn số CP (§8); (b) cần thêm
hậu tố vào mọi tên output + `prime()` toàn universe cho mọi rebal; nhánh chỉ chạy khi `BASKET_DCF_MODE` bật,
production không đặt (R8 grep crontab/bin; lần này `crontab -l | grep -c BASKET_DCF` = 0). Hệ quả: `pin` là
toàn tiến trình (cùng cơ chế R3). Bản sao `data/fscore_c30v_20260801/custom_basket_fsx.py` không sửa (đóng băng).

## Selfcheck `oshares_dcf_selfcheck.py`
| Chạy | Kết quả | Log |
|---|---|---|
| TZ=UTC + `--bq` | 0 FAIL, 36/36 mutant KILLED, rc=0 | `run_selfcheck_bq_UTC.txt` |
| env -u TZ | 0 FAIL, 36/36 KILLED, rc=0 | `run_selfcheck_noTZ.txt` |
| TZ=Asia/Ho_Chi_Minh | 0 FAIL, 36/36 KILLED, rc=0 | `run_selfcheck_ICT.txt` |
36 = M1-M4, M7-M38 (R8: 22; R9 thêm 14). `DCF_OS_OPS_HEALTH`/`DCF_OS_LAG_DD_PACK` trỏ worktree mike.

Sửa check cũ do hành vi R9 (không nới): C4 2 check stdout chuyển sang `price=None` (có giá không price_date giờ
không gọi `oshares_for` nên check cũ thành rỗng nghĩa); C7 "không đọc được lịch" cô lập `frame_events` bằng
`unexecuted_events=[]` (cả hai đọc cùng `pricing_events`; nếu không cô lập M17 sẽ sống); C4/C7/C10 nạp
fixture lịch rỗng để không chạm BQ.

### Việc 7 — M22 trên cây canonical (`m22_canonical_style.py`, `m22_canonical_style_out.txt`)
HERE = PROD (`/home/trido/thanhdt/WorkingClaude`, code main):
- PIN thật: check cũ (so với HERE) PASS · C18 PASS.
- M22 (`PIN=[""]`): check cũ **PASS** (= equivalent mutant, đúng khe dispatch nêu) · C18 **FAIL** (oshares_dcf,
  oshares_pit, oshares_live, corp_action_lib, trading_bot.strategies nạp từ PROD thay vì cây tạm) ⇒ KILLED.

## Việc 3 — đếm truy vấn BQ đường plan (`bq_calls_r9.py`, `bq_calls_r9_out.txt`)
live, `_dcf_check_for_order(tk, Price, 2026-10-29)` không price_date, KHÔNG prime, 10 mã
(FPT MST PHR HTN AIG REE GAS BSR HPG DGC), đếm `subprocess.run` của `bq` CLI (đường `corp_action_lib.bq`, timeout 300s):
main **9 lời gọi bq CLI / 9 oshares_for** → nhánh R9 **0 / 0**; status 10/10 trùng.

## fin byte-identical (`byte_identical_r9.py`, `byte_compare_r9.py`, `run_byte_identical_stdout.txt`)
main (PROD = `f442ed0b2`, `git diff --quiet` sạch) vs nhánh, env trống: 6.228 kết quả (fair_value / dcf_check
/ `_dcf_check_for_order` / ref, mỗi loại 1.557; 4 asof 2026-10-29 336, 2026-07-29 361, 2025-10-29 438,
2024-10-29 422) — `keys_equal True`, `diff_repr 0`. (Dispatch ghi "895/895"; số đo ở đây là 6.228/6.228.)

## Impact khi bật live (`measure_impact_r9.py`, `out_impact_r9_*.csv`, `impact_r9_summary.json`, `impact_r9_vs_r8.txt`)
So từng ô với `out_impact_r8_*.csv` (cột st/rb/mos/fv/osh, 5 chân FIN/NOPD/PD/FINM1/PDM1): **0 ô khác / 38.925**.
PHR/HTN/AIG (2026-10-29), REE (2026-07-29), GAS (2024-10-29), BSR, MST (2025-10-29) không đổi so với R8. Việc 1
không bắt ca nào ở 4 asof (`r9_unexecuted_fallback` rỗng), việc 5 không bắt ca nào (`r9_price_run_fallback`
rỗng), việc 3 không đổi số (chỉ bỏ lời gọi). Lệch > 10% nay HIỆN: 2026-10-29 PD AIG +15%, HTN +50%, PHR +80%;
2026-07-29 PD PSD +30%, PTB +25%, REE +15%; 2025-10-29 PD BKC +100%, ELC +10,1%, **MST −26,4%**.

## Selfcheck rộng (strategies/custom_basket là lõi dùng chung ⇒ quét rộng, `run_dcf_selfchecks.sh`, wc_venv)
| Script | WT UTC | WT noTZ | PROD UTC | Kết luận |
|---|---|---|---|---|
| dcf_rate_frame / dcf_check / dcf_selector / dcf_refresh_gate / dcf_earning_power / tz_asof_ict_dd_dcf / due_diligence / basket_oshares_step_exdate / basket_price_basis_audit / basket_price_basis / basket_return_leg_oshares | 0 | 0 | 0 | PASS |
| test_trading_bot | 1 | 1 | 0 | MÔI TRƯỜNG (stub `secrets/` của worktree, như R8). Config thật (symlink tạm, đã trả stub): rc=0 UTC + noTZ (`sc_wt_realcfg_*`) |
| custom_basket_forensic_failclosed | 1 | 1 | 0 | MÔI TRƯỜNG có sẵn (R8 §3): `data/forensic_flags.csv` được track ⇒ tiền đề test sai trên mọi worktree |
| test_multi_strategy | 1 | 1 | 1 | CÓ SẴN trên PROD: DuckDB cache thiếu `VNINDEX_RSI_Max3M` |
`[run_wt] modules ngoài WT: KHÔNG` ở mọi log WT.

## H6 trên máy thật (`h6_live_ops17_20261031.txt`)
Khối mục 17 nhánh R9 chạy trên HOME//proc thật: OK, 0 gán — 11 file ngoài cây + 28 tiến trình đọc được. Hiện
không file settings nào chứa chuỗi quyền `Bash(DCF_OSHARES_SOURCE=` (grep) — false-positive việc 6 là tiềm ẩn.

## Còn lại / hạn chế
- Việc 1 chỉ thấy sự kiện CÓ dòng ISS (kể cả announced); vendor không có dòng nào ⇒ vẫn lọt (như R8).
- Việc 5: Price lặp vì cổ phiếu thật sự đứng giá cũng mở khung (bảo thủ, có thể về số quý không cần thiết);
  giá caller khác Price phiên đó (DNSE) ⇒ guard không áp. Trần 20 phiên và 90 ngày lookback, ngưỡng 10% là
  hằng chọn tay, không hiệu chỉnh.
- MST 2025-10-29: nay hiện cảnh báo, kết luận đúng/sai số AIS vẫn mở (skeptic R8 mục 4).
