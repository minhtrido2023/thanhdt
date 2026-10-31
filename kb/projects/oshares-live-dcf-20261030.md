# oshares_live cho DCF (`DCF_OSHARES_SOURCE`) — knob TẮT, CHƯA bật live

**CUTOVER-MARKER: CHƯA BẬT** — `OSHARES_SOURCE_DEFAULT = "fin"` trong `dcf_valuation.py`. Ngày bật
(đổi 1 từ → `"live"`, cần user duyệt + quant-skeptic) ghi mốc ICT vào đây VÀ vào
`kb/data_registry/trading-bot/dcf_lens_history.md` trong CÙNG commit bật.

## Đã có
- Vòng 1 (job `Taylor_20261030_094435`, merge WC `cc257bc01` / mike `925c936fd`): `oshares_dcf.py`
  (`oshares_for` = chính sách `oshares_pit`; `classify_oshares_gap` lọc OShares DIV/ISS), knob env.
- Vòng R2-R7 (job `Taylor_20261030_155013`, nhánh WC `session/oshares-r2r7-20261030`, mike
  `session/oshares-r2r7-ops-20261030`, CHƯA merge): bằng chứng ở
  `agents/Taylor/research/oshares_live_r2r7_20261030/SELFCHECK.md`.
  - R2 nguồn sự thật = hằng `OSHARES_SOURCE_DEFAULT` (env chỉ override; giá trị lạ ⇒ `fin` + kêu);
    `ops_health_check.sh` mục 17 (khối `CHECKDCFOS`) WARN khi cron/launcher/wc_env.sh gán biến.
  - R3 `dcf_backtest.py`, `dcf_rate_robustness.py`, `dcf_fv_sens_cache.py` gọi
    `pin_oshares_source_fin()` (ghi cache không hậu tố nguồn).
  - R4 bỏ nhánh promote ISS `announced` (rỗng ở 1.557/1.557 hàng đo).
  - R5 khoá khung ex-date giá↔số CP (`dcf_valuation._live_oshares`): không khoá được ⇒ `fin` + kêu.

- Vòng R2-R7 đã MERGE 31/10 (WC `c2c817139`, mike `153d7ec24` + INDEX `97bbf64ec`).
- Vòng R8 (job `Taylor_20261031_025427`, CHƯA merge): WC nhánh `session/oshares-r8-20261031`
  (worktree `/home/trido/wt-oshares-r8-20261031`), mike `session/oshares-r8-ops-20261031`. Bằng chứng:
  `agents/Taylor/research/oshares_live_r8_20261031/SELFCHECK.md`.

## Điều kiện TRƯỚC khi bật live
Đã đóng ở R8 (trên nhánh, chờ arch-review + quant-skeptic + merge):
1. ~~Caller khai `price_date`~~ (H4). `_dcf_check_for_order(..., price_date=None)`; khai ở
   `lag_dd_pack.run_valuation` (phiên `Price` qua `dd._ref_price_session`), trục DCF của
   `due_diligence` (row.time khi tự đọc `Price`; `ctx["price_date"]` khi caller truyền giá),
   `custom_basket.dcf_at` (`price_date=d`), `dcf_valuation.dcf_check` khi tự đọc giá. Rơi về `Close`
   (đã điều chỉnh ngược) ⇒ KHÔNG khai. **CỐ Ý không khai** (không xác định được phiên của giá ⇒ live = số quý):
   `send_plan_report.sh` / `eod_trading_report.sh` (`ref_price` của plan — nguồn tuỳ người lập plan),
   `converge_report` (giá caller), `dc_book_waterfall_paper` (giá state, paper).
2. ~~Khoá R5 lọt ca ex đúng asof~~ (H1). Hợp đồng `price_date` = phiên giá THUỘC VỀ (docstring
   `fair_value`). Khoá thêm lịch: ISS dời khung giá (`PRICE_ADJUSTING_ISS` + ISS không ghi phương thức)
   ex trong [price_date, asof], đọc `pricing_events` (gồm `announced` ⇒ bắt được một phần trễ vendor) ⇒
   số quý + kêu; cả price_date > asof và lỗi đọc lịch ⇒ số quý.
3. ~~ERROR im lặng~~ (H2): `oshares_for` ERROR/raise ⇒ số quý + kêu stderr 1 lần/tiến trình/mã.
4. ~~Probe selfcheck nạp code PROD~~ (H3): `dcf_valuation.py:64` chèn WORKDIR canonical lên đầu
   `sys.path`; probe ghim lại cây đang test + kiểm đường dẫn module (C4/C6/C12, mutant M22).
5. ~~Launcher ngoài cây~~ (H6): mục 17 quét thêm systemd user (+drop-in, environment.d), ccdb `.env`,
   settings Claude, shell profile, `/proc/*/environ` đọc được. 31/10: 0 lần gán (11 file + 18 tiến trình).
   Hạn chế: /proc của user khác không đọc được; launcher ngoài các gốc này không quét.

Còn lại:
- arch-review + quant-skeptic gói R8, merge 2 nhánh, rồi user duyệt bật (đổi 1 từ + cutover-marker).
- Vendor trễ lật `announced→executed` mà KHÔNG có dòng ISS nào (kể cả announced) ⇒ khoá không thấy;
  `fin` cùng lỗi.
- Mất mát đã biết của khoá lịch: phiên ex đúng ngày giá luôn về số quý (BSR 2025-10-29 ex 10-29 là ca
  đổi số ĐÚNG bị bỏ). Bảo thủ có chủ đích.
- quant-skeptic mục 4 (MST 2025-10-29 ×0,7359: số quý 113,6tr vs AIS 83,6tr) CHƯA kết luận — bật live
  làm MST MẤT cờ DCF_RICH sâu của `lag_dd_pack` ở asof đó.

## Ảnh hưởng nếu bật live (R8, đo qua caller thật, `out_impact_r8_*.csv`)
- Lời gọi không khai price_date (plan approval / EOD): 0 thay đổi ở 4 asof (toàn bộ FRAME_FALLBACK).
- `lag_dd_pack` / DD / `dcf_at` (khai phiên giá): lật CHEAP→RICH = PHR, HTN, AIG (2026-10-29), REE
  (2026-07-29), GAS (2024-10-29) — cả 5 khớp đúng số CP thật trong `corporate_action` (H5); RICH đều
  NHẸ ⇒ chỉ là WARNING, KHÔNG thêm cờ DCF_RICH. Cờ DCF_RICH sâu mất: MST (2025-10-29). Chạy sáng T+1
  (giá phiên T): HHV 2025-10-30 robust False→True (số quý 547tr chứa trước đợt quyền mua ex 12-25 ⇒
  `fin` nhìn trộm tương lai, live đúng).
- `custom_basket.dcf_at` chỉ chạy khi `BASKET_DCF_MODE` bật — production không đặt (grep crontab/bin).

## Rollback
Đổi `OSHARES_SOURCE_DEFAULT` về `"fin"` (1 từ). Mặc định `fin` trùng byte bản trước knob
(774 kết quả `fair_value`, 0 khác `repr`, asof 2026-10-29 + 2025-10-29).

## Script nghiên cứu đọc DCF (R3, grep 30/10)
Ép fin: 3 file trên. Không sửa (đóng băng, kết quả đã ghim; chạy trước knob ⇒ fin, hoặc tự đặt nguồn tường minh): mọi
`agents/Taylor/research/*` + `agents/Taylor/exp_capit*` gọi `fair_value`. `custom_basket.py` (+ bản sao
`data/fscore_c30v_20260801/custom_basket_fsx.py`) truyền giá không `price_date` ⇒ R5 ép `fin` khi live.
Không cron mới; không đổi lịch.
