"""A/B of the custom30V PUBLISH path (the live money path) under the two rating vintages.

custom30_history.py -> cb.build_pit(gate_rating=3, ...) -> data/custom30v_8l_publish.csv ->
tav2_bq.custom30v_8l -> compute_park_trim.py. We call build_pit directly with the SAME arguments
custom30_history.py uses, so membership + reference weight are derived identically, but we NEVER
touch BQ (custom30_history.py's tail does `bq load` into the production table).

Cache: farms over data/bq_cache (the LIVE-ish 2026-09-25 sync — needed because the question is about
the rebalance currently IN FORCE, 2026-08-05, which is past the end of the pinned 07-29 snapshot),
with only fa_ratings_8l.parquet swapped between legs.
"""
import os, sys, json, hashlib
import pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(WC)
sys.path.insert(0, WC)

LEG = sys.argv[1]                      # ctl_anyvalue | new_icbpit
os.environ["BQ_LOCAL_CACHE"] = os.path.join(HERE, f"livecache_{LEG}")
os.environ["BQ_CACHE_THREADS"] = "1"
os.environ["BASKET_SELECT"] = "yieldcombo"     # custom30V, per papertrade_daily.sh step [6b]
os.environ["BASKET_WT"] = "namecap"
os.environ["TZ"] = "Asia/Ho_Chi_Minh"

from simulate_holistic_nav import bq
import custom_basket as cb

START, END = "2014-01-02", "2026-09-25"   # END pinned to the cache vintage, not detect_end_date()
print(f"[{LEG}] build_pit {START} -> {END}  cache={os.environ['BQ_LOCAL_CACHE']}", flush=True)
lvl, adv, memdf, bx = cb.build_pit(bq, START, END, quality="none", rebal="q2m5",
                                   gate_rating=3, weight_scheme="namecap")
memdf["rebal_date"] = pd.to_datetime(memdf["rebal_date"])
out = memdf.sort_values(["rebal_date", "liq_rank"])[
    [c for c in ("rebal_date", "ticker", "liq_rank", "rating", "weight") if c in memdf.columns]]
p = os.path.join(HERE, f"publish_{LEG}.csv")
out.to_csv(p, index=False)
print(f"[{LEG}] wrote {p}  rows={len(out)}  rebals={out.rebal_date.nunique()}  "
      f"md5={hashlib.md5(open(p,'rb').read()).hexdigest()}")
json.dump({"leg": LEG, "rows": int(len(out)), "rebals": int(out.rebal_date.nunique()),
           "md5": hashlib.md5(open(p, "rb").read()).hexdigest(),
           "cols": list(out.columns)}, open(os.path.join(HERE, f"publish_{LEG}.json"), "w"), indent=1)
