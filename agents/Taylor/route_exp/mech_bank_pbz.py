# -*- coding: utf-8 -*-
"""mech_bank_pbz.py — MECHANISM study (job Taylor_20260714_132942).

Question (user): ranking banks WITHIN their own route on pb_z is more economically correct
than ranking them against manufacturers on 1/PCF (a metric we KNOW is wrong for banks) —
so why does the correct one LOSE?

Research/diagnostic only. Reads the frozen PIT panel + already-built member CSVs.
Writes NOTHING production reads. No new backtest arms.

Tests
  A  Linear rank-IC of pb_z WITHIN the BANK route vs fwd profit_2M — full / IS / OOS / per-year.
     Same construction as ic_panel_8l: collapse (ticker, quarter)=last, per-quarter Spearman,
     t = mean/(sd/sqrt(Nq)). Compare against ey=1/PE and cfy=1/PCF measured the same way.
  B  Non-linearity: pb_z quintile (within BANK, per quarter) -> mean fwd return. Is the signal
     monotone (usable as a rank) or concentrated in the pb_z<=-1 "golden cell" tail only?
  C  H1: fundamentals of the BANK names yieldcombo (1/PCF) picks vs v3latest picks.
  D  H2: the lowest-pb_z bank each quarter — what did it actually return?

Run: source ./wc_env.sh && $DNA_PYEXE mike/agents/Taylor/route_exp/mech_bank_pbz.py
"""
import warnings; warnings.filterwarnings("ignore")
import os
import numpy as np, pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
OUT = os.path.join(WORKDIR, "mike", "agents", "Taylor", "route_exp")
IS_END = pd.Timestamp("2019-12-31")

P = pd.read_csv(os.path.join(WORKDIR, "data", "value_panel_2014.csv"), parse_dates=["time"])
# profit_2M is ALREADY in percent (min -100, median 0) and carries +inf rows (division blowups).
# inf poisons every mean; drop it rather than clip so no fabricated number enters a table.
P["profit_2M"] = P["profit_2M"].replace([np.inf, -np.inf], np.nan)
P["q"] = P["time"].dt.to_period("Q")
# one obs per (ticker, quarter) = last  -- exactly what custom_basket._score_v3 eats
P = P.sort_values("time").groupby(["ticker", "q"], as_index=False).last()
P["year"] = P["time"].dt.year

# lens construction identical to the selector's: yields, negatives -> NaN (no reward)
for src, dst in (("PE", "ey"), ("PCF", "cfy"), ("PS", "ps")):
    P[dst] = np.where(P[src] > 0, 1.0 / P[src], np.nan)
# pb_z: negative = cheap-vs-own-history. Sign-flip so "higher = cheaper" like the yields,
# matching value_score_v2's (0.5 - pb_z/2) direction.
P["pbz_cheap"] = -P["pb_z"]

BANK = P[P["route"] == "BANK"].copy()
print("=" * 92)
print(f"BANK route panel: {len(BANK)} (ticker,quarter) obs | {BANK.ticker.nunique()} names | "
      f"{BANK.q.nunique()} quarters | avg {len(BANK)/BANK.q.nunique():.1f} names/quarter")
print(f"  names: {sorted(BANK.ticker.unique())}")


def ic_table(df, lens, target="profit_2M", by=None):
    """per-quarter cross-sectional Spearman IC; returns (mean, t, hit%, Nq, avg_n)."""
    rows = []
    for q, g in df.groupby("q"):
        g = g[[lens, target]].dropna()
        if len(g) < 4:          # need a real cross-section
            continue
        ic = g[lens].rank().corr(g[target].rank())
        if pd.notna(ic):
            rows.append({"q": q, "ic": ic, "n": len(g), "t": g.iloc[0].name})
    if not rows:
        return None
    r = pd.DataFrame(rows)
    r["date"] = r["q"].dt.start_time
    return r


def summarise(r, label):
    if r is None or len(r) < 3:
        return {"lens": label, "ic": np.nan, "t": np.nan, "hit": np.nan, "nq": 0, "avg_n": np.nan}
    m, sd, n = r.ic.mean(), r.ic.std(ddof=1), len(r)
    return {"lens": label, "ic": round(m, 4), "t": round(m / (sd / np.sqrt(n)), 2),
            "hit": round((r.ic > 0).mean(), 3), "nq": n, "avg_n": round(r.n.mean(), 1)}


# ---------------------------------------------------------------- A: linear IC within BANK
print("\n" + "=" * 92)
print("[A] LINEAR rank-IC WITHIN the BANK route (target = profit_2M, T+40 fwd)")
print("=" * 92)
rows = []
for lens, label in (("pbz_cheap", "pb_z (cheap=high)"), ("ey", "ey = 1/PE"), ("cfy", "cfy = 1/PCF")):
    r = ic_table(BANK, lens)
    if r is None:
        continue
    full = summarise(r, label)
    is_ = summarise(r[r.date <= IS_END], label)
    oos = summarise(r[r.date > IS_END], label)
    rows.append({"lens": label, "IC_full": full["ic"], "t_full": full["t"], "hit_full": full["hit"],
                 "Nq": full["nq"], "avg_n": full["avg_n"],
                 "IC_IS": is_["ic"], "t_IS": is_["t"], "IC_OOS": oos["ic"], "t_OOS": oos["t"]})
A = pd.DataFrame(rows)
print(A.to_string(index=False))
A.to_csv(os.path.join(OUT, "mech_A_bank_linear_ic.csv"), index=False)

print("\n--- per-YEAR IC within BANK (H4: did a regime break?) ---")
yr_rows = []
for lens, label in (("pbz_cheap", "pb_z"), ("ey", "ey"), ("cfy", "cfy")):
    r = ic_table(BANK, lens)
    if r is None:
        continue
    r["year"] = r.date.dt.year
    for y, g in r.groupby("year"):
        yr_rows.append({"lens": label, "year": y, "ic": round(g.ic.mean(), 3), "nq": len(g)})
Y = pd.DataFrame(yr_rows).pivot(index="year", columns="lens", values="ic")
print(Y.to_string())
Y.to_csv(os.path.join(OUT, "mech_A_bank_ic_by_year.csv"))

# ---------------------------------------------------------------- B: non-linearity
print("\n" + "=" * 92)
print("[B] NON-LINEARITY: is pb_z a RANK or only a TAIL flag? (within-BANK pb_z buckets)")
print("=" * 92)
b = BANK.dropna(subset=["pb_z", "profit_2M"]).copy()
# absolute economic buckets (the golden-cell definition lives in absolute pb_z, not quintiles)
bins = [-99, -1.0, -0.3, 0.3, 1.0, 99]
lab = ["<=-1 (golden cell)", "-1..-0.3 (cheap)", "-0.3..0.3 (normal)", "0.3..1 (rich)", ">1 (very rich)"]
b["bucket"] = pd.cut(b["pb_z"], bins=bins, labels=lab)
agg = b.groupby("bucket").agg(n=("profit_2M", "size"), fwd2M=("profit_2M", "mean"),
                              med=("profit_2M", "median"))
agg["fwd2M"] = agg["fwd2M"].round(2); agg["med"] = agg["med"].round(2)
print("ALL PERIOD:"); print(agg.to_string())
for tag, sub in (("IS 2014-19", b[b.time <= IS_END]), ("OOS 2020+", b[b.time > IS_END])):
    a2 = sub.groupby("bucket").agg(n=("profit_2M", "size"), fwd2M=("profit_2M", "mean"))
    a2["fwd2M"] = a2["fwd2M"].round(2)
    print(f"\n{tag}:"); print(a2.to_string())
agg.to_csv(os.path.join(OUT, "mech_B_pbz_buckets.csv"))

# monotonicity check: within-quarter quintile spread
print("\n--- within-quarter pb_z quintile (Q1=most expensive .. Q5=cheapest) mean fwd2M % ---")
qrows = []
for q, g in b.groupby("q"):
    g = g.dropna(subset=["pb_z"])
    if len(g) < 5:
        continue
    g = g.copy()
    g["quint"] = pd.qcut(g["pbz_cheap"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    for k, gg in g.groupby("quint"):
        qrows.append({"q": q, "quint": int(k), "fwd": gg.profit_2M.mean(),
                      "is_": g.time.iloc[0] <= IS_END})
Q = pd.DataFrame(qrows)
piv = Q.groupby("quint").fwd.mean()
piv_is = Q[Q.is_].groupby("quint").fwd.mean()
piv_oos = Q[~Q.is_].groupby("quint").fwd.mean()
print(pd.DataFrame({"ALL": piv.round(2), "IS": piv_is.round(2), "OOS": piv_oos.round(2)}).to_string())
print(f"  Q5-Q1 spread: ALL {piv[5]-piv[1]:+.2f}pp | IS {piv_is[5]-piv_is[1]:+.2f}pp | "
      f"OOS {piv_oos[5]-piv_oos[1]:+.2f}pp")
Q.to_csv(os.path.join(OUT, "mech_B_pbz_quintiles.csv"), index=False)

# ---------------------------------------------------------------- C: who gets picked
print("\n" + "=" * 92)
print("[C] H1: which BANKS does each selector pick, and how do they differ fundamentally?")
print("=" * 92)
mem_y = pd.read_csv(os.path.join(OUT, "members_yieldcombo.csv"), parse_dates=["quarter"])
mem_v = pd.read_csv(os.path.join(OUT, "members_v3latest.csv"), parse_dates=["quarter"])
mem_r = pd.read_csv(os.path.join(OUT, "members_v3route3.csv"), parse_dates=["quarter"])

route_of = P.sort_values("time").groupby("ticker")["route"].last()
P["qs"] = P["q"].dt.start_time
feat = P.set_index(["ticker", "qs"])


def bank_picks(mem, tag):
    m = mem.copy()
    m["route"] = m.ticker.map(route_of)
    mb = m[m.route == "BANK"]
    j = mb.join(feat, on=["ticker", "quarter"], rsuffix="_p")
    return j.assign(sel=tag)


bp = pd.concat([bank_picks(mem_y, "yieldcombo"), bank_picks(mem_v, "v3latest"),
                bank_picks(mem_r, "v3route3")], ignore_index=True)
cols = ["pb_z", "PB", "PE", "PCF", "ey", "cfy", "ROE_Min3Y", "CF_OA_P0", "CF_OA_3Y",
        "FSCORE", "profit_2M"]
cmp = bp.groupby("sel")[cols].mean().round(3)
cmp["n_picks"] = bp.groupby("sel").size()
cmp["banks_per_q"] = (bp.groupby("sel").size() / bp.groupby("sel")["quarter"].nunique()).round(2)
print(cmp.to_string())
cmp.to_csv(os.path.join(OUT, "mech_C_bank_pick_profile.csv"))

print("\n--- fwd2M of the BANK slots each selector holds (IS / OOS) ---")
for tag, g in bp.groupby("sel"):
    fi = g[g.quarter <= IS_END].profit_2M.mean()
    fo = g[g.quarter > IS_END].profit_2M.mean()
    print(f"  {tag:12s} n={len(g):4d}  fwd2M ALL {g.profit_2M.mean():+.2f}%  "
          f"IS {fi:+.2f}%  OOS {fo:+.2f}%")

print("\n--- most-picked BANK names per selector ---")
for tag, g in bp.groupby("sel"):
    top = g.ticker.value_counts().head(8)
    print(f"  {tag:12s}: " + ", ".join(f"{t}({c})" for t, c in top.items()))

# ---------------------------------------------------------------- D: the cheapest bank
print("\n" + "=" * 92)
print("[D] H2: the LOWEST-pb_z bank each quarter — 'cheap' or 'distressed for a reason'?")
print("=" * 92)
d = BANK.dropna(subset=["pb_z"]).copy()
idx = d.groupby("q")["pb_z"].idxmin()
low = d.loc[idx, ["q", "ticker", "pb_z", "PB", "PE", "ROE_Min3Y", "profit_2M"]].copy()
low["fwd2M_%"] = low["profit_2M"].round(2)
low["q"] = low["q"].astype(str)
print(low[["q", "ticker", "pb_z", "PB", "ROE_Min3Y", "fwd2M_%"]].to_string(index=False))
print(f"\n  mean fwd2M of the cheapest-pb_z bank: {low.profit_2M.mean():+.2f}%")
print(f"  mean fwd2M of ALL banks             : {BANK.profit_2M.mean():+.2f}%")
low.to_csv(os.path.join(OUT, "mech_D_cheapest_bank.csv"), index=False)
print("\ndone.")
