#!/usr/bin/env python3
"""probe_max5_exclude.py — H6a (R&D Q3 program Wave 1) pre-backtest proxy: MAX5_1M
LOTTERY-EXCLUSION overlay. T2 panel-extension (job Taylor_20260705_075638) confirmed MAX5_1M
(mean of 5 largest daily adj returns over trailing 21 sessions) is the ONE surviving marginal-IC
lens: mIC -0.047 IS / -0.042 OOS (both clear <=-0.03), crash% Q5 10.1% vs Q1 4.2% — the lottery/
MAX effect (Bali-Cakici-Whitelaw 2011) on VN, orthogonal to the value block. Its natural form is
an EXCLUSION/penalty overlay (avoid the most lottery-like names inside the value basket), NOT a
value tilt. This probe tests that: within the top-60 liquid gated pool each quarter, DROP the
top-q by MAX5_1M (the MOST lottery-like) BEFORE ranking yieldcombo = rank(1/PE)+rank(1/PCF), then
pick top-30 as usual. Same design as H1 (probe_fscore_exclude.py) but the lens is inverted:
H1 drops the WORST-quality tail (low FSCORE), here we drop the HIGHEST-lottery tail (high MAX5).

q in {10%, 20%} only (2 points, NOT a grid-sweep). Compared to base (no exclusion) on the same
frozen PIT panel: mean profit_2M per quarter, quarter win% vs base, split IS(2014-2019)/OOS(2020+).
Reuses ic_panel_8l.{load,bq}; MAX5_1M attached as-of each quarter (backward-only, end-of-day at obs,
identical query to ic_panel_ext_q3.attach_new_lenses). NOT the NAV backtest — a directional screen
to decide whether the full pt_v23 harness is worth building.

PASS = mean profit_2M >= base in BOTH IS AND OOS, quarter win% >= 50%, AND strictly better than the
H1 negative-control (H1 FAILED at this tier: dIS/dOOS both negative). Fail => close H6a at proxy
tier, do NOT build the harness.
Usage: source ./wc_env.sh && $DNA_PYEXE probe_max5_exclude.py
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from ic_panel_8l import load, bq

POOL_N, PICK_N = 60, 30
TGT = "profit_2M"
QS = [0.0, 0.10, 0.20]          # 0.0 = base (no exclusion); 10% and 20% top-MAX5 drop


def attach_max5(d):
    """Merge MAX5_1M as-of each panel row (ticker, time). PIT: trailing 21 sessions ending at obs,
    end-of-day at obs date, strictly backward. Same SQL as ic_panel_ext_q3.attach_new_lenses (H6a)."""
    tickers = sorted(d.ticker.dropna().unique().tolist())
    dates   = sorted(pd.to_datetime(d.time.dropna().unique()))
    tk_in   = ",".join("'%s'" % t for t in tickers)
    dt_in   = ",".join("'%s'" % pd.Timestamp(x).date() for x in dates)
    micro = bq(f"""
      WITH base AS (
        SELECT k.ticker AS ticker, k.time AS time,
               SAFE_DIVIDE(k.Close, k.Close_T1)-1 AS ret_adj
        FROM tav2_bq.ticker AS k
        WHERE k.ticker IN ({tk_in}) AND k.time >= '2013-06-01'
      ),
      w AS (
        SELECT ticker, time,
               ARRAY_AGG(ret_adj) OVER win AS arr,
               COUNTIF(ret_adj IS NOT NULL) OVER win AS nd
        FROM base
        WINDOW win AS (PARTITION BY ticker ORDER BY time ROWS BETWEEN 20 PRECEDING AND CURRENT ROW)
      )
      SELECT ticker, time,
             (SELECT AVG(x) FROM UNNEST(ARRAY(SELECT r FROM UNNEST(arr) r WHERE r IS NOT NULL ORDER BY r DESC LIMIT 5)) x) AS max5_1M,
             nd
      FROM w
      WHERE time IN ({dt_in}) AND nd >= 15
    """)
    micro["time"] = pd.to_datetime(micro["time"])
    micro["max5_1M"] = pd.to_numeric(micro["max5_1M"], errors="coerce")
    d = d.merge(micro[["ticker", "time", "max5_1M"]], on=["ticker", "time"], how="left")
    return d


def main():
    d = load()
    d = attach_max5(d)
    d = d[(d["rating"] <= 3)].copy()                        # the gated investable set V2.4 acts within
    d["liq"] = pd.to_numeric(d.get("turnover"), errors="coerce")
    d = d[d["liq"].notna() & d[TGT].notna()]
    rk = lambda s: s.rank(pct=True)
    perq = {q: [] for q in QS}; perq_yr = {q: [] for q in QS}
    dropped = {q: [] for q in QS}            # avg names excluded from the pool (diagnostic)
    cov = []                                 # max5_1M coverage inside each pool (diagnostic)
    nq = 0
    for qtr, g in d.groupby("q"):
        g = g.sort_values("liq", ascending=False).head(POOL_N)      # tradable pool (top-60 liquid gated)
        if len(g) < PICK_N + 5: continue
        ey_v  = pd.Series(np.where(g["PE"]  > 0, 1.0/g["PE"],  np.nan), index=g.index)
        cfy_v = pd.Series(np.where(g["PCF"] > 0, 1.0/g["PCF"], np.nan), index=g.index)
        yc = rk(ey_v).fillna(0.5) + rk(cfy_v).fillna(0.5)           # yieldcombo, identical to production
        mx = pd.to_numeric(g["max5_1M"], errors="coerce")
        mx_pct = mx.rank(pct=True)                                  # NaN max5 -> NaN pct (fail-safe: keep)
        cov.append(float(mx.notna().mean()))
        nq += 1
        for q in QS:
            if q == 0.0:
                pool = g
            else:
                # fail-safe: exclude ONLY names whose MAX5 is known-HIGH (rank pct >= 1-q); keep NaN-max5
                keep = ~(mx_pct >= 1.0 - q)                         # NaN -> keep (not known-high)
                pool = g[keep]
                dropped[q].append(int((~keep).sum()))
            if len(pool) < PICK_N: continue                         # safety; near-never with q<=0.2
            sc = yc.loc[pool.index]
            pick = pool.loc[sc.sort_values(ascending=False).head(PICK_N).index]
            m = pick[TGT].mean()
            perq[q].append(m); perq_yr[q].append((qtr.year, m))
    print(f"H6a MAX5_1M top-EXCLUSION overlay — selected-basket forward {TGT} "
          f"(equal-weight top-{PICK_N} of top-{POOL_N} liquid, gate rating<=3), {nq} quarters")
    print(f"pool max5_1M coverage: mean {np.mean(cov):.2f} (fail-safe keeps NaN-max5 names)\n")
    print(f"{'excl_q':>7} {'mean2M%':>9} {'vs base':>9} {'IS(14-19)':>10} {'OOS(20+)':>9} "
          f"{'win%q':>6} {'avg_drop':>9}")
    base_mean = np.mean(perq[0.0])
    base_is   = np.mean([m for (y, m) in perq_yr[0.0] if y <= 2019])
    base_oos  = np.mean([m for (y, m) in perq_yr[0.0] if y >= 2020])
    verdict = {}
    for q in QS:
        arr = np.array(perq[q]); ys = perq_yr[q]
        isv  = np.mean([m for (y, m) in ys if y <= 2019])
        oosv = np.mean([m for (y, m) in ys if y >= 2020])
        winq = (np.mean([1.0 if a > b else 0.0 for a, b in zip(perq[q], perq[0.0])])
                if q != 0 else np.nan)
        avgdrop = (np.mean(dropped[q]) if q != 0 else 0.0)
        print(f"{q:>7.2f} {arr.mean():>9.2f} {arr.mean()-base_mean:>+9.2f} {isv:>10.2f} {oosv:>9.2f} "
              f"{('   -  ' if q==0 else f'{winq:>5.0%}')} {avgdrop:>9.1f}")
        if q != 0:
            verdict[q] = dict(passes=(isv >= base_is and oosv >= base_oos and winq >= 0.50),
                              d_mean=arr.mean()-base_mean, d_is=isv-base_is, d_oos=oosv-base_oos, winq=winq)
    print(f"\nbase: mean {base_mean:.2f} | IS {base_is:.2f} | OOS {base_oos:.2f}")
    print("PASS rule = mean2M >= base in BOTH IS and OOS AND win%q >= 50% (and beats H1 neg-control).")
    for q, v in verdict.items():
        tag = "PASS" if v["passes"] else "FAIL"
        print(f"  excl {q:.0%}: {tag}  (dIS {v['d_is']:+.2f}, dOOS {v['d_oos']:+.2f}, winq {v['winq']:.0%})")
    print("\nNOTE: directional proxy (no NAV sim/costs/T+1). Full pt_v23 harness (env BASKET_MAX5_PENALTY,")
    print("OFF-default) only worth building if a q PASSES here.")


if __name__ == "__main__":
    main()
