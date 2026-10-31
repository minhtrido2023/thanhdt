# oshares_live DCF — R2-R7 (job Taylor_20261030_155013). Knob GIỮ TẮT, CHƯA merge.

Nhánh: outer `session/oshares-r2r7-20261030` (worktree `/home/trido/wt-oshares-r2r7-20261030`), mike
`session/oshares-r2r7-ops-20261030` (worktree `WorkingClaude/wt-oshares-r2r7-ops-20261030`). Gốc: WC main
`cc257bc01`, mike master `44ca5076c`. Mọi số đo trong phiên 30/10 tối; file nguồn ghi cạnh.

## R2 — nguồn sự thật duy nhất
`dcf_valuation.py`: `OSHARES_SOURCE_DEFAULT = "fin"` + `_resolve_oshares_source` (mẫu `RATE_FRAME_DEFAULT`).
Env `DCF_OSHARES_SOURCE` chỉ override (khác default ⇒ kêu "OVERRIDE"); giá trị lạ ở env HOẶC ở hằng số ⇒
`fin` + `_shout` (stderr + logging), không raise. `ops_health_check.sh` mục 17, khối `CHECKDCFOS_BEGIN/END`:
WARN khi default lạ / env cron mang biến / crontab, wc_env.sh, `*.sh`, `*.py` (gốc WC, trading_bot, mike/bin)
gán biến; OK in nguồn đang chạy. Selfcheck C6 (9 check) + C8 (13 check, chạy khối thật bằng exec trên cây giả).

## R3 — script nghiên cứu/backtest
Liệt kê bằng `grep -rlnE "\bfair_value\s*\(|import dcf_valuation|from dcf_valuation import|_dcf_check_for_order\s*\(" --include=*.py`
(bỏ `wt-*`) + `grep -cE '\bfair_value\s*\('` từng file gốc WC:
| File | fair_value( | Xử lý |
|---|---|---|
| `dcf_backtest.py` | 1 (price=None, ghi cache parquet) | `D.pin_oshares_source_fin(__file__)` |
| `dcf_rate_robustness.py` | 1 (price=None, ghi cache) | idem |
| `dcf_fv_sens_cache.py` | 2 (price=None, ghi parquet) | idem |
| `custom_basket.py`, `data/fscore_c30v_20260801/custom_basket_fsx.py` | 4 | không sửa: truyền giá không `price_date` ⇒ R5 ép fin (đường selector production) |
| `alphalens_report.py`, `converge_report.py`, `dc_book_waterfall_paper.py`, `dcf_earning_power.py`, `sector_lens_monitor.py` | 0 | không gọi fair_value |
| `mike/agents/Taylor/research/**` + `exp_capit*` (21 file, find + grep -l) + `pending_adv3t_hard_gate_20260810/due_diligence.py` | — | đóng băng: chạy trước knob (⇒ fin) hoặc tự đặt `OSHARES_SOURCE` tường minh (`oshares_live_dcf_20261030/*`); không sửa kết quả ghim |
`pin_oshares_source_fin`: live ⇒ ép fin + kêu; đã fin ⇒ im. Selfcheck C9.

## R4 — BỎ nhánh promote `announced`
Bằng chứng: cột `ann_added` rỗng ở **1.557/1.557** hàng (`oshares_live_dcf_20261030/out_impact_{2024-10-29,
2025-10-29,2026-07-29,2026-10-29}.csv` = 422+438+361+336; lệnh pandas trong phiên). Hai ca nhắm tới: TCB = ngân
hàng (`fair_value` loại trước khi đọc số CP — 3 asof có TCB đều `financial-sector`), NED không có trong
universe đo ở 2026-10-29. Vendor đã tự lật: `--bq` 30/10 tối `oshares_for("TCB","2026-10-30")` = 10.629.360.621
ANCHOR_ONLY qua `oshares_live` (chỉ đọc `executed`). Đã gỡ `_fetch_announced`, `_clip`, `PROMOTE_MAX_AGE_DAYS`,
khoá `announced_added`/`oshares_announced_added`. Selfcheck C2/C3 viết lại; mutant M5/M6 cũ bỏ theo.

## R5 — khoá khung ex-date giá↔số CP
`fair_value(..., price_date=None)` (tham số mới, bị bỏ qua ở `fin`). Ở `live`, `_live_oshares`:
không giá ⇒ số sống tại asof; có giá ⇒ cần `price_date`, và `oshares_for(price_date) == oshares_for(asof)`.
Không khoá được (thiếu `price_date` / hai số khác / ngày hỏng) ⇒ số quý, `oshares_method="FRAME_FALLBACK"`,
`oshares_frame_error` ghi lý do, `_shout` (thiếu price_date: 1 lần/tiến trình; lệch: 1 lần/(mã, asof, ngày giá)).
Selfcheck C7 (10 check). Giới hạn: KHÔNG bắt vendor trễ lật status (cả hai ngày cùng đọc dữ liệu cũ) — `fin` cùng lỗi đó.

## Selfcheck
Lệnh (từ `/home/trido/wt-oshares-r2r7-20261030/WorkingClaude`, `DCF_OS_OPS_HEALTH=<ops worktree>`):
- `oshares_dcf_selfcheck.py`: **67 PASS, 0 FAIL, 12/12 mutant KILLED** ở `TZ=UTC` (`run_selfcheck_UTC.txt`) và
  `env -u TZ` (`run_selfcheck_noTZ.txt`); `--bq` TZ=UTC 74 PASS (`run_selfcheck_bq_UTC.txt`).
  Mutant mới: M8 bỏ khoá, M9 khoá không so số hai ngày, M10 env lạ nhận nguyên văn, M11 pin no-op,
  M12 bỏ dedupe tiếng kêu, M13 ops bỏ quét .py, M14 ops bỏ cảnh báo env cron.
- `dcf_rate_frame_selfcheck`, `dcf_check_selfcheck`, `dcf_selector_selfcheck`, `dcf_refresh_gate_selfcheck`,
  `dcf_earning_power_test`, `tz_asof_ict_dd_dcf_selfcheck`: rc=0 cả `TZ=UTC` và `env -u TZ` (`run_dcf_selfchecks.txt`).
- Byte-identical mặc định: `byte_identical.py` main vs worktree, env trống, asof 2026-10-29 + 2025-10-29:
  **774 kết quả, 0 khác repr** (`run_byte_identical_stdout.txt`).
- Phụ thuộc môi trường: BQ (`--bq`, đo ảnh hưởng), parquet canonical `data/bq_cache` (WORKDIR cứng).

## R7 — ảnh hưởng (đo lại sau R4+R5: `measure_impact_r5.py`, `run_impact_r5_stdout.txt`, `out_impact_r5_<asof>.csv`)
| asof | DCF ok | live KHÔNG price_date | live price_date=phiên giá: FV đổi / >1% / >5% / lật status / đổi robust |
|---|---|---|---|
| 2026-10-29 | 145 | 0 mã đổi (145 FRAME_FALLBACK) | 9 / 7 / 6 / 3 (PHR, HTN, AIG CHEAP→RICH) / 1 (HTN) |
| 2026-07-29 | 157 | 0 | 13 / 11 / 9 / 1 (REE CHEAP→RICH) / 0 |
| 2025-10-29 | 184 | 0 | 7 / 6 / 4 / 1 (BSR CHEAP→RICH) / 1 (BSR) |
| 2024-10-29 | 149 | 0 | 4 / 2 / 1 / 1 (GAS CHEAP→RICH) / 0 |
Trùng từng số với bảng vòng 1 (`oshares_live_dcf_20261030/SELFCHECK.md` §4) ⇒ bỏ R4 không đổi kết quả. `ok_fin != ok_live` = 0 ở cả 4 asof.
**Hệ quả quan trọng:** bật live mà chưa sửa caller ⇒ 0 thay đổi trên đường tiền (mọi caller production truyền giá, không truyền `price_date`).

## Gói cho quant-skeptic (Mike gọi)
1. Khoá R5 so `oshares_for(price_date)` vs `oshares_for(asof)` — có ca nào số CP bằng nhau nhưng khung vẫn lệch
   (vd sự kiện ex đúng `asof` khi giá là tham chiếu phiên trước được khai `price_date=asof`)? Hợp đồng `price_date`
   = phiên mà giá CHƯA điều chỉnh thuộc về; caller khai sai thì khoá không cứu.
2. R4: bằng chứng "chưa từng có hiệu lực" dựa trên 4 asof × universe_pit — đủ chưa? Ca vendor trễ trên mã
   phi tài chính trong cửa sổ ≤1 ngày có bỏ sót trước-mốc-lật không?
3. 3 lật CHEAP→RICH 2026-10-29 (PHR thưởng 80% ex 09-11, HTN 50% ex 09-10, AIG 15% ex 08-04) — đối chiếu
   `corporate_action`; BSR 2025-10-29 method `FIN_FALLBACK` mà osh_live 5,007tr ≠ fin 3,100tr — kiểm nhãn method.
4. MST 2025-10-29 ×1,3588 (số quý 113,6tr restated > AIS 83,6tr) — PIT hay lỗi AIS?
5. R3: có script nghiên cứu nào ghi output canonical/ghim mà grep bỏ sót (gọi qua `custom_basket` với DCF gate)?
6. Ops CHECKDCFOS: quét `*.py` gốc + trading_bot + mike/bin, bỏ selfcheck/test — có launcher nằm ngoài (systemd unit, ccdb)?

## Merge (CHỈ sau arch-review + quant-skeptic + user)
```bash
git -C /home/trido/thanhdt merge --no-ff session/oshares-r2r7-20261030
git -C /home/trido/thanhdt/WorkingClaude/mike merge --no-ff session/oshares-r2r7-ops-20261030
```
Bật live = quyết định RIÊNG, sau khi caller khai `price_date` (xem `kb/projects/oshares-live-dcf-20261030.md`).
