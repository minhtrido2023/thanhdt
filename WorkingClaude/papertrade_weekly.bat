@echo off
REM Weekly paper-trade report — runs Sunday 16:00 after daily refresh.
setlocal
set WORKDIR=C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude
set TODAY=%date:~10,4%-%date:~4,2%-%date:~7,2%
set LOGFILE=%WORKDIR%\data\papertrade_weekly_run_%TODAY%.log

cd /d "%WORKDIR%"
echo Weekly report — %DATE% %TIME% > "%LOGFILE%"
python papertrade_weekly_report.py >> "%LOGFILE%" 2>&1
echo Done %TIME% >> "%LOGFILE%"
endlocal
