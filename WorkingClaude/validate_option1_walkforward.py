#!/usr/bin/env python3
"""
validate_option1_walkforward.py — Walk-forward validation Option 1

Uses pre-computed NAVs from option1_bal_lagged_vs_prod.csv.
Multiple split windows + annual breakdown.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)

print("="*100)
print("  WALK-FORWARD VALIDATION — Option 1 (BAL+LAGGED+ETF) vs Current (BAL+VN30+ETF)")
print("="*100)

df = pd.read_csv("data/option1_bal_lagged_vs_prod.csv", index_col=0, parse_dates=True)
df.columns = ["Current", "Opt1"]
print(f"NAVs loaded: {len(df)} days  ({df.index.min().date()} → {df.index.max().date()})")
print(f"  Current final: {df['Current'].iloc[-1]:.3f}x")
print(f"  Opt1 final:    {df['Opt1'].iloc[-1]:.3f}x")

# VNI
vni = pd.read_csv("data/VNINDEX.csv", parse_dates=["time"])
vni_n = vni.set_index("time")["Close"].reindex(df.index).ffill()
vni_n = vni_n / vni_n.iloc[0]

def metrics(nav, start, end):
    s = nav[(nav.index >= start) & (nav.index <= end)]
    if len(s) < 30: return None
    rets = s.pct_change().dropna()
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    spy = len(rets)/yrs if yrs>0 else 252
    cagr = (s.iloc[-1]/s.iloc[0])**(1/yrs) - 1 if yrs>0 else 0
    sh = rets.mean()/rets.std()*np.sqrt(spy) if rets.std()>0 else 0
    dd = ((s - s.cummax())/s.cummax()).min()
    cal = cagr/abs(dd) if dd<0 else 0
    return {"CAGR":cagr*100,"Sharpe":sh,"DD":dd*100,"Calmar":cal,"wealth":s.iloc[-1]/s.iloc[0]}

# ─── Walk-forward windows ────────────────────────────────────────────────
print("\n" + "="*100)
print("  WALK-FORWARD WINDOWS (Current → Opt1)")
print("="*100)
windows = [
    ("FULL_14-26",       df.index.min(), df.index.max()),
    ("P1_IS_14-18",      pd.Timestamp("2014-01-01"), pd.Timestamp("2018-12-31")),
    ("P2_OOS_19-26",     pd.Timestamp("2019-01-01"), df.index.max()),
    ("P3_IS_14-20",      pd.Timestamp("2014-01-01"), pd.Timestamp("2020-12-31")),
    ("P4_OOS_21-26",     pd.Timestamp("2021-01-01"), df.index.max()),
    ("P5_IS_14-22",      pd.Timestamp("2014-01-01"), pd.Timestamp("2022-12-31")),
    ("P6_OOS_23-26",     pd.Timestamp("2023-01-01"), df.index.max()),
]
print(f"\n  {'Window':<18}{'Current CAGR':>14}{'Opt1 CAGR':>13}{'Δ':>8}{'Cur Sh':>10}{'Opt1 Sh':>10}{'Δ Sh':>8}{'Cur DD':>10}{'Opt1 DD':>10}{'Δ DD':>8}")
print("  " + "-"*120)
for wn, sw, ew in windows:
    c = metrics(df["Current"], sw, ew); o = metrics(df["Opt1"], sw, ew)
    if c is None or o is None: continue
    print(f"  {wn:<18}{c['CAGR']:>+13.2f}%{o['CAGR']:>+12.2f}%{o['CAGR']-c['CAGR']:>+7.2f}"
          f"{c['Sharpe']:>+10.2f}{o['Sharpe']:>+10.2f}{o['Sharpe']-c['Sharpe']:>+8.2f}"
          f"{c['DD']:>+9.2f}%{o['DD']:>+9.2f}%{o['DD']-c['DD']:>+7.2f}")

# IS vs OOS deltas
print(f"\n  IS-vs-OOS sanity check:")
splits = [
    ("18/19", "P1_IS_14-18", "P2_OOS_19-26"),
    ("20/21", "P3_IS_14-20", "P4_OOS_21-26"),
    ("22/23", "P5_IS_14-22", "P6_OOS_23-26"),
]
for nm, isn, oosn in splits:
    is_w = [w for w in windows if w[0] == isn][0]
    oos_w = [w for w in windows if w[0] == oosn][0]
    is_o = metrics(df["Opt1"], is_w[1], is_w[2])
    oos_o = metrics(df["Opt1"], oos_w[1], oos_w[2])
    is_c = metrics(df["Current"], is_w[1], is_w[2])
    oos_c = metrics(df["Current"], oos_w[1], oos_w[2])
    print(f"    {nm}: Opt1 IS={is_o['CAGR']:+.2f}% → OOS={oos_o['CAGR']:+.2f}%  Δ={oos_o['CAGR']-is_o['CAGR']:+.2f}pp")
    print(f"        Cur  IS={is_c['CAGR']:+.2f}% → OOS={oos_c['CAGR']:+.2f}%  Δ={oos_c['CAGR']-is_c['CAGR']:+.2f}pp")

# ─── Annual breakdown ────────────────────────────────────────────────────
print("\n" + "="*100)
print("  ANNUAL CAGR (Current vs Opt1)")
print("="*100)
print(f"  {'Year':<6}{'Current%':>11}{'Opt1%':>11}{'Δ':>8}{'Cur Sh':>10}{'Opt1 Sh':>10}{'VNI%':>10}")
print("  " + "-"*70)
annual = []
for yr in range(2014, 2026):
    sw = pd.Timestamp(f"{yr}-01-01"); ew = pd.Timestamp(f"{yr}-12-31")
    c = metrics(df["Current"], sw, ew); o = metrics(df["Opt1"], sw, ew)
    v = metrics(vni_n, sw, ew)
    if c is None or o is None: continue
    delta = o["CAGR"] - c["CAGR"]
    vc = v["CAGR"] if v else 0
    annual.append({"year":yr, "Cur":c["CAGR"], "Opt1":o["CAGR"], "delta":delta})
    print(f"  {yr:<6}{c['CAGR']:>+10.2f}%{o['CAGR']:>+10.2f}%{delta:>+7.2f}{c['Sharpe']:>+10.2f}{o['Sharpe']:>+10.2f}{vc:>+9.2f}%")

an_df = pd.DataFrame(annual)
print(f"\n  Years Opt1 beats Current: {(an_df['delta']>0).sum()}/{len(an_df)}")
print(f"  Avg Δ: {an_df['delta'].mean():+.2f}pp  | Median: {an_df['delta'].median():+.2f}pp")
print(f"  Worst Δ year: {an_df.loc[an_df['delta'].idxmin(),'year']} ({an_df['delta'].min():+.2f}pp)")
print(f"  Best Δ year:  {an_df.loc[an_df['delta'].idxmax(),'year']} ({an_df['delta'].max():+.2f}pp)")

# ─── Rolling 3-year metrics ──────────────────────────────────────────────
print("\n" + "="*100)
print("  ROLLING 3-YEAR WINDOWS (CAGR + Sharpe)")
print("="*100)
rolling_results = []
for start_y in range(2014, 2024):
    sw = pd.Timestamp(f"{start_y}-01-01"); ew = pd.Timestamp(f"{start_y+2}-12-31")
    c = metrics(df["Current"], sw, ew); o = metrics(df["Opt1"], sw, ew)
    if c is None or o is None: continue
    rolling_results.append({"window":f"{start_y}-{start_y+2}",
                            "Cur_CAGR":c["CAGR"], "Opt1_CAGR":o["CAGR"],
                            "Cur_Sh":c["Sharpe"], "Opt1_Sh":o["Sharpe"],
                            "Cur_DD":c["DD"], "Opt1_DD":o["DD"]})
roll_df = pd.DataFrame(rolling_results)
print(f"\n  {'Window':<12}{'Cur CAGR':>10}{'Opt1 CAGR':>11}{'Δ':>8}{'Cur Sh':>9}{'Opt1 Sh':>10}{'Δ Sh':>8}{'Cur DD':>10}{'Opt1 DD':>10}")
for _, r in roll_df.iterrows():
    d_cagr = r['Opt1_CAGR'] - r['Cur_CAGR']
    d_sh = r['Opt1_Sh'] - r['Cur_Sh']
    print(f"  {r['window']:<12}{r['Cur_CAGR']:>+9.2f}%{r['Opt1_CAGR']:>+10.2f}%{d_cagr:>+7.2f}{r['Cur_Sh']:>+9.2f}{r['Opt1_Sh']:>+10.2f}{d_sh:>+8.2f}{r['Cur_DD']:>+9.2f}%{r['Opt1_DD']:>+9.2f}%")

print(f"\n  Opt1 beats Cur on CAGR: {(roll_df['Opt1_CAGR']>roll_df['Cur_CAGR']).sum()}/{len(roll_df)}")
print(f"  Opt1 beats Cur on Sharpe: {(roll_df['Opt1_Sh']>roll_df['Cur_Sh']).sum()}/{len(roll_df)}")

print("\nSaved: validate_option1_walkforward.csv")
roll_df.to_csv("data/validate_option1_walkforward.csv", index=False)
