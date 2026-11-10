# -*- coding: utf-8 -*-
"""Dựng earnings_px / lagged_pos_ov ĐIỀU CHỈNH (NON-canonical) vào thư mục này, bằng ĐÚNG hàm
production `lagged_cache_adjusted.build` của nhánh feat/lag-cache-adjusted-20261110.
Chạy: source wc_env.sh; $DNA_PYEXE build_adjusted_pkls.py. END = max(time) pkl canonical.
Nguồn BQ sống được lưu ở data/bq_live_adjusted_*.parquet (lần sau đọc lại file này ⇒ tái lập).
Không ghi gì vào data/ canonical."""
import os, sys, pickle, hashlib, json
import pandas as pd
WT = "/home/trido/thanhdt/wt-lagadj-1110/WorkingClaude"
W = "/home/trido/thanhdt/WorkingClaude"
R = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WT); sys.path.insert(0, W)
from simulate_holistic_nav import bq
import lagged_cache_adjusted as L

md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
CPX, COV = f"{W}/data/earnings_px.pkl", f"{W}/data/lagged_pos_ov.pkl"
m0 = {"canonical_px": md5(CPX), "canonical_ov": md5(COV)}
px = pd.read_pickle(CPX); ov = pd.read_pickle(COV)
end = pd.to_datetime(px.time).max()
raw_p = f"{R}/data/bq_live_adjusted_2011-01-04_{end.date()}.parquet"
live = L.live_bq(bq)
if os.path.exists(raw_p):
    cached = pd.read_parquet(raw_p)
    def q(sql):   # phát lại đúng bản pull đã lưu (cắt theo năm như pull_adjusted)
        import re
        a, b = re.findall(r"DATE '([0-9-]+)'", sql)
        t = pd.to_datetime(cached.time)
        return cached[(t >= a) & (t <= b)]
else:
    store = []
    def q(sql):
        d = live(sql); store.append(d); return d
npx, nov, probs, stats, carried = L.build(q, px, ov, end)
if not os.path.exists(raw_p):
    pd.concat(store, ignore_index=True).to_parquet(raw_p, index=False)
print("validate problems:", probs); print("stats:", stats); print(carried.to_string())
for o, p in [(npx, f"{R}/earnings_px_adj.pkl"), (nov, f"{R}/lagged_pos_ov_adj.pkl")]:
    with open(p, "wb") as f: pickle.dump(o, f)
carried.to_csv(f"{R}/carried_tickers.csv", index=False)
assert md5(CPX) == m0["canonical_px"] and md5(COV) == m0["canonical_ov"], "canonical đổi trong lúc dựng!"
out = {**m0, "raw_pull": md5(raw_p), "earnings_px_adj": md5(f"{R}/earnings_px_adj.pkl"),
       "lagged_pos_ov_adj": md5(f"{R}/lagged_pos_ov_adj.pkl"), "end": str(end.date()),
       "rows_new": len(npx), "rows_old": len(px), "validate_problems": probs, "stats": stats}
json.dump(out, open(f"{R}/build_manifest.json", "w"), indent=1, ensure_ascii=False, default=str)
print(json.dumps(out, indent=1, ensure_ascii=False, default=str))
