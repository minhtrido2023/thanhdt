@echo off
REM 12-month report wrapper — scheduled for 2027-05-19
cd /d "C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude"
python sbv_macro_tracker.py report > sbv_macro_report_run.log 2>&1
