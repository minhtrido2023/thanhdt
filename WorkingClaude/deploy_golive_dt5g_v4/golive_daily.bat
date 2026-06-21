@echo off
REM ============================================================================
REM golive_daily.bat  —  V2.3 + DT5G production go-live daily pipeline.
REM (2026-06-12: step [5] switched golive_recommend.py V4 -> golive_recommend_v23.py.
REM  V4 retired from production; see README_zip3_v23.md.)
REM Run once per trading day AFTER the BQ `ticker` table has the latest session
REM (recommended ~15:30 ICT, after market close + BQ ingest). One scheduled task.
REM
REM Flow:
REM   [1] pull_us_market          refresh US VIX/SPX (Pillar B of DT5G macro)
REM   [2] rebuild_state_from_ticker  self-update v3.4b + DT4 state from BQ ticker (local)
REM   [3] macro_healthcheck       feed health + writes data\macro_health.json (fail-safe gate input)
REM   [4] publish_gated_state     gated DT5G state -> BQ vnindex_5state_dt5g_live (+ json)
REM   [5] golive_recommend_v23    V2.3+DT5G daily order/position recommendations
REM Logs: data\golive_run_YYYY-MM-DD.log
REM ============================================================================
setlocal
set ROOT=C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude
set PKG=%ROOT%\deploy_golive_dt5g_v4
set TODAY=%date:~10,4%-%date:~4,2%-%date:~7,2%
set LOG=%ROOT%\data\golive_run_%TODAY%.log
cd /d "%ROOT%"

echo ============================================== > "%LOG%"
echo GO-LIVE V2.3+DT5G daily — %DATE% %TIME% >> "%LOG%"
echo ============================================== >> "%LOG%"

echo [1/5] pull_us_market.py                 >> "%LOG%"
python pull_us_market.py                     >> "%LOG%" 2>&1

echo [2/5] rebuild_state_from_ticker.bat      >> "%LOG%"
call rebuild_state_from_ticker.bat           >> "%LOG%" 2>&1

echo [3/5] macro_healthcheck.py               >> "%LOG%"
python macro_healthcheck.py                  >> "%LOG%" 2>&1
REM exit codes: 0 HEALTHY, 1 DEGRADED, 2 FAILED. Pipeline continues either way;
REM the gate (publish_gated_state) auto-reverts to DT4-only when health != OK.

echo [4/5] publish_gated_state.py             >> "%LOG%"
python deploy_golive_dt5g_v4\publish_gated_state.py >> "%LOG%" 2>&1

echo [5/5] golive_recommend_v23.py             >> "%LOG%"
python deploy_golive_dt5g_v4\golive_recommend_v23.py >> "%LOG%" 2>&1

echo Done %TIME% >> "%LOG%"
echo Recommendations: %PKG%\out\golive_v23_recommendations_%TODAY%.md
endlocal
