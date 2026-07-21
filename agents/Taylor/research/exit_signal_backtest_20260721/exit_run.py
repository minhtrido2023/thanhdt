#!/usr/bin/env python
import pandas as pd, numpy as np
exec(open("/tmp/exit_backtest.py").read().split("if __name__")[0])
deals=pd.read_csv("/tmp/dealset.csv"); deals['entry']=pd.to_datetime(deals['entry'])
bal=deals[deals.book=='BAL']; lag=deals[deals.book=='LAG']

# sanity: sess_since_rel spacing between releases ~quarterly
rel_events=pan[pan.groupby('ticker')['ID_Release'].transform(lambda s:s.ne(s.shift()))]
gap=rel_events.groupby('ticker')['time'].apply(lambda s: s.sort_values().diff().dt.days.median())
print("median days between release-events (should be ~90):", round(gap.median(),1))

def metrics_nav(df, ret_col, exit_col):
    """renormalized active-deal equal-weight daily NAV from deal Close paths."""
    from collections import defaultdict
    buck=defaultdict(list)
    for r in df.itertuples():
        g=pan_by[r.ticker]; i0=g.index[g.time==r.entry]
        if len(i0)==0: continue
        i0=i0[0]; xd=getattr(r,exit_col)
        ix=g.index[g.time==xd]
        if len(ix)==0: continue
        ix=ix[0]
        seg=g.iloc[i0:ix+1]
        dr=seg['Close'].pct_change().iloc[1:]
        for t,v in zip(seg['time'].iloc[1:], dr):
            if np.isfinite(v): buck[t].append(v)
    if not buck: return None
    s=pd.Series({t:np.mean(v) for t,v in buck.items()}).sort_index()
    idx=pd.bdate_range(s.index.min(), s.index.max())
    s=s.reindex(idx).fillna(0.0)
    nav=(1+s).cumprod()
    yrs=(s.index[-1]-s.index[0]).days/365.25
    cagr=nav.iloc[-1]**(1/yrs)-1
    sharpe=s.mean()/s.std()*np.sqrt(252) if s.std()>0 else 0
    dd=(nav/nav.cummax()-1).min()
    return dict(cagr=cagr*100, sharpe=sharpe, maxdd=dd*100, final=nav.iloc[-1], invested_days=int((s!=0).sum()))

def report(name, entry_df, hold, stop, sig):
    df=run(entry_df, hold, stop, 2, sig, name)
    df=df.dropna(subset=['b_ret'])
    n=len(df); nfire=(df.c_reason=='SIGNAL').sum()
    print(f"\n===== {name}  |  entries={n}  hold={hold} stop={stop}  signal={sig} =====")
    print(f"  candidate exited EARLIER on {nfire}/{n} deals ({100*nfire/n:.1f}%)")
    print(f"  PER-DEAL RETURN:  baseline mean {df.b_ret.mean()*100:+.2f}%  median {df.b_ret.median()*100:+.2f}%  win {100*(df.b_ret>0).mean():.1f}%  hold {df.b_hold.mean():.1f}d")
    print(f"                    candidate mean {df.c_ret.mean()*100:+.2f}%  median {df.c_ret.median()*100:+.2f}%  win {100*(df.c_ret>0).mean():.1f}%  hold {df.c_hold.mean():.1f}d")
    print(f"                    delta mean {(df.c_ret.mean()-df.b_ret.mean())*100:+.3f}pp")
    # only on the deals where signal fired: does candidate dodge DD or cut winners?
    f=df[df.c_reason=='SIGNAL']
    if len(f):
        print(f"  ON {len(f)} SIGNAL-EXIT DEALS: base_ret_at_this_deal mean {f.b_ret.mean()*100:+.2f}%  cand_ret mean {f.c_ret.mean()*100:+.2f}%  delta {(f.c_ret.mean()-f.b_ret.mean())*100:+.2f}pp")
        print(f"     fwd return AFTER candidate exit -> baseline exit: mean {f.fwd_after_exit.mean()*100:+.2f}%  median {f.fwd_after_exit.median()*100:+.2f}%  (<0=dodged DD, >0=cut winner)")
        print(f"     frac fwd<0 (dodged loss): {100*(f.fwd_after_exit<0).mean():.1f}%")
    # NAV path
    for tag,rc,xc in [('baseline','b_ret','b_exit'),('candidate','c_ret','c_exit')]:
        m=metrics_nav(df,rc,xc)
        if m: print(f"  NAV[{tag}]: CAGR {m['cagr']:+.2f}%  Sharpe {m['sharpe']:.2f}  MaxDD {m['maxdd']:.1f}%  final {m['final']:.3f}x  investeddays {m['invested_days']}")
    # walk-forward IS/OOS by entry year
    for lab,mask in [('IS 2014-19',entry_df.entry.dt.year<=2019),('OOS 2020+',entry_df.entry.dt.year>=2020)]:
        sub=run(entry_df[mask],hold,stop,2,sig,name).dropna(subset=['b_ret'])
        if len(sub)==0: continue
        print(f"  [{lab}] n={len(sub)} base {sub.b_ret.mean()*100:+.2f}% cand {sub.c_ret.mean()*100:+.2f}% delta {(sub.c_ret.mean()-sub.b_ret.mean())*100:+.3f}pp")
    return df

# PRIMARY tests
d1=report("SellResistance @ BAL", bal, 45, -0.20, 'SIG_SellResistance')
d2=report("BearDvg2 @ BAL",       bal, 45, -0.20, 'SIG_BearDvg2')
d3=report("SellLowGrowth @ LAG",  lag, 25, None,  'SIG_SellLowGrowth')
