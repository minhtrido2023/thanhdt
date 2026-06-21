"""
v23_improvements.py — Two overlays to fix V2.3's style-divergence grind weakness
================================================================================
V2.3 = V2.2 (BAL|LAG static+park) + capit. Known weak spot: 2025-08 -> now the
book bled -11.8% over 294d while VNINDEX +8.4% (VIC-led narrow megacap bull the
8L/momentum book avoids).

Overlay #1 — NARROW-BULL MEGACAP PARTICIPATION (user: size by market concentration):
  When the index is in an uptrend but breadth is NARROW (megacap-led), tilt part
  of the book into index-beta so it isn't left behind. Participation weight scales
  with concentration = (1 - breadth). Gated to uptrend only.

Overlay #2 — BOOK-LEVEL GRIND STOP (independent of DT5G; cut grind early):
  DT5G doesn't flag style-divergence (no crisis), so add a stop on the BOOK's own
  NAV. Test 3 flavors: hard drawdown-stop, NAV-trend stop (NAV<MA_N), book-momentum
  stop (trailing-3M<0). De-risk to cash/ETF when triggered; re-risk on recovery.

First-pass at RETURN level (blend / exposure-scale daily returns) to decide IF the
ideas work before touching the live engine. Reports full-period + the 2025-08 grind.
"""
import sys, os, subprocess
from io import StringIO
try: sys.stdout.reconfigure(encoding='utf-8')
except: pass
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings; warnings.filterwarnings('ignore')

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
BQ_PATH = r"bq"
PROJECT = "lithe-record-440915-m9"
STATE_TABLE = "tav2_bq.vnindex_5state_dt5g_live"

def bq(sql):
    cmd = (f'"{BQ_PATH}" query --use_legacy_sql=false --project_id={PROJECT}'
           f' --format=csv --quiet --max_rows=500000')
    r = subprocess.run(cmd, input=sql, capture_output=True, text=True, encoding="utf-8", shell=True)
    return pd.read_csv(StringIO(r.stdout)) if r.returncode == 0 and r.stdout.strip() else pd.DataFrame()

# ---- V2.3 daily NAV (BAL_cap + LAG_cap) ----
bal = pd.read_csv('data/pt_v22_bal_v21_cap.csv', parse_dates=['time']).set_index('time')['nav']
lag = pd.read_csv('data/pt_v22_lag_v21_cap.csv', parse_dates=['time']).set_index('time')['nav']
idx = bal.index.intersection(lag.index)
v23 = (bal.reindex(idx) + lag.reindex(idx))
d0, d1 = idx.min().date(), idx.max().date()

# ---- market data: breadth, VNINDEX, state ----
print("Pulling breadth / VNINDEX / state...")
mkt = bq(f"""
WITH br AS (
  SELECT t.time,
    SAFE_DIVIDE(COUNTIF(t.Close>t.MA200), COUNT(*)) AS breadth
  FROM tav2_bq.ticker_prune t
  WHERE t.time BETWEEN DATE '{d0}' AND DATE '{d1}' AND t.MA200 IS NOT NULL
    AND t.Trading_Value_1M_P50 >= 2e9
  GROUP BY t.time )
SELECT b.time, b.breadth, v.Close AS vni, v.ma200 AS vni_ma200, s.state
FROM br b
LEFT JOIN (SELECT tk.time, tk.Close, tk.MA200 AS ma200 FROM tav2_bq.ticker AS tk WHERE tk.ticker='VNINDEX') v ON v.time=b.time
LEFT JOIN {STATE_TABLE} s ON s.time=b.time
ORDER BY b.time
""")
mkt["time"] = pd.to_datetime(mkt["time"]); mkt = mkt.set_index("time")
mkt = mkt.reindex(idx).ffill()
breadth = mkt["breadth"]; vni = mkt["vni"]; vni_ma = mkt["vni_ma200"]; state = mkt["state"].fillna(3).astype(int)

v23_ret = v23.pct_change().fillna(0)
vni_ret = vni.pct_change().fillna(0)

YEARS = (idx[-1]-idx[0]).days/365.25
def metrics(nav):
    r = nav.pct_change().dropna(); tdy = len(r)/YEARS
    cagr = (nav.iloc[-1]/nav.iloc[0])**(1/YEARS)-1
    sd = r.std()*np.sqrt(tdy); mu = r.mean()*tdy
    dd = (nav/nav.cummax()-1).min()
    return dict(CAGR=cagr*100, Sharpe=mu/sd if sd>0 else 0, MaxDD=dd*100,
                Calmar=cagr/abs(dd) if dd<0 else np.nan)
def from_ret(r): return (1+r).cumprod()

# grind window
peak_date = v23.idxmax()
def grind_ret(r):
    g = r[r.index > peak_date]; return ((1+g).prod()-1)*100
base_grind = grind_ret(v23_ret)

print("="*78)
print(f"V2.3 IMPROVEMENT OVERLAYS  ({d0} -> {d1}, {YEARS:.1f}y)")
print(f"Grind window: {peak_date.date()} -> {d1}  (V2.3 base {base_grind:+.1f}%, VNI {grind_ret(vni_ret):+.1f}%)")
print("="*78)

mb = metrics(v23)
print(f"\n  BASE V2.3: CAGR {mb['CAGR']:.1f}% / Sh {mb['Sharpe']:.2f} / DD {mb['MaxDD']:.1f}% / "
      f"Cal {mb['Calmar']:.2f} / grind {base_grind:+.1f}%")

# ============================================================================
# OVERLAY #1 — narrow-bull megacap participation (size by concentration)
# ============================================================================
print("\n" + "="*78)
print("OVERLAY #1 — NARROW-BULL PARTICIPATION (tilt to index when breadth narrow)")
print("="*78)
# NOTE (revised): the narrow-drift grind (2025 VIC-led) is often NEUTRAL not BULL in DT5G
# (index drifts up on megacaps while breadth is weak). So gate on INDEX-UPTREND only
# (Close>MA200), NOT on DT5G bull state. Participation fires exactly when index rises but
# breadth is narrow — the regime where the broad book lags.
uptrend = (vni > vni_ma)                          # index above its own MA200
# diagnostic: DT5G state mix during the actual grind
gmask = idx > peak_date
print(f"  index-uptrend sessions: {int(uptrend.sum())}/{len(idx)} ({uptrend.mean()*100:.0f}%)")
gst = state[gmask].value_counts().sort_index()
print(f"  DT5G state mix in grind {peak_date.date()}->now: "
      + ", ".join(f"{int(k)}:{int(v)}d" for k,v in gst.items())
      + f"  (mean breadth {breadth[gmask].mean():.2f})")

def overlay1(breadth_thr, w_max, breadth_floor=0.20):
    # concentration score in [0,1]: 0 when breadth>=thr, 1 when breadth<=floor
    conc = ((breadth_thr - breadth)/(breadth_thr - breadth_floor)).clip(0,1)
    w_idx = (w_max * conc).where(uptrend, 0.0)     # only tilt in narrow bull
    blended = (1 - w_idx)*v23_ret + w_idx*vni_ret
    return blended, w_idx

print(f"\n  {'thr':>5s} {'w_max':>6s} | {'CAGR':>6s} {'Sharpe':>7s} {'MaxDD':>7s} {'Calmar':>7s} {'grind':>7s} {'avgW%':>6s}")
print("  " + "-"*68)
best1 = None
for thr in [0.45, 0.55]:
    for wm in [0.15, 0.25, 0.35]:
        bl, wi = overlay1(thr, wm)
        nav = from_ret(bl); m = metrics(nav)
        avgw = wi[uptrend].mean()*100 if uptrend.sum() else 0
        tag = ""
        if best1 is None or m['Sharpe'] > best1[1]['Sharpe']: best1 = ((thr,wm), m, bl, wi)
        print(f"  {thr:>5.2f} {wm:>6.2f} | {m['CAGR']:5.1f}% {m['Sharpe']:6.2f} {m['MaxDD']:6.1f}% "
              f"{m['Calmar']:6.2f} {grind_ret(bl):+6.1f}% {avgw:5.1f}%")
print(f"\n  base (no overlay):      {mb['CAGR']:5.1f}% {mb['Sharpe']:6.2f} {mb['MaxDD']:6.1f}% "
      f"{mb['Calmar']:6.2f} {base_grind:+6.1f}%")

# ============================================================================
# OVERLAY #2 — book-level grind stop (3 flavors, independent of DT5G)
# ============================================================================
print("\n" + "="*78)
print("OVERLAY #2 — BOOK GRIND STOP (de-risk on book's own weakness)")
print("="*78)

def stop_ddstop(dd_trig=-0.10, dd_release=-0.04, e_low=0.3):
    """De-risk to e_low when book DD from peak < dd_trig; re-risk when DD recovers above dd_release."""
    nav = v23.copy(); peak = nav.iloc[0]; stopped = False; exp = []
    navv = nav.values; pk = navv[0]
    for x in navv:
        pk = max(pk, x); dd = x/pk - 1
        if not stopped and dd <= dd_trig: stopped = True
        elif stopped and dd >= dd_release: stopped = False
        exp.append(e_low if stopped else 1.0)
    e = pd.Series(exp, index=nav.index).shift(1).fillna(1.0)   # act next day (no look-ahead)
    return e

def stop_trend(ma_n=60, e_low=0.3, confirm=0):
    """De-risk when book NAV < its own MA_n; re-risk when back above.
    confirm=K requires K consecutive days on the new side before switching (debounce)."""
    ma = v23.rolling(ma_n, min_periods=ma_n//2).mean()
    raw = (v23 >= ma)
    if confirm > 0:
        # only switch state after `confirm` consecutive days agree
        st = []; cur = True; run = 0; prev = True
        for ok in raw.values:
            if ok == prev: run += 1
            else: run = 1; prev = ok
            if run >= confirm: cur = ok
            st.append(cur)
        e = pd.Series([1.0 if s else e_low for s in st], index=v23.index)
    else:
        e = raw.astype(float).where(raw, e_low)
    return e.shift(1).fillna(1.0)

def stop_mom(win=63, e_low=0.3):
    """De-risk when book trailing-win return < 0."""
    tr = v23/v23.shift(win) - 1
    e = (tr >= 0).astype(float)
    e = e.where(e==1, e_low).shift(1).fillna(1.0)
    return e

STOP_TC = 0.003   # round-trip TC on the de-risked/re-risked fraction at each exposure change
def apply_stop(e):
    # de-risked portion sits in cash (0 return); charge TC on exposure changes (whipsaw cost)
    tc = e.diff().abs().fillna(0) * STOP_TC
    r = e*v23_ret - tc
    return from_ret(r), e

variants = []
for nm, e in [("DD-stop -10%/-4%", stop_ddstop(-0.10,-0.04,0.3)),
              ("Trend MA60 raw",   stop_trend(60,0.3,confirm=0)),
              ("Trend MA60 conf5", stop_trend(60,0.3,confirm=5)),
              ("Trend MA100 conf5",stop_trend(100,0.3,confirm=5)),
              ("Mom 6M<0",         stop_mom(126,0.3))]:
    nav, ee = apply_stop(e); m = metrics(nav)
    flips = int((ee.diff().abs()>0.01).sum())
    variants.append((nm, m, nav, ee, flips))

print(f"\n  {'variant':18s} | {'CAGR':>6s} {'Sharpe':>7s} {'MaxDD':>7s} {'Calmar':>7s} {'grind':>7s} {'flips':>5s} {'%derisk':>7s}")
print("  " + "-"*78)
for nm, m, nav, ee, flips in variants:
    derisk_pct = (ee<0.99).mean()*100
    print(f"  {nm:18s} | {m['CAGR']:5.1f}% {m['Sharpe']:6.2f} {m['MaxDD']:6.1f}% "
          f"{m['Calmar']:6.2f} {grind_ret(nav.pct_change().fillna(0)):+6.1f}% {flips:5d} {derisk_pct:6.1f}%")
print(f"  {'BASE (no stop)':18s} | {mb['CAGR']:5.1f}% {mb['Sharpe']:6.2f} {mb['MaxDD']:6.1f}% "
      f"{mb['Calmar']:6.2f} {base_grind:+6.1f}%")

# ============================================================================
# COMBINED best #1 + best #2
# ============================================================================
print("\n" + "="*78)
print("COMBINED — best participation + best stop")
print("="*78)
(p1, m1, bl1, wi1) = best1
# pick best stop by Sharpe that also doesn't kill CAGR much
best2 = max(variants, key=lambda v: v[1]['Sharpe'])
nm2, m2, nav2, ee2, fl2 = best2
print(f"  #1 best: thr={p1[0]} w_max={p1[1]} (Sh {m1['Sharpe']:.2f})")
print(f"  #2 best: {nm2} (Sh {m2['Sharpe']:.2f})")
# combine: apply participation blend, then book-stop exposure on top (with stop TC)
comb_ret = ee2 * bl1 - ee2.diff().abs().fillna(0) * STOP_TC
navc = from_ret(comb_ret); mc = metrics(navc)
print(f"\n  {'strategy':22s} | {'CAGR':>6s} {'Sharpe':>7s} {'MaxDD':>7s} {'Calmar':>7s} {'grind':>7s}")
print("  " + "-"*70)
print(f"  {'BASE V2.3':22s} | {mb['CAGR']:5.1f}% {mb['Sharpe']:6.2f} {mb['MaxDD']:6.1f}% {mb['Calmar']:6.2f} {base_grind:+6.1f}%")
print(f"  {'+#1 participation':22s} | {m1['CAGR']:5.1f}% {m1['Sharpe']:6.2f} {m1['MaxDD']:6.1f}% {m1['Calmar']:6.2f} {grind_ret(bl1):+6.1f}%")
print(f"  {'+#2 '+nm2:22s} | {m2['CAGR']:5.1f}% {m2['Sharpe']:6.2f} {m2['MaxDD']:6.1f}% {m2['Calmar']:6.2f} {grind_ret(nav2.pct_change().fillna(0)):+6.1f}%")
print(f"  {'+both':22s} | {mc['CAGR']:5.1f}% {mc['Sharpe']:6.2f} {mc['MaxDD']:6.1f}% {mc['Calmar']:6.2f} {grind_ret(comb_ret):+6.1f}%")

# IS/OOS for the combined
def slice_metrics(r, lo, hi):
    s = r[(r.index>=lo)&(r.index<=hi)]
    nav = from_ret(s); yrs=(s.index[-1]-s.index[0]).days/365.25
    cagr=(nav.iloc[-1])**(1/yrs)-1; tdy=len(s)/yrs
    sh=s.mean()*tdy/(s.std()*np.sqrt(tdy)); dd=(nav/nav.cummax()-1).min()
    return cagr*100, sh, dd*100
print("\n  IS/OOS (combined vs base):")
for lbl, lo, hi in [("IS 2014-19","2014-01-01","2019-12-31"),("OOS 2020-now","2020-01-01","2026-12-31")]:
    cb=slice_metrics(comb_ret, lo, hi); bs=slice_metrics(v23_ret, lo, hi)
    print(f"    {lbl}: base {bs[0]:.1f}%/Sh{bs[1]:.2f}/DD{bs[2]:.0f}  ->  +both {cb[0]:.1f}%/Sh{cb[1]:.2f}/DD{cb[2]:.0f}")

# ============================================================================
# FIGURE
# ============================================================================
fig = plt.figure(figsize=(19,10)); fig.patch.set_facecolor('#0d1117')
fig.suptitle('V2.3 Improvement Overlays — narrow-bull participation + book grind-stop\n'
             f'{d0} -> {d1} | grind from {peak_date.date()}',
             fontsize=12, color='white', fontweight='bold', y=0.99)
dark='#161b22'; sp='#30363d'
gs=gridspec.GridSpec(2,3,figure=fig,hspace=0.40,wspace=0.34)
def sty(ax,t=""):
    ax.set_facecolor(dark);[s.set_color(sp) for s in ax.spines.values()]
    ax.tick_params(colors='#8b949e',labelsize=8)
    if t: ax.set_title(t,color='#e6edf3',fontsize=10,fontweight='bold',pad=6)

ax1=fig.add_subplot(gs[0,:2]); sty(ax1,'NAV: base vs +#1 vs +#2 vs +both (log)')
for r,lbl,col,lw in [(v23_ret,'BASE V2.3','#8b949e',1.2),(bl1,'+#1 participation','#58a6ff',1.4),
                     (nav2.pct_change().fillna(0),f'+#2 {nm2}','#e8c547',1.4),(comb_ret,'+both','#3fb950',2.0)]:
    nav=from_ret(r); ax1.semilogy(nav.index, nav.values, color=col, lw=lw, label=lbl)
ax1.legend(fontsize=8,facecolor='#1c2128',labelcolor='white'); ax1.set_ylabel('NAV (log)',color='#8b949e')

ax2=fig.add_subplot(gs[0,2]); sty(ax2,'Grind window zoom (2025-06+)')
for r,lbl,col in [(v23_ret,'base','#8b949e'),(bl1,'+#1','#58a6ff'),(comb_ret,'+both','#3fb950')]:
    s=r[r.index>='2025-06-01']; nav=from_ret(s); ax2.plot(nav.index,nav.values/nav.iloc[0],color=col,lw=1.5,label=lbl)
vs=vni_ret[vni_ret.index>='2025-06-01']; navv=from_ret(vs); ax2.plot(navv.index,navv.values/navv.iloc[0],color='#d62728',lw=1.2,ls='--',label='VNI')
ax2.legend(fontsize=8,facecolor='#1c2128',labelcolor='white')

ax3=fig.add_subplot(gs[1,0]); sty(ax3,'Overlay #1 grid (Sharpe)')
labs=[]; shs=[]
for thr in [0.45,0.55]:
    for wm in [0.15,0.25,0.35]:
        bl,_=overlay1(thr,wm); labs.append(f"{thr}/{wm}"); shs.append(metrics(from_ret(bl))['Sharpe'])
ax3.bar(range(len(labs)),shs,color='#58a6ff',alpha=0.85); ax3.axhline(mb['Sharpe'],color='#d62728',ls='--',lw=1,label=f'base {mb["Sharpe"]:.2f}')
ax3.set_xticks(range(len(labs))); ax3.set_xticklabels(labs,rotation=40,ha='right',color='#8b949e',fontsize=7)
ax3.legend(fontsize=8,facecolor='#1c2128',labelcolor='white'); ax3.set_ylabel('Sharpe',color='#8b949e')
ax3.set_ylim(min(shs+[mb['Sharpe']])*0.97, max(shs+[mb['Sharpe']])*1.02)

ax4=fig.add_subplot(gs[1,1]); sty(ax4,'Overlay #2 variants (Sharpe vs grind)')
v_lab=[v[0] for v in variants]; v_sh=[v[1]['Sharpe'] for v in variants]
v_gr=[grind_ret(v[2].pct_change().fillna(0)) for v in variants]
x=np.arange(len(v_lab)); ax4b=ax4.twinx()
ax4.bar(x-0.2,v_sh,0.4,color='#e8c547',alpha=0.85,label='Sharpe')
ax4b.bar(x+0.2,v_gr,0.4,color='#3fb950',alpha=0.7,label='grind%')
ax4.axhline(mb['Sharpe'],color='#d62728',ls='--',lw=1)
ax4.set_xticks(x); ax4.set_xticklabels(v_lab,rotation=40,ha='right',color='#8b949e',fontsize=6.5)
ax4.set_ylabel('Sharpe',color='#e8c547'); ax4b.set_ylabel('grind %',color='#3fb950')
ax4.set_ylim(min(v_sh+[mb['Sharpe']])*0.96, max(v_sh+[mb['Sharpe']])*1.02)

ax5=fig.add_subplot(gs[1,2]); ax5.set_facecolor(dark); ax5.axis('off'); sty(ax5,'Summary')
tr=[['','CAGR','Sh','MaxDD','grind']]
for nm,m,gr in [('base',mb,base_grind),('+#1',m1,grind_ret(bl1)),('+#2',m2,grind_ret(nav2.pct_change().fillna(0))),('+both',mc,grind_ret(comb_ret))]:
    tr.append([nm,f"{m['CAGR']:.1f}%",f"{m['Sharpe']:.2f}",f"{m['MaxDD']:.1f}%",f"{gr:+.1f}%"])
t=ax5.table(cellText=tr[1:],colLabels=tr[0],loc='center',cellLoc='center')
t.auto_set_font_size(False); t.set_fontsize(9); t.scale(1.1,2.4)
for (ri,ci),c in t.get_celld().items():
    c.set_facecolor('#1c2128' if ri%2==0 else dark); c.set_text_props(color='#e6edf3'); c.set_edgecolor(sp)
    if ri==0: c.set_facecolor('#21262d'); c.set_text_props(color='white',fontweight='bold')
    if ri==4: c.set_facecolor('#0d2e14')

fig.savefig(WORKDIR+r"\v23_improvements.png", dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f"\nSaved: v23_improvements.png"); plt.close(); print("DONE")
