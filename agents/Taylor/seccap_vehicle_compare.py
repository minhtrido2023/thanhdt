# -*- coding: utf-8 -*-
"""seccap_vehicle_compare.py — job Taylor_20260714_095953.

The full V2.4 harness dilutes the basket: parking is only part of NAV, so a big change to the
basket shows up as a small change to the system. This isolates the PURE vehicle effect —
custom30V level series under each sector-cap variant — plus the intra-basket TURNOVER that the
harness does NOT charge (build_pit's ret = sum(W*r), no cost inside the basket).

Turnover = sum_i |w_i(new) - w_i(drifted from prev rebal)| at each rebalance, i.e. the fraction
of the sleeve that must actually be traded. x2 = round-trip notional. This is the cost variant A
gets for FREE in the harness -> the harness number is an OPTIMISTIC bound for A.
"""
import os, sys
import numpy as np, pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import bq
import custom_basket as cb

START, END = "2014-01-02", "2026-06-19"
NAME_CAP, SEC_CODE = 0.10, 8
os.environ["BASKET_SELECT"] = "yieldcombo"

VARIANTS = [("baseline_namecap", "namecap", None),
            ("A_fix50",          "sectorcap", None),
            ("B_mktcap",         "sectorcap", "mktcap"),
            ("B15_mktx1.5",      "sectorcap", "mktx1.5")]

def stats(lvl):
    s = pd.Series(lvl).sort_index()
    r = s.pct_change().dropna()
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1
    sharpe = r.mean() / r.std() * np.sqrt(252)
    dd = (s / s.cummax() - 1).min()
    return cagr, sharpe, dd, cagr / abs(dd)

rows = []
levels = {}
for tag, wt, mode in VARIANTS:
    if mode: os.environ["BASKET_SECCAP_MODE"] = mode
    else: os.environ.pop("BASKET_SECCAP_MODE", None)
    print(f"\n--- {tag} (weight_scheme={wt}, seccap_mode={mode}) ---")
    lvl, adv, memdf, bx = cb.build_pit(bq, START, END, quality="none", rebal="q2m5",
                                       gate_rating=3, weight_scheme=wt)
    levels[tag] = pd.Series(lvl).sort_index()
    c, sh, dd, cal = stats(lvl)
    rows.append({"variant": tag, "CAGR": c, "Sharpe": sh, "MaxDD": dd, "Calmar": cal})
    print(f"  CAGR {c:.2%}  Sharpe {sh:.2f}  MaxDD {dd:.1%}  Calmar {cal:.2f}")
os.environ.pop("BASKET_SECCAP_MODE", None)

print("\n=== PURE VEHICLE (custom30V level series, undiluted by BAL/LAG) ===")
res = pd.DataFrame(rows)
b = res.iloc[0]
for c in ("CAGR", "Sharpe", "MaxDD", "Calmar"):
    res[f"d_{c}"] = res[c] - b[c]
print(res.to_string(index=False, float_format=lambda v: f"{v:+.4f}"))

# ---- TURNOVER at each rebalance (the cost the harness does not charge) ----
print("\n=== INTRA-BASKET TURNOVER per rebalance (harness charges NONE of this) ===")
memdf["rebal_date"] = pd.to_datetime(memdf["rebal_date"])
bx["time"] = pd.to_datetime(bx["time"])
rebals = sorted(memdf["rebal_date"].unique())
mcap = bx.pivot_table(index="time", columns="ticker", values="mcap").sort_index()
icb = bq(f"""SELECT x.ticker, x.sec FROM (SELECT t.ticker AS ticker,
    CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS sec,
    ROW_NUMBER() OVER (PARTITION BY t.ticker ORDER BY t.time DESC) AS rn
  FROM tav2_bq.ticker AS t WHERE t.ticker IN ({",".join(f"'{x}'" for x in sorted(memdf.ticker.unique()))})
    AND t.ICB_Code IS NOT NULL) AS x WHERE x.rn=1""")
sec_map = {t: int(s) for t, s in zip(icb["ticker"], icb["sec"])}

# per-rebal market cap of sector 8 (for the dynamic caps)
hist = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sector_conc_history.csv"))
mkw = {pd.Timestamp(r.rebal_date): r.mkt_w8_prune for r in hist.itertuples()}

def weights_at(rd, tag):
    mem = memdf[memdf["rebal_date"] == rd].sort_values("liq_rank")
    tks = list(mem["ticker"])
    sub = mcap.loc[mcap.index <= rd, [t for t in tks if t in mcap.columns]]
    mc = sub.ffill().iloc[-1].reindex(tks).fillna(0.0)
    base = (mc / mc.sum()).values if mc.sum() > 0 else np.ones(len(tks)) / len(tks)
    w = cb._cap_names(base, NAME_CAP)
    sv = np.array([sec_map.get(t, -1) for t in tks])
    if tag != "baseline_namecap":
        scap = {"A_fix50": 0.50, "B_mktcap": mkw.get(rd, np.nan),
                "B15_mktx1.5": min(1.0, mkw.get(rd, np.nan) * 1.5)}[tag]
        if np.isfinite(scap):
            w = cb._cap_names(cb._cap_sector(w, sv, SEC_CODE, scap), NAME_CAP)
    return pd.Series(w, index=tks)

tv_rows = []
for tag, _, _ in VARIANTS:
    tos = []
    prev_w, prev_rd = None, None
    for rd in rebals:
        rd = pd.Timestamp(rd)
        w = weights_at(rd, tag)
        if prev_w is not None:
            # drift prev weights to rd by each name's price return, then renormalise
            common = [t for t in prev_w.index if t in mcap.columns]
            px0 = mcap.loc[mcap.index <= prev_rd, common].ffill().iloc[-1]
            px1 = mcap.loc[mcap.index <= rd, common].ffill().iloc[-1]
            gr = (px1 / px0).replace([np.inf, -np.inf], np.nan).fillna(1.0)
            d = (prev_w[common] * gr); d = d / d.sum()
            allt = sorted(set(d.index) | set(w.index))
            to = float((w.reindex(allt).fillna(0) - d.reindex(allt).fillna(0)).abs().sum())
            tos.append(to)
        prev_w, prev_rd = w, rd
    tv_rows.append({"variant": tag, "turnover_mean": np.mean(tos), "turnover_med": np.median(tos),
                    "turnover_max": np.max(tos), "annual_x": np.mean(tos) * 4})
tv = pd.DataFrame(tv_rows)
tv["extra_cost_pa_at_TC0.3%"] = (tv.annual_x - tv.annual_x.iloc[0]) * 0.003
print(tv.to_string(index=False, float_format=lambda v: f"{v:.4f}"))
print("\n  turnover = sum|w_new - w_drifted| per rebal (1.0 = 100% of sleeve traded, one-way)")
print("  annual_x = mean turnover x 4 rebals/yr; extra cost vs baseline at TC=0.3% round-trip")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seccap_vehicle_compare.csv")
res.merge(tv, on="variant").to_csv(out, index=False)
print(f"\n-> {out}")
