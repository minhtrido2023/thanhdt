# Bull-commit breadth/liquidity check — job Taylor_20260710_163939
# Question: is the pending NEUTRAL->BULL DT4 commit (streak 9/10 as of 2026-07-09)
# confirmed by market breadth/liquidity, or an index-only narrow rally?
# Research only, no production code touched.
import numpy as np
import pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
BQC = f"{WC}/data/bq_cache"

# ── load prune universe ──────────────────────────────────────────────
import duckdb
tp = duckdb.sql(f"""
    SELECT CAST(time AS DATE) AS time, ticker, Close, Price, Volume,
           MA200, Trading_Value, VNINDEX
    FROM read_parquet('{BQC}/ticker_prune/*.parquet')
    WHERE time >= DATE '2013-01-01'
""").df()
tp["time"] = pd.to_datetime(tp["time"])
tp = tp.sort_values(["time", "ticker"])
print(f"prune rows {len(tp):,}  range {tp['time'].min().date()} → {tp['time'].max().date()}")

# daily metrics
g = tp.groupby("time")
n_names = g["ticker"].nunique()

# breadth: % Close > MA200 (causal same-day; guard >=100 names like macro layer)
ab = tp.dropna(subset=["Close", "MA200"])
br = ab.groupby("time").apply(lambda x: (x["Close"] > x["MA200"]).mean(), include_groups=False)
br = br.where(n_names.reindex(br.index) >= 100)

# trading value: prefer Trading_Value, fallback Price*Volume
tv = tp["Trading_Value"].where(tp["Trading_Value"] > 0, tp["Price"] * tp["Volume"])
tp2 = tp.assign(tv=tv)
tot_tv = tp2.groupby("time")["tv"].sum()
# CR5: top-5 share of daily trading value
cr5 = tp2.groupby("time")["tv"].apply(lambda x: x.nlargest(5).sum() / x.sum())

# pct of names up vs 60 sessions ago (per-ticker, session-aligned via pivot)
px = tp.pivot_table(index="time", columns="ticker", values="Close")
px60 = px.shift(60)
valid = px.notna() & px60.notna()
pct_up_3m = ((px > px60) & valid).sum(axis=1) / valid.sum(axis=1)
pct_up_3m = pct_up_3m.where(valid.sum(axis=1) >= 100)

# VNINDEX series (first per day) + 60-session return
vni = tp.groupby("time")["VNINDEX"].first()
vni_r60 = vni / vni.shift(60) - 1

# liquidity ratio: 20d avg total TV / trailing 252d median total TV
liq_ratio = tot_tv.rolling(20).mean() / tot_tv.rolling(252).median()
cr5_20 = cr5.rolling(20).mean()

M = pd.DataFrame(dict(breadth=br, pct_up_3m=pct_up_3m, vni_r60=vni_r60,
                      liq_ratio=liq_ratio, cr5_20=cr5_20, n=n_names)).sort_index()

# ── snapshots at historical NEUTRAL->BULL commits + now ──────────────
commits = ["2017-12-26", "2020-10-06", "2021-03-05", "2021-08-23",
           "2021-10-26", "2024-01-24", "2025-03-07", "2026-01-28"]
rows = []
idx = M.index
for d in commits + ["2026-07-09", "NOW_LATEST"]:
    dt = idx.max() if d.startswith("NOW") else pd.Timestamp(d)
    if dt not in idx:
        dt = idx[idx <= dt][-1]
    i = idx.get_loc(dt)
    r = M.iloc[i]
    br_60ago = M["breadth"].iloc[i - 60] if i >= 60 else np.nan
    rows.append(dict(event=d, date=str(dt.date()),
                     breadth=r["breadth"], breadth_60ago=br_60ago,
                     d_breadth=r["breadth"] - br_60ago,
                     pct_up_3m=r["pct_up_3m"], vni_r60=r["vni_r60"],
                     liq_ratio=r["liq_ratio"], cr5_20=r["cr5_20"], n=int(r["n"])))
T = pd.DataFrame(rows)
hist = T.iloc[:8]
print("\n=== NEUTRAL→BULL commits — breadth/liquidity at commit date ===")
print(T.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
print("\nhistorical min/median/max (8 commits):")
for c in ["breadth", "d_breadth", "pct_up_3m", "vni_r60", "liq_ratio", "cr5_20"]:
    print(f"  {c:>10}: min {hist[c].min():.3f}  med {hist[c].median():.3f}  "
          f"max {hist[c].max():.3f}   | NOW {T[c].iloc[-1]:.3f}")

# ── 6-month weekly series for the report ─────────────────────────────
six = M[M.index >= M.index.max() - pd.Timedelta(days=185)]
wk = six.resample("W-FRI").last().dropna(subset=["breadth"])
print("\n=== last 6 months, weekly (Fri close) ===")
print(wk[["breadth", "pct_up_3m", "vni_r60", "liq_ratio", "cr5_20"]]
      .to_string(float_format=lambda x: f"{x:.3f}"))
M.to_csv(f"{WC}/mike/agents/Taylor/data_bull_breadth_series.csv")
T.to_csv(f"{WC}/mike/agents/Taylor/data_bull_commit_snapshots.csv", index=False)

# ── counterfactual: base state had the EW leg NOT gone stale ─────────
# actual dual_v3 blend fell back to r_raw alone since 2026-06-22 (data/ ew_full
# stale at 06-19 while ew_v1 writes fresh output to WORKDIR root).
dv = pd.read_csv(f"{WC}/data/vnindex_5state_dual_v3_full.csv")
dv["time"] = pd.to_datetime(dv["time"])
ew = pd.read_csv(f"{WC}/vnindex_5state_ew_full.csv")[["time", "r_score"]]
ew["time"] = pd.to_datetime(ew["time"])
cf = dv.merge(ew.rename(columns={"r_score": "r_ew_fresh"}), on="time", how="left")
a = cf["alpha"].values
r_raw = cf["r_score_raw"].values
r_ewf = cf["r_ew_fresh"].values
r_dual = np.where(np.isnan(r_ewf), r_raw,
                  np.where(np.isnan(r_raw), r_ewf, a * r_raw + (1 - a) * r_ewf))
ema = np.full(len(cf), np.nan)
for t in range(len(cf)):
    v, prev = r_dual[t], (ema[t - 1] if t else np.nan)
    ema[t] = prev if np.isnan(v) else (v if np.isnan(prev) else 0.40 * v + 0.60 * prev)

def classify(rs):
    if np.isnan(rs): return 3
    return 1 if rs < .10 else 2 if rs < .20 else 3 if rs < .70 else 4 if rs < .90 else 5

cf["state_raw_cf"] = [classify(x) for x in ema]
cf["ema_cf"] = ema
# sanity: pre-06-20 counterfactual must match actual state_raw (same inputs)
pre = cf[(cf["time"] >= "2025-01-01") & (cf["time"] <= "2026-06-19")]
print(f"\n[selfcheck] counterfactual vs actual state_raw pre-staleness (2025-01→2026-06-19): "
      f"{(pre['state_raw_cf'] != pre['state_raw']).sum()} diffs / {len(pre)} rows")
recent = cf[cf["time"] >= "2026-06-15"][["time", "alpha", "r_score_raw", "r_ew_fresh",
                                         "ema_cf", "state_raw_cf", "state_raw", "state"]]
print("\n=== counterfactual (fresh EW leg) vs actual ===")
print(recent.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
