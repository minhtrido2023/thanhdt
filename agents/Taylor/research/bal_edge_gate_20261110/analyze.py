import sys, datetime as dt
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/wt-bal-edge-gate-20261110/WorkingClaude")
import pandas as pd, bal_edge_gate as g
aud = sys.argv[1]
# 1) đối chiếu tái dựng: mọi holding book BAL (kể cả CAPITB) ở cuối tháng vs bal_stocks_ref engine
s_all = g.bal_monthly_series(aud, include_capit=True)
d = s_all.attrs["daily"].set_index("ymd")
ref = d["bal_stocks_ref"].astype(float)
diff = [(r["month"], r["_mv_end"] - ref.loc[pd.Timestamp(r["month_end_session"])]) for r in s_all.to_dict("records")]
ad = pd.Series({m: abs(x) for m, x in diff})
print(f"[recon] tháng={len(ad)}  max|Δ|={ad.max():,.0f} VND  tháng |Δ|>1 VND: {(ad>1).sum()}  (Δ>1: {list(ad[ad>1].index[:8])})")
# 2) chuỗi BAL (loại CAPIT*)
s = g.bal_monthly_series(aud)
today = dt.date(2026, 11, 10)
cm = g.closed_months(s, today)
print(f"[series] tháng có trong audit={len(s)}  tháng đã đóng={len(cm)}  cuối={cm[-1]['month']} ({cm[-1]['month_end_session']})")
n = pd.Series([r["n"] for r in cm]); 
print(f"[n] tháng n=0: {(n==0).sum()}  n<3: {(n<3).sum()}  n>=3: {(n>=3).sum()}  /{len(n)}")
for k in (1, 3, 5):
    st, logs = g.evaluate(None, cm, min_n=k)
    tr = sum(x["transition"] for x in logs); lk = sum(x["state_after"] == "LOCKED" for x in logs)
    print(f"[MIN_N={k}] state cuối={st['state']} since={st['since']}  transitions={tr}  tháng LOCKED={lk}/{len(logs)}")
st, logs = g.evaluate(None, cm)
print("\n12 tháng gần nhất (MIN_N=3):")
for x in logs[-12:]:
    r = "   n/a" if x["ret"] is None else f"{x['ret']*100:+6.2f}%"
    print(f"  {x['month']}  {r}  n={x['n']:2d}  pnl={x['pnl_vnd']/1e6:+9.1f}tr  {x['state_before']}->{x['state_after']} {x['decision']}")
pd.DataFrame(logs).to_csv(sys.argv[2], index=False)
