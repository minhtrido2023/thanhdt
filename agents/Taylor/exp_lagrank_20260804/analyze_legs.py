# -*- coding: utf-8 -*-
"""LAG forward-window ranking — leg analyser (job Taylor_20260804_051145).

For each audit CSV: portfolio metrics (FULL/IS/OOS + per-year) recomputed INDEPENDENTLY from the
DAILY combined_nav series, PLUS the LAG-book breadth numbers the dispatch asks for (question 3):
  N_entries  = number of LAG stock ENTRY events that actually got a first fill (holding_id level)
  N_tickers  = distinct names ever entered by the LAG book (diversity/breadth)
  N_aband    = entries that got a partial fill then ABANDONED_REFUND (capital burned, no position)
  hhi_names  = Herfindahl of entry counts across names (higher = more concentrated)
Usage: python analyze_legs.py <label>=<csv> [<label>=<csv> ...]
"""
import sys, pandas as pd, numpy as np

SPY = 252.0


def metrics(nav):
    nav = nav.dropna().astype(float)
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    cagr = ((nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1) * 100
    r = nav.pct_change().dropna()
    sharpe = (r.mean() / r.std() * np.sqrt(SPY)) if r.std() > 0 else np.nan
    dd = (nav / nav.cummax() - 1).min() * 100
    return cagr, sharpe, dd, (cagr / abs(dd) if dd else np.nan)


def one(label, path):
    df = pd.read_csv(path, low_memory=False)
    d = df[df["combined_nav"].notna() & df["ymd"].notna()].copy()
    d["ymd"] = pd.to_datetime(d["ymd"], errors="coerce")
    nav = d.dropna(subset=["ymd"]).sort_values("ymd").groupby("ymd")["combined_nav"].last()

    tx = df[df.get("record_type", pd.Series(dtype=str)) == "TX"].copy() if "record_type" in df else pd.DataFrame()
    if tx.empty:                                    # fall back: any row carrying an action+play_type
        tx = df[df["action"].notna() & df["play_type"].notna()].copy() if "action" in df else pd.DataFrame()
    lag = tx[tx["play_type"].astype(str).str.startswith("LAG_")].copy() if not tx.empty else pd.DataFrame()

    n_ent = n_tk = n_ab = 0
    hhi = np.nan
    if not lag.empty:
        buys = lag[lag["action"].astype(str).str.lower() == "buy"]
        n_ent = buys["holding_id"].nunique()
        n_tk = buys["ticker"].nunique()
        ab = lag[lag.get("reason", "").astype(str) == "ABANDONED_REFUND"]
        n_ab = ab["holding_id"].nunique()
        cnt = buys.groupby("ticker")["holding_id"].nunique()
        w = cnt / cnt.sum()
        hhi = float((w ** 2).sum())

    # LAG-book-only NAV (question 3: is the PEAD sleeve itself damaged, not just the blend?)
    lagnav = None
    dd2 = df[df.get("record_type", "") == "DAILY"].copy()
    if not dd2.empty and "nav_lag_ref" in dd2:
        dd2["ymd"] = pd.to_datetime(dd2["ymd"], errors="coerce")
        lagnav = dd2.dropna(subset=["ymd"]).sort_values("ymd").groupby("ymd")["nav_lag_ref"].last().dropna()

    f = metrics(nav)
    i = metrics(nav[nav.index <= "2019-12-31"])
    o = metrics(nav[nav.index >= "2020-01-01"])
    lm = metrics(lagnav) if lagnav is not None and len(lagnav) > 10 else (np.nan,) * 4
    print(f"{label:<22} FULL {f[0]:6.2f}% Sh {f[1]:4.2f} DD {f[2]:6.1f}% Cal {f[3]:4.2f} | "
          f"IS {i[0]:6.2f}% Cal {i[3]:4.2f} | OOS {o[0]:6.2f}% Cal {o[3]:4.2f} | "
          f"N_ent {n_ent:5d} N_tk {n_tk:4d} N_aband {n_ab:5d} HHI {hhi:.4f} | "
          f"LAGbook {lm[0]:6.2f}% Cal {lm[3]:4.2f} | finalNAV {nav.iloc[-1]/1e9:9.2f}B")
    py = {}
    for y in range(int(nav.index[0].year), int(nav.index[-1].year) + 1):
        ny = nav[nav.index.year == y]
        if len(ny) >= 5:
            py[y] = (ny.iloc[-1] / ny.iloc[0] - 1) * 100
    return {"label": label, "nav": nav, "peryear": py,
            "full": f, "is": i, "oos": o,
            "n_ent": n_ent, "n_tk": n_tk, "n_ab": n_ab, "hhi": hhi}


if __name__ == "__main__":
    out = [one(*a.split("=", 1)) for a in sys.argv[1:]]
    if len(out) > 1:
        base = out[0]
        print("\nper-year Δ vs " + base["label"] + " (pp):")
        for r in out[1:]:
            ds = {y: r["peryear"].get(y, np.nan) - base["peryear"].get(y, np.nan) for y in base["peryear"]}
            print(f"  {r['label']:<22} " + "  ".join(f"{y}:{v:+.1f}" for y, v in ds.items()))
