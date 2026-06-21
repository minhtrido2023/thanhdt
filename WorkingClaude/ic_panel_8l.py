#!/usr/bin/env python3
"""ic_panel_8l.py — UNIFIED MARGINAL-IC PANEL for the 8L lenses (rating + value), PIT.

Research deliverable (2026-06-21, Taylor): one synchronized cross-sectional IC table for
every lens 8L/V2.4 consumes, so all downstream weights stand on measured marginal IC instead
of scattered single-lens comments.

FAITHFUL TO WHAT V2.4 EATS — no re-derivation, no look-ahead:
  * value lenses + route + forward returns  <- data/value_panel_2014.csv (frozen PIT panel that
    custom_basket._score_v3 reads; profit_1M/2M/3M = T+20/40/60 forward, the IC target).
  * as-of rating                            <- BQ tav2_bq.fa_ratings_8l (the exact table
    custom_basket.rating_asof() bisects), merge_asof backward by ticker.

METHOD: collapse to 1 obs/(ticker,quarter)=last (matches _score_v3); per-quarter cross-sectional
Spearman IC; mean across quarters; t = mean/(std/sqrt(Ndates)); hit = %quarters IC>0. MARGINAL IC =
residualize a lens's pct-rank on the OTHER core value lenses' ranks (per date, OLS) then corr the
residual with the fwd-return rank => the signal a lens adds BEYOND the value block. Two universes:
FULL (all names) and GATE (as-of rating<=3 = the set custom30V actually picks within).

Outputs: prints 3 tables + writes data/ic_panel_8l_2014.csv (lens x metric) and
data/ic_rating_risk_2014.csv (rating bucket -> fwd return + crash%). Self-check: coverage + Ndates.
Usage: source ./wc_env.sh && $DNA_PYEXE ic_panel_8l.py
"""
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, tempfile
from io import StringIO
import numpy as np, pandas as pd

WORKDIR = os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude")
PROJECT = "lithe-record-440915-m9"
PANEL   = os.path.join(WORKDIR, "data", "value_panel_2014.csv")
TARGET  = "profit_2M"          # primary IC horizon (T+40); 1M/3M also reported
N_MIN   = 20                   # min names in a cross-section to score that date
CRASH   = -20.0                # profit_2M < -20% = "crash" (profit_* are PERCENT)

def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False) as f:
        f.write(sql); tmp = f.name
    try:
        r = subprocess.run(f'cat "{tmp}" | bq query --use_legacy_sql=false --project_id={PROJECT} '
                           f'--format=csv --max_rows=1000000', capture_output=True, text=True, shell=True)
    finally: os.unlink(tmp)
    if not r.stdout.strip(): raise RuntimeError("bq no rows:\n"+r.stderr[-1000:])
    return pd.read_csv(StringIO(r.stdout.strip()))

# ---------- load + assemble PIT panel ----------
def load():
    d = pd.read_csv(PANEL, parse_dates=["time"])
    d["q"] = d["time"].dt.to_period("Q")
    d = d.sort_values("time").groupby(["ticker", "q"], as_index=False).last()   # 1 obs / ticker / quarter
    # as-of rating (the table custom_basket.rating_asof bisects)
    rat = bq("SELECT ticker, time, rating FROM tav2_bq.fa_ratings_8l ORDER BY ticker, time")
    rat["time"] = pd.to_datetime(rat["time"])
    d = pd.merge_asof(d.sort_values("time"), rat.sort_values("time"),
                      by="ticker", on="time", direction="backward")
    # forward returns: inf -> NaN (division artifacts), percent units
    for c in ["profit_1M", "profit_2M", "profit_3M"]:
        d[c] = pd.to_numeric(d[c], errors="coerce").replace([np.inf, -np.inf], np.nan)
    # ---- lens construction (cross-sectional, higher = cheaper/better = expect higher fwd return) ----
    pos = lambda s: np.where(s > 0, 1.0 / s, np.nan)
    d["ey"]  = pos(d["PE"])                                   # 1/PE earnings yield
    d["cfy"] = pos(d["PCF"])                                  # 1/PCF cashflow yield
    d["ps"]  = pos(d["PS"])                                   # 1/PS sales yield
    ttm = d[["CF_OA_P0","CF_OA_P1","CF_OA_P2","CF_OA_P3"]].sum(axis=1, min_count=1)
    n3  = d["CF_OA_3Y"] / 3.0
    d["cfo_normy"] = np.where((d["PCF"]>0)&(ttm>0)&(n3>0),
                              (1.0/d["PCF"])*np.clip(n3/ttm, 0.3, 3.0), np.nan)   # cycle-normalized cfy
    d["neg_pbz"] = -d["pb_z"]                                 # lower pb_z = cheaper
    d["golden"]  = (d["pb_z"] <= -1).astype(float)
    d["neg_rating"] = -d["rating"]                            # lower rating = better durability
    # raw durability sub-lenses already in the panel
    d["FSCORE"]   = pd.to_numeric(d["FSCORE"], errors="coerce")
    d["ROIC5Y"]   = pd.to_numeric(d["ROIC5Y"], errors="coerce")
    d["ROE_Min3Y"] = pd.to_numeric(d["ROE_Min3Y"], errors="coerce")
    return d

# ---------- IC machinery ----------
CORE_VALUE = ["ey", "cfy", "ps", "neg_pbz"]    # the value block we residualize against

def _rank(s):
    return s.rank(pct=True)

def ic_series(d, lens, target, mask=None):
    """per-quarter Spearman IC of lens vs target. returns array of IC_t and avg n."""
    sub = d if mask is None else d[mask]
    ics, ns = [], []
    for _, g in sub.groupby("q"):
        x = pd.to_numeric(g[lens], errors="coerce"); y = pd.to_numeric(g[target], errors="coerce")
        ok = x.notna() & y.notna()
        if ok.sum() < N_MIN: continue
        ic = np.corrcoef(_rank(x[ok]), _rank(y[ok]))[0, 1]
        if np.isfinite(ic): ics.append(ic); ns.append(int(ok.sum()))
    return np.array(ics), (np.mean(ns) if ns else 0)

def marginal_ic_series(d, lens, target, mask=None):
    """residualize rank(lens) on ranks of CORE_VALUE\{lens} per quarter (OLS), corr resid vs rank(target)."""
    sub = d if mask is None else d[mask]
    others = [c for c in CORE_VALUE if c != lens]
    ics = []
    for _, g in sub.groupby("q"):
        y = pd.to_numeric(g[target], errors="coerce")
        x = pd.to_numeric(g[lens], errors="coerce")
        X = g[others].apply(pd.to_numeric, errors="coerce")
        ok = x.notna() & y.notna() & X.notna().all(axis=1)
        if ok.sum() < N_MIN: continue
        xr = _rank(x[ok]).values
        Xr = np.column_stack([np.ones(ok.sum())] + [_rank(X[c][ok]).values for c in others])
        beta, *_ = np.linalg.lstsq(Xr, xr, rcond=None)
        resid = xr - Xr @ beta
        ic = np.corrcoef(resid, _rank(y[ok]))[0, 1]
        if np.isfinite(ic): ics.append(ic)
    return np.array(ics)

def summ(ics):
    if len(ics) == 0: return dict(ic=np.nan, t=np.nan, hit=np.nan, n=0)
    m, s = float(np.mean(ics)), float(np.std(ics, ddof=1)) if len(ics) > 1 else np.nan
    t = m / (s/np.sqrt(len(ics))) if (s and s > 0) else np.nan
    return dict(ic=m, t=t, hit=float(np.mean(ics > 0)), n=len(ics))

# ---------- main ----------
def main():
    d = load()
    nq = d["q"].nunique()
    print(f"panel: {len(d)} obs (1/ticker/quarter), {nq} quarters, {d.ticker.nunique()} tickers, "
          f"rating cov {d.rating.notna().mean():.2f}, {TARGET} cov {d[TARGET].notna().mean():.2f}")
    gate = d["rating"] <= 3   # the investable set V2.4 acts within

    LENSES = ["ey", "cfy", "cfo_normy", "ps", "neg_pbz", "golden",
              "neg_rating", "FSCORE", "ROIC5Y", "ROE_Min3Y"]
    rows = []
    for L in LENSES:
        rF, nF = ic_series(d, L, TARGET);            sF = summ(rF)
        rG, nG = ic_series(d, L, TARGET, gate);      sG = summ(rG)
        mF = summ(marginal_ic_series(d, L, TARGET))
        mG = summ(marginal_ic_series(d, L, TARGET, gate))
        r1, _ = ic_series(d, L, "profit_1M");  r3, _ = ic_series(d, L, "profit_3M")
        rows.append(dict(lens=L, cov=round(d[L].notna().mean(), 2), avg_n=int(nF),
            ic_full=sF["ic"], t_full=sF["t"], hit_full=sF["hit"],
            mic_full=mF["ic"], mt_full=mF["t"],
            ic_gate=sG["ic"], t_gate=sG["t"], mic_gate=mG["ic"], mt_gate=mG["t"],
            ic_1M=summ(r1)["ic"], ic_3M=summ(r3)["ic"]))
    tab = pd.DataFrame(rows)

    fmt = lambda v: f"{v:+.3f}" if pd.notna(v) else "  -  "
    print(f"\n=== (A) IC PANEL — target={TARGET} (T+40), {nq} quarterly cross-sections ===")
    print(f"{'lens':11} {'cov':>4} {'avgN':>5} | {'IC_full':>8} {'t':>5} {'hit':>4} {'mIC_full':>8} {'mt':>5} "
          f"| {'IC_gate':>8} {'t':>5} {'mIC_gate':>8} {'mt':>5} | {'IC_1M':>7} {'IC_3M':>7}")
    for _, r in tab.iterrows():
        print(f"{r['lens']:11} {r['cov']:>4.2f} {r['avg_n']:>5} | {fmt(r['ic_full']):>8} {r['t_full']:>5.1f} {r['hit_full']:>4.0%} "
              f"{fmt(r['mic_full']):>8} {r['mt_full']:>5.1f} | {fmt(r['ic_gate']):>8} {r['t_gate']:>5.1f} "
              f"{fmt(r['mic_gate']):>8} {r['mt_gate']:>5.1f} | {fmt(r['ic_1M']):>7} {fmt(r['ic_3M']):>7}")
    print("  IC=raw Spearman | mIC=marginal vs value block {ey,cfy,ps,neg_pbz} | gate=within as-of rating<=3")
    tab.round(4).to_csv(os.path.join(WORKDIR, "data", "ic_panel_8l_2014.csv"), index=False)

    # ---- (B) per-route raw IC (pooled dates; small routes noisy) ----
    print(f"\n=== (B) per-route raw IC ({TARGET}, FULL universe; pooled, routes with enough names) ===")
    routes = [r for r in d.route.dropna().unique()]
    show = ["ey", "cfy", "ps", "neg_pbz", "neg_rating"]
    hdr = f"{'route':11} {'names/q':>7} |" + "".join(f"{l:>9}" for l in show)
    print(hdr)
    for rt in ["COMPOUNDER","BANK","SECURITIES","POWER","CYCLICAL","REALESTATE","INSURANCE"]:
        m = d.route == rt
        if m.sum() == 0: continue
        cells = []
        for L in show:
            ics, n = ic_series(d, L, TARGET, m); cells.append(summ(ics)["ic"])
        avgn = int(d[m].groupby("q").size().mean())
        print(f"{rt:11} {avgn:>7} |" + "".join(f"{fmt(c):>9}" for c in cells))

    # ---- (C) rating -> forward return + crash (gate vs tilt decision) ----
    print(f"\n=== (C) RATING as a SIGNAL — fwd return & crash by as-of rating bucket ===")
    rr = []
    for k in [1, 2, 3, 4, 5]:
        g = d[d["rating"] == k]
        if len(g) == 0: continue
        rr.append(dict(rating=k, n=len(g),
            p1M=g["profit_1M"].mean(), p2M=g["profit_2M"].mean(), p3M=g["profit_3M"].mean(),
            med2M=g["profit_2M"].median(),
            crash=(g["profit_2M"] < CRASH).mean()*100))
    rrt = pd.DataFrame(rr)
    print(f"{'rating':>6} {'n':>7} {'fwd1M%':>7} {'fwd2M%':>7} {'fwd3M%':>7} {'med2M%':>7} {'crash%':>7}")
    for _, r in rrt.iterrows():
        print(f"{int(r.rating):>6} {int(r.n):>7} {r.p1M:>7.2f} {r.p2M:>7.2f} {r.p3M:>7.2f} {r.med2M:>7.2f} {r.crash:>7.1f}")
    rrt.round(3).to_csv(os.path.join(WORKDIR, "data", "ic_rating_risk_2014.csv"), index=False)

    # ---- (D) IS/OOS robustness for the decisive lenses (sign must hold both halves) ----
    d["yr"] = d["q"].dt.year
    IS, OOS = d["yr"] <= 2019, d["yr"] >= 2020
    print(f"\n=== (D) IS(2014-19) vs OOS(2020+) robustness — {TARGET} ===")
    print(f"{'lens':11} | {'IC_IS':>7} {'IC_OOS':>7} | {'gate-mIC_IS':>11} {'gate-mIC_OOS':>12}")
    for L in ["ey","cfy","cfo_normy","ps","neg_pbz","neg_rating","FSCORE"]:
        icis  = summ(ic_series(d, L, TARGET, IS)[0])["ic"]
        icoos = summ(ic_series(d, L, TARGET, OOS)[0])["ic"]
        gmis  = summ(marginal_ic_series(d, L, TARGET, gate & IS))["ic"]
        gmoos = summ(marginal_ic_series(d, L, TARGET, gate & OOS))["ic"]
        print(f"{L:11} | {fmt(icis):>7} {fmt(icoos):>7} | {fmt(gmis):>11} {fmt(gmoos):>12}")
    print("\nwrote data/ic_panel_8l_2014.csv + data/ic_rating_risk_2014.csv")

if __name__ == "__main__":
    main()
