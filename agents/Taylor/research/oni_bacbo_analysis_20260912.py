import pandas as pd
import numpy as np

# CANONICAL ONI source (per dispatch instruction): data/oni_index.csv, fetched directly from
# NOAA CPC oni.ascii.txt by oni_index_feed.py (job Taylor_20260912_081906), NOT the manual snapshot
# used in the original VSH/SJD memo section 3 (that snapshot is 95.7% identical anyway, verified).
oni_df = pd.read_csv("/home/trido/thanhdt/WorkingClaude/data/oni_index.csv")
oni_df = oni_df.rename(columns={"anom": "oni"})

season_end_month = {"DJF":2,"JFM":3,"FMA":4,"MAM":5,"AMJ":6,"MJJ":7,"JJA":8,
                     "JAS":9,"ASO":10,"SON":11,"OND":12,"NDJ":1}
oni_df["end_month"] = oni_df["season"].map(season_end_month)
oni_df["end_year"] = np.where(oni_df["season"] == "NDJ", oni_df["year"] + 1, oni_df["year"])
oni_df = oni_df.sort_values(["end_year", "end_month"]).reset_index(drop=True)

# Restrict to 2005-2025 window (same as original memo) to keep 2026 (post-cutoff, unverified
# independently) out of the confirmed-episode classification, per memo's §1.1 caveat.
oni_df = oni_df[(oni_df.end_year >= 2005) & (oni_df.end_year <= 2025)].reset_index(drop=True)

# CPC rule: episode = >=5 consecutive overlapping seasons with ONI >=0.5 (El Nino) or <=-0.5 (La Nina)
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

def oni_for_quarter(year, q, lag_seasons=0):
    target_month = q_end_month[q]
    row = oni_df[(oni_df.end_year == year) & (oni_df.end_month == target_month)]
    if row.empty:
        return None, None
    idx = row.index[0] - lag_seasons
    if idx < 0 or idx >= len(oni_df):
        return None, None
    r = oni_df.iloc[idx]
    return r["oni"], r["enso_confirmed"]

# Financials: VSH+SJD (Nam Trung Bo / Tay Nguyen, from original job) + TBC+HJS (Bac Bo, this job)
fin_orig = pd.read_csv("/tmp/hydro_financials.csv")
fin_new = pd.read_csv("/tmp/hydro_bacbo_financials.csv")
fin = pd.concat([fin_orig, fin_new], ignore_index=True)
fin["year"] = fin["quarter"].str[:4].astype(int)
fin["q"] = fin["quarter"].str[5:6].astype(int)
fin = fin.dropna(subset=["NP_R"])

results = []
for _, row in fin.iterrows():
    oni_c, phase_c = oni_for_quarter(row.year, row.q, lag_seasons=0)
    oni_l2, phase_l2 = oni_for_quarter(row.year, row.q, lag_seasons=2)
    results.append({**row.to_dict(), "oni_contemp": oni_c, "phase_contemp": phase_c,
                     "oni_lag2": oni_l2, "phase_lag2": phase_l2})
out = pd.DataFrame(results).dropna(subset=["oni_lag2"])
out.to_csv("/tmp/hydro_oni_merged_full.csv", index=False)

PHASE_LABEL = {1: "El Nino", -1: "La Nina", 0: "Neutral"}

print("=== BAC BO (TBC+HJS) group means: NP_R (YoY) by ENSO phase (lag=2Q) ===")
bacbo = out[out.ticker.isin(["TBC", "HJS"])]
print(bacbo.groupby("phase_lag2")["NP_R"].agg(["count", "mean", "median", "std"]).rename(index=PHASE_LABEL))

print()
print("=== BAC BO, Q3/Q4 only (peak wet-season quarters) ===")
bacbo_q34 = bacbo[bacbo.q.isin([3, 4])]
print(bacbo_q34.groupby("phase_lag2")["NP_R"].agg(["count", "mean", "median", "std"]).rename(index=PHASE_LABEL))

print()
print("=== REFERENCE: Nam Trung Bo/Tay Nguyen (VSH+SJD), same window/method ===")
ntbtn = out[out.ticker.isin(["VSH", "SJD"])]
print(ntbtn.groupby("phase_lag2")["NP_R"].agg(["count", "mean", "median", "std"]).rename(index=PHASE_LABEL))

print()
print("=== Per-ticker breakdown (Bac Bo) ===")
for t in ["TBC", "HJS"]:
    sub = out[out.ticker == t]
    print(f"-- {t} (n rows={len(sub)}, quarter range {sub.quarter.min()}..{sub.quarter.max()}) --")
    print(sub.groupby("phase_lag2")["NP_R"].agg(["count", "mean", "median"]).rename(index=PHASE_LABEL))

print()
print("=== Event-level (N=independent episodes) for Bac Bo ===")
ep = oni_df[oni_df.enso_confirmed != 0].copy()
ep["event_id"] = (ep.enso_confirmed != ep.enso_confirmed.shift()).cumsum()
events = ep.groupby("event_id").agg(phase=("enso_confirmed", "first"),
                                      start=("season", "first"), end=("season", "last"),
                                      start_year=("end_year", "first"), end_year=("end_year", "last"),
                                      n_seasons=("season", "count"), peak_oni=("oni", lambda s: s.abs().max()))
events["phase"] = events["phase"].map(PHASE_LABEL)
print(events.to_string())

oni_df["event_id"] = np.nan
oni_df.loc[ep.index, "event_id"] = ep["event_id"]

def event_for_quarter(year, q, lag_seasons=2):
    target_month = q_end_month[q]
    row = oni_df[(oni_df.end_year == year) & (oni_df.end_month == target_month)]
    if row.empty:
        return None
    idx = row.index[0] - lag_seasons
    if idx < 0 or idx >= len(oni_df):
        return None
    return oni_df.iloc[idx]["event_id"]

out["event_id"] = out.apply(lambda r: event_for_quarter(int(r.year), int(r.q)), axis=1)
bacbo2 = out[out.ticker.isin(["TBC", "HJS"])].dropna(subset=["event_id"])
per_event = bacbo2.groupby("event_id").agg(phase=("phase_lag2", "first"),
                                             n_qtrs=("NP_R", "count"),
                                             median_NP_R=("NP_R", "median"))
per_event["phase"] = per_event["phase"].map(PHASE_LABEL)
print(per_event.to_string())
print()
print("Bac Bo event-level median NP_R by phase:")
print(per_event.groupby("phase")["median_NP_R"].agg(["count", "mean", "median"]))

print()
print("=== Cross-check: how many El Nino/La Nina episodes have data coverage for BOTH region groups? ===")
ntbtn2 = out[out.ticker.isin(["VSH", "SJD"])].dropna(subset=["event_id"])
per_event_ntb = ntbtn2.groupby("event_id").agg(phase=("phase_lag2", "first"), median_NP_R=("NP_R", "median"))
common = set(per_event.index) & set(per_event_ntb.index)
print(f"Bac Bo events: {sorted(per_event.index)}")
print(f"NTB/TN events: {sorted(per_event_ntb.index)}")
print(f"Common event_ids: {sorted(common)}")
for eid in sorted(common):
    print(f"event {eid}: phase={per_event.loc[eid,'phase']} BacBo_median={per_event.loc[eid,'median_NP_R']:.3f} NTB_TN_median={per_event_ntb.loc[eid,'median_NP_R']:.3f}")
