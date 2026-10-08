"""Capacity of positions started on slots 13+ (n_slots>=12 at FILL_START) vs slots 1-12: VND size at engine NAV
(50B total) and scaled to live 1B, as % of the ticker's 20-session median trading value (Price*Volume, raw PIT)."""
import pandas as pd, numpy as np, duckdb, sys
a = pd.read_csv(sys.argv[1], parse_dates=["ymd"]); a = a[(a.book == "v23audit_BAL") & (a.outcome == "FILL_START")]
tk = sorted(a.ticker.unique())
px = duckdb.sql(f"""SELECT ticker, CAST(time AS DATE) t, Price*Volume tv FROM read_parquet('/home/trido/thanhdt/WorkingClaude/data/bq_cache_asof20260729_postrestate/ticker/*.parquet')
 WHERE ticker IN ({','.join("'"+t+"'" for t in tk)}) AND time>='2013-10-01'""").df()
px["t"] = pd.to_datetime(px.t); px = px.sort_values(["ticker", "t"])
px["adv20"] = px.groupby("ticker").tv.transform(lambda s: s.shift(1).rolling(20, min_periods=10).median())
a = a.merge(px[["ticker", "t", "adv20"]], left_on=["ticker", "ymd"], right_on=["ticker", "t"], how="left")
a["slot"] = np.where(a.n_slots >= 12, "13+", "1-12")
for nav_scale, lab in [(1.0, "50B"), (1 / 50, "1B live")]:
    a["size"] = a.target * nav_scale; a["pct_adv"] = a["size"] / a.adv20
    g = a.groupby("slot").agg(n=("size", "size"), size_med_B=("size", lambda s: s.median() / 1e9), pct_adv_med=("pct_adv", "median"), pct_adv_p90=("pct_adv", lambda s: s.quantile(.9)))
    print(f"== NAV {lab}\n" + g.round(4).to_string())
