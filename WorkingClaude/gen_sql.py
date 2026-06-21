"""
gen_sql.py - Phase 1: Generate SQL queries and write them to files.
Also write a bash script that runs them all and saves CSVs.
"""
import json
import os
import re

WORKDIR   = r"/home/trido/thanhdt/WorkingClaude"
SQL_DIR   = os.path.join(WORKDIR, "sql_queries")
os.makedirs(SQL_DIR, exist_ok=True)

FILTER_JSON = os.path.join(WORKDIR, "filter.json")
DICT_JSON   = os.path.join(WORKDIR, "bigquery_dictionary.json")
DATE_FROM   = "2020-01-01"
DATE_TO     = "2026-04-03"
PROJECT     = "lithe-record-440915-m9"

with open(FILTER_JSON, encoding="utf-8") as f:
    filters = json.load(f)
with open(DICT_JSON, encoding="utf-8") as f:
    bq_dict = json.load(f)

NON_COLUMNS = {"ticker", "time", "quarter"}
ALL_COLUMNS_SORTED = sorted(
    [k for k in bq_dict.keys() if k not in NON_COLUMNS],
    key=len, reverse=True
)
MISSING_COLS = {
    "Close_2Y_P90", "Dividend_Min3Y", "Dividend_1Y", "Dividend_3Y",
    "Inventory_P0", "LtInvest_P0", "StLiab_P0",
    "Trading_Value", "Trading_Value_1M_P50",
    "Trading_Value_Total_1W", "Trading_Value_Total_1W_Max6M",
    "Volume_Max1Y",
}

def remove_missing_col_conditions(expr: str) -> str:
    """Remove AND/OR (...missing_col...) conditions using balanced-paren parsing."""
    # Split on top-level AND/OR, remove groups containing missing cols
    # We do this by finding balanced paren groups and checking if they contain missing cols
    result_parts = []
    i = 0
    n = len(expr)
    # We'll tokenize the expression into: non-paren text + paren groups
    # Then filter out paren groups (with their preceding AND/OR) that reference missing cols
    tokens = []  # list of ('text', content) or ('group', content)
    pos = 0
    while pos < n:
        if expr[pos] == '(':
            # Find matching close paren (handle nesting)
            depth = 1
            j = pos + 1
            while j < n and depth > 0:
                if expr[j] == '(':
                    depth += 1
                elif expr[j] == ')':
                    depth -= 1
                j += 1
            tokens.append(('group', expr[pos:j]))
            pos = j
        else:
            # Find next open paren or end
            j = pos
            while j < n and expr[j] != '(':
                j += 1
            tokens.append(('text', expr[pos:j]))
            pos = j

    # Reconstruct, skipping groups that contain missing cols along with ONE adjacent AND/OR
    out_tokens = []
    for idx, (ttype, tcontent) in enumerate(tokens):
        if ttype == 'group':
            # Check if this group contains a missing col
            has_missing = any(
                re.search(r'\b' + re.escape(mc) + r'\b', tcontent)
                for mc in MISSING_COLS
            )
            if has_missing:
                # Prefer removing trailing AND/OR from previous text token
                removed = False
                if out_tokens and out_tokens[-1][0] == 'text':
                    prev = re.sub(r'\s*(AND|OR)\s*$', '', out_tokens[-1][1])
                    if prev != out_tokens[-1][1]:
                        out_tokens[-1] = ('text', prev)
                        removed = True
                # If nothing removed before, remove leading AND/OR from next
                if not removed:
                    next_idx = idx + 1
                    if next_idx < len(tokens) and tokens[next_idx][0] == 'text':
                        nxt = re.sub(r'^\s*(AND|OR)\s*', '', tokens[next_idx][1])
                        tokens[next_idx] = ('text', nxt)
                continue  # skip this group
        out_tokens.append((ttype, tcontent))

    return ''.join(t[1] for t in out_tokens)


def to_sql(expr: str) -> str:
    expr = expr.replace("{Init}", f"(t.time >= '{DATE_FROM}' AND t.time <= '{DATE_TO}')")
    expr = re.sub(r'\)\s*&\s*\(', ') AND (', expr)
    expr = re.sub(r'\)\s*\|\s*\(', ') OR (', expr)
    expr = expr.replace(" & ", " AND ").replace(" | ", " OR ")
    expr = re.sub(r'(?<![!<>=])&(?!=)', ' AND ', expr)
    expr = re.sub(r'(?<![!<>=])\|(?!=)', ' OR ', expr)
    expr = expr.replace("==", "=")
    expr = re.sub(
        r'abs\(([A-Za-z_][A-Za-z0-9_]*)\s*([><=!]+)\s*([0-9.]+)\)',
        lambda m: f'ABS({m.group(1)}) {m.group(2)} {m.group(3)}', expr
    )
    expr = expr.replace("abs(", "ABS(")
    # Remove conditions containing missing columns (balanced-paren approach, no backtracking)
    expr = remove_missing_col_conditions(expr)
    for col in ALL_COLUMNS_SORTED:
        expr = re.sub(r'(?<![.\w])' + re.escape(col) + r'(?!\w)', f't.{col}', expr)
    expr = re.sub(
        r't\.ICB_Code\s*(!=|=)\s*(\d+)',
        lambda m: f"CAST(t.ICB_Code AS STRING) {m.group(1)} '{m.group(2)}'",
        expr
    )
    expr = re.sub(
        r'/\s*(t\.[A-Za-z_][A-Za-z0-9_]*)',
        lambda m: f'/ NULLIF({m.group(1)}, 0)', expr
    )
    return expr.strip()

strategies    = {}
sell_signals  = {}
strategy_sells = {}
for key, val in filters.items():
    if key == "Init": continue
    elif key.startswith("$"): strategy_sells[key[1:]] = [s.strip() for s in val.split(",")]
    elif key.startswith("_"): strategies[key[1:]] = val
    elif key.startswith("~"): sell_signals[key[1:]] = val

used_sell_signals = set()
for slist in strategy_sells.values():
    used_sell_signals.update(slist)

# Write SQL files and build bash script
bash_lines = ["#!/bin/bash", "source ~/.bashrc 2>/dev/null", f"PROJECT={PROJECT}", ""]
bash_lines.append("SQL_DIR=\"$(cygpath -u 'C:\\\\Users\\\\hotro\\\\OneDrive\\\\Pictures\\\\Documents\\\\WorkingClaude\\\\sql_queries')\"")
bash_lines.append("")

# Buy signals
bash_lines.append("echo '=== Running BUY signal queries ==='")
for strat_name, raw_expr in strategies.items():
    sql_where = to_sql(raw_expr)
    sql = f"SELECT t.ticker, t.time FROM `tav2_bq.ticker` AS t WHERE {sql_where} ORDER BY t.ticker, t.time"
    sql_file = os.path.join(SQL_DIR, f"buy_{strat_name}.sql")
    csv_file = os.path.join(SQL_DIR, f"buy_{strat_name}.csv")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(sql)
    sql_bash = sql_file.replace("\\", "/").replace("C:", "/c")
    csv_bash = csv_file.replace("\\", "/").replace("C:", "/c")
    bash_lines.append(f"echo -n '  {strat_name} ... '")
    bash_lines.append(
        f"bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "
        f"\"$(cat '{sql_bash}')\" > '{csv_bash}' 2>&1 && echo OK || echo FAILED"
    )

# Sell signals
bash_lines.append("")
bash_lines.append("echo '=== Running SELL signal queries ==='")
for sig_name, raw_expr in sell_signals.items():
    if sig_name not in used_sell_signals:
        continue
    raw_with_date = f"{{Init}} & {raw_expr}"
    sql_where = to_sql(raw_with_date)
    sql = f"SELECT t.ticker, t.time FROM `tav2_bq.ticker` AS t WHERE {sql_where} ORDER BY t.ticker, t.time"
    sql_file = os.path.join(SQL_DIR, f"sell_{sig_name}.sql")
    csv_file = os.path.join(SQL_DIR, f"sell_{sig_name}.csv")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(sql)
    sql_bash = sql_file.replace("\\", "/").replace("C:", "/c")
    csv_bash = csv_file.replace("\\", "/").replace("C:", "/c")
    bash_lines.append(f"echo -n '  {sig_name} ... '")
    bash_lines.append(
        f"bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=2000000 "
        f"\"$(cat '{sql_bash}')\" > '{csv_bash}' 2>&1 && echo OK || echo FAILED"
    )

# Open prices - get all tickers from one query
bash_lines.append("")
bash_lines.append("echo '=== Fetching Open prices ==='")
open_sql = f"SELECT t.ticker, t.time, t.Open FROM `tav2_bq.ticker` AS t WHERE t.time >= '{DATE_FROM}' AND t.time <= '{DATE_TO}' ORDER BY t.ticker, t.time"
open_sql_file = os.path.join(SQL_DIR, "open_prices.sql")
open_csv_file = os.path.join(SQL_DIR, "open_prices.csv")
with open(open_sql_file, "w", encoding="utf-8") as f:
    f.write(open_sql)
open_sql_bash = open_sql_file.replace("\\", "/").replace("C:", "/c")
open_csv_bash = open_csv_file.replace("\\", "/").replace("C:", "/c")
bash_lines.append(f"echo -n '  Open prices for all tickers ... '")
bash_lines.append(
    f"bq query --use_legacy_sql=false --project_id=$PROJECT --format=csv --max_rows=20000000 "
    f"\"$(cat '{open_sql_bash}')\" > '{open_csv_bash}' 2>&1 && echo OK || echo FAILED"
)
bash_lines.append("echo 'All queries done!'")

# Write the bash script
bash_script = os.path.join(WORKDIR, "run_queries.sh")
with open(bash_script, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(bash_lines) + "\n")

# Write metadata for matching
meta = {
    "strategies": {k: to_sql(v) for k, v in strategies.items()},
    "sell_signals": {k: to_sql(f"{{Init}} & {v}") for k, v in sell_signals.items() if k in used_sell_signals},
    "strategy_sells": strategy_sells,
    "strat_names": list(strategies.keys()),
    "sell_sig_names": [k for k in sell_signals.keys() if k in used_sell_signals],
    "used_sell_signals": sorted(used_sell_signals),
}
import json as json2
with open(os.path.join(WORKDIR, "query_meta.json"), "w", encoding="utf-8") as f:
    json2.dump(meta, f, indent=2)

print(f"Generated {len(strategies)} buy SQL files and {len([s for s in sell_signals if s in used_sell_signals])} sell SQL files")
print(f"Bash script: {bash_script}")
print(f"Run with: bash run_queries.sh")
