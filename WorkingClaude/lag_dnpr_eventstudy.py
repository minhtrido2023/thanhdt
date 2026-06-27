"""Step 1 — Event study: does earnings ACCELERATION (d_NPR>=0) improve the LAG/PEAD pool?

Tests the EXACT harness-traded LAG pool (NP_R>=15 & prior_n_good>=4 & pa_HL3>=5, forensic gate),
then splits each event by d_NPR sign and compares forward 25-session return, IS(<2020)/OOS(>=2020).

d_NPR (earnings acceleration, PIT, single-row vintage, percentage points):
  NP_R_cur   = (NP_P0/NP_P4 - 1)*100      (current-quarter YoY growth %)
  NP_R_prior = (NP_P1/NP_P5 - 1)*100      (prior-quarter YoY growth %)
  d_NPR      = NP_R_cur - NP_R_prior      (2nd derivative; >=0 = accelerating)
  guards: NP_P4>0 AND NP_P5>0 (positive base; else ratio meaningless -> NaN, event ungrouped)

Forward return = realized return over the harness hold: entry = Release_Date+5 sessions,
exit = entry+25 sessions, on each ticker's own adj-Close series (ticker_prune).

REJECT criterion (from dispatch): if Group A (d_NPR>=0) does NOT beat Group B (d_NPR<0) in OOS -> STOP.
"""
import os, sys, pickle
os.chdir("/home/trido/thanhdt/WorkingClaude")
import numpy as np, pandas as pd, duckdb

TP = "data/bq_cache/ticker_prune/*.parquet"
START, END = "2014-01-01", "2026-06-15"
c = duckdb.connect()

# ---- 1. Replicate the harness LAG gate (faithful to pt_v23_audit_2014.py [4]) ----
with open("data/earnings_surprise_data.pkl", "rb") as f: fin = pickle.load(f)
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
ev = pd.read_csv("data/earnings_events_classified.csv", parse_dates=["Release_Date"])
ev = ev.sort_values(["ticker", "Release_Date"]).reset_index(drop=True)
LN2, HL = np.log(2), 3.0
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
# forensic gate (drop human-flagged, date-aware) — matches harness default LAG_FORENSIC_GATE=1
_forx = {}
try:
    _ff = pd.read_csv("data/forensic_flags.csv")
    _forx = {r["ticker"]: pd.Timestamp(r["date"]) for _, r in _ff.iterrows() if str(r["severity"]).strip() == "exclude"}
except Exception: pass
ev["_forbid"] = [(tk in _forx) and (rd >= _forx[tk]) for tk, rd in zip(ev["ticker"], ev["Release_Date"])]
_m = (ev["NP_R"] >= 15) & (ev["prior_n_good"] >= 4) & (ev["pa_HL3"] >= 5) & (~ev["_forbid"])
pool = ev[_m].copy()
print(f"[gate] harness LAG pool (NP_R>=15 & prior_n_good>=4 & pa_HL3>=5, forensic): {len(pool)} events")

# ---- 2. Compute d_NPR (PIT) from fin NP_P columns, join onto pool by (ticker, quarter) ----
f4, f5 = fin["NP_P4"], fin["NP_P5"]
fin["NP_R_cur"]   = np.where(f4 > 0, (fin["NP_P0"]/f4 - 1)*100, np.nan)
fin["NP_R_prior"] = np.where(f5 > 0, (fin["NP_P1"]/f5 - 1)*100, np.nan)
fin["d_NPR"] = fin["NP_R_cur"] - fin["NP_R_prior"]
pool = pool.merge(fin[["ticker","quarter","d_NPR","NP_R_cur","NP_R_prior"]], on=["ticker","quarter"], how="left")
print(f"[d_NPR] computed: {pool['d_NPR'].notna().sum()}/{len(pool)} events have valid d_NPR "
      f"(NaN={pool['d_NPR'].isna().sum()} from non-positive base NP_P4/NP_P5)")

# ---- 3. Forward 25-session return on each ticker's own adj-Close (entry=Release+5, exit=+30) ----
tks = tuple(sorted(pool["ticker"].unique()))
px = c.execute(f"""SELECT ticker, time, Close, profit_1M FROM read_parquet('{TP}')
  WHERE time>=DATE '2013-06-01' AND time<=DATE '{END}' AND ticker IN {tks} AND Close IS NOT NULL
  ORDER BY ticker, time""").df()
px["time"] = pd.to_datetime(px["time"])
px_by_tk = {tk: g.reset_index(drop=True) for tk, g in px.groupby("ticker")}

def fwd_ret(tk, rd):
    g = px_by_tk.get(tk)
    if g is None: return (np.nan, np.nan)
    pos = g["time"].searchsorted(rd, side="right") - 1   # last trading day <= release
    ein, exo = pos + 5, pos + 30
    if pos < 0 or exo >= len(g): return (np.nan, np.nan)
    c_in, c_out = g["Close"].iloc[ein], g["Close"].iloc[exo]
    p1m = g["profit_1M"].iloc[ein]   # cross-check: harness-style T+20 fwd at entry
    if c_in and c_in > 0:
        return ((c_out/c_in - 1)*100, p1m)
    return (np.nan, p1m)

rr = pool.apply(lambda r: fwd_ret(r["ticker"], r["Release_Date"]), axis=1, result_type="expand")
pool["ret25"], pool["p1m"] = rr[0], rr[1]
pool["era"] = np.where(pool["Release_Date"] < "2020-01-01", "IS", "OOS")
pool = pool.dropna(subset=["ret25"]).copy()
print(f"[fwd] events with realized 25-session return: {len(pool)} "
      f"({(pool.era=='IS').sum()} IS / {(pool.era=='OOS').sum()} OOS)\n")

# ---- 4. Compare Group A (d_NPR>=0) vs Group B (d_NPR<0) ----
def stats(g):
    r = g["ret25"]
    sharpe = r.mean()/r.std()*np.sqrt(252/25) if len(g) > 2 and r.std() > 0 else np.nan
    return len(g), (r > 0).mean()*100, r.mean(), r.median(), sharpe

print(f"{'era':>4} {'group':>14} {'N':>5} {'win%':>6} {'mean25':>7} {'med25':>7} {'Sharpe':>7}")
res = {}
for era in ["IS", "OOS"]:
    e = pool[pool.era == era]
    for lbl, sub in [("A: d_NPR>=0", e[e.d_NPR >= 0]), ("B: d_NPR<0", e[e.d_NPR < 0]),
                     ("ALL(baseline)", e[e.d_NPR.notna()])]:
        n, win, mean, med, sh = stats(sub)
        res[(era, lbl)] = (n, win, mean, med, sh)
        print(f"{era:>4} {lbl:>14} {n:>5} {win:>5.0f}% {mean:>6.2f}% {med:>6.2f}% {sh:>7.2f}")
    a, b = res[(era,"A: d_NPR>=0")], res[(era,"B: d_NPR<0")]
    print(f"     -> {era} A-minus-B mean spread: {a[2]-b[2]:+.2f}pp | win {a[1]-b[1]:+.0f}pp | "
          f"A-vs-ALL: {a[2]-res[(era,'ALL(baseline)')][2]:+.2f}pp\n")

print("VERDICT RULE: PROCEED to harness only if Group A beats Group B in OOS (mean & ideally win-rate).")
print("If A does NOT beat B in OOS -> REJECT, do not run Step 2.")
