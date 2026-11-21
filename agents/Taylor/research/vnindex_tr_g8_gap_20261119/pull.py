"""Kéo panel BQ từ 2025-11-01 (đủ nền cho chuỗi 2026) qua fetch_bq() + MIN(time)/COUNT theo mã toàn
bảng `ticker`. Chỉ đọc; KHÔNG ghi data/benchmark/."""
import sys, os, datetime as dt, pickle
W = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-vnindex-tr-g8-gap-20261119/bin"
sys.path.insert(0, W)
import vnindex_total_return as v
sys.path.insert(0, v.WC_ROOT)
from corp_action_lib import TABLE, bq
inp = v.fetch_bq(dt.date(2025, 11, 3))
proj = TABLE.split(".")[0]
inp["first_seen"] = bq(f"SELECT t.ticker, CAST(MIN(t.time) AS STRING) first_time, COUNT(*) n, "
                       f"COUNTIF(t.OShares > 0) n_osh FROM `{proj}.tav2_bq.ticker` AS t GROUP BY t.ticker")
pickle.dump(inp, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bq_inputs_20251103.pkl"), "wb"))
print(len(inp["panel"]), len(inp["ca"]), inp["ca_max_ingested_utc"], len(inp["first_seen"]))
