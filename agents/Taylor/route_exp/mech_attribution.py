# -*- coding: utf-8 -*-
"""mech_attribution.py — WHERE does the route fix lose? (job Taylor_20260714_132942)

Paradox found in mech_bank_pbz.py [C]: v3route3's BANK picks earn MORE per slot than
v3latest's (+6.65% vs +5.79% fwd2M) — yet v3route3's vehicle is 2.38pp/yr WORSE.
A better pick that produces a worse basket means the damage is not in bank-vs-bank ranking.

Brinson-style decomposition of the basket's mean forward return, per arm:
    R = share_bank * ret_bank + share_nonbank * ret_nonbank
    dR(route3 - latest) = ALLOCATION (d_share * ret)  +  SELECTION (share * d_ret)  + interaction

ALLOCATION = the score change moved how many bank slots clear the cross-route top-30 cut.
SELECTION  = the score change moved WHICH banks / which non-banks got picked.

If the loss is ALLOCATION, the user's premise (within-route ranking is more correct) is
intact — but irrelevant, because the machine consuming the score makes a CROSS-route cut.

Research/diagnostic only. Reads frozen panel + already-built member CSVs.
Run: source ./wc_env.sh && $DNA_PYEXE mike/agents/Taylor/route_exp/mech_attribution.py
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
FIN = {"BANK", "INSURANCE", "SECURITIES"}
feat = P.set_index(["ticker", "qs"])[["profit_2M", "route", "pb_z", "PE", "PB"]]

ARMS = {"yieldcombo": "members_yieldcombo.csv",
        "v3latest": "members_v3latest.csv",
        "v3route3": "members_v3route3.csv"}


def load(tag):
    m = pd.read_csv(os.path.join(OUT, ARMS[tag]), parse_dates=["quarter"])
    j = m.join(feat, on=["ticker", "quarter"])
    j["is_fin"] = j["route"].isin(FIN)
    j["arm"] = tag
    return j


A = pd.concat([load(t) for t in ARMS], ignore_index=True)
A = A.dropna(subset=["profit_2M"])          # need a realised forward return to attribute

print("=" * 92)
print("[1] BASKET COMPOSITION + PER-SLOT RETURN (equal-weight proxy of the top-30 cut)")
print("=" * 92)


def profile(df, tag):
    n_q = df["quarter"].nunique()
    fin, non = df[df.is_fin], df[~df.is_fin]
    return {"arm": tag, "slots/q": round(len(df) / n_q, 2),
            "fin/q": round(len(fin) / n_q, 2), "share_fin": round(len(fin) / len(df), 4),
            "ret_fin": round(fin.profit_2M.mean(), 3),
            "ret_nonfin": round(non.profit_2M.mean(), 3),
            "ret_basket": round(df.profit_2M.mean(), 3)}


rows = [profile(g, t) for t, g in A.groupby("arm")]
prof = pd.DataFrame(rows).set_index("arm").loc[list(ARMS)]
print(prof.to_string())
prof.to_csv(os.path.join(OUT, "mech_E_composition.csv"))

print("\n" + "=" * 92)
print("[2] BRINSON DECOMPOSITION — v3route3 minus v3latest (the CLEAN route-fix ablation)")
print("=" * 92)


def brinson(df, base_tag, new_tag, label):
    b, n = df[df.arm == base_tag], df[df.arm == new_tag]
    wb, wn = (b.is_fin).mean(), (n.is_fin).mean()
    rb_f, rb_n = b[b.is_fin].profit_2M.mean(), b[~b.is_fin].profit_2M.mean()
    rn_f, rn_n = n[n.is_fin].profit_2M.mean(), n[~n.is_fin].profit_2M.mean()
    R_b = wb * rb_f + (1 - wb) * rb_n
    R_n = wn * rn_f + (1 - wn) * rn_n
    alloc = (wn - wb) * rb_f + ((1 - wn) - (1 - wb)) * rb_n      # weight moved, base returns
    selec = wb * (rn_f - rb_f) + (1 - wb) * (rn_n - rb_n)        # returns moved, base weights
    inter = (R_n - R_b) - alloc - selec
    return {"window": label, "share_fin_base": round(wb, 4), "share_fin_new": round(wn, 4),
            "d_share_fin": round(wn - wb, 4),
            "ret_fin_base": round(rb_f, 3), "ret_fin_new": round(rn_f, 3),
            "ret_nonfin_base": round(rb_n, 3), "ret_nonfin_new": round(rn_n, 3),
            "R_base": round(R_b, 3), "R_new": round(R_n, 3), "dR": round(R_n - R_b, 3),
            "ALLOCATION": round(alloc, 3), "SELECTION": round(selec, 3),
            "interaction": round(inter, 3)}


brows = []
for label, sub in (("FULL", A), ("IS 2014-19", A[A.quarter <= IS_END]), ("OOS 2020+", A[A.quarter > IS_END])):
    brows.append(brinson(sub, "v3latest", "v3route3", label))
B = pd.DataFrame(brows)
print(B[["window", "share_fin_base", "share_fin_new", "d_share_fin", "R_base", "R_new", "dR",
         "ALLOCATION", "SELECTION", "interaction"]].to_string(index=False))
print("\n  detail (per-slot fwd2M %):")
print(B[["window", "ret_fin_base", "ret_fin_new", "ret_nonfin_base", "ret_nonfin_new"]].to_string(index=False))
B.to_csv(os.path.join(OUT, "mech_E_brinson.csv"), index=False)

print("\n" + "=" * 92)
print("[3] THE DISPLACED NAMES — who lost a slot when banks were re-scored?")
print("=" * 92)
lat = A[A.arm == "v3latest"][["quarter", "ticker", "route", "profit_2M", "is_fin"]]
rt3 = A[A.arm == "v3route3"][["quarter", "ticker", "route", "profit_2M", "is_fin"]]
key_l = set(map(tuple, lat[["quarter", "ticker"]].values))
key_r = set(map(tuple, rt3[["quarter", "ticker"]].values))
dropped = lat[[t not in key_r for t in map(tuple, lat[["quarter", "ticker"]].values)]]
added = rt3[[t not in key_l for t in map(tuple, rt3[["quarter", "ticker"]].values)]]
print(f"  slots DROPPED by the route fix : n={len(dropped):4d}  fwd2M {dropped.profit_2M.mean():+.2f}%  "
      f"(fin {dropped.is_fin.sum()} / nonfin {(~dropped.is_fin).sum()})")
print(f"  slots ADDED   by the route fix : n={len(added):4d}  fwd2M {added.profit_2M.mean():+.2f}%  "
      f"(fin {added.is_fin.sum()} / nonfin {(~added.is_fin).sum()})")
print(f"  NET on the churned slots       : {added.profit_2M.mean() - dropped.profit_2M.mean():+.2f}pp")
for tag, sub in (("IS", slice(None)),):
    pass
for label, qsel in (("IS 2014-19", lambda d: d.quarter <= IS_END), ("OOS 2020+", lambda d: d.quarter > IS_END)):
    dd, aa = dropped[qsel(dropped)], added[qsel(added)]
    print(f"    {label}: dropped {dd.profit_2M.mean():+.2f}% (n={len(dd)}) -> added "
          f"{aa.profit_2M.mean():+.2f}% (n={len(aa)}) = {aa.profit_2M.mean()-dd.profit_2M.mean():+.2f}pp")

print("\n  dropped-name route mix:"); print("   ", dropped.route.value_counts().head(8).to_dict())
print("  added-name route mix  :"); print("   ", added.route.value_counts().head(8).to_dict())
dropped.assign(side="dropped").to_csv(os.path.join(OUT, "mech_E_dropped.csv"), index=False)
added.assign(side="added").to_csv(os.path.join(OUT, "mech_E_added.csv"), index=False)

print("\n" + "=" * 92)
print("[4] CROSS-ROUTE COMPARABILITY — what a WITHIN-route percentile throws away")
print("=" * 92)
# value_score_v2's absolute leg is ey RANKED WITHIN ROUTE. Two names with the same
# within-route percentile can have wildly different ABSOLUTE cheapness. Quantify.
P["ey"] = np.where(P["PE"] > 0, 1.0 / P["PE"], np.nan)
liq = P.dropna(subset=["ey", "profit_2M"]).copy()
liq["ey_pct_within_route"] = liq.groupby(["q", "route"])["ey"].transform(lambda s: s.rank(pct=True))
liq["ey_pct_global"] = liq.groupby("q")["ey"].transform(lambda s: s.rank(pct=True))
liq["is_fin"] = liq["route"].isin(FIN)
top = liq[liq.ey_pct_within_route >= 0.8]
print("  Names in the TOP-20% of their OWN route by 1/PE — where do they sit GLOBALLY?")
g = top.groupby("is_fin").agg(n=("ey", "size"), ey_mean=("ey", "mean"),
                              global_pct_mean=("ey_pct_global", "mean"),
                              fwd2M=("profit_2M", "mean")).round(3)
g.index = ["non-financial", "financial"]
print(g.to_string())
print("\n  => a within-route percentile says 'cheap for a bank'. The top-30 cut needs")
print("     'cheap, full stop'. Those are different questions; the percentile cannot answer the second.")
g.to_csv(os.path.join(OUT, "mech_E_crossroute.csv"))
print("\ndone.")
