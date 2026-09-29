#!/usr/bin/env python3
"""W2b step 2b — the DISCRETE branch point.

Step 2a showed the first TX difference (2014-02-06 for both vehicles) is a CONTINUOUS one: same
name set, same actions, shares differ by ~0.4%, and shares are FRACTIONAL (no lot rounding exists in
this engine). So the interesting event is the first session where the SET of (book,ticker,action)
differs -- a name traded in one leg and not in the other. That is where a smooth cash difference
crosses a discrete decision boundary. This script finds it and dumps what the engine was deciding.
"""
import os, sys, json
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from paired_w2 import leg_path

def load(p):
    df = pd.read_csv(p, low_memory=False)
    df["t"] = pd.to_datetime(df["ymd"], errors="coerce")
    return df

def keys(tx):
    return tx[["book", "ticker", "action"]].agg("|".join, axis=1)

def scan(tag_a, tag_b, nmax=4):
    a, b = load(leg_path(tag_a)), load(leg_path(tag_b))
    ta = a[a["record_type"] == "TX"].copy(); tb = b[b["record_type"] == "TX"].copy()
    ta["k"] = keys(ta); tb["k"] = keys(tb)
    da = a[a["record_type"] == "DAILY"].groupby("t").last()
    db = b[b["record_type"] == "DAILY"].groupby("t").last()
    days = sorted(set(ta["t"].dropna()) | set(tb["t"].dropna()))
    found, n_days_setdiff, tot = [], 0, 0
    for d in days:
        ka = set(ta.loc[ta["t"] == d, "k"]); kb = set(tb.loc[tb["t"] == d, "k"])
        if ka != kb:
            n_days_setdiff += 1
            if len(found) < nmax:
                ra = da.loc[d] if d in da.index else None
                rb = db.loc[d] if d in db.index else None
                onlya = sorted(ka - kb); onlyb = sorted(kb - ka)
                def det(tx, d, kk):
                    r = tx[(tx["t"] == d) & (tx["k"].isin(kk))]
                    return r[["k", "shares", "adj_price", "buy_amount", "sell_amount", "fee", "reason"]].to_dict("records")
                found.append({
                    "ymd": str(d.date()),
                    "state": float(ra["state"]) if ra is not None else None,
                    "n_tx": [int((ta["t"] == d).sum()), int((tb["t"] == d).sum())],
                    "cash_bal_a_minus_b": round(float(ra["bal_cash_ref"]) - float(rb["bal_cash_ref"]), 0),
                    "cash_lag_a_minus_b": round(float(ra["lag_cash_ref"]) - float(rb["lag_cash_ref"]), 0),
                    "nav_rel_diff_pct": round((float(ra["combined_nav"]) / float(rb["combined_nav"]) - 1) * 100, 4),
                    f"only_in_{tag_a}": det(ta, d, onlya),
                    f"only_in_{tag_b}": det(tb, d, onlyb),
                })
        tot += 1
    # how many TX rows differ in total, and how many are pure size vs set
    all_a = ta.groupby(["t", "k"])["shares"].sum(); all_b = tb.groupby(["t", "k"])["shares"].sum()
    j = pd.concat([all_a.rename("a"), all_b.rename("b")], axis=1)
    return {"legs": [tag_a, tag_b],
            "n_sessions_with_tx": tot,
            "n_sessions_with_NAME_SET_diff": n_days_setdiff,
            "n_tx_keys_only_in_a": int(j["b"].isna().sum()),
            "n_tx_keys_only_in_b": int(j["a"].isna().sum()),
            "n_tx_keys_shared_but_size_diff": int(((~j["a"].isna()) & (~j["b"].isna()) & (j["a"] != j["b"])).sum()),
            "n_tx_keys_total": int(len(j)),
            "shares_are_fractional": bool((ta["shares"].dropna() % 1 != 0).any()),
            "first_name_set_divergences": found}

if __name__ == "__main__":
    res = {"D": scan("w2d_baseline", "w2d_floor"), "A": scan("w2a_baseline", "w2a_floor")}
    json.dump(res, open(os.path.join(HERE, "w2b_trace2.json"), "w"), indent=1)
    for k, v in res.items():
        print("=====", k, {kk: vv for kk, vv in v.items() if kk != "first_name_set_divergences"})
        for f in v["first_name_set_divergences"]:
            print(json.dumps(f, indent=1, ensure_ascii=False))
