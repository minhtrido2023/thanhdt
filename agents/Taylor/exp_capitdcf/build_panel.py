# -*- coding: utf-8 -*-
"""PANEL A builder — point-in-time DCF MoS + pb_z on the FULL quality/liquidity-gated
CAPIT-eligible universe, at monthly observation dates 2014-2026.
(Quarterly/annual non-overlapping sub-samples are drawn from this panel downstream.)
No look-ahead: dcf_valuation.fair_value only reads ticker_financial.time <= asof.
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd, duckdb
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
import dcf_valuation as D

con = duckdb.connect(":memory:"); con.execute("SET threads=1")
PRUNE = f"read_parquet('{WORKDIR}/data/bq_cache/ticker_prune/*.parquet')"

# ---- trading calendar + monthly observation dates (first session of each month) ----
cal = con.execute(f"SELECT DISTINCT time FROM {PRUNE} WHERE time>=DATE '2014-01-01' ORDER BY 1").df()
cal["time"] = pd.to_datetime(cal["time"])
sessions = cal["time"].tolist()
obs_dates = cal.groupby(cal["time"].dt.to_period("M"))["time"].min().tolist()
print(f"sessions {len(sessions)} | monthly obs dates {len(obs_dates)} "
      f"({obs_dates[0].date()} -> {obs_dates[-1].date()})")

# ---- price panel for forward returns (adjusted Close) ----
px = con.execute(f"SELECT ticker, time, Close FROM {PRUNE}").df()
px["time"] = pd.to_datetime(px["time"])
P = px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index()

def fwd(tk, d, h):
    if tk not in P.columns: return np.nan
    s = P[tk].dropna(); s = s[s.index >= d]
    if len(s) < 2: return np.nan
    j = min(h, len(s) - 1)
    if j < h * 0.8: return np.nan          # truncated at panel end -> drop, don't bias
    return s.iloc[j] / s.iloc[0] - 1

# ---- eligible universe per obs date (production quality+liquidity gate, NO pb_z pre-filter) ----
fin = D._load_financials()
recs, n_dcf = [], 0
for i, d in enumerate(obs_dates):
    e = con.execute(f"""SELECT ticker, (PB-PB_MA5Y)/NULLIF(PB_SD5Y,0) pbz, COALESCE(Price,Close) px
FROM {PRUNE} WHERE time = DATE '{d.date()}' AND ROE_Min5Y>=0.12 AND ROIC5Y>=0.10 AND FSCORE>=6
  AND COALESCE(Price,Close)*Volume/1e9 >= 2""").df().dropna(subset=["pbz"])
    if len(e) < 3: continue
    for _, r in e.iterrows():
        try:
            res = D.fair_value(r.ticker, d, price=float(r.px), fin=fin)
            mos = res.get("margin_of_safety") if res.get("ok") else np.nan
        except Exception:
            mos = np.nan
        n_dcf += 1
        recs.append({"obs": d, "ticker": r.ticker, "pbz": float(r.pbz), "mos": mos,
                     **{f"r{h}": fwd(r.ticker, d, h) for h in (60, 250)}})
    if (i + 1) % 24 == 0:
        print(f"  ...{i+1}/{len(obs_dates)} obs dates, {n_dcf} DCF evals", flush=True)

X = pd.DataFrame(recs)
X["mos"] = pd.to_numeric(X["mos"], errors="coerce")
out = "mike/agents/Taylor/exp_capitdcf/panelA.csv"
X.to_csv(out, index=False)
print(f"\nwrote {out}: {len(X)} rows | {X.obs.nunique()} obs dates | "
      f"names/date median {X.groupby('obs').size().median():.0f} | "
      f"DCF computable {X.mos.notna().mean()*100:.0f}%")
