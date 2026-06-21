@echo off
REM 8L daily EOD orchestrator — refresh ranking + surprise-jump Telegram alert.
REM Schedule via Windows Task Scheduler ~17:45 on trading days (before the 18:00 V4 12.1 report, so rating_8l.csv is fresh for its R column).
REM Chain: rating_8l (credit-style quality 1-5 + top30 + buynow) -> unified_screener (merges rating) -> rank_8l -> dna_card (full-universe DNA cards for the bot) -> daily_alert -> cheap_pb_floor (rating x PB-floor x Ngu Hanh buy-now alert).
setlocal
set WORKDIR=C:\Users\hotro\OneDrive\Pictures\Documents\WorkingClaude
set TODAY=%date:~10,4%-%date:~4,2%-%date:~7,2%
set LOGFILE=%WORKDIR%\data\pt_8l_daily_%TODAY%.log
set PATH=%PATH%;C:\Users\hotro\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin
set CLOUDSDK_PYTHON=C:\Users\hotro\AppData\Local\Google\Cloud SDK\google-cloud-sdk\platform\bundledpython\python.exe
cd /d "%WORKDIR%"

echo ==================================================== > "%LOGFILE%"
echo 8L daily ranking + alert — %DATE% %TIME% >> "%LOGFILE%"
echo ==================================================== >> "%LOGFILE%"

echo [1/5] rating_8l.py  (credit-style quality rating 1-5, 7 routes -^> rating_8l.csv + top30 + buynow) >> "%LOGFILE%"
python rating_8l.py           >> "%LOGFILE%" 2>&1

echo [1b] screener_paper_diff.py  (OLD pb_z-only vs NEW composite zones -^> daily diff + sanity, go-live gate 2026-06-30) >> "%LOGFILE%"
python screener_paper_diff.py >> "%LOGFILE%" 2>&1

echo [2/5] unified_screener.py  (route + live valuation, 4 sector lenses, merges rating) >> "%LOGFILE%"
python unified_screener.py    >> "%LOGFILE%" 2>&1

echo [3/5] rank_8l.py  (composite score) >> "%LOGFILE%"
python rank_8l.py             >> "%LOGFILE%" 2>&1

echo [4/6] dna_card.py  (full-universe DNA cards -^> dna_cards.csv, feeds bot 2-block DNA block) >> "%LOGFILE%"
python dna_card.py            >> "%LOGFILE%" 2>&1

echo [4b] vn30_8l.py  (deployable 8L-VN30 basket: liq^>=10B top-30 EW -^> data/vn30_8l.csv, bot "vn30") >> "%LOGFILE%"
python vn30_8l.py             >> "%LOGFILE%" 2>&1

echo [5/6] rank_8l_daily_alert.py  (top-30 surprise-jump -^> Telegram) >> "%LOGFILE%"
python rank_8l_daily_alert.py >> "%LOGFILE%" 2>&1

echo [6/7] cheap_pb_floor.py  (rating x PB-floor x Ngu Hanh buy-now -^> Telegram) >> "%LOGFILE%"
python cheap_pb_floor.py      >> "%LOGFILE%" 2>&1

echo [7/7] snapshot rank_8l (dated, for bot "new"=mã mới vào top30 trong tuần) >> "%LOGFILE%"
python -c "import bot_8l_commands as b; print(b.snapshot_today())" >> "%LOGFILE%" 2>&1

echo Done %DATE% %TIME% >> "%LOGFILE%"
endlocal
