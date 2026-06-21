@echo off
REM rebuild_baseline.bat — refresh the DT5G prod-spec baseline + recompute the
REM capitulation overlay BEFORE any upgrade decision. Guards against the stale-file
REM trap (data\5sys_prodspec_201401_202605_dt5g.csv had drifted x9.98 vs fresh x13.23).
setlocal
set WORKDIR=C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude
cd /d "%WORKDIR%"
set STATE_OVERRIDE=dt5g
set TAG_SUFFIX=_dt5g
set PYTHONIOENCODING=utf-8

echo [1/2] Rebuilding fresh DT5G baseline + REAL daily cash ledger...
python run_5systems_prodspec.py
echo.
echo [2/2] Recomputing capitulation overlay on the fresh baseline (no proxy)...
python final_overlay_realcash.py
echo.
echo Done. Use these fresh numbers for the decision — do NOT trust older _dt5g.csv.
endlocal
