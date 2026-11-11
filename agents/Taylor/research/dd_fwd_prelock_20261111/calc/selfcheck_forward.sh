#!/usr/bin/env bash
# selfcheck score_dd_zones_forward.py: sổ GIẢ dd_date 2025-01-15 (10 mã, FPT có rev 1+2), cắt giá 2026-03-01.
# Kỳ vọng: 10 dòng, FPT giữ rev 2, TR_12 khớp tỉ số Close tra độc lập, N=24 insufficient, N=12 đủ.
set -euo pipefail
PY=${DNA_PYEXE:-/home/trido/thanhdt/wc_venv/bin/python}
HERE=$(cd "$(dirname "$0")" && pwd); TMP=$(mktemp -d)
"$PY" - "$TMP" <<'PYEOF'
import json, sys, duckdb
tks=['FPT','HPG','GAS','DGC','VGS','PVT','NT2','DRI','SAS','CSV']; c=duckdb.connect(); ents=[]
for i,t in enumerate(tks):
  p=c.execute(f"SELECT Price FROM read_parquet('/home/trido/thanhdt/WorkingClaude/data/bq_cache/ticker/*.parquet') WHERE ticker='{t}' AND time<=DATE '2025-01-15' ORDER BY time DESC LIMIT 1").fetchone()[0]
  ents.append({"ticker":t,"dd_date":"2025-01-15","rev":1,"price_ref":p,"price_date":"2025-01-15","center":p*(0.7+0.06*i),"center_kind":"point","zone_low":p*0.6,"zone_high":p*1.5})
  if i==0: ents.append(dict(ents[-1], rev=2, center=p*0.7))
json.dump({"entries":ents},open(sys.argv[1]+'/z.json','w'))
PYEOF
"$PY" -W ignore "$HERE/score_dd_zones_forward.py" --zones "$TMP/z.json" --out "$TMP/o" --asof 2026-03-01 >/dev/null
"$PY" - "$TMP" <<'PYEOF'
import sys, pandas as pd, duckdb
R=pd.read_csv(sys.argv[1]+'/o/dd_zones_forward_rows.csv'); assert len(R)==10, len(R)
assert (R[R.ticker=='FPT'].rev==2).all(); c=duckdb.connect()
P="read_parquet('/home/trido/thanhdt/WorkingClaude/data/bq_cache/ticker/*.parquet')"
for t in ['HPG','DGC']:
  q=c.execute(f"SELECT (SELECT Close FROM {P} WHERE ticker='{t}' AND time<=DATE '2026-01-15' ORDER BY time DESC LIMIT 1)/(SELECT Close FROM {P} WHERE ticker='{t}' AND time<=DATE '2025-01-15' ORDER BY time DESC LIMIT 1)").fetchone()[0]
  assert abs(q/R[R.ticker==t].TR_12.iloc[0]-1)<1e-12, t
assert R.insufficient_24.all() and not R.insufficient_12.any()
print("SELFCHECK PASS")
PYEOF
rm -rf "$TMP"
