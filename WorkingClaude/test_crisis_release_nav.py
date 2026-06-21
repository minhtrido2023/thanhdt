# -*- coding: utf-8 -*-
"""
test_crisis_release_nav.py — pure state->VNINDEX-allocation NAV backtest, comparing
the family state machine WITH vs WITHOUT the unconfirmed-CRISIS release overlay.

Reuses the canonical vnindex_5state_system mechanics exactly:
  T+1 delay, RAMP 3, SNAP 3%, TC 0.1%, deposit 6%/yr, borrow 10%/yr, TARGET_W{1..5}.
This isolates the state machine's allocation quality (no stock-book confound).
"""
import sys, io
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from crisis_release import apply_crisis_release, segments, CRISIS

WORK = r"/home/trido/thanhdt/WorkingClaude"
TC, RAMP, SNAP = 0.001, 3, 0.03
DEP, BOR = 0.06/252, 0.10/252
W = {1:0.00, 2:0.20, 3:0.70, 4:1.00, 5:1.30}

vix = pd.read_csv(f"{WORK}/data/VNINDEX.csv", parse_dates=["time"]).sort_values("time")
close_all = vix.set_index("time")["Close"]

def nav(states: pd.Series, close: pd.Series):
    """states & close aligned, sorted. Returns pv array + weight array."""
    s = states.values.astype(int); c = close.values; n = len(s)
    pv = np.zeros(n); pv[0] = 1e9; w = W[3]; warr = np.zeros(n); warr[0] = w
    for t in range(1, n):
        tgt = W.get(int(s[t-1]), 0.70)
        diff = tgt - w
        wn = tgt if abs(diff) < SNAP else w + diff/RAMP
        wn = float(np.clip(wn, 0.0, 1.30))
        r = c[t]/c[t-1]-1 if c[t-1] > 0 else 0.0
        pv[t] = pv[t-1]*(1 + wn*r + max(0,1-wn)*DEP - max(0,wn-1)*BOR - abs(wn-w)*TC)
        w = wn; warr[t] = w
    return pv, warr

def metrics(pv, dates):
    pv = np.asarray(pv); yrs = (dates[-1]-dates[0]).days/365.25
    cagr = (pv[-1]/pv[0])**(1/yrs)-1
    peak = np.maximum.accumulate(pv); dd = pv/peak-1; mdd = dd.min()
    ret = pv[1:]/pv[:-1]-1
    spy = len(pv)/yrs
    sharpe = ret.mean()/ret.std()*np.sqrt(spy) if ret.std()>0 else 0
    calmar = cagr/abs(mdd) if mdd<0 else float('nan')
    return dict(cagr=cagr, mdd=mdd, sharpe=sharpe, calmar=calmar)

def trans(states):
    s = states.values; return int((s[1:] != s[:-1]).sum())

def report(name, st, K, margin, hold):
    st = st[~st.index.duplicated(keep="last")].sort_index()
    close = close_all.reindex(st.index).ffill()
    keep = close.notna()
    st, close = st[keep], close[keep]
    new = apply_crisis_release(st, close, K=K, margin=margin, hold=hold)

    pv_b, _ = nav(st, close); pv_o, _ = nav(new, close)
    dates = st.index
    print(f"\n========== {name}  (overlay K={K} margin={margin:.0%} hold={hold}) ==========")
    print(f"  CRISIS days {int((st==CRISIS).sum())} -> {int((new==CRISIS).sum())}   "
          f"transitions {trans(st)} -> {trans(new)}")
    for lab, lo in [("FULL", dates[0]), ("2011+", pd.Timestamp('2011-01-01')),
                    ("2014+", pd.Timestamp('2014-01-01')), ("2020+", pd.Timestamp('2020-01-01'))]:
        m = dates >= lo
        if m.sum() < 60: continue
        mb = metrics(pv_b[m]/pv_b[m][0], dates[m]); mo = metrics(pv_o[m]/pv_o[m][0], dates[m])
        print(f"  [{lab:5}] base  CAGR={mb['cagr']:6.2%} DD={mb['mdd']:7.2%} Sh={mb['sharpe']:.2f} Cal={mb['calmar']:.2f}"
              f"   |  overlay CAGR={mo['cagr']:6.2%} DD={mo['mdd']:7.2%} Sh={mo['sharpe']:.2f} Cal={mo['calmar']:.2f}"
              f"   | dCAGR={mo['cagr']-mb['cagr']:+.2%}")

def load(name, f, col=None):
    d = pd.read_csv(f"{WORK}/{f}")
    col = col or ("state" if "state" in d.columns else d.columns[1])
    return d.assign(time=pd.to_datetime(d[d.columns[0]])).set_index("time")[col].astype(int)

if __name__ == "__main__":
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    margin = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
    hold = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    report("canonical_TinhTe", load("c", "data/vnindex_5state.csv"), K, margin, hold)
    report("DT_10_25_25",      load("d", "data/vnindex_5state_dt_10_25_25.csv"), K, margin, hold)
    report("v3.4b",            load("v", "data/vnindex_5state_tam_quan_v3_4b_full_history.csv"), K, margin, hold)
    report("DT5G(state_raw)",  load("g", "data/vnindex_5state_dt5g_live.csv", col="state_raw"), K, margin, hold)
