# -*- coding: utf-8 -*-
"""basket_picture.py — what each v4final arm actually HOLDS, and how much of it is financial.

Job Taylor_20260714_140127. Research-only; reads nothing production writes.

Answers the two dispatch questions that code inspection alone cannot:
  1. Does the 0.30 financial cap really hold quarter by quarter, on the REAL daily weight vector
     over the FULL 2014-2026 panel (the selfcheck only proved it on a 3y mechanism window)?
  2. What does each arm's basket look like at the 2026-05-05 rebal vs the 30 names custom30V holds
     live today?

Weights come from v4final_lib.daily_fin_weights' own re-derivation, NOT from custom_basket's
internals — same reason the selfcheck uses it: measuring the cap with the code under test would be
circular.
"""
import os
import sys

import numpy as np
import pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
from simulate_holistic_nav import bq  # noqa: E402
import custom_basket as cb  # noqa: E402
from v4final_lib import FIN_ROUTES, daily_fin_weights, route_asof  # noqa: E402

OUT = os.path.join(WORKDIR, "mike", "agents", "Taylor", "v4final_exp")
START, END = "2014-01-02", "2026-06-19"
PIT = dict(quality="none", rebal="q2m5", gate_rating=3, top_n=30, name_cap=0.10, qtilt=None)

ARMS = [
    ("A0_yieldcombo", "yieldcombo", "namecap", None),
    ("A1_eyfin",      "eyfin",      "namecap", None),
    ("A2_eyonly",     "eyonly",     "namecap", None),
    ("A3_eyonly_cap", "eyonly",     "fincap",  0.30),
]


def build(select, wt, fincap):
    saved = {k: os.environ.get(k) for k in ("BASKET_SELECT", "BASKET_FIN_CAP")}
    os.environ["BASKET_SELECT"] = select
    if fincap is not None:
        os.environ["BASKET_FIN_CAP"] = str(fincap)
    try:
        return cb.build_pit(bq, START, END, weight_scheme=wt, **PIT)
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


rows, baskets, summ = [], {}, []
for name, sel, wt, fincap in ARMS:
    print(f"\n===== {name} (select={sel} wt={wt} fincap={fincap}) =====")
    lvl, adv, mem, bx = build(sel, wt, fincap)
    fw = daily_fin_weights(bx, mem, name_cap=0.10, fin_cap=fincap)
    fw["time"] = pd.to_datetime(fw["time"])
    print(f"  financial weight: mean {fw.fin_w.mean():.3f} / median {fw.fin_w.median():.3f} / "
          f"max {fw.fin_w.max():.3f} / >30% on {(fw.fin_w > 0.3005).mean():.1%} of {len(fw)} days")
    summ.append({"arm": name, "fin_mean": fw.fin_w.mean(), "fin_med": fw.fin_w.median(),
                 "fin_max": fw.fin_w.max(), "days_over_30pct": float((fw.fin_w > 0.3005).mean()),
                 "n_days": len(fw)})
    q = fw.set_index("time").fin_w.groupby(pd.Grouper(freq="QE")).mean()
    for qq, v in q.items():
        rows.append({"arm": name, "quarter": str(qq.to_period("Q")), "fin_weight": v})

    # basket picture at the last rebal on/before 2026-05-05
    m = mem.copy()
    m["rebal_date"] = pd.to_datetime(m["rebal_date"])
    tgt = pd.Timestamp("2026-05-05")
    d0 = max(d for d in m.rebal_date.unique() if d <= tgt)
    sq = (pd.Timestamp(d0).to_period("Q").start_time - pd.Timedelta(days=1)).to_period("Q").start_time
    b = m[m.rebal_date == d0][["ticker"]].copy()
    b["route"] = [route_asof(t, sq) for t in b.ticker]
    b["is_fin"] = b.route.isin(FIN_ROUTES)
    baskets[name] = b.sort_values(["is_fin", "ticker"], ascending=[False, True]).reset_index(drop=True)
    print(f"  basket @ {pd.Timestamp(d0).date()}: {len(b)} names, financial {int(b.is_fin.sum())}/{len(b)}")

S = pd.DataFrame(summ)
Q = pd.DataFrame(rows).pivot(index="quarter", columns="arm", values="fin_weight")
Q.to_csv(os.path.join(OUT, "fin_weight_by_quarter.csv"))
S.to_csv(os.path.join(OUT, "fin_weight_summary.csv"), index=False)

print("\n" + "=" * 96)
print("FINANCIAL (BANK+INSURANCE+SECURITIES) DAILY WEIGHT — full 2014-2026 panel")
print("=" * 96)
print(S.round(3).to_string(index=False))
print("\nBY QUARTER (mean daily financial weight):")
print(Q.round(3).to_string())
print("\nworst quarter per arm:")
print(Q.max().round(3).to_string())

a0 = set(baskets["A0_yieldcombo"].ticker)
with open(os.path.join(OUT, "basket_20260505.md"), "w") as f:
    f.write("# v4final — basket @ 2026-05-05 rebal (job Taylor_20260714_140127)\n")
    for name in baskets:
        b = baskets[name]
        f.write(f"\n## {name} — {len(b)} names, financial {int(b.is_fin.sum())}/{len(b)}\n\n")
        f.write("| # | ticker | route | fin |\n|---|--------|-------|-----|\n")
        for i, r in enumerate(b.itertuples(), 1):
            f.write(f"| {i} | {r.ticker} | {r.route} | {'✓' if r.is_fin else ''} |\n")
    for name in baskets:
        if name == "A0_yieldcombo":
            continue
        s = set(baskets[name].ticker)
        f.write(f"\n### {name} vs A0_yieldcombo (live custom30V)\n\n")
        f.write(f"- kept: {len(a0 & s)}/{len(a0)}\n- IN: {sorted(s - a0)}\n- OUT: {sorted(a0 - s)}\n")

print("\n" + "=" * 96)
print("BASKET CHURN vs A0 = live custom30V @ 2026-05-05")
print("=" * 96)
for name in baskets:
    b = baskets[name]
    print(f"  {name:16s} fin {int(b.is_fin.sum()):2d}/{len(b)}")
    if name == "A0_yieldcombo":
        continue
    s = set(baskets[name].ticker)
    print(f"      kept {len(a0 & s)}/{len(a0)} | IN {sorted(s - a0)} | OUT {sorted(a0 - s)}")
print(f"\nartifacts: {OUT}/fin_weight_by_quarter.csv, fin_weight_summary.csv, basket_20260505.md")
