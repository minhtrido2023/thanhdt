#!/usr/bin/env python3
"""probe_route_eveb_h7.py — H7 (R&D Q3 program Wave 1) pre-backtest proxy: EVEB route-aware
yieldcombo swap for the D&A_HEAVY route. TIER-2 proxy (HIGH bar) because H7 is a close relative
of composite-v3-as-selector, which was REJECTED globally (IS-overfit, -0.78pp OOS). H7 is a NARROW,
route-conditional swap (only ~24 capital-intensive names), NOT a global composite change.

Hypothesis: for D&A_HEAVY names (ports/tankers/BOT-toll/telecom — heavy depreciation depresses
reported earnings, so 1/PE understates value; EVEB=EV/EBITDA is pre-D&A, cleaner), replacing the
1/PCF leg of yieldcombo with 1/EVEB improves selection. Names OUTSIDE the route keep the base
yieldcombo = rank(1/PE)+rank(1/PCF).

DESIGN (identical scaffold to probe_max5_exclude.py / probe_fscore_exclude.py):
  * universe/gate/liquidity/target/route  <- ic_panel_8l.load() (frozen PIT panel, quarterly collapse)
  * PE, PCF, EVEB                          <- re-pulled FRESH from tav2_bq.ticker at the exact quarter-end
    (ticker,time) of each panel row, so all three value legs share ONE adjustment basis. (The frozen
    panel's PE/PCF have drifted from the live table via per-ticker cumulative price adjustment — GMD
    2023-01-31 panel PE 12.14 vs live 16.05, PCF 5.18 vs 6.85, same 1.32x rescale — so mixing frozen
    1/PE with a live 1/EVEB would be an apples-to-oranges cross-section. Pulling all three fresh keeps
    base and H7 on ONE internally-consistent basis; PIT-valid: each value is read at its own `time`.)
  * pool = top-60 by turnover, gate as-of rating<=3 (the set V2.4 acts within); pick top-30 by yieldcombo.

  base:  second leg = rank(1/PCF) for ALL pool names.
  H7:    second leg = rank(1/EVEB) for names in DA_HEAVY_SET, rank(1/PCF) otherwise.
         (1/EVEB and 1/PCF are each ranked cross-sectionally over the WHOLE 60-name pool, then the
          route picks which leg feeds each name — the standard per-route-lens construction.)

Compare mean profit_2M/quarter of the selected top-30, split IS(2014-2019)/OOS(2020+), quarter win%.

PASS (HIGH bar, set in plan because prior is low — close relative already rejected globally):
  H7 must beat base by >= +0.3pp in BOTH halves (dIS >= +0.30 AND dOOS >= +0.30). Fail => CLOSE H7 at
  proxy tier immediately, do NOT try soft-penalty / other variants / the NAV harness.

NOT the NAV backtest — a directional screen (no costs / T+1 / sizing). Reads BQ (no DuckDB cache).
Usage: source ./wc_env.sh && $DNA_PYEXE probe_route_eveb_h7.py
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from ic_panel_8l import load, bq

POOL_N, PICK_N = 60, 30
TGT = "profit_2M"

# DA_HEAVY_SET — copied verbatim from rating_8l.py (2026-07-04, job Taylor_20260704_102937).
# NAME-LEVEL whitelist (DA/Revenue>=5% TTM), NOT ICB-derived. POWER route excluded (own lens).
DA_HEAVY_SET = {
 "ACV","GMD","HAH","PHP","VSC",        # ports
 "PVT","PVP","VOS",                    # tankers
 "CII","HHV","CTI","PC1",             # BOT-toll
 "FOX","VGI",                          # telecom
 "PVD","BWE","REE","VGC","KSV","MSR","VPL","HAG","AAA"}


def attach_val(d):
    """Re-pull PE, PCF, EVEB FRESH from tav2_bq.ticker at each panel (ticker,time). ONE basis for all
    three value legs. PIT: value read at its own quarter-end `time`, strictly no forward field."""
    tickers = sorted(d.ticker.dropna().unique().tolist())
    dates   = sorted(pd.to_datetime(d.time.dropna().unique()))
    tk_in   = ",".join("'%s'" % t for t in tickers)
    dt_in   = ",".join("'%s'" % pd.Timestamp(x).date() for x in dates)
    v = bq(f"""
      SELECT t.ticker AS ticker, t.time AS time, t.PE AS PE_f, t.PCF AS PCF_f, t.EVEB AS EVEB_f
      FROM tav2_bq.ticker AS t
      WHERE t.ticker IN ({tk_in}) AND t.time IN ({dt_in})
    """)
    v["time"] = pd.to_datetime(v["time"])
    for c in ["PE_f", "PCF_f", "EVEB_f"]:
        v[c] = pd.to_numeric(v[c], errors="coerce")
    return d.merge(v, on=["ticker", "time"], how="left")


def main():
    d = load()
    d = attach_val(d)
    d = d[d["rating"] <= 3].copy()                        # gated investable set V2.4 acts within
    d["liq"] = pd.to_numeric(d.get("turnover"), errors="coerce")
    d = d[d["liq"].notna() & d[TGT].notna()]
    rk = lambda s: s.rank(pct=True)

    perq_base, perq_h7 = [], []
    yr = []                                               # year per quarter (for IS/OOS)
    da_in_pool, eveb_cov = [], []                         # diagnostics
    nq = 0
    for qtr, g in d.groupby("q"):
        g = g.sort_values("liq", ascending=False).head(POOL_N)
        if len(g) < PICK_N + 5: continue
        ey_v   = pd.Series(np.where(g["PE_f"]   > 0, 1.0/g["PE_f"],   np.nan), index=g.index)
        cfy_v  = pd.Series(np.where(g["PCF_f"]  > 0, 1.0/g["PCF_f"],  np.nan), index=g.index)
        eveb_v = pd.Series(np.where(g["EVEB_f"] > 0, 1.0/g["EVEB_f"], np.nan), index=g.index)
        r_ey, r_cfy, r_eveb = rk(ey_v).fillna(0.5), rk(cfy_v).fillna(0.5), rk(eveb_v).fillna(0.5)
        is_da = g["ticker"].isin(DA_HEAVY_SET)

        yc_base = r_ey + r_cfy                             # base: 1/PE + 1/PCF for all
        yc_h7   = r_ey + r_cfy.where(~is_da, r_eveb)       # H7: swap PCF->EVEB leg for DA names only

        pick_b = g.loc[yc_base.sort_values(ascending=False).head(PICK_N).index]
        pick_h = g.loc[yc_h7.sort_values(ascending=False).head(PICK_N).index]
        perq_base.append(pick_b[TGT].mean())
        perq_h7.append(pick_h[TGT].mean())
        yr.append(qtr.year)
        da_in_pool.append(int(is_da.sum()))
        eveb_cov.append(float((g["EVEB_f"] > 0).mean()))
        nq += 1

    perq_base, perq_h7, yr = np.array(perq_base), np.array(perq_h7), np.array(yr)
    IS, OOS = yr <= 2019, yr >= 2020
    b_all, h_all = perq_base.mean(), perq_h7.mean()
    b_is,  h_is  = perq_base[IS].mean(),  perq_h7[IS].mean()
    b_oos, h_oos = perq_base[OOS].mean(), perq_h7[OOS].mean()
    winq = float(np.mean(perq_h7 > perq_base))
    # quarters where the DA-swap actually changed the top-30 (else H7==base identically)
    changed = int(np.sum(np.abs(perq_h7 - perq_base) > 1e-9))

    print(f"H7 EVEB route-aware yieldcombo swap (D&A_HEAVY) — forward {TGT}, top-{PICK_N} of top-{POOL_N} "
          f"liquid, gate rating<=3, {nq} quarters")
    print(f"DA names in pool/quarter: mean {np.mean(da_in_pool):.1f} (min {min(da_in_pool)}, "
          f"max {max(da_in_pool)}) | pool EVEB>0 cov mean {np.mean(eveb_cov):.2f} | "
          f"quarters where swap changed top-30: {changed}/{nq}\n")
    print(f"{'split':>10} {'base%':>9} {'H7%':>9} {'dpp':>8}")
    print(f"{'ALL':>10} {b_all:>9.2f} {h_all:>9.2f} {h_all-b_all:>+8.2f}")
    print(f"{'IS(14-19)':>10} {b_is:>9.2f} {h_is:>9.2f} {h_is-b_is:>+8.2f}")
    print(f"{'OOS(20+)':>10} {b_oos:>9.2f} {h_oos:>9.2f} {h_oos-b_oos:>+8.2f}")
    print(f"\nquarter win% (H7 > base): {winq:.0%}")

    d_is, d_oos = h_is - b_is, h_oos - b_oos
    BAR = 0.30
    passes = (d_is >= BAR) and (d_oos >= BAR)
    print(f"\nPASS rule (TIER-2, HIGH bar): H7 - base >= +{BAR:.2f}pp in BOTH IS and OOS.")
    print(f"  dIS {d_is:+.2f}pp, dOOS {d_oos:+.2f}pp  ->  {'PASS' if passes else 'FAIL'}")
    if not passes:
        print("  => CLOSE H7 at proxy tier. Do NOT try soft-penalty / variants / NAV harness (prior low,")
        print("     close relative = composite-v3-as-selector already rejected globally).")
    print("\nNOTE: directional proxy (no NAV sim / costs / T+1). Fresh PE/PCF/EVEB from tav2_bq.ticker so")
    print("all three legs share one adjustment basis; base here is the internal control, not production NAV.")


if __name__ == "__main__":
    main()
