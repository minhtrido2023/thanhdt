"""Diagnostic (no full NAV harness): list events admitted ONLY via BULL-SUE relax, with
post_ret, state, breadth tercile, year -- to check independence (N episodes) and deal quality.
RESEARCH ONLY, reads same source files as pt_v23_lagbullsue.py, no writes to canonical data."""
import os, sys
import numpy as np, pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
import simulate_holistic_nav as shn
from simulate_holistic_nav import bq, VNI_QUERY

END_DATE = "2026-06-19"
cal_df = bq(VNI_QUERY.format(start="2013-06-01", end=END_DATE))
cal_df["time"] = pd.to_datetime(cal_df["time"])
all_dates = np.array(sorted(cal_df["time"].unique()), dtype="datetime64[ns]")

fin = pd.read_pickle("data/earnings_surprise_data.pkl")
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"]); FLOOR = 1e9
fin["exp_B_MA"] = fin[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)
fin["surprise_B_MA"] = ((fin["NP_P0"] - fin["exp_B_MA"]) / np.maximum(np.abs(fin["exp_B_MA"]), FLOOR)).clip(-5, 5)
ev_class = pd.read_csv("data/earnings_events_classified.csv", parse_dates=["Release_Date"])
ev = ev_class.merge(fin[["ticker","quarter","Release_Date","surprise_B_MA"]],
                    on=["ticker","quarter","Release_Date"], how="left")
ev = ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True)
ev["surprise_B_MA"] = ev["surprise_B_MA"].fillna(0)
LN2 = np.log(2); HL = 3.0
ev["prior_n_good"] = 0; ev["pa_HL3"] = np.nan
for tk, g in ev.groupby("ticker"):
    hist = []
    for ri in g.index.tolist():
        row = ev.loc[ri]; cur = row["Release_Date"]
        ev.at[ri, "prior_n_good"] = len(hist)
        if hist:
            da = pd.to_datetime([d for d, _ in hist]); pa = np.array([p for _, p in hist])
            w = np.exp(-LN2 * ((cur - da).days.values / 365.25) / HL)
            ev.at[ri, "pa_HL3"] = (pa * w).sum() / w.sum() if w.sum() > 0 else np.nan
        if pd.notna(row["NP_R"]) and row["NP_R"] >= 15 and pd.notna(row["post_ret"]):
            hist.append((cur, row["post_ret"]))

_qm = bq("SELECT f.ticker,f.quarter,f.NPM_P0,f.EBITM_P0 FROM tav2_bq.ticker_financial f WHERE f.quarter IS NOT NULL")
ev = ev.merge(_qm, on=["ticker","quarter"], how="left")
ev["_nonop"] = (ev["NPM_P0"] > 1.2 * ev["EBITM_P0"]) & ev["EBITM_P0"].notna()
_forx = {}
try:
    _ff = pd.read_csv("data/forensic_flags.csv")
    _forx = {r["ticker"]: pd.Timestamp(r["date"]) for _, r in _ff.iterrows() if str(r["severity"]).strip() == "exclude"}
except Exception: pass
ev["_forbid"] = [(tk in _forx) and (rd >= _forx[tk]) for tk, rd in zip(ev["ticker"], ev["Release_Date"])]

_m_base = (ev["NP_R"] >= 15) & (ev["prior_n_good"] >= 4) & (ev["pa_HL3"] >= 5) & ~ev["_nonop"].fillna(False)
_m_base &= ~ev["_forbid"]  # forensic ON by default in production

state_df = bq("SELECT s.time, s.state FROM tav2_bq.vnindex_5state_dt5g_live AS s WHERE s.time <= DATE '2026-06-19'")
state_df["time"] = pd.to_datetime(state_df["time"])
state_by_date = dict(zip(state_df["time"], state_df["state"]))

brdf = pd.read_csv(os.path.join(WORKDIR, "mike/agents/Taylor/research/strategy_regime_matrix_20260822/b2_breadth.csv"),
                    parse_dates=["time"]).sort_values("time").reset_index(drop=True)
bv = brdf["breadth"].to_numpy(); pc = np.full(len(bv), np.nan)
for i in range(252, len(bv)):
    pc[i] = (bv[i-252:i] < bv[i]).mean()
brdf["pct252"] = pc
brdf["btile"] = pd.cut(brdf["pct252"], [-0.001, 1/3, 2/3, 1.001], labels=["LOW","MID","HIGH"])
breadth_by_date = dict(zip(brdf["time"], brdf["btile"]))

def off(ref, o):
    pos = np.searchsorted(all_dates, np.datetime64(ref), side="right") - 1
    tgt = pos + o
    return pd.Timestamp(all_dates[tgt]) if 0 <= tgt < len(all_dates) else pd.NaT

ev["entry"] = ev["Release_Date"].apply(lambda d: off(d, 5))
ev["state_at_entry"] = ev["entry"].map(state_by_date)
ev["btile_at_entry"] = ev["entry"].map(breadth_by_date)
ev["bull_hi"] = ev["state_at_entry"].isin([4,5]) & (ev["btile_at_entry"] == "HIGH")

for thr in (12.0, 10.5):
    m_rel = (ev["NP_R"] >= thr) & (ev["prior_n_good"] >= 4) & (ev["pa_HL3"] >= 5) & ev["bull_hi"] & ~ev["_nonop"].fillna(False) & ~ev["_forbid"]
    new = ev[m_rel & ~_m_base].copy()
    print(f"\n=== thr={thr} : {len(new)} new events ===")
    if len(new):
        new["yr"] = new["Release_Date"].dt.year
        print(new.groupby("yr").size())
        print(new[["ticker","quarter","Release_Date","entry","NP_R","post_ret"]].sort_values("Release_Date").to_string(index=False))
        print(f"  mean post_ret NEW = {new['post_ret'].mean():.2f}%  median={new['post_ret'].median():.2f}%  win-rate(>0)={100*(new['post_ret']>0).mean():.1f}%")

base = ev[_m_base & ev["bull_hi"]].copy()
print(f"\n=== BASELINE events already in BULL+breadth-HIGH regime: {len(base)} ===")
if len(base):
    print(f"  mean post_ret BASE(bull_hi) = {base['post_ret'].mean():.2f}%  median={base['post_ret'].median():.2f}%  win-rate(>0)={100*(base['post_ret']>0).mean():.1f}%")
    base["yr"] = base["Release_Date"].dt.year
    print(base.groupby("yr").size())

print(f"\n=== ALL baseline events (any regime): {int(_m_base.sum())}, mean post_ret={ev.loc[_m_base,'post_ret'].mean():.2f}% ===")

# --- independent BULL+breadth-HIGH episode count (contiguous blocks in ev["entry"] calendar) ---
cal = pd.DataFrame({"time": all_dates})
cal["state"] = cal["time"].map(state_by_date)
cal["btile"] = cal["time"].map(breadth_by_date)
cal["bull_hi"] = cal["state"].isin([4,5]) & (cal["btile"] == "HIGH")
cal = cal[cal["time"] >= "2014-01-01"].reset_index(drop=True)
blk = (cal["bull_hi"] != cal["bull_hi"].shift(1)).cumsum()
eps = cal[cal["bull_hi"]].groupby(blk).agg(start=("time","min"), end=("time","max"), n=("time","size"))
eps["yr_start"] = eps["start"].dt.year
print(f"\n=== BULL+breadth-HIGH contiguous episodes 2014+: N={len(eps)} ===")
print(eps.to_string())
is_eps = eps[eps["start"] < "2020-01-01"]; oos_eps = eps[eps["start"] >= "2020-01-01"]
print(f"IS(<2020) episodes: {len(is_eps)}  OOS(>=2020) episodes: {len(oos_eps)}")
