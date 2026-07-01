# -*- coding: utf-8 -*-
"""
composite_selector_backtest.py — review-only standalone backtest (Taylor, job 20260630_170123).

Question: does the 8L axis-2 COMPOSITE value_score_v2 (0.35*pb_z-rel + 0.65*(1/PE sector-neutral)
+ CFO-3Y confirm + track-record bonus + TRAP-gate ROE_Min3Y<0), used as an ENTRY SELECTOR (top-N
each month, equal-weight), OUTPERFORM the production parking basket custom30V (yieldcombo = 1/PE+1/PCF
top-30) on the SAME panel/engine?  Walk-forward IS(2014-19)/OOS(2020+)/Full.

Self-contained: reads ONLY data/value_panel_2014.csv. No BQ. Equal-weight, monthly rebal, TC=0.1%/side.
The composite is replicated BYTE-FAITHFUL from rating_8l.py value_score_v2 (lines 466-611).
"""
import numpy as np, pandas as pd

PANEL = "data/value_panel_2014.csv"
TC = 0.001            # 0.1% per side
N_LIST = [20, 30]
CLIP = (-95.0, 200.0) # clip forward % to drop bad-data inf (Close~0 -> inf return)

df = pd.read_csv(PANEL)
df["time"] = pd.to_datetime(df["time"])
# monthly rebal calendar = month-end snapshots with real breadth (>=50 names)
b = df.groupby("time").size()
REBAL = sorted(b[b >= 50].index)
df = df[df["time"].isin(REBAL)].copy()

# ---- forward 1M return (target), clean ----
df["fwd"] = pd.to_numeric(df["profit_1M"], errors="coerce")
df.loc[~np.isfinite(df["fwd"]), "fwd"] = np.nan
df["fwd"] = df["fwd"].clip(*CLIP) / 100.0

# ---- derived value fields (exact rating_8l.py replication) ----
df["earn_yield"] = np.where(df["PE"] > 0, 1.0 / df["PE"], np.nan)
_ttm_cf = df[["CF_OA_P0", "CF_OA_P1", "CF_OA_P2", "CF_OA_P3"]].sum(axis=1, min_count=1)
_norm_cf3 = df["CF_OA_3Y"] / 3.0
df["cfo_normy"] = np.where((df["PCF"] > 0) & (_ttm_cf > 0) & (_norm_cf3 > 0),
                           (1.0 / df["PCF"]) * np.clip(_norm_cf3 / _ttm_cf, 0.3, 3.0), np.nan)
df["proven5y"] = df["CF_OA_5Y"] > 0
df["cfo_yield"] = np.where(df["PCF"] > 0, 1.0 / df["PCF"], np.nan)  # for yieldcombo baseline


def _ey_rank_within_route(g):
    return g.rank(pct=True) if g.notna().sum() >= 5 else pd.Series(np.nan, index=g.index)


def score_month(m):
    m = m.copy()
    # --- COMPOSITE value_score_v2 (rating_8l.py) ---
    vyp = m.groupby("route")["earn_yield"].transform(_ey_rank_within_route)
    vyp = vyp.fillna(m["earn_yield"].rank(pct=True))          # route<5 -> global
    rel = (0.5 - m["pb_z"] / 2.0).clip(0, 1)                  # pb_z relative cheapness
    cfo_pct = m["cfo_normy"].rank(pct=True)
    adj = np.where(cfo_pct.notna() & (cfo_pct >= 0.5), 0.05,
          np.where(cfo_pct.notna() & (cfo_pct < 0.2), -0.08, 0.0))
    track = (np.where(m["proven5y"].fillna(False), 0.03, 0.0)
             + np.where(m["ROE_Min5Y"].fillna(-9) > 0.10, 0.03, 0.0))
    m["composite"] = (0.35 * rel + 0.65 * vyp.fillna(0.5) + adj + track).clip(0, 1)
    # --- baseline custom30V yieldcombo = rank(1/PE)+rank(1/PCF), global ---
    m["yieldcombo"] = m["earn_yield"].rank(pct=True).fillna(0) + m["cfo_yield"].rank(pct=True).fillna(0)
    return m


def backtest(sel_col, N, trap_gate=False, liq_min=0.0):
    """sel_col: column to rank desc. Returns monthly return Series indexed by rebal date."""
    rets, dates, prev = [], [], set()
    for t in REBAL:
        m = df[df["time"] == t]
        m = score_month(m)
        if trap_gate:
            m = m[~(m["ROE_Min3Y"] < 0)]                     # TRAP gate: drop chronic destroyers
        if liq_min > 0:
            m = m[m["turnover"].fillna(0) >= liq_min * 1e9]
        m = m[m[sel_col].notna() & m["fwd"].notna()]
        if len(m) < 5:
            continue
        pick = m.nlargest(N, sel_col)
        cur = set(pick["ticker"])
        turn = len(cur - prev) / max(len(cur), 1)            # one-way entering fraction
        gross = pick["fwd"].mean()
        net = gross - TC * 2 * turn                          # round-trip on rotated names
        rets.append(net); dates.append(t); prev = cur
    return pd.Series(rets, index=pd.to_datetime(dates))


def metrics(r):
    if len(r) < 6:
        return (np.nan,) * 4
    s = (1 + r).cumprod()
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    cagr = s.iloc[-1] ** (1 / yrs) - 1
    spm = 12.0  # monthly
    sh = r.mean() / r.std() * np.sqrt(spm) if r.std() > 0 else 0
    dd = (s / s.cummax() - 1).min()
    cal = (cagr * 100) / abs(dd * 100) if dd < 0 else 0
    return cagr * 100, sh, dd * 100, cal


WINS = [("FULL 2014-now", None, None),
        ("IS   2014-19", None, pd.Timestamp("2019-12-31")),
        ("OOS  2020-now", pd.Timestamp("2020-01-01"), None)]


def report(label, r):
    print(f"\n### {label}  (n_months={len(r)}) ###")
    out = {}
    for tag, a, bnd in WINS:
        rr = r.copy()
        if a is not None: rr = rr[rr.index >= a]
        if bnd is not None: rr = rr[rr.index <= bnd]
        c, sh, dd, cal = metrics(rr)
        out[tag] = (c, sh, dd, cal)
        print(f"  {tag:<14} CAGR {c:6.2f}%  Sharpe {sh:5.2f}  MaxDD {dd:6.1f}%  Calmar {cal:5.2f}")
    return out


print(f"costs: TC={TC} ({TC*100}%/side, round-trip on rotated names), equal-weight, monthly rebal")
print(f"calendar: {len(REBAL)} month-end snapshots {REBAL[0].date()} -> {REBAL[-1].date()}")

ALL = {}
for N in N_LIST:
    ALL[("custom30V_yieldcombo", N)] = report(f"BASELINE custom30V yieldcombo (1/PE+1/PCF) top{N}",
                                              backtest("yieldcombo", N))
    ALL[("composite_TRAP", N)] = report(f"COMPOSITE value_score_v2 + TRAP-gate top{N}",
                                        backtest("composite", N, trap_gate=True))
    ALL[("composite_noTRAP", N)] = report(f"COMPOSITE value_score_v2 (no TRAP gate) top{N}",
                                          backtest("composite", N, trap_gate=False))

# liquidity-screened variant (parking basket must be tradable): turnover >= 1bn VND/day
print("\n========== LIQUID variant (turnover >= 1bn VND, parking-realistic) ==========")
for N in N_LIST:
    ALL[("custom30V_liq", N)] = report(f"BASELINE yieldcombo top{N} liq>=1bn",
                                       backtest("yieldcombo", N, liq_min=1.0))
    ALL[("composite_liq", N)] = report(f"COMPOSITE+TRAP top{N} liq>=1bn",
                                       backtest("composite", N, trap_gate=True, liq_min=1.0))

# ---- head-to-head delta (Full + OOS) ----
print("\n========== HEAD-TO-HEAD: composite - custom30V (pp) ==========")
for N in N_LIST:
    for tag in ["FULL 2014-now", "OOS  2020-now"]:
        cc = ALL[("composite_TRAP", N)][tag][0]
        bb = ALL[("custom30V_yieldcombo", N)][tag][0]
        print(f"  top{N} {tag:<14} composite {cc:6.2f}% - custom30V {bb:6.2f}% = {cc-bb:+5.2f}pp CAGR")
