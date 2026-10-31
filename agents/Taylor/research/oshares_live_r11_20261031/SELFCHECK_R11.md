# oshares_live R11: áp live cho các caller còn ở `fin` (job Taylor_20261031_082449, 31/10/2026)

Nhánh (CHƯA merge, knob `OSHARES_SOURCE_DEFAULT` giữ nguyên `"live"` như main, không đặt lệnh):
- WC `session/oshares-r11-20261031` (worktree `/home/trido/wt-oshares-r11-20261031`, gốc main `8fcfa8b95`):
  `dcf_valuation.py` +83/−8, `oshares_dcf_selfcheck.py` +131/−0, `dc_book_waterfall_paper.py` +8/−1,
  `trading_bot/strategies.py` +4/−2 (chỉ docstring).
- mike `session/oshares-r11-ops-20261031` (worktree `/home/trido/wt-oshares-r11-ops-20261031`, gốc master `1649d105d`):
  `bin/send_plan_report.sh` +17/−1, `bin/eod_trading_report.sh` +14/−1, `kb/projects/oshares-live-dcf-20261030.md`, thư mục này.
(`git diff --numstat` trước commit.) Interpreter `/home/trido/thanhdt/wc_venv/bin/python`.

## Thiết kế: khớp giá với phiên (`dcf_valuation.price_session_for` / `price_sessions_for`)
Caller có giá nhưng không biết giá thuộc phiên nào (ref_price của plan = DNSE, `Close` cache) ⇒ tìm trong
**5 phiên cache gần nhất ≤ asof** phiên có `Price` (CHƯA điều chỉnh) **trùng** giá (|chênh| ≤ 0,5 VND), lấy
phiên mới nhất. Khớp ở phiên s ⇒ `price_date = s`. Không khớp / giá hỏng / lỗi đọc ⇒ `PRICE_SESSION_UNKNOWN`
(về số quý). Bước khớp chỉ đọc parquet local, 0 truy vấn BQ.

**Vì sao không nhìn trước (chứng minh, không phải ước lượng):** `fair_value` chỉ phụ thuộc CON SỐ giá. Khi
X == Price(s) với s ≤ asof thì `fair_value(t, asof, price=X, price_date=s)` là **đúng lời gọi** mà caller tự đọc
`Price(s)` thực hiện (`lag_dd_pack.run_valuation`, `dcf_check` tự đọc giá, `due_diligence`) — hợp đồng đó đã
qua review R8–R10. X thật ra lấy ở đâu (DNSE, phiên khác) không đổi được kết quả. Chỉ xét phiên ≤ asof
(C21 + M47); khớp phiên cũ hơn chỉ làm khung khoá `[price_date, asof]` rộng hơn, tức là chặt hơn.

**Không chứng minh được ⇒ không làm:** khai thẳng `price_date = signal_date` của plan (ref_price ghi bằng chữ tự
do, 13/144 lệnh mua có `ref_price_source`; giá cũ hơn signal_date sẽ lọt ex ở giữa) — KHÔNG làm.

## (1) Kiểm kê caller (grep `fair_value|dcf_check|dcf_line|_dcf_check_for_order|format_dcf_check`, trừ research/archive/worktree)
| Caller | file:line (nhánh) | Giá | Trước R11 | Sau R11 |
|---|---|---|---|---|
| plan echo | `mike/bin/send_plan_report.sh:1086` | `ref_price` (DNSE, của phiên signal_date) | không khai ⇒ số quý + kêu | `price_sessions_for` ⇒ khai phiên khớp / UNKNOWN (im) |
| EOD | `mike/bin/eod_trading_report.sh:507` | `ref_price` của plan, asof=plan_date | không khai | như trên |
| paper DC-book | `dc_book_waterfall_paper.py:759` | `last_close` của state = `Close` cache phiên mới nhất | không khai | như trên |
| converge_report | `converge_report.py:207` → `dcf_line(price=)` | `Close` cache | `dcf_check` với giá truyền vào ⇒ None | `dcf_check` tự khớp (`dcf_valuation.py:926`) khi live |
| alphalens_report | `alphalens_report.py:181` → `dcf_line(price=)` | `Close` cache | như trên | như trên |
| CLI `dcf_valuation.py` | `dcf_valuation.py:1025` | tự đọc / `--price` | tự đọc `latest_price` (không phiên) | `latest_price_session` / khớp `--price` |
| sector_lens_monitor | `sector_lens_monitor.py:514` → `dcf_line` không giá | tự đọc `Price` | ĐÃ khai (R8) | giữ |
| lag_dd_pack | `mike/bin/lag_dd_pack.py:251` | `_ref_price_session` | ĐÃ khai (R8) | giữ |
| due_diligence | `trading_bot/due_diligence.py:1041-1048` | tự đọc Price / `ctx["price_date"]` | ĐÃ khai (R8) | giữ; plan echo gọi với `skip_dcf=True` ⇒ không chạy DCF |
| custom_basket `dcf_at` | `custom_basket.py:882,906` | Price phiên d | ép fin (`pin_oshares_source_fin`, R9) | **GIỮ fin**: output basket không có hậu tố nguồn số CP (§8) |
| dcf_backtest / dcf_rate_robustness / dcf_fv_sens_cache | `:32/:32/:27` | không giá | ép fin (R3) | **GIỮ fin** (cache/kết quả không có hậu tố nguồn số CP) |
| `data/fscore_c30v_20260801/custom_basket_fsx.py`, `agents/Taylor/research/*`, `exp_capit*` | — | — | đóng băng | không sửa; giá không phiên ⇒ số quý + KÊU (đúng: chưa kiểm) |
| `dcf_earning_power.py:158` | — | `fv_experimental` (không gọi `fair_value`) | — | ngoài phạm vi |
`alt_valuation_lens`, `discretionary_accumulation`, `plan.py`, `sector_valuation_lens`, `apply_cash_redesign` chỉ
import/nhắc tên, không gọi các hàm trên (grep).

## (3) Tiếng ồn stderr
- `price_date=PRICE_SESSION_UNKNOWN` (caller ĐÃ kiểm, không khớp ⇒ về số quý là HỢP LỆ) ⇒ `logging.info` 1 lần
  /(mã, asof), **không stderr** (`_info_once`).
- `price_date=None` (caller CHƯA kiểm: script đóng băng, research, caller mới) ⇒ **giữ kêu stderr** 1 lần/tiến trình.
- Các fallback khác (sự kiện ISS, số CP lệch, lỗi đọc lịch, LIVE_BELOW_FIN, chuỗi Price lặp) giữ kêu.
- Chưa nới lại `dcf_rate_frame_selfcheck` (b0): probe của nó gọi `fair_value` với giá mà không khai ⇒ vẫn kêu
  (đúng phân loại "chưa kiểm"); b0 tiếp tục bỏ qua dòng `DCF_OSHARES_SOURCE`. Không đổi.

## (4) Tác động (`measure_impact_r11.py` → `impact_r11_summary.json`, `out_impact_r11_plans.csv`; paper `paper_impact.txt`)
Replay theo khung cache khi job chạy thật (cache sync 23:45): plan echo 21:00 ngày T−1 chỉ thấy phiên < signal_date;
EOD 19:10 ngày T thấy phiên < plan_date. 279 lệnh MUA (plan_date ≥ 2026-09-01, SpaceX 8 · ZaloPay 9 · paper main 262).

| | khớp phiên | dòng DCF hiển thị đổi | đổi MoS | đổi nhãn | đổi robust | cờ DCF_RICH sâu mất/thêm | không khớp: byte-identical |
|---|---|---|---|---|---|---|---|
| EOD | 277/279 | 26 (đều FPT, paper main) | 26 | 0 | 10 | 0/0 | 2/2 |
| plan echo | 57/279 (0/17 SpaceX+ZaloPay) | 4 (FPT) | 4 | 0 | 0 | 0/0 | 222/222 |
Khác trong dict mà dòng hiển thị giữ nguyên: 64 (EOD) + 12 (plan echo) ⇒ chỉ khoá metadata `oshares_method`
(FRAME_FALLBACK → AIS_EXACT…), VNM/FPT/HT1/MCH.

- **FPT là ca đúng của live:** thưởng CP ex 2026-09-21 (`fpt_corp_action.txt`, BQ `corporate_action`), số quý 2026Q2
  1.714,3tr vs live 1.885,7tr (+10,0%, AIS_EXACT, `probe_fpt.py`). Giá sau ex chia số CP trước thưởng ⇒ `fin` thổi MoS
  (vd 2026-09-23: +14,2% robust → live +5,6% không robust). Cùng lớp với PHR.
- **SpaceX/ZaloPay: 0 dòng hiển thị đổi** (15/17 lệnh EOD khớp; HT1/MCH/SCL/VPB/VPI giữ nguyên nhãn và MoS).
- **Paper DC-book hiện tại (asof 2026-10-30, 7 mã):** 7/7 khớp phiên; 0 dòng đổi (FPT nay số quý 2026Q3 đã cập
  nhật số CP; 6 mã còn lại NOT_COMPUTED tài chính/FCFE âm).
- **fin byte-identical** (`byte_identical_r11.py`, env `DCF_OSHARES_SOURCE=fin`, main `8fcfa8b95` TZ=UTC vs nhánh
  TZ=Asia/Ho_Chi_Minh): **2.322/2.322** (`dcf_check(price=Close)`, `_dcf_check_for_order(+price_date)`, `dcf_check` tự
  đọc; 774 mỗi loại; asof 2026-10-29 336, 2025-10-29 438), `diff_repr 0`.

**HẠN CHẾ CHÍNH — plan echo ≠ EOD:** lúc 21:00 cache chưa có phiên signal_date (sync 23:45) nên ref_price
(DNSE đóng cửa T−1) hiếm khi khớp ⇒ plan echo của SpaceX/ZaloPay vẫn là số quý; EOD hôm sau khớp ⇒ live.
Đo được 22 cặp (plan, mã) dòng plan echo ≠ dòng EOD, đều FPT ở paper main. Ở ca có sự kiện CP, số user DUYỆT
(21:00) có thể khác số EOD. Muốn plan echo live cần nguồn `Price` phiên T−1 trước 21:00 (BQ `tav2_bq.ticker` ingest
~17:2x, hoặc DNSE) — R11 KHÔNG làm vì đưa BQ lại vào đường 21:00 (R9 mục 8) và cần cổng freshness §6; để user quyết.
**[ĐÍNH CHÍNH R12, arch-review R11]** câu trên ngụ ý đường 21:00 của R11 vẫn 0 BQ — SAI: khi có mã khớp (57/279
lệnh replay), `price_sessions_for` gọi `oshares_dcf.prime` ⇒ truy vấn BQ ngay trên đường 21:00. R12 gỡ hẳn khớp phiên
khỏi plan echo (khai `PRICE_SESSION_UNKNOWN` có chủ đích; đo 0 lời gọi BQ / 279 lệnh) — `../oshares_live_r12_20261031/SELFCHECK_R12.md`.

Chi phí vận hành: khi có mã khớp, `price_sessions_for` gọi `oshares_dcf.prime` MỘT lô cho các mã đó (C21) thay vì
~4–5 truy vấn BQ/mã. EOD 19:10 nay có truy vấn BQ (trước: 0). Prime lỗi ⇒ oshares_dcf kêu stderr, từng mã tự hỏi
lại / về số quý (fail-closed, không chặn report — khối DCF nằm trong try).

## (5) Selfcheck
`oshares_dcf_selfcheck.py` (WT, `DCF_OS_OPS_HEALTH`/`DCF_OS_LAG_DD_PACK` trỏ worktree mike):
| Chạy | Kết quả | Log |
|---|---|---|
| TZ=UTC | 0 FAIL (168 PASS), **50/50** mutant KILLED, rc=0 | `run_selfcheck_UTC.txt` |
| env -u TZ | 0 FAIL (168 PASS), 50/50 KILLED, rc=0 | `run_selfcheck_noTZ.txt` |
| TZ=Asia/Ho_Chi_Minh | 0 FAIL (168 PASS), 50/50 KILLED, rc=0 | `run_selfcheck_ICT.txt` |
Mới: C21 (15 check): khớp phiên gần nhất ≤ asof; giá lệch/hỏng ⇒ UNKNOWN; giá chỉ có ở phiên > asof ⇒ UNKNOWN;
chỉ khớp phiên cũ hơn 5 ⇒ UNKNOWN; `dcf_check(price=)` chuyển phiên (live) / None (fin); UNKNOWN ⇒ số quý,
0 BQ, không stderr, có logging.info; None vẫn kêu; `price_sessions_for` prime 1 lần chỉ mã khớp, không prime ở fin;
3 caller (plan echo/EOD/paper) nối helper; đường merge lệch ⇒ None.
Mutant mới: M47 bỏ chặn asof · M48 dung sai 1e9 · M49 không giới hạn số phiên · M50 UNKNOWN kêu stderr ·
M51 None im · M52 dcf_check bỏ khớp — 6/6 KILLED.
Heredoc Python của 2 script mike: `ast.parse` OK; `bash -n` OK. **Không chạy end-to-end** `send_plan_report.sh`/
`eod_trading_report.sh` (kể cả `--dry-run`: `signal_holds.py --enforce` sửa file plan thật) — bằng chứng chức năng
là replay ở (4) gọi đúng hai hàm caller dùng.

Selfcheck rộng (`run_dcf_selfchecks.sh`, `sc_*`):
| Script | WT UTC | WT noTZ | PROD UTC | Kết luận |
|---|---|---|---|---|
| dcf_rate_frame / dcf_check / dcf_refresh_gate / dcf_earning_power / tz_asof_ict_dd_dcf / due_diligence / basket_oshares_step_exdate / basket_price_basis_audit / basket_price_basis / basket_return_leg_oshares | 0 | 0 | 0 | PASS |
| dcf_selector | 1 | 1 | 1 | CÓ SẴN trên PROD (`39/40 samples match production exactly`), không do R11 |
| test_trading_bot | 1 | 1 | 0 | MÔI TRƯỜNG, cùng chữ ký R9/R10 (`gap_adaptive_enabled`, stub `secrets/` worktree) |
| custom_basket_forensic_failclosed | 1 | 1 | 0 | MÔI TRƯỜNG, cùng chữ ký R9/R10 |
| test_multi_strategy | 1 | 1 | 1 | CÓ SẴN trên PROD |
`lag_dd_gate_selfcheck.py` (WC_ROOT=WT): TỔNG PASS, 52/52 mutant, rc=0 ở TZ=UTC và env -u TZ.
`ops_health_check_selfcheck.py`: toàn bộ assertion PASS, rc=0 (worktree mike + PROD).
`strategies.py` chỉ đổi docstring SAU lượt selfcheck rộng (không đổi hành vi).

## Còn lại
- Plan echo 21:00 vẫn số quý cho tài khoản thật (cache trễ) — cần user quyết nguồn Price T−1 (xem hạn chế chính).
- Ngưỡng 5 phiên / 0,5 VND chọn tay; khớp trùng số với phiên khác vẫn cho kết quả hợp lệ (cùng lời gọi), chỉ
  là "giá của phiên s".
- converge/alphalens khi khớp sẽ truy vấn BQ theo từng mã (không prime) — report nghiên cứu, chấp nhận.
- Đường tiền (plan echo / EOD / paper) ⇒ cần arch-review (opus high) + quant-skeptic trước merge.
