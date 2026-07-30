@echo off
REM daily_refresh_v3_4b.bat
REM Windows version of daily_refresh_v3_4b.sh

cd /d "%~dp0"
set STATE_WORKDIR=%CD%

echo ============================================================
echo Daily v3.4b refresh pipeline
echo WORKDIR: %STATE_WORKDIR%
echo ============================================================

echo.
echo [1/4] Pulling US market data...
python pull_us_market.py || exit /b 1

echo.
echo [2/4] Building v3.1...
python build_v3_1_clean.py || exit /b 1
copy /Y vnindex_5state_tam_quan_v3_1_clean.csv vnindex_5state_tam_quan_v3_1_full_history.csv >nul

echo.
echo [3/4] Building v3.4b...
python build_v3_4_bull_aware.py || exit /b 1

echo.
echo [4/4] Deploying to LIVE BQ...
python deploy_v3_4b_to_live.py || exit /b 1

echo.
echo ============================================================
echo Daily v3.4b refresh complete
echo ============================================================
