#!/usr/bin/env python3
"""W2b step 2 — WHY does a cash-only perturbation change the BAL trade set?
(quant-skeptic recommended_rerun #3; the question that decides whether any +-0.3pp A/B on this
engine is readable at all.)

Compares two legs that differ ONLY in the idle-cash carry rate: same universe, same signals, same
CAPIT events. Finds the FIRST session whose TX set differs, then dumps that session and the next 3.
Classifies each first-divergent order against the engine's quantisation rails.
"""
import os, sys, json
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from paired_w2 import leg_path

def load(path):
    df = pd.read_csv(path, low_memory=False)
    df["t"] = pd.to_datetime(df["ymd"], errors="coerce")
    return df

def tx_key(df):
    tx = df[df["record_type"] == "TX"].copy()
    return tx

def first_div(a, b, cols):
    """First session where the multiset of (book,ticker,action,shares) differs."""
    ta, tb = tx_key(a), tx_key(b)
    days = sorted(set(ta["t"].dropna()) | set(tb["t"].dropna()))
    for d in days:
        sa = ta[ta["t"] == d][cols].round(6).astype(str).agg("|".join, axis=1).sort_values().tolist()
        sb = tb[tb["t"] == d][cols].round(6).astype(str).agg("|".join, axis=1).sort_values().tolist()
        if sa != sb:
            return d, sa, sb
    return None, None, None

def daily_row(df, d, cols):
    r = df[(df["record_type"] == "DAILY") & (df["t"] == d)]
    return r[cols].iloc[-1].to_dict() if len(r) else None

def report(tag_a, tag_b, label):
    a, b = load(leg_path(tag_a)), load(leg_path(tag_b))
    cols = ["book", "ticker", "action", "shares"]
    d, sa, sb = first_div(a, b, cols)
    out = {"label": label, "legs": [tag_a, tag_b], "first_tx_divergence": str(d.date()) if d is not None else None}
    dcols = ["bal_cash_ref", "bal_stocks_ref", "bal_etf_ref", "lag_cash_ref", "lag_stocks_ref",
             "lag_etf_ref", "nav_bal_ref", "nav_lag_ref", "combined_nav", "state", "w_lag_tgt"]
    # cash divergence starts earlier than trade divergence -- find that too
    da = a[a["record_type"] == "DAILY"].groupby("t").last()
    db = b[b["record_type"] == "DAILY"].groupby("t").last()
    ix = da.index.intersection(db.index)
    diff_cash = (da.loc[ix, "bal_cash_ref"].astype(float) - db.loc[ix, "bal_cash_ref"].astype(float)).abs()
    nz = diff_cash[diff_cash > 1.0]
    out["first_cash_divergence"] = str(nz.index[0].date()) if len(nz) else None
    if d is None:
        return out
    win = [x for x in sorted(set(da.index) | set(db.index)) if x >= d][:4]
    out["sessions"] = []
    for w in win:
        ra, rb = daily_row(a, w, dcols), daily_row(b, w, dcols)
        txa = tx_key(a); txb = tx_key(b)
        ea = txa[txa["t"] == w][["book", "ticker", "action", "shares", "adj_price", "buy_amount",
                                 "sell_amount", "fee", "reason"]]
        eb = txb[txb["t"] == w][["book", "ticker", "action", "shares", "adj_price", "buy_amount",
                                 "sell_amount", "fee", "reason"]]
        ka = set(ea[["book", "ticker", "action"]].agg("|".join, axis=1))
        kb = set(eb[["book", "ticker", "action"]].agg("|".join, axis=1))
        # per-key share comparison for the shared keys
        ma = ea.set_index(ea[["book", "ticker", "action"]].agg("|".join, axis=1))
        mb = eb.set_index(eb[["book", "ticker", "action"]].agg("|".join, axis=1))
        shared_diff = {}
        for k in sorted(ka & kb):
            va, vb = float(ma.loc[k, "shares"]) if np.ndim(ma.loc[k, "shares"]) == 0 else None, \
                     float(mb.loc[k, "shares"]) if np.ndim(mb.loc[k, "shares"]) == 0 else None
            if va is not None and vb is not None and va != vb:
                shared_diff[k] = [va, vb, round(vb - va, 2)]
        out["sessions"].append({
            "ymd": str(w.date()),
            "cash_bal_A_minus_B": round(float(ra["bal_cash_ref"]) - float(rb["bal_cash_ref"]), 1) if ra and rb else None,
            "nav_A_minus_B": round(float(ra["combined_nav"]) - float(rb["combined_nav"]), 1) if ra and rb else None,
            "state": (ra or {}).get("state"),
            "only_in_" + tag_a: sorted(ka - kb),
            "only_in_" + tag_b: sorted(kb - ka),
            "same_key_diff_shares": shared_diff,
            "n_tx": [len(ea), len(eb)],
        })
    return out

if __name__ == "__main__":
    res = [report("w2d_baseline", "w2d_floor", "D vehicle (park 0.0), tier1 vs tier2"),
           report("w2a_baseline", "w2a_floor", "A vehicle (custom30V park 0.3), tier1 vs tier2")]
    json.dump(res, open(os.path.join(HERE, "w2b_trace.json"), "w"), indent=1)
    print(json.dumps(res, indent=1, ensure_ascii=False))
