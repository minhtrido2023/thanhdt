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

## Điều kiện TRƯỚC khi bật live (chưa làm — cố ý)
1. **Caller phải khai `price_date`.** Hiện KHÔNG caller production nào truyền ⇒ nếu bật live hôm nay,
   mọi lời gọi có giá rơi về `fin` (kêu stderr 1 lần/tiến trình), chỉ lời gọi `price=None` đổi số.
   Cần sửa (đường tiền, cần review riêng): `trading_bot/strategies.py::_dcf_check_for_order`
   (gọi từ `mike/bin/lag_dd_pack.py:247` qua `dd._ref_price_for`, `trading_bot/due_diligence.py:1035`
   qua `ctx["price"]`/`row.Price`), `custom_basket.py::dcf_at` (Price phiên `d`).
2. Khoá R5 chỉ bắt lệch giữa ngày giá và asof; KHÔNG bắt vendor trễ lật `announced→executed`
   (TCB ISS ex 29/10: còn `announced` 30/10 16:5x ICT, đã `executed` khi chạy selfcheck BQ 30/10 tối).
   Lớp sai số này `fin` cũng mắc.
3. quant-skeptic phản biện gói R7 (Mike gọi) + user duyệt.

## Rollback
Đổi `OSHARES_SOURCE_DEFAULT` về `"fin"` (1 từ). Mặc định `fin` trùng byte bản trước knob
(774 kết quả `fair_value`, 0 khác `repr`, asof 2026-10-29 + 2025-10-29).

## Script nghiên cứu đọc DCF (R3, grep 30/10)
Ép fin: 3 file trên. Không sửa (đóng băng, kết quả đã ghim; chạy trước knob ⇒ fin, hoặc tự đặt nguồn tường minh): mọi
`agents/Taylor/research/*` + `agents/Taylor/exp_capit*` gọi `fair_value`. `custom_basket.py` (+ bản sao
`data/fscore_c30v_20260801/custom_basket_fsx.py`) truyền giá không `price_date` ⇒ R5 ép `fin` khi live.
Không cron mới; không đổi lịch.
