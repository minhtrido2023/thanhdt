import pandas as pd, numpy as np
exec(open("/tmp/exit_backtest.py").read().split("if __name__")[0])
deals=pd.read_csv("/tmp/dealset.csv"); deals['entry']=pd.to_datetime(deals['entry'])
bal=deals[deals.book=='BAL']; lag=deals[deals.book=='LAG']

def nav_fixed_slots(df, variant):
    """Honest isolation: slot occupied entry->BASELINE-exit in BOTH variants.
       baseline: earns deal daily ret whole window.
       candidate: earns deal daily ret until candidate-exit, then CASH(0) to baseline-exit.
       Denominator (active slots per day) identical across variants."""
    from collections import defaultdict
    buck=defaultdict(list)
    for r in df.itertuples():
        g=pan_by[r.ticker]; i0=g.index[g.time==r.entry]
        if len(i0)==0: continue
        i0=i0[0]
        ib=g.index[g.time==r.b_exit]
        if len(ib)==0: continue
        ib=ib[0]
        # candidate cutoff index
        ic=ib
        if variant=='candidate' and r.c_reason=='SIGNAL':
            icl=g.index[g.time==r.c_exit]
            if len(icl): ic=icl[0]
        seg=g.iloc[i0:ib+1]
        closes=seg['Close'].values; times=seg['time'].values; idxs=seg.index.values
        for k in range(1,len(seg)):
            t=times[k]
            if idxs[k]<=ic:
                v=closes[k]/closes[k-1]-1
            else:
                v=0.0   # cash after candidate exit, slot still reserved
            if np.isfinite(v): buck[t].append(v)
    s=pd.Series({t:np.mean(v) for t,v in buck.items()}).sort_index()
    idx=pd.bdate_range(s.index.min(),s.index.max()); s=s.reindex(idx).fillna(0.0)
    nav=(1+s).cumprod(); yrs=(s.index[-1]-s.index[0]).days/365.25
    return dict(cagr=(nav.iloc[-1]**(1/yrs)-1)*100, sharpe=s.mean()/s.std()*np.sqrt(252) if s.std()>0 else 0,
                maxdd=(nav/nav.cummax()-1).min()*100, final=nav.iloc[-1])

def go(name,entry_df,hold,stop,sig):
    df=run(entry_df,hold,stop,2,sig,name).dropna(subset=['b_ret'])
    b=nav_fixed_slots(df,'baseline'); c=nav_fixed_slots(df,'candidate')
    print(f"\n{name}: (fixed-slot honest NAV, cash after early exit)")
    print(f"  baseline : CAGR {b['cagr']:+.2f}%  Sharpe {b['sharpe']:.2f}  MaxDD {b['maxdd']:.1f}%  final {b['final']:.3f}x")
    print(f"  candidate: CAGR {c['cagr']:+.2f}%  Sharpe {c['sharpe']:.2f}  MaxDD {c['maxdd']:.1f}%  final {c['final']:.3f}x")
    print(f"  DELTA CAGR {c['cagr']-b['cagr']:+.3f}pp  Sharpe {c['sharpe']-b['sharpe']:+.3f}  MaxDD {c['maxdd']-b['maxdd']:+.2f}pp")

go("SellResistance @ BAL", bal,45,-0.20,'SIG_SellResistance')
go("BearDvg2 @ BAL",       bal,45,-0.20,'SIG_BearDvg2')
go("SellLowGrowth @ LAG",  lag,25,None,'SIG_SellLowGrowth')
