@echo off
REM Wrapper for Windows Task Scheduler — runs paper-trade simulator daily
REM Outputs go to paper_trade_log.txt in workdir
cd /d "C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude"
python paper_trade_daily.py >> paper_trade_cron.log 2>&1
