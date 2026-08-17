#!/usr/bin/env python3
"""Post-hoc robustness, run AFTER the preregistered estimates. Offline.

Every block here is a DEVIATION from PREREG.md — added, not substituted, and recorded in
DEVIATIONS.md with the reason. Two of them exist because a preregistered falsification test
actually fired, which is what those tests are for:

  R1  Q1's far placebo came back +30.2%, significant. Issuers raise after a run-up, so the
      post-event number cannot be read as an issuance effect until the pre-event run-up is
      conditioned on. R1 splits events by pre-trend and re-measures.
  R2  Q2b's spread is large (~-10%/yr). If it lives in names below the book's own liquidity floor
      it is a description of the market's tail, not something relevant to this fleet. R2 adds a
      size-matched leg and an ADV floor, and shows the two legs' raw levels rather than only their
      difference.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

from analyze import CTRL, HORIZONS, OOS_FROM, RAISE_SET, panel_path, prep_q2, q2a
from scr_lib import Index, boot, nw_tstat

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
ADV_FLOOR = 2_000_000_000.0  # the production LAG/BAL liquidity gate, `lag_liquidity_filter.py`


# ---------------------------------------------------------------------------------------------
# R1 — is Q1's underperformance an issuance effect or reversal of the pre-event run-up?
# ---------------------------------------------------------------------------------------------
def r1_pretrend_conditional() -> dict:
    d = pd.read_csv(os.path.join(OUT, "q1_bhar.csv"), dtype={"icb": str})
    z = d[d.subtype.isin(RAISE_SET) & d.pretrend_250.notna() & d.bhar_250.notna()].copy()
    z["ptq"] = pd.qcut(z.pretrend_250, 4, labels=False)

    out = {"n": int(len(z)), "n_tickers": int(z.ticker.nunique()), "by_pretrend_quartile": {}}
    for q, g in z.groupby("ptq"):
        out["by_pretrend_quartile"][int(q)] = {
            "pretrend_mean": float(g.pretrend_250.mean()),
            "n": int(len(g)), "n_tickers": int(g.ticker.nunique()),
            **{f"bhar_{h}": boot(g[f"bhar_{h}"], g.month) for h in HORIZONS},
        }

    # Same question as a regression: does the raise dummy survive next to the run-up it followed?
    # Sample = every ISS event; regressor of interest = "this was a cash raise".
    a = d[d.bhar_250.notna() & d.pretrend_250.notna()].copy()
    a["is_raise"] = a.subtype.isin(RAISE_SET).astype(float)
    a["ln_adv"] = np.where(a.adv60 > 0, np.log(a.adv60), np.nan)
    a = a[a.ln_adv.notna() & a.rvol60.notna()].copy()
    yr = pd.get_dummies(a.t0.str[:4], drop_first=True, dtype=float)
    X = np.column_stack([np.ones(len(a)), a.is_raise, a.pretrend_250, a.ln_adv, a.rvol60,
                         yr.to_numpy()])
    y = a.bhar_250.to_numpy()
    inv = np.linalg.pinv(X.T @ X)
    beta = inv @ X.T @ y
    e = y - X @ beta

    def meat(g):
        M = np.zeros((X.shape[1], X.shape[1]))
        gs = np.asarray(g).astype(str)
        for q in pd.unique(gs):
            s = X[gs == q].T @ e[gs == q]
            M += np.outer(s, s)
        return M

    g1, g2 = a.ticker.to_numpy().astype(str), a.month.to_numpy().astype(str)
    g12 = np.char.add(np.char.add(g1, "|"), g2)
    V = inv @ (meat(g1) + meat(g2) - meat(g12)) @ inv
    se = np.sqrt(np.maximum(np.diag(V), 0))
    out["regression"] = {
        "n": int(len(a)), "note": "y=bhar_250; year FE; SE two-way clustered ticker x month",
        "is_raise_beta": float(beta[1]), "is_raise_t": float(beta[1] / se[1]),
        "pretrend_beta": float(beta[2]), "pretrend_t": float(beta[2] / se[2]),
    }
    return out


# ---------------------------------------------------------------------------------------------
# R2 — is the Q2b spread size-driven, and does it survive the book's liquidity floor?
# ---------------------------------------------------------------------------------------------
def r2_spread(d: pd.DataFrame, sortcol: str, tag: str, size_match: bool,
              adv_floor: float | None, nq: int = 5, nsz: int = 3,
              min_leg: int = 3) -> dict:
    ser, occ = f"serial_{tag}", f"occas_{tag}"
    cols = [sortcol, "fwd_ret_1m", ser, occ, "month", "ticker", "adv60"]
    z = d[cols].dropna().copy()
    if adv_floor is not None:
        z = z[z.adv60 >= adv_floor]
    z["base"] = ((z[ser] == 0) & (z[occ] == 0)).astype(float)

    rows = []
    for m, g in z.groupby("month", observed=True):
        if len(g) < nq * 2:
            continue
        try:
            g = g.assign(q=pd.qcut(g[sortcol], nq, labels=False, duplicates="drop"))
        except ValueError:
            continue
        if size_match:
            try:
                g = g.assign(sz=pd.qcut(g.adv60, nsz, labels=False, duplicates="drop"))
            except ValueError:
                continue
            keys = ["q", "sz"]
        else:
            g = g.assign(sz=0)
            keys = ["q"]
        sp, la, lb = [], [], []
        for _, gc in g.groupby(keys, observed=True):
            a = gc[gc[ser] == 1].fwd_ret_1m
            b = gc[gc.base == 1].fwd_ret_1m
            if len(a) >= min_leg and len(b) >= min_leg:
                sp.append(a.mean() - b.mean())
                la.append(a.mean())
                lb.append(b.mean())
        if sp:
            rows.append({"month": m, "spread": float(np.mean(sp)),
                         "leg_serial": float(np.mean(la)), "leg_base": float(np.mean(lb)),
                         "n_cells": len(sp)})
    s = pd.DataFrame(rows)
    if s.empty:
        return {"n_months": 0}
    r = boot(s.spread, s.month)
    r.update(nw_tstat(s.spread.to_numpy(), lag=6))
    cum = float(np.prod(1 + s.spread.to_numpy()) - 1)
    return {
        "sortcol": sortcol, "tag": tag, "size_match": size_match,
        "adv_floor": adv_floor, "n_months": int(len(s)),
        "mean_cells_per_month": float(s.n_cells.mean()),
        "n_serial_names": int(z[z[ser] == 1].ticker.nunique()),
        "n_base_names": int(z[z.base == 1].ticker.nunique()),
        "serial_share_rows": float((z[ser] == 1).mean()),
        "spread": r,
        "leg_serial_mean": float(s.leg_serial.mean()),
        "leg_base_mean": float(s.leg_base.mean()),
        "cumulative": cum,
        "annualised": float((1 + cum) ** (12 / len(s)) - 1),
        "IS": nw_tstat(s[s.month < OOS_FROM[:7]].spread.to_numpy(), 6),
        "OOS": nw_tstat(s[s.month >= OOS_FROM[:7]].spread.to_numpy(), 6),
    }


def r3_unmatched(d: pd.DataFrame, tag: str, adv_floor: float | None) -> dict:
    """Raw, unmatched levels: what did each leg actually return, before any value matching?"""
    ser, occ = f"serial_{tag}", f"occas_{tag}"
    z = d[["fwd_ret_1m", ser, occ, "month", "ticker", "adv60", "PE", "PB"]].dropna(
        subset=["fwd_ret_1m", ser, occ, "month"]).copy()
    if adv_floor is not None:
        z = z[z.adv60 >= adv_floor]
    z["base"] = ((z[ser] == 0) & (z[occ] == 0)).astype(float)
    rows = []
    for m, g in z.groupby("month", observed=True):
        a, b = g[g[ser] == 1].fwd_ret_1m, g[g.base == 1].fwd_ret_1m
        if len(a) >= 3 and len(b) >= 3:
            rows.append({"month": m, "serial": float(a.mean()), "base": float(b.mean()),
                         "spread": float(a.mean() - b.mean())})
    s = pd.DataFrame(rows)
    if s.empty:
        return {"n_months": 0}
    return {"adv_floor": adv_floor, "n_months": int(len(s)),
            "serial_mean_mo": float(s.serial.mean()), "base_mean_mo": float(s.base.mean()),
            "spread": {**boot(s.spread, s.month), **nw_tstat(s.spread.to_numpy(), 6)},
            "median_PE_serial": float(z[(z[ser] == 1) & (z.PE > 0)].PE.median()),
            "median_PE_base": float(z[(z.base == 1) & (z.PE > 0)].PE.median()),
            "median_PB_serial": float(z[(z[ser] == 1) & (z.PB > 0)].PB.median()),
            "median_PB_base": float(z[(z.base == 1) & (z.PB > 0)].PB.median())}


def main() -> None:
    res: dict = {}
    print("== R1: Q1 conditioned on the pre-event run-up ==")
    res["r1"] = r1_pretrend_conditional()
    for q, v in res["r1"]["by_pretrend_quartile"].items():
        print(f"  pretrend Q{q} (mean {v['pretrend_mean']:+.3f}) n={v['n']:4d} tk={v['n_tickers']:4d}  "
              + "  ".join(f"h{h}={v[f'bhar_{h}']['mean']:+.4f}"
                          f"[{v[f'bhar_{h}']['lo']:+.3f},{v[f'bhar_{h}']['hi']:+.3f}]"
                          for h in HORIZONS))
    rg = res["r1"]["regression"]
    print(f"  regression n={rg['n']}: is_raise={rg['is_raise_beta']:+.4f} (t={rg['is_raise_t']:+.2f}), "
          f"pretrend={rg['pretrend_beta']:+.4f} (t={rg['pretrend_t']:+.2f})")

    d = prep_q2()
    print("\n== R2: Q2b spread with size matching and the production ADV floor ==")
    res["r2"] = {}
    for tag in ("raise", "wide"):
        for sortcol in ("ey", "by"):
            for sm in (False, True):
                for af in (None, ADV_FLOOR):
                    k = f"{sortcol}_{tag}_sz{int(sm)}_adv{0 if af is None else 2}"
                    r = r2_spread(d, sortcol, tag, sm, af)
                    res["r2"][k] = r
                    if not r.get("n_months"):
                        print(f"  {k:26s} EMPTY")
                        continue
                    sp = r["spread"]
                    print(f"  {k:26s} mo={r['n_months']:3d} cells/mo={r['mean_cells_per_month']:.1f} "
                          f"serial_tk={r['n_serial_names']:3d} "
                          f"spread={sp['mean']*100:+.3f}%/mo NW_t={sp['t']:+.2f} "
                          f"boot_p={sp['p']:.3f} ann={r['annualised']*100:+.2f}% "
                          f"| legs {r['leg_serial_mean']*100:+.3f} vs {r['leg_base_mean']*100:+.3f} "
                          f"| IS_t={r['IS']['t']:+.2f} OOS_t={r['OOS']['t']:+.2f}")

    print("\n== R3: unmatched levels ==")
    res["r3"] = {}
    for tag in ("raise", "wide", "all"):
        for af in (None, ADV_FLOOR):
            k = f"{tag}_adv{0 if af is None else 2}"
            r = r3_unmatched(d, tag, af)
            res["r3"][k] = r
            if not r.get("n_months"):
                print(f"  {k:14s} EMPTY")
                continue
            print(f"  {k:14s} mo={r['n_months']:3d} serial={r['serial_mean_mo']*100:+.3f}%/mo "
                  f"base={r['base_mean_mo']*100:+.3f}%/mo "
                  f"spread_t={r['spread']['t']:+.2f} (boot_p={r['spread']['p']:.3f}) "
                  f"| medPE {r['median_PE_serial']:.2f} vs {r['median_PE_base']:.2f} "
                  f"| medPB {r['median_PB_serial']:.2f} vs {r['median_PB_base']:.2f}")

    # R4 — Q2a restricted to the investable slice, since that is the only slice the book can act on.
    print("\n== R4: Q2a discount regression on the ADV>=2bn slice ==")
    dd = d[d.adv60 >= ADV_FLOOR]
    res["r4"] = {y: q2a(dd, y, "raise") for y in ("ey", "by")}
    for y, r in res["r4"].items():
        print(f"  {y}: n={r['n']} cells={r['n_eff_cells']} serial={r['coef']['serial_raise']:+.5f} "
              f"(t={r['tstat']['serial_raise']:+.2f}, p={r['pval']['serial_raise']:.4f}) "
              f"occas={r['coef']['occas_raise']:+.5f} (t={r['tstat']['occas_raise']:+.2f})")

    with open(os.path.join(OUT, "robust.json"), "w") as fh:
        json.dump(res, fh, indent=2, sort_keys=True, default=str)


if __name__ == "__main__":
    main()
