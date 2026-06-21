@echo off
REM rebuild_state_from_ticker.bat
REM ============================================================================
REM Self-update the v3.4b + DT4-gate market-state series LOCALLY from the freshest
REM BQ `ticker` data — so the live state tracks ticker (no dependence on the BQ
REM vnindex_5state_tam_quan_v34b_clean table, which lags when deploy is skipped).
REM macro_state_live.get_macro_state() reads the local CSV produced here.
REM
REM Chain: ew_v1 (BQ pull) -> concentration -> dual_v3 -> v3.1(clean) -> v3.4b -> dt_4gate.
REM LOCAL CSVs ONLY — the risky BQ deploy step (deploy_v3_4b_to_live.py) is deliberately
REM SKIPPED. Bug guards: (1) delete pkl caches first (ew_v1 skips refresh if they exist);
REM (2) set STATE_WORKDIR so the v3.1/v3.4b builders read fresh files from MAIN, not the
REM package dir. Assumes us_market_history.csv was already refreshed (pull_us_market.py).
setlocal
set WORKDIR=C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude
set STATE_WORKDIR=%WORKDIR%
cd /d "%WORKDIR%"

REM bug 1: stale caches -> ew_v1 would reuse old pulls
del /q "%WORKDIR%\_cache_vnindex_2000_now.pkl" "%WORKDIR%\_cache_universe_2013_now.pkl" 2>nul

python vnindex_5state_ew_v1.py                || goto :err
python build_concentration_history.py         || goto :err
python vnindex_5state_dual_v3.py              || goto :err
python deploy_v3_4b_package\build_v3_1_clean.py || goto :err
copy /Y "%WORKDIR%\vnindex_5state_tam_quan_v3_1_clean.csv" "%WORKDIR%\vnindex_5state_tam_quan_v3_1_full_history.csv" >nul
python deploy_v3_4b_package\build_v3_4_bull_aware.py || goto :err
python build_dt_4gate.py                       || goto :err
echo rebuild_state_from_ticker: OK
endlocal & exit /b 0

:err
echo rebuild_state_from_ticker: FAILED (step errored) — macro_state_live will keep using the last good local CSV; macro_healthcheck will flag staleness.
endlocal & exit /b 1
