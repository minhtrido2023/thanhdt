@echo off
REM Layer 3 v4 shadow tracker — daily Windows Task Scheduler entry
REM Runs after market close to capture today's BA picks vs T+1 fill alpha
REM Schedule: trigger 15:30 weekdays (after 14:45 ATC close + settle)
cd /d "C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude"
echo === %DATE% %TIME% === >> data\layer3_v4_shadow_cron.log
python layer3_v4_shadow.py update >> data\layer3_v4_shadow_cron.log 2>&1
echo --- alert: >> data\layer3_v4_shadow_cron.log
python layer3_v4_shadow.py alert >> data\layer3_v4_shadow_cron.log 2>&1
