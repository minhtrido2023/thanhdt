#!/usr/bin/env python
"""Exit-signal overlay backtest — SellResistance / SellLowGrowth / BearDvg2.
Isolates exit-signal delta on the SAME production entry set (from R3 audit CSV).
Baseline exits verified in pt_v23_audit_2014.py: BAL hold=45d stop=-0.20; LAG hold=25d no-stop.
Candidate = baseline OR earlier exit if signal fires (execute next-session Open, no look-ahead)."""
import pandas as pd, numpy as np, sys

pan=pd.read_pickle("/tmp/panel.pkl").sort_values(['ticker','time']).reset_index(drop=True)
deals=pd.read_csv("/tmp/dealset.csv"); deals['entry']=pd.to_datetime(deals['entry'])

# ---- sessions since last earnings release: count rows since ID_Release last changed (per ticker) ----
pan['rel_chg']=pan.groupby('ticker')['ID_Release'].transform(lambda s: s.ne(s.shift()).cumsum())
pan['sess_since_rel']=pan.groupby(['ticker','rel_chg']).cumcount()

# ---- candidate exit-signal booleans (all backward-only cols) ----
c=pan
pan['SIG_SellResistance']=((c.Open/c.Close<0.95)&(c.Close<0.8*c.Res_1Y)&
    (c.Close/c.LO_3M_T1>1.58)&(c.Volume>2.47*c.Volume_3M_P50))
pan['SIG_SellLowGrowth']=((c.NP_P0/c.NP_P4<1.2)&(c.sess_since_rel<=10))
pan['SIG_BearDvg2']=((c.D_RSI_Max1W/c.D_RSI>0.88)&(c.D_RSI_T1/c.D_RSI>1.11)&(c.D_RSI_Max3M>0.66)&
    (c.D_RSI_Max1W<0.76)&(c.D_RSI_Max1W>0.57)&(c.D_RSI_Max1W_Close/c.D_RSI_Max3M_Close>1.12)&
    (c.D_RSI_Max3M_MACD/c.D_RSI_Max1W_MACD>1.29)&(c.Volume>1.11*c.Volume_1M)&
    (c.D_RSI_Max3M/c.D_RSI_Max1W>1.21))
for s in ['SIG_SellResistance','SIG_SellLowGrowth','SIG_BearDvg2']:
    pan[s]=pan[s].fillna(False)
print("signal fire-rate (all panel rows):")
for s in ['SIG_SellResistance','SIG_SellLowGrowth','SIG_BearDvg2']:
    print(f"  {s}: {pan[s].mean()*100:.3f}%  ({int(pan[s].sum())} fires)")

# index panel by ticker for fast lookup
pan_by={tk:g.reset_index(drop=True) for tk,g in pan.groupby('ticker')}

def sim_deal(tk, entry, hold_days, stop_loss, min_hold, sigcol=None):
    """Return dict: baseline & candidate exit for one deal. Return computed Close/Close.
    Candidate exit executes at NEXT session Open after the signal day (T+1, no look-ahead)."""
    g=pan_by.get(tk)
    if g is None: return None
    i0=g.index[g.time==entry]
    if len(i0)==0: return None
    i0=i0[0]
    ep=g.at[i0,'Close']
    if not (ep>0): return None
    n=len(g)
    # baseline
    b_exit_i=None; b_reason=None
    for k in range(1, hold_days+1):
        i=i0+k
        if i>=n: b_exit_i=n-1; b_reason='EOD'; break
        px=g.at[i,'Close']; ret=px/ep-1
        if k>=min_hold and stop_loss is not None and ret<=stop_loss:
            b_exit_i=i; b_reason='STOP'; break
        if k==hold_days:
            b_exit_i=i; b_reason='TIME'; break
    if b_exit_i is None: b_exit_i=min(i0+hold_days,n-1); b_reason='TIME'
    b_ret=g.at[b_exit_i,'Close']/ep-1; b_hold=b_exit_i-i0
    out=dict(ticker=tk,entry=entry,ep=ep,b_exit=g.at[b_exit_i,'time'],b_ret=b_ret,b_hold=b_hold,b_reason=b_reason)
    if sigcol is None: return out
    # candidate: baseline OR earlier signal exit (exec next-session open)
    c_exit_i=b_exit_i; c_reason=b_reason; c_ret=b_ret; c_exec_px=g.at[b_exit_i,'Close']
    for k in range(1, b_hold+1):          # scan only within baseline holding window
        i=i0+k
        if i>=n: break
        px=g.at[i,'Close']; ret=px/ep-1
        if k>=min_hold and stop_loss is not None and ret<=stop_loss:
            break  # hard-stop reached first at same point as baseline; no earlier signal exit before it
        if k>=min_hold and bool(g.at[i,sigcol]):
            # execute next session open
            j=i+1
            if j<n:
                c_exec_px=g.at[j,'Open'] if g.at[j,'Open']>0 else g.at[j,'Close']
                c_exit_i=j
            else:
                c_exec_px=g.at[i,'Close']; c_exit_i=i
            c_reason='SIGNAL'; c_ret=c_exec_px/ep-1
            break
    out['c_exit']=g.at[c_exit_i,'time']; out['c_ret']=c_ret; out['c_hold']=c_exit_i-i0; out['c_reason']=c_reason
    # forward return from candidate-exit to baseline-exit (what candidate gave up / dodged), on Close
    if c_reason=='SIGNAL':
        fwd=g.at[b_exit_i,'Close']/c_exec_px-1
        out['fwd_after_exit']=fwd   # >0 = candidate cut a winner short; <0 = candidate dodged drawdown
    else:
        out['fwd_after_exit']=np.nan
    return out

def run(entry_df, hold_days, stop_loss, min_hold, sigcol, label):
    rows=[sim_deal(r.ticker,r.entry,hold_days,stop_loss,min_hold,sigcol) for r in entry_df.itertuples()]
    rows=[x for x in rows if x is not None]
    return pd.DataFrame(rows)

def daily_nav(df, ret_col, exit_col, start, end):
    """Equal-weight active-deal daily return, renormalized to active set (fully invested in held deals).
    Approx: spread each deal's total return uniformly (geometric) across its holding calendar days."""
    # build daily contribution: for each deal, per-calendar-day the active flag; portfolio ret = mean of per-deal daily rets
    # Use per-deal daily close path
    days=pd.bdate_range(start,end)
    # too heavy per-day; instead compute a simple compounded 1/N-slot NAV via non-overlap approx below (report per-deal instead)
    return None

if __name__=='__main__':
    print("\nloaded deals:",deals.book.value_counts().to_dict())
    pd.to_pickle(pan_by,"/tmp/pan_by.pkl")
    print("READY")
