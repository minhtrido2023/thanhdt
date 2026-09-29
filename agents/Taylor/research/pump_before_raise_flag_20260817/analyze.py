#!/usr/bin/env python3
"""Executes PREREG.md for the pre-raise high-momentum (PRHM) flag. Offline — no BigQuery.

Mục 1  threshold grid + false-positive rate + the preregistered T-selection rule
Mục 2  sector, with ICB 8777 (investment services / brokerages) called out
Mục 3  beta bins on a self-computed 250-session coefficient, + the combined cut

Estimators are imported from the prior program's `scr_lib` so both programs' CIs come from one
implementation. The only new estimator is `boot_gap` (two-group difference), documented below.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PRIOR = os.path.join(os.path.dirname(HERE), "serial_capital_raiser_20260817")
sys.path.insert(0, PRIOR)

from scr_lib import SEED, boot, holm, loo  # noqa: E402

OUT = os.path.join(HERE, "out")
NBOOT = 10_000

# --- preregistered constants (PREREG §2/§3/§4). Changing one of these is a DEVIATION. ---
GRID = [0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60]
PRIMARY_SUBTYPES = ("RIGHTS", "PRIVATE_PLACEMENT")
RAISE_SET = ("RIGHTS", "PRIVATE_PLACEMENT", "AUCTION")
MIN_EVENTS_PER_SIDE = 100
MIN_TICKERS_PER_SIDE = 60
GAP_MAX = -0.05          # gap must be at least this negative
FPR_MAX = 0.40
FSCORE_GOOD = 4          # "FSCORE > 4"
BETA_LOW_HI, BETA_MID_HI = 1.2, 1.8
SECTOR_CI_FLOOR, SECTOR_VERDICT_FLOOR = 30, 100
COMBINED_MIN_EVENTS, COMBINED_MIN_TICKERS = 60, 40
OOS_YEAR = 2020

# ICB labels are used ONLY where the actual ticker membership was inspected and matches the ICB
# name (PREREG §3). Everything else prints as the bare code, not a guess.
ICB_LABEL = {
    8777: "Investment Services (securities brokerages)",
    8355: "Banks",
    8633: "Real Estate Holding & Development",
    2357: "Heavy Construction",
    8536: "Full Line Insurance",
    8575: "Property & Casualty Insurance",
    8773: "Consumer Finance",
    8775: "Specialty Finance",
    2353: "Building Materials & Fixtures",
    3573: "Farming & Fishing",
    3577: "Food Products",
    1757: "Iron & Steel",
    3763: "Clothing & Accessories",
    2777: "Transportation Services",
    9537: "Computer Services",
    5379: "Specialty Retailers",
}
SEC_ICB = 8777


def label(code) -> str:
    if code is None or (isinstance(code, float) and not np.isfinite(code)):
        return "ICB unknown"
    c = int(code)
    return f"ICB {c} ({ICB_LABEL[c]})" if c in ICB_LABEL else f"ICB {c} (unverified label)"


def boot_gap(x_a, x_b, blk_a, blk_b, seed: int = SEED, nboot: int = NBOOT) -> dict:
    """Block bootstrap of mean(A) - mean(B), resampling the SAME block draw for both groups.

    Blocks are anchor year-months. Drawing one block index vector and applying it to both legs
    keeps the two groups' shared market shock inside the resample: a month that is drawn twice
    contributes twice on BOTH sides, which is what makes the difference's CI a difference-in-the-
    same-market CI rather than two independent ones subtracted. A block that contains no event on
    one side contributes nothing to that side (handled by summing sums and counts, not means).
    """
    x_a, x_b = np.asarray(x_a, float), np.asarray(x_b, float)
    blk_a, blk_b = np.asarray(blk_a, dtype=object), np.asarray(blk_b, dtype=object)
    ma, mb = np.isfinite(x_a), np.isfinite(x_b)
    x_a, blk_a, x_b, blk_b = x_a[ma], blk_a[ma], x_b[mb], blk_b[mb]
    if not len(x_a) or not len(x_b):
        return {"gap": None, "lo": None, "hi": None, "p": None}
    u = np.unique(np.concatenate([blk_a, blk_b]))
    ix = {b: i for i, b in enumerate(u)}

    def agg(x, blk):
        s = np.zeros(len(u))
        n = np.zeros(len(u))
        for v, b in zip(x, blk):
            s[ix[b]] += v
            n[ix[b]] += 1
        return s, n

    sa, na = agg(x_a, blk_a)
    sb, nb = agg(x_b, blk_b)
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(u), (nboot, len(u)))
    with np.errstate(divide="ignore", invalid="ignore"):
        ga = sa[draws].sum(1) / na[draws].sum(1)
        gb = sb[draws].sum(1) / nb[draws].sum(1)
    d = ga - gb
    d = d[np.isfinite(d)]
    lo, hi = np.percentile(d, [2.5, 97.5])
    p = 2 * min((d <= 0).mean(), (d >= 0).mean())
    return {"gap": float(x_a.mean() - x_b.mean()), "lo": float(lo), "hi": float(hi),
            "p": float(min(1.0, p)), "n_blocks": int(len(u)), "nboot_eff": int(len(d))}


def load() -> pd.DataFrame:
    q1 = pd.read_csv(os.path.join(PRIOR, "out", "q1_bhar.csv"))
    ex = pd.read_csv(os.path.join(OUT, "extras.csv"))
    ka = set(zip(q1.ticker, q1.t0))
    kb = set(zip(ex.ticker, ex.t0))
    if ka != kb:
        raise SystemExit(f"CC5 FAIL: event key sets differ ({len(ka - kb)} / {len(kb - ka)})")
    df = q1.merge(ex, on=["ticker", "t0"], how="left", validate="one_to_one")
    df["block"] = df["month"]
    return df


def crosschecks(df: pd.DataFrame) -> dict:
    """CC1/CC2 — reproduce the prior program's published numbers before producing new ones."""
    r = df[df.subtype.isin(RAISE_SET)]
    out = {}
    for name, col, want in (("CC1_bhar250_raiseset", "bhar_250", -0.0774),
                            ("CC2a_pretrend_raiseset", "pretrend_250", 0.4554),
                            ("CC2b_placebo_raiseset", "placebo_250", 0.3021)):
        v = r[col].dropna()
        out[name] = {"n": int(len(v)), "mean": float(v.mean()),
                     "published": want, "abs_diff": abs(float(v.mean()) - want)}
    out["CC1_n_expected"] = 712
    out["CC1_n_match"] = bool(out["CC1_bhar250_raiseset"]["n"] == 712)
    # published values are rounded to 2dp, so agreement is asserted at 5e-5 not 1e-6
    out["pass"] = bool(out["CC1_n_match"]
                       and all(out[k]["abs_diff"] < 5e-5 for k in
                               ("CC1_bhar250_raiseset", "CC2a_pretrend_raiseset",
                                "CC2b_placebo_raiseset")))
    return out


def select_T(rows: list[dict]) -> tuple[float | None, str, float | None]:
    """PREREG §2 selection rule, verbatim and in order. Pure function of the grid rows.

    Extracted from `muc1` so `selfcheck_pump_flag.py` can drive it with fixtures where the answer
    is known by construction — including the case that actually occurred (nothing eligible) and
    the cases that did not (a clear winner, a 1pp tie). A rule that is only ever exercised on the
    one dataset it was written for is a rule nobody has tested.

    Returns (T_chosen, verdict, T_least_bad). `T_least_bad` is the most negative gap among the
    power-passing rows and is ONLY for labelling an exploratory slice downstream; it is never a
    recommendation, and it is returned even when the verdict is NO-FLAG.
    """
    for r in rows:
        r["pass_power"] = bool(r["n_susp"] >= MIN_EVENTS_PER_SIDE
                               and r["n_non"] >= MIN_EVENTS_PER_SIDE
                               and r["tickers_susp"] >= MIN_TICKERS_PER_SIDE
                               and r["tickers_non"] >= MIN_TICKERS_PER_SIDE)
        # CI excludes zero  <=>  both endpoints share a sign
        r["pass_gap"] = bool(r["gap_250"] is not None and r["gap_250"] <= GAP_MAX
                             and r["gap_lo"] is not None and r["gap_hi"] is not None
                             and (r["gap_lo"] < 0) == (r["gap_hi"] < 0)
                             and r["gap_p_holm"] is not None and r["gap_p_holm"] < 0.05)
        r["pass_fpr"] = bool(r["fpr"] is not None and r["fpr"] < FPR_MAX)
        r["eligible"] = bool(r["pass_power"] and r["pass_gap"] and r["pass_fpr"])

    elig = [r for r in rows if r["eligible"]]
    if elig:
        best = max(abs(r["gap_250"]) for r in elig)
        near = [r for r in elig if abs(r["gap_250"]) >= best - 0.01]  # within 1pp => "tied"
        near.sort(key=lambda r: (r["T"], r["fpr"]))                   # then smaller T, then FPR
        chosen, verdict = near[0]["T"], "T_SELECTED"
    else:
        chosen, verdict = None, "NO-FLAG"

    powered = [r for r in rows if r["pass_power"]]
    least_bad = min(powered, key=lambda r: r["gap_250"])["T"] if powered else None
    return chosen, verdict, least_bad


# ------------------------------------------------------------------ Mục 1
def muc1(df: pd.DataFrame, subtypes, tag: str) -> dict:
    p = df[df.subtype.isin(subtypes) & df.pretrend_250.notna() & df.bhar_250.notna()].copy()
    roic_median = float(p.roic_trailing.median())
    fp_elig = p.roic_trailing.notna() & p.fscore.notna()
    p["healthy"] = (p.roic_trailing > roic_median) & (p.fscore > FSCORE_GOOD)

    rows = []
    for T in GRID:
        s = p.pretrend_250 > T
        a, b = p[s], p[~s]
        g = boot_gap(a.bhar_250, b.bhar_250, a.block, b.block)
        sf = fp_elig & s
        fpr = float(p.loc[sf, "healthy"].mean()) if sf.sum() else None
        rows.append({
            "T": T,
            "n_susp": int(len(a)), "n_non": int(len(b)),
            "tickers_susp": int(a.ticker.nunique()), "tickers_non": int(b.ticker.nunique()),
            "partition_ok": bool(len(a) + len(b) == len(p)),
            "mean_bhar250_susp": float(a.bhar_250.mean()),
            "mean_bhar250_non": float(b.bhar_250.mean()),
            "median_bhar250_susp": float(a.bhar_250.median()),
            "gap_250": g["gap"], "gap_lo": g["lo"], "gap_hi": g["hi"], "gap_p": g["p"],
            # DEVIATION D-2: PREREG committed to REPORTING the 500/750 gaps "for context" but
            # specified only the point estimate. A bare point estimate with no CI invites exactly
            # the over-reading this program exists to prevent, so the CI/p are added. They are
            # Holm-adjusted inside their own horizon family and are NOT inputs to the selection
            # rule, which keys on h=250 exactly as preregistered.
            **{f"gap_{h}{k}": v for h in (500, 750)
               for k, v in (lambda d: {"": d["gap"], "_lo": d["lo"], "_hi": d["hi"],
                                       "_p": d["p"]})(
                   boot_gap(a[f"bhar_{h}"], b[f"bhar_{h}"], a.block, b.block)).items()},
            "fpr": fpr, "fpr_denom": int(sf.sum()),
            "mean_pretrend_susp": float(a.pretrend_250.mean()),
        })
    adj = holm({str(r["T"]): r["gap_p"] for r in rows})
    for r in rows:
        r["gap_p_holm"] = adj.get(str(r["T"]))
    for h in (500, 750):  # D-2: separate Holm family per horizon, never pooled with h=250
        a_h = holm({str(r["T"]): r[f"gap_{h}_p"] for r in rows})
        for r in rows:
            r[f"gap_{h}_p_holm"] = a_h.get(str(r["T"]))

    chosen, verdict, least_bad = select_T(rows)

    res = {"tag": tag, "n_population": int(len(p)), "tickers_population": int(p.ticker.nunique()),
           "roic_median_used": roic_median, "grid": rows, "verdict": verdict,
           "T_chosen": chosen, "T_least_bad": least_bad,
           "fpr_denominator_note": "events missing ROIC_Trailing or FSCORE are excluded",
           "fpr_coverage": float(fp_elig.mean())}

    # within-year median sensitivity for the FPR (PREREG §2)
    med_y = p.groupby("year").roic_trailing.transform("median")
    p["healthy_y"] = (p.roic_trailing > med_y) & (p.fscore > FSCORE_GOOD)
    res["fpr_within_year_median"] = {
        str(T): float(p.loc[fp_elig & (p.pretrend_250 > T), "healthy_y"].mean())
        for T in GRID}

    # stability at the chosen (or least-bad) T
    Tx = chosen if chosen is not None else least_bad
    if Tx is not None:
        s = p.pretrend_250 > Tx
        sub = {}
        for nm, mask in (("IS", p.year < OOS_YEAR), ("OOS", p.year >= OOS_YEAR)):
            a, b = p[s & mask], p[~s & mask]
            g = boot_gap(a.bhar_250, b.bhar_250, a.block, b.block)
            g.update({"n_susp": int(len(a)), "n_non": int(len(b))})
            sub[nm] = g
        # D-2 continued: the same IS/OOS split on the context horizons. A long-horizon gap that
        # holds in both halves says something quite different from one carried by the old half,
        # and h=500/750 lose the most recent events by construction (an event needs 750 forward
        # sessions to have a 3Y outcome at all) — so the attrition is reported alongside.
        res_h = {}
        for h in (500, 750):
            col = f"bhar_{h}"
            v = p[p[col].notna()]
            res_h[h] = {"n": int(len(v)), "share_pre_oos": float((v.year < OOS_YEAR).mean()),
                        "max_year": int(v.year.max())}
            for nm, mask in (("IS", p.year < OOS_YEAR), ("OOS", p.year >= OOS_YEAR)):
                a, b = p[s & mask], p[~s & mask]
                d = boot_gap(a[col], b[col], a.block, b.block)
                d.update({"n_susp": int(a[col].notna().sum()),
                          "n_non": int(b[col].notna().sum())})
                res_h[h][nm] = d
        res["stability_long_horizons"] = res_h
        sign_flip = (sub["IS"]["gap"] is not None and sub["OOS"]["gap"] is not None
                     and np.sign(sub["IS"]["gap"]) != np.sign(sub["OOS"]["gap"]))
        # LOO on the suspected leg's BHAR (a year that carries the whole level also carries the gap)
        res["stability"] = {"T_used": Tx, "IS": sub["IS"], "OOS": sub["OOS"],
                            "oos_sign_flip": bool(sign_flip),
                            "loo_suspected": loo(p.loc[s, "bhar_250"].values,
                                                 p.loc[s, "year"].values)}
    return res


# ------------------------------------------------------------------ Mục 2
def muc2(df: pd.DataFrame) -> dict:
    all_iss = df.copy()
    p = df[df.subtype.isin(PRIMARY_SUBTYPES)].copy()
    out: dict = {}

    def by_sector(frame: pd.DataFrame, col: str) -> list[dict]:
        rows = []
        for code, g in frame.groupby(frame.icb_m1.fillna(-1)):
            v = g[col].dropna()
            r = {"icb": int(code), "label": label(code) if code > 0 else "ICB unknown",
                 "n_events": int(len(g)), "n_tickers": int(g.ticker.nunique()),
                 "raises_per_ticker": round(len(g) / max(g.ticker.nunique(), 1), 3),
                 "share_tickers_ge2": float(
                     (g.groupby("ticker").size() >= 2).mean()) if len(g) else None,
                 "n_with_outcome": int(len(v)),
                 "mean": float(v.mean()) if len(v) else None}
            if len(v) >= SECTOR_CI_FLOOR:
                b = boot(v.values, g.loc[v.index, "block"].values)
                r.update({"lo": b["lo"], "hi": b["hi"], "p": b["p"], "median": b["median"]})
            r["below_ci_floor"] = bool(len(v) < SECTOR_CI_FLOOR)
            r["below_verdict_floor"] = bool(len(v) < SECTOR_VERDICT_FLOOR
                                            or g.ticker.nunique() < MIN_TICKERS_PER_SIDE)
            rows.append(r)
        return sorted(rows, key=lambda z: -z["n_events"])

    out["raise_by_sector"] = by_sector(p, "bhar_250")
    out["all_iss_by_sector"] = [r for r in by_sector(all_iss, "bhar_250")][:15]

    # securities (8777) vs everything else, on the primary population
    for name, frame in (("raise", p), ("all_iss", all_iss)):
        a = frame[frame.icb_m1 == SEC_ICB]
        b = frame[frame.icb_m1 != SEC_ICB]
        g = boot_gap(a.bhar_250, b.bhar_250, a.block, b.block)
        g.update({
            "n_sec": int(len(a)), "n_rest": int(len(b)),
            "tickers_sec": int(a.ticker.nunique()), "tickers_rest": int(b.ticker.nunique()),
            "mean_sec": float(a.bhar_250.mean()), "mean_rest": float(b.bhar_250.mean()),
            "mean_pretrend_sec": float(a.pretrend_250.mean()),
            "mean_pretrend_rest": float(b.pretrend_250.mean()),
            "below_verdict_floor": bool(len(a.bhar_250.dropna()) < SECTOR_VERDICT_FLOOR
                                        or a.ticker.nunique() < MIN_TICKERS_PER_SIDE)})
        out[f"sec_vs_rest_{name}"] = g

    # ISS frequency: 8777 vs rest, counted per company over the whole window
    for name, frame in (("raise", p), ("all_iss", all_iss)):
        per = frame.groupby(["ticker"]).agg(n=("t0", "size"),
                                            icb=("icb_m1", "last")).reset_index()
        sec, rest = per[per.icb == SEC_ICB], per[per.icb != SEC_ICB]
        out[f"freq_{name}"] = {
            "sec_tickers": int(len(sec)), "sec_events_per_ticker": float(sec.n.mean()),
            "sec_share_ge2": float((sec.n >= 2).mean()) if len(sec) else None,
            "sec_share_ge3": float((sec.n >= 3).mean()) if len(sec) else None,
            "rest_tickers": int(len(rest)), "rest_events_per_ticker": float(rest.n.mean()),
            "rest_share_ge2": float((rest.n >= 2).mean()),
            "rest_share_ge3": float((rest.n >= 3).mean())}

    top = (all_iss.groupby("ticker")
           .agg(n_iss=("t0", "size"), icb=("icb_m1", "last"),
                n_raise=("subtype", lambda s: int(s.isin(PRIMARY_SUBTYPES).sum())),
                first=("t0", "min"), last=("t0", "max"))
           .sort_values("n_iss", ascending=False).head(20).reset_index())
    top["label"] = top.icb.map(label)
    out["top20_iss"] = top.to_dict("records")

    top_r = (p.groupby("ticker")
             .agg(n_raise=("t0", "size"), icb=("icb_m1", "last"),
                  mean_bhar250=("bhar_250", "mean"), mean_pretrend=("pretrend_250", "mean"))
             .sort_values("n_raise", ascending=False).head(20).reset_index())
    top_r["label"] = top_r.icb.map(label)
    out["top20_raise"] = top_r.to_dict("records")
    return out


# ------------------------------------------------------------------ Mục 3
def bin_beta(x: float) -> str | None:
    if x is None or not np.isfinite(x):
        return None
    return "low" if x <= BETA_LOW_HI else ("mid" if x <= BETA_MID_HI else "high")


def muc3(df: pd.DataFrame, T_used, T_is_recommended: bool) -> dict:
    p = df[df.subtype.isin(PRIMARY_SUBTYPES) & df.bhar_250.notna()].copy()
    p["bbin"] = p.beta_raw.map(bin_beta)
    # Mục 3's population is DELIBERATELY wider than Mục 1's: a beta result needs an outcome, not a
    # pre-trend, so events with a missing `pretrend_250` stay in here (646) while Mục 1 drops them
    # (590). The combined cut below still excludes them, because `NaN > T` is False. Recorded so
    # the two Ns can be reconciled without re-deriving them.
    out: dict = {"n_population": int(len(p)),
                 "n_population_muc1": int((p.pretrend_250.notna()).sum()),
                 "beta_coverage": float(p.beta_raw.notna().mean()),
                 "beta_describe": {k: float(v) for k, v in
                                   p.beta_raw.describe().items()}}

    rows = []
    for nm in ("low", "mid", "high"):
        g = p[p.bbin == nm]
        b = boot(g.bhar_250.values, g.block.values) if len(g) else {}
        rows.append({"bin": nm, "n": int(len(g)), "tickers": int(g.ticker.nunique()),
                     "mean_beta": float(g.beta_raw.mean()) if len(g) else None,
                     "mean_bhar250": float(g.bhar_250.mean()) if len(g) else None,
                     "lo": b.get("lo"), "hi": b.get("hi"), "p": b.get("p"),
                     "median": b.get("median"),
                     "mean_pretrend": float(g.pretrend_250.mean()) if len(g) else None,
                     "below_power_floor": bool(len(g) < MIN_EVENTS_PER_SIDE
                                               or g.ticker.nunique() < MIN_TICKERS_PER_SIDE)})
    adj = holm({r["bin"]: r["p"] for r in rows if r["p"] is not None})
    for r in rows:
        r["p_holm"] = adj.get(r["bin"])
    out["bins_raw_beta"] = rows

    lo_g, hi_g = p[p.bbin == "low"], p[p.bbin == "high"]
    gd = boot_gap(hi_g.bhar_250, lo_g.bhar_250, hi_g.block, lo_g.block)
    means = [r["mean_bhar250"] for r in rows]
    monotone = all(a is not None and b is not None and a >= b
                   for a, b in zip(means, means[1:]))
    out["high_minus_low"] = gd
    out["monotone_decreasing"] = bool(monotone)
    out["ordering_detected"] = bool(monotone and gd["lo"] is not None
                                    and (gd["lo"] < 0) == (gd["hi"] < 0))

    # DEVIATION D-3. PREREG §4 fixed the three bins but specified no stability test for them, while
    # the fleet's standing bar is `edge rớt OOS = loại`. A claim about beta that has not been shown
    # to survive out of sample cannot be written into FLAG_SPEC, so IS/OOS + leave-one-year-out are
    # run here. This check can only WEAKEN a claim, never create one.
    #
    # The regrouping to `beta > 1.2` is not a new cut point: it merges two PREREGISTERED adjacent
    # bins (mid ∪ high). It exists because the dispatched `high` bin (>1.8) holds 31 events and is
    # below the declared power floor, so the powered version of the same ordering has to be stated.
    hi_all = p[p.beta_raw > BETA_LOW_HI]
    lo_all = p[p.beta_raw <= BETA_LOW_HI]
    g12 = boot_gap(hi_all.bhar_250, lo_all.bhar_250, hi_all.block, lo_all.block)
    g12.update({"n_hi": int(len(hi_all)), "n_lo": int(len(lo_all)),
                "tickers_hi": int(hi_all.ticker.nunique()),
                "tickers_lo": int(lo_all.ticker.nunique()),
                "mean_hi": float(hi_all.bhar_250.mean()),
                "mean_lo": float(lo_all.bhar_250.mean()),
                "powered": bool(len(hi_all) >= MIN_EVENTS_PER_SIDE
                                and len(lo_all) >= MIN_EVENTS_PER_SIDE
                                and hi_all.ticker.nunique() >= MIN_TICKERS_PER_SIDE
                                and lo_all.ticker.nunique() >= MIN_TICKERS_PER_SIDE)})
    sub = {}
    for nm, keep in (("IS", lambda f: f[f.year < OOS_YEAR]),
                     ("OOS", lambda f: f[f.year >= OOS_YEAR])):
        a, b = keep(hi_all), keep(lo_all)
        d = boot_gap(a.bhar_250, b.bhar_250, a.block, b.block)
        d.update({"n_hi": int(len(a)), "n_lo": int(len(b))})
        sub[nm] = d
    g12["IS"], g12["OOS"] = sub["IS"], sub["OOS"]
    g12["oos_sign_flip"] = bool(sub["IS"]["gap"] is not None and sub["OOS"]["gap"] is not None
                                and np.sign(sub["IS"]["gap"]) != np.sign(sub["OOS"]["gap"]))
    g12["loo_hi_leg"] = loo(hi_all.bhar_250.values, hi_all.year.values)
    out["beta_gt_1_2_vs_le"] = g12

    # What else moves with beta? Descriptive only — states the confounds instead of hiding them.
    out["bin_covariates"] = [
        {"bin": nm,
         "mean_rvol60": float(g.rvol60.mean()), "median_adv60_vnd": float(g.adv60.median()),
         "mean_pretrend": float(g.pretrend_250.mean()),
         "median_pe": float(g.pe.median()) if g.pe.notna().any() else None,
         "median_roic": float(g.roic_trailing.median()) if g.roic_trailing.notna().any() else None,
         "share_year_lt_2020": float((g.year < OOS_YEAR).mean()),
         "top_sectors": [f"{label(c)} n={n}" for c, n in
                         g.icb_m1.value_counts().head(3).items()]}
        for nm, g in ((nm, p[p.bbin == nm]) for nm in ("low", "mid", "high"))]

    # secondary cross-check on the canonical risk_rating bin (its own 1-5 scale)
    rr = p[p.rr_beta_bin.notna()].copy()
    rr["rrbin"] = pd.cut(rr.rr_beta_bin, [0, 2, 3, 5], labels=["1-2", "3", "4-5"])
    out["rr_coverage"] = float(p.rr_beta_bin.notna().mean())
    out["bins_rr_beta"] = [
        {"bin": str(k), "n": int(len(g)), "tickers": int(g.ticker.nunique()),
         "mean_bhar250": float(g.bhar_250.mean()),
         "mean_beta_raw": float(g.beta_raw.mean()) if g.beta_raw.notna().any() else None,
         **{kk: boot(g.bhar_250.values, g.block.values).get(kk) for kk in ("lo", "hi", "p")}}
        for k, g in rr.groupby("rrbin", observed=True)]
    # does the canonical bin agree with the computed coefficient at all?
    ok = rr.beta_raw.notna()
    out["rr_vs_raw_corr"] = (float(np.corrcoef(rr.loc[ok, "rr_beta_bin"],
                                               rr.loc[ok, "beta_raw"])[0, 1])
                             if ok.sum() > 10 else None)
    out["rr_mean_raw_by_bin"] = {str(k): float(g.beta_raw.mean())
                                 for k, g in rr[ok].groupby("rrbin", observed=True)}

    # combined cut
    if T_used is not None:
        c = p[(p.pretrend_250 > T_used) & (p.bbin == "high")]
        rest = p[~((p.pretrend_250 > T_used) & (p.bbin == "high"))]
        b = boot(c.bhar_250.values, c.block.values) if len(c) else {}
        g = boot_gap(c.bhar_250, rest.bhar_250, c.block, rest.block)
        under = bool(len(c) < COMBINED_MIN_EVENTS or c.ticker.nunique() < COMBINED_MIN_TICKERS)
        out["combined"] = {
            "T_used": T_used, "T_is_recommended": bool(T_is_recommended),
            "n": int(len(c)), "tickers": int(c.ticker.nunique()),
            "mean_bhar250": float(c.bhar_250.mean()) if len(c) else None,
            "lo": b.get("lo"), "hi": b.get("hi"), "p": b.get("p"), "median": b.get("median"),
            "gap_vs_rest": g["gap"], "gap_lo": g["lo"], "gap_hi": g["hi"], "gap_p": g["p"],
            "underpowered": under,
            "verdict": "UNDERPOWERED — no verdict" if under else "powered"}
    return out


def main() -> None:
    df = load()
    res: dict = {"seed": SEED, "nboot": NBOOT, "n_events": int(len(df)),
                 "n_tickers": int(df.ticker.nunique())}
    res["crosschecks"] = crosschecks(df)
    if not res["crosschecks"]["pass"]:
        print(json.dumps(res["crosschecks"], indent=2))
        raise SystemExit("CC1/CC2 FAIL — prior program's numbers not reproduced; stopping.")
    print("CC1/CC2 PASS — prior program reproduced.", flush=True)

    res["muc1_primary"] = muc1(df, PRIMARY_SUBTYPES, "RIGHTS+PP")
    print(f"Mục 1 verdict: {res['muc1_primary']['verdict']} "
          f"(T={res['muc1_primary']['T_chosen']})", flush=True)
    res["muc1_sensitivity_raiseset"] = muc1(df, RAISE_SET, "RAISE_SET (incl AUCTION)")

    res["muc2"] = muc2(df)
    print("Mục 2 done.", flush=True)

    m1 = res["muc1_primary"]
    T_used = m1["T_chosen"] if m1["T_chosen"] is not None else m1["T_least_bad"]
    res["muc3"] = muc3(df, T_used, T_is_recommended=m1["T_chosen"] is not None)
    print("Mục 3 done.", flush=True)

    # CC4 — the chosen/used T's suspected mean vs the prior program's pre-trend-quartile band
    row = next(r for r in m1["grid"] if r["T"] == T_used)
    res["crosschecks"]["CC4"] = {
        "T_used": T_used, "mean_bhar250_susp": row["mean_bhar250_susp"],
        "prior_q2_q3_band": [-0.1038, -0.0790],
        "inside_band": bool(-0.1038 <= row["mean_bhar250_susp"] <= -0.0790)}

    with open(os.path.join(OUT, "results.json"), "w") as fh:
        json.dump(res, fh, indent=2, sort_keys=True, default=str)
    print(json.dumps({"verdict": m1["verdict"], "T_chosen": m1["T_chosen"],
                      "T_used": T_used, "CC4": res["crosschecks"]["CC4"]}, indent=2))


if __name__ == "__main__":
    sys.exit(main())
