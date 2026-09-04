import pandas as pd, numpy as np, os, bisect
W = os.path.dirname(os.path.abspath(__file__))
rat = pd.read_csv(f"{W}/fa_ratings_8l.csv", parse_dates=["eff_date"]).sort_values(["ticker","eff_date"])
rat_by_tk = {tk: (g["eff_date"].tolist(), g["rating"].tolist()) for tk, g in rat.groupby("ticker")}
def rating_asof(tk, d):
    e = rat_by_tk.get(tk)
    if not e: return np.nan
    i = bisect.bisect_right(e[0], d) - 1
    return e[1][i] if i >= 0 else np.nan
q = pd.read_csv(f"{W}/quarterly_panel.csv", parse_dates=["q"])
qtrs = sorted(q["q"].unique())
rows = []
for qd in qtrs:
    day = q[q["q"] == qd]
    n_rating_ok = sum(1 for r in day.itertuples() if (lambda rt: pd.notna(rt) and rt<=3)(rating_asof(r.ticker, pd.Timestamp(qd))))
    n_both = sum(1 for r in day.itertuples()
                 if (lambda rt: pd.notna(rt) and rt<=3)(rating_asof(r.ticker, pd.Timestamp(qd)))
                 and pd.notna(r.roe_min3y) and r.roe_min3y>=0 and pd.notna(r.cfo_ttm) and r.cfo_ttm>0)
    rows.append({"q": qd, "n_rating_ok": n_rating_ok, "n_both": n_both})
df = pd.DataFrame(rows)
df.to_csv(f"{W}/capacity_by_quarter.csv", index=False)
print(df.tail(20).to_string(index=False))
print(f"\nmedian n_rating_ok={df.n_rating_ok.median():.0f}  median n_both={df.n_both.median():.0f}  "
      f"median shrink={100*(1-df.n_both/df.n_rating_ok.replace(0,np.nan)).median():.1f}%")
print(f"quarters with n_both < 30 (top_n): {(df.n_both<30).sum()}/{len(df)}")
