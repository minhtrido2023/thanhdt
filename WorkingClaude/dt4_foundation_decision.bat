@echo off
REM DT4-vs-TQ34b foundation A/B — GO-LIVE decision review.
REM Pulled forward per user (go-live early June): one-time on 2026-05-29 16:00.
setlocal
set WORKDIR=C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude
cd /d "%WORKDIR%"
python pt_dt4_vs_tq34b_ab.py > "%WORKDIR%\data\dt4_foundation_decision_run.log" 2>&1
copy /Y "%WORKDIR%\data\pt_dt4_vs_tq34b_ab_report.md" "%WORKDIR%\data\DT4_FOUNDATION_DECISION.md" >nul
powershell -NoProfile -Command "try{Add-Type -AssemblyName System.Windows.Forms; $t=Get-Content '%WORKDIR%\data\DT4_FOUNDATION_DECISION.md' -Raw; [System.Windows.Forms.MessageBox]::Show($t,'DT4 vs TQ34b — GO-LIVE decision')}catch{}"
endlocal
