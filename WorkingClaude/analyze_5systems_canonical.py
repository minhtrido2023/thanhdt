#!/usr/bin/env python3
"""analyze_5systems_canonical.py — Primary report combining canonical 12y + 4 fresh-start variants.

Reads:
  - data/5sys_prodspec_201401_202605.csv   (canonical, 12y continuous)
  - data/5sys_prodspec_201801_202605.csv   (fresh 2018)
  - data/5sys_prodspec_202001_202605.csv   (fresh 2020)
  - data/5sys_prodspec_202201_202605.csv   (fresh 2022)
  - data/5sys_prodspec_202401_202605.csv   (fresh 2024)

Writes:
  - data/papertrade_canonical_2026-05.md
  - data/papertrade_canonical_metrics.csv
  - data/papertrade_canonical_curves.png
  - data/papertrade_canonical_drawdown.png

Convention (per user decision 2026-05-25):
  - Quote BOTH 12y-continuous CAGR AND fresh-start CAGR for any horizon
  - "Expected for new deployer" = fresh-start 2024-01 (most recent cold start)
  - Paper-trade 2026-04+ live = primary forward evidence (separate file)
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)

# ─── Load ────────────────────────────────────────────────────────────────────
SOURCES = {
    "12y_cont":   "data/5sys_prodspec_201401_202605.csv",
    "fresh_2018": "data/5sys_prodspec_201801_202605.csv",
    "fresh_2020": "data/5sys_prodspec_202001_202605.csv",
    "fresh_2022": "data/5sys_prodspec_202201_202605.csv",
    "fresh_2024": "data/5sys_prodspec_202401_202605.csv",
}
dfs = {tag: pd.read_csv(f, index_col=0, parse_dates=True) for tag, f in SOURCES.items()}
canon = dfs["12y_cont"]

SYSTEMS = ["V1_V11_TQ34b","V2_V12_TQ34b","V3_V12_LIVE","V4_V121_ENS_TQ34b","V5_V4_KellyQ2"]
SHORT   = ["V1 V11+TQ34b","V2 V12+TQ34b","V3 V12+LIVE","V4 V121_ENS","V5 V4+KellyQ2"]
COLORS  = ["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd"]

def metrics(nav, start=None, end=None):
    s = nav.dropna()
    if start is not None: s = s[s.index >= start]
    if end   is not None: s = s[s.index <= end]
    if len(s) < 30: return None
    rets = s.pct_change().dropna()
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    spy = len(rets) / yrs if yrs > 0 else 252
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1/yrs) - 1 if yrs > 0 else 0
    sh   = rets.mean()/rets.std()*np.sqrt(spy) if rets.std()>0 else 0
    neg  = rets[rets<0]
    sortino = rets.mean()/neg.std()*np.sqrt(spy) if len(neg)>0 and neg.std()>0 else 0
    dd   = ((s - s.cummax())/s.cummax()).min()
    cal  = cagr/abs(dd) if dd<0 else 0
    return {"CAGR":cagr*100,"Sharpe":sh,"Sortino":sortino,"DD":dd*100,"Calmar":cal,
            "Wealth":s.iloc[-1]/s.iloc[0],"Years":yrs}

# ─── 1. Headline FULL (12y cont) ─────────────────────────────────────────────
rows = []
for tag, df in dfs.items():
    for col, short in zip(SYSTEMS+["VNI"], SHORT+["VNI B&H"]):
        m = metrics(df[col])
        if not m: continue
        rows.append({"Source":tag,"System":short,**m})
m_df = pd.DataFrame(rows)
m_df.to_csv("data/papertrade_canonical_metrics.csv", index=False)

# ─── 2. New-deployer expected return = fresh_2024 (~2.4y) ────────────────────
new_deploy = m_df[m_df["Source"]=="fresh_2024"].copy()

# ─── 3. Equity curves + drawdown for 12y canonical ──────────────────────────
fig, ax = plt.subplots(figsize=(13, 7))
for col, short, c in zip(SYSTEMS, SHORT, COLORS):
    ax.plot(canon.index, canon[col], label=short, color=c, linewidth=1.3)
ax.plot(canon.index, canon["VNI"], label="VNI B&H", color="gray", linewidth=1.0, linestyle="--", alpha=0.7)
ax.set_yscale("log")
ax.set_title(f"Equity Curves — 5 Systems (prod spec, canonical 2014-01-02 → {canon.index.max().date()}, log scale)")
ax.set_ylabel("Wealth (NAV / init)"); ax.grid(True, alpha=0.3); ax.legend(loc="upper left", fontsize=9)
plt.tight_layout(); plt.savefig("data/papertrade_canonical_curves.png", dpi=120); plt.close()

fig, ax = plt.subplots(figsize=(13, 5))
for col, short, c in zip(SYSTEMS, SHORT, COLORS):
    s = canon[col].dropna()
    dd = (s - s.cummax())/s.cummax() * 100
    ax.plot(dd.index, dd, label=short, color=c, linewidth=1.0)
ax.fill_between(canon.index, -100, 0, color="red", alpha=0.03)
ax.set_title("Drawdown — 5 Systems (canonical 12y)"); ax.set_ylabel("Drawdown %"); ax.set_ylim(-50, 5)
ax.grid(True, alpha=0.3); ax.legend(loc="lower left", fontsize=9)
plt.tight_layout(); plt.savefig("data/papertrade_canonical_drawdown.png", dpi=120); plt.close()

# ─── 4. Markdown report ──────────────────────────────────────────────────────
md = []
md.append(f"# Paper-Trade 5 Systems — Canonical Backtest Report (prod spec)")
md.append("")
md.append(f"*Generated: {pd.Timestamp.now().date()}*  •  *Engine: run_5systems_prodspec.py + simulate_holistic_nav.py*  •  *Init NAV: 50B per system, prod spec (max_pos=12 + tier_weights 10% + t1_open + RE_BACKLOG + SV_TIGHT)*")
md.append("")
md.append("## TL;DR — expected return for new deployer (most relevant)")
md.append("")
md.append("If you deploy 50B fresh today, the *best historical proxy* is the fresh-start backtest from 2024-01-02 (most recent 2.37y cold-start). Numbers below are from that variant.")
md.append("")
md.append("| System | Expected CAGR (fresh 2024) | Sharpe | MaxDD | Wealth in 2.4y |")
md.append("|---|---:|---:|---:|---:|")
for _, r in new_deploy.iterrows():
    if "VNI" in r["System"]: continue
    md.append(f"| **{r['System']}** | **{r['CAGR']:+.2f}%** | {r['Sharpe']:+.2f} | {r['DD']:+.2f}% | {r['Wealth']:.2f}x |")
vni_row = new_deploy[new_deploy["System"]=="VNI B&H"]
if len(vni_row)>0:
    r = vni_row.iloc[0]
    md.append(f"| VNI B&H | {r['CAGR']:+.2f}% | {r['Sharpe']:+.2f} | {r['DD']:+.2f}% | {r['Wealth']:.2f}x |")
md.append("")
md.append("⚠ Real return ≈ backtest − 1.5pp/yr (slippage + tax + execution drag not modelled). So V5 realistic ≈ 35% CAGR; V1 ≈ 28%.")
md.append("")

md.append("## A. Headline — 12y continuous (canonical prod spec)")
md.append("")
md.append("Treats the backtest as if the system was running continuously since 2014-01-02. Compounds carryover positions; reflects MAX possible historical performance.")
md.append("")
md.append("| System | CAGR | Sharpe | Sortino | MaxDD | Calmar | Wealth (12.4y) |")
md.append("|---|---:|---:|---:|---:|---:|---:|")
for col, short in zip(SYSTEMS+["VNI"], SHORT+["VNI B&H"]):
    m = metrics(canon[col])
    if not m: continue
    md.append(f"| {short} | {m['CAGR']:+.2f}% | {m['Sharpe']:+.2f} | {m['Sortino']:+.2f} | {m['DD']:+.2f}% | {m['Calmar']:+.2f} | {m['Wealth']:.2f}x |")
md.append("")

md.append("## B. Period slices — 12y canonical")
md.append("")
SLICES = [
    ("OOS 2024-26", "2024-01-01", canon.index.max()),
    ("IS 2014-19",  "2014-01-01", "2019-12-31"),
    ("Mid 2018-23", "2018-01-01", "2023-12-31"),
    ("Bull 2020-21","2020-01-01", "2021-12-31"),
    ("Bear 2022",   "2022-01-01", "2022-12-31"),
    ("Y2025 bull",  "2025-01-01", "2025-12-31"),
    ("2026 YTD",    "2025-12-30", canon.index.max()),
]
for label, st, en in SLICES:
    md.append(f"### {label}")
    md.append("")
    md.append("| System | CAGR | Sharpe | MaxDD | Wealth |")
    md.append("|---|---:|---:|---:|---:|")
    for col, short in zip(SYSTEMS+["VNI"], SHORT+["VNI B&H"]):
        m = metrics(canon[col], pd.Timestamp(st), pd.Timestamp(en))
        if not m: continue
        md.append(f"| {short} | {m['CAGR']:+.2f}% | {m['Sharpe']:+.2f} | {m['DD']:+.2f}% | {m['Wealth']:.2f}x |")
    md.append("")

md.append("## C. Fresh-start variants — path-dependency robust")
md.append("")
md.append("Each row = restart sim with fresh 50B all-cash from that date. Different starts simulate *new deployer* at that moment.")
md.append("")
md.append("### C1. CAGR per system per start")
md.append("")
md.append("| Start | Years | V1 V11 | V2 V12 | V3 V12+LIVE | V4 V121_ENS | V5 V4+KellyQ2 | VNI |")
md.append("|---|---:|---:|---:|---:|---:|---:|---:|")
for tag in ["12y_cont","fresh_2018","fresh_2020","fresh_2022","fresh_2024"]:
    df = dfs[tag]
    yrs = (df.index.max() - df.index.min()).days/365.25
    row = [f"| {tag.replace('_','-')} | {yrs:.2f}"]
    for col in SYSTEMS+["VNI"]:
        m = metrics(df[col])
        row.append(f"{m['CAGR']:+.2f}%" if m else "-")
    md.append(" | ".join(row) + " |")
md.append("")

md.append("### C2. Sharpe per system per start")
md.append("")
md.append("| Start | V1 V11 | V2 V12 | V3 V12+LIVE | V4 V121_ENS | V5 V4+KellyQ2 | VNI |")
md.append("|---|---:|---:|---:|---:|---:|---:|")
for tag in ["12y_cont","fresh_2018","fresh_2020","fresh_2022","fresh_2024"]:
    df = dfs[tag]
    row = [f"| {tag.replace('_','-')}"]
    for col in SYSTEMS+["VNI"]:
        m = metrics(df[col])
        row.append(f"{m['Sharpe']:+.2f}" if m else "-")
    md.append(" | ".join(row) + " |")
md.append("")

md.append("### C3. MaxDD per system per start")
md.append("")
md.append("| Start | V1 V11 | V2 V12 | V3 V12+LIVE | V4 V121_ENS | V5 V4+KellyQ2 | VNI |")
md.append("|---|---:|---:|---:|---:|---:|---:|")
for tag in ["12y_cont","fresh_2018","fresh_2020","fresh_2022","fresh_2024"]:
    df = dfs[tag]
    row = [f"| {tag.replace('_','-')}"]
    for col in SYSTEMS+["VNI"]:
        m = metrics(df[col])
        row.append(f"{m['DD']:+.2f}%" if m else "-")
    md.append(" | ".join(row) + " |")
md.append("")

md.append("## D. Annual returns (12y canonical)")
md.append("")
md.append("| Year | V1 V11 | V2 V12 | V3 V12+LIVE | V4 V121_ENS | V5 V4+KellyQ2 | VNI |")
md.append("|---|---:|---:|---:|---:|---:|---:|")
for yr in range(2014, 2027):
    sy = pd.Timestamp(f"{yr}-01-01"); ey = pd.Timestamp(f"{yr}-12-31")
    row = [f"| {yr}"]
    for col in SYSTEMS+["VNI"]:
        s = canon[col][(canon.index>=sy) & (canon.index<=ey)].dropna()
        if len(s)<2: row.append("-"); continue
        r = (s.iloc[-1]/s.iloc[0]-1)*100
        row.append(f"{r:+.1f}%")
    md.append(" | ".join(row) + " |")
md.append("")

md.append("## E. Charts")
md.append("")
md.append("- 12y equity curves (log): `data/papertrade_canonical_curves.png`")
md.append("- 12y drawdown: `data/papertrade_canonical_drawdown.png`")
md.append("- Fresh-vs-canon overlay: `data/path_dependency_curves.png`")
md.append("")

md.append("## F. Critical caveats — read before interpreting any CAGR")
md.append("")
md.append("1. **Start-date sensitivity**: 5 systems × 4 fresh starts = 20 datapoints; mean ΔCAGR vs canonical = **+2.23pp**, std **2.76pp**. Fresh > canon in 17/20 (85%) of cases. Quoting 12y CAGR alone is misleading.")
md.append("2. **Look-ahead bias from artifacts**: `ba_v11_unified_12y_sig.pkl` (2026-05-20 vintage) bakes in current FA tier definitions, sector classifications, ticker_prune universe (survivorship), and SIGNAL_V10 logic — applied retroactively to 2014 data. True point-in-time replay would differ.")
md.append("3. **Tier evolution**: SV_TIGHT, P3 overheat, RE_BACKLOG_BUY, slot12 (max_pos=12), 10% fixed sizing — all deployed 2026-05. Pre-2026 reality used different rules.")
md.append("4. **No intraday HYBRID buy** (data unavailable pre-2024). Production gets +0.5pp Sharpe edge from this; backtest is conservative.")
md.append("5. **Real-world haircut**: subtract ~1.5pp/yr from backtest CAGR for slippage + tax + execution drag not modeled.")
md.append("6. **Paper-trade live (2026-04 onward) is the only zero-lookahead forward evidence**. After ~5 months: V5 = +5.11% (CAGR ann +46%, n=32 sessions, too noisy).")
md.append("")

md.append("## G. Recommended usage")
md.append("")
md.append("| Audience | Use this number |")
md.append("|---|---|")
md.append("| Long-term theoretical max (12y compound) | Section A — 12y canonical CAGR |")
md.append("| New deployer expected (next ~2-3 years) | Section TL;DR — fresh 2024-01 CAGR |")
md.append("| Forward-looking live evidence | Paper-trade 5-system live (data/papertrade_milestone_mid_*.md) |")
md.append("| Regime-conditional bet sizing | Section B — period slices |")
md.append("| Risk budgeting (drawdown reserve) | Section C3 — MaxDD across starts (worst case) |")
md.append("")

md.append("## H. Source artifacts")
md.append("")
md.append("- Engine: `run_5systems_prodspec.py` (canonical; env START_DATE/END_DATE)")
md.append("- Daily NAV CSVs: `data/5sys_prodspec_<start>_<end>.csv` (5 files)")
md.append("- Path-dep report: `data/path_dependency_report.md`")
md.append("- Path-dep gaps: `data/path_dependency_gaps.csv`")
md.append("- Metrics: `data/papertrade_canonical_metrics.csv`")
md.append("- Old simplified spec (deprecated): `run_full_5systems_2014_2026.py`")
md.append("")

with open("data/papertrade_canonical_2026-05.md","w",encoding="utf-8") as f:
    f.write("\n".join(md))

print(f"Wrote data/papertrade_canonical_2026-05.md ({len(md)} lines)")
print(f"Wrote data/papertrade_canonical_metrics.csv ({len(m_df)} rows)")
print(f"Wrote data/papertrade_canonical_curves.png")
print(f"Wrote data/papertrade_canonical_drawdown.png")

# Stdout summary
print("\n=== Headline 12y canonical ===")
for col, short in zip(SYSTEMS, SHORT):
    m = metrics(canon[col])
    print(f"  {short:<20} CAGR={m['CAGR']:+6.2f}%  Sharpe={m['Sharpe']:+.2f}  DD={m['DD']:+6.2f}%  Wealth={m['Wealth']:.2f}x")

print("\n=== Expected for new deployer (fresh 2024) ===")
fr24 = dfs["fresh_2024"]
for col, short in zip(SYSTEMS, SHORT):
    m = metrics(fr24[col])
    print(f"  {short:<20} CAGR={m['CAGR']:+6.2f}%  Sharpe={m['Sharpe']:+.2f}  DD={m['DD']:+6.2f}%")
