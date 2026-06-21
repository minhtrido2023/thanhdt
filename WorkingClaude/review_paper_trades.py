# -*- coding: utf-8 -*-
"""
review_paper_trades.py
======================
Review hop nhat 3 paper-trade overlay phai sinh (chay tai moc 30/06 va 31/08/2026).
Doc cac log/status do tracker daily ghi, in bao cao tong + goi y quyet dinh.
Chay: python review_paper_trades.py
"""
import sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd
WD = r"/home/trido/thanhdt/WorkingClaude"

def load_json(name):
    p=os.path.join(WD,"data",name)
    if not os.path.exists(p): return None
    try:
        with open(p,encoding="utf-8") as f: return json.load(f)
    except Exception: return None
def load_csv(name):
    p=os.path.join(WD,"data",name)
    return pd.read_csv(p) if os.path.exists(p) else None

def sharpe(r):
    r=np.asarray(r,float); sd=r.std()
    return r.mean()/sd*np.sqrt(252) if sd>0 and len(r)>1 else 0
def maxdd(nav):
    nav=np.asarray(nav,float); return float((nav/np.maximum.accumulate(nav)-1).min()) if len(nav) else 0

print("="*86)
print("  REVIEW PAPER-TRADE PHAI SINH (overlay VN30F)")
print("="*86)

# ---- 1) Vol-spike hedge cho V5 ----
print("\n[1] 🛡️ VOL-SPIKE HEDGE cho V5")
s=load_json("vol_spike_hedge_status.json"); log=load_csv("vol_spike_hedge_pt_log.csv")
if s and s.get("window_started") and log is not None:
    on=int(log["sig_held"].sum()) if "sig_held" in log else 0
    print(f"    {s['n_days']} phien | hedge ON {on} phien | co hom nay: {'ON' if s['signal_on'] else 'OFF'}")
    print(f"    V5 only {s['v5_only_ret']*100:+.2f}%  vs  V5+hedge {s['v5_hedged_ret']*100:+.2f}%  "
          f"(dong gop {s['hedge_pp']:+.2f}pp)")
    print(f"    => Danh gia: hedge co kich hoat khong? Co cat duoc DD nao khong? Neu thi truong em ca ky -> du kien ~0 (dung thiet ke).")
else:
    print(f"    Chua co du lieu (window_started={s.get('window_started') if s else 'no status'}).")

# ---- 2) F-system sleeve ----
print("\n[2] ⚙️ F-SYSTEM sleeve (DT5G+Van)")
s=load_json("f_sleeve_status.json"); log=load_csv("f_sleeve_pt_log.csv")
if s and s.get("window_started") and log is not None and len(log)>1:
    sh=sharpe(log["sleeve_ret"]); dd=maxdd((1+log["sleeve_ret"]).cumprod())
    print(f"    {s['n_days']} phien | return {s['sleeve_ret']*100:+.2f}% | Sharpe {sh:.2f} | MaxDD {dd*100:.1f}%")
    print(f"    Vi the hien tai: {s['side']} {s['reco_contracts']} HD (DT5G={s['state_name']})")
    print(f"    => So voi backtest (Sharpe ~0.90, MaxDD ~-21%): live co bam khong?")
else:
    print(f"    Chua du du lieu (n_days={s.get('n_days') if s else 'no status'}).")

# ---- 3) ORB intraday ----
print("\n[3] 📈 ORB intraday VN30F")
s=load_json("orb_pt_status.json"); log=load_csv("orb_pt_log.csv")
if s and s.get("window_started") and log is not None and len(log)>1:
    sh=sharpe(log["net"]); dd=maxdd((1+log["net"]).cumprod()); wr=(log["net"]>0).mean()
    longn=(log["sig"]>0).sum(); shortn=(log["sig"]<0).sum()
    print(f"    {s['n_days']} phien | cum {s['cum_ret']*100:+.2f}% | WR {wr*100:.0f}% | Sharpe {sh:.2f} | MaxDD {dd*100:.1f}%")
    print(f"    Long {longn} / Short {shortn} phien")
    print(f"    => So voi backtest (Sharpe ~1.4-1.6 net thuc te, duong moi nam): live co bam? Slippage thuc te ra sao?")
else:
    print(f"    Chua du du lieu (n_days={s.get('n_days') if s else 'no status'}).")

print("\n"+"="*86)
print("  CHECKLIST QUYET DINH")
print("="*86)
print("""  - Vol-spike hedge V5: co kich hoat dung luc vol bung? Co gay nhieu/ton khi nhan roi?
  - F-sleeve DT5G+Van: live-vs-backtest gap? Co whipsaw bat thuong?
  - ORB intraday: Sharpe live co bam backtest? Slippage thuc te (so voi gia thiet 1tick)?
    WR ~52-55%? Co nam/thang nao am bat thuong?
  - Quyet dinh: (a) tiep tuc paper; (b) tang/giam size; (c) go-live tien that; (d) dung.""")
print("\nDone.")
