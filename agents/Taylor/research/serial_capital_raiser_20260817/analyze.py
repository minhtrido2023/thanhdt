#!/usr/bin/env python3
"""Execute the preregistered Q1 and Q2 estimates from out/. Offline: no BigQuery, no network.

Everything here was fixed in PREREG.md before any number was seen. Results land in
out/results.json plus a handful of readable CSVs.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

from scr_lib import Index, absorb, boot, cluster2_ols, holm, loo, nw_tstat

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

RAISE_SET = ["RIGHTS", "PRIVATE_PLACEMENT", "AUCTION"]
WIDE_SET = RAISE_SET + ["ESOP", "CONVERTIBLE"]
HORIZONS = [250, 500, 750]
OOS_FROM = "2020-01-01"
CTRL = ["ln_adv", "roic", "npm", "fscore", "debt_eq"]


# =============================================================================================
# Q1 — long-run BHAR after an issuance
# =============================================================================================
def q1(vni: Index) -> dict:
    d = pd.read_csv(os.path.join(OUT, "q1_events.csv"), dtype={"icb": str})
    d["month"] = d.t0.str[:7]
    d["year"] = d.t0.str[:4].astype(int)

    # BHAR at each horizon: stock buy-and-hold minus VNINDEX over the SAME dates.
    for h in HORIZONS:
        stock = d[f"c_{h}"] / d.c_0 - 1
        bench = vni.ret(d.d_0.fillna("").tolist(), d[f"d_{h}"].fillna("").tolist())
        d[f"bhar_{h}"] = stock - bench

    # Pre-trend [t0-250, t0] and far placebo [t0-500, t0-250].
    d["pretrend_250"] = (d.c_0 / d.c_m250 - 1) - vni.ret(
        d.d_m250.fillna("").tolist(), d.d_0.fillna("").tolist())
    d["placebo_250"] = (d.c_m250 / d.c_m500 - 1) - vni.ret(
        d.d_m500.fillna("").tolist(), d.d_m250.fillna("").tolist())

    d.to_csv(os.path.join(OUT, "q1_bhar.csv"), index=False)

    def cut(sel: pd.Series, label: str) -> dict:
        z = d[sel]
        res = {"label": label, "n_events": int(len(z)),
               "n_tickers": int(z.ticker.nunique()), "n_months": int(z.month.nunique()),
               "horizons": {}}
        for h in HORIZONS:
            res["horizons"][str(h)] = boot(z[f"bhar_{h}"], z.month)
        res["holm"] = holm({str(h): res["horizons"][str(h)]["p"] for h in HORIZONS})
        res["pretrend_250"] = boot(z.pretrend_250, z.month)
        res["placebo_250"] = boot(z.placebo_250, z.month)
        # splits on the PRIMARY horizon (250)
        for name, m in (("IS", z.t0 < OOS_FROM), ("OOS", z.t0 >= OOS_FROM)):
            zz = z[m]
            res[f"primary_{name}"] = boot(zz.bhar_250, zz.month) if len(zz) else None
        res["loo_primary"] = loo(z.bhar_250.to_numpy(), z.year.to_numpy())
        return res

    variants = {
        "RAISE_SET": cut(d.subtype.isin(RAISE_SET), "RAISE_SET (rights+PP+auction)"),
        "V_WIDE": cut(d.subtype.isin(WIDE_SET), "V-WIDE (+ESOP+convertible)"),
        "V_ALL": cut(pd.Series(True, index=d.index), "V-ALL (every ISS subtype)"),
    }
    subtypes = {s: cut(d.subtype == s, f"subtype={s}") for s in sorted(d.subtype.unique())}
    return {"variants": variants, "subtypes": subtypes,
            "n_events_total": int(len(d)), "n_tickers_total": int(d.ticker.nunique())}


# =============================================================================================
# Q2 — cross-sectional valuation discount
# =============================================================================================
def panel_path(name: str) -> str:
    """Prefer the plain CSV a fresh `build.py` writes; fall back to the committed `.gz`.

    The monthly panel is 11 MB uncompressed, so only the gzip is committed. pandas reads either
    transparently — this just picks whichever exists so a clean checkout runs without re-billing a
    BigQuery pull.
    """
    plain = os.path.join(OUT, name)
    return plain if os.path.exists(plain) else plain + ".gz"


def prep_q2() -> pd.DataFrame:
    d = pd.read_csv(panel_path("q2_panel.csv"), dtype={"icb": str})
    d["month"] = d.mth.str[:7]
    d["year"] = d.mth.str[:4].astype(int)
    d["icb"] = d.icb.fillna("NA")

    # Valuation on the YIELD scale. PE/PB read AS STORED — never rescaled by Price/Close.
    d["ey"] = np.where(d.PE > 0, 1.0 / d.PE, np.nan)
    d["by"] = np.where(d.PB > 0, 1.0 / d.PB, np.nan)

    d["ln_adv"] = np.where(d.adv60 > 0, np.log(d.adv60), np.nan)
    d["roic"] = d.ROIC_Trailing
    d["npm"] = d.NPM_P0
    d["fscore"] = d.FSCORE
    d["debt_eq"] = d.Debt_Eq_P0

    for tag, col in (("raise", "n_raise_3y"), ("wide", "n_wide_3y"), ("all", "n_all_3y")):
        d[f"serial_{tag}"] = (d[col] >= 2).astype(float)
        d[f"occas_{tag}"] = (d[col] == 1).astype(float)
    d["serial_fwd"] = (d.n_raise_fwd180 >= 1).astype(float)
    d["cell"] = d.month + "|" + d.icb
    return d


def q2a(d: pd.DataFrame, ycol: str, tag: str, xcols: list[str] | None = None,
        winsor: bool = False) -> dict:
    """Within-(month x sector) regression of a valuation yield on raiser state + controls."""
    xs = xcols if xcols is not None else [f"serial_{tag}", f"occas_{tag}"]
    cols = [ycol] + xs + CTRL
    z = d[cols + ["ticker", "month", "cell"]].dropna().copy()
    if winsor:
        lo = z.groupby("month", observed=True)[ycol].transform(lambda s: s.quantile(0.01))
        hi = z.groupby("month", observed=True)[ycol].transform(lambda s: s.quantile(0.99))
        z[ycol] = z[ycol].clip(lo, hi)

    # Drop singleton cells explicitly: they demean to exactly zero and carry no information.
    sizes = z.groupby("cell", observed=True)[ycol].transform("size")
    z = z[sizes >= 2]
    dm = absorb(z, [ycol] + xs + CTRL, z.cell)
    n_cells = int(z.cell.nunique())

    y = dm[ycol].to_numpy()
    X = dm[xs + CTRL].to_numpy()
    r = cluster2_ols(y, X, z.ticker.to_numpy(), z.month.to_numpy(), n_absorbed=n_cells)
    names = xs + CTRL
    r["names"] = names
    r["n_eff_cells"] = n_cells
    r["y"] = ycol
    r["y_median_all"] = float(z[ycol].median())
    r["multiple_median_all"] = float(1.0 / z[ycol].median()) if z[ycol].median() else None
    r["shares"] = {c: float(z[c].mean()) for c in xs}
    # p-values from a normal approximation on the clustered t (dof >> 100 here)
    from math import erfc, sqrt
    r["p"] = [float(erfc(abs(t) / sqrt(2))) if t is not None else None for t in r["t"]]
    r["coef"] = dict(zip(names, r["beta"]))
    r["tstat"] = dict(zip(names, r["t"]))
    r["pval"] = dict(zip(names, r["p"]))
    return r


def q2b(d: pd.DataFrame, sortcol: str, tag: str, nq: int = 5, min_leg: int = 3) -> dict:
    """Value-matched, monthly-rebalanced serial-minus-baseline spread.

    Within each month, names are split into `nq` quantiles of `sortcol`; inside each quantile the
    equal-weight serial leg is differenced against the equal-weight non-raiser leg. Averaging over
    quantiles gives one observation per month, so the series is non-overlapping by construction —
    there is no overlapping-window inference problem to argue about.
    """
    ser, occ = f"serial_{tag}", f"occas_{tag}"
    z = d[[sortcol, "fwd_ret_1m", ser, occ, "month", "ticker"]].dropna().copy()
    z["base"] = ((z[ser] == 0) & (z[occ] == 0)).astype(float)

    rows = []
    for m, g in z.groupby("month", observed=True):
        if len(g) < nq * 2:
            continue
        try:
            g = g.assign(q=pd.qcut(g[sortcol], nq, labels=False, duplicates="drop"))
        except ValueError:
            continue
        sp, w = [], []
        for _, gq in g.groupby("q", observed=True):
            a = gq[gq[ser] == 1].fwd_ret_1m
            b = gq[gq.base == 1].fwd_ret_1m
            if len(a) >= min_leg and len(b) >= min_leg:
                sp.append(a.mean() - b.mean())
                w.append(min(len(a), len(b)))
        if sp:
            rows.append({"month": m, "spread": float(np.mean(sp)), "n_q": len(sp),
                         "n_serial": int((g[ser] == 1).sum()),
                         "n_base": int((g.base == 1).sum())})
    s = pd.DataFrame(rows)
    if s.empty:
        return {"n_months": 0, "note": "no month had both legs above the floor"}
    s.to_csv(os.path.join(OUT, f"q2b_spread_{tag}_{sortcol}.csv"), index=False)

    def blk(x: pd.DataFrame) -> dict:
        r = boot(x.spread, x.month)
        r.update(nw_tstat(x.spread.to_numpy(), lag=6))
        return r

    out = {"sortcol": sortcol, "tag": tag, "n_months": int(len(s)),
           "n_serial_names": int(z[z[ser] == 1].ticker.nunique()),
           "n_base_names": int(z[z.base == 1].ticker.nunique()),
           "mean_q_per_month": float(s.n_q.mean()),
           "full": blk(s),
           "IS": blk(s[s.month < OOS_FROM[:7]]) if (s.month < OOS_FROM[:7]).any() else None,
           "OOS": blk(s[s.month >= OOS_FROM[:7]]) if (s.month >= OOS_FROM[:7]).any() else None}
    cum = float(np.prod(1 + s.spread.to_numpy()) - 1)
    out["cumulative_spread"] = cum
    out["annualised_spread"] = float((1 + cum) ** (12 / len(s)) - 1)
    return out


def q2_placebo_shuffle(d: pd.DataFrame, ycol: str, tag: str, seed: int = 20260817) -> dict:
    """Reassign the serial label at random WITHIN each (month, sector) cell and rerun Q2a.

    A significant coefficient here would mean the FE/clustering machinery manufactures one.
    """
    rng = np.random.default_rng(seed)
    z = d.copy()
    ser, occ = f"serial_{tag}", f"occas_{tag}"
    z[[ser, occ]] = (z.groupby("cell", observed=True)[[ser, occ]]
                     .transform(lambda s: rng.permutation(s.to_numpy())))
    return q2a(z, ycol, tag)


def main() -> None:
    v = pd.read_csv(os.path.join(OUT, "vnindex.csv"))
    vni = Index(v.time.tolist(), v.Close.to_numpy())

    res: dict = {"seed": 20260817, "oos_from": OOS_FROM}
    res["q1"] = q1(vni)

    d = prep_q2()
    res["q2_panel"] = {
        "rows": int(len(d)), "tickers": int(d.ticker.nunique()),
        "months": int(d.month.nunique()),
        "rows_with_ey": int(d.ey.notna().sum()), "rows_with_by": int(d.by.notna().sum()),
        "share_pe_nonpositive": float((d.PE <= 0).mean()),
        "fwd_gap_rate": float(d.fwd_gap.mean()),
        "serial_share": {t: float(d[f"serial_{t}"].mean()) for t in ("raise", "wide", "all")},
        "occas_share": {t: float(d[f"occas_{t}"].mean()) for t in ("raise", "wide", "all")},
        "serial_tickers": {t: int(d[d[f"serial_{t}"] == 1].ticker.nunique())
                           for t in ("raise", "wide", "all")},
        "median_PE": float(d.PE[d.PE > 0].median()), "median_PB": float(d.PB[d.PB > 0].median()),
    }

    # --- Q2a: discount regressions -------------------------------------------------------
    a: dict = {}
    for tag in ("raise", "wide", "all"):
        for ycol in ("ey", "by"):
            a[f"{ycol}_{tag}"] = q2a(d, ycol, tag)
    # Holm over the primary family {ey, by} on the primary raise set
    res["q2a"] = a
    res["q2a_holm_primary"] = holm({k: a[k]["pval"][f"serial_raise"]
                                    for k in ("ey_raise", "by_raise")})
    res["q2a_winsor_primary"] = {f"{y}_raise": q2a(d, y, "raise", winsor=True)
                                 for y in ("ey", "by")}
    res["q2a_shuffle_placebo"] = {y: q2_placebo_shuffle(d, y, "raise") for y in ("ey", "by")}
    # Look-ahead probe: FUTURE raises in place of past ones.
    res["q2a_future_probe"] = {y: q2a(d, y, "raise", xcols=["serial_fwd"]) for y in ("ey", "by")}
    # IS / OOS on the primary
    res["q2a_splits"] = {
        f"{y}_{nm}": q2a(d[m], y, "raise")
        for y in ("ey", "by")
        for nm, m in (("IS", d.mth < OOS_FROM), ("OOS", d.mth >= OOS_FROM))
    }

    # --- Q2b: value-matched forward-return spread ----------------------------------------
    res["q2b"] = {f"{s}_{t}": q2b(d, s, t)
                  for t in ("raise", "wide", "all") for s in ("ey", "by")}

    with open(os.path.join(OUT, "results.json"), "w") as fh:
        json.dump(res, fh, indent=2, sort_keys=True, default=str)

    # --- readable console digest ---------------------------------------------------------
    print("== Q1 long-run BHAR (primary horizon 250 sessions) ==")
    for k, r in res["q1"]["variants"].items():
        h = r["horizons"]
        print(f"{k:10s} N={r['n_events']:5d} tk={r['n_tickers']:4d} mo={r['n_months']:3d}  "
              + "  ".join(f"h{hh}={h[str(hh)]['mean']:+.4f}(p={h[str(hh)]['p']:.3f},"
                          f"holm={r['holm'][str(hh)]:.3f})" for hh in HORIZONS))
        print(f"{'':10s} pretrend={r['pretrend_250']['mean']:+.4f} "
              f"[{r['pretrend_250']['lo']:+.4f},{r['pretrend_250']['hi']:+.4f}] "
              f"placebo={r['placebo_250']['mean']:+.4f} "
              f"[{r['placebo_250']['lo']:+.4f},{r['placebo_250']['hi']:+.4f}] "
              f"loo_flip={r['loo_primary']['sign_flip']}")
    print("\n-- subtypes (primary horizon) --")
    for k, r in res["q1"]["subtypes"].items():
        hh = r["horizons"]["250"]
        print(f"  {k:20s} N={r['n_events']:5d} tk={r['n_tickers']:4d} "
              f"bhar250={hh['mean']:+.4f} CI[{hh['lo']:+.4f},{hh['hi']:+.4f}] p={hh['p']:.3f}")

    print("\n== Q2 panel ==")
    print(json.dumps(res["q2_panel"], indent=2, sort_keys=True))

    print("\n== Q2a discount (positive serial coef = CHEAPER) ==")
    for k, r in res["q2a"].items():
        tag = k.split("_", 1)[1]
        b, t, p = (r["coef"][f"serial_{tag}"], r["tstat"][f"serial_{tag}"],
                   r["pval"][f"serial_{tag}"])
        bo, to = r["coef"][f"occas_{tag}"], r["tstat"][f"occas_{tag}"]
        print(f"  {k:10s} n={r['n']:6d} cells={r['n_eff_cells']:5d} share={r['shares'][f'serial_{tag}']:.3f} "
              f"serial={b:+.5f} (t={t:+.2f}, p={p:.4f})  occas={bo:+.5f} (t={to:+.2f})  "
              f"median_multiple={r['multiple_median_all']:.2f}")
    print(f"  Holm primary: {res['q2a_holm_primary']}")
    print("  shuffle placebo:", {y: round(r['tstat']['serial_raise'], 3)
                                 for y, r in res["q2a_shuffle_placebo"].items()})
    print("  future probe:", {y: (round(r['coef']['serial_fwd'], 5), round(r['tstat']['serial_fwd'], 2))
                              for y, r in res["q2a_future_probe"].items()})
    print("  splits:", {k: (round(r['coef']['serial_raise'], 5), round(r['tstat']['serial_raise'], 2))
                        for k, r in res["q2a_splits"].items()})

    print("\n== Q2b value-matched forward spread (monthly, serial - nonraiser) ==")
    for k, r in res["q2b"].items():
        if not r.get("n_months"):
            print(f"  {k:10s} EMPTY")
            continue
        f = r["full"]
        print(f"  {k:10s} months={r['n_months']:3d} qpm={r['mean_q_per_month']:.2f} "
              f"mean={f['mean']*100:+.3f}%/mo NW_t={f['t']:+.2f} boot_p={f['p']:.3f} "
              f"CI[{f['lo']*100:+.3f}%,{f['hi']*100:+.3f}%] ann={r['annualised_spread']*100:+.2f}%")
        for nm in ("IS", "OOS"):
            s = r.get(nm)
            if s:
                print(f"{'':12s}   {nm}: mean={s['mean']*100:+.3f}%/mo NW_t={s['t']:+.2f} "
                      f"boot_p={s['p']:.3f} n={s['n']}")


if __name__ == "__main__":
    main()
