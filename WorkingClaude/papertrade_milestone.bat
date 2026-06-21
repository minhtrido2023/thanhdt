@echo off
REM Milestone paper-trade report — runs 2026-06-30 (mid) + 2026-08-31 (final).
REM Auto-detects tag based on date.
setlocal
set WORKDIR=C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude
set TODAY=%date:~10,4%-%date:~4,2%-%date:~7,2%
set LOGFILE=%WORKDIR%\data\papertrade_milestone_run_%TODAY%.log

cd /d "%WORKDIR%"
echo Milestone report — %DATE% %TIME% > "%LOGFILE%"
python papertrade_milestone_report.py >> "%LOGFILE%" 2>&1
echo Done %TIME% >> "%LOGFILE%"
endlocal
