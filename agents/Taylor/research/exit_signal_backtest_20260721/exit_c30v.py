#!/usr/bin/env python
"""SellResistance exit-overlay backtest on custom30V (NEUTRAL parking sleeve).
Deal = one inter-rebalance hold of one name: entry=rebal_date Close, baseline exit=next rebal_date
Close, NO stop-loss (custom30V design = sizing + quarterly rebal only). Candidate = baseline OR
earlier exit if ~SellResistance fires during the hold (exec T+1 Open, no look-ahead).
Same discipline as job Taylor_20260721_045810 (BAL/LAG): honest fixed-slot NAV, N=1 trial."""
import pandas as pd, numpy as np
OUT="/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/exit_signal_backtest_20260721"

pan=pd.read_pickle(f"{OUT}/panel_c30v.pkl").sort_values(['ticker','time']).reset_index(drop=True)
deals=pd.read_csv(f"{OUT}/dealset_c30v.csv")
deals['entry']=pd.to_datetime(deals['entry']); deals['base_exit']=pd.to_datetime(deals['base_exit'])

# ---- ~SellResistance (filter.json): backward-only cols ----
c=pan
pan['SIG']=((c.Open/c.Close<0.95)&(c.Close<0.8*c.Res_1Y)&(c.Close/c.LO_3M_T1>1.58)&(c.Volume>2.47*c.Volume_3M_P50))
pan['SIG']=pan['SIG'].fillna(False)
print(f"~SellResistance fire-rate (all panel rows): {pan['SIG'].mean()*100:.3f}%  ({int(pan['SIG'].sum())} fires / {len(pan)})")

pan_by={tk:g.reset_index(drop=True) for tk,g in pan.groupby('ticker')}

def sim(tk, entry, base_exit):
    g=pan_by.get(tk)
    if g is None: return None
    i0=g.index[g.time==entry]
    if len(i0)==0:  # rebal day not a trading row for this ticker: use first row >= entry
        after=g.index[g.time>=entry]
        if len(after)==0: return None
        i0=after[0]
    else: i0=i0[0]
    ep=g.at[i0,'Close']
    if not (ep>0): return None
    ib=g.index[g.time==base_exit]
    if len(ib)==0:
        bef=g.index[g.time<base_exit]  # last trading row before next rebal
        if len(bef)==0: return None
        ib=bef[-1]
    else: ib=ib[0]
    if ib<=i0: return None
    b_ret=g.at[ib,'Close']/ep-1
    # candidate: scan hold window for signal; exec T+1 Open
    c_exit_i=ib; c_reason='TIME'; c_ret=b_ret; c_exec_px=g.at[ib,'Close']
    for i in range(i0+1, ib+1):
        if bool(g.at[i,'SIG']):
            j=i+1
            if j<=ib:
                c_exec_px=g.at[j,'Open'] if g.at[j,'Open']>0 else g.at[j,'Close']
                c_exit_i=j
            else:  # signal on last hold day -> exit at base_exit close (== baseline, no effect)
                c_exec_px=g.at[ib,'Close']; c_exit_i=ib
            c_reason='SIGNAL'; c_ret=c_exec_px/ep-1
            break
    fwd=(g.at[ib,'Close']/c_exec_px-1) if c_reason=='SIGNAL' else np.nan  # >0 cut winner, <0 dodged DD
    return dict(ticker=tk,entry=entry,base_exit=base_exit,ep=ep,b_ret=b_ret,b_hold=ib-i0,
                i0=i0,ib=ib,c_exit_i=c_exit_i,c_ret=c_ret,c_hold=c_exit_i-i0,c_reason=c_reason,fwd=fwd)

def run(df):
    rows=[sim(r.ticker,r.entry,r.base_exit) for r in df.itertuples()]
    return pd.DataFrame([x for x in rows if x is not None])

def nav_fixed_slots(res, variant):
    """entry->baseline-exit slot in BOTH; candidate holds cash(0) after early exit. Equal-weight."""
    from collections import defaultdict
    buck=defaultdict(list)
    for r in res.itertuples():
        g=pan_by[r.ticker]
        seg=g.iloc[r.i0:r.ib+1]; closes=seg['Close'].values; times=seg['time'].values; idxs=seg.index.values
        ic=r.c_exit_i if (variant=='candidate' and r.c_reason=='SIGNAL') else r.ib
        for k in range(1,len(seg)):
            v=(closes[k]/closes[k-1]-1) if idxs[k]<=ic else 0.0
            if np.isfinite(v): buck[times[k]].append(v)
    s=pd.Series({t:np.mean(v) for t,v in buck.items()}).sort_index()
    idx=pd.bdate_range(s.index.min(),s.index.max()); s=s.reindex(idx).fillna(0.0)
    nav=(1+s).cumprod(); yrs=(s.index[-1]-s.index[0]).days/365.25
    return dict(cagr=(nav.iloc[-1]**(1/yrs)-1)*100, sharpe=(s.mean()/s.std()*np.sqrt(252)) if s.std()>0 else 0,
                maxdd=(nav/nav.cummax()-1).min()*100, final=nav.iloc[-1])

if __name__=='__main__':
    res=run(deals)
    n=len(res); nf=int((res.c_reason=='SIGNAL').sum())
    print(f"\n===== ~SellResistance @ custom30V =====")
    print(f"deals simulated: {n} (of {len(deals)})   signal fired (early exit) on: {nf} ({100*nf/n:.2f}%)")
    print(f"PER-DEAL:  baseline mean {res.b_ret.mean()*100:+.2f}% median {res.b_ret.median()*100:+.2f}% win {100*(res.b_ret>0).mean():.1f}% hold {res.b_hold.mean():.1f}d")
    print(f"           candidate mean {res.c_ret.mean()*100:+.2f}% median {res.c_ret.median()*100:+.2f}% win {100*(res.c_ret>0).mean():.1f}% hold {res.c_hold.mean():.1f}d")
    print(f"           DELTA mean {(res.c_ret.mean()-res.b_ret.mean())*100:+.3f}pp")
    f=res[res.c_reason=='SIGNAL']
    if len(f):
        print(f"\nON {len(f)} SIGNAL-EXIT DEALS:")
        print(f"  base_ret@these mean {f.b_ret.mean()*100:+.2f}%  cand_ret mean {f.c_ret.mean()*100:+.2f}%  delta {(f.c_ret.mean()-f.b_ret.mean())*100:+.2f}pp")
        print(f"  fwd AFTER exit->baseline: mean {f.fwd.mean()*100:+.2f}% median {f.fwd.median()*100:+.2f}%  (<0 dodged DD, >0 cut winner)")
        print(f"  frac fwd<0 (dodged loss): {100*(f.fwd<0).mean():.1f}%   |  paired t on fwd: t={f.fwd.mean()/(f.fwd.std()/np.sqrt(len(f))):.2f}")
    # honest fixed-slot NAV
    b=nav_fixed_slots(res,'baseline'); cc=nav_fixed_slots(res,'candidate')
    print(f"\nHONEST FIXED-SLOT NAV (equal-weight, cash after early exit):")
    print(f"  baseline : CAGR {b['cagr']:+.2f}%  Sharpe {b['sharpe']:.2f}  MaxDD {b['maxdd']:.1f}%  final {b['final']:.3f}x")
    print(f"  candidate: CAGR {cc['cagr']:+.2f}%  Sharpe {cc['sharpe']:.2f}  MaxDD {cc['maxdd']:.1f}%  final {cc['final']:.3f}x")
    print(f"  DELTA CAGR {cc['cagr']-b['cagr']:+.3f}pp  Sharpe {cc['sharpe']-b['sharpe']:+.3f}  MaxDD {cc['maxdd']-b['maxdd']:+.2f}pp")
    # walk-forward IS/OOS by entry year
    print(f"\nWALK-FORWARD (per-deal delta):")
    for lab,mask in [('IS 2014-19',res.entry.dt.year<=2019),('OOS 2020+',res.entry.dt.year>=2020)]:
        sub=res[mask]; sf=int((sub.c_reason=='SIGNAL').sum())
        print(f"  [{lab}] n={len(sub)} fire={sf} base {sub.b_ret.mean()*100:+.2f}% cand {sub.c_ret.mean()*100:+.2f}% delta {(sub.c_ret.mean()-sub.b_ret.mean())*100:+.3f}pp")
    res.to_csv(f"{OUT}/result_c30v.csv",index=False)
    print(f"\nsaved -> {OUT}/result_c30v.csv")
