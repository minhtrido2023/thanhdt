"""
Tier 2 (lite) — Vietnam macro proxies from yfinance.

Since direct VN monthly macro is unscrapeable from this network, use GLOBAL
proxies that capture similar information:

  CPI proxy:        Brent oil (CL=F), Copper (HG=F), DBA agriculture
  Rate proxy:       ^TNX (US 10Y), ^IRX (US 3M), TLT/IEF ratio (yield curve)
  Credit stress:    HYG (HY bond ETF), LQD (IG bond ETF), HYG/LQD ratio
  EM stress:        VWO (EM equities), EEM, EMLC/EMB
  VN-specific:      VNM (VanEck Vietnam ETF) premium/discount
  Risk regime:      VIX, ^VIX, GVZ (gold vol)

These are NOT Vietnamese CPI/PMI/deposit rate, but they capture:
  - Inflation pressure (via commodity prices Vietnam imports/exports)
  - Rate cycle (via US yields — Vietnam follows USD trajectory)
  - Credit stress (via HY OAS proxy)
  - Foreign demand for Vietnam exposure (via VNM ETF flows)

Test: do any of these (+lag) add marginal IC over what DXY already provides?
"""
import pandas as pd
import numpy as np
import yfinance as yf
import subprocess, io

def spearman(x, y):
    x = pd.Series(x); y = pd.Series(y)
    m = x.notna() & y.notna()
    x, y = x[m], y[m]
    if len(x) < 30: return np.nan
    rx, ry = x.rank(), y.rank()
    sx, sy = rx.std(), ry.std()
    if sx*sy == 0: return np.nan
    return ((rx-rx.mean())*(ry-ry.mean())).mean()/(sx*sy)

# ── Pull all proxies ──
print("Pulling global macro proxies via yfinance...")
syms = {
    'OIL':'CL=F', 'COPPER':'HG=F', 'GOLD':'GC=F',
    'TNX':'^TNX', 'IRX':'^IRX', 'TYX':'^TYX',
    'HYG':'HYG', 'LQD':'LQD',
    'VWO':'VWO', 'EEM':'EEM', 'VNM':'VNM',
    'VIX':'^VIX',
    'DXY':'DX-Y.NYB', 'USDVND':'USDVND=X',
    'EMB':'EMB', 'EMLC':'EMLC',
}
data = {}
for name, sym in syms.items():
    try:
        h = yf.Ticker(sym).history(start='2010-01-01', end='2026-05-20', auto_adjust=False)
        if len(h) < 100:
            print(f"  {name}: TOO SHORT n={len(h)}"); continue
        h = h[['Close']].copy()
        h.columns = [name]
        h.index = pd.to_datetime(h.index.date)
        data[name] = h
        print(f"  {name}: n={len(h)}, {h.index[0].date()} -> {h.index[-1].date()}")
    except Exception as e:
        print(f"  {name}: FAIL {str(e)[:60]}")

# Merge
mac = data['DXY']
for k in data:
    if k != 'DXY':
        mac = mac.join(data[k], how='outer')
mac = mac.ffill().dropna(subset=['DXY','VNM','VIX','HYG'])  # require key series
print(f"\nMerged macro panel: {len(mac)} rows, {mac.index[0].date()} -> {mac.index[-1].date()}")

# ── Engineered features ──
# Commodity inflation pulse
mac['OIL_mom20'] = mac['OIL'].pct_change(20)
mac['OIL_mom60'] = mac['OIL'].pct_change(60)
mac['COPPER_mom20'] = mac['COPPER'].pct_change(20)
mac['GOLD_mom60']   = mac['GOLD'].pct_change(60)
# Rate environment
mac['TNX_d20'] = mac['TNX'].diff(20)
mac['TNX_d60'] = mac['TNX'].diff(60)
mac['TNX_rank252'] = mac['TNX'].rolling(252).rank(pct=True)
# Yield curve (10Y - 3M)
mac['yield_curve'] = mac['TNX'] - mac['IRX']
mac['yc_d60'] = mac['yield_curve'].diff(60)
# Credit stress
mac['HYG_ret60'] = mac['HYG'].pct_change(60)
mac['HYG_LQD'] = mac['HYG'] / mac['LQD']
mac['HYG_LQD_d60'] = mac['HYG_LQD'].diff(60)
mac['HYG_LQD_rank252_inv'] = 1 - mac['HYG_LQD'].rolling(252).rank(pct=True)
# VIX
mac['VIX_z60'] = (mac['VIX'] - mac['VIX'].rolling(60).mean()) / mac['VIX'].rolling(60).std()
mac['VIX_rank252'] = mac['VIX'].rolling(252).rank(pct=True)
# EM stress
mac['VWO_ret60']  = mac['VWO'].pct_change(60)
mac['EEM_ret60']  = mac['EEM'].pct_change(60)
mac['EMB_ret60']  = mac['EMB'].pct_change(60)
mac['EMLC_ret60'] = mac['EMLC'].pct_change(60)
# VNM ETF (direct foreign appetite for Vietnam)
mac['VNM_ret20']   = mac['VNM'].pct_change(20)
mac['VNM_ret60']   = mac['VNM'].pct_change(60)
mac['VNM_rank252_inv'] = 1 - mac['VNM'].rolling(252).rank(pct=True)
# DXY (anchor)
mac['DXY_rank252'] = mac['DXY'].rolling(252).rank(pct=True)
mac['DXY_mom60']   = mac['DXY'].pct_change(60)

# ── VNI ──
vni_csv = subprocess.run(['bq','query','--use_legacy_sql=false','--project_id=lithe-record-440915-m9',
                          '--format=csv','--max_rows=20000','-q',
                          'SELECT t.time, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker="VNINDEX" AND t.time>="2011-01-01" ORDER BY t.time'],
                         capture_output=True,text=True,shell=True).stdout
vni = pd.read_csv(io.StringIO(vni_csv), parse_dates=['time']).set_index('time')
vni.columns = ['VNI']
state = pd.read_csv('_state.csv', parse_dates=['time']).set_index('time')

df = vni.join(mac, how='left').join(state, how='left')
df['state'] = df['state'].ffill()
df = df.ffill().dropna(subset=['VNI','DXY','VNM'])
print(f"Final joined: {len(df)} rows")

# Forward VNI returns
for h in [20, 60, 120]:
    df[f'fwd{h}'] = df['VNI'].shift(-h)/df['VNI'] - 1

# ── IC matrix: feature × lag × horizon ──
features = ['OIL_mom20','OIL_mom60','COPPER_mom20','GOLD_mom60',
            'TNX_d20','TNX_d60','TNX_rank252','yield_curve','yc_d60',
            'HYG_ret60','HYG_LQD_d60','HYG_LQD_rank252_inv',
            'VIX_z60','VIX_rank252',
            'VWO_ret60','EEM_ret60','EMB_ret60','EMLC_ret60',
            'VNM_ret20','VNM_ret60','VNM_rank252_inv',
            'DXY_rank252','DXY_mom60']
lags = [0, 5, 10, 20, 40, 60]

# Full table
print("\n" + "="*100)
print("MARGINAL IC TABLE (fwd60, FULL sample)")
print("="*100)
print(f"{'feature':22s} " + " ".join(f"{'lag'+str(l):>8s}" for l in lags))
records = []
for f in features:
    row_str = f"{f:22s} "
    for l in lags:
        ic = spearman(df[f].shift(l), df['fwd60'])
        row_str += f" {ic:+8.3f}" if not np.isnan(ic) else f" {'nan':>8s}"
        records.append({'feat':f,'lag':l,'horizon':60,'ic':ic})
    print(row_str)

print("\n--- fwd120 ---")
print(f"{'feature':22s} " + " ".join(f"{'lag'+str(l):>8s}" for l in lags))
for f in features:
    row_str = f"{f:22s} "
    for l in lags:
        ic = spearman(df[f].shift(l), df['fwd120'])
        row_str += f" {ic:+8.3f}" if not np.isnan(ic) else f" {'nan':>8s}"
        records.append({'feat':f,'lag':l,'horizon':120,'ic':ic})
    print(row_str)

# Top features by |IC| at fwd60
rec = pd.DataFrame(records)
rec['abs_ic'] = rec['ic'].abs()
print("\n" + "="*100)
print("TOP 20 (feat, lag) at fwd60 by |IC|")
print("="*100)
print(rec[rec['horizon']==60].nlargest(20, 'abs_ic')[['feat','lag','ic']].to_string(index=False))

print("\nTOP 20 at fwd120 by |IC|")
print(rec[rec['horizon']==120].nlargest(20, 'abs_ic')[['feat','lag','ic']].to_string(index=False))

# ── Walk-forward consistency for top candidates ──
df_is  = df[df.index < '2019-01-01']
df_oos = df[df.index >= '2019-01-01']
print("\n" + "="*100)
print("WALK-FORWARD top candidates at fwd60")
print("="*100)
print(f"{'feat':22s} {'lag':>4s} {'IC_full':>9s} {'IC_IS':>9s} {'IC_OOS':>9s} {'consistent':>12s}")
top = rec[rec['horizon']==60].nlargest(15, 'abs_ic')
for _, r in top.iterrows():
    f, l = r['feat'], int(r['lag'])
    ic_is  = spearman(df_is[f].shift(l), df_is['fwd60'])
    ic_oos = spearman(df_oos[f].shift(l), df_oos['fwd60'])
    cons = (not np.isnan(ic_is) and not np.isnan(ic_oos)
            and np.sign(ic_is)==np.sign(ic_oos)
            and abs(ic_is)>=0.10 and abs(ic_oos)>=0.10)
    print(f"{f:22s} {l:>4d} {r['ic']:+9.3f} {ic_is:+9.3f} {ic_oos:+9.3f} {'YES' if cons else 'no':>12s}")

# ── Marginal vs DXY ──
print("\n" + "="*100)
print("MARGINAL CONTRIBUTION OVER DXY_rank252 (partial correlation, fwd60)")
print("="*100)
print(f"{'feature':22s} {'lag':>4s} {'raw_IC':>8s} {'partial_IC_over_DXY':>20s}")

# Compute partial correlation: corr(feature, fwd60 | DXY_rank252)
def partial_corr(a, b, c):
    """Spearman partial corr of a,b controlling for c."""
    a = pd.Series(a); b = pd.Series(b); c = pd.Series(c)
    m = a.notna() & b.notna() & c.notna()
    a, b, c = a[m], b[m], c[m]
    if len(a) < 40: return np.nan
    # Rank-based residualization
    ra, rb, rc = a.rank(), b.rank(), c.rank()
    # Linear regression on ranks: residual_a = ra - beta_ac*rc; same for b
    beta_ac = ((ra-ra.mean())*(rc-rc.mean())).sum() / max(((rc-rc.mean())**2).sum(),1e-9)
    beta_bc = ((rb-rb.mean())*(rc-rc.mean())).sum() / max(((rc-rc.mean())**2).sum(),1e-9)
    res_a = ra - beta_ac*rc
    res_b = rb - beta_bc*rc
    sa, sb = res_a.std(), res_b.std()
    if sa*sb == 0: return np.nan
    return ((res_a-res_a.mean())*(res_b-res_b.mean())).mean()/(sa*sb)

for _, r in rec[rec['horizon']==60].nlargest(20, 'abs_ic').iterrows():
    f, l = r['feat'], int(r['lag'])
    if f == 'DXY_rank252': continue
    raw_ic = r['ic']
    pic = partial_corr(df[f].shift(l), df['fwd60'], df['DXY_rank252'])
    print(f"{f:22s} {l:>4d} {raw_ic:+8.3f} {pic:+20.3f}")

# Save
df.to_csv('tier2_macro_panel.csv')
rec.to_csv('tier2_macro_ic.csv', index=False)
print("\nSaved: tier2_macro_panel.csv, tier2_macro_ic.csv")
