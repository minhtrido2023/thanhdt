# oshares_live R10 (vòng cuối) — SELFCHECK (job Taylor_20261031_064246, 31/10/2026)

Nhánh (CHƯA merge, knob `OSHARES_SOURCE_DEFAULT` VẪN `"fin"`, không đặt lệnh):
- WC `session/oshares-r10-20261031` (worktree `/home/trido/wt-oshares-r10-20261031`, gốc main `336add4e7`):
  `dcf_valuation.py` +38/−0, `oshares_dcf_selfcheck.py` +192/−11, `trading_bot/strategies.py` +4/−0.
- mike `session/oshares-r10-ops-20261031` (worktree `/home/trido/wt-oshares-r10-ops-20261031`, gốc master `dc8007523`):
  `bin/lag_dd_pack.py` +24/−1, `bin/ops_health_check.sh` +15/−0, `bin/run_selfchecks.sh` +4/−1,
  `kb/data_registry/trading-bot/dcf_lens_history.md` +10/−6, `kb/projects/oshares-live-dcf-20261030.md` +24/−7,
  `SELFCHECK_R9.md` +1/−1, cộng thư mục này.
(`git diff --numstat` trước commit.) Interpreter `/home/trido/thanhdt/wc_venv/bin/python`.

## Từng việc
| # | Việc | Sửa | Check | Mutant (KILLED) | Kết quả |
|---|---|---|---|---|---|
| 1 | **KILLER R9**: live xoá cờ DCF_RICH sâu ⇒ CLEARED bỏ qua ack | `fair_value` (chỉ live) thêm `fair_value_ps_fin`/`margin_of_safety_fin` (cùng FCFE/r/g, chia số quý); `_dcf_check_for_order` chuyển `margin_of_safety_fin`; `lag_dd_pack._rich_deep_fin`: dict live ⇒ RICH sâu theo số quý (MoS < −100%) cũng là cờ `DCF_RICH`; live thiếu MoS số quý ⇒ cờ (fail-closed). Áp **mọi mức lệch**, không chỉ >10% (cổng không phụ thuộc ngưỡng hiển thị) | C19 (7 check) | M39 chỉ nhìn số live · M40 bỏ fail-closed · M41 "số quý" lấy nhầm MoS live | PASS |
| 2 | MST / ISS không theo tỷ lệ | `_live_oshares` (e): live < số quý × (1 − 0,5%) ⇒ số quý, method `LIVE_BELOW_FIN` + kêu stderr (mọi ca, kể cả không giá) ⇒ số CP luôn = số LỚN hơn (FV/cp thấp, bảo thủ) | C20 (6 check, gồm đầu-cuối MST → DCF_RICH vẫn cờ) | M42 tắt guard · M43 áp cả chiều live > quý · M44 dung sai 50% | PASS — xem đính chính MST |
| 3 | Cutover-marker | `dcf_lens_history.md` + `oshares-live-dcf-20261030.md`: "ĐÃ SẴN SÀNG, CHƯA BẬT", deploy 2 repo cùng lúc, rollback 1 từ | — | — | XONG |
| 4a | Trần `run_selfchecks.sh` | `oshares_dcf_selfcheck.py` 240 → 480s (đo 170s một mình, 230s khi 4 tiến trình song song) | `bash -n` | — | XONG |
| 4b | Harness mutant | KILLED = có FAIL MỚI so với baseline không-mutant (in baseline nếu có) | đã thấy hoạt động: trong lúc sửa, 1 FAIL sẵn (C20/C16) không làm mutant nào "chết" giả | — | PASS |
| 4c | Mục 17 settings JSON | quét chuỗi `command` trong `hooks` + `statusLine` bằng mẫu gán kiểu shell (không quét permissions) | C8/R10 (2 check) | M45 | PASS |
| 4d | Câu sai SELFCHECK_R9.md | đính chính: `basket_return_leg_oshares` nạp `custom_basket` PROD (log R9 có ghi) | — | — | XONG |
| 4e | Guard `_price_run_start` tắt im lặng | thiếu dòng Price phiên price_date / giá caller ≠ Price ⇒ kêu stderr 1 lần/(mã, price_date); hành vi khoá giữ nguyên | C16/R10 (2 check) | M46 | PASS |

## Đính chính MST (việc 2) — giả thuyết R8/R9 ngược chiều
Skeptic R8 mục 4 / R9: "live 83,6tr vs số quý 113,6tr ⇒ live có thể phóng đại FV/cp ~36%". Đo lại
(`mst_hhv_timeline.txt`, BQ `corporate_action`):
- Đợt riêng lẻ 30tr của MST: `record_date`/`exright_date` 2025-11-24, đổi niêm yết hiệu lực 31/12/2025, giao
  dịch 25/11/2026. Live: 83,6tr ở 2025-10-29 → 113,6tr từ 2025-11-30 (theo đúng ISS executed).
- Dòng quý 2025Q3 (công bố 2025-10-22) ghi 113,6tr — tức là số CP **sau** đợt phát hành tháng 11 ⇒ dòng
  `ticker_financial` bị vendor ghi đè về sau (không PIT). Ở 2025-10-29, **live đúng, số quý nhìn trước**.
- HHV cùng lớp: 2025Q3 (công bố 2025-10-30) = 547,2tr đã gồm quyền mua ex 2025-12-25; live 497,4tr = AIS đúng.

Vì vậy khi live < số quý thì có hai nguyên nhân NGƯỢC chiều: (A) live sót CP đã phát hành không theo tỷ lệ
(vendor ghi ngày trễ ⇒ live phóng đại FV) và (B) dòng quý ghi đè số CP về sau (live đúng). Ở thời gian thực
không phân biệt được ⇒ R10 chọn số CP lớn hơn (phía FV thấp, thêm RICH ⇒ cần ack người, không bao giờ lỏng
hơn fin). Đo lớp này (`measure_nonprorata.py` → `measure_nonprorata_out.txt`, `nonprorata_live_vs_fin.csv`):
342 sự kiện ISS không theo tỷ lệ executed từ 2023 (riêng lẻ 166 dòng, ESOP 211, chuyển đổi TP 22, đấu giá 11,
sáp nhập 6), asof ∈ {ex−1, ex+30, ex+180}: live < số quý >0,5% ở **29/1.004** lần đo, 29/29 method
`AIS_EXACT`; lớn nhất HHP −48%, CII −42%, MST −26%, NVL −25%, VPI −9%, HHV −9%. Hạn chế: không có nguồn
số CP PIT độc lập để chia 29 ca thành (A)/(B); ca có xác minh ngày (MST, HHV) đều là (B).

## Selfcheck `oshares_dcf_selfcheck.py` (cuối cùng, sau mọi sửa)
| Chạy | Kết quả | Log |
|---|---|---|
| TZ=UTC + `--bq` | 0 FAIL (160 PASS), **44/44** mutant KILLED, rc=0, 230s | `run_selfcheck_bq_UTC.txt` |
| env -u TZ | 0 FAIL (153 PASS), 44/44 KILLED, rc=0 | `run_selfcheck_noTZ.txt` |
| TZ=Asia/Ho_Chi_Minh | 0 FAIL (153 PASS), 44/44 KILLED, rc=0 | `run_selfcheck_ICT.txt` |
44 = 36 (R9) + M39-M46. `DCF_OS_OPS_HEALTH`/`DCF_OS_LAG_DD_PACK` trỏ worktree mike.
Sửa check cũ do hành vi R10 (không nới): C15 đo hiển thị lệch bằng chiều live > quý (×1,3591, +36%) vì
×0,7359 nay về số quý (C20 phủ); C19 ca MST tắt tạm guard việc 2 (`LIVE_BELOW_FIN_TOL=1.0`, khôi phục giá
trị lúc vào) để cô lập cổng việc 1.

`lag_dd_gate_selfcheck.py` (mike worktree): TỔNG PASS, 52/52 mutant killed, rc=0 ở TZ=UTC và env -u TZ
(`lag_dd_gate_selfcheck_UTC.txt`, `lag_dd_gate_selfcheck_noTZ.txt`).

## fin byte-identical (`byte_identical_r10.py`, `byte_compare_r10.py`, `run_byte_identical_stdout.txt`)
main PROD (`336add4e7`, `git diff --quiet` sạch trên file DCF), TZ=UTC vs nhánh (sau sửa cuối), TZ=Asia/Ho_Chi_Minh,
env trống: **4.784/4.784** (fv/chk/dcfc/ref mỗi loại 1.196; asof 2026-10-29 336, 2025-10-29 438,
2024-10-29 422) — `keys_equal True`, `diff_repr 0`.

## Impact khi bật live vs R9 (`measure_impact_r10.py`, `out_impact_r10_*.csv`, `compare_impact_r10_vs_r9.py` → `impact_r10_vs_r9.txt`)
So từng ô với `out_impact_r9_*.csv` (st/rb/mos/fv/osh × 5 chân): **16 ô khác / 38.925**, đúng 3 mã, tất cả do việc 2:
- MST 2025-10-29 (PD + PDM1): OShares 83,6tr → 113,6tr, FV 3.792 → 2.791, MoS −53% → −108% ⇒ **cờ DCF_RICH
  giữ như fin** (cổng: R9 50 → R10 51 mã ở PD; 49 → 50 ở PDM1; không mã nào mất cờ).
- HHV 2025-10-30 (PDM1): 497,4tr → 547,2tr, MoS +19,9% → +11,8%, robust True → False (R8 coi live đúng ở ca này —
  nay bảo thủ về số quý, chấp nhận theo quyết định việc 2).
- DGW 2026-10-29 (PD + PDM1): 221,3tr → 223,4tr (−0,9%), MoS −400% → −405% (đã RICH sâu, không đổi cờ).
Asof 2024-10-29 và 2026-07-29: 0 ô khác. Cổng DCF_RICH ở cả 4 asof: R10 ⊇ chân fin cùng giá (theo cấu trúc luật).
Các lật CHEAP→RICH nhẹ PHR/HTN/AIG/REE/GAS (live > quý) không đổi so với R9.
Impact chạy trước khi sửa câu chữ thông báo `LIVE_BELOW_FIN` (chỉ chuỗi stderr, không đổi số).

## Selfcheck rộng (strategies là lõi dùng chung ⇒ quét rộng; `run_dcf_selfchecks.sh`, `run_wt.py`, wc_venv)
| Script | WT UTC | WT noTZ | PROD UTC | Kết luận |
|---|---|---|---|---|
| dcf_rate_frame / dcf_check / dcf_selector / dcf_refresh_gate / dcf_earning_power / tz_asof_ict_dd_dcf / due_diligence / basket_oshares_step_exdate / basket_price_basis_audit / basket_price_basis / basket_return_leg_oshares | 0 | 0 | 0 | PASS |
| test_trading_bot | 1 | 1 | 0 | MÔI TRƯỜNG, cùng chữ ký R9 (`gap_adaptive_enabled` — stub `secrets/` của worktree) |
| custom_basket_forensic_failclosed | 1 | 1 | 0 | MÔI TRƯỜNG, cùng chữ ký R9 (`worktree LẠI có forensic_flags.csv`) |
| test_multi_strategy | 1 | 1 | 1 | CÓ SẴN trên PROD (DuckDB cache thiếu `VNINDEX_RSI_Max3M`) |
`[run_wt] modules ngoài WT: KHÔNG` ở mọi log WT **trừ** `basket_return_leg_oshares` (nạp `custom_basket` PROD —
R10 không sửa `custom_basket.py`).

## Còn lại / hạn chế
- Việc 2 là quyết định bảo thủ, không phải phân loại đúng/sai: ca (B) (MST/HHV lịch sử) bị đẩy về số quý dù
  live đúng. Chỉ đổi được nếu có nguồn số CP PIT độc lập.
- Dung sai 0,5% và các ngưỡng R9 (90 ngày, 20 phiên, 10%) vẫn là hằng chọn tay.
- `margin_of_safety_fin` chỉ có khi live; merge lệch (mike trước WC) ở live ⇒ cờ DCF_RICH fail-closed mọi mã live.
- Knob vẫn `fin`; bật = user duyệt + cutover-marker cùng commit.
