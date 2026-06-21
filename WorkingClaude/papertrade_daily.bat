@echo off
REM Daily paper-trade orchestrator — runs 4 sims + comparison.
REM Triggered by Windows Task Scheduler at 15:30 daily.
REM Logs each run to data\papertrade_run_YYYY-MM-DD.log
REM
REM Updated 2026-05-27:
REM  - Removed pt_v12_live (V3 alt state test, no longer needed)
REM  - UPGRADED V11: KELLY ETF + DT_10_25_25 state (validated +1.90pp Full CAGR)
REM  - Renamed versions to architecture-based names for clarity:
REM    V11        = Song Sinh (BAL+VN30) + KELLY + DT_10_25_25  ⭐ upgraded
REM    V12        = Am Duong (BAL+LAGGED) + TQ34b
REM    V121_ENS   = V12.1 + Ensemble (M1+M3r AND-HOLD) + TQ34b + BASE
REM    V121_Kelly = V121_ENS + Kelly NEUTRAL parking {3:1.0}

setlocal
set WORKDIR=C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude
set TODAY=%date:~10,4%-%date:~4,2%-%date:~7,2%
set LOGFILE=%WORKDIR%\data\papertrade_run_%TODAY%.log

cd /d "%WORKDIR%"

echo ==================================================== > "%LOGFILE%"
echo Paper-trade daily run (5 systems + DT A/B) — %DATE% %TIME% >> "%LOGFILE%"
echo ==================================================== >> "%LOGFILE%"

echo [0a] pull_us_market.py  (refresh US VIX/SPX -^> us_market_history.csv, Pillar B) >> "%LOGFILE%"
python pull_us_market.py                                              >> "%LOGFILE%" 2>&1

echo [0a2] rebuild_state_from_ticker.bat  (self-update v3.4b+DT4 state from BQ ticker, local only) >> "%LOGFILE%"
call rebuild_state_from_ticker.bat                                    >> "%LOGFILE%" 2>&1

echo [0/6] refresh_lagged_caches.py  (extend px/ov/surprise/events to latest BQ) >> "%LOGFILE%"
python refresh_lagged_caches.py                                       >> "%LOGFILE%" 2>&1

echo [0b] snapshot_state_vintage.py  (accumulate point-in-time state vintage) >> "%LOGFILE%"
python snapshot_state_vintage.py                                      >> "%LOGFILE%" 2>&1

echo [0c] macro_healthcheck.py  (DT5G feed health + fail-safe gate -^> data\macro_health.json) >> "%LOGFILE%"
python macro_healthcheck.py                                           >> "%LOGFILE%" 2>&1

echo [0d] publish_gated_state.py  (publish DT5G gated state -^> BQ vnindex_5state_dt5g_live) >> "%LOGFILE%"
python deploy_golive_dt5g_v4\publish_gated_state.py                  >> "%LOGFILE%" 2>&1

echo [0e] custom30_history.py     (publish 8L custom30 parking basket -^> BQ tav2_bq.custom30_8l, namecap) >> "%LOGFILE%"
python custom30_history.py                                           >> "%LOGFILE%" 2>&1

REM [0e] golive_recommend.py (V4 12.1 LAYER2 picks) RETIRED from daily run 2026-06-12 —
REM 18:00 report now centers on V2.3 picks (golive_recommend_v23.py at [4c2]); V4 demoted to
REM NAV benchmark only (pt_v4_dt5g still runs at [4b]). Script kept; re-enable if V4 picks needed.

REM === Production base = DT4G + MACRO overlay (adopted 2026-05-29) ===
echo [1/4] pt_v11_tq34b.py        (V11 = Song Sinh + KELLY + DT4G+MACRO) >> "%LOGFILE%"
python pt_v11_tq34b.py                                                 >> "%LOGFILE%" 2>&1

echo [2/4] pt_v12_macro.py        (V12 = Am Duong: BAL+LAGGED + DT4G+MACRO) >> "%LOGFILE%"
python pt_v12_macro.py                                                 >> "%LOGFILE%" 2>&1

REM Retired 2026-05-29 (DT4G+macro adopted as base): pt_v12_tq34b (old TQ34b base),
REM pt_v12_dt4 (DT-only shadow) -- both superseded by pt_v12_macro.

echo [3/4] pt_v121_ensemble.py    (V121_ENS: V12.1 + Ensemble + BASE + TQ34b*) >> "%LOGFILE%"
python pt_v121_ensemble.py                                             >> "%LOGFILE%" 2>&1
REM *ensemble still on TQ34b pending DT4G+macro integrated validation (research: DT hurts ensemble OOS)

echo [4/4] pt_v121_ens_q2.py      (V121_Kelly: V121_ENS + Kelly + TQ34b*) >> "%LOGFILE%"
python pt_v121_ens_q2.py                                               >> "%LOGFILE%" 2>&1

echo [4b] pt_v4_dt5g.py           (V4 12.1: V121_ENS + BASE on DT5G, fresh 2026-06-01) >> "%LOGFILE%"
python pt_v4_dt5g.py                                                   >> "%LOGFILE%" 2>&1

echo [4c] pt_v22_dt5g.py          (V2.3 = V2.2 BAL^|LAG static + parking + CAPIT v2, fresh 2026-06-11 — OOS showdown vs V4) >> "%LOGFILE%"
python pt_v22_dt5g.py                                                  >> "%LOGFILE%" 2>&1

echo [4c2] golive_recommend_v23.py (V2.3 LAYER2 picks: BAL + LAG + allocator + capit -^> out\golive_v23_recommendations_DATE.csv + data\golive_v23_status.json, read by 18:00 report) >> "%LOGFILE%"
python deploy_golive_dt5g_v4\golive_recommend_v23.py                  >> "%LOGFILE%" 2>&1

REM [4d] pt_book_c.py (Book C VALUE) RETIRED 2026-06-12 — 3-book plan dropped (Book C not a
REM reliable grind hedge: value+momentum co-fell in 2025-26; Sharpe gain not worth MaxDD/Calmar
REM tradeoff + complexity). Focus = improve V2.3. Script kept for reference, not run daily.

echo [5] papertrade_compare.py    (system comparison)                 >> "%LOGFILE%"
python papertrade_compare.py                                           >> "%LOGFILE%" 2>&1

echo [5b] vol_spike_hedge_pt.py   (VOL-SPIKE HEDGE cho V5, paper-trade tam thoi -^> 2026-06-30) >> "%LOGFILE%"
python vol_spike_hedge_pt.py                                           >> "%LOGFILE%" 2>&1

echo [5c] f_sleeve_pt.py          (F-SYSTEM standalone sleeve DT5G+Van, paper-trade -^> 2026-06-30) >> "%LOGFILE%"
python f_sleeve_pt.py                                                  >> "%LOGFILE%" 2>&1

echo [5d] orb_pt.py               (ORB intraday VN30F paper-trade live, tai dung tu bar 1m sau dong phien) >> "%LOGFILE%"
python orb_pt.py                                                       >> "%LOGFILE%" 2>&1

echo [7] pt_dt4_vs_tq34b_ab.py   (DT4 vs TQ34b foundation A/B, V1-V5, DECISION 2026-06-30) >> "%LOGFILE%"
python pt_dt4_vs_tq34b_ab.py                                           >> "%LOGFILE%" 2>&1

echo [8] crisis_alert_push.py     (DT5G x 8L capitulation -^> Telegram push ONLY if WATCH/STRONG) >> "%LOGFILE%"
python crisis_alert_push.py                                           >> "%LOGFILE%" 2>&1

echo [9] pt_capitulation_shadow.py (capitulation-overlay SHADOW sleeve, separate from V4/V5 books) >> "%LOGFILE%"
python pt_capitulation_shadow.py                                      >> "%LOGFILE%" 2>&1

echo [10] fetch_bdi_daily.py      (forward-accumulate REAL Baltic Dry Index -^> data\bdi_daily_real.csv) >> "%LOGFILE%"
python fetch_bdi_daily.py                                             >> "%LOGFILE%" 2>&1

echo [11] edge_health_monitor.py  (AMH#1: rolling-12M IC edge health + per-sector + capit-edge -^> data\edge_health_block.md) >> "%LOGFILE%"
python edge_health_monitor.py --refresh                               >> "%LOGFILE%" 2>&1

echo [12] ecology_dashboard.py    (AMH#4: breadth/dispersion/mood/divergence -^> data\ecology_now.md) >> "%LOGFILE%"
python ecology_dashboard.py --refresh                                 >> "%LOGFILE%" 2>&1

echo [13] amh_cockpit.py          (V6 Tu Tru allocation + #1/#4 dashboards -^> data\amh_cockpit.md, read by 18:00 push) >> "%LOGFILE%"
python amh_cockpit.py                                                 >> "%LOGFILE%" 2>&1

echo [14] pt_sleeve_allocator.py  (FORWARD paper-trade V6 Tu Tru vs V5 -^> data\v6_vs_v5_paper.csv, go-live evidence) >> "%LOGFILE%"
python pt_sleeve_allocator.py                                         >> "%LOGFILE%" 2>&1

echo [15] phosphorus_dgc_weekly.py (WEEKLY Fri only: P4 spot trend -^> DGC nhan dinh, data\dgc_phosphorus_watch.md) >> "%LOGFILE%"
for /f %%d in ('powershell -NoProfile -Command "(Get-Date).DayOfWeek"') do set DOW=%%d
if /i "%DOW%"=="Friday" (
    python phosphorus_dgc_weekly.py                                  >> "%LOGFILE%" 2>&1
) else (
    echo   skipped — runs Fridays only ^(today=%DOW%^)                >> "%LOGFILE%"
)

echo Done %TIME%                                                       >> "%LOGFILE%"
endlocal
