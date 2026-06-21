@echo off
set WORKDIR=C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude
set CLOUDSDK_PYTHON=C:\Users\hotro\AppData\Local\Google\Cloud SDK\google-cloud-sdk\platform\bundledpython\python.exe
cd /d "%WORKDIR%"
"%CLOUDSDK_PYTHON%" remind_bc.py >> "%WORKDIR%\data\remind_bc.log" 2>&1
