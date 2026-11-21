"""Kéo panel BQ (time,ticker,Price,Close,OShares) + DIV từ 2026-05-01 qua đúng fetch_bq() của
vnindex_total_return.py; cache pickle. Chỉ đọc, không ghi data/benchmark/."""
import sys, os, datetime as dt, pickle
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/bin")
import vnindex_total_return as v
inp = v.fetch_bq(dt.date(2026, 5, 4))
pickle.dump(inp, open(os.path.join(os.path.dirname(__file__), "bq_inputs_20260504.pkl"), "wb"))
print(len(inp["panel"]), len(inp["ca"]), inp["ca_max_ingested_utc"])
