# -*- coding: utf-8 -*-
"""anomaly_gate_prod_parity_selfcheck.py — D1 mở rộng (job Taylor_20260721_092529).

So bản inline trong deploy_golive_dt5g_v4/golive_recommend_v23.py (PRODUCTION) với bản
dùng chung anomaly_gate.anomaly_excluded trên MỌI phiên giao dịch trong 60 ngày gần nhất
(gồm cả ngày có cờ anomaly active lẫn ngày không cờ) — phải zero-diff thì refactor
"production gọi module chung" mới là refactor thuần tuý.

Read-only: KHÔNG sửa file nào, chỉ exec đúng nguyên văn thân hàm inline hiện tại.
"""
import io
import json
import os
import subprocess
import sys
from datetime import date, timedelta

import pandas as pd

W = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, W)
PROJECT = "lithe-record-440915-m9"

from anomaly_gate import anomaly_excluded as shared

# --- bản inline production, exec nguyên văn từ file (không copy tay) ---
src = open(os.path.join(W, "deploy_golive_dt5g_v4", "golive_recommend_v23.py"), encoding="utf-8").read()
body = src[src.index("def anomaly_excluded"):src.index("def capit_adv_caps")]
ns = {"os": os, "json": json, "pd": pd, "WORKDIR": W, "ANOMALY_TTL_DAYS": 30}
exec("from datetime import timedelta\n" + body, ns)
prod = ns["anomaly_excluded"]

# --- tập ngày: mọi phiên giao dịch trong 60 ngày gần nhất ---
o = subprocess.run(["bq", "query", "--use_legacy_sql=false", f"--project_id={PROJECT}",
                    "--format=csv", "--max_rows=200",
                    "SELECT time FROM tav2_bq.vnindex_5state_dt5g_live "
                    "ORDER BY time DESC LIMIT 60"], capture_output=True, text=True)
if o.returncode != 0:
    raise RuntimeError(o.stdout + o.stderr)
days = sorted(pd.read_csv(io.StringIO(o.stdout))["time"].astype(str))

flags = json.load(open(os.path.join(W, "data", "anomaly_flags.json"), encoding="utf-8"))
print(f"cờ hiện có: { {t: f['last_alert'] for t, f in flags.items()} }")

diffs, n_active, n_empty = [], 0, 0
for d in days:
    a, b = prod(d), shared(d)
    if a != b:
        diffs.append((d, sorted(a), sorted(b)))
    (n_active := n_active + 1) if a else (n_empty := n_empty + 1)

print(f"\nso sánh {len(days)} phiên ({days[0]} → {days[-1]})")
print(f"  ngày CÓ cờ active : {n_active}")
print(f"  ngày KHÔNG cờ     : {n_empty}")
print(f"  diff              : {len(diffs)}")
for d in diffs:
    print("   ", d)

ok = len(diffs) == 0 and len(days) >= 15 and n_active >= 1 and n_empty >= 1
print(("\nPASS — zero-diff, phủ cả 2 loại ngày" if ok else "\nFAIL"))
sys.exit(0 if ok else 1)
