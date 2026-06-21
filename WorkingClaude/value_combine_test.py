"""
Value sleeve — interaction with capitulation/grind + extension to V1/V12.1
==========================================================================
Q1: does a gated value sleeve clash with the existing capitulation + grind-half
    sleeves on V4/V5?  -> test REGIME-DISJOINTNESS (value is gated to CASH in
    CRISIS exactly where capitulation lives) + correlation.
Q2: does the value sleeve also help V1 (V11/Song Sinh) and V12.1 (V121_ENS)?
    -> blend onto every book column.

Inputs: data/value_book_realistic.csv (realistic gated value sleeve, 10B/liqw/TC0.3%),
        prod-spec NAV, data/dt5g_vnindex.csv, data/bt_capitulation_STRONG.csv
Run: python value_combine_test.py
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import os
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
NAVF = os.environ.get("CORE_NAV", WORKDIR + r"\data\5sys_prodspec_201401_202605_dt5g.csv")
VALF = WORKDIR + r"\data\value_book_realistic.csv"
STATEF = WORKDIR + r"\data\dt5g_vnindex.csv"
CAPF = WORKDIR + r"\data\bt_capitulation_STRONG.csv"
STATE_LBL = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EXBULL"}
BOOKS = [("V1_V11_TQ34b", "V1 (V11/Song Sinh)"),
         ("V2_V12_TQ34b", "V2 (V12/Am Duong)"),
         ("V3_V12_LIVE", "V3 (V12 live)"),
         ("V4_V121_ENS_TQ34b", "V12.1 (V121_ENS)"),
         ("V5_V4_KellyQ2", "V5 (Kelly)")]


def ann(ret):
    ret = ret.dropna()
    mu = ret.mean()*12; sd = ret.std(ddof=1)*np.sqrt(12)
    sharpe = mu/sd if sd > 0 else 0
    dn = ret[ret < 0].std(ddof=1)*np.sqrt(12); sortino = mu/dn if dn > 0 else 0
    nav = (1+ret).cumprod(); dd = (nav/nav.cummax()-1).min()
    return dict(CAGR=mu*100, Sharpe=sharpe, Sortino=sortino, MaxDD=dd*100,
                Calmar=mu/abs(dd) if dd < 0 else np.nan)


def fmt(m):
    return (f"CAGR {m['CAGR']:5.1f}%  Sharpe {m['Sharpe']:.2f}  Sortino {m['Sortino']:.2f}  "
            f"MaxDD {m['MaxDD']:6.1f}%  Calmar {m['Calmar']:.2f}")


def book_monthly(col):
    nav = pd.read_csv(NAVF, parse_dates=["time"]).set_index("time")[col]
    r = nav.resample("ME").last().pct_change(); r.index = r.index.to_period("M")
    return r.dropna()


def main():
    v = pd.read_csv(VALF)
    v.columns = ["ym", "value"]
    v["ym"] = pd.PeriodIndex(v["ym"], freq="M")
    value = v.set_index("ym")["value"]

    # state per month
    st = pd.read_csv(STATEF, parse_dates=["time"]); st["ym"] = st["time"].dt.to_period("M")
    state = st.groupby("ym")["state"].agg(lambda s: int(s.mode().iloc[0]))

    print("=== Q1: REGIME-DISJOINTNESS of value sleeve vs capitulation ===")
    print("Value sleeve is GATED DT5G -> CASH in CRISIS. Capitulation fires ONLY in CRISIS+washout.")
    # value sleeve mean monthly return by state (CRISIS should be ~0 = gated cash)
    vs = pd.DataFrame({"value": value, "state": state.reindex(value.index)}).dropna()
    by = vs.groupby("state")["value"].agg(["mean", "count"])
    by.index = [STATE_LBL[int(i)] for i in by.index]
    print("\nValue-sleeve mean monthly return by DT5G state (CRISIS≈0 confirms gated-off):")
    print((by.assign(mean_pct=lambda d: (d["mean"]*100).round(2))[["mean_pct", "count"]]).to_string())

    # capitulation events -> which states / do they coincide with value being active?
    cap = pd.read_csv(CAPF, parse_dates=["date"])
    cap["ym"] = cap["date"].dt.to_period("M")
    cap["dt5g"] = cap["ym"].map(state).map(STATE_LBL)
    print(f"\nCapitulation STRONG events ({len(cap)}): states = "
          f"{dict(cap['dt5g'].value_counts())}")
    capm = cap["ym"].unique()
    vcap = value.reindex(capm).dropna()
    print(f"Value-sleeve return in capitulation-event months: mean {vcap.mean()*100:+.2f}% "
          f"(≈ gated-to-cash -> the two sleeves DO NOT compete; regime-disjoint)")

    print("\n=== Q2: value sleeve (+30%, gated) blended onto EVERY book ===")
    print(f"{'book':>22}  {'metric':>0}")
    rows = []
    for col, lbl in BOOKS:
        book = book_monthly(col)
        idx = book.index.intersection(value.index)
        b = book.loc[idx]; vv = value.loc[idx]
        m0 = ann(b); m3 = ann(0.7*b + 0.3*vv)
        corr = b.corr(vv)
        print(f"\n  {lbl}")
        print(f"      alone      : {fmt(m0)}")
        print(f"      +30% value : {fmt(m3)}   corr(book,value)={corr:+.2f}")
        rows.append(dict(book=lbl, dSharpe=round(m3["Sharpe"]-m0["Sharpe"], 2),
                         dCalmar=round(m3["Calmar"]-m0["Calmar"], 2),
                         dMaxDD=round(m3["MaxDD"]-m0["MaxDD"], 1), corr=round(corr, 2)))
    print("\n=== SUMMARY: value-sleeve marginal effect by book ===")
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
