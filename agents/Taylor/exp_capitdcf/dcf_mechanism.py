# -*- coding: utf-8 -*-
"""Stage 1 — MECHANISM test: does point-in-time DCF margin-of-safety predict realized
return WITHIN a CAPIT washout basket? Within-event demeaning isolates name-selection
from event-timing (same methodology as data/capit_selection_study.py)."""
import os, sys, io, pickle
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
import dcf_valuation as D

pos = pd.read_csv("data/capit_selection_features.csv", parse_dates=["entry"])
print(f"holdings {len(pos)} | tickers {pos.ticker.nunique()} | events {pos.evidx.nunique()}")

# point-in-time DCF at ENTRY date, price = entry-day Close (already in the features file)
fin = D._load_financials()
rows = []
for _, r in pos.iterrows():
    px = r["Close"]
    try:
        res = D.fair_value(r["ticker"], r["entry"], price=(None if pd.isna(px) else float(px)), fin=fin)
    except Exception as e:
        res = {"ok": False, "reason": f"error:{e}"}
    mos = res.get("margin_of_safety") if res.get("ok") else np.nan
    rows.append({"holding_id": r["holding_id"], "mos": mos,
                 "ok": bool(res.get("ok")), "reason": res.get("reason")})
d = pos.merge(pd.DataFrame(rows), on="holding_id")
d["mos"] = pd.to_numeric(d["mos"], errors="coerce")
d["dcf_na"] = d["mos"].isna()

print("\n=== DCF computability on actual CAPIT holdings ===")
print(f"  computed : {(~d.dcf_na).sum()}/{len(d)} ({(~d.dcf_na).mean()*100:.0f}%)")
print("  N/A reasons:")
for k, v in d.loc[d.dcf_na, "reason"].fillna("?").value_counts().items():
    print(f"    {v:3d}  {k[:80]}")

# ---- within-event demeaned rank IC ----
def within_ic(df, col, retcol="ret"):
    ics, ns = [], []
    for ev, g in df.groupby("evidx"):
        g = g.dropna(subset=[col, retcol])
        if len(g) < 3 or g[col].nunique() < 2: continue
        ics.append(g[col].rank().corr(g[retcol].rank())); ns.append(len(g))
    ics = np.array(ics, float)
    if len(ics) == 0: return np.nan, np.nan, 0, 0
    t = ics.mean() / (ics.std(ddof=1) / np.sqrt(len(ics))) if len(ics) > 1 and ics.std(ddof=1) > 0 else np.nan
    return ics.mean(), t, len(ics), sum(ns)

print("\n=== Within-event rank IC vs realized return (higher = better predictor) ===")
print(f"{'axis':<16}{'IC':>8}{'t':>7}{'n_ev':>6}{'n_obs':>7}")
for col, lab in [("mos", "DCF MoS"), ("PB_z", "pb_z (raw)"), ("own_dd52", "own dd52")]:
    dd = d.copy()
    if col == "PB_z": dd["PB_z"] = -dd["PB_z"]   # cheaper (lower pbz) should predict higher ret
    ic, t, ne, no = within_ic(dd, col)
    print(f"{lab:<16}{ic:>8.3f}{t:>7.2f}{ne:>6}{no:>7}")

# ---- group comparison: RICH vs CHEAP vs N/A (the actual decision the filter makes) ----
print("\n=== Realized return by DCF bucket (within-event demeaned) ===")
d["ev_mean"] = d.groupby("evidx")["ret"].transform("mean")
d["ret_dm"] = d["ret"] - d["ev_mean"]
d["bucket"] = np.where(d.dcf_na, "N/A", np.where(d["mos"] > 0, "CHEAP(mos>0)", "RICH(mos<=0)"))
g = d.groupby("bucket").agg(n=("ret", "size"), ret_raw=("ret", "mean"), ret_dm=("ret_dm", "mean"),
                            med_dm=("ret_dm", "median"), winrate=("ret", lambda s: (s > 0).mean()))
print(g.round(4).to_string())

# bootstrap CI on RICH-vs-rest demeaned gap, resampling EVENTS (the true independent unit)
evs = d.evidx.unique(); rng = np.random.default_rng(7)
gaps = []
for _ in range(5000):
    s = d[d.evidx.isin(rng.choice(evs, len(evs), replace=True))]
    # note: sampling by event membership (approx; events resampled with replacement)
    r = s[s.bucket == "RICH(mos<=0)"]["ret_dm"]; o = s[s.bucket != "RICH(mos<=0)"]["ret_dm"]
    if len(r) >= 3 and len(o) >= 3: gaps.append(r.mean() - o.mean())
gaps = np.array(gaps)
print(f"\nRICH minus non-RICH (demeaned ret), event-bootstrap: "
      f"point={d[d.bucket=='RICH(mos<=0)']['ret_dm'].mean():+.4f} "
      f"CI95=[{np.percentile(gaps,2.5):+.4f},{np.percentile(gaps,97.5):+.4f}] "
      f"P(gap<0)={np.mean(gaps<0):.2f}")
d.to_csv("mike/agents/Taylor/exp_capitdcf/holdings_dcf.csv", index=False)
print("\nwrote mike/agents/Taylor/exp_capitdcf/holdings_dcf.csv")
