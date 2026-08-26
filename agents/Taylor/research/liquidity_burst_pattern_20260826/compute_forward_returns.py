"""
Step 3 — forward return / accumulation-vs-distribution analysis for LBC events.
dispatch Taylor_20260826_120750
"""
import pandas as pd
import numpy as np

BASE = "mike/agents/Taylor/research/liquidity_burst_pattern_20260826/"

ev = pd.read_csv(BASE + "lbc_events.csv", parse_dates=["accum_start", "accum_end", "cat_date", "cat_month", "burst_month"])
px = pd.read_csv(BASE + "lbc_ticker_prices.csv", parse_dates=["time"])
px = px.dropna(subset=["Close"]).sort_values(["ticker", "time"]).reset_index(drop=True)

def get_px(tkr, target_date, tolerance_days=10):
    g = px[px.ticker == tkr]
    if g.empty:
        return None, None, None
    idx = (g["time"] - target_date).abs().idxmin()
    row = g.loc[idx]
    if abs((row["time"] - target_date).days) > tolerance_days:
        return None, None, None
    return row["Close"], row["VNINDEX"], row["time"]

def px_offset(tkr, anchor_date, trading_days):
    g = px[px.ticker == tkr].reset_index(drop=True)
    if g.empty:
        return None, None, None
    pos = (g["time"] - anchor_date).abs().idxmin()
    target_pos = pos + trading_days
    if target_pos < 0 or target_pos >= len(g):
        return None, None, None
    row = g.loc[target_pos]
    return row["Close"], row["VNINDEX"], row["time"]

# NOTE (critical): burst confirmation window = catalyst -> catalyst+3mo (~63 trading days).
# Any "forward return" measured from cat_date over a window that OVERLAPS the burst-confirmation
# window is near-TAUTOLOGICAL: ADV_VND = Price x Volume, so a burst in ADV is mechanically
# correlated with a burst in price over the SAME window (events were selected BECAUSE turnover
# value rose 3x). ret_fwd_60/ret_fwd_120 below are kept only as DESCRIPTIVE ("how much of the
# move happened during the phase the pattern is defined by"), never as an alpha claim.
# The only genuine, non-tautological, actionable test is the return measured AFTER burst_month
# (the month ADV first confirmed >=3x) — an investor cannot know the burst happened until that
# data point prints. ret_post_burst_* is the number that matters for Bước 4 exploitability.

records = []
for _, r in ev.iterrows():
    tkr = r["ticker"]
    cat_date = r["cat_date"]
    burst_date = r["burst_month"]
    c_t0, v_t0, d_t0 = px_offset(tkr, cat_date, 0)
    c_tm60, v_tm60, d_tm60 = px_offset(tkr, cat_date, -60)
    c_tp30, v_tp30, d_tp30 = px_offset(tkr, cat_date, 30)
    c_tp60, v_tp60, d_tp60 = px_offset(tkr, cat_date, 60)
    c_tp120, v_tp120, d_tp120 = px_offset(tkr, cat_date, 120)
    # actionable: enter AT burst confirmation, hold forward
    c_b0, v_b0, d_b0 = px_offset(tkr, burst_date, 0)
    c_bp30, v_bp30, d_bp30 = px_offset(tkr, burst_date, 30)
    c_bp60, v_bp60, d_bp60 = px_offset(tkr, burst_date, 60)
    c_bp120, v_bp120, d_bp120 = px_offset(tkr, burst_date, 120)
    if None in (c_t0, c_tm60, c_tp120, v_t0, v_tm60, v_tp120):
        continue
    def ret(c1, c0):
        return (c1 / c0 - 1) if (c0 and c1) else np.nan
    rec = {
        "ticker": tkr, "cat_type": r["cat_type"], "cat_date": cat_date, "burst_date": burst_date,
        "accum_months": r["accum_months"], "burst_multiple": r["burst_multiple"],
        "ret_accum_pre": ret(c_t0, c_tm60),          # T-60 -> T0 (pre-catalyst drift, descriptive)
        "vnindex_ret_accum_pre": ret(v_t0, v_tm60),
        "ret_fwd_30": ret(c_tp30, c_t0) if c_tp30 else np.nan,     # DESCRIPTIVE, tautology risk
        "ret_fwd_60": ret(c_tp60, c_t0) if c_tp60 else np.nan,     # DESCRIPTIVE, tautology risk
        "ret_fwd_120": ret(c_tp120, c_t0),                          # DESCRIPTIVE, tautology risk
        "vnindex_ret_fwd_120": ret(v_tp120, v_t0),
        "ret_post_burst_30": ret(c_bp30, c_b0) if (c_bp30 and c_b0) else np.nan,
        "ret_post_burst_60": ret(c_bp60, c_b0) if (c_bp60 and c_b0) else np.nan,
        "ret_post_burst_120": ret(c_bp120, c_b0) if (c_bp120 and c_b0) else np.nan,
        "vnindex_ret_post_burst_120": ret(v_bp120, v_b0) if (v_bp120 and v_b0) else np.nan,
    }
    rec["excess_ret_fwd_120"] = rec["ret_fwd_120"] - rec["vnindex_ret_fwd_120"]
    rec["excess_ret_accum_pre"] = rec["ret_accum_pre"] - rec["vnindex_ret_accum_pre"]
    rec["excess_ret_post_burst_120"] = (rec["ret_post_burst_120"] - rec["vnindex_ret_post_burst_120"]) \
        if (rec["ret_post_burst_120"] == rec["ret_post_burst_120"] and rec["vnindex_ret_post_burst_120"] == rec["vnindex_ret_post_burst_120"]) else np.nan
    records.append(rec)

res = pd.DataFrame(records)
res.to_csv(BASE + "lbc_forward_returns.csv", index=False)
print(f"N events with full price coverage: {len(res)} (of {len(ev)} raw events)")
print(f"N independent tickers: {res['ticker'].nunique()}")
print(f"N independent years: {res['cat_date'].dt.year.nunique()}")

def manual_ttest_1samp(s):
    s = np.asarray(s, dtype=float)
    n = len(s)
    if n < 2:
        return np.nan, np.nan
    mean = s.mean()
    se = s.std(ddof=1) / np.sqrt(n)
    t = mean / se if se > 0 else np.nan
    # normal approx p-value (two-sided) — adequate for n>30, flagged as approx for smaller n
    from math import erf, sqrt
    p = 2 * (1 - 0.5 * (1 + erf(abs(t) / sqrt(2))))
    return t, p

print("\n=== DESCRIPTIVE (tautology risk — window overlaps burst-detection window) ===")
for col in ["ret_accum_pre", "excess_ret_accum_pre", "ret_fwd_30", "ret_fwd_60", "ret_fwd_120", "excess_ret_fwd_120"]:
    s = res[col].dropna()
    print(f"{col:24s} N={len(s):3d} mean={s.mean()*100:7.1f}% median={s.median()*100:7.1f}% "
          f"pos_rate={(s>0).mean()*100:5.1f}% std={s.std()*100:6.1f}%")

print("\n=== ACTIONABLE (entry AT burst confirmation, hold forward — the real alpha test) ===")
for col in ["ret_post_burst_30", "ret_post_burst_60", "ret_post_burst_120", "excess_ret_post_burst_120"]:
    s = res[col].dropna()
    if len(s) == 0:
        print(f"{col:28s} N=0")
        continue
    print(f"{col:28s} N={len(s):3d} mean={s.mean()*100:7.1f}% median={s.median()*100:7.1f}% "
          f"pos_rate={(s>0).mean()*100:5.1f}% std={s.std()*100:6.1f}%")

s = res["excess_ret_post_burst_120"].dropna()
t, p = manual_ttest_1samp(s)
print(f"\nexcess_ret_post_burst_120 vs 0: N={len(s)} t={t:.2f} p={p:.4f} (approx-normal, raw — NOT corrected for cross-event/year clustering; treat as indicative only, N=91 events from 85 tickers is NOT 91 independent draws)")

# by cat_type
print("\n=== By catalyst type (actionable) ===")
print(res.groupby("cat_type")[["excess_ret_post_burst_120", "ret_post_burst_120"]].agg(["mean", "median", "count"]))

# LOO by year (leave-one-year-out mean stability)
res["year"] = res["cat_date"].dt.year
print("\n=== Mean excess_ret_post_burst_120 by year (event count) ===")
by_year = res.groupby("year")["excess_ret_post_burst_120"].agg(["mean", "count"])
print(by_year)

overall_mean = res["excess_ret_post_burst_120"].mean()
loo = []
for y in res["year"].unique():
    sub = res[res["year"] != y]["excess_ret_post_burst_120"]
    if len(sub.dropna()) > 0:
        loo.append(sub.mean())
print(f"\nOverall mean excess_ret_post_burst_120: {overall_mean*100:.1f}%")
print(f"LOO-by-year range: [{min(loo)*100:.1f}%, {max(loo)*100:.1f}%] (n_years={len(loo)})")
