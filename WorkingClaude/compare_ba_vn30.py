"""
BA-only vs BA+VN30 (50/50) vs V5-ensemble — momentum-pillar composition test
=============================================================================
Does the VN30 (large-cap momentum) leg earn its place in the momentum pillar, or
is BA (broad momentum) enough? Compares 3 momentum-pillar variants (real-ETF+DT5G):
  BA-only       = BAL_kelly_leg (100% broad momentum)
  BA+VN30 50/50 = 0.5 BAL + 0.5 VN30 (fixed)
  V5-ensemble   = the production book (BAL + ensemble-switched VN30/LAGGED)
Examines megacap-led windows (2021, 2025) vs broad bull (2017) + grind, since the
VN30 thesis is "captures megacap-led trends BA misses".
Run: python compare_ba_vn30.py
"""
import sys, glob
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
F = WORKDIR + r"\data\5sys_prodspec_201401_202605_dt5g_realetf_legs.csv"


def ann(ret):
    ret = ret.dropna(); n = len(ret)
    if n < 5: return dict(CAGR=np.nan, Sharpe=np.nan, MaxDD=np.nan, Calmar=np.nan)
    mu = ret.mean()*252; sd = ret.std(ddof=1)*np.sqrt(252)
    nav = (1+ret).cumprod(); yrs = n/252; cagr = nav.iloc[-1]**(1/yrs)-1
    dd = (nav/nav.cummax()-1).min()
    return dict(CAGR=cagr*100, Sharpe=mu/sd if sd > 0 else 0, MaxDD=dd*100,
                Calmar=cagr/abs(dd) if dd < 0 else np.nan)


def fmt(m):
    return f"CAGR {m['CAGR']:6.1f}%  Sharpe {m['Sharpe']:5.2f}  MaxDD {m['MaxDD']:6.1f}%  Calmar {m['Calmar']:5.2f}"


def cum(ret):
    return ((1 + ret.dropna()).prod() - 1) * 100


def main():
    df = pd.read_csv(F, parse_dates=["time"]).set_index("time")
    ba = df["BAL_kelly_leg"].pct_change()
    vn = df["VN30_kelly_leg"].pct_change()
    v5 = df["V5_V4_KellyQ2"].pct_change()
    vni = df["VNI"].pct_change()
    arms = {
        "BA-only": ba,
        "BA+VN30 50/50": 0.5*ba + 0.5*vn,
        "V5-ensemble": v5,
        "VN30-only (ref)": vn,
        "VNI B&H (ref)": vni,
    }
    print(f"Momentum-pillar test (real-ETF+DT5G)  {df.index[0].date()} → {df.index[-1].date()}\n")
    print(f"{'variant':>16}  FULL")
    for n, r in arms.items():
        print(f"{n:>16}  {fmt(ann(r))}")

    wins = {"2017 broad bull": ("2017-01-01", "2017-12-31"),
            "2021 megacap bull": ("2021-01-01", "2021-12-31"),
            "2025 (VIC-led narrow)": ("2025-01-01", "2025-12-31"),
            "grind 25-09..26-03": ("2025-09-01", "2026-03-31"),
            "2020 COVID+rebound": ("2020-01-01", "2020-12-31")}
    print(f"\n  --- window cum returns (megacap-led = where VN30 should help) ---")
    print(f"  {'window':>22}  {'BA-only':>9} {'BA+VN30':>9} {'V5-ens':>9} {'VN30':>9} {'VNI':>9}")
    for lbl, (lo, hi) in wins.items():
        sl = lambda r: r[(r.index >= lo) & (r.index <= hi)]
        print(f"  {lbl:>22}  {cum(sl(ba)):8.1f}% {cum(sl(0.5*ba+0.5*vn)):8.1f}% "
              f"{cum(sl(v5)):8.1f}% {cum(sl(vn)):8.1f}% {cum(sl(vni)):8.1f}%")

    # correlation of BA vs VN30 (are they redundant?)
    c = ba.corr(vn)
    print(f"\n  corr(BA, VN30) daily = {c:.2f}  (high = redundant momentum legs)")
    print(f"  BA+VN30 vol {ann(0.5*ba+0.5*vn)['Sharpe']:.2f} Sharpe vs BA-only {ann(ba)['Sharpe']:.2f} "
          f"-> {'VN30 leg ADDS' if ann(0.5*ba+0.5*vn)['Sharpe'] > ann(ba)['Sharpe'] else 'VN30 leg drags'} risk-adj")


if __name__ == "__main__":
    main()
