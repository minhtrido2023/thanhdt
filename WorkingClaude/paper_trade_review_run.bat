@echo off
REM One-time roster-cleanup review — scheduled for 2026-06-30 (Task: PaperTradeReview_0630).
REM Runs the quantitative keep/drop review for time-boxed sleeves (#6/#7/#10) + V6-v2 merge check.
REM Writes data\paper_trade_review.md (recommendation only — does NOT edit the live bat).
cd /d C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude
echo ===== paper-trade roster review %date% %time% ===== >> data\paper_trade_review_run.log
python paper_trade_review.py >> data\paper_trade_review_run.log 2>&1
echo ===== done %time% ===== >> data\paper_trade_review_run.log
