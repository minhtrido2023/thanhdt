"""A4 việc 1: phân rã Δ(L3P - K_L3) theo năm + theo deal. Usage: decomp.py bq.csv pit.csv"""
import sys, pandas as pd, numpy as np
def load(p):
    X = pd.read_csv(p, low_memory=False); X["ymd"] = pd.to_datetime(X["ymd"].astype(str).str[:10], errors="coerce"); return X
A, B = load(sys.argv[1]), load(sys.argv[2])
def nav(X): return X[X.record_type=="DAILY"].set_index("ymd").sort_index()["combined_nav"].astype(float)
na, nb = nav(A), nav(B)
print("== lợi suất theo năm (bq | pit | Δpp), đóng góp vào Δ log-NAV cuối kỳ")
ya, yb = na.groupby(na.index.year).last(), nb.groupby(nb.index.year).last()
ra = ya.pct_change(); ra.iloc[0]=ya.iloc[0]/na.iloc[0]-1; rb = yb.pct_change(); rb.iloc[0]=yb.iloc[0]/nb.iloc[0]-1
tot = np.log(nb.iloc[-1]/na.iloc[-1])
for y in ya.index:
    d = np.log(1+rb[y])-np.log(1+ra[y]); print(f" {y}: {ra[y]*100:6.1f} | {rb[y]*100:6.1f} | {100*(rb[y]-ra[y]):+5.1f}pp | dlogNAV {d:+.4f}")
print(f" Σ dlog = {sum(np.log(1+rb[y])-np.log(1+ra[y]) for y in ya.index):+.4f}  (log NAV cuối pit/bq = {tot:+.4f})")
T = lambda X: X[X.record_type=="TX"]
for bk in ("LAG","BAL"):
    for nm,X in (("bq",A),("pit",B)):
        t=T(X); t=t[t.book.astype(str)==bk]; print(f" {bk} {nm}: buy {int((t.action=='buy').sum())} sell {int((t.action=='sell').sum())} | Σbuy {t.buy_amount.astype(float).sum()/1e9:.1f}B")
