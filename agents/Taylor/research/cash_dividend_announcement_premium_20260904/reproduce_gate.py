"""
Independent reproduction of the regime-conditioned cash-dividend pre-ex gate
(dispatch Taylor_20260904_111503, follow-up to Mike's exploratory
regime_conditioned_gate_mike_20260904.md, corrected DT5G mapping).

Mapping (macro_state_live.py:42 + BQ vnindex_5state_dt5g_live, verified):
1=CRISIS, 2=BEAR, 3=NEUTRAL, 4=BULL, 5=EXBULL.
"""
import sys, os
import pandas as pd, numpy as np
from scipy import stats

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from deposit_rate_vn import merge_deposit

REGIME_MAP = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EXBULL"}

df = pd.read_csv("raw_events.csv", parse_dates=["ex_date", "t28", "t15", "t14", "t1"])
n0 = len(df)
df = df.dropna(subset=["c28", "c15", "c14", "c1", "v28", "v15", "v14", "v1"])
n1 = len(df)
df = df[(df[["c28", "c15", "c14", "c1"]] > 0).all(axis=1)]
print(f"dropped {n0-n1} rows missing boundary price/index; dropped {n1-len(df)} more zero/neg price; N={len(df)}")

df["pre_ex_ret"] = df["c1"] / df["c14"] - 1
df["baseline_ret"] = df["c15"] / df["c28"] - 1
df["vnindex_pre_ex_ret"] = df["v1"] / df["v14"] - 1
df["abnormal_return"] = df["pre_ex_ret"] - df["baseline_ret"] - df["vnindex_pre_ex_ret"]

cash_all = df[df["grp"] == "CASH"].copy().sort_values("ex_date")
stock_all = df[df["grp"] == "STOCK_DIV"].copy()

# prior_3y: count of CASH events for same ticker with ex_date in (event.ex_date-1095d, event.ex_date)
# computed on raw (unfiltered by price/yield) CASH history -> ticker's actual dividend track record.
cash_hist = cash_all[["ticker", "ex_date"]].rename(columns={"ex_date": "hist_date"})
prior_counts = []
for tkr, grp in cash_all.groupby("ticker"):
    dates = np.sort(grp["ex_date"].values)
    hist = cash_hist[cash_hist["ticker"] == tkr]["hist_date"].values
    hist = np.sort(hist)
    for d in dates:
        lo = d - np.timedelta64(1095, "D")
        cnt = int(((hist > lo) & (hist < d)).sum())
        prior_counts.append((tkr, d, cnt))
prior_df = pd.DataFrame(prior_counts, columns=["ticker", "ex_date", "prior_3y"])
cash_all = cash_all.merge(prior_df, on=["ticker", "ex_date"], how="left")

# deposit rate PIT at t14 (as-of backward)
cash_all = merge_deposit(cash_all, time_col="t14")
cash_all = cash_all.rename(columns={"deposit_rate": "deposit_rate_pit"})
cash_all["raw_yield"] = cash_all["div_vnd"] / cash_all["c14"]
cash_all["excess"] = cash_all["raw_yield"] * 100 - cash_all["deposit_rate_pit"]

# regime PIT at t14
regime_hist = pd.read_csv("dt5g_state_history.csv", parse_dates=["time"]).sort_values("time")
cash_all = cash_all.sort_values("t14")
cash_all = pd.merge_asof(cash_all, regime_hist, left_on="t14", right_on="time", direction="backward")
cash_all["regime"] = cash_all["state"].map(REGIME_MAP)

# same PIT joins for STOCK_DIV (for same-regime negative control comparison)
stock_all = merge_deposit(stock_all, time_col="t14").rename(columns={"deposit_rate": "deposit_rate_pit"})
stock_all["raw_yield"] = np.nan  # STOCK_DIV has no div_vnd cash yield concept
stock_all = stock_all.sort_values("t14")
stock_all = pd.merge_asof(stock_all, regime_hist, left_on="t14", right_on="time", direction="backward")
stock_all["regime"] = stock_all["state"].map(REGIME_MAP)

# eligible pool: price/yield filter
elig = cash_all[(cash_all["c14"] >= 10000) & (cash_all["raw_yield"] <= 0.50)].copy()
elig = elig.dropna(subset=["regime"])
print(f"\neligible CASH pool (c14>=10000, raw_yield<=0.50, regime not null): N={len(elig)}, date range {elig.ex_date.min().date()}..{elig.ex_date.max().date()}")

sub = elig[(elig["excess"] > 0) & (elig["prior_3y"] >= 3)].copy()
print(f"excess>0 & prior_3y>=3 subset: N={len(sub)}")

stock_elig = stock_all[(stock_all["c14"] >= 10000)].dropna(subset=["regime"]).copy()

print("\n=== Per-regime table (excess>0 & prior_3y>=3) ===")
rows = []
for st in [1, 2, 3, 4, 5]:
    name = REGIME_MAP[st]
    g = sub[sub["state"] == st]
    n = len(g)
    if n == 0:
        rows.append((name, 0, 0, np.nan, np.nan, np.nan))
        continue
    med = g["abnormal_return"].median()
    hit = (g["abnormal_return"] > 0).mean()
    if n >= 5:
        p = stats.wilcoxon(g["abnormal_return"]).pvalue
    else:
        p = np.nan
    ntkr = g["ticker"].nunique()
    rows.append((name, n, ntkr, med, hit, p))
    # same-regime STOCK_DIV comparison (two-sided: direction of any difference is not assumed)
    gs = stock_elig[stock_elig["state"] == st]
    if len(gs) >= 5 and n >= 5:
        u2 = stats.mannwhitneyu(g["abnormal_return"], gs["abnormal_return"], alternative="two-sided")
        print(f"  {name}: N={n} tkr={ntkr} med={med:.4%} hit={hit:.0%} p={p:.3g} | STOCK(N={len(gs)}) med={gs['abnormal_return'].median():.4%} MWU_two-sided_p={u2.pvalue:.3g}")
    else:
        print(f"  {name}: N={n} tkr={ntkr} med={med:.4%} hit={hit:.0%} p={p:.3g} | STOCK N={len(gs)} too thin")

print("\n=== GATE: regime in {CRISIS,BEAR} & excess>0 & prior_3y>=3 & c14>=10000 ===")
gate = sub[sub["state"].isin([1, 2])].copy()
n = len(gate)
med = gate["abnormal_return"].median()
hit = (gate["abnormal_return"] > 0).mean()
p = stats.wilcoxon(gate["abnormal_return"]).pvalue
ntkr = gate["ticker"].nunique()
print(f"N={n}, tickers={ntkr}, median={med:.4%}, hit={hit:.1%}, wilcoxon_p={p:.3g}")
print(f"p5={gate['abnormal_return'].quantile(0.05):.4%}, p95={gate['abnormal_return'].quantile(0.95):.4%}")

# cluster-robust: median per ticker, then test that distribution vs 0
tkr_med = gate.groupby("ticker")["abnormal_return"].median()
cr_med = tkr_med.median()
cr_p = stats.wilcoxon(tkr_med).pvalue if len(tkr_med) >= 5 else np.nan
print(f"cluster-robust (median-of-ticker-medians): median={cr_med:.4%}, N_ticker={len(tkr_med)}, p={cr_p:.3g}")

print("\n--- Bản chặt (excess>4pp) ---")
gate_tight = gate[gate["excess"] > 4]
n2 = len(gate_tight)
med2 = gate_tight["abnormal_return"].median()
hit2 = (gate_tight["abnormal_return"] > 0).mean()
tkr_med2 = gate_tight.groupby("ticker")["abnormal_return"].median()
cr_med2 = tkr_med2.median()
print(f"N={n2}, tickers={gate_tight['ticker'].nunique()}, median={med2:.4%}, hit={hit2:.1%}, cluster-robust median={cr_med2:.4%}")

print("\n--- Dose-response trong gate ---")
for lo, hi, lbl in [(0, 4, "0-4pp"), (4, 8, "4-8pp"), (8, np.inf, ">8pp")]:
    g = gate[(gate["excess"] > lo) & (gate["excess"] <= hi)]
    print(f"  {lbl}: N={len(g)}, median={g['abnormal_return'].median():.4%}")

print("\n--- Split-half ---")
for lbl, cond in [("2014-2019", gate["ex_date"] <= "2019-12-31"), ("2020+", gate["ex_date"] > "2019-12-31")]:
    g = gate[cond]
    p_ = stats.wilcoxon(g["abnormal_return"]).pvalue if len(g) >= 5 else np.nan
    print(f"  {lbl}: N={len(g)}, median={g['abnormal_return'].median():.4%}, p={p_:.3g}")

print("\n--- LOYO: bỏ 2022 ---")
g = gate[gate["ex_date"].dt.year != 2022]
print(f"  N={len(g)}, median={g['abnormal_return'].median():.4%}")
for yr in sorted(gate["ex_date"].dt.year.unique()):
    if yr != 2022:
        gy = gate[gate["ex_date"].dt.year == yr]
        print(f"    excl-others check {yr}: (not excluded) N={len(gy)}")

print("\n=== Kiểm tra thêm 1: Ticker concentration trong gate ===")
tc = gate["ticker"].value_counts()
print(tc.head(10))
print(f"top ticker share = {tc.iloc[0]}/{n} = {tc.iloc[0]/n:.1%}")
print(f"tickers with >3% of N ({0.03*n:.1f} events): {(tc > 0.03*n).sum()}")

gate.to_csv("gate_events_reproduced.csv", index=False)
sub.to_csv("excess_prior_subset_reproduced.csv", index=False)
print("\nSaved gate_events_reproduced.csv, excess_prior_subset_reproduced.csv")
