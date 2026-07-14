# -*- coding: utf-8 -*-
"""mech_scale_drift.py — the crux test (job Taylor_20260714_132942).

CLAIM UNDER TEST
  value_score_v2's pb_z leg is an ABSOLUTE-scaled term: (0.5 - pb_z/2).clip(0,1).
  Every other leg in the selector (ey/cfy/ps in v3latest, and v2's own ey leg) is a
  PERCENTILE, re-normalised every quarter.

  A percentile is immune to a common move: if every bank gets cheaper together, the
  median bank still sits at 0.5, so the sector's slot count in the cross-route top-30
  is untouched. An ABSOLUTE term is not immune: when the whole sector's PB drifts up
  against its own 5Y history, EVERY bank's pb_z rises together, EVERY bank's score
  falls together, and banks get expelled from the top-30 en masse -- for a reason that
  has nothing to do with any bank being relatively less attractive.

  If true, "rank banks correctly among banks" silently buys an UNCONTROLLED
  SECTOR-TIMING BET, priced off a 5Y-trailing book-value average.

TESTS
  1  Is bank pb_z a common factor? (share of variance explained by the quarterly mean)
  2  Does the sector's median pb_z drive the bank SLOT COUNT delta (route3 - latest)?
  3  Was that timing bet a good one? (bank-slot count vs the sector's realised fwd return)
  4  Counterfactual: replace the absolute pb_z leg with a WITHIN-ROUTE PERCENTILE of the
     same pb_z -- same economic claim ("cheap for a bank"), no absolute scale. Does the
     en-masse expulsion disappear?

Research/diagnostic only. Reads frozen panel + already-built member CSVs. No production touch.
Run: source ./wc_env.sh && $DNA_PYEXE mike/agents/Taylor/route_exp/mech_scale_drift.py
"""
import warnings; warnings.filterwarnings("ignore")
import os
import numpy as np, pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
OUT = os.path.join(WORKDIR, "mike", "agents", "Taylor", "route_exp")
IS_END = pd.Timestamp("2019-12-31")

P = pd.read_csv(os.path.join(WORKDIR, "data", "value_panel_2014.csv"), parse_dates=["time"])
P["profit_2M"] = P["profit_2M"].replace([np.inf, -np.inf], np.nan)
P["q"] = P["time"].dt.to_period("Q")
P = P.sort_values("time").groupby(["ticker", "q"], as_index=False).last()
P["qs"] = P["q"].dt.start_time
BANK = P[P.route == "BANK"].copy()

print("=" * 92)
print("[1] IS pb_z A COMMON FACTOR ACROSS BANKS? (if yes, an absolute leg moves the whole sector)")
print("=" * 92)
bz = BANK.dropna(subset=["pb_z"])
qmean = bz.groupby("q")["pb_z"].mean()
bz = bz.assign(qmean=bz["q"].map(qmean))
bz["demeaned"] = bz["pb_z"] - bz["qmean"]
var_total = bz["pb_z"].var()
var_within = bz["demeaned"].var()
var_common = var_total - var_within
print(f"  total var(pb_z) across all bank-quarters : {var_total:.4f}")
print(f"  var WITHIN quarter (bank vs bank)        : {var_within:.4f}  ({var_within/var_total:.1%})")
print(f"  var of the quarterly MEAN (common move)  : {qmean.var():.4f}")
print(f"  => share of pb_z variance that is a COMMON sector move: {var_common/var_total:.1%}")
print(f"\n  quarterly mean pb_z of the BANK sector, range {qmean.min():+.2f} .. {qmean.max():+.2f} "
      f"(swing {qmean.max()-qmean.min():.2f} z-units)")
print("  the (0.5 - pb_z/2) leg turns that swing into a score move of "
      f"{(qmean.max()-qmean.min())/2:.2f} -- against a leg whose full range is 0..1.")
sect = qmean.to_frame("mean_pbz")
sect["median_pbz"] = bz.groupby("q")["pb_z"].median()
sect["frac_golden(pb_z<=-1)"] = bz.groupby("q")["pb_z"].apply(lambda s: (s <= -1).mean()).round(3)
sect["year"] = sect.index.to_timestamp().year
print("\n  sector median pb_z by year:")
print(sect.groupby("year")[["median_pbz", "frac_golden(pb_z<=-1)"]].mean().round(3).to_string())
sect.to_csv(os.path.join(OUT, "mech_F_sector_pbz.csv"))

print("\n" + "=" * 92)
print("[2] DOES THE SECTOR'S pb_z DRIVE THE BANK SLOT COUNT? (route3 vs latest, per quarter)")
print("=" * 92)
route_of = P.sort_values("time").groupby("ticker")["route"].last()


def bank_count(fn):
    m = pd.read_csv(os.path.join(OUT, fn), parse_dates=["quarter"])
    m["route"] = m.ticker.map(route_of)
    c = m.groupby("quarter").apply(lambda g: (g.route == "BANK").sum())
    return c.rename(fn.split("_", 1)[1].replace(".csv", ""))


c_lat = bank_count("members_v3latest.csv")
c_rt3 = bank_count("members_v3route3.csv")
c_yld = bank_count("members_yieldcombo.csv")
C = pd.concat([c_yld, c_lat, c_rt3], axis=1)
C.columns = ["yieldcombo", "v3latest", "v3route3"]
C["d_route_fix"] = C["v3route3"] - C["v3latest"]
C["q"] = C.index.to_period("Q")
C = C.join(sect[["median_pbz"]], on="q")
C["year"] = C.index.year
print(C[["yieldcombo", "v3latest", "v3route3", "d_route_fix", "median_pbz"]].to_string())
r = C[["d_route_fix", "median_pbz"]].dropna()
rho = r["d_route_fix"].corr(r["median_pbz"], method="spearman")
print(f"\n  Spearman( bank-slot delta caused by the route fix , sector median pb_z ) = {rho:+.3f}  (n={len(r)})")
print("  negative => the richer the sector looks vs its OWN 5Y history, the more banks the")
print("              route fix expels -- a sector-timing bet nobody asked for.")
C.to_csv(os.path.join(OUT, "mech_F_bank_slot_counts.csv"))

print("\n" + "=" * 92)
print("[3] WAS THE TIMING BET ANY GOOD? (bank-slot count vs the sector's realised fwd return)")
print("=" * 92)
sect_ret = BANK.dropna(subset=["profit_2M"]).groupby("q")["profit_2M"].mean().rename("bank_fwd2M")
nonbank_ret = P[(P.route != "BANK")].dropna(subset=["profit_2M"]).groupby("q")["profit_2M"].mean().rename("nonbank_fwd2M")
T = C.join(sect_ret, on="q").join(nonbank_ret, on="q")
T["bank_minus_nonbank"] = T["bank_fwd2M"] - T["nonbank_fwd2M"]
tt = T[["d_route_fix", "bank_minus_nonbank"]].dropna()
rho2 = tt["d_route_fix"].corr(tt["bank_minus_nonbank"], method="spearman")
print(f"  Spearman( bank-slot delta , bank-minus-nonbank fwd2M that quarter ) = {rho2:+.3f} (n={len(tt)})")
print("  ~0 or negative => the fix cut bank exposure with no ability to tell good from bad quarters.")
for label, sub in (("IS 2014-19", T[T.index <= IS_END]), ("OOS 2020+", T[T.index > IS_END])):
    s = sub[["d_route_fix", "bank_minus_nonbank"]].dropna()
    if len(s) > 3:
        print(f"    {label}: rho {s['d_route_fix'].corr(s['bank_minus_nonbank'], method='spearman'):+.3f} "
              f"(n={len(s)}) | mean d_slots {s.d_route_fix.mean():+.2f} | "
              f"mean bank-minus-nonbank {s.bank_minus_nonbank.mean():+.2f}pp")
T.to_csv(os.path.join(OUT, "mech_F_timing_bet.csv"))

print("\n" + "=" * 92)
print("[4] COUNTERFACTUAL: same economic claim, PERCENTILE scale instead of ABSOLUTE")
print("=" * 92)
print("  If the damage is the ABSOLUTE scale (not the pb_z idea), then ranking banks on a")
print("  WITHIN-ROUTE PERCENTILE of pb_z should keep the sector's slot count stable.")
b2 = BANK.dropna(subset=["pb_z"]).copy()
b2["abs_leg"] = (0.5 - b2["pb_z"] / 2.0).clip(0, 1)
b2["pct_leg"] = b2.groupby("q")["pb_z"].transform(lambda s: (-s).rank(pct=True))
ab = b2.groupby("q")["abs_leg"].mean()
pc = b2.groupby("q")["pct_leg"].mean()
print(f"  sector-mean of the ABSOLUTE leg (0.5-pb_z/2): mean {ab.mean():.3f}  sd ACROSS QUARTERS {ab.std():.3f}"
      f"  range {ab.min():.3f}..{ab.max():.3f}")
print(f"  sector-mean of a PERCENTILE leg of same pb_z: mean {pc.mean():.3f}  sd ACROSS QUARTERS {pc.std():.3f}"
      f"  range {pc.min():.3f}..{pc.max():.3f}")
print(f"\n  => the absolute leg drags the WHOLE bank sector's score up and down by "
      f"{ab.max()-ab.min():.2f} over the sample;")
print(f"     the percentile leg is pinned at ~0.5 by construction ({pc.max()-pc.min():.2f} range) "
      "-- it can only ever say WHICH bank, never HOW MANY banks.")
pd.DataFrame({"abs_leg_mean": ab, "pct_leg_mean": pc}).to_csv(os.path.join(OUT, "mech_F_leg_scales.csv"))
print("\ndone.")
