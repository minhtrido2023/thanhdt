@echo off
REM 8L interactive Telegram bot — long-polls for ticker queries (e.g. "BMP 8L") and replies with 8L ranking.
REM Registered ONLOGON so it stays running. Logs to data\telegram_8l_bot.log
setlocal
set WORKDIR=C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude
set PATH=%PATH%;C:\Users\hotro\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin
set CLOUDSDK_PYTHON=C:\Users\hotro\AppData\Local\Google\Cloud SDK\google-cloud-sdk\platform\bundledpython\python.exe
set SYSPY=C:\Users\hotro\AppData\Local\Python\pythoncore-3.14-64\python.exe
cd /d "%WORKDIR%"
"%SYSPY%" telegram_8l_bot.py >> "%WORKDIR%\data\telegram_8l_bot.log" 2>&1
endlocal
