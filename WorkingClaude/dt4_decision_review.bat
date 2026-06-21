@echo off
REM One-time end-of-June reminder: surface the V12 DT 4-gate vs TQ34b A/B decision.
REM Registered as Windows scheduled task "DT4DecisionReview" (runs once 2026-06-29 09:00 local).
setlocal
set WORKDIR=C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude
cd /d "%WORKDIR%"
python dt4_decision_review.py >> "%WORKDIR%\data\dt4_decision_review.log" 2>&1
endlocal
