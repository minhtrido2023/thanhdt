#!/usr/bin/env python3
"""
sector_strong_threshold.py — calibrate the STRONG (screaming-buy) tier for Group-A sector
lenses that today only have an ACCUMULATE tier (job Taylor_20260706_070219).

METHOD (same discipline that produced CTR EVEB<9 = STRONG):
  1. For each sector, pool the ICB universe (statistical power; single-name histories like
     FPT/MSH/DHG are too thin to calibrate a threshold on alone) and apply the SAME quality
     gate + buy-window the live monitor uses -> the ACCUMULATE-eligible population.
  2. Rank that in-window population by DEPTH (how deep in the buy window) and split into
     quintiles (Q5 = deepest / most-oversold vs its own history).
  3. Measure forward return (profit_1M / 2M / 3M — EVAL ONLY, never a live filter) per
     depth quintile, split walk-forward IS(2014-19) / OOS(2020-26).
  4. A STRONG tier is justified ONLY if there is a real STEP-UP in forward return at some
     depth AND it survives OOS. If the return rises smoothly with no break, we say so and
     fall back to a fixed top-quantile percentile line (honest, not a fabricated break).

Overlap: daily forward returns overlap heavily. We sample every 5th trading day per name
(weekly) to cut autocorrelation ~5x and report N (weekly obs) honestly. RESEARCH ONLY —
reads the read-only BQ DuckDB cache; touches no production file.
"""
import os, duckdb, numpy as np, pandas as pd

ROOT = os.environ.get("WORKDIR", "/home/trido/thanhdt/WorkingClaude")
CACHE = os.path.join(ROOT, "data", "bq_cache")
TKG = f"read_parquet('{CACHE}/ticker/*.parquet')"

# sector -> ICB codes to pool
SECTORS = {
    "Banking":    [8355],
    "Tech":       [9537],
    "Textile":    [3763],
    "Securities": [8777],
    "Pharma":     [4577],
    "Logistics":  [2777, 2773],
}


def load_sector(icbs):
    q = ",".join(str(i) for i in icbs)
    df = duckdb.sql(f"""
        SELECT ticker, CAST(time AS DATE) AS time, PE, PB, EVEB, PE_MA5Y, ROE5Y, ROE_Min3Y, ROIC5Y,
               IntCov_P0, Debt_Eq_P0, profit_1M, profit_2M, profit_3M
        FROM {TKG}
        WHERE ICB_Code IN ({q}) AND CAST(time AS DATE) >= DATE '2014-01-01'
        ORDER BY ticker, time
    """).df()
    # self-rolled trailing-1Y (252 trading day) mean of daily PE per ticker (PE_MA1Y proxy;
    # PE_MA1Y is not in the daily ticker cache, only quarterly ticker_financial — the rolling
    # daily mean is a finer-grained, join-free equivalent, and STRONG is expressed as a RATIO
    # so the exact MA source washes out).
    df["PE_MA1Y"] = (df.groupby("ticker")["PE"]
                       .transform(lambda s: s.rolling(252, min_periods=120).mean()))
    return df


def gate_and_depth(sector, d):
    """Return (in_window_mask, depth_series) where depth is increasing = deeper in buy window.
    Mirrors the live monitor gate for each sector."""
    pe, pb, eveb = d["PE"], d["PB"], d["EVEB"]
    if sector == "Banking":
        just = (d["ROE5Y"] - 0.05) / 0.08
        qual = (d["ROE5Y"] >= 0.12) & (d["ROE_Min3Y"] >= 0.08)
        win = qual & (pb > 0) & (pb < 2.0) & (pb < just)
        depth = (just - pb) / just                       # discount fraction
    elif sector == "Tech":
        thr = d["PE_MA1Y"] * 0.9
        qual = (d["ROIC5Y"] > 0.12) & (d["ROE5Y"] > 0.15)
        win = qual & (pe > 0) & (pe < thr)
        depth = 1.0 - pe / d["PE_MA1Y"]                   # how far below own 1Y PE
    elif sector == "Textile":
        qual = (d["ROE5Y"] > 0.15) & ((d["IntCov_P0"] > 1.5) | d["IntCov_P0"].isna())
        win = qual & (pe > 0) & (pe < d["PE_MA1Y"])
        depth = 1.0 - pe / d["PE_MA1Y"]
    elif sector == "Securities":
        # inflection gate (ROE_Trailing>ROE3Y) needs quarterly financial -> approximated here by
        # the euphoria cap + efficiency proxy on daily fields; depth = how far below the 1.8 cap.
        qual = (d["IntCov_P0"] > 1.5) | d["IntCov_P0"].isna()
        win = qual & (pb > 0) & (pb < 1.8)
        depth = (1.8 - pb) / 1.8
    elif sector == "Pharma":
        qual = (d["ROE5Y"] > 0.15) & (d["ROIC5Y"] > 0.15)
        win = qual & (pe > 0) & (pe < d["PE_MA5Y"])
        depth = 1.0 - pe / d["PE_MA5Y"]
    elif sector == "Logistics":
        # Screen A (EVEB cheap) union Screen B (PB trough); depth = normalized cheapness on the
        # metric that flags. Use EVEB<10 branch (broader) as the primary buy window here.
        qual = (d["ROE5Y"] > 0.15) & (d["Debt_Eq_P0"] < 2.0)
        win = qual & (eveb > 0) & (eveb < 10)
        depth = (10.0 - eveb) / 10.0
    else:
        raise ValueError(sector)
    return win.fillna(False), depth


def weekly_sample(d):
    """every 5th trading-day row per ticker to cut forward-return overlap."""
    return d.groupby("ticker", group_keys=False).apply(lambda g: g.iloc[::5])


def bucketize(sub, depth_col="depth", n=5):
    try:
        sub = sub.copy()
        sub["q"] = pd.qcut(sub[depth_col], n, labels=False, duplicates="drop") + 1
        return sub
    except ValueError:
        return None


def report(sector, d):
    win, depth = gate_and_depth(sector, d)
    d = d.assign(depth=depth)[win].dropna(subset=["depth", "profit_1M"])
    d = weekly_sample(d)
    n_all = len(d)
    if n_all < 100:
        print(f"\n### {sector}: only {n_all} in-window weekly obs — TOO THIN, skip.")
        return None
    out = {"sector": sector, "n": n_all}
    for label, sub in [("ALL", d),
                       ("IS 2014-19", d[d["time"] < "2020-01-01"]),
                       ("OOS 2020-26", d[d["time"] >= "2020-01-01"])]:
        b = bucketize(sub)
        print(f"\n### {sector} — {label}  (in-window weekly N={len(sub)}, "
              f"depth range {sub['depth'].min():.3f}..{sub['depth'].max():.3f})")
        if b is None or b["q"].nunique() < 3:
            print("   (insufficient spread to bucket)")
            continue
        g = b.groupby("q").agg(
            depth_lo=("depth", "min"), depth_hi=("depth", "max"),
            n=("depth", "size"),
            p1M=("profit_1M", "mean"), p2M=("profit_2M", "mean"), p3M=("profit_3M", "mean"),
            hit1M=("profit_1M", lambda s: (s > 0).mean()))
        print(g.round(3).to_string())
        if label == "ALL":
            out["table"] = g
    return out


# =====================================================================================
# FOLLOW-UP (job Taylor_20260706_074228) — quant-skeptic CONFIRMED asked for two robustness
# add-ons. NOTHING below changes the calibration above; it stress-tests it.
#   Việc 1 (Tech/FPT sample thinness): enumerate the tech ICB universe (can we add names?),
#     then block/episode bootstrap the FPT STRONG-line forward return to put a CI on the
#     +3.5%/1M IS & +7.3%/3M OOS point estimates.
#   Việc 2 (Banking & Securities plateau): sweep the chosen line ±one step and re-measure
#     forward return / hit IS+OOS — a robust line is a PLATEAU, not a single sensitive point.
# =====================================================================================

def tech_universe_check():
    """Việc 1.1 — is the tech STRONG sample expandable beyond FPT? Enumerate ICB 9537:
    liquidity (avg daily turnover) + whether each name passes the live quality gate
    (ROIC5Y>0.12 & ROE5Y>0.15). A name only helps the sample if it is BOTH tradeable AND
    a quality compounder (the gate the monitor applies)."""
    print("\n" + "=" * 96)
    print("VIỆC 1.1 — TECH (ICB 9537) UNIVERSE: can we add names to the FPT-only STRONG sample?")
    print("=" * 96)
    df = duckdb.sql(f"""
        SELECT ticker, COUNT(*) AS days, MIN(time) AS first, MAX(time) AS last,
               AVG(Close*Volume) AS turnover_vnd, AVG(ROIC5Y) AS roic5y, AVG(ROE5Y) AS roe5y
        FROM {TKG} WHERE ICB_Code=9537 AND CAST(time AS DATE) >= DATE '2014-01-01'
        GROUP BY ticker ORDER BY turnover_vnd DESC
    """).df()
    df["turnover_bnVND"] = (df["turnover_vnd"] / 1e9).round(2)
    # quality-gate pass = fraction of days meeting ROIC5Y>0.12 & ROE5Y>0.15
    q = duckdb.sql(f"""
        SELECT ticker,
               AVG(CASE WHEN ROIC5Y>0.12 AND ROE5Y>0.15 THEN 1.0 ELSE 0.0 END) AS q_pass_frac
        FROM {TKG} WHERE ICB_Code=9537 AND CAST(time AS DATE) >= DATE '2014-01-01'
        GROUP BY ticker
    """).df()
    df = df.merge(q, on="ticker")
    # liquidity floor: a real book needs ~>=1 bn VND/day (the monitor's tradeable-name bar)
    df["tradeable"] = df["turnover_bnVND"] >= 1.0
    df["quality"] = df["q_pass_frac"] >= 0.10          # ever a compounder in-sample
    df["USABLE"] = df["tradeable"] & df["quality"]
    print(df[["ticker", "days", "turnover_bnVND", "q_pass_frac", "tradeable",
              "quality", "USABLE"]].round(3).to_string(index=False))
    usable = df[df["USABLE"]]["ticker"].tolist()
    print(f"\n→ USABLE (tradeable ≥1bn/day AND passes quality gate): {usable}")
    print("  Interpretation: the STRONG study population is exactly these names. If it is [FPT]")
    print("  only, the universe CANNOT be widened — go to the bootstrap CI (Việc 1.2).")
    return usable


def _episodes(dates, gap_days=90):
    """Group an ordered date series into episodes separated by > gap_days (a de-rating cluster
    is one independent event; 26 weekly obs in 3 clusters is effectively n≈3, not 26)."""
    dates = list(dates)
    eps, cur = [], [0]
    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days > gap_days:
            eps.append(cur); cur = []
        cur.append(i)
    if cur:
        eps.append(cur)
    return eps


def bootstrap_fpt_strong(n_boot=5000, seed=20260706):
    """Việc 1.2 — CI on the FPT STRONG-line (depth>=0.25 i.e. PE<0.75*PE_MA1Y) forward return.
    Two resamplers, because the honest N is the number of de-rating EPISODES, not weekly rows:
      (a) i.i.d. weekly bootstrap  — the OPTIMISTIC bound (ignores overlap/clustering);
      (b) episode-cluster bootstrap — resample whole de-rating episodes (the HONEST bound).
    Report point, 90/95% CI and P(mean>0) for each of profit_1M/2M/3M, split IS/OOS/ALL."""
    print("\n" + "=" * 96)
    print("VIỆC 1.2 — FPT STRONG-line forward-return BOOTSTRAP CI (depth>=0.25 = PE<0.75*PE_MA1Y)")
    print("=" * 96)
    df = duckdb.sql(f"""
        SELECT CAST(time AS DATE) AS time, PE, ROIC5Y, ROE5Y, profit_1M, profit_2M, profit_3M
        FROM {TKG} WHERE ticker='FPT' AND CAST(time AS DATE) >= DATE '2014-01-01' ORDER BY time
    """).df()
    df["PE_MA1Y"] = df["PE"].rolling(252, min_periods=120).mean()
    df["depth"] = 1.0 - df["PE"] / df["PE_MA1Y"]
    qual = (df["ROIC5Y"] > 0.12) & (df["ROE5Y"] > 0.15)
    win = qual & (df["PE"] > 0) & (df["PE"] < df["PE_MA1Y"] * 0.9)
    d = df[win.fillna(False)].dropna(subset=["depth", "profit_1M"]).copy()
    d = d.iloc[::5]                                    # weekly, same as the calibration
    strong = d[d["depth"] >= 0.25].reset_index(drop=True)
    rng = np.random.default_rng(seed)

    for label, sub in [("ALL 2014-26", strong),
                       ("IS 2014-19", strong[strong["time"] < pd.Timestamp("2020-01-01")]),
                       ("OOS 2020-26", strong[strong["time"] >= pd.Timestamp("2020-01-01")])]:
        sub = sub.reset_index(drop=True)
        eps = _episodes(sub["time"])
        yrs = sorted(set(str(t)[:4] for t in sub["time"]))
        print(f"\n--- FPT STRONG · {label}: N_weekly={len(sub)}, episodes(n_eff)={len(eps)} "
              f"[{','.join(yrs)}] ---")
        if len(sub) < 4:
            print("   too few obs to bootstrap"); continue
        for col in ["profit_1M", "profit_2M", "profit_3M"]:
            vals = sub[col].dropna().values
            pt = vals.mean()
            # (a) i.i.d weekly
            bi = rng.choice(vals, size=(n_boot, len(vals)), replace=True).mean(axis=1)
            # (b) episode-cluster: resample whole episodes with replacement
            ep_arrays = [sub[col].iloc[ix].dropna().values for ix in eps]
            ep_arrays = [a for a in ep_arrays if len(a)]
            bc = np.empty(n_boot)
            for k in range(n_boot):
                pick = rng.integers(0, len(ep_arrays), size=len(ep_arrays))
                bc[k] = np.concatenate([ep_arrays[j] for j in pick]).mean()
            def ci(b, lo, hi):
                return np.percentile(b, lo), np.percentile(b, hi)
            i90 = ci(bi, 5, 95); i95 = ci(bi, 2.5, 97.5)
            c90 = ci(bc, 5, 95); c95 = ci(bc, 2.5, 97.5)
            print(f"  {col}: point={pt:+.2f}%")
            print(f"     iid-weekly   90%CI [{i90[0]:+.2f},{i90[1]:+.2f}]  95%CI "
                  f"[{i95[0]:+.2f},{i95[1]:+.2f}]  P(>0)={(bi>0).mean():.2f}")
            print(f"     episode(n≈{len(ep_arrays)}) 90%CI [{c90[0]:+.2f},{c90[1]:+.2f}]  95%CI "
                  f"[{c95[0]:+.2f},{c95[1]:+.2f}]  P(>0)={(bc>0).mean():.2f}")
    print("\n→ Read the EPISODE CI as the real one: if it spans 0 the point estimate is not")
    print("  statistically separable from noise on n≈3 episodes — decide the line on that basis.")


def sensitivity_sweep(sector, icbs, thresholds, kind):
    """Việc 2 — sweep the chosen line ±one step. For each threshold recompute forward return /
    hit over the population AT-OR-BEYOND that line (the actual STRONG trigger set), IS+OOS.
    kind='bank_disc' -> depth(discount)>=thr ; kind='sec_pb' -> PB<thr (deeper=lower)."""
    print("\n" + "=" * 96)
    print(f"VIỆC 2 — {sector} PLATEAU SWEEP ({kind}, thresholds={thresholds})")
    print("=" * 96)
    d0 = load_sector(icbs)
    win, depth = gate_and_depth(sector, d0)
    if kind == "sec_pb":
        base = d0.assign(depth=depth, PB_=d0["PB"])[win].dropna(subset=["profit_1M", "PB_"])
    else:
        base = d0.assign(depth=depth)[win].dropna(subset=["depth", "profit_1M"])
    base = weekly_sample(base)
    rows = []
    for thr in thresholds:
        if kind == "sec_pb":
            sel = base[base["PB_"] < thr]
        else:
            sel = base[base["depth"] >= thr]
        for seg, mask in [("ALL", sel["time"].notna()),
                          ("IS", sel["time"] < "2020-01-01"),
                          ("OOS", sel["time"] >= "2020-01-01")]:
            s = sel[mask]
            rows.append({
                "thr": thr, "seg": seg, "n": len(s),
                "p1M": round(s["profit_1M"].mean(), 2) if len(s) else np.nan,
                "p3M": round(s["profit_3M"].mean(), 2) if len(s) else np.nan,
                "hit1M": round((s["profit_1M"] > 0).mean(), 3) if len(s) else np.nan,
            })
    r = pd.DataFrame(rows)
    print(r.pivot(index="thr", columns="seg", values=["n", "p1M", "p3M", "hit1M"]).to_string())
    print("→ PLATEAU if p1M/p3M/hit stay similar across the 3 thresholds (line is robust);")
    print("  a spike at only the middle threshold = single-point artifact / possible overfit.")
    return r


def main():
    print("=" * 96)
    print("STRONG-TIER THRESHOLD CALIBRATION — depth quintile vs forward return (profit_*, %, EVAL-ONLY)")
    print("job Taylor_20260706_070219 | pooled ICB universe, live-monitor gate, weekly-sampled, IS/OOS")
    print("=" * 96)
    results = {}
    for sector, icbs in SECTORS.items():
        d = load_sector(icbs)
        results[sector] = report(sector, d)
    print("\n" + "=" * 96)
    print("Read the Q5 (deepest) row vs Q1-Q4: a STRONG tier is justified only where Q5 fwd return")
    print("STEPS UP materially AND the step survives OOS. Smooth/no-break -> fixed top-quantile line.")
    print("=" * 96)

    # ---- Follow-up robustness (job Taylor_20260706_074228) ----
    tech_universe_check()
    bootstrap_fpt_strong()
    sensitivity_sweep("Banking", [8355], [0.40, 0.45, 0.50], "bank_disc")
    sensitivity_sweep("Securities", [8777], [0.70, 0.75, 0.80], "sec_pb")


if __name__ == "__main__":
    main()
