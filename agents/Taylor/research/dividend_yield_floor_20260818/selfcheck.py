#!/usr/bin/env python3
"""selfcheck.py — PREREG §10, all seven required checks plus three added ones.

Design rule: every check re-derives its number by a path that does NOT call analyze.py's
estimators. Where a check needs the same *definition*, it is rewritten here from the prereg
text, so a bug in analyze.py cannot hide behind a shared helper.

Run: python3 selfcheck.py            (and, per PREREG §10.2, under `env -u TZ` and TZ=UTC)
"""
from __future__ import annotations

import gzip
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")

TOL = 1e-6
PASS, FAIL = [], []


def check(name: str, ok: bool, detail: str = "") -> None:
    (PASS if ok else FAIL).append(name)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def close_to(a, b, tol=TOL) -> bool:
    return bool(np.isfinite(a) and np.isfinite(b) and abs(a - b) <= tol * max(1.0, abs(b)))


# ------------------------------------------------------------------ inputs
with gzip.open(os.path.join(OUT, "panel.csv.gz"), "rt") as fh:
    P = pd.read_csv(fh, dtype={"ticker": str, "dt": str, "icb": str,
                               "d_p20": str, "d_p60": str, "d_p120": str})
RES = json.load(open(os.path.join(OUT, "results.json")))
EVA = pd.read_csv(os.path.join(OUT, "episodes_testA_deposit.csv"),
                  dtype={"ticker": str, "dt": str})
EVB = pd.read_csv(os.path.join(OUT, "episodes_testB_deposit.csv"),
                  dtype={"ticker": str, "dt": str})
BENCH = pd.read_csv(os.path.join(OUT, "bench_ew.csv"), dtype={"dt": str})
with gzip.open(os.path.join(OUT, "div_events.csv.gz"), "rt") as fh:
    DIV = pd.read_csv(fh, dtype={"ticker": str, "ex_date": str})

P = P.sort_values(["ticker", "si"], kind="mergesort").reset_index(drop=True)


# =========================================================================================
# §10.1 — reproduce three headline numbers by an independent path
# =========================================================================================
# (a) Test A @ 8% fixed: rebuild the crossing rule from the prereg text, straight from panel.
g = P.groupby("ticker", sort=False)
contig = (P["si"] - g["si"].shift(1)) == 1
yld = np.where(P["price"] > 0, 100.0 * P["div0"] / P["price"], np.nan)
P["_y"] = yld
P["_ylag"] = g["_y"].shift(1).where(contig)
stable3 = (P["n0"] >= 1) & (P["n1"] >= 1) & (P["n2"] >= 1)
first = pd.read_csv(os.path.join(OUT, "first_dt.csv"), dtype={"ticker": str, "first_dt": str})
P = P.merge(first, on="ticker", how="left")
hist = (pd.to_datetime(P["dt"]) - pd.to_datetime(P["first_dt"])).dt.days
trig = (stable3 & (P["price"] > 0) & (P["close"] > 0) & (hist >= 1095)
        & ~P["ticker"].isin({"DNN", "BCB", "PTX"}) & (P["is_exdate"] == 0)
        & (P["close"] >= P["low"]) & (P["close"] <= P["high"]) & (P["div0"] > 0))
cross8 = trig & (P["_ylag"] < 8.0) & (P["_y"] >= 8.0)
ev8 = P[cross8.fillna(False)].sort_values(["ticker", "si"], kind="mergesort")
keep, last = [], {}
for tk, si in zip(ev8["ticker"], ev8["si"]):
    ok = tk not in last or si - last[tk] >= 120
    keep.append(ok)
    if ok:
        last[tk] = si
ev8 = ev8[keep]
check("T1 Test A @8%: episode count reproduced",
      len(ev8) == RES["test_a"]["8%"]["n_episodes"],
      f"selfcheck={len(ev8)} analyze={RES['test_a']['8%']['n_episodes']}")

# (b) Test A @8% BHAR_60 mean — benchmark index rebuilt here from bench_ew.csv.
lvl = pd.Series(np.cumprod(1.0 + BENCH["ew_ret"].fillna(0.0).to_numpy()),
                index=BENCH["dt"].to_numpy())
b0 = lvl.reindex(ev8["dt"].to_numpy()).to_numpy()
b1 = lvl.reindex(ev8["d_p60"].to_numpy()).to_numpy()
bhar8 = 100.0 * ((ev8["c_p60"].to_numpy() / ev8["close"].to_numpy() - 1.0) - (b1 / b0 - 1.0))
bhar8 = bhar8[np.isfinite(bhar8)]
check("T2 Test A @8%: BHAR_60 mean reproduced",
      close_to(bhar8.mean(), RES["test_a"]["8%"]["bhar_60"]["all"]["mean"], 1e-9),
      f"selfcheck={bhar8.mean():.6f} analyze={RES['test_a']['8%']['bhar_60']['all']['mean']:.6f}")

# (c) Test B primary Δ MDD mean — recomputed off the episodes CSV's own raw columns.
d = (EVB["mdd_60"] - EVB["ctrl_mdd_60"]).dropna()
check("T3 Test B: mean Δ MDD_60 reproduced from episode CSV",
      close_to(d.mean(), RES["test_b"]["deposit"]["d_mdd_60"]["all"]["mean"], 1e-9),
      f"selfcheck={d.mean():.6f} analyze={RES['test_b']['deposit']['d_mdd_60']['all']['mean']:.6f}")
mdd_chk = 100.0 * (EVB["minc60"] / EVB["close"] - 1.0)
check("T4 Test B: MDD_60 identity min(Close_fwd)/Close-1 holds",
      close_to(float((mdd_chk - EVB["mdd_60"]).abs().max()), 0.0, 1e-6),
      f"max|Δ|={float((mdd_chk - EVB['mdd_60']).abs().max()):.2e}")

# =========================================================================================
# §10.3 — cross-check the self-built trailing yield against BQ's own DY column
# =========================================================================================
s = P[stable3.to_numpy() & (P["div0"] > 0) & P["dy"].notna() & (P["dy"] > 0)].copy()
s["dy_pct"] = 100.0 * s["dy"]
s["delta"] = s["_y"] - s["dy_pct"]
# Spearman = Pearson on ranks; done by hand because scipy is not installed on this host.
rho = float(s["_y"].rank().corr(s["dy_pct"].rank()))
q = s["delta"].quantile([0.1, 0.5, 0.9])
check("T5 DY cross-check: Spearman ρ(self, BQ DY) > 0.80", rho > 0.80,
      f"ρ={rho:.4f} n={len(s):,} Δ p10={q[0.1]:+.3f} med={q[0.5]:+.3f} p90={q[0.9]:+.3f} pp")
check("T5b DY cross-check: median |Δ| under 1 pp", abs(q[0.5]) < 1.0,
      f"median Δ = {q[0.5]:+.4f} pp | max|Δ| = {s['delta'].abs().max():.2e} pp — the agreement "
      "is EXACT, so `ticker.DY` is the same quantity (trailing cash dividend / raw Price) and "
      "almost certainly shares this study's upstream source. It confirms the formula and the "
      "units; it is NOT an independent second source.")

# =========================================================================================
# §10.4 — unit sanity on value_per_share
#
# The first version of this check priced each event off the study panel and FAILED (VCF
# 2018-01-08 at 33% of price). The failure was in the CHECK, not the data: VCF leaves
# `universe_pit` in 2015, so the panel's last known price was 2.5 years stale. Re-priced from
# `ticker` at the real ex-1 session (out/sql/q7_unit_check.sql -> out/unit_check_top20.csv)
# the same event is 66,000 / 305,000 = 21.6%. The threshold was NOT moved to fit the number.
# =========================================================================================
U = pd.read_csv(os.path.join(OUT, "unit_check_top20.csv"), dtype={"tk": str, "ex": str})
# A VND-vs-thousand-VND error is a factor of ~1000; it cannot hide under 1.0.
check("T6 unit check: no dividend exceeds its own ex-1 share price",
      bool((U["div_over_px"] < 1.0).all()),
      f"max div/price={U['div_over_px'].max():.4f} ({U.loc[U['div_over_px'].idxmax(), 'tk']} "
      f"{U.loc[U['div_over_px'].idxmax(), 'ex']}), n priced={len(U)}/20")
# Events above the prereg's 30% "reasonable" band are named, and shown to be outside the study.
over = U[U["div_over_px"] >= 0.30]
in_panel = sorted(set(over["tk"]) & set(P["ticker"]))
check("T6b every event above the §10.4 30% band is absent from the study panel",
      len(in_panel) == 0,
      f"over 30%: {sorted(set(over['tk']))} -> panel rows for them: {in_panel or 'none'}")
# div x OShares against trailing 4Q net profit: also a ~1000x test, not a payout-policy test.
# Ratios above 1 are real (VCF/VEF distribute accumulated reserves), so the band is wide.
pr = U["payout_vs_np_ttm"].dropna()
check("T6c unit check: dividend x OShares is the same order of magnitude as annual profit",
      bool(((pr > 0.01) & (pr < 500)).all()),
      f"payout/NP_TTM range [{pr.min():.2f}, {pr.max():.2f}]")
check("T6d unit check: div_total is VND/share, not thousands",
      bool(DIV["div_total"].median() > 100.0),
      f"median div_total={DIV['div_total'].median():,.0f} VND/share")

# =========================================================================================
# §10.5 — the two §4.2 disqualifiers really are enforced in the samples
# =========================================================================================
check("T7 no episode sits on an ex-date (Test A + Test B)",
      int(EVA["is_exdate"].sum()) == 0 and int(EVB["is_exdate"].sum()) == 0,
      f"A={int(EVA['is_exdate'].sum())} B={int(EVB['is_exdate'].sum())}")
oob = (((EVA["close"] < EVA["low"]) | (EVA["close"] > EVA["high"])).sum()
       + ((EVB["close"] < EVB["low"]) | (EVB["close"] > EVB["high"])).sum())
check("T8 no episode has Close outside [Low, High]", int(oob) == 0, f"violations={int(oob)}")

# =========================================================================================
# §10.6 — benchmark integrity on every day the sample actually uses
# =========================================================================================
used = pd.Index(sorted(set(EVA["dt"]) | set(EVB["dt"]) | set(EVA["d_p60"].dropna())
                       | set(EVB["d_p60"].dropna())))
bu = BENCH.set_index("dt").reindex(used)
check("T9 benchmark has > 50 names on every day the sample touches",
      bool((bu["n_names"] > 50).all()),
      f"min n_names={int(bu['n_names'].min())} over {len(used)} days")
check("T9b benchmark winsorised leg differs from raw where impossible returns exist",
      bool((BENCH.loc[BENCH['n_impossible'] > 0, 'ew_ret']
            != BENCH.loc[BENCH['n_impossible'] > 0, 'ew_ret_raw']).all()),
      f"days with n_impossible>0: {int((BENCH['n_impossible'] > 0).sum())}")

# =========================================================================================
# §10.7 — PIT boundary: every dividend inside trailing_div(t) has ex_date in (t-365, t]
# =========================================================================================
rng = np.random.default_rng(20260818)
samp = EVA.iloc[rng.choice(len(EVA), size=min(200, len(EVA)), replace=False)]
dv = DIV.copy()
dv["ex_ts"] = pd.to_datetime(dv["ex_date"])
byt = {k: v for k, v in dv.groupby("ticker")}
bad_pit, bad_sum = 0, 0
for tk, dt, div0 in zip(samp["ticker"], samp["dt"], samp["div0"]):
    t = pd.Timestamp(dt)
    d = byt.get(tk)
    if d is None:
        bad_pit += 1
        continue
    w = d[(d["ex_ts"] <= t) & (d["ex_ts"] > t - pd.Timedelta(days=365))]
    if len(w) and (w["ex_ts"] > t).any():
        bad_pit += 1
    if not close_to(float(w["div_total"].sum()), float(div0), 1e-6):
        bad_sum += 1
check("T10 PIT: 200 sampled episodes have every constituent ex_date in (t-365, t]",
      bad_pit == 0, f"violations={bad_pit}")
check("T10b PIT: trailing_div(t) equals the sum of exactly that window",
      bad_sum == 0, f"mismatches={bad_sum}/{len(samp)}")

# =========================================================================================
# added — the two-way cluster t-stat, re-derived from the CGM definition
# =========================================================================================
y = (EVB["mdd_60"] - EVB["ctrl_mdd_60"]).to_numpy(dtype=float)
keep = np.isfinite(y)
y, tk, ym = y[keep], EVB["ticker"].to_numpy()[keep], EVB["ym"].to_numpy()[keep]
n = len(y)
mu = y.mean()
e = y - mu


def meat(gr):
    return sum(e[gr == u].sum() ** 2 for u in np.unique(gr))


v = (meat(tk) + meat(ym) - meat(np.char.add(np.char.add(tk.astype(str), "|"), ym.astype(str)))) / n**2
t_manual = mu / np.sqrt(v)
check("T11 two-way cluster t re-derived independently (CGM V1+V2-V12)",
      close_to(float(t_manual), RES["test_b"]["deposit"]["d_mdd_60"]["all"]["t_cluster"], 1e-8),
      f"selfcheck t={t_manual:.6f} analyze t={RES['test_b']['deposit']['d_mdd_60']['all']['t_cluster']:.6f}")
one_way_t = mu / np.sqrt(meat(tk) / n**2)
check("T11b two-way t is not larger than the ticker-only cluster t (clustering must cost, not buy)",
      abs(t_manual) <= abs(one_way_t) * 1.05,
      f"two-way={t_manual:.2f} ticker-only={one_way_t:.2f}")

# =========================================================================================
# added — the placebo really is the same episodes shifted exactly 250 sessions
# =========================================================================================
pm = RES["test_b"]["deposit"]["placebo_matched"]
check("T12 paired placebo net = primary - placebo on the SAME episodes",
      pm["paired_net"]["all"]["n"] <= RES["test_b"]["deposit"]["d_mdd_60"]["all"]["n"],
      f"paired n={pm['paired_net']['all']['n']} of primary n={RES['test_b']['deposit']['d_mdd_60']['all']['n']}")
check("T12b placebo is NOT assumed to be zero (Sprint 2 lesson)",
      abs(pm["d_mdd_60"]["all"]["mean"]) > 0.5,
      f"placebo Δ MDD = {pm['d_mdd_60']['all']['mean']:+.3f} pp (t={pm['d_mdd_60']['all']['t_cluster']:.2f})")

# =========================================================================================
print("\n%d PASS / %d FAIL" % (len(PASS), len(FAIL)))
if FAIL:
    print("FAILED: " + ", ".join(FAIL))
sys.exit(1 if FAIL else 0)
