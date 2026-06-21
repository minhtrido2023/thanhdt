"""
value_quality_gate_test.py
Test quality gate trên value book (PB+PE composite) + kết luận Option A capital structure.

So sánh 6 variants:
  V0 : no gate (baseline)
  V1 : ROIC5Y >= 8%
  V2 : FSCORE >= 5
  V3 : ROE_Min5Y >= 10%
  V4 : ROIC5Y >= 8% + FSCORE >= 5  (combined light)
  V5 : ROIC5Y >= 10% + FSCORE >= 6  (strict quality)

Sau đó: Option A = blend winner (30%) vào V5 proxy (V2.2 momentum).
"""
import sys, os
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
import subprocess
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from io import StringIO
import warnings; warnings.filterwarnings('ignore')

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
PROJECT = "lithe-record-440915-m9"
BQ_PATH = r"bq"
os.chdir(WORKDIR)

PANELF = WORKDIR + r"\data\edge_panel.csv"
NAVF   = WORKDIR + r"\data\5sys_prodspec_201401_202605_dt5g_realetf.csv"

LIQ_FLOOR = 1e10        # 10B/day
NAME_CAP  = 0.08        # max 8% per name
QTILE     = 0.20        # top quintile
TC        = 0.003       # 0.30% round-trip
STATE_W   = {1:0.0, 2:0.2, 3:0.7, 4:1.0, 5:1.3}

STATE_NAMES = {1:'CRISIS',2:'BEAR',3:'NEUTRAL',4:'BULL',5:'EX-BULL'}
STATE_COLORS= {1:'#d62728',2:'#ff7f0e',3:'#7fafcf',4:'#2ca02c',5:'#9467bd'}

def bq(sql):
    cmd = (f'"{BQ_PATH}" query --use_legacy_sql=false'
           f' --project_id={PROJECT} --format=csv --quiet --max_rows=100000')
    r = subprocess.run(cmd, input=sql, capture_output=True,
                       text=True, encoding='utf-8', shell=True)
    return pd.read_csv(StringIO(r.stdout)) if r.returncode == 0 else pd.DataFrame()

def ann(ret):
    ret = ret.dropna(); n = len(ret)
    if n < 3: return dict(CAGR=np.nan, Sharpe=np.nan, MaxDD=np.nan,
                          Calmar=np.nan, Sortino=np.nan)
    mu = ret.mean()*12; sd = ret.std(ddof=1)*np.sqrt(12)
    dn = ret[ret<0].std(ddof=1)*np.sqrt(12)
    cagr = (1+ret).prod()**(12/n)-1
    nav = (1+ret).cumprod(); dd = (nav/nav.cummax()-1).min()
    return dict(CAGR=cagr*100, Sharpe=mu/sd if sd>0 else 0,
                Sortino=mu/dn if dn>0 else 0,
                MaxDD=dd*100, Calmar=cagr/abs(dd) if dd<0 else np.nan)

def sub(r, lo, hi):
    return r[(r.index>=pd.Period(lo))&(r.index<=pd.Period(hi))]

# ════════════════════════════════════════════════════════════
# BUILD VALUE BOOK WITH QUALITY GATE
# ════════════════════════════════════════════════════════════
def build_value_book(df, quality_fn=None, label=""):
    """
    df: edge_panel with ym, ticker, PB, PE, liq, fwd_1m, state, + quality cols
    quality_fn: lambda row -> bool (pre-filter before ranking)
    Returns monthly Series of gated, TC-adjusted returns.
    """
    rets = {}; prev_w = None; sizes = []
    for ym, g in df.groupby("ym"):
        s = g[["ticker","PB","PE","liq","fwd_1m","state",
               "ROIC5Y","FSCORE","ROE_Min5Y"]].dropna(
                   subset=["PB","PE","fwd_1m","liq"])
        s = s[s["liq"] >= LIQ_FLOOR].copy()
        # apply quality gate
        if quality_fn is not None:
            s = s[s.apply(quality_fn, axis=1)]
        if len(s) < 8:          # need at least 8 names to form a portfolio
            sizes.append(0); continue
        s["vscore"] = s["PB"].rank(pct=True) + s["PE"].rank(pct=True)
        k = max(5, int(len(s)*QTILE))
        picks = s.nsmallest(k, "vscore").copy()
        # liq-weighted, name cap
        w = np.minimum(picks["liq"], picks["liq"].quantile(0.9))
        w = w/w.sum()
        w = np.minimum(w, NAME_CAP); w = w/w.sum()
        wser = pd.Series(w.values, index=picks["ticker"].values)
        raw  = float((w.values * picks["fwd_1m"].values).sum())
        # turnover TC
        if prev_w is None:
            turn = 1.0
        else:
            alln = wser.index.union(prev_w.index)
            turn = (wser.reindex(alln,fill_value=0)
                    - prev_w.reindex(alln,fill_value=0)).abs().sum()
        prev_w = wser
        gate = STATE_W.get(int(picks["state"].iloc[0]), 0.7)
        rets[ym] = gate*raw - TC*turn*gate
        sizes.append(len(picks))
    ser = pd.Series(rets).sort_index()
    avg_sz = np.mean(sizes) if sizes else 0
    return ser, avg_sz

# ════════════════════════════════════════════════════════════
# LOAD DATA
# ════════════════════════════════════════════════════════════
print("Loading edge panel...")
panel = pd.read_csv(PANELF, parse_dates=["time"])
panel = panel[panel["fwd_1m"].notna()].copy()
panel["ym"] = panel["time"].dt.to_period("M")

# Monthly state from DT5G
raw_st = bq("""
    SELECT s.time, s.state
    FROM tav2_bq.vnindex_5state_dt5g_live AS s ORDER BY s.time
""")
raw_st["time"] = pd.to_datetime(raw_st["time"])
raw_st = raw_st.set_index("time")["state"].astype(int)
mo_state = raw_st.resample("ME").apply(lambda x: int(x.mode()[0]))
mo_state.index = mo_state.index.to_period("M")
panel["state"] = panel["ym"].map(mo_state).fillna(3).astype(int)

print(f"  Panel: {len(panel):,} obs, {panel['ym'].nunique()} months, "
      f"{panel['ticker'].nunique()} tickers")

# Momentum book (V5)
nav = pd.read_csv(NAVF, parse_dates=["time"]).set_index("time")
M_d = nav["V5_V4_KellyQ2"].resample("ME").last().pct_change()
M_d.index = M_d.index.to_period("M")
M = M_d.dropna()

# ════════════════════════════════════════════════════════════
# BUILD ALL VARIANTS
# ════════════════════════════════════════════════════════════
print("\nBuilding value book variants...")
variants = {
    "V0 no gate":                  (None,
        "PB+PE cheapest, no quality filter"),
    "V1 ROIC>=8%":                 (lambda r: r["ROIC5Y"]>=0.08,
        "ROIC5Y >= 8%"),
    "V2 FSCORE>=5":                (lambda r: r["FSCORE"]>=5,
        "Piotroski FSCORE >= 5"),
    "V3 ROE_Min>=10%":             (lambda r: r["ROE_Min5Y"]>=0.10,
        "ROE_Min5Y >= 10%"),
    "V4 ROIC>=8%+FSCORE>=5":       (lambda r: (r["ROIC5Y"]>=0.08) & (r["FSCORE"]>=5),
        "ROIC5Y>=8% AND FSCORE>=5"),
    "V5 ROIC>=10%+FSCORE>=6":      (lambda r: (r["ROIC5Y"]>=0.10) & (r["FSCORE"]>=6),
        "ROIC5Y>=10% AND FSCORE>=6 (strict)"),
}

books = {}
for name, (fn, desc) in variants.items():
    ser, sz = build_value_book(panel, fn, name)
    books[name] = (ser, sz)
    m = ann(ser)
    print(f"  {name:28s}  avg_names={sz:4.1f}  "
          f"CAGR {m['CAGR']:5.1f}%  Sh {m['Sharpe']:.2f}  "
          f"MaxDD {m['MaxDD']:5.1f}%  Cal {m['Calmar']:.2f}")

# ════════════════════════════════════════════════════════════
# DETAILED COMPARISON
# ════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("FULL PERIOD + IS/OOS + GRIND")
print("="*70)

GRIND = ("2025-09", "2026-03")

print(f"\n{'Variant':28s}  {'Full Cal':>9s}  {'IS Cal':>8s}  {'OOS Cal':>8s}  "
      f"{'Grind%':>8s}  {'MaxDD':>7s}  {'Sh':>5s}")
print("-"*78)
for name, (ser, sz) in books.items():
    idx_ = M.index.intersection(ser.index)
    s_ = ser.loc[idx_]
    mf = ann(s_)
    mi = ann(sub(s_,'2014-01','2019-12'))
    mo = ann(sub(s_,'2020-01','2026-12'))
    g  = sub(s_, *GRIND)
    gc = ((1+g).prod()-1)*100 if len(g)>0 else np.nan
    print(f"{name:28s}  {mf['Calmar']:>8.2f}  {mi['Calmar']:>7.2f}  "
          f"{mo['Calmar']:>7.2f}  {gc:>7.1f}%  "
          f"{mf['MaxDD']:>6.1f}%  {mf['Sharpe']:>5.2f}")

# ── Compare by state ─────────────────────────────────────────
print("\n" + "="*70)
print("MEAN MONTHLY RETURN BY DT5G STATE")
print("="*70)
state_ser = mo_state.copy()
print(f"\n{'Variant':28s}", end="")
for s in [1,2,3,4,5]:
    print(f"  {STATE_NAMES[s]:>8s}", end="")
print()
print("-"*70)
for name, (ser, sz) in books.items():
    print(f"{name:28s}", end="")
    for s in [1,2,3,4,5]:
        mask = state_ser.reindex(ser.index) == s
        vals = ser[mask]
        print(f"  {vals.mean()*100:+7.1f}%" if len(vals)>0 else f"  {'n/a':>8s}", end="")
    print()

# ── Value vs momentum gap by variant ─────────────────────────
print("\n" + "="*70)
print("VALUE-MOMENTUM GAP (avg/month full period)")
print("="*70)
for name, (ser, sz) in books.items():
    idx_ = M.index.intersection(ser.index)
    gap = (ser.loc[idx_] - M.loc[idx_]).mean()*100
    corr = ser.loc[idx_].corr(M.loc[idx_])
    print(f"  {name:28s}  gap={gap:+.2f}%/mo  corr={corr:.3f}")

# ── Annual returns ────────────────────────────────────────────
print("\n" + "="*70)
print("ANNUAL RETURNS BY VARIANT")
print("="*70)
print(f"\n{'Year':6s}  {'Momentum':>9s}", end="")
for name in books: print(f"  {name[:12]:>12s}", end="")
print()
print("-"*100)
for yr in range(2014,2027):
    sm = sub(M,f'{yr}-01',f'{yr}-12')
    if len(sm)<6: continue
    rm = ((1+sm).prod()-1)*100
    print(f"{yr}    {rm:>8.1f}%", end="")
    for name,(ser,_) in books.items():
        sv = sub(ser,f'{yr}-01',f'{yr}-12')
        rv = ((1+sv).prod()-1)*100 if len(sv)>=6 else np.nan
        mark = "*" if (not np.isnan(rv) and rv>rm) else " "
        print(f"  {rv:>10.1f}%{mark}", end="")
    print()
print("  (* = value beats momentum that year)")

# ════════════════════════════════════════════════════════════
# OPTION A: BLEND WINNER (30%) INTO V2.2 MOMENTUM
# ════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("OPTION A: V2.2 + VALUE 30% (choose best quality-gate variant)")
print("Option A capital: BAL 17.5B + LAG 17.5B + VALUE 15B = 50B total")
print("="*70)

W_VAL = 0.30
print(f"\n{'Strategy':32s}  {'CAGR':>7s}  {'Sh':>5s}  {'MaxDD':>7s}  {'Cal':>6s}  "
      f"{'OOS Cal':>8s}  {'Grind':>7s}  {'vs pure':>8s}")
print("-"*85)

# pure momentum baseline
m_pure = ann(M)
print(f"{'Pure V2.2 (momentum)':32s}  "
      f"{m_pure['CAGR']:>6.1f}%  {m_pure['Sharpe']:>5.2f}  "
      f"{m_pure['MaxDD']:>6.1f}%  {m_pure['Calmar']:>6.2f}  "
      f"{ann(sub(M,'2020-01','2026-12'))['Calmar']:>7.2f}  "
      f"{((1+sub(M,*GRIND)).prod()-1)*100:>6.1f}%  {'baseline':>8s}")

for name,(ser,sz) in books.items():
    idx_ = M.index.intersection(ser.index)
    blend = (1-W_VAL)*M.loc[idx_] + W_VAL*ser.loc[idx_]
    mf = ann(blend)
    mo = ann(sub(blend,'2020-01','2026-12'))
    g  = ((1+sub(blend,*GRIND)).prod()-1)*100 if len(sub(blend,*GRIND))>0 else np.nan
    d_cal = mf['Calmar']-m_pure['Calmar']
    print(f"{'V2.2+30% '+name[:18]:32s}  "
          f"{mf['CAGR']:>6.1f}%  {mf['Sharpe']:>5.2f}  "
          f"{mf['MaxDD']:>6.1f}%  {mf['Calmar']:>6.2f}  "
          f"{mo['Calmar']:>7.2f}  {g:>6.1f}%  {d_cal:>+7.2f}")

# ════════════════════════════════════════════════════════════
# FINAL ARCHITECTURE DESIGN (Option A)
# ════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("FINAL ARCHITECTURE: V2.2 + VALUE (Option A, 50B total)")
print("="*70)

# Pick best variant: highest OOS Calmar after blending
best_name, best_cal, best_ser = None, -1, None
for name,(ser,sz) in books.items():
    idx_ = M.index.intersection(ser.index)
    blend = (1-W_VAL)*M.loc[idx_] + W_VAL*ser.loc[idx_]
    mo = ann(sub(blend,'2020-01','2026-12'))
    if not np.isnan(mo['Calmar']) and mo['Calmar'] > best_cal:
        best_cal, best_name, best_ser = mo['Calmar'], name, ser

print(f"\n  Best value variant (by OOS Calmar): {best_name}")
print(f"\n  ARCHITECTURE SUMMARY:")
print(f"  ┌─────────────────────────────────────────────────────┐")
print(f"  │  TOTAL: 50B                                         │")
print(f"  │  ├─ BOOK A: BAL (V11 momentum)   17.5B  (35%)      │")
print(f"  │  ├─ BOOK B: LAG (PEAD momentum)  17.5B  (35%)      │")
print(f"  │  └─ BOOK C: VALUE ({best_name[:16]:16s}) 15.0B  (30%)      │")
print(f"  │                                                     │")
print(f"  │  DT5G gating (tất cả 3 books):                     │")
print(f"  │    CRISIS → VALUE gated 0%  (CAPIT sleeve takes over)│")
print(f"  │    BEAR   → VALUE 20% (~10B)                       │")
print(f"  │    NEUTRAL→ VALUE 30% (~15B) [target]              │")
print(f"  │    BULL   → VALUE 35% (~17.5B)                     │")
print(f"  │    EX-BULL→ VALUE 45% (~22.5B), BAL+LAG 12.5B each │")
print(f"  │                                                     │")
print(f"  │  CAPIT sleeve: on BAL+LAG books (unchanged)        │")
print(f"  │  Parking ETF:  on all 3 books (unchanged)          │")
print(f"  └─────────────────────────────────────────────────────┘")

# ════════════════════════════════════════════════════════════
# FIGURES
# ════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(20, 14))
fig.patch.set_facecolor('#0d1117')
fig.suptitle('Quality Gate Test: Value Book Variants + Option A Capital Structure\n'
             'V2.2 = BAL 17.5B + LAG 17.5B + VALUE 15B (30%) — 50B total',
             fontsize=12, fontweight='bold', color='white', y=0.98)
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.38)
dark = '#161b22'; sp = '#30363d'

def sty(ax, t=""):
    ax.set_facecolor(dark)
    for s in ax.spines.values(): s.set_color(sp)
    ax.tick_params(colors='#8b949e')
    if t: ax.set_title(t, color='#e6edf3', fontsize=9.5, fontweight='bold', pad=8)

V_COLORS = ['#8b949e','#58a6ff','#3fb950','#e8c547','#f97316','#d62728']

# ── R1C0-1: NAV all value variants + V2.2 ────────────────
ax1 = fig.add_subplot(gs[0, :2])
sty(ax1, 'Cumulative NAV: V2.2 vs Value Book Variants (standalone)')
nav_M = (1+M.dropna()).cumprod(); nav_M.index = nav_M.index.to_timestamp()
ax1.semilogy(nav_M.index, nav_M.values,
             label='Momentum V2.2 (V5)', color='white', lw=2.5)
for (name,(ser,sz)), col in zip(books.items(), V_COLORS):
    nav_v = (1+ser.dropna()).cumprod(); nav_v.index = nav_v.index.to_timestamp()
    ax1.semilogy(nav_v.index, nav_v.values, label=name, color=col, lw=1.5, alpha=0.8)
ax1.legend(fontsize=8, facecolor='#1c2128', labelcolor='white', ncol=2)
ax1.set_ylabel('NAV (log, start=1)', color='#8b949e')

# ── R1C2: Calmar comparison ───────────────────────────────
ax2 = fig.add_subplot(gs[0, 2])
sty(ax2, 'Calmar: Full vs OOS\nby Value Variant + Blend')
names_short = ['M only'] + [n[:10] for n in books]
cal_full = [ann(M)['Calmar']]
cal_oos  = [ann(sub(M,'2020-01','2026-12'))['Calmar']]
for name,(ser,sz) in books.items():
    idx_ = M.index.intersection(ser.index)
    bl = (1-W_VAL)*M.loc[idx_] + W_VAL*ser.loc[idx_]
    cal_full.append(ann(bl)['Calmar'])
    cal_oos.append(ann(sub(bl,'2020-01','2026-12'))['Calmar'])
x = np.arange(len(names_short))
w = 0.38
ax2.bar(x-w/2, cal_full, w, label='Full', color='#3fb950', alpha=0.8)
ax2.bar(x+w/2, cal_oos,  w, label='OOS',  color='#58a6ff', alpha=0.8)
ax2.axhline(cal_full[0], color='white', lw=1, ls='--', alpha=0.4)
ax2.set_xticks(x)
ax2.set_xticklabels(names_short, color='#8b949e', fontsize=7.5, rotation=30, ha='right')
ax2.set_ylabel('Calmar', color='#8b949e')
ax2.legend(fontsize=9, facecolor='#1c2128', labelcolor='white')

# ── R2C0: Portfolio size by variant ──────────────────────
ax3 = fig.add_subplot(gs[1, 0])
sty(ax3, 'Avg Portfolio Size by Variant\n(after quality gate)')
szs  = [sz for _,(_, sz) in books.items()]
cols = [V_COLORS[i] for i in range(len(books))]
names_v = [n.split()[0]+'\n'+n.split()[1] if len(n.split())>1 else n
           for n in books.keys()]
bars = ax3.bar(range(len(szs)), szs, color=cols, alpha=0.85)
ax3.axhline(8, color='red', lw=1, ls='--', alpha=0.7, label='Min viable (8)')
ax3.set_xticks(range(len(szs)))
ax3.set_xticklabels([n[:10] for n in books.keys()],
                     color='#8b949e', fontsize=8, rotation=30, ha='right')
ax3.set_ylabel('Avg names in portfolio', color='#8b949e')
ax3.legend(fontsize=8, facecolor='#1c2128', labelcolor='white')
for bar, sz in zip(bars, szs):
    ax3.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.3,
             f'{sz:.0f}', ha='center', color='white', fontsize=9)

# ── R2C1: Option A NAV comparison ────────────────────────
ax4 = fig.add_subplot(gs[1, 1])
sty(ax4, 'Option A (30% value): V2.2 + each variant\nOrange = best variant')
nav_M2 = (1+M.dropna()).cumprod(); nav_M2.index = nav_M2.index.to_timestamp()
ax4.semilogy(nav_M2.index, nav_M2.values,
             label='Pure V2.2', color='white', lw=2.5)
for (name,(ser,sz)), col in zip(books.items(), V_COLORS):
    idx_ = M.index.intersection(ser.index)
    bl = (1-W_VAL)*M.loc[idx_] + W_VAL*ser.loc[idx_]
    nav_bl = (1+bl.dropna()).cumprod(); nav_bl.index = nav_bl.index.to_timestamp()
    lw = 2.5 if name == best_name else 1.2
    alpha = 1.0 if name == best_name else 0.5
    ax4.semilogy(nav_bl.index, nav_bl.values,
                 label=f'+{name[:12]}' + (' BEST' if name==best_name else ''),
                 color='#f97316' if name==best_name else col,
                 lw=lw, alpha=alpha)
ax4.legend(fontsize=8, facecolor='#1c2128', labelcolor='white')
ax4.set_ylabel('NAV (log)', color='#8b949e')

# ── R2C2: Summary table ───────────────────────────────────
ax5 = fig.add_subplot(gs[1, 2])
ax5.set_facecolor(dark); ax5.axis('off')
sty(ax5, 'Option A: V2.2+30%VALUE summary')
hdr = ['Variant','Cal','OOS Cal','MaxDD','Grind']
rows_t = [hdr]
# pure
g0 = ((1+sub(M,*GRIND)).prod()-1)*100
rows_t.append(['Pure V2.2',
               f"{ann(M)['Calmar']:.2f}",
               f"{ann(sub(M,'2020-01','2026-12'))['Calmar']:.2f}",
               f"{ann(M)['MaxDD']:.1f}%",
               f"{g0:.1f}%"])
for name,(ser,sz) in books.items():
    idx_ = M.index.intersection(ser.index)
    bl = (1-W_VAL)*M.loc[idx_] + W_VAL*ser.loc[idx_]
    g = ((1+sub(bl,*GRIND)).prod()-1)*100 if len(sub(bl,*GRIND))>0 else np.nan
    rows_t.append([name[:16],
                   f"{ann(bl)['Calmar']:.2f}",
                   f"{ann(sub(bl,'2020-01','2026-12'))['Calmar']:.2f}",
                   f"{ann(bl)['MaxDD']:.1f}%",
                   f"{g:.1f}%"])
tbl = ax5.table(cellText=rows_t[1:], colLabels=rows_t[0],
                loc='center', cellLoc='center')
tbl.auto_set_font_size(False); tbl.set_fontsize(8); tbl.scale(1.1, 1.75)
for (r_i,c_i), cell in tbl.get_celld().items():
    cell.set_facecolor('#1c2128' if r_i%2==0 else dark)
    cell.set_text_props(color='#e6edf3'); cell.set_edgecolor(sp)
    if r_i==0:
        cell.set_facecolor('#21262d')
        cell.set_text_props(color='white', fontweight='bold')
    if r_i>0 and rows_t[r_i][0]==best_name[:16]:
        cell.set_facecolor('#1a2e0d')

out = WORKDIR + r"\value_quality_gate_test.png"
fig.savefig(out, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f"\nSaved: value_quality_gate_test.png")
plt.close()
print("DONE")
