#!/usr/bin/env python
"""DGC-shaped false alarm: does FSCORE punish companies that are simply in a legitimate CAPEX
phase (cash down, ratios wobble) rather than genuinely deteriorating?

Piotroski's 9 signals are YoY CHANGES; a big investment year mechanically hurts several of them
(CFO/assets, current ratio, asset turnover, leverage if debt-funded). So the a-priori concern is
real. The test that settles it:

  Q1  Is FSCORE systematically LOWER for names in a heavy-capex quarter?          (mechanical bias)
  Q2  INSIDE the heavy-capex group, does a low FSCORE still predict LOW forward
      returns?  If IC collapses to ~0 there, the flag IS a false alarm for capex
      names. If IC survives, the low score is information, not an artifact.       (is it a FALSE alarm?)

Capex intensity = per-quarter cross-sectional rank of CF_Invest_P0 (most negative = heaviest
investment). PIT-joined from ticker_financial by Release_Date. Routes COMPOUNDER+CYCLICAL.
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
TARGET = "profit_2M"
N_MIN = 15

d = pd.read_csv(os.path.join(WORKDIR, "data", "value_panel_2014.csv"), parse_dates=["time"])
d["q"] = d["time"].dt.to_period("Q")
d = d.sort_values("time").groupby(["ticker", "q"], as_index=False).last()
d = d[d["route"].isin(["COMPOUNDER", "CYCLICAL"])].copy()
for c in [TARGET, "FSCORE"]:
    d[c] = pd.to_numeric(d[c], errors="coerce").replace([np.inf, -np.inf], np.nan)

fin = CACHE.query(
    "SELECT t.ticker, t.Release_Date, t.CF_Invest_P0, t.CF_OA_P0 AS cfoq, t.totalAsset_P0 "
    "FROM tav2_bq.ticker_financial t WHERE t.Release_Date IS NOT NULL ORDER BY t.Release_Date")
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
d = pd.merge_asof(d.sort_values("time"), fin.sort_values("Release_Date"), by="ticker",
                  left_on="time", right_on="Release_Date", direction="backward")
d = d[d["CF_Invest_P0"].notna() & d["FSCORE"].notna()].copy()
print(f"[panel] {len(d)} obs with CF_Invest_P0 + FSCORE, {d['q'].nunique()} quarters")

d["fs_pts"] = np.where(d["FSCORE"] >= 8, 2.0, np.where(d["FSCORE"] >= 6, 1.0, 0.0))
# capex tercile per quarter: rank ascending => most NEGATIVE CF_Invest = rank 0 = heaviest capex
d["cx_rank"] = d.groupby("q")["CF_Invest_P0"].rank(pct=True)
d["cx_grp"] = pd.cut(d["cx_rank"], [0, 1 / 3, 2 / 3, 1.0],
                     labels=["HEAVY capex", "mid", "LIGHT capex"], include_lowest=True)

print("\n" + "=" * 90)
print("Q1 — is FSCORE mechanically depressed in a heavy-capex quarter?")
print("=" * 90)
g = d.groupby("cx_grp", observed=True).agg(
    n=("FSCORE", "size"), mean_FSCORE=("FSCORE", "mean"),
    pct_below6=("FSCORE", lambda s: (s < 6).mean()),
    mean_fwd=(TARGET, "mean"))
for b, r in g.iterrows():
    print(f"  {str(b):<12} n={int(r['n']):>5}  mean FSCORE {r['mean_FSCORE']:>4.2f}  "
          f"share FSCORE<6 {r['pct_below6']*100:>5.1f}%  mean {TARGET} {r['mean_fwd']:>+6.2f}%")
hv, lt = d[d.cx_grp == "HEAVY capex"], d[d.cx_grp == "LIGHT capex"]
print(f"\n  HEAVY-capex names are flagged FSCORE<6 {(hv.FSCORE<6).mean()*100:.1f}% of the time vs "
      f"{(lt.FSCORE<6).mean()*100:.1f}% for LIGHT-capex "
      f"=> {'YES, mechanical bias exists' if (hv.FSCORE<6).mean() > (lt.FSCORE<6).mean() else 'NO bias'}")

print("\n" + "=" * 90)
print("Q2 — INSIDE each capex group, does the FSCORE axis still predict? (false alarm or signal?)")
print("=" * 90)


def ic(sub, lens):
    out = {}
    for qq, gg in sub.groupby("q"):
        gg = gg.dropna(subset=[lens, TARGET])
        if len(gg) < N_MIN:
            continue
        x, y = gg[lens].rank(pct=True), gg[TARGET].rank(pct=True)
        if x.std() == 0 or y.std() == 0:
            continue
        out[qq] = float(np.corrcoef(x, y)[0, 1])
    return pd.Series(out)


rows = []
for b in ["HEAVY capex", "mid", "LIGHT capex"]:
    sub = d[d.cx_grp == b]
    for lens in ("fs_pts", "FSCORE"):
        s = ic(sub, lens)
        t = s.mean() / (s.std(ddof=1) / np.sqrt(len(s))) if len(s) > 3 else np.nan
        rows.append(dict(group=b, lens=lens, n_q=len(s), ic=s.mean(), t=t, hit=(s > 0).mean()))
        print(f"  {b:<12} {lens:<8} Nq={len(s):>3}  IC {s.mean():>+7.3f}  t={t:>+6.2f}  "
              f"hit {(s>0).mean()*100:>4.0f}%")
pd.DataFrame(rows).to_csv(os.path.join(OUT, "capex_falsealarm.csv"), index=False)

print("\n" + "=" * 90)
print("Q2b — the sharpest cut: among HEAVY-capex names flagged FSCORE<6, what happened next?")
print("=" * 90)
for b in ["HEAVY capex", "LIGHT capex"]:
    sub = d[(d.cx_grp == b) & d[TARGET].notna()]
    lo, hi = sub[sub.FSCORE < 6], sub[sub.FSCORE >= 6]
    print(f"  {b:<12}  FSCORE<6: n={len(lo):>5} mean {lo[TARGET].mean():>+6.2f}%  |  "
          f"FSCORE>=6: n={len(hi):>5} mean {hi[TARGET].mean():>+6.2f}%  |  "
          f"gap {(hi[TARGET].mean()-lo[TARGET].mean()):>+5.2f}pp")

print("\n" + "=" * 90)
print("Q3 — the specific DGC shape: STRONG operations + heavy investment (CFO high, capex heavy)")
print("=" * 90)
d["cfo_rank"] = d.groupby("q")["cfoq"].rank(pct=True)
dgc = d[(d.cx_grp == "HEAVY capex") & (d.cfo_rank >= 0.67) & d[TARGET].notna()]
oth = d[(d.cx_grp == "HEAVY capex") & (d.cfo_rank < 0.67) & d[TARGET].notna()]
print(f"  DGC-shape (heavy capex + top-tercile CFO): n={len(dgc)}  "
      f"share FSCORE<6 {(dgc.FSCORE<6).mean()*100:.1f}%  mean {TARGET} {dgc[TARGET].mean():+.2f}%")
print(f"  other heavy-capex                        : n={len(oth)}  "
      f"share FSCORE<6 {(oth.FSCORE<6).mean()*100:.1f}%  mean {TARGET} {oth[TARGET].mean():+.2f}%")
lo, hi = dgc[dgc.FSCORE < 6], dgc[dgc.FSCORE >= 6]
if len(lo) > 20 and len(hi) > 20:
    rng = np.random.default_rng(11)
    boot = [rng.choice(hi[TARGET].values, len(hi)).mean() - rng.choice(lo[TARGET].values, len(lo)).mean()
            for _ in range(10000)]
    q5, q95 = np.percentile(boot, [5, 95])
    print(f"  WITHIN the DGC shape: FSCORE<6 n={len(lo)} mean {lo[TARGET].mean():+.2f}%  vs  "
          f"FSCORE>=6 n={len(hi)} mean {hi[TARGET].mean():+.2f}%")
    print(f"    gap {(hi[TARGET].mean()-lo[TARGET].mean()):+.2f}pp  bootstrap CI90 "
          f"[{q5:+.2f}, {q95:+.2f}]pp  P(gap<=0)={np.mean(np.array(boot)<=0):.3f}")
    print("    => a low FSCORE on a strong-CFO heavy-capex name is "
          + ("STILL INFORMATIVE (not a false alarm)" if q5 > 0 else
             "NOT reliably informative (consistent with a FALSE ALARM)"))
print(f"\n[written] {OUT}/capex_falsealarm.csv")
