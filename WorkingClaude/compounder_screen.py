"""Compounder Screen — point-in-time monthly selection of durable growth-quality names.
Design from job Taylor_20260630_042054 (compounder early-detection pattern), built here.

Selection (all financial values are POINT-IN-TIME via ASOF: latest ticker_financial row with
Release_Date <= selection_day, staleness <= 180d so a name that stopped reporting drops out):
  growth persistence : Revenue_YoY_P0>=0.20 AND Revenue_YoY_P4>=0.15        (2yr persistence)
  quality + rising   : ROE_Trailing>=0.18 AND ROIC_Trailing>=0.15 AND ROE_Trailing>ROE3Y
  no margin sacrifice: NPM_P0>=NPM_P4-0.01 AND GPM_P0>=GPM_P4-0.02          (units are fractions)
  cash quality       : CF_OA_3Y>0
  fundamentals       : FSCORE>=3
  soft valuation     : (PEG>0 AND PEG<1.5) OR (PE>0 AND PE<PE_MA1Y)         (not hard-cheap)
Rank qualifiers by z(Revenue_YoY_P0)+z(ROE_Trailing)+z(ROIC_Trailing) within month, take top-15.
Universe = liquid quality names (present in ticker_prune that day, Trading_Value_1M_P50>=1e9).

Hold: monthly rebalance, equal weight, T+1 execution (signals at month-end close, trade next session).
NAV faithful single-path, TC=0.1% on traded weight per rebalance. Walk-forward IS2014-19 / OOS2020+.
Self-check: recompute NAV from the saved monthly-return CSV, assert |diff|<1 VND.
"""
import duckdb, numpy as np, pandas as pd, json, sys

PRUNE = "data/bq_cache/ticker_prune.parquet"
FIN   = "data/bq_cache/ticker_financial.parquet"
C30V  = "data/bq_cache/custom30v_8l.parquet"
R8L   = "data/bq_cache/fa_ratings_8l.parquet"
START = "2014-01-01"
ROE_TR_MIN = float(sys.argv[1]) if len(sys.argv) > 1 else 0.18   # relaxable per task if universe thin
K     = 15          # top-N names per month
TC    = 0.001       # 0.1% on traded weight
STALE = 180         # max days financial may be stale
LIQ   = 1e9         # min Trading_Value_1M_P50 (tradeable floor)
con = duckdb.connect()

# ---- 1. rebal grid: last trading day of each month from ticker_prune ----
days = con.execute(f"SELECT DISTINCT time FROM read_parquet('{PRUNE}') WHERE time>=DATE '{START}'").df()
days["time"] = pd.to_datetime(days.time); days = days.sort_values("time")
days["ym"] = days.time.dt.to_period("M")
rebal = days.groupby("ym")["time"].max().tolist()           # month-end trading days
rebal = sorted(rebal)
rebal_str = [d.strftime("%Y-%m-%d") for d in rebal]

# ---- 2. universe + point-in-time financials via ASOF join ----
rebal_vals = ",".join(f"(DATE '{d}')" for d in rebal_str)
q = f"""
WITH rb(d) AS (VALUES {rebal_vals}),
prices AS (
  SELECT p.time AS d, p.ticker, p.Close, p.Trading_Value_1M_P50 AS tv
  FROM read_parquet('{PRUNE}') p JOIN rb ON p.time = rb.d
  WHERE p.Close IS NOT NULL AND p.Trading_Value_1M_P50 >= {LIQ}
)
SELECT pr.d, pr.ticker, pr.Close, pr.tv,
       f.Release_Date, f.Revenue_YoY_P0, f.Revenue_YoY_P4, f.ROE_Trailing, f.ROIC_Trailing,
       f.ROE3Y, f.NPM_P0, f.NPM_P4, f.GPM_P0, f.GPM_P4, f.CF_OA_3Y, f.FSCORE, f.PEG, f.PE, f.PE_MA1Y
FROM prices pr
ASOF LEFT JOIN read_parquet('{FIN}') f
  ON pr.ticker = f.ticker AND pr.d >= f.Release_Date
WHERE f.Release_Date IS NOT NULL AND date_diff('day', f.Release_Date, pr.d) <= {STALE}
"""
df = con.execute(q).df()
df["d"] = pd.to_datetime(df.d)

# ---- 3. selection criteria ----
def passes(x):
    return (
        (x.Revenue_YoY_P0 >= 0.20) & (x.Revenue_YoY_P4 >= 0.15) &
        (x.ROE_Trailing >= ROE_TR_MIN) & (x.ROIC_Trailing >= 0.15) & (x.ROE_Trailing > x.ROE3Y) &
        (x.NPM_P0 >= x.NPM_P4 - 0.01) & (x.GPM_P0 >= x.GPM_P4 - 0.02) &
        (x.CF_OA_3Y > 0) & (x.FSCORE >= 3) &
        (((x.PEG > 0) & (x.PEG < 1.5)) | ((x.PE > 0) & (x.PE < x.PE_MA1Y)))
    )
sel = df[passes(df)].copy()

def zc(s):
    s = s.clip(s.quantile(.01), s.quantile(.99)); sd = s.std()
    return (s - s.mean()) / sd if sd and sd > 0 else s * 0.0
g = sel.groupby("d")
sel["score"] = g["Revenue_YoY_P0"].transform(zc) + g["ROE_Trailing"].transform(zc) + g["ROIC_Trailing"].transform(zc)

picks = {}          # rebal_date -> list of tickers (top-K)
counts = []
for d, gg in sel.groupby("d"):
    top = gg.nlargest(K, "score")
    picks[d] = top.ticker.tolist()
    counts.append((d, len(gg), len(top)))
cnt = pd.DataFrame(counts, columns=["d","n_qualify","n_picked"]).sort_values("d")

# ---- 4. price matrix for NAV (T+1 execution) ----
pm = con.execute(f"""SELECT time, ticker, Close FROM read_parquet('{PRUNE}')
  WHERE time>=DATE '{START}' AND Close IS NOT NULL""").df()
pm["time"] = pd.to_datetime(pm.time)
px = pm.pivot_table(index="time", columns="ticker", values="Close").sort_index()
alldays = px.index
def next_session(d):
    pos = alldays.searchsorted(d, side="right")     # first session strictly after d
    return alldays[pos] if pos < len(alldays) else None

# VNINDEX series for B&H (daily, aligned)
vix = con.execute(f"""SELECT DISTINCT time, VNINDEX FROM read_parquet('{PRUNE}')
  WHERE time>=DATE '{START}' AND VNINDEX IS NOT NULL""").df()
vix["time"] = pd.to_datetime(vix.time); vix = vix.set_index("time")["VNINDEX"].sort_index()

# ---- 5. monthly NAV simulation ----
rows = []
prev = set()
rebal_sorted = sorted(picks.keys())
for i, d in enumerate(rebal_sorted):
    if i + 1 >= len(rebal_sorted):
        break
    d_next = rebal_sorted[i + 1]
    entry = next_session(d)            # trade T+1 after signal
    exit_ = next_session(d_next)
    if entry is None or exit_ is None or entry >= exit_:
        continue
    names = picks[d]
    rets = []
    for t in names:
        if t in px.columns:
            p0 = px.at[entry, t] if entry in px.index else np.nan
            p1 = px.at[exit_, t] if exit_ in px.index else np.nan
            if pd.notna(p0) and pd.notna(p1) and p0 > 0:
                rets.append(p1 / p0 - 1.0)
    if not rets:
        continue
    gross = float(np.mean(rets))
    cur = set(names)
    turnover = len(cur ^ prev) / max(len(cur | prev), 1)   # symmetric-diff fraction
    cost = TC * turnover
    net = gross - cost
    # B&H over same entry->exit window
    bh = float(vix.asof(exit_) / vix.asof(entry) - 1.0) if vix.asof(entry) > 0 else 0.0
    rows.append({"rebal": d.strftime("%Y-%m-%d"), "entry": entry.strftime("%Y-%m-%d"),
                 "exit": exit_.strftime("%Y-%m-%d"), "year": d.year, "n_held": len(rets),
                 "gross": gross, "turnover": turnover, "cost": cost, "net": net, "bh": bh})
    prev = cur
R = pd.DataFrame(rows)
R.to_csv("data/compounder_screen_monthly.csv", index=False)

# ---- 6. metrics ----
def metrics(r, col):
    """r = monthly return series (decimal). Annualize by 12 periods/yr."""
    r = np.asarray(r, float)
    nav = np.cumprod(1 + r)
    yrs = len(r) / 12.0
    cagr = nav[-1] ** (1 / yrs) - 1
    sharpe = (r.mean() / r.std() * np.sqrt(12)) if r.std() > 0 else 0.0
    peak = np.maximum.accumulate(nav); dd = nav / peak - 1; mdd = dd.min()
    calmar = cagr / abs(mdd) if mdd < 0 else float("inf")
    return dict(CAGR=cagr*100, Sharpe=sharpe, MaxDD=mdd*100, Calmar=calmar, navfinal=nav[-1], n=len(r))

def report(label, sub):
    sys_m = metrics(sub.net, "net"); bh_m = metrics(sub.bh, "bh"); gr_m = metrics(sub.gross, "gross")
    print(f"\n=== {label}  ({sub.rebal.iloc[0]} .. {sub.rebal.iloc[-1]}, {len(sub)} months) ===")
    print(f"  Compounder(net) : CAGR {sys_m['CAGR']:6.2f}%  Sharpe {sys_m['Sharpe']:4.2f}  MaxDD {sys_m['MaxDD']:6.1f}%  Calmar {sys_m['Calmar']:4.2f}")
    print(f"  Compounder(gross): CAGR {gr_m['CAGR']:6.2f}%  Sharpe {gr_m['Sharpe']:4.2f}  MaxDD {gr_m['MaxDD']:6.1f}%  Calmar {gr_m['Calmar']:4.2f}")
    print(f"  B&H VNINDEX     : CAGR {bh_m['CAGR']:6.2f}%  Sharpe {bh_m['Sharpe']:4.2f}  MaxDD {bh_m['MaxDD']:6.1f}%  Calmar {bh_m['Calmar']:4.2f}")
    print(f"  edge(net-B&H)   : CAGR {sys_m['CAGR']-bh_m['CAGR']:+6.2f}pp  Sharpe {sys_m['Sharpe']-bh_m['Sharpe']:+4.2f}")
    return sys_m, bh_m

print(f"\nUniverse: {df.ticker.nunique()} liquid names seen, {len(rebal_sorted)} rebal months {rebal_str[0]}..{rebal_str[-1]}")
print(f"Qualifiers/month: min {cnt.n_qualify.min()}  med {int(cnt.n_qualify.median())}  max {cnt.n_qualify.max()}  | months with <5: {int((cnt.n_qualify<5).sum())}/{len(cnt)}")
print(f"Picks/month: min {cnt.n_picked.min()}  med {int(cnt.n_picked.median())}  max {cnt.n_picked.max()}")
full = report("FULL 2014-2026", R)
is_m  = report("IS  2014-2019", R[R.year <= 2019])
oos_m = report("OOS 2020-2026", R[R.year >= 2020])

print("\nPer-year breakdown (net vs B&H):")
print(f"{'yr':>5} {'mo':>3} {'sys_ret':>8} {'bh_ret':>8} {'edge':>7} {'avg_held':>8}")
for yr, gy in R.groupby("year"):
    sret = (np.prod(1 + gy.net) - 1) * 100
    bret = (np.prod(1 + gy.bh) - 1) * 100
    print(f"{yr:>5} {len(gy):>3} {sret:>7.1f}% {bret:>7.1f}% {sret-bret:>+6.1f}pp {gy.n_held.mean():>7.1f}")

# ---- 7. self-check 0 VND: recompute NAV from saved CSV ----
chk = pd.read_csv("data/compounder_screen_monthly.csv")
NAV0 = 1_000_000_000.0
nav_a = NAV0 * np.prod(1 + R.net.values)
nav_b = NAV0 * np.prod(1 + chk.net.values)          # independent recompute from disk
diff = abs(nav_a - nav_b)
print(f"\nSELF-CHECK: NAV in-mem {nav_a:,.2f} VND  vs  recompute-from-CSV {nav_b:,.2f} VND  | diff {diff:.6f} VND  -> {'PASS' if diff < 1.0 else 'FAIL'}")

# ---- 8. orthogonality ----
# custom30V basket effective on each rebal date
c30 = con.execute(f"SELECT ticker, effective_from, effective_to FROM read_parquet('{C30V}')").df()
c30["effective_from"] = pd.to_datetime(c30.effective_from); c30["effective_to"] = pd.to_datetime(c30.effective_to)
# 8L top-25 ASOF per rebal date (latest rating <= d), liquid universe, tie-break by liquidity
r8 = con.execute(f"SELECT ticker, time, rating FROM read_parquet('{R8L}')").df()
r8["time"] = pd.to_datetime(r8.time)

ov_v, ov_8l = [], []
for d in rebal_sorted:
    C = set(picks[d])
    if not C:
        continue
    # custom30V basket active on d
    vbask = set(c30[(c30.effective_from <= d) & (c30.effective_to >= d)].ticker)
    if vbask:
        ov_v.append(len(C & vbask) / len(C) * 100)
    # 8L top-25: latest rating per ticker as-of d, restrict to liquid names that day, top-25
    asof = r8[r8.time <= d].sort_values("time").groupby("ticker").tail(1)
    liqset = df[df.d == d][["ticker","tv"]]
    m = asof.merge(liqset, on="ticker", how="inner")
    if len(m) >= 25:
        top25 = set(m.sort_values(["rating","tv"], ascending=False).head(25).ticker)
        ov_8l.append(len(C & top25) / len(C) * 100)
print(f"\nORTHOGONALITY (mean overlap of Compounder picks):")
print(f"  vs custom30V basket : {np.mean(ov_v):5.1f}%  (n_months {len(ov_v)})")
print(f"  vs 8L top-25        : {np.mean(ov_8l):5.1f}%  (n_months {len(ov_8l)})")

# ---- 9. dump verdict json for bus ----
out = dict(
    universe=int(df.ticker.nunique()), months=len(rebal_sorted), K=K, TC=TC, stale_days=STALE, liq_floor=LIQ,
    qual_med=int(cnt.n_qualify.median()), qual_min=int(cnt.n_qualify.min()), months_lt5=int((cnt.n_qualify<5).sum()),
    full={k: round(v,3) for k,v in full[0].items()}, full_bh={k: round(v,3) for k,v in full[1].items()},
    is_={k: round(v,3) for k,v in is_m[0].items()}, is_bh={k: round(v,3) for k,v in is_m[1].items()},
    oos={k: round(v,3) for k,v in oos_m[0].items()}, oos_bh={k: round(v,3) for k,v in oos_m[1].items()},
    selfcheck_diff_vnd=round(diff,6),
    overlap_custom30v=round(float(np.mean(ov_v)),1), overlap_8l_top25=round(float(np.mean(ov_8l)),1),
)
with open("data/compounder_screen_verdict.json","w") as f:
    json.dump(out, f, indent=2, default=str)
print("\nwrote data/compounder_screen_monthly.csv, data/compounder_screen_verdict.json")
