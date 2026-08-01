#!/usr/bin/env python
"""CAU B — is the 8L FSCORE AXIS weaker for asset-LIGHT companies than asset-HEAVY ones?

User's prior: "Piotroski F-Score only suits manufacturers with heavy fixed assets." Tests it the
same way the value composite was measured (ic_panel_8l.py, registry entry '1/PE dominant IC+0.125,
94% hit'): per-quarter cross-sectional Spearman IC of the LENS against forward return, mean across
quarters, t = mean/(sd/sqrt(Nq)), hit = %quarters IC>0.

WHAT IS MEASURED: the FSCORE AXIS AS IMPLEMENTED in core_score() —
    fs_pts = 2 if FSCORE>=8 else 1 if FSCORE>=6 else 0      (rating_8l.py:226)
not the raw score (raw reported alongside as a reference).

SCOPE: routes COMPOUNDER + CYCLICAL only. Verified in rating_8l.py: rate_securities/rate_insurance
ignore FSCORE entirely, rate_bank + rate_power use their own cached lenses (never call core_score's
result), rate_realestate uses its own 1/9-point leg. So COMPOUNDER+CYCLICAL are the ONLY routes
where the full 2/12 FSCORE axis reaches the rating.

SPLIT: per-quarter cross-sectional median of the asset-intensity variable, PIT-joined from
tav2_bq.ticker_financial by Release_Date (never by fiscal `time` — that would look ahead).
  FAsset_Eq_P0   = fixed assets / equity      (primary; high = asset-HEAVY)
  FAssetTurn_P0  = fixed-asset turnover       (robustness; high = asset-LIGHT)

Pure measurement. No production wiring.
"""
import os
import sys

import numpy as np
import pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.environ["BQ_LOCAL_CACHE"] = os.path.join(WORKDIR, "data", "bq_cache_asof20260729_postrestate")
os.environ.setdefault("BQ_CACHE_THREADS", "1")
from bq_local_cache import get_cache  # noqa: E402

CACHE = get_cache()
OUT = os.path.join(WORKDIR, "data", "fscore_review_20260801")
PANEL = os.path.join(WORKDIR, "data", "value_panel_2014.csv")
TARGET = "profit_2M"     # T+40 forward, same target as the pinned IC panel
N_MIN = 15               # min names per cross-section per GROUP to score that quarter

# ---------------------------------------------------------------- load frozen PIT value panel
d = pd.read_csv(PANEL, parse_dates=["time"])
d["q"] = d["time"].dt.to_period("Q")
d = d.sort_values("time").groupby(["ticker", "q"], as_index=False).last()   # 1 obs / ticker / quarter
d = d[d["route"].isin(["COMPOUNDER", "CYCLICAL"])].copy()
print(f"[panel] {len(d)} (ticker,quarter) obs, routes COMPOUNDER+CYCLICAL, "
      f"{d['q'].nunique()} quarters {d['q'].min()}..{d['q'].max()}")

for c in [TARGET, "PE", "PCF", "PS", "pb_z", "FSCORE"]:
    d[c] = pd.to_numeric(d[c], errors="coerce").replace([np.inf, -np.inf], np.nan)

# ---------------------------------------------------------------- PIT asset-intensity join
fin = CACHE.query(
    "SELECT t.ticker, t.Release_Date, t.FAsset_Eq_P0, t.FAssetTurn_P0 "
    "FROM tav2_bq.ticker_financial t WHERE t.Release_Date IS NOT NULL ORDER BY t.Release_Date")
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
fin = fin.dropna(subset=["Release_Date"]).sort_values("Release_Date")
d = pd.merge_asof(d.sort_values("time"), fin, by="ticker",
                  left_on="time", right_on="Release_Date", direction="backward")
print(f"[asof] FAsset_Eq_P0 coverage {d['FAsset_Eq_P0'].notna().mean()*100:.1f}%, "
      f"FAssetTurn_P0 {d['FAssetTurn_P0'].notna().mean()*100:.1f}%, "
      f"{TARGET} {d[TARGET].notna().mean()*100:.1f}%, FSCORE {d['FSCORE'].notna().mean()*100:.1f}%")

# ---------------------------------------------------------------- lens construction
pos = lambda s: np.where(s > 0, 1.0 / s, np.nan)
d["ey"], d["cfy"], d["ps"] = pos(d["PE"]), pos(d["PCF"]), pos(d["PS"])
d["neg_pbz"] = -d["pb_z"]
# THE AXIS AS IMPLEMENTED (rating_8l.py:226) — a 3-level step, not the raw 0-9 score
d["fs_pts"] = np.where(d["FSCORE"] >= 8, 2.0, np.where(d["FSCORE"] >= 6, 1.0, 0.0))
d.loc[d["FSCORE"].isna(), "fs_pts"] = np.nan
CORE_VALUE = ["ey", "cfy", "ps", "neg_pbz"]


def _rank(s):
    return s.rank(pct=True)


def ic_series(sub, lens, marginal=False):
    """Per-quarter Spearman IC. marginal=True residualizes the lens rank on the value block."""
    out = {}
    for qq, g in sub.groupby("q"):
        g = g.dropna(subset=[lens, TARGET])
        if len(g) < N_MIN:
            continue
        x, y = _rank(g[lens]), _rank(g[TARGET])
        if marginal:
            Z = g[CORE_VALUE].apply(_rank)
            Z = Z.fillna(Z.mean())
            A = np.column_stack([np.ones(len(g)), Z.values])
            try:
                beta, *_ = np.linalg.lstsq(A, x.values, rcond=None)
            except np.linalg.LinAlgError:
                continue
            x = pd.Series(x.values - A @ beta, index=g.index)
        if x.std() == 0 or y.std() == 0:
            continue
        out[qq] = float(np.corrcoef(x, y)[0, 1])
    return pd.Series(out)


def summarize(ic):
    if len(ic) < 4:
        return dict(n_q=len(ic), ic=np.nan, t=np.nan, hit=np.nan)
    return dict(n_q=len(ic), ic=ic.mean(), t=ic.mean() / (ic.std(ddof=1) / np.sqrt(len(ic))),
                hit=(ic > 0).mean())


def report(label, sub, rows):
    for lens, marg in (("fs_pts", False), ("fs_pts", True), ("FSCORE", False), ("ey", False)):
        ic = ic_series(sub, lens, marginal=marg)
        s = summarize(ic)
        s.update(group=label, lens=lens + ("_marginal" if marg else "_raw"),
                 n_obs=int(sub[[lens, TARGET]].dropna().shape[0]))
        rows.append(s)
        # IS/OOS
        for half, m in (("IS 2014-19", ic.index.year <= 2019), ("OOS 2020+", ic.index.year >= 2020)):
            s2 = summarize(ic[m])
            s2.update(group=label + " | " + half, lens=lens + ("_marginal" if marg else "_raw"),
                      n_obs=np.nan)
            rows.append(s2)


rows = []
report("ALL (COMPOUNDER+CYCLICAL)", d, rows)

for var, heavy_is_high in (("FAsset_Eq_P0", True), ("FAssetTurn_P0", False)):
    sub = d[d[var].notna()].copy()
    # per-quarter cross-sectional median split (no look-ahead: uses only that quarter's own names)
    med = sub.groupby("q")[var].transform("median")
    hi = sub[var] >= med
    heavy, light = (hi, ~hi) if heavy_is_high else (~hi, hi)
    report(f"HEAVY by {var}", sub[heavy], rows)
    report(f"LIGHT by {var}", sub[light], rows)

res = pd.DataFrame(rows)[["group", "lens", "n_q", "n_obs", "ic", "t", "hit"]]
res.to_csv(os.path.join(OUT, "fscore_axis_ic.csv"), index=False)

print("\n" + "=" * 96)
print(f"FSCORE AXIS IC vs {TARGET} (T+40) — COMPOUNDER+CYCLICAL, per-quarter Spearman")
print("=" * 96)
print(f"{'group':<34} {'lens':<18} {'Nq':>3} {'Nobs':>6} {'IC':>8} {'t':>7} {'hit':>6}")
for _, r in res.iterrows():
    nb = "" if pd.isna(r["n_obs"]) else f"{int(r['n_obs']):>6}"
    ic = "    n/a" if pd.isna(r["ic"]) else f"{r['ic']:>+8.3f}"
    tt = "    n/a" if pd.isna(r["t"]) else f"{r['t']:>+7.2f}"
    hh = "   n/a" if pd.isna(r["hit"]) else f"{r['hit']*100:>5.0f}%"
    print(f"{r['group']:<34} {r['lens']:<18} {int(r['n_q']):>3} {nb:>6} {ic} {tt} {hh}")

# ---------------------------------------------------------------- HEAVY-vs-LIGHT difference test
print("\n" + "=" * 96)
print("HEAVY minus LIGHT — paired by quarter (same market, same period => the clean comparison)")
print("=" * 96)
for var, heavy_is_high in (("FAsset_Eq_P0", True), ("FAssetTurn_P0", False)):
    sub = d[d[var].notna()].copy()
    med = sub.groupby("q")[var].transform("median")
    hi = sub[var] >= med
    heavy, light = (hi, ~hi) if heavy_is_high else (~hi, hi)
    for lens, marg in (("fs_pts", False), ("fs_pts", True)):
        a, b = ic_series(sub[heavy], lens, marg), ic_series(sub[light], lens, marg)
        j = a.index.intersection(b.index)
        dif = (a[j] - b[j])
        t = dif.mean() / (dif.std(ddof=1) / np.sqrt(len(dif))) if len(dif) > 3 else np.nan
        tag = lens + ("_marginal" if marg else "_raw")
        print(f"  {var:<15} {tag:<18} Nq={len(j):>3}  heavy {a[j].mean():+.3f}  light {b[j].mean():+.3f}"
              f"  diff {dif.mean():+.3f}  t={t:+.2f}  "
              f"{'HEAVY>LIGHT' if dif.mean() > 0 else 'LIGHT>HEAVY'} on {(dif>0).mean()*100:.0f}% of quarters")

# ---------------------------------------------------------------- what the axis actually does
print("\n" + "=" * 96)
print("AXIS MECHANICS — how many names each fs_pts level captures, and their mean fwd return")
print("=" * 96)
for var, heavy_is_high in (("FAsset_Eq_P0", True),):
    sub = d[d[var].notna() & d["fs_pts"].notna() & d[TARGET].notna()].copy()
    med = sub.groupby("q")[var].transform("median")
    hi = sub[var] >= med
    sub["grp"] = np.where(hi if heavy_is_high else ~hi, "HEAVY", "LIGHT")
    for grp, g in sub.groupby("grp"):
        print(f"  {grp}:")
        for lv, gg in g.groupby("fs_pts"):
            print(f"    fs_pts={lv:.0f} (FSCORE {'>=8' if lv==2 else '6-7' if lv==1 else '<6'}): "
                  f"n={len(gg):>5} ({len(gg)/len(g)*100:>4.1f}%)  mean {TARGET} {gg[TARGET].mean():>+6.2f}%")
print(f"\n[written] {OUT}/fscore_axis_ic.csv")
