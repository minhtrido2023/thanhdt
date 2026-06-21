#!/usr/bin/env python3
"""Debug script to print generated SQL and test BQ queries."""
import json
import re
import subprocess
from pathlib import Path

BASE_DIR = Path(r"/home/trido/thanhdt/WorkingClaude")
FILTER_F = BASE_DIR / "filter.json"
DICT_F   = BASE_DIR / "bigquery_dictionary.json"
PROJECT  = "lithe-record-440915-m9"
BQ_BIN   = r"bq"
DATE_FROM = "2020-01-01"
DATE_TO   = "2026-04-03"

filters = json.loads(FILTER_F.read_text(encoding="utf-8"))
bq_dict = json.loads(DICT_F.read_text(encoding="utf-8"))

COLS = sorted(
    [c for c in bq_dict.keys() if c not in {"ticker","time","quarter"}],
    key=len, reverse=True
)
CAST_COLS = {"ICB_Code"}
INIT_SQL  = f"(t.time >= '{DATE_FROM}' AND t.time <= '{DATE_TO}')"

def expr_to_sql(expr: str) -> str:
    s = expr.strip()
    s = s.replace("{Init}", INIT_SQL)
    s = s.replace(" & ", " AND ")
    s = s.replace(" | ",  " OR ")
    s = s.replace("==",   "=")
    s = re.sub(r'\babs\(', 'ABS(', s)
    for col in COLS:
        pattern = r'(?<![.\w])' + re.escape(col) + r'(?!\w)'
        if col in CAST_COLS:
            repl = f'CAST(t.{col} AS STRING)'
        else:
            repl = f't.{col}'
        s = re.sub(pattern, repl, s)
    s = re.sub(r'\bt\.t\.', 't.', s)
    s = re.sub(r't\.CAST\(t\.', 'CAST(t.', s)
    return s

# Test with RSILow30 first (simpler query)
test_strats = ["_RSILow30", "_TL3M", "_CashCowStock", "_TradingValueMax"]

for strat in test_strats:
    expr = filters.get(strat, "")
    if not expr:
        continue
    sql_where = expr_to_sql(expr)
    sql = f"""
SELECT t.ticker, t.time AS signal_date
FROM tav2_bq.ticker AS t
WHERE {sql_where}
ORDER BY t.ticker, t.time
LIMIT 5
"""
    print(f"\n{'='*60}")
    print(f"Strategy: {strat}")
    print(f"WHERE clause:\n{sql_where}")
    print(f"\nFull SQL:\n{sql}")

    # Run BQ
    cmd = [BQ_BIN, "query", "--use_legacy_sql=false",
           f"--project_id={PROJECT}", "--format=csv",
           "--max_rows=10", sql]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120, shell=True)
    print(f"\nReturn code: {r.returncode}")
    print(f"STDOUT: {repr(r.stdout[:500])}")
    print(f"STDERR: {repr(r.stderr[:1000])}")
    print()
