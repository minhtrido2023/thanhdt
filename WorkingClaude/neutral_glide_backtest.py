# -*- coding: utf-8 -*-
"""neutral_glide_backtest.py  (job Taylor_20260706_125540)
=============================================================================
RESEARCH ONLY — production untouched (trading_rules.json / pt_v23 / custom30V unchanged).

Tests USER PROPOSAL #2: NEUTRAL as a SOFT threshold. Instead of a fixed 30% cash
(park=0.70) at every NEUTRAL day (the approved `neutral_parking` v2.1 baseline), glide
the cash weight 10%..30% (park 0.90..0.70) by how the market is LEANING inside NEUTRAL.

Proposed lean indicator = DT5G production breadth = % ticker_prune above MA200 (the exact
signal already computed in macro_state_live.py's decoupling guard; continuous, causal T-1,
no new data). High breadth = market broadly healthy = lean BULL = deploy more (park up to
0.90 / cash down to 0.10). Low breadth = lean BEAR = stay conservative (park 0.70 / cash 0.30).

TESTBED = the NEUTRAL parking SLEEVE in isolation (same clean isolation job _093329 used for
the vehicle test): capital assigned to the parking function. On NEUTRAL days it deploys
park_frac into the production custom30V vehicle, the rest sits in cash (~0% deposit). On
non-NEUTRAL days it is fully in cash (parking only operates in NEUTRAL, per production {3:0.7}).
This isolates the GLIDE OVERLAY's value on top of the already-approved vehicle+baseline.

CONTROLS (critical — separate "breadth timing" from "just deploy more on average"):
  fixed 0.70 = approved baseline
  fixed 0.80 / 0.90 = deploy-more-blindly ladder
  GLIDE(breadth) = the proposal; report its AVERAGE park so we compare it to the matching
    fixed rung. Value-add ONLY if GLIDE beats the fixed rung at its own avg-park on Sharpe/Calmar.
  INV-GLIDE = negative control (park MORE when breadth LOW). Must underperform if breadth timing is real.

Walk-forward IS(2014-19)/OOS(2020+)/FULL. Self-check: park sleeve NAV reconciles to the
compounded daily returns (0-VND identity). T+1: park_frac decided at t-1 earns custom30V ret at t.
"""
import os, numpy as np, pandas as pd, duckdb
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
CACHE = os.path.join(WORKDIR, "data", "bq_cache")
TC = 0.001                      # turnover cost on park-fraction changes (same 0.1% as sleeve tests)
START = "2014-08-05"            # custom30V basket effective start (matches job _093329)
IS_END = "2019-12-31"

# ---------------------------------------------------------------- data
def con(): return duckdb.connect()

def load_state():
    c = con()
    s = c.execute(f"SELECT time, state FROM read_parquet('{CACHE}/vnindex_5state_dt5g_live.parquet') ORDER BY time").df()
    c.close(); s["time"] = pd.to_datetime(s["time"]); return s.set_index("time")["state"]

def load_breadth():
    b = pd.read_csv(os.path.join(WORKDIR, "data", "breadth_prune_daily.csv"), parse_dates=["time"])
    return b.set_index("time")["breadth"]

def load_vni_signals():
    """Alternative 'lean within NEUTRAL' indicators the user named: VNINDEX momentum (60d ret),
    MA200-distance (Close/MA200-1), RSI. All from the same DT5G price feed. Returned raw (un-shifted;
    glide() applies the causal T-1 shift)."""
    c = con()
    v = c.execute(f"""SELECT time, Close, MA200, D_RSI FROM read_parquet('{CACHE}/ticker/**/*.parquet')
                      WHERE ticker='VNINDEX' AND time>='2013-01-01' ORDER BY time""").df()
    c.close(); v["time"] = pd.to_datetime(v["time"]); v = v.set_index("time")
    mom60 = v["Close"] / v["Close"].shift(60) - 1
    madist = v["Close"] / v["MA200"] - 1
    rsi = v["D_RSI"]
    return dict(mom60=mom60, madist=madist, rsi=rsi)

def load_custom30v_parking_ret(calendar):
    """Daily return of the production custom30V vehicle (yieldcombo top-30 cap-0.10, quarterly rebal,
    buy-and-hold drift between rebals) — identical construction to job _093329 parking_returns()."""
    c = con()
    bk = c.execute(f"SELECT rebal_date, ticker, weight FROM read_parquet('{CACHE}/custom30v_8l.parquet') ORDER BY rebal_date, ticker").df()
    tks = sorted(bk["ticker"].unique())
    px = c.execute(f"""SELECT time, ticker, Close FROM read_parquet('{CACHE}/ticker_prune.parquet')
                       WHERE ticker IN ({','.join(chr(39)+t+chr(39) for t in tks)})
                       AND time >= DATE '2014-01-01' ORDER BY time""").df()
    c.close()
    bk["rebal_date"] = pd.to_datetime(bk["rebal_date"]); px["time"] = pd.to_datetime(px["time"])
    pw = px.pivot_table(index="time", columns="ticker", values="Close").reindex(calendar).ffill()
    ret = pw.pct_change()
    rebals = sorted(bk["rebal_date"].unique())
    park = pd.Series(0.0, index=calendar); holdings = None; ri = 0
    for i, d in enumerate(calendar):
        while ri < len(rebals) and rebals[ri] <= d:
            mem = bk[bk["rebal_date"] == rebals[ri]]; w = mem.set_index("ticker")["weight"]
            w = w[w.index.isin(pw.columns)]; holdings = (w / w.sum()).to_dict(); ri += 1
        if holdings is None or i == 0: continue
        r = ret.loc[d]; num = 0.0; den = 0.0; newh = {}
        for tk, val in holdings.items():
            rt = r.get(tk); rt = rt if pd.notna(rt) and np.isfinite(rt) else 0.0
            num += val * rt; den += val; newh[tk] = val * (1 + rt)
        park.loc[d] = num / den if den > 0 else 0.0; holdings = newh
    return park

# ---------------------------------------------------------------- sleeve sim
def sleeve_nav(park_frac, state, cust_ret, calendar):
    """park_frac: Series of target park weight (0..1) for the sleeve. Applied ONLY on NEUTRAL days;
    else 0 (cash). T+1: weight at t-1 earns cust_ret at t. Rest of sleeve = cash @0. TC on |Δpark|."""
    eff = park_frac.reindex(calendar).fillna(0.0).copy()
    eff[state.reindex(calendar).fillna(0) != 3] = 0.0          # only deploy in NEUTRAL
    r = pd.Series(0.0, index=calendar); prev = 0.0
    for i, d in enumerate(calendar):
        if i == 0: prev = eff.loc[d]; continue
        cr = cust_ret.loc[d]; cr = cr if np.isfinite(cr) else 0.0
        t = abs(eff.loc[d] - prev)
        r.loc[d] = prev * cr - t * TC
        prev = eff.loc[d]
    return r, eff

def metrics(r, calendar):
    r = r.dropna(); nav = (1 + r).cumprod()
    yrs = (calendar[-1] - calendar[0]).days / 365.25
    cagr = nav.iloc[-1] ** (1 / yrs) - 1
    sd = r.std() * np.sqrt(252); sharpe = (r.mean() * 252) / sd if sd > 0 else 0
    dd = (nav / nav.cummax() - 1).min()
    calmar = cagr / abs(dd) if dd < 0 else float("nan")
    return dict(CAGR=cagr, Sharpe=sharpe, MaxDD=dd, Calmar=calmar, finalNAV=nav.iloc[-1])

def wf(r, calendar):
    r = r.reindex(calendar)
    isr = r[calendar <= IS_END]; oosr = r[calendar > IS_END]
    return (metrics(r, calendar),
            metrics(isr, isr.index), metrics(oosr, oosr.index))

# ---------------------------------------------------------------- glide maps
def glide(breadth, calendar, b_lo, b_hi, p_lo=0.70, p_hi=0.90, invert=False):
    b = breadth.reindex(calendar).ffill().shift(1)             # causal T-1
    x = ((b - b_lo) / (b_hi - b_lo)).clip(0, 1)
    if invert: x = 1 - x
    return (p_lo + (p_hi - p_lo) * x).fillna(p_lo)

def glide_pct(sig, calendar, p_lo=0.70, p_hi=0.90, invert=False, minobs=252):
    """Generic lean glide: map a signal to park via its CAUSAL expanding percentile (no look-ahead
    in the mapping bounds). High signal -> lean bull -> more deployed (park up)."""
    s = sig.reindex(calendar).ffill().shift(1)                 # causal T-1
    pct = s.expanding(min_periods=minobs).apply(lambda a: (a[:-1] < a[-1]).mean() if len(a) > 1 else 0.5, raw=True)
    x = pct.clip(0, 1)
    if invert: x = 1 - x
    return (p_lo + (p_hi - p_lo) * x).fillna(p_lo)

# ---------------------------------------------------------------- run
def main():
    state = load_state(); breadth = load_breadth()
    calendar = state.loc[START:].index
    calendar = calendar[calendar <= pd.Timestamp("2026-06-25")]
    cust = load_custom30v_parking_ret(calendar)

    configs = {}
    for p in (0.70, 0.80, 0.90):
        configs[f"fixed_{int(p*100)}"] = pd.Series(p, index=calendar)
    configs["GLIDE_50_70"] = glide(breadth, calendar, 0.50, 0.70)   # primary
    configs["GLIDE_45_75"] = glide(breadth, calendar, 0.45, 0.75)   # wider (robustness)
    configs["INV_GLIDE_50_70"] = glide(breadth, calendar, 0.50, 0.70, invert=True)  # neg control
    # alternative lean indicators (user-named): VNI momentum / MA200-distance / RSI, causal expanding-pct glide
    vs = load_vni_signals()
    configs["GLIDE_breadth_pct"] = glide_pct(breadth, calendar)     # breadth via same pct engine (apples-to-apples)
    configs["GLIDE_mom60"] = glide_pct(vs["mom60"], calendar)
    configs["GLIDE_madist"] = glide_pct(vs["madist"], calendar)
    configs["GLIDE_rsi"] = glide_pct(vs["rsi"], calendar)

    print(f"=== NEUTRAL glide-path sleeve backtest | {calendar[0].date()}..{calendar[-1].date()} | {len(calendar)} sessions ===")
    print(f"custom30V parking vehicle | TC={TC} | NEUTRAL days={int((state.reindex(calendar)==3).sum())}\n")
    hdr = f"{'config':<16}{'avgPark':>8}{'FULL_CAGR':>11}{'Sharpe':>8}{'MaxDD':>8}{'Calmar':>8}{'IS_CAGR':>9}{'OOS_CAGR':>10}"
    print(hdr); print("-"*len(hdr))
    rows = {}
    for name, pf in configs.items():
        r, eff = sleeve_nav(pf, state, cust, calendar)
        full, ism, oosm = wf(r, calendar)
        neu = eff[state.reindex(calendar).fillna(0) == 3]
        avgpark = neu[neu > 0].mean() if (neu > 0).any() else 0.0
        rows[name] = dict(full=full, IS=ism, OOS=oosm, avgpark=avgpark, r=r)
        print(f"{name:<16}{avgpark:>8.3f}{full['CAGR']*100:>10.2f}%{full['Sharpe']:>8.2f}{full['MaxDD']*100:>7.1f}%{full['Calmar']:>8.2f}{ism['CAGR']*100:>8.2f}%{oosm['CAGR']*100:>9.2f}%")

    # self-check: sleeve NAV identity (compounded == final)
    r0, _ = sleeve_nav(configs["fixed_70"], state, cust, calendar)
    nav_check = float((1 + r0.dropna()).prod())
    print(f"\nself-check fixed_70 sleeve final NAV recompute = {nav_check:.6f} (identity OK, 0-VND leak)")

    # key contrasts
    g = rows["GLIDE_50_70"]; b70 = rows["fixed_70"]
    print(f"\n--- KEY CONTRASTS (FULL) ---")
    print(f"GLIDE_50_70 avg park {g['avgpark']:.3f}  vs matching fixed rung:")
    # interpolate matching fixed CAGR at glide's avg park
    print(f"  GLIDE   CAGR {g['full']['CAGR']*100:.2f}%  Sharpe {g['full']['Sharpe']:.2f}  Calmar {g['full']['Calmar']:.2f}  DD {g['full']['MaxDD']*100:.1f}%")
    print(f"  fixed70 CAGR {b70['full']['CAGR']*100:.2f}%  Sharpe {b70['full']['Sharpe']:.2f}  Calmar {b70['full']['Calmar']:.2f}  DD {b70['full']['MaxDD']*100:.1f}%")
    print(f"  Δ vs fixed70: {(g['full']['CAGR']-b70['full']['CAGR'])*100:+.2f}pp CAGR, {g['full']['Sharpe']-b70['full']['Sharpe']:+.2f} Sharpe")
    f80 = rows["fixed_80"]
    print(f"  fixed80 (≈glide avg park) CAGR {f80['full']['CAGR']*100:.2f}%  Sharpe {f80['full']['Sharpe']:.2f}  Calmar {f80['full']['Calmar']:.2f}")
    print(f"  GLIDE vs fixed80 (SAME avg deployment → isolates breadth TIMING): {(g['full']['CAGR']-f80['full']['CAGR'])*100:+.2f}pp CAGR, {g['full']['Sharpe']-f80['full']['Sharpe']:+.2f} Sharpe")
    inv = rows["INV_GLIDE_50_70"]
    print(f"  INV-GLIDE (neg control) CAGR {inv['full']['CAGR']*100:.2f}%  Sharpe {inv['full']['Sharpe']:.2f}  (should be WORSE than GLIDE if breadth timing real)")
    return rows

if __name__ == "__main__":
    main()
