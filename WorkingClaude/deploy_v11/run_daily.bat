@echo off
REM BA-system V11 daily runner — Windows.
REM Schedule via Task Scheduler (xem DEPLOY.md mục 4.2).

REM ─── CONFIG — sửa các path này cho server của bạn ────────────────────────
set WORKDIR=C:\Users\USER\deploy_v11
set VENV_PYTHON=%WORKDIR%\.venv\Scripts\python.exe
set LOG_DIR=%WORKDIR%\logs

REM Service account key
set GOOGLE_APPLICATION_CREDENTIALS=%USERPROFILE%\.gcp\ba-sa-key.json

REM ─── RUN ─────────────────────────────────────────────────────────────────
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set DT=%%I
set DATE=%DT:~0,4%-%DT:~4,2%-%DT:~6,2%
set LOG=%LOG_DIR%\run_%DATE%.log

echo === %DATE% %TIME% --- BA-system daily run === >> "%LOG%"
cd /d "%WORKDIR%"

if "%~1"=="" (
    "%VENV_PYTHON%" recommend_holistic.py >> "%LOG%" 2>&1
) else (
    "%VENV_PYTHON%" recommend_holistic.py %1 >> "%LOG%" 2>&1
)

set EXIT=%ERRORLEVEL%
echo === exit %EXIT% === >> "%LOG%"
exit /b %EXIT%
