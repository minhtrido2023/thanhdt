# oshares_live R8 — SELFCHECK (job Taylor_20261031_025427, 31/10/2026)

Nhánh (CHƯA merge, knob `OSHARES_SOURCE_DEFAULT` VẪN `fin`):
- WC `session/oshares-r8-20261031` @ `7b4d43a98` (worktree `/home/trido/wt-oshares-r8-20261031`):
  `custom_basket.py`, `dcf_valuation.py`, `oshares_dcf.py`, `oshares_dcf_selfcheck.py`,
  `trading_bot/due_diligence.py`, `trading_bot/strategies.py` (+460/−41, `git show --stat`).
- mike `session/oshares-r8-ops-20261031` @ `96dcb2ce5` (worktree `WorkingClaude/wt-oshares-r8-ops-20261031`):
  `bin/lag_dd_pack.py`, `bin/ops_health_check.sh` (mục 17/H6), `kb/projects/oshares-live-dcf-20261030.md` (+97/−13).

## 1. oshares_dcf_selfcheck.py (phần mới H1/H2/H3/H4/H6)
| Chạy | Kết quả | Log |
|---|---|---|
| TZ=UTC | 102 PASS, 22/22 mutant KILLED, rc=0 | `run_selfcheck_UTC.txt` |
| env -u TZ | 22/22 mutant KILLED, rc=0 | `run_selfcheck_noTZ.txt` |
| TZ=UTC + BQ | 22/22 mutant KILLED, rc=0 | `run_selfcheck_bq_UTC.txt` |
`DCF_OS_OPS_HEALTH` trỏ `bin/ops_health_check.sh` của worktree mike (worktree không có `mike/` ở gốc).
Ca killer của skeptic (ex==asof, giá pre-ex, price_date=asof) = C7; ERROR im lặng = C10; probe nạp
đúng cây = C4/C6/C12 (+ M22 ghim HERE); caller khai phiên = C11 (+ M21 rơi về Close ⇒ không khai).

## 2. fin byte-identical (đường tiền khi knob = fin)
`byte_identical_r8.py` / `byte_compare_r8.py`: main vs nhánh, 6.228 kết quả (fair_value 1.557 +
dcf_check 1.557 + `_dcf_check_for_order` 1.557 + ref 1.557; 4 asof 2026-10-29/2026-07-29/2025-10-29/
2024-10-29), `keys_equal True`, `diff_repr 0` (`run_byte_identical_stdout.txt`).

## 3. Selfcheck rộng (module lõi dùng chung: strategies/due_diligence/custom_basket ⇒ quét rộng)
Chạy qua `run_wt.py` (nạp code WT thật, in đường dẫn module lúc thoát), so với PROD (`sc_prod_UTC.txt`):

| Script | WT UTC | WT noTZ | PROD UTC | Kết luận |
|---|---|---|---|---|
| dcf_rate_frame / dcf_check / dcf_selector / dcf_refresh_gate / dcf_earning_power / tz_asof_ict_dd_dcf / due_diligence / basket_price_basis_audit | 0 | 0 | 0 | PASS |
| test_trading_bot | 1 | 1 | 0 | MÔI TRƯỜNG: `secrets/` gitignored, WT chỉ có stub 190 byte ⇒ `gap_adaptive_enabled` của 'main' sai. Chạy lại code nhánh với config thật (symlink tạm, đã trả stub): **rc=0 cả UTC lẫn noTZ** (`sc_wt_realcfg_{UTC,none}_test_trading_bot.py.log`) |
| custom_basket_forensic_failclosed | 1 | 1 | 0 | MÔI TRƯỜNG, có sẵn: test giả định worktree KHÔNG có `data/forensic_flags.csv`, nhưng file này đã được track trong git ⇒ worktree main sạch (`wt-r8-control-main`) cũng FAIL y hệt (`sc_control_main_UTC_*.log`) |
| basket_oshares_step_exdate / basket_price_basis / basket_return_leg_oshares | 1 | 1 | 1 | ĐÍNH CHÍNH 31/10 (arch-reviewer): FAIL này chỉ xảy ra khi chạy bằng `python3` hệ thống (pandas 2.3); dưới `wc_venv` (pandas 3, interpreter pin) cả 3 PASS. Không phải lỗi có sẵn của PROD. |
| test_multi_strategy | 1 | 1 | 1 | CÓ SẴN trên PROD: DuckDB cache thiếu cột `VNINDEX_RSI_Max3M` |
Lưu ý (đính chính 31/10): 3 selfcheck basket PASS dưới `wc_venv`; chạy bằng `python3` hệ thống thì hỏng do pandas 2.3 — luôn dùng `$DNA_PYEXE`. `custom_basket.dcf_at` được phủ bởi cả selfcheck basket (wc_venv) lẫn oshares_dcf_selfcheck C11 + đo impact (mục 4).
`basket_return_leg_oshares` in `custom_basket` nạp từ PROD (script tự chèn path) — không ảnh hưởng kết
luận vì fail trước đó ở merge.

## 4. Impact khi bật live (`measure_impact_r8.py`, `impact_r8_summary.json`, `impact_r8_decisions.txt`)
- NOPD (caller không khai price_date — plan approval/EOD): fv_changed 0 ở 4 asof (toàn FRAME_FALLBACK).
- PD (caller khai phiên giá): fv_changed 6 / 13 / 5 / 4; lật CHEAP→RICH: AIG, HTN, PHR (2026-10-29),
  REE (2026-07-29), GAS (2024-10-29). DCF_RICH sâu (MoS<−100%) mới: 0; mất: MST (2025-10-29).
- PDM1 (chạy sáng T+1): HHV 2025-10-30 robust False→True.

## 5. H5 — đối chiếu corporate_action (`h5_corporate_action.csv`, `h5_ratio_check.txt`)
| asof | Mã | osh_PD/osh_FIN | 1+tỷ lệ CA | Sự kiện | Kết luận |
|---|---|---|---|---|---|
| 2026-10-29 | PHR | 1,8000 | 1,8000 | ISS Bonus 80% ex 2026-09-11 | CP tăng thật |
| 2026-10-29 | HTN | 1,5000 | 1,5000 | ISS Bonus 50% ex 2026-09-10 | CP tăng thật |
| 2026-10-29 | AIG | 1,1500 | 1,1500 | ISS Bonus 15% ex 2026-08-04 | CP tăng thật |
| 2026-07-29 | REE | 1,1500 | 1,1500 | ISS DIV 15% ex 2026-05-18 | CP tăng thật |
| 2024-10-29 | GAS | 1,0200 | 1,0200 | ISS Bonus 2% ex 2024-09-13 | CP tăng thật |
| 2025-10-29 | BSR | 1,0000 | 1,6150 | ISS Bonus 31,5% + DIV 30%, ex 2025-10-29 = phiên giá | Khoá lịch H1 ép số quý (bảo thủ, mất 1 ca đúng) |
| 2025-10-29 | MST | 0,7359 | n/a | AIS 83,6tr vs số quý 113,6tr; PP ex 2025-11-24 SAU asof | CHƯA kết luận (skeptic mục 4) |
⇒ 5/5 lật là đúng (số quý chưa cộng CP thưởng/cổ tức ⇒ FV/CP bị thổi phồng), không phải artefact.

## 6. H6
Mục 17 `ops_health_check.sh` quét thêm: systemd user (+drop-in, environment.d), ccdb `.env`, settings
Claude, shell profile, `/proc/*/environ`. 31/10: 0 lần gán `DCF_OSHARES_SOURCE` (11 file + 18 tiến trình).
Hạn chế: /proc của user khác không đọc được.
