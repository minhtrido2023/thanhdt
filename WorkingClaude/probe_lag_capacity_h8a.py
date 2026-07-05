"""
H8a — LAG capacity tiebreaker audit (RESEARCH ONLY, no production touched).
Job Taylor_20260705_085949.

Q: Over 2014-2026, how often does the LAG book's 12-slot capacity actually BIND?
   (i.e. more names qualify+want-to-hold than the 12 slots allow) -> would a d_NPR
   tiebreaker ever fire? If bind < 10% of entry-days -> CLOSE (registry already says
   d_NPR = soft tiebreaker only, not hard filter; a rarely-binding cap => not worth coding).

Faithful to pt_v23_audit_2014.py [4] Building LAGGED schedule:
  - prodspec gate: NP_R>=15 & prior_n_good>=4 & pa_HL3>=5
  - prior_n_good / pa_HL3 rebuilt EXACTLY (LN2, HL=3.0, good = NP_R>=15 & post_ret notna)
  - entry = Release_Date + 5 trading sessions (offset on global calendar)
  - hold  = 25 sessions (audit metadata lag_signal_rule, line 1959); exit = entry + 25 sessions
  - SLOT LIMIT = 12 (registry: "capacity-constrained at 12 slots")
Forensic/non-op gates omitted (drop only a few human-flagged names; do not affect count materially;
the dispatch's stated gate is exactly NP_R>=15 & prior_n_good>=4 & pa_HL3>=5).
"""
import duckdb, numpy as np, pandas as pd

SLOT = 12
HOLD = 25
ENTRY_OFF = 5
WIN_START = pd.Timestamp("2014-01-01")
WIN_END   = pd.Timestamp("2026-06-15")

# --- trading calendar ---
con = duckdb.connect()
cal = con.execute("SELECT DISTINCT time FROM 'data/bq_cache/ticker/*.parquet' ORDER BY time").df()
all_dates = np.array(sorted(pd.to_datetime(cal["time"]).unique()), dtype="datetime64[ns]")

def offset_date(ref, off):
    pos = np.searchsorted(all_dates, np.datetime64(ref), side="right") - 1
    tgt = pos + off
    return pd.Timestamp(all_dates[tgt]) if 0 <= tgt < len(all_dates) else None

# --- events + rebuild prior_n_good / pa_HL3 exactly (pt_v23_audit_2014.py) ---
ev = pd.read_csv("data/earnings_events_classified.csv", parse_dates=["Release_Date"])
ev = ev.sort_values(["ticker", "Release_Date"]).reset_index(drop=True)
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

_m = (ev["NP_R"] >= 15) & (ev["prior_n_good"] >= 4) & (ev["pa_HL3"] >= 5)
e = ev[_m].copy()
print(f"prodspec-gated events (all-time): {len(e)}")

# --- entry/exit sessions in window ---
rows = []
for _, r in e.iterrows():
    entry = offset_date(r["Release_Date"], ENTRY_OFF)
    if entry is None or entry < WIN_START or entry > WIN_END:
        continue
    exit_ = offset_date(entry, HOLD)
    if exit_ is None:
        exit_ = pd.Timestamp(all_dates[-1])
    rows.append({"ticker": r["ticker"], "entry": entry, "exit": exit_})
sched = pd.DataFrame(rows).sort_values("entry").reset_index(drop=True)
print(f"LAG entries in window {WIN_START.date()}..{WIN_END.date()}: {len(sched)}")

# --- (1) LITERAL reading: new candidates per single entry-day > SLOT ---
per_day = sched.groupby("entry").size()
n_entry_days = len(per_day)
lit_bind = (per_day > SLOT).sum()
print(f"\n[1] LITERAL (new candidates on one entry-day > {SLOT}):")
print(f"    entry-days: {n_entry_days} | days with >{SLOT} new: {lit_bind} "
      f"({100*lit_bind/n_entry_days:.2f}%) | max new/day: {per_day.max()} | "
      f"days with >6: {(per_day>6).sum()} | 95th pct new/day: {per_day.quantile(0.95):.0f}")

# --- (2) MEANINGFUL reading: concurrent holdings (rolling 25-session) > SLOT ---
# For each entry event, count how many positions are already open on that entry day
# (entered earlier, not yet exited) + this one -> DEMAND. Capacity binds if demand > SLOT.
entries = sched["entry"].values.astype("datetime64[ns]")
exits   = sched["exit"].values.astype("datetime64[ns]")
demand_at_entry = []
for i in range(len(sched)):
    d = entries[i]
    # positions open at day d: entered <= d and exit > d (exclusive at exit day)
    open_now = np.sum((entries <= d) & (exits > d))
    demand_at_entry.append(open_now)
sched["concurrent"] = demand_at_entry
bind_events = (sched["concurrent"] > SLOT).sum()
print(f"\n[2] CONCURRENT holdings at each entry (demand vs {SLOT}-slot cap):")
print(f"    total entries: {len(sched)} | entries where concurrent>{SLOT}: {bind_events} "
      f"({100*bind_events/len(sched):.2f}%)")
print(f"    concurrent distribution: max={sched['concurrent'].max()} "
      f"mean={sched['concurrent'].mean():.1f} median={sched['concurrent'].median():.0f} "
      f"p90={sched['concurrent'].quantile(0.90):.0f} p95={sched['concurrent'].quantile(0.95):.0f} "
      f"p99={sched['concurrent'].quantile(0.99):.0f}")

# also: on ANY calendar day in window, peak concurrent holdings (daily grid)
grid = all_dates[(all_dates >= np.datetime64(WIN_START)) & (all_dates <= np.datetime64(WIN_END))]
daily_conc = np.array([np.sum((entries <= d) & (exits > d)) for d in grid])
over = np.sum(daily_conc > SLOT)
print(f"\n[2b] DAILY grid ({len(grid)} sessions): days holding >{SLOT} names: {over} "
      f"({100*over/len(grid):.2f}%) | peak concurrent: {daily_conc.max()} | "
      f"mean held: {daily_conc.mean():.1f}")

# year breakdown of concurrent demand
sched["yr"] = pd.to_datetime(sched["entry"]).dt.year
yb = sched.groupby("yr").agg(entries=("ticker","size"),
                             max_conc=("concurrent","max"),
                             bind=("concurrent", lambda s:(s>SLOT).sum()))
print("\n[year] entries / max_concurrent / bind(>12):")
print(yb.to_string())

verdict = "CLOSE" if (100*bind_events/len(sched) < 10 and 100*over/len(grid) < 10) else "PROPOSE_TIEBREAKER"
print(f"\nVERDICT (bind<10% => CLOSE): {verdict}")
