@echo off
REM Daily wrapper for BullDvg Boost tracker
REM Scheduled via: schtasks /create /tn "BullDvgBoost" /tr ... /sc daily /st 15:15
cd /d "C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude"
python bull_div_boost_tracker.py update >> bull_div_boost_run.log 2>&1
