"""LAG P1 gate (lag_rating_filter: 8L rating <=3 as-of, auto-exclude >=4) replayed on both legs.

Only HDG/DIH matter (the only tickers whose route moves). HDG is in the LAG PEAD candidate pool
(data/lag_dnpr_pool.csv) 22 times; DIH never appears -> DIH's 5 gate flips cannot reach the LAG book.
As-of key = Release_Date of the pool quarter, exactly what lag_filter_low_rating passes as `asof`.
"""
import pandas as pd, os, json

WC = "/home/trido/thanhdt/WorkingClaude"
c = pd.read_csv(os.path.join(WC, "data/rating_8l_history.csv"))
n = pd.read_csv("r8l_hist_EXP_icbpit_v2.csv")
for d in (c, n):
    d["eff_date"] = pd.to_datetime(d["eff_date"])

def asof_rating(df, tk, when):
    s = df[(df.ticker == tk) & (df.eff_date <= when)].sort_values(["eff_date", "q_time"])
    return None if s.empty else int(s.iloc[-1].rating)

pool = pd.read_csv(os.path.join(WC, "data/lag_dnpr_pool.csv"))
pool["Release_Date"] = pd.to_datetime(pool["Release_Date"])
rows = []
for _, r in pool[pool.ticker.isin(["HDG", "DIH"])].sort_values("Release_Date").iterrows():
    rc, rn = asof_rating(c, r.ticker, r.Release_Date), asof_rating(n, r.ticker, r.Release_Date)
    # gate semantics: must HAVE a rating <=3; missing = excluded (fail-closed)
    gc = (rc is not None and rc <= 3)
    gn = (rn is not None and rn <= 3)
    rows.append({"ticker": r.ticker, "quarter": r.quarter, "release": str(r.Release_Date.date()),
                 "split": r.year and r["win"], "ctl_rating": rc, "new_rating": rn,
                 "ctl_ADMIT": gc, "new_ADMIT": gn, "FLIP": gc != gn,
                 "ret25_realized": round(float(r.ret25), 2)})
d = pd.DataFrame(rows)
print(d.to_string(index=False))
d.to_csv("lag_gate_ab.csv", index=False)
f = d[d.FLIP]
print(f"\nLAG pool quarters for changed tickers: {len(d)}  |  gate decision FLIPS: {len(f)}")
if len(f):
    print(f"  flips: {f.ctl_ADMIT.sum()} were ADMITTED under control and are now excluded, "
          f"{int((~f.ctl_ADMIT).sum())} were EXCLUDED and are now admitted")
    print(f"  realized ret25 of the newly-ADMITTED quarters: "
          f"mean {f[~f.ctl_ADMIT].ret25_realized.mean():.2f}%  "
          f"(n={int((~f.ctl_ADMIT).sum())} — far too small to infer edge, reported for disclosure only)")
    print(f"  split breakdown: {f['split'].value_counts().to_dict()}")
json.dump({"pool_quarters_changed_tickers": int(len(d)),
           "gate_flips": int(len(f)),
           "newly_admitted": int((~f.ctl_ADMIT).sum()) if len(f) else 0,
           "newly_excluded": int(f.ctl_ADMIT.sum()) if len(f) else 0,
           "flipped_quarters": f[["ticker", "quarter", "release", "ctl_rating", "new_rating",
                                  "ret25_realized"]].to_dict("records") if len(f) else []},
          open("lag_gate_summary.json", "w"), indent=1)
