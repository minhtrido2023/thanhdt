@echo off
REM Daily BA-system Telegram notifier — runs at 18:00 each weekday
REM Set up via Task Scheduler. See TELEGRAM_SETUP.md for instructions.

cd /d C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude

REM Logfile (rolling per day)
set LOGFILE=telegram_run_%date:~10,4%-%date:~4,2%-%date:~7,2%.log

echo ===== BA-system Telegram run started %date% %time% ===== >> %LOGFILE%

REM Run the notifier (use full Python path if needed)
python telegram_recommend.py >> %LOGFILE% 2>&1

set EXITCODE=%ERRORLEVEL%
echo ===== Exit code: %EXITCODE% at %time% ===== >> %LOGFILE%

REM Keep last 30 days of logs (delete older)
forfiles /p . /m telegram_run_*.log /d -30 /c "cmd /c del @path" 2>nul

exit /b %EXITCODE%
