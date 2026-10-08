"""Mechanism diagnosis: treatment vs control BAL book — starts, size at start, exit mix, BULL cash, 2021."""
import pandas as pd, numpy as np, glob
D = "/home/trido/thanhdt/WorkingClaude/data/"
def L(tag): return pd.read_csv(glob.glob(D + f"*_exp_{tag}_univpit.csv")[0], low_memory=False)
for tag in ["bmx_ctl_off", "bmx_m16_off", "bmx_m20_off"]:
    df = L(tag); d = df[df.record_type == "DAILY"].copy(); d["ymd"] = pd.to_datetime(d.ymd)
    for c in ["state", "nav_bal_ref", "bal_cash_ref", "nav_lag_ref"]: d[c] = pd.to_numeric(d[c])
    tx = df[df.record_type == "TX"]; b = tx[tx.book == "BAL"].copy(); b["ymd"] = pd.to_datetime(b.ymd)
    a = pd.read_csv(f"slot_audit_{tag.replace('bmx_', '')}.csv", parse_dates=["ymd"]); a = a[a.book == "v23audit_BAL"]
    fs = a[a.outcome == "FILL_START"].copy(); fs["w"] = fs.target / fs.cur_nav
    bull = d[d.state.isin([4, 5])]
    nav = d.set_index("ymd").nav_bal_ref
    r21 = nav[nav.index.year == 2021].iloc[-1] / nav[nav.index.year == 2020].iloc[-1] - 1
    sells = b[b.action == "sell"]; sells = sells.assign(pnl=pd.to_numeric(sells.sell_amount) )
    print(f"{tag}: LAG navT {d.nav_lag_ref.iloc[-1]/1e9:.4f}B | BAL navT {d.nav_bal_ref.iloc[-1]/1e9:.2f}B | starts {len(fs)}"
          f" (BULL/EX {fs.state.isin([4,5]).sum()}) | start w med {fs.w.median():.3f}, share w<5% {(fs.w<0.05).mean():.2f}"
          f" | BAL 2021 {r21*100:.1f}% | BAL cash/NAV BULL+EX {(bull.bal_cash_ref/bull.nav_bal_ref).mean():.3f}"
          f" | exits {sells.reason.value_counts().to_dict()}")
    fs.assign(yr=fs.ymd.dt.year).query("yr==2021").groupby("play_type").size().pipe(lambda s: print("   2021 starts by tier:", s.to_dict()))
