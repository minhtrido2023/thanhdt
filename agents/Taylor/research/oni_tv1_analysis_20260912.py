import pandas as pd
import numpy as np

# CANONICAL ONI source (same as hydro_hydrology_oni_overlay_20260912.md §5/§9.2):
# data/oni_index.csv, fetched directly from NOAA CPC oni.ascii.txt by oni_index_feed.py.
oni_df = pd.read_csv("/home/trido/thanhdt/WorkingClaude/data/oni_index.csv")
oni_df = oni_df.rename(columns={"anom": "oni"})

season_end_month = {"DJF": 2, "JFM": 3, "FMA": 4, "MAM": 5, "AMJ": 6, "MJJ": 7, "JJA": 8,
                     "JAS": 9, "ASO": 10, "SON": 11, "OND": 12, "NDJ": 1}
oni_df["end_month"] = oni_df["season"].map(season_end_month)
oni_df["end_year"] = np.where(oni_df["season"] == "NDJ", oni_df["year"] + 1, oni_df["year"])
oni_df = oni_df.sort_values(["end_year", "end_month"]).reset_index(drop=True)

# Same window as original memo (2005-2025), excludes 2026 (post-cutoff, unverified independently).
oni_df = oni_df[(oni_df.end_year >= 2005) & (oni_df.end_year <= 2025)].reset_index(drop=True)

oni_df["phase_raw"] = np.where(oni_df.oni >= 0.5, 1, np.where(oni_df.oni <= -0.5, -1, 0))
phase = oni_df["phase_raw"].values.copy()
n = len(phase)
confirmed = np.zeros(n, dtype=int)
for target in (1, -1):
    run_start = None
    for i in range(n):
        if phase[i] == target:
            if run_start is None:
                run_start = i
        else:
            if run_start is not None and i - run_start >= 5:
                confirmed[run_start:i] = target
            run_start = None
    if run_start is not None and n - run_start >= 5:
        confirmed[run_start:n] = target
oni_df["enso_confirmed"] = confirmed

q_end_month = {1: 3, 2: 6, 3: 9, 4: 12}


def oni_for_quarter(year, q, lag_seasons=2):
    target_month = q_end_month[q]
    row = oni_df[(oni_df.end_year == year) & (oni_df.end_month == target_month)]
    if row.empty:
        return None, None
    idx = row.index[0] - lag_seasons
    if idx < 0 or idx >= len(oni_df):
        return None, None
    r = oni_df.iloc[idx]
    return r["oni"], r["enso_confirmed"]


fin = pd.read_csv("/tmp/tv1_financials.csv")
fin["year"] = fin["quarter"].str[:4].astype(int)
fin["q"] = fin["quarter"].str[5:6].astype(int)
fin = fin.dropna(subset=["NP_R"])

results = []
for _, row in fin.iterrows():
    oni_l2, phase_l2 = oni_for_quarter(row.year, row.q, lag_seasons=2)
    results.append({**row.to_dict(), "oni_lag2": oni_l2, "phase_lag2": phase_l2})
out = pd.DataFrame(results).dropna(subset=["oni_lag2"])
out.to_csv("/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/hydro_oni_tv1_panel_20260912.csv", index=False)

PHASE_LABEL = {1: "El Nino", -1: "La Nina", 0: "Neutral"}

# SB5 COD: to 1 (2012-12-28), to 2 (2013-07-19) -> full 57MW plant operating from 2013Q3 onward.
post_cod = out[out["time"] >= "2013-07-19"].copy()
pre_cod = out[out["time"] < "2013-07-19"].copy()

print("=== TV1 ALL QUARTERS (2010Q2-2026Q2), quarter-level pseudo-replicated ===")
print(out.groupby("phase_lag2")["NP_R"].agg(["count", "mean", "median", "std"]).rename(index=PHASE_LABEL))

print()
print(f"=== TV1 POST-COD only (>=2013Q3, N={len(post_cod)} quarters) ===")
print(post_cod.groupby("phase_lag2")["NP_R"].agg(["count", "mean", "median", "std"]).rename(index=PHASE_LABEL))

print()
print(f"=== TV1 PRE-COD only (<2013Q3, N={len(pre_cod)} quarters, hydro NOT yet operating -- sanity check) ===")
print(pre_cod.groupby("phase_lag2")["NP_R"].agg(["count", "mean", "median", "std"]).rename(index=PHASE_LABEL))

# Episode-level (independent events), same 5 El Nino + 4 La Nina episodes as memo §3.2,
# but only count an episode if TV1 has >=1 post-COD quarter observation inside it.
episodes = [
    ("2006-07", "El Nino", "2006-01-01", "2007-12-31"),
    ("2007-09", "La Nina", "2007-06-01", "2009-06-30"),
    ("2009-10", "El Nino", "2009-06-01", "2010-06-30"),
    ("2010-12", "La Nina", "2010-06-01", "2012-06-30"),
    ("2014-16", "El Nino", "2014-06-01", "2016-06-30"),
    ("2017-18", "La Nina", "2017-06-01", "2018-06-30"),
    ("2018-20", "El Nino", "2018-06-01", "2020-06-30"),
    ("2020-23", "La Nina", "2020-06-01", "2023-06-30"),
    ("2023-24", "El Nino", "2023-06-01", "2024-06-30"),
]

print()
print("=== TV1 episode-level median NP_R (post-COD quarters only, N=events with usable data) ===")
for label, phase, start, end in episodes:
    sub = post_cod[(post_cod["time"] >= start) & (post_cod["time"] <= end)]
    if len(sub) == 0:
        print(f"{label:10s} {phase:9s} N=0 (no post-COD quarter data in this episode window)")
    else:
        print(f"{label:10s} {phase:9s} N={len(sub)} quarters, median NP_R={sub['NP_R'].median():+.3f}, "
              f"individual={[round(x,2) for x in sub['NP_R'].tolist()]}")
