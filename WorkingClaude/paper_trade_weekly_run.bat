@echo off
REM Weekly paper-trade report to Telegram — runs Fri 15:30 (after daily 14:55)

cd /d C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude

set LOGFILE=paper_trade_weekly_%date:~10,4%-%date:~4,2%-%date:~7,2%.log

echo ===== Paper-trade weekly report started %date% %time% ===== >> %LOGFILE%

python paper_trade_weekly_report.py >> %LOGFILE% 2>&1

set EXITCODE=%ERRORLEVEL%
echo ===== Exit code: %EXITCODE% at %time% ===== >> %LOGFILE%

REM Keep last 60 days of logs
forfiles /p . /m paper_trade_weekly_*.log /d -60 /c "cmd /c del @path" 2>nul

exit /b %EXITCODE%
