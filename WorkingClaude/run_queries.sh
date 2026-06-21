#!/bin/bash
source ~/.bashrc 2>/dev/null
PROJECT=lithe-record-440915-m9

SQL_DIR="$(cygpath -u 'C:\\Users\\hotro\\OneDrive\\Pictures\\Documents\\WorkingClaude\\sql_queries')"

echo '=== Running BUY signal queries ==='
echo -n '  BKMA200 ... '
bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "$(cat '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_BKMA200.sql')" > '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_BKMA200.csv' 2>&1 && echo OK || echo FAILED
echo -n '  BullDvg ... '
bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "$(cat '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_BullDvg.sql')" > '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_BullDvg.csv' 2>&1 && echo OK || echo FAILED
echo -n '  BuySupport ... '
bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "$(cat '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_BuySupport.sql')" > '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_BuySupport.csv' 2>&1 && echo OK || echo FAILED
echo -n '  CashCowStock ... '
bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "$(cat '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_CashCowStock.sql')" > '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_CashCowStock.csv' 2>&1 && echo OK || echo FAILED
echo -n '  Conservative ... '
bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "$(cat '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_Conservative.sql')" > '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_Conservative.csv' 2>&1 && echo OK || echo FAILED
echo -n '  DividendYield ... '
bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "$(cat '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_DividendYield.sql')" > '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_DividendYield.csv' 2>&1 && echo OK || echo FAILED
echo -n '  RSILow30 ... '
bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "$(cat '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_RSILow30.sql')" > '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_RSILow30.csv' 2>&1 && echo OK || echo FAILED
echo -n '  SuperGrowth ... '
bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "$(cat '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_SuperGrowth.sql')" > '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_SuperGrowth.csv' 2>&1 && echo OK || echo FAILED
echo -n '  SurpriseEarning ... '
bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "$(cat '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_SurpriseEarning.sql')" > '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_SurpriseEarning.csv' 2>&1 && echo OK || echo FAILED
echo -n '  TL3M ... '
bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "$(cat '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_TL3M.sql')" > '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_TL3M.csv' 2>&1 && echo OK || echo FAILED
echo -n '  TradingValueMax ... '
bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "$(cat '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_TradingValueMax.sql')" > '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_TradingValueMax.csv' 2>&1 && echo OK || echo FAILED
echo -n '  TrendingGrowth ... '
bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "$(cat '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_TrendingGrowth.sql')" > '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_TrendingGrowth.csv' 2>&1 && echo OK || echo FAILED
echo -n '  UnderBV ... '
bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "$(cat '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_UnderBV.sql')" > '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_UnderBV.csv' 2>&1 && echo OK || echo FAILED
echo -n '  VolMax1Y ... '
bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "$(cat '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_VolMax1Y.sql')" > '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/buy_VolMax1Y.csv' 2>&1 && echo OK || echo FAILED

echo '=== Running SELL signal queries ==='
echo -n '  MA21 ... '
bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "$(cat '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/sell_MA21.sql')" > '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/sell_MA21.csv' 2>&1 && echo OK || echo FAILED
echo -n '  MA31 ... '
bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "$(cat '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/sell_MA31.sql')" > '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/sell_MA31.csv' 2>&1 && echo OK || echo FAILED
echo -n '  MA41 ... '
bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "$(cat '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/sell_MA41.sql')" > '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/sell_MA41.csv' 2>&1 && echo OK || echo FAILED
echo -n '  S13 ... '
bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "$(cat '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/sell_S13.sql')" > '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/sell_S13.csv' 2>&1 && echo OK || echo FAILED
echo -n '  SellBV ... '
bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "$(cat '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/sell_SellBV.sql')" > '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/sell_SellBV.csv' 2>&1 && echo OK || echo FAILED
echo -n '  SellBV2 ... '
bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "$(cat '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/sell_SellBV2.sql')" > '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/sell_SellBV2.csv' 2>&1 && echo OK || echo FAILED
echo -n '  SellPE ... '
bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "$(cat '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/sell_SellPE.sql')" > '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/sell_SellPE.csv' 2>&1 && echo OK || echo FAILED
echo -n '  SellResistance ... '
bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "$(cat '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/sell_SellResistance.sql')" > '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/sell_SellResistance.csv' 2>&1 && echo OK || echo FAILED
echo -n '  SellResistance1M ... '
bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "$(cat '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/sell_SellResistance1M.sql')" > '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/sell_SellResistance1M.csv' 2>&1 && echo OK || echo FAILED
echo -n '  SellResistance1Y ... '
bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "$(cat '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/sell_SellResistance1Y.sql')" > '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/sell_SellResistance1Y.csv' 2>&1 && echo OK || echo FAILED
echo -n '  BearDvg2 ... '
bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "$(cat '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/sell_BearDvg2.sql')" > '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/sell_BearDvg2.csv' 2>&1 && echo OK || echo FAILED
echo -n '  SellVolMax ... '
bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "$(cat '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/sell_SellVolMax.sql')" > '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/sell_SellVolMax.csv' 2>&1 && echo OK || echo FAILED

echo '=== Fetching Open prices ==='
echo -n '  Open prices for all tickers ... '
bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=20000000 "$(cat '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/open_prices.sql')" > '/c/Users/hotro/OneDrive/Pictures/Documents/WorkingClaude/sql_queries/open_prices.csv' 2>&1 && echo OK || echo FAILED
echo 'All queries done!'
