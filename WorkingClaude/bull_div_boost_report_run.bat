@echo off
REM 12-month report wrapper — scheduled one-time for 2027-05-19
cd /d "C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude"
python bull_div_boost_tracker.py report > bull_div_boost_report_run.log 2>&1
REM Optional: email the report (uncomment if email script exists)
REM python send_email.py --subject "BullDvg Boost 12mo Report" --body bull_div_boost_report.txt
