#!/usr/bin/env bash
# Tái lập hist_2y.csv (không commit — 8.466 dòng, gitignore): Close điều chỉnh 2 năm của các mã trong sổ
# kb/dd_price_zones.json, từ BQ tav2_bq.ticker (lịch sử, không phải giá cùng ngày). Cột: ticker,d,c,p (p = Price chưa điều chỉnh).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(git -C "$HERE" rev-parse --show-toplevel)"
TK="$(python3 -c "import json;print(','.join(sorted({\"'%s'\"%e['ticker'] for e in json.load(open('$ROOT/kb/dd_price_zones.json'))['entries']})))")"
# shellcheck disable=SC1091
. /home/trido/thanhdt/WorkingClaude/wc_env.sh
bq query --use_legacy_sql=false --format=csv --max_rows=100000 --project_id=lithe-record-440915-m9 \
  "SELECT t.ticker, CAST(t.time AS STRING) AS d, t.Close AS c, t.Price AS p FROM tav2_bq.ticker AS t
   WHERE t.ticker IN ($TK) AND t.time >= DATE '2024-10-30' AND t.time <= DATE '2026-10-30' ORDER BY 1,2" > "$HERE/hist_2y.csv"
wc -l "$HERE/hist_2y.csv"
