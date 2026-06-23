#!/usr/bin/env python3
"""probe_stockpick_2012.py — (B) STOCK-SELECTION test of the user's "2012-13 great buy" memory at the
RIGHT altitude. The index-timing test (backtest_recovery_alloc_2011.py) said hold 14% cash in 2012;
but the user recalls QUALITY names with dividend > deposit recovering hard. This tests whether a
quality + deep-value basket, formed monthly across 2012-13, beat (a) VNINDEX and (b) cash(deposit).

Selection as-of each formation month-end (point-in-time, no look-ahead):
  universe = liquid (Trading_Value_1M_P50>3e9) ticker_prune
  quality floor = NP_P0>0 (profitable) AND FSCORE>=5 AND ROE5Y>=0.08 AND Debt_Eq_P0<2
  cheapness     = pb_z = (PB-PB_MA5Y)/PB_SD5Y, rank ASC, take top-N deepest
Forward return = equal-weight mean of adjusted-Close total return over +126 sess (~6M) / +252 (~12M).
Benchmarks over same window: VNINDEX price return; cash = deposit accrual (DEPOSIT_EVENTS, era-aware).
NOTE pre-2014 PE is corrupt (unused); DY is NULL pre-2013-05 (can't add a dividend tilt for 2012).
Usage: source ./wc_env.sh && $DNA_PYEXE probe_stockpick_2012.py
"""
import warnings; warnings.filterwarnings("ignore")
import os
import numpy as np, pandas as pd
from ic_panel_8l import bq
from deposit_rate_vn import DEPOSIT_EVENTS

TOPN = int(os.environ.get("TOPN", "8"))
FS_MIN = int(os.environ.get("FS_MIN", "5"))
ROE_MIN = float(os.environ.get("ROE_MIN", "0.05"))
LO, HI = os.environ.get("LO", "2011-06-01"), os.environ.get("HI", "2014-12-31")

def load():
    df = bq(f"""SELECT t.time, t.ticker, t.Close, t.VNINDEX,
      SAFE_DIVIDE(t.PB - t.PB_MA5Y, NULLIF(t.PB_SD5Y,0)) pbz,
      t.NP_P0, t.FSCORE, t.ROE5Y, t.Debt_Eq_P0, t.Trading_Value_1M_P50 tv
    FROM tav2_bq.ticker_prune AS t
    WHERE t.time BETWEEN DATE '{LO}' AND DATE '{HI}' AND t.Close>0
    ORDER BY t.time, t.ticker""")
    df["time"] = pd.to_datetime(df["time"])
    return df

def cash_factor(d0, d1):
    """deposit accrual between two dates using the step series (era-aware, causal)."""
    dep = pd.Series({pd.Timestamp(dt): v/100 for dt, v in DEPOSIT_EVENTS}).sort_index()
    days = pd.date_range(d0, d1, freq="D")
    rate = dep.reindex(dep.index.union(days)).ffill().reindex(days)
    return float(np.prod((1 + rate.values) ** (1/365)))

def main():
    df = load()
    # per-ticker forward Close via session index
    df = df.sort_values(["ticker", "time"])
    piv = df.pivot_table(index="time", columns="ticker", values="Close")
    vni = df.groupby("time")["VNINDEX"].first()
    sess = piv.index
    # formation = last trading day of each month
    months = pd.Series(sess, index=sess).groupby(sess.to_period("M")).max()
    rows = []
    for H, hname in [(126, "6M"), (252, "12M")]:
        for m, fdate in months.items():
            si = sess.get_loc(fdate)
            if si + H >= len(sess):  # need forward window
                continue
            fwd_date = sess[si + H]
            snap = df[df["time"] == fdate].copy()
            # quality floor + liquid + cheap rank
            q = snap[(snap.tv > 3e9) & (snap.NP_P0 > 0) & (snap.FSCORE >= FS_MIN)
                     & (snap.ROE5Y >= ROE_MIN) & (snap.Debt_Eq_P0 < 3) & snap.pbz.notna()]
            if len(q) < TOPN:
                continue
            pick = q.nsmallest(TOPN, "pbz")["ticker"].tolist()
            p0 = piv.loc[fdate, pick]; p1 = piv.loc[fwd_date, pick]
            valid = p0.notna() & p1.notna() & (p0 > 0)
            if valid.sum() < TOPN * 0.6:
                continue
            bret = float((p1[valid] / p0[valid] - 1).mean())
            vret = float(vni.loc[fwd_date] / vni.loc[fdate] - 1)
            cret = cash_factor(fdate, fwd_date) - 1
            rows.append(dict(H=hname, form=str(fdate.date()), n=int(valid.sum()),
                             med_pbz=round(float(q["pbz"].min()), 2),
                             basket=bret, vnindex=vret, cash=cret,
                             vs_vni=bret - vret, vs_cash=bret - cret, picks=",".join(pick[:6])))
    R = pd.DataFrame(rows)
    for H in ["6M", "12M"]:
        sub = R[R.H == H]
        if not len(sub): continue
        print(f"\n===== forward {H} — quality+deep-value top{TOPN}, formed monthly =====")
        print(f"{'form':10} {'n':>3} {'basket':>8} {'vnindex':>8} {'cash':>7} {'vs_vni':>7} {'vs_cash':>8}")
        for _, r in sub.iterrows():
            print(f"{r.form:10} {r.n:>3} {r.basket*100:>+7.1f}% {r.vnindex*100:>+7.1f}% "
                  f"{r.cash*100:>+6.1f}% {r.vs_vni*100:>+6.1f}% {r.vs_cash*100:>+7.1f}%")
        print(f"  MEAN over {len(sub)} forms: basket {sub.basket.mean()*100:+.1f}% | "
              f"vni {sub.vnindex.mean()*100:+.1f}% | cash {sub.cash.mean()*100:+.1f}% | "
              f"vs_vni {sub.vs_vni.mean()*100:+.1f}% | vs_cash {sub.vs_cash.mean()*100:+.1f}% | "
              f"win-vs-cash {(sub.vs_cash>0).mean()*100:.0f}%")
    # zoom: the H2-2012 deep-low formations (rates already cut to 9-12%) the user remembers
    print("\n--- ZOOM: H2-2012 / early-2013 formations (rates falling 12->9->7.5%) ---")
    z = R[(R.H == "12M") & (R.form >= "2012-06-01") & (R.form <= "2013-03-31")]
    for _, r in z.iterrows():
        print(f"  {r.form} (12M): basket {r.basket*100:+.1f}% vs vni {r.vnindex*100:+.1f}% "
              f"vs cash {r.cash*100:+.1f}% | picks: {r.picks}")

if __name__ == "__main__":
    main()
