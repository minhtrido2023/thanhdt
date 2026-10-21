# -*- coding: utf-8 -*-
"""Q3: quyền mua có ex-date trong cửa sổ giữ LAG (entry R+5 → R+30). adj lý thuyết, tiền cần, lỗ nếu bỏ quyền."""
import numpy as np, pandas as pd
w = pd.read_csv("q3_rights_inwin.csv", parse_dates=["Release_Date", "entry", "exit30", "exright_date"])
# dedup: same event & same exright with multiple rows -> keep max ratio row (inspect titles separately)
w = w.sort_values("exercise_ratio").drop_duplicates(["ticker", "Release_Date", "exright_date"], keep="last")
px = pd.read_csv("q3_px.csv", parse_dates=["time"]).sort_values("time")
pxb = {tk: g.set_index("time") for tk, g in px.groupby("ticker")}
rows = []
for r in w.itertuples():
    g = pxb[r.ticker]
    before = g[g.index < r.exright_date]; on = g[g.index >= r.exright_date]
    if before.empty or on.empty: continue
    P, Pex = before.Price.iloc[-1], on.Price.iloc[0]
    C1, C0 = before.Close.iloc[-1], on.Close.iloc[0]
    Pent = g[g.index >= r.entry].Price.iloc[0]
    rr, K = r.exercise_ratio, r.K
    out = {"ticker": r.ticker, "Release_Date": r.Release_Date.date(), "entry": r.entry.date(),
           "exright": r.exright_date.date(), "r": rr, "K": K, "P_prev": P, "P_entry": Pent,
           "raw_ex_ret": Pex / P - 1, "adj_close_ex_ret": C0 / C1 - 1, "y_ex": r.y_ex}
    if np.isfinite(K):
        terp = (P + rr * K) / (1 + rr)
        out["adj_theo"] = terp / P - 1                      # (b)  = −r(P−K)/((1+r)P)
        out["cash_per_pos"] = rr * K / Pent                 # (c)  cash need / position value at entry
        out["K_over_P"] = K / P
    rows.append(out)
q = pd.DataFrame(rows)
q.to_csv("q3_rights_table.csv", index=False)
n = len(q); nK = q.adj_theo.notna().sum()
print("events with rights ex in window:", n, "| with K:", int(nK), "| release dates:", q.Release_Date.nunique())
print("(b) adj_theo % quantiles:", (q.adj_theo.quantile([.1, .25, .5, .75, .9]) * 100).round(1).tolist())
print("    K/P quantiles:", q.K_over_P.quantile([.1, .5, .9]).round(2).tolist(), " K>P (quyền vô giá trị):", int((q.K_over_P > 1).sum()))
print("    raw Price ret on ex (median %):", round(q.raw_ex_ret.median() * 100, 1), " adj Close ret on ex (median %):", round(q.adj_close_ex_ret.median() * 100, 1))
print("    corr(raw_ex_ret, adj_theo):", round(q[["raw_ex_ret", "adj_theo"]].corr().iloc[0, 1], 2))
for slot in (0.08, 0.10):
    c = q.cash_per_pos * slot * 100
    print(f"(c) slot {slot:.0%}: tiền cần %NAV quantiles [10,50,90,max]:", c.quantile([.1, .5, .9]).round(2).tolist(), round(c.max(), 2))
    loss = -q.adj_theo * slot * 100
    print(f"(d) slot {slot:.0%}: lỗ nếu bỏ quyền %NAV quantiles [10,50,90,max]:", loss.quantile([.1, .5, .9]).round(2).tolist(), round(loss.max(), 2))
    yrs = (pd.Timestamp("2026-09-30") - pd.Timestamp("2014-01-01")).days / 365.25
    print(f"(e) slot {slot:.0%}: tổng lỗ bỏ quyền {loss.sum():.2f}%NAV trên {yrs:.1f} năm ⇒ ~{loss.sum()/yrs:.3f}pp/năm (CHẶN TRÊN, ước lượng)")
print("cash per position (% vị thế) quantiles:", (q.cash_per_pos.quantile([.1, .5, .9]) * 100).round(1).tolist(), "max", round(q.cash_per_pos.max() * 100, 1))
print("per-year count:", pd.Series(pd.to_datetime(q.entry).dt.year).value_counts().sort_index().to_dict())
print(q.sort_values("adj_theo").head(8)[["ticker", "entry", "exright", "r", "K", "P_prev", "adj_theo", "cash_per_pos"]].round(3).to_string(index=False))
