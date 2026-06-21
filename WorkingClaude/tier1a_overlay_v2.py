"""
Tier 1A overlay v2 — corrected design based on state-conditional IC.

Old (v1) design FAILED: fired override at state 4-5 where DXY IC is weakest.
New (v2) design: fire at state 3 (NEUTRAL) where DXY IC is strongest.

Variant A: state 3 + DXY_rank > th → scale BA daily return by s
Variant B: state 3 OR 5 + DXY_rank > th → scale by s
Variant C: continuous scale: scale = 1 - max(0, dxy_rank - th) * intensity
           (gradual reduction as DXY rank rises above threshold)
Variant D: EMLC confirmation: only fire when BOTH DXY_rank high AND EMLC_rank_inv high
"""
import pandas as pd
import numpy as np

df = pd.read_csv('data/macro_lag_data.csv', parse_dates=['time'])
ba = pd.read_csv('data/ba_v11_nav.csv', parse_dates=['time'])
df = df.merge(ba[['time','BA_v11']], on='time', how='left')
df['ba_ret'] = df['BA_v11'].pct_change().fillna(0.0)
df = df[df['BA_v11'].notna()].reset_index(drop=True)

print(f"Period: {df['time'].iloc[0].date()} -> {df['time'].iloc[-1].date()}, n={len(df)}")

# Baseline BA NAV
nav_base = np.ones(len(df))
for i in range(1, len(df)):
    nav_base[i] = nav_base[i-1] * (1 + df['ba_ret'].iloc[i])

def stats(nav, dates, t0=None, t1=None):
    if t0 is not None:
        mask = (dates>=pd.Timestamp(t0))
        if t1: mask &= (dates<=pd.Timestamp(t1))
        nav = nav[mask]; dates = dates[mask]
    rets = pd.Series(nav).pct_change().dropna()
    yrs = (dates.iloc[-1]-dates.iloc[0]).days/365.25
    cagr = (nav[-1]/nav[0])**(1/yrs)-1
    sh = rets.mean()/rets.std()*np.sqrt(250) if rets.std()>0 else 0
    cm = pd.Series(nav).cummax()
    dd = (pd.Series(nav)/cm-1).min()
    return dict(cagr=cagr*100, sh=sh, dd=dd*100, calmar=cagr/abs(dd) if dd!=0 else 0)

# ── Variant runners ──
def run_variant_A(df, th, scale, states={3}):
    """state in {states} AND DXY_rank > th → scale"""
    nav = np.ones(len(df))
    n_fire = 0
    for i in range(1, len(df)):
        r = df['ba_ret'].iloc[i]
        st = df['state'].iloc[i]
        dxr = df['DXY_rank252'].iloc[i]
        if not pd.isna(dxr) and not pd.isna(st) and int(st) in states and dxr > th:
            r = r * scale
            n_fire += 1
        nav[i] = nav[i-1]*(1+r)
    return nav, n_fire

def run_variant_C(df, th, intensity, states={3}):
    """Gradual: scale = 1 - max(0, dxy_rank - th) * intensity, only in target states"""
    nav = np.ones(len(df))
    n_fire = 0
    for i in range(1, len(df)):
        r = df['ba_ret'].iloc[i]
        st = df['state'].iloc[i]
        dxr = df['DXY_rank252'].iloc[i]
        if not pd.isna(dxr) and not pd.isna(st) and int(st) in states:
            extra = max(0, dxr - th)
            scale = max(0.3, 1 - extra*intensity)
            if scale < 1: n_fire += 1
            r = r * scale
        nav[i] = nav[i-1]*(1+r)
    return nav, n_fire

def run_variant_D(df, dxy_th, emlc_th, scale, states={3}):
    """state in {states} AND DXY_rank > dxy_th AND EMLC_inv > emlc_th → scale"""
    nav = np.ones(len(df))
    n_fire = 0
    for i in range(1, len(df)):
        r = df['ba_ret'].iloc[i]
        st = df['state'].iloc[i]
        dxr = df['DXY_rank252'].iloc[i]
        emi = df['EMLC_rank252_inv'].iloc[i]
        if (not pd.isna(dxr) and not pd.isna(emi) and not pd.isna(st)
            and int(st) in states and dxr > dxy_th and emi > emlc_th):
            r = r * scale
            n_fire += 1
        nav[i] = nav[i-1]*(1+r)
    return nav, n_fire

def run_variant_E(df, th, scale, states={3}, lookahead_avoid=20):
    """state in {states} AND DXY_rank > th sustained for N days (avoid false signals)"""
    nav = np.ones(len(df))
    n_fire = 0
    dxr_sustained = df['DXY_rank252'].rolling(lookahead_avoid).min()
    for i in range(1, len(df)):
        r = df['ba_ret'].iloc[i]
        st = df['state'].iloc[i]
        sus = dxr_sustained.iloc[i]
        if not pd.isna(sus) and not pd.isna(st) and int(st) in states and sus > th:
            r = r * scale
            n_fire += 1
        nav[i] = nav[i-1]*(1+r)
    return nav, n_fire

# Periods
periods = [('FULL 2014-2026', None, None),
           ('IS  (2014-2018)', '2014-01-01', '2018-12-31'),
           ('OOS (2019-2026)', '2019-01-01', None)]

print(f"\n{'config':<60s} {'period':<18s} {'CAGR':>7s} {'Sh':>5s} {'DD':>7s} {'Calmar':>6s} {'dCAGR':>7s} {'n_fire':>7s}")
print('-'*120)
for plabel, t0, t1 in periods:
    sb = stats(nav_base, df['time'], t0, t1)
    print(f"{'BA v11 baseline':<60s} {plabel:<18s} {sb['cagr']:7.2f} {sb['sh']:5.2f} "
          f"{sb['dd']:7.2f} {sb['calmar']:6.2f}")
print()

# ── Variant A: state 3 only ──
print("--- Variant A: state {3} ONLY (corrected from v1 which used {4,5}) ---")
for th, sc in [(0.85, 0.7), (0.85, 0.5), (0.80, 0.7), (0.85, 0.3), (0.75, 0.7)]:
    nav, nf = run_variant_A(df, th, sc, states={3})
    for plabel, t0, t1 in periods:
        s = stats(nav, df['time'], t0, t1)
        sb = stats(nav_base, df['time'], t0, t1)
        d = s['cagr']-sb['cagr']
        marker = ' *' if (plabel.startswith('OOS') and d>0
                          and s['sh']>=sb['sh']-0.02 and s['dd']>=sb['dd']-0.5) else ''
        print(f"VarA state=3 th={th} scale={sc:.1f}                                  {plabel:<18s} "
              f"{s['cagr']:7.2f} {s['sh']:5.2f} {s['dd']:7.2f} {s['calmar']:6.2f} {d:+7.2f} {nf:>7d}{marker}")
    print()

# ── Variant A: state 3 OR 1 ──
print("--- Variant A: state {1,3} (also CRISIS, since CRISIS IC was -0.124 not zero) ---")
for th, sc in [(0.85, 0.7), (0.80, 0.5)]:
    nav, nf = run_variant_A(df, th, sc, states={1,3})
    for plabel, t0, t1 in periods:
        s = stats(nav, df['time'], t0, t1)
        sb = stats(nav_base, df['time'], t0, t1)
        d = s['cagr']-sb['cagr']
        marker = ' *' if (plabel.startswith('OOS') and d>0
                          and s['sh']>=sb['sh']-0.02 and s['dd']>=sb['dd']-0.5) else ''
        print(f"VarA state={{1,3}} th={th} scale={sc:.1f}                            {plabel:<18s} "
              f"{s['cagr']:7.2f} {s['sh']:5.2f} {s['dd']:7.2f} {s['calmar']:6.2f} {d:+7.2f} {nf:>7d}{marker}")
    print()

# ── Variant C: gradual scale ──
print("--- Variant C: gradual scale (state=3) ---")
for th, inten in [(0.70, 2.0), (0.70, 1.5), (0.80, 2.0), (0.75, 3.0)]:
    nav, nf = run_variant_C(df, th, inten, states={3})
    for plabel, t0, t1 in periods:
        s = stats(nav, df['time'], t0, t1)
        sb = stats(nav_base, df['time'], t0, t1)
        d = s['cagr']-sb['cagr']
        marker = ' *' if (plabel.startswith('OOS') and d>0
                          and s['sh']>=sb['sh']-0.02 and s['dd']>=sb['dd']-0.5) else ''
        print(f"VarC state=3 th={th} intensity={inten}                              {plabel:<18s} "
              f"{s['cagr']:7.2f} {s['sh']:5.2f} {s['dd']:7.2f} {s['calmar']:6.2f} {d:+7.2f} {nf:>7d}{marker}")
    print()

# ── Variant D: dual confirmation ──
print("--- Variant D: DXY high AND EMLC stress (state=3) ---")
for dth, eth, sc in [(0.80, 0.70, 0.7), (0.85, 0.75, 0.5), (0.75, 0.75, 0.7)]:
    nav, nf = run_variant_D(df, dth, eth, sc, states={3})
    for plabel, t0, t1 in periods:
        s = stats(nav, df['time'], t0, t1)
        sb = stats(nav_base, df['time'], t0, t1)
        d = s['cagr']-sb['cagr']
        marker = ' *' if (plabel.startswith('OOS') and d>0
                          and s['sh']>=sb['sh']-0.02 and s['dd']>=sb['dd']-0.5) else ''
        print(f"VarD state=3 DXY>{dth} EMLC>{eth} sc={sc:.1f}                       {plabel:<18s} "
              f"{s['cagr']:7.2f} {s['sh']:5.2f} {s['dd']:7.2f} {s['calmar']:6.2f} {d:+7.2f} {nf:>7d}{marker}")
    print()

# ── Variant E: sustained high (avoid blip false signals) ──
print("--- Variant E: DXY sustained > th for 20d (state=3) ---")
for th, sc in [(0.80, 0.7), (0.75, 0.7), (0.85, 0.5)]:
    nav, nf = run_variant_E(df, th, sc, states={3}, lookahead_avoid=20)
    for plabel, t0, t1 in periods:
        s = stats(nav, df['time'], t0, t1)
        sb = stats(nav_base, df['time'], t0, t1)
        d = s['cagr']-sb['cagr']
        marker = ' *' if (plabel.startswith('OOS') and d>0
                          and s['sh']>=sb['sh']-0.02 and s['dd']>=sb['dd']-0.5) else ''
        print(f"VarE state=3 DXY sus 20d > {th} sc={sc:.1f}                         {plabel:<18s} "
              f"{s['cagr']:7.2f} {s['sh']:5.2f} {s['dd']:7.2f} {s['calmar']:6.2f} {d:+7.2f} {nf:>7d}{marker}")
    print()
