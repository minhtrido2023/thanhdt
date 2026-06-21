import json, re

DATE_FROM = "2020-01-01"
DATE_TO = "2026-04-03"

with open(r"/home/trido/thanhdt/WorkingClaude/bigquery_dictionary.json", encoding="utf-8") as f:
    bq_dict = json.load(f)
with open(r"/home/trido/thanhdt/WorkingClaude/filter.json", encoding="utf-8") as f:
    filters = json.load(f)

NON_COLUMNS = {"ticker", "time", "quarter"}
ALL_COLUMNS = [k for k in bq_dict.keys() if k not in NON_COLUMNS]
ALL_COLUMNS_SORTED = sorted(ALL_COLUMNS, key=len, reverse=True)

MISSING_COLS = {
    "Close_2Y_P90", "Dividend_Min3Y", "Inventory_P0", "LtInvest_P0", "StLiab_P0",
    "Trading_Value", "Trading_Value_1M_P50", "Trading_Value_Total_1W",
    "Trading_Value_Total_1W_Max6M", "Volume_Max1Y",
    "Dividend_1Y", "Dividend_3Y",
}

def to_sql(expr):
    expr = expr.replace("{Init}", f"(t.time >= '{DATE_FROM}' AND t.time <= '{DATE_TO}')")
    expr = re.sub(r'\)\s*&\s*\(', ') AND (', expr)
    expr = re.sub(r'\)\s*\|\s*\(', ') OR (', expr)
    expr = expr.replace(" & ", " AND ").replace(" | ", " OR ")
    expr = re.sub(r'(?<![!<>=])&(?!=)', ' AND ', expr)
    expr = re.sub(r'(?<![!<>=])\|(?!=)', ' OR ', expr)
    expr = expr.replace("==", "=")
    expr = re.sub(
        r'abs\(([A-Za-z_][A-Za-z0-9_]*)\s*([><=!]+)\s*([0-9.]+)\)',
        lambda m: f'ABS({m.group(1)}) {m.group(2)} {m.group(3)}',
        expr
    )
    expr = expr.replace("abs(", "ABS(")
    for mc in MISSING_COLS:
        pat1 = r'\s*(AND|OR)\s*\((?:[^()]*|\([^()]*\))*\b' + re.escape(mc) + r'\b(?:[^()]*|\([^()]*\))*\)'
        pat2 = r'\((?:[^()]*|\([^()]*\))*\b' + re.escape(mc) + r'\b(?:[^()]*|\([^()]*\))*\)\s*(AND|OR)\s*'
        expr = re.sub(pat1, '', expr)
        expr = re.sub(pat2, '', expr)
    for col in ALL_COLUMNS_SORTED:
        pattern = r'(?<![.\w])' + re.escape(col) + r'(?!\w)'
        expr = re.sub(pattern, f't.{col}', expr)
    expr = re.sub(
        r't\.ICB_Code\s*(!=|=)\s*(\d+)',
        lambda m: f"CAST(t.ICB_Code AS STRING) {m.group(1)} '{m.group(2)}'",
        expr
    )
    expr = re.sub(
        r'/\s*(t\.[A-Za-z_][A-Za-z0-9_]*)',
        lambda m: f'/ NULLIF({m.group(1)}, 0)',
        expr
    )
    return expr.strip()

# Check each filter for any remaining missing col references
ticker_cols_path = r"C:\Users\hotro\AppData\Local\Temp\ticker_cols.txt"
try:
    with open(ticker_cols_path, encoding="utf-8") as f:
        ticker_cols = set(f.read().splitlines())
except:
    print("Could not load ticker_cols.txt")
    ticker_cols = set()

print("=== BUY SIGNALS ===")
for key, raw in filters.items():
    if not key.startswith("_"):
        continue
    strat = key[1:]
    result = to_sql(raw)
    used = re.findall(r't\.([A-Za-z_][A-Za-z0-9_]*)', result)
    bad = [c for c in used if c not in ticker_cols]
    if bad:
        print(f"{strat}: BAD COLS: {sorted(set(bad))}")
        print(f"  SQL: {result[:200]}")
    else:
        print(f"{strat}: OK")

print("\n=== SELL signals ===")
for key, raw in filters.items():
    if not key.startswith("~"):
        continue
    sig = key[1:]
    raw2 = f"{{Init}} & {raw}"
    result = to_sql(raw2)
    used = re.findall(r't\.([A-Za-z_][A-Za-z0-9_]*)', result)
    bad = [c for c in used if c not in ticker_cols]
    if bad:
        print(f"{sig}: BAD COLS: {sorted(set(bad))}")
    else:
        print(f"{sig}: OK")
