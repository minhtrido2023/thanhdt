@echo off
REM Ngũ Hành Shadow Daily Wrapper
REM Used by Windows Task Scheduler — runs ngu_hanh_shadow_tracker.py + appends log
cd /d "C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude"
python ngu_hanh_shadow_tracker.py >> "ngu_hanh_shadow_daily.log" 2>&1
echo. >> "ngu_hanh_shadow_daily.log"
echo ==================================================== >> "ngu_hanh_shadow_daily.log"
echo. >> "ngu_hanh_shadow_daily.log"
