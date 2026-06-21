# -*- coding: utf-8 -*-
"""Loader for the point-in-time (vintage) 5-state reference.

A backtest that wants reproducible / no-look-ahead state should call load_vintage(asof),
which returns the state series exactly as it was KNOWN on `asof` (the latest snapshot <= asof).
Pass asof=None to get the most recent frozen snapshot.

Returns a DataFrame[time(datetime64), state(int)].
"""
import os, glob
import pandas as pd

VDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state_vintage")


def _asof_of(path):
    s = os.path.basename(path).replace("vnindex_5state_VINTAGE_", "").replace(".csv", "")
    return f"{s[:4]}-{s[4:6]}-{s[6:]}"


def list_vintages():
    files = sorted(glob.glob(os.path.join(VDIR, "vnindex_5state_VINTAGE_*.csv")))
    return [(_asof_of(f), f) for f in files]


def load_vintage(asof=None):
    """Return state series as known on `asof` (YYYY-MM-DD str or None=latest)."""
    vs = list_vintages()
    if not vs:
        raise FileNotFoundError("No vintage snapshots in state_vintage/. Run snapshot_state_vintage.py --init")
    if asof is None:
        chosen = vs[-1][1]
    else:
        cands = [f for (a, f) in vs if a <= asof]
        if not cands:
            raise ValueError(f"No vintage snapshot on/before {asof}; earliest is {vs[0][0]}")
        chosen = cands[-1]
    df = pd.read_csv(chosen)
    df["time"] = pd.to_datetime(df["time"])
    df["state"] = df["state"].astype(int)
    return df.sort_values("time").reset_index(drop=True)


if __name__ == "__main__":
    for a, f in list_vintages():
        print(a, os.path.basename(f))
    d = load_vintage()
    print("latest:", d["time"].min().date(), "->", d["time"].max().date(), len(d), "rows")
