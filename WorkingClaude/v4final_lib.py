# -*- coding: utf-8 -*-
"""v4final_lib.py — independent recompute of the custom30V daily weight vector.
Job Taylor_20260714_140127. Research/audit only; nothing in production imports this.

Why this exists: `custom_basket.build_pit` returns levels and membership, but NOT the daily weight
vector it actually feeds into the chained return. Every claim about "the financial cap holds" has to
be measured on THAT vector, not inferred from the cap parameter (`_cap_names` runs AFTER
`_cap_sector` and water-fills excess into every uncapped name — financials included — so the sector
cap is NOT self-evidently binding after it). This replicates build_pit's loop line-for-line from the
raw panel it returns, so a reviewer can check the cap independently of the module's own reporting.
"""
import bisect
import os

import numpy as np
import pandas as pd

FIN_ROUTES = {"BANK", "INSURANCE", "SECURITIES"}
_PANEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "value_panel_2014.csv")
_route_hist = None


def _load_routes():
    global _route_hist
    if _route_hist is None:
        p = pd.read_csv(_PANEL_PATH, parse_dates=["time"], usecols=["ticker", "time", "route"])
        p["qstart"] = p["time"].dt.to_period("Q").dt.start_time
        p = p.dropna(subset=["route"]).sort_values("time")
        rl = p.groupby(["ticker", "qstart"])["route"].last().reset_index()
        _route_hist = {tk: (list(g["qstart"]), list(g["route"])) for tk, g in rl.groupby("ticker")}
    return _route_hist


def route_asof(tk, q):
    e = _load_routes().get(tk)
    if not e:
        return None
    i = bisect.bisect_right(e[0], pd.Timestamp(q)) - 1
    return e[1][i] if i >= 0 else e[1][0]


def _cap_names(w, cap):
    w = np.array(w, dtype=float)
    s = w.sum()
    if s <= 0:
        return w
    w = w / s
    for _ in range(100):
        over = w > cap + 1e-12
        if not over.any():
            break
        excess = float((w[over] - cap).sum())
        w[over] = cap
        under = ~over
        us = float(w[under].sum())
        if us <= 1e-12:
            break
        w[under] = w[under] + excess * w[under] / us
    return w


def _cap_sector(w, sec, code, scap):
    w = np.array(w, dtype=float)
    s = w.sum()
    if s <= 0:
        return w
    w = w / s
    grp = (sec == code)
    g = float(w[grp].sum())
    other = float(w[~grp].sum())
    if g > scap + 1e-12 and grp.any() and (~grp).any() and other > 1e-12:
        w[grp] = w[grp] * (scap / g)
        w[~grp] = w[~grp] * ((1.0 - scap) / other)
    return w


def _cap_group_jointly(w, grp, gcap, ncap):
    """Independent re-implementation of custom_basket._cap_group_jointly (see its docstring).
    Deliberately re-derived here rather than imported: this library exists to CHECK the module, and
    importing the thing under test would make the check vacuous."""
    w = np.array(w, dtype=float)
    s = w.sum()
    if s <= 0:
        return w, gcap
    w = w / s
    g = np.asarray(grp, dtype=bool)
    if not g.any() or not (~g).any():
        return _cap_names(w, ncap), gcap
    gcap_eff = max(gcap, 1.0 - int((~g).sum()) * ncap)
    b_in = min(float(w[g].sum()), gcap_eff)
    out = np.zeros_like(w)
    for m, b in ((g, b_in), (~g, 1.0 - b_in)):
        if b > 0 and w[m].sum() > 0:
            out[m] = _cap_names(w[m], ncap / b) * b
    return out, gcap_eff


def daily_fin_weights(bx, mem, name_cap=0.10, fin_cap=None):
    """-> DataFrame(time, fin_w, wsum, n_fin, n_active): the financial-route share of the ACTUAL
    daily weight vector. fin_cap=None reproduces plain `namecap`; a float reproduces `fincap`."""
    bx = bx.copy()
    bx["time"] = pd.to_datetime(bx["time"])
    mcap = bx.pivot_table(index="time", columns="ticker", values="mcap").sort_index()
    m = mem.copy()
    m["rebal_date"] = pd.to_datetime(m["rebal_date"])
    m["quarter"] = pd.to_datetime(m["quarter"])
    members = {d: list(zip(g["ticker"], g["qmult"])) for d, g in m.groupby("rebal_date")}
    # selection quarter per rebal = the quarter PRIOR to the rebal's own quarter — the same PIT rule
    # build_pit uses to pick members, so routes are read at the same vintage the selector saw.
    src_q = {d: (pd.Timestamp(d).to_period("Q").start_time - pd.Timedelta(days=1)).to_period("Q").start_time
             for d in members}
    reb = sorted(members)
    rows = []
    prev = None
    for d in mcap.index:
        i = bisect.bisect_right(reb, d) - 1
        if i < 0 or prev is None:
            prev = d
            continue
        aq = reb[i]
        mem_a = members[aq]
        tks = [t for t, _ in mem_a if t in mcap.columns]
        qm = np.array([q for t, q in mem_a if t in mcap.columns])
        today = mcap.loc[d, tks].values.astype(float)
        yest = mcap.loc[prev, tks].values.astype(float)
        valid = ~np.isnan(today) & ~np.isnan(yest)
        if valid.sum() > 0:
            base = yest[valid] * qm[valid]
            W = base / base.sum() if base.sum() > 0 else base
            fv = np.array([route_asof(t, src_q[aq]) in FIN_ROUTES
                           for t, ok in zip(tks, valid) if ok])
            cap_eff = fin_cap
            if fin_cap is not None:
                W, cap_eff = _cap_group_jointly(W, fv, fin_cap, name_cap)
            else:
                W = _cap_names(W, name_cap)
            rows.append({"time": d, "fin_w": float(W[fv].sum()), "wsum": float(W.sum()),
                         "n_fin": int(fv.sum()), "n_active": int(valid.sum()),
                         "cap_eff": cap_eff})
        prev = d
    return pd.DataFrame(rows)


def metrics(level_series, name=""):
    """CAGR / Sharpe / MaxDD / Calmar on a vehicle level series (calendar-time CAGR)."""
    s = pd.Series(level_series).sort_index()
    s.index = pd.to_datetime(s.index)
    r = s.pct_change().dropna()
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1
    n = len(r) / yrs
    sharpe = r.mean() / r.std() * np.sqrt(n) if r.std() > 0 else np.nan
    dd = (s / s.cummax() - 1).min()
    return {"name": name, "CAGR": cagr * 100, "Sharpe": sharpe, "MaxDD": dd * 100,
            "Calmar": (cagr * 100) / abs(dd * 100) if dd < 0 else np.nan}
