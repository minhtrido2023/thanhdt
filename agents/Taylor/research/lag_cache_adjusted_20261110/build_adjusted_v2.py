# -*- coding: utf-8 -*-
"""Vòng 2 (job Taylor_20261110_132044): dựng lại pkl điều chỉnh bằng code vòng 2 (có cột Price THÔ, FOR SYSTEM_TIME
AS OF một mốc, known_carried). Ghi v2/ (non-canonical). Lưu pull thô v2/bq_live_adjusted_v2_*.parquet (tái lập).
Chạy: source wc_env.sh; $DNA_PYEXE build_adjusted_v2.py"""
import os, sys, pickle, hashlib, json
import pandas as pd
WT = "/home/trido/thanhdt/wt-lagadj-1110/WorkingClaude"; W = "/home/trido/thanhdt/WorkingClaude"
R = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, WT); sys.path.insert(0, W)
from simulate_holistic_nav import bq
import lagged_cache_adjusted as L
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
CPX, COV = f"{W}/data/earnings_px.pkl", f"{W}/data/lagged_pos_ov.pkl"
px = pd.read_pickle(CPX); ov = pd.read_pickle(COV); end = pd.to_datetime(px.time).max()
known = set(pd.read_csv(f"{R}/carried_tickers.csv").ticker)
asof = L.new_asof(); live = L.live_bq(bq); store = []
def q(sql):
    d = live(sql); store.append(d); return d
npx, nov, probs, stats, carried = L.build(q, px, ov, end, known_carried=known, asof=asof)
raw_p = f"{R}/v2/bq_live_adjusted_v2_2011-01-04_{end.date()}.parquet"
pd.concat(store, ignore_index=True).to_parquet(raw_p, index=False)
print("problems:", probs); print("stats:", stats)
for o, p in [(npx, f"{R}/v2/earnings_px_adj.pkl"), (nov, f"{R}/v2/lagged_pos_ov_adj.pkl")]:
    with open(p, "wb") as f: pickle.dump(o, f)
# so với v1 (cùng END): Close/Open/Volume_3M_P50 phải y hệt nếu BQ không đổi trong ~1h
o1x = pd.read_pickle(f"{R}/earnings_px_adj.pkl"); o1o = pd.read_pickle(f"{R}/lagged_pos_ov_adj.pkl")
mx = o1x.merge(npx, on=["ticker", "time"], how="outer", indicator=True, suffixes=("_1", "_2"))
mo = o1o.merge(nov, on=["ticker", "time"], how="outer", indicator=True, suffixes=("_1", "_2"))
rep = {"asof": str(asof), "end": str(end.date()), "canonical_px": md5(CPX), "canonical_ov": md5(COV), "raw_pull_v2": md5(raw_p),
       "earnings_px_adj_v2": md5(f"{R}/v2/earnings_px_adj.pkl"), "lagged_pos_ov_adj_v2": md5(f"{R}/v2/lagged_pos_ov_adj.pkl"),
       "rows_v1": len(o1x), "rows_v2": len(npx), "key_only_v1": int((mx._merge == "left_only").sum()), "key_only_v2": int((mx._merge == "right_only").sum()),
       "close_diff_rows": int(((mx.Close_1 - mx.Close_2).abs() > 1e-6).sum()), "open_diff_rows": int(((mo.Open_1 - mo.Open_2).abs() > 1e-6).sum()),
       "vol_diff_rows": int(((mo.Volume_3M_P50_1 - mo.Volume_3M_P50_2).abs() > 1e-6).sum()),
       "price_ne_close_share": float((nov.Price != npx.set_index(['ticker','time']).Close.reindex(pd.MultiIndex.from_frame(nov[['ticker','time']])).values).mean()),
       "validate_problems": probs, "stats": stats}
json.dump(rep, open(f"{R}/v2/build_manifest_v2.json", "w"), indent=1, ensure_ascii=False, default=str); print(json.dumps(rep, indent=1, ensure_ascii=False, default=str))
