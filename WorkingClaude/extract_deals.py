#!/usr/bin/env python3
"""
extract_deals.py
================
Parse filter.json -> convert buy/sell rules to BigQuery SQL
-> query all signal dates -> match into deals -> save deals.csv

Execution model:
  Signal fires on Close[D] -> execute at Open[D+1]
"""

import json
import os
import re
import subprocess
import tempfile
from io import StringIO
from pathlib import Path

import pandas as pd

# ── CONFIG ────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(r"/home/trido/thanhdt/WorkingClaude")
FILTER_F   = BASE_DIR / "filter.json"
DICT_F     = BASE_DIR / "bigquery_dictionary.json"
OUT_CSV    = BASE_DIR / "data/deals.csv"
OUT_SUM    = BASE_DIR / "deals_summary.csv"

PROJECT    = "lithe-record-440915-m9"
BQ_BIN     = r"bq"
BQ_CHUNK   = 120
DATE_FROM  = "2020-01-01"
DATE_TO    = "2026-04-03"

# ── LOAD ──────────────────────────────────────────────────────────────────────
filters  = json.loads(FILTER_F.read_text(encoding="utf-8"))
bq_dict  = json.loads(DICT_F.read_text(encoding="utf-8"))

strategies = {}
for k, v in filters.items():
    if k.startswith("$"):
        name         = k[1:]
        sell_signals = [s.strip() for s in v.split(",")]
        buy_expr     = filters.get(f"_{name}", "")
        strategies[name] = {"buy_expr": buy_expr, "sell_signals": sell_signals}

sell_exprs = {k[1:]: v for k, v in filters.items() if k.startswith("~")}

print(f"Strategies  : {list(strategies.keys())}")
print(f"Sell signals: {list(sell_exprs.keys())}")

# ── SQL CONVERTER ─────────────────────────────────────────────────────────────
# Column names sorted longest-first to avoid partial substitution
COLS = sorted(
    [c for c in bq_dict.keys() if c not in {"ticker","time","quarter"}],
    key=len, reverse=True
)
CAST_COLS  = {"ICB_Code"}
INIT_SQL   = f"(t.time >= '{DATE_FROM}' AND t.time <= '{DATE_TO}')"

def expr_to_sql(expr: str) -> str:
    s = expr.strip()
    s = s.replace("{Init}", INIT_SQL)
    s = s.replace(" & ", " AND ")
    s = s.replace(" | ",  " OR ")
    s = s.replace("==",   "=")
    s = re.sub(r'\babs\(', 'ABS(', s)
    # Prefix columns with t.
    for col in COLS:
        pattern = r'(?<![.\w])' + re.escape(col) + r'(?!\w)'
        if col in CAST_COLS:
            repl = f'CAST(t.{col} AS STRING)'
        else:
            repl = f't.{col}'
        s = re.sub(pattern, repl, s)
    # Fix accidental double-prefix
    s = re.sub(r'\bt\.t\.', 't.', s)
    s = re.sub(r't\.CAST\(t\.', 'CAST(t.', s)
    return s

# ── BQ HELPER ─────────────────────────────────────────────────────────────────
def bq_query(sql: str, label: str = "") -> pd.DataFrame | None:
    # Write SQL to a temp file and pipe via stdin to avoid Windows arg-passing issues
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False,
                                     encoding='utf-8') as f:
        f.write(sql)
        tmppath = f.name
    try:
        # Use "type tmpfile | bq query" pattern to pass SQL via stdin on Windows
        bq_escaped = BQ_BIN.replace("\\", "\\\\")
        cmd_str = f'type "{tmppath}" | "{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=2000000'
        r = subprocess.run(cmd_str, capture_output=True, text=True,
                           timeout=300, shell=True)
    finally:
        try:
            os.unlink(tmppath)
        except OSError:
            pass
    if r.returncode != 0:
        print(f"  [BQ ERROR] {label}:\n    stdout: {r.stdout[:200]}\n    stderr: {r.stderr[:400]}")
        return None
    txt = r.stdout.strip()
    if not txt:
        return pd.DataFrame()
    try:
        return pd.read_csv(StringIO(txt))
    except Exception as e:
        print(f"  [PARSE ERROR] {label}: {e}")
        return None

# ── STEP 1: Buy signals ───────────────────────────────────────────────────────
print("\n=== Querying BUY signals ===")
buy_frames = []

for strat, info in strategies.items():
    expr = info["buy_expr"]
    if not expr:
        print(f"  {strat}: no buy expr — skip")
        continue
    sql_where = expr_to_sql(expr)
    sql = f"""
SELECT t.ticker, t.time AS signal_date
FROM tav2_bq.ticker AS t
WHERE {sql_where}
ORDER BY t.ticker, t.time
"""
    print(f"  {strat} ...", end=" ", flush=True)
    df = bq_query(sql, strat)
    if df is not None and len(df) > 0:
        df["strategy"]    = strat
        df["signal_date"] = pd.to_datetime(df["signal_date"])
        buy_frames.append(df)
        print(f"{len(df):,} signals")
    else:
        print("0 or error")

if not buy_frames:
    print("No buy signals. Exiting.")
    raise SystemExit(1)

buy_all = pd.concat(buy_frames, ignore_index=True)
print(f"\nTotal buy signals: {len(buy_all):,}")
print(buy_all.groupby("strategy").size().rename("count").to_string())

# ── STEP 2: Sell signals ──────────────────────────────────────────────────────
print("\n=== Querying SELL signals ===")
sell_frames = []

for sig_name, expr in sell_exprs.items():
    sql_where = expr_to_sql(expr)
    sql = f"""
SELECT t.ticker, t.time AS signal_date
FROM tav2_bq.ticker AS t
WHERE {sql_where}
  AND t.time >= '{DATE_FROM}' AND t.time <= '{DATE_TO}'
ORDER BY t.ticker, t.time
"""
    print(f"  {sig_name} ...", end=" ", flush=True)
    df = bq_query(sql, sig_name)
    if df is not None and len(df) > 0:
        df["signal_name"] = sig_name
        df["signal_date"] = pd.to_datetime(df["signal_date"])
        sell_frames.append(df)
        print(f"{len(df):,} signals")
    else:
        print("0 or error")

sell_all = (pd.concat(sell_frames, ignore_index=True)
            if sell_frames else
            pd.DataFrame(columns=["ticker","signal_date","signal_name"]))
print(f"\nTotal sell signals: {len(sell_all):,}")

# ── STEP 3: Open prices ───────────────────────────────────────────────────────
print("\n=== Fetching Open prices ===")
all_tickers = sorted(
    set(buy_all["ticker"].unique()) | set(sell_all["ticker"].unique())
)
n_chunks = -(-len(all_tickers) // BQ_CHUNK)
print(f"  {len(all_tickers)} tickers | {n_chunks} chunks")

price_frames = []
for i in range(0, len(all_tickers), BQ_CHUNK):
    chunk = all_tickers[i:i+BQ_CHUNK]
    tstr  = ", ".join(f'"{t}"' for t in chunk)
    sql   = f"""
SELECT t.ticker, t.time, t.Open
FROM tav2_bq.ticker AS t
WHERE t.ticker IN ({tstr})
  AND t.time >= '{DATE_FROM}' AND t.time <= '{DATE_TO}'
ORDER BY t.ticker, t.time
"""
    df = bq_query(sql, f"prices-{i//BQ_CHUNK+1}")
    if df is not None and len(df) > 0:
        price_frames.append(df)
    print(f"  chunk {i//BQ_CHUNK+1}/{n_chunks}: "
          f"{len(df) if df is not None else 0:,} rows")

prices = pd.concat(price_frames, ignore_index=True)
prices["time"] = pd.to_datetime(prices["time"])
prices.sort_values(["ticker","time"], inplace=True)
prices["Open_next"] = prices.groupby("ticker")["Open"].shift(-1)
prices["exec_date"] = prices.groupby("ticker")["time"].shift(-1)
price_lkp = prices.set_index(["ticker","time"])[["exec_date","Open_next"]]
print(f"  Total price rows: {len(prices):,}")

# ── STEP 4: Index sell signals ────────────────────────────────────────────────
sell_by_ticker: dict[str, list] = {}
if len(sell_all) > 0:
    for ticker, grp in sell_all.sort_values("signal_date").groupby("ticker"):
        sell_by_ticker[ticker] = list(zip(grp["signal_date"], grp["signal_name"]))

def find_first_sell(ticker, buy_date, valid_signals):
    for sd, sn in sell_by_ticker.get(ticker, []):
        if sd > buy_date and sn in valid_signals:
            return sd, sn
    return None, None

def get_exec(ticker, signal_date):
    try:
        row = price_lkp.loc[(ticker, signal_date)]
        return row["exec_date"], row["Open_next"]
    except KeyError:
        return None, None

# ── STEP 5: Match deals ───────────────────────────────────────────────────────
print("\n=== Matching deals ===")
deal_rows = []
buy_sorted = buy_all.sort_values(["strategy","ticker","signal_date"])

for strat, info in strategies.items():
    valid_sells = set(info["sell_signals"])
    strat_buys  = buy_sorted[buy_sorted["strategy"] == strat]
    for _, brow in strat_buys.iterrows():
        ticker  = brow["ticker"]
        buy_sig = brow["signal_date"]

        buy_exec, buy_open = get_exec(ticker, buy_sig)
        sell_sig, sell_name = find_first_sell(ticker, buy_sig, valid_sells)

        if sell_sig is not None:
            sell_exec, sell_open = get_exec(ticker, sell_sig)
            if (buy_open and sell_open
                    and not pd.isna(buy_open) and not pd.isna(sell_open)
                    and buy_open > 0 and sell_open > 0):
                pnl_pct     = (sell_open / buy_open - 1) * 100
                holding_cal = (sell_sig - buy_sig).days
                status      = "closed"
            else:
                pnl_pct = holding_cal = None
                sell_exec = sell_open = None
                status = "closed_no_price"
        else:
            sell_exec = sell_open = sell_name = None
            pnl_pct   = holding_cal = None
            status    = "open"

        deal_rows.append({
            "strategy":         strat,
            "ticker":           ticker,
            "buy_signal_date":  buy_sig,
            "buy_exec_date":    buy_exec,
            "buy_open":         buy_open,
            "sell_signal_date": sell_sig,
            "sell_exec_date":   sell_exec,
            "sell_open":        sell_open,
            "sell_signal_name": sell_name,
            "holding_days":     holding_cal,
            "pnl_pct":          pnl_pct,
            "status":           status,
        })

deals = pd.DataFrame(deal_rows)
deals.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
print(f"  {len(deals):,} deals -> {OUT_CSV}")

# ── STEP 6: Summary ───────────────────────────────────────────────────────────
print("\n=== Summary (2020-present, closed deals only) ===")
closed = deals[deals["status"] == "closed"].copy()

sum_rows = []
for strat in strategies.keys():
    sub = closed[closed["strategy"] == strat]
    if len(sub) == 0:
        continue
    wins     = sub["pnl_pct"] > 0
    n_open   = deals[(deals["strategy"]==strat) & (deals["status"]=="open")].shape[0]
    sum_rows.append({
        "strategy":      strat,
        "n_closed":      len(sub),
        "n_open":        n_open,
        "win_rate":      round(wins.mean()*100, 1),
        "avg_pnl":       round(sub["pnl_pct"].mean(), 2),
        "avg_win":       round(sub.loc[wins,  "pnl_pct"].mean(), 2) if wins.any()  else 0,
        "avg_loss":      round(sub.loc[~wins, "pnl_pct"].mean(), 2) if (~wins).any() else 0,
        "avg_hold_days": round(sub["holding_days"].mean(), 0),
        "max_win":       round(sub["pnl_pct"].max(), 2),
        "max_loss":      round(sub["pnl_pct"].min(), 2),
        "median_pnl":    round(sub["pnl_pct"].median(), 2),
    })

summary = pd.DataFrame(sum_rows).sort_values("avg_pnl", ascending=False)
summary.to_csv(OUT_SUM, index=False, encoding="utf-8-sig")

print(f"\n{'Strategy':<20} {'Cls':>5} {'Opn':>4} {'WR%':>6} "
      f"{'AvgPnl':>8} {'Median':>8} {'AvgWin':>8} {'AvgLoss':>9} "
      f"{'Hold':>5} {'MaxW':>8} {'MaxL':>8}")
print("-" * 100)
for _, r in summary.iterrows():
    print(f"{r['strategy']:<20} {int(r['n_closed']):>5} {int(r['n_open']):>4} "
          f"{r['win_rate']:>6.1f}% {r['avg_pnl']:>+7.2f}% "
          f"{r['median_pnl']:>+7.2f}% {r['avg_win']:>+7.2f}% "
          f"{r['avg_loss']:>+8.2f}% {int(r['avg_hold_days']):>4}d "
          f"{r['max_win']:>+7.2f}% {r['max_loss']:>+7.2f}%")

print(f"\nSummary -> {OUT_SUM}")
print(f"Deals   -> {OUT_CSV}")
