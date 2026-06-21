@echo off
REM 5-state daily refresh + classify + upload (Windows).
REM Schedule via Task Scheduler (xem DEPLOY.md).

set WORKDIR=C:\Users\USER\deploy_5state
set VENV_PYTHON=%WORKDIR%\.venv\Scripts\python.exe
set LOG_DIR=%WORKDIR%\logs

set BAVN_WORKDIR=%WORKDIR%
set GOOGLE_APPLICATION_CREDENTIALS=%USERPROFILE%\.gcp\ba-sa-key.json

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set DT=%%I
set DATE=%DT:~0,4%-%DT:~4,2%-%DT:~6,2%
set LOG=%LOG_DIR%\5state_%DATE%.log

echo === %DATE% %TIME% --- 5-state daily run === >> "%LOG%"
cd /d "%WORKDIR%"

echo. >> "%LOG%"
echo [STEP 1] refresh_data.py >> "%LOG%"
"%VENV_PYTHON%" refresh_data.py >> "%LOG%" 2>&1
if errorlevel 1 goto :error

echo. >> "%LOG%"
echo [STEP 2] vnindex_5state_system.py >> "%LOG%"
"%VENV_PYTHON%" vnindex_5state_system.py >> "%LOG%" 2>&1
if errorlevel 1 goto :error

echo. >> "%LOG%"
echo [STEP 3] upload_to_bq.py >> "%LOG%"
"%VENV_PYTHON%" upload_to_bq.py >> "%LOG%" 2>&1
if errorlevel 1 goto :error

echo. >> "%LOG%"
echo === DONE === >> "%LOG%"
exit /b 0

:error
echo. >> "%LOG%"
echo === FAILED at step (errorlevel %ERRORLEVEL%) === >> "%LOG%"
exit /b 1
