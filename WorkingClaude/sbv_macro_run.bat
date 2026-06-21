@echo off
REM Daily wrapper for SBV Macro Overlay tracker
cd /d "C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude"
python sbv_macro_tracker.py update >> sbv_macro_run.log 2>&1
