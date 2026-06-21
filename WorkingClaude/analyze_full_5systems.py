#!/usr/bin/env python3
"""analyze_full_5systems.py — full evaluation suite for 5 paper-trade systems on 2014-2026 backtest.

Reads: data/full_5systems_2014_2026.csv
Outputs:
  - data/papertrade_full_2014_2026.md       (markdown report)
  - data/papertrade_full_2014_2026_metrics.csv  (per-system x period metric table)
  - data/papertrade_full_2014_2026_curves.png   (equity curves)
  - data/papertrade_full_2014_2026_drawdown.png (drawdown curves)
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)

df = pd.read_csv("data/full_5systems_2014_2026.csv", index_col=0, parse_dates=True)
SYSTEMS = ["V1_V11_TQ34b","V2_V12_TQ34b","V3_V12_LIVE","V4_V121_ENS_TQ34b","V5_V4_KellyQ2"]
SHORT   = ["V1 V11+TQ34b","V2 V12+TQ34b","V3 V12+LIVE","V4 V121_ENS","V5 V4+KellyQ2"]
COLORS  = ["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd"]

def metrics(nav, start, end):
    s = nav[(nav.index>=start) & (nav.index<=end)].dropna()
    if len(s)<30: return None
    rets = s.pct_change().dropna()
    yrs = (s.index[-1]-s.index[0]).days/365.25
    spy = len(rets)/yrs if yrs>0 else 252
    cagr = (s.iloc[-1]/s.iloc[0])**(1/yrs)-1 if yrs>0 else 0
    sh   = rets.mean()/rets.std()*np.sqrt(spy) if rets.std()>0 else 0
    neg  = rets[rets<0]
    sortino = rets.mean()/neg.std()*np.sqrt(spy) if len(neg)>0 and neg.std()>0 else 0
    dd   = ((s-s.cummax())/s.cummax()).min()
    cal  = cagr/abs(dd) if dd<0 else 0
    return {"CAGR":cagr*100,"Sharpe":sh,"Sortino":sortino,"DD":dd*100,"Calmar":cal,
            "Wealth":s.iloc[-1]/s.iloc[0],"TotRet":(s.iloc[-1]/s.iloc[0]-1)*100}

# ─── 1. Headline (FULL + OOS + walk-forward windows) ────────────────────────
periods = [
    ("FULL 2014-26",     df.index.min(),                df.index.max()),
    ("OOS 2024-26",      pd.Timestamp("2024-01-01"),    df.index.max()),
    ("IS 2014-19",       pd.Timestamp("2014-01-01"),    pd.Timestamp("2019-12-31")),
    ("Mid 2018-23",      pd.Timestamp("2018-01-01"),    pd.Timestamp("2023-12-31")),
    ("Bull 2020-21",     pd.Timestamp("2020-01-01"),    pd.Timestamp("2021-12-31")),
    ("Bear 2022",        pd.Timestamp("2022-01-01"),    pd.Timestamp("2022-12-31")),
    ("Recovery 2023",    pd.Timestamp("2023-01-01"),    pd.Timestamp("2023-12-31")),
    ("Y2024",            pd.Timestamp("2024-01-01"),    pd.Timestamp("2024-12-31")),
    ("Y2025",            pd.Timestamp("2025-01-01"),    pd.Timestamp("2025-12-31")),
    ("2026 YTD",         pd.Timestamp("2025-12-30"),    df.index.max()),
]

rows = []
for label, st, en in periods:
    for col, short in zip(SYSTEMS+["VNI"], SHORT+["VNI B&H"]):
        m = metrics(df[col], st, en)
        if not m: continue
        rows.append({"Period":label,"System":short,**m})
m_df = pd.DataFrame(rows)
m_df.to_csv("data/papertrade_full_2014_2026_metrics.csv", index=False)

# ─── 2. Annual breakdown ────────────────────────────────────────────────────
ann_rows = []
for yr in range(2014, 2027):
    sy = pd.Timestamp(f"{yr}-01-01"); ey = pd.Timestamp(f"{yr}-12-31")
    row = {"Year":yr}
    for col, short in zip(SYSTEMS+["VNI"], SHORT+["VNI B&H"]):
        s = df[col][(df.index>=sy) & (df.index<=ey)].dropna()
        if len(s)<2: row[short] = np.nan; continue
        row[short] = (s.iloc[-1]/s.iloc[0]-1)*100
    ann_rows.append(row)
ann_df = pd.DataFrame(ann_rows)

# ─── 3. State-conditional returns (using TQ34b state) ───────────────────────
sc_rows = []
state_col = "state_tq34b"
if state_col in df.columns:
    st_series = df[state_col].ffill()
    for s in [1,2,3,4,5]:
        mask = (st_series==s)
        days = mask.sum()
        if days < 10: continue
        for col, short in zip(SYSTEMS+["VNI"], SHORT+["VNI B&H"]):
            rets = df[col].pct_change()
            r_in_state = rets[mask].dropna()
            if len(r_in_state) < 5: continue
            mean_d = r_in_state.mean()
            ann   = mean_d * 252 * 100
            hit   = (r_in_state>0).mean()*100
            sc_rows.append({"State":s,"Days":days,"System":short,"AnnRet%":ann,"DailyMean%":mean_d*100,"HitRate%":hit})
sc_df = pd.DataFrame(sc_rows)

# ─── 4. Equity curves PNG ───────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(13, 7))
for col, short, c in zip(SYSTEMS, SHORT, COLORS):
    ax.plot(df.index, df[col], label=short, color=c, linewidth=1.3)
ax.plot(df.index, df["VNI"], label="VNI B&H", color="gray", linewidth=1.0, linestyle="--", alpha=0.7)
ax.set_yscale("log")
ax.set_title("Equity Curves — 5 Systems, 2014-01-01 → 2026-05-15 (log scale, init=1.0)")
ax.set_ylabel("Wealth (NAV / init)")
ax.grid(True, alpha=0.3); ax.legend(loc="upper left", fontsize=9)
plt.tight_layout()
plt.savefig("data/papertrade_full_2014_2026_curves.png", dpi=120)
plt.close()

# ─── 5. Drawdown curves PNG ─────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(13, 5))
for col, short, c in zip(SYSTEMS, SHORT, COLORS):
    s = df[col].dropna()
    dd = (s - s.cummax())/s.cummax() * 100
    ax.plot(dd.index, dd, label=short, color=c, linewidth=1.0)
ax.fill_between(df.index, -100, 0, color="red", alpha=0.03)
ax.set_title("Drawdown — 5 Systems")
ax.set_ylabel("Drawdown %"); ax.set_ylim(-50, 5)
ax.grid(True, alpha=0.3); ax.legend(loc="lower left", fontsize=9)
plt.tight_layout()
plt.savefig("data/papertrade_full_2014_2026_drawdown.png", dpi=120)
plt.close()

# ─── 6. Markdown report ─────────────────────────────────────────────────────
md = []
md.append(f"# Paper-Trade 5 Systems — Full Backtest 2014-01-01 → {df.index.max().date()}")
md.append("")
md.append(f"*Generated: {pd.Timestamp.now().date()}*  •  *Init NAV: 50B per system*  •  *Engine: simulate_holistic_nav.simulate + LAGGED book + ensemble routing*")
md.append("")
md.append("## Systems")
md.append("")
md.append("| Tag | Name | Composition | State | ETF{state:frac} |")
md.append("|---|---|---|---|---|")
md.append("| V1 | V11 'Song Sinh'      | BAL (BA v11) + VN30 (BA on top-30)        | TQ34b | {3:0.7} |")
md.append("| V2 | V12 'Am Duong'       | BAL + LAGGED_v12 (HL_3y, fixed 8%)        | TQ34b | {3:0.7} |")
md.append("| V3 | V12 + LIVE Tinh Te   | BAL + LAGGED_v12                          | LIVE  | {3:0.7} |")
md.append("| V4 | V12.1 Ensemble       | BAL + ensemble{VN30 \| LAGGED_v121 S2}    | TQ34b | {3:0.7} |")
md.append("| V5 | V4 + Kelly Q2        | V4 with NEUTRAL ETF parking 100%          | TQ34b | {3:1.0} |")
md.append("")
md.append("Ensemble signal: M1 (concentration) + M3r (rolling Top10 ADV momentum), AND-HOLD logic. M1==M3r flip set leg; otherwise keep last.")
md.append("")

md.append("## A. Headline metrics by period")
md.append("")
for label, st, en in periods:
    md.append(f"### {label}")
    md.append("")
    md.append("| System | CAGR | Sharpe | Sortino | MaxDD | Calmar | Wealth |")
    md.append("|---|---:|---:|---:|---:|---:|---:|")
    for col, short in zip(SYSTEMS+["VNI"], SHORT+["VNI B&H"]):
        m = metrics(df[col], st, en)
        if not m: continue
        md.append(f"| {short} | {m['CAGR']:+.2f}% | {m['Sharpe']:+.2f} | {m['Sortino']:+.2f} | {m['DD']:+.2f}% | {m['Calmar']:+.2f} | {m['Wealth']:.2f}x |")
    md.append("")

md.append("## B. Annual returns (calendar years)")
md.append("")
md.append("| Year | " + " | ".join(SHORT+["VNI B&H"]) + " |")
md.append("|---|" + "|".join(["---:"]*(len(SHORT)+1)) + "|")
for _, row in ann_df.iterrows():
    md.append(f"| {int(row['Year'])} | " + " | ".join(
        ("-" if pd.isna(row[c]) else f"{row[c]:+.1f}%") for c in SHORT+["VNI B&H"]) + " |")
md.append("")

if len(sc_df)>0:
    md.append("## C. State-conditional annualised return (TQ34b state, daily-mean * 252)")
    md.append("")
    md.append("State 1=CRISIS, 2=BEAR, 3=NEUTRAL, 4=BULL, 5=EX-BULL.")
    md.append("")
    pivot = sc_df.pivot_table(index="System", columns="State", values="AnnRet%")
    pivot = pivot.reindex(SHORT+["VNI B&H"])
    md.append("| System | " + " | ".join(f"State {s}" for s in sorted(sc_df['State'].unique())) + " |")
    md.append("|---|" + "|".join(["---:"]*len(sorted(sc_df['State'].unique()))) + "|")
    for sys_name in pivot.index:
        if sys_name not in pivot.index: continue
        cells = []
        for s in sorted(sc_df['State'].unique()):
            v = pivot.loc[sys_name, s] if s in pivot.columns else np.nan
            cells.append("-" if pd.isna(v) else f"{v:+.1f}%")
        md.append(f"| {sys_name} | " + " | ".join(cells) + " |")
    days_row = sc_df[sc_df['System']==SHORT[0]].set_index('State')['Days'] if SHORT[0] in sc_df['System'].values else pd.Series()
    if len(days_row)>0:
        md.append("")
        md.append("Days in each state: " + ", ".join(f"S{s}={int(days_row[s])}d" for s in sorted(days_row.index)))
    md.append("")

md.append("## D. V5 (Kelly Q2) vs V4 (baseline ensemble) — overlay validation")
md.append("")
md.append("| Period | ΔCAGR | ΔSharpe | ΔDD | ΔCalmar | ΔWealth |")
md.append("|---|---:|---:|---:|---:|---:|")
for label, st, en in periods[:4]:
    m4 = metrics(df["V4_V121_ENS_TQ34b"], st, en)
    m5 = metrics(df["V5_V4_KellyQ2"], st, en)
    if not m4 or not m5: continue
    md.append(f"| {label} | {m5['CAGR']-m4['CAGR']:+.2f}pp | {m5['Sharpe']-m4['Sharpe']:+.2f} | {m5['DD']-m4['DD']:+.2f}pp | {m5['Calmar']-m4['Calmar']:+.2f} | {m5['Wealth']-m4['Wealth']:+.2f}x |")
md.append("")

md.append("## E. Charts")
md.append("")
md.append("- Equity curves (log): `data/papertrade_full_2014_2026_curves.png`")
md.append("- Drawdown: `data/papertrade_full_2014_2026_drawdown.png`")
md.append("")

md.append("## F. Source artifacts")
md.append("")
md.append("- Daily NAV CSV: `data/full_5systems_2014_2026.csv` (columns: V1-V5 NAV + VNI + ensemble signal + states)")
md.append("- Metrics CSV: `data/papertrade_full_2014_2026_metrics.csv`")
md.append("- Run log: `data/full_5systems_run.log`")
md.append("- Backtest engine: `simulate_holistic_nav.py` (canonical T+1 open exec, slippage 0.1% in / 0.15% out, tax 0.1%, ETF friction 0.15%, borrow 10%/yr, deposit 0%/yr)")
md.append("- Builder script: `run_full_5systems_2014_2026.py`")
md.append("")

md.append("## G. Caveats")
md.append("")
md.append("1. **End date 2026-05-15**: signal pickle ba_v11_unified_12y_sig.pkl was generated up to that date. Live data extends to 2026-05-20.")
md.append("2. **V1 ≡ V4 in early years if ensemble doesn't flip**: M1+M3r AND-HOLD signal needs ≥252 days history → first flip not until late 2014/early 2015.")
md.append("3. **LAGGED book uses earnings_px / earnings_surprise_data pickles**: vintage 2026-05-20.")
md.append("4. **All numbers backtested with knowledge of FA tier definitions, sector caps, overheat rules as they exist 2026-05-24** — no point-in-time fundamentals timeline for tier classification (well-known limitation).")
md.append("")

with open("data/papertrade_full_2014_2026.md","w",encoding="utf-8") as f:
    f.write("\n".join(md))

print(f"Wrote data/papertrade_full_2014_2026.md ({len(md)} lines)")
print(f"Wrote data/papertrade_full_2014_2026_metrics.csv ({len(m_df)} rows)")
print(f"Wrote data/papertrade_full_2014_2026_curves.png")
print(f"Wrote data/papertrade_full_2014_2026_drawdown.png")

# Echo headline to stdout for quick review
print("\n--- HEADLINE FULL 2014-26 ---")
for col, short in zip(SYSTEMS+["VNI"], SHORT+["VNI B&H"]):
    m = metrics(df[col], df.index.min(), df.index.max())
    if m: print(f"  {short:<20} CAGR={m['CAGR']:+6.2f}%  Sharpe={m['Sharpe']:+.2f}  DD={m['DD']:+6.2f}%  Wealth={m['Wealth']:.2f}x")

print("\n--- OOS 2024-26 ---")
for col, short in zip(SYSTEMS+["VNI"], SHORT+["VNI B&H"]):
    m = metrics(df[col], pd.Timestamp("2024-01-01"), df.index.max())
    if m: print(f"  {short:<20} CAGR={m['CAGR']:+6.2f}%  Sharpe={m['Sharpe']:+.2f}  DD={m['DD']:+6.2f}%  Wealth={m['Wealth']:.2f}x")
