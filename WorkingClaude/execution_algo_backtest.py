"""Execution-algo backtest on 1-min intraday data (data/intraday_1m/*.csv, 16 VN names, 2023-09→2026-06).
Question: which execution algo should Mafee use? Measures implementation shortfall (IS, bps vs arrival)
+ fill-rate for PASSIVE_LIMIT / LADDER / TWAP across order sizes (% of day volume) and liquidity tiers.

Specs (from Mafee's execution tree, S70):
  PASSIVE_LIMIT : 1 limit at arrival price; fills only if price comes to you; unfilled -> ATC cross (penalty).
  LADDER        : N=5 limits in a band below arrival (buy); each level fills when touched; unfilled -> ATC.
  TWAP          : K=8 time slices (≈30-min cycles), each marketable (crosses to guarantee fill).
Benchmark = day VWAP. BUY side (sells symmetric). IS_bps>0 = paid more than arrival = worse.

Fill model (1-min OHLCV, no L2): a resting buy limit L fills when bar.low<=L, up to PART*bar.volume/bar
(participation cap -> large orders can't all fill passively). Marketable slice fills at bar VWAP≈(h+l+c)/3.
Spread not modelled in the price path; noted separately (passive captures ~half-spread, TWAP pays it)."""
import os, glob
import numpy as np, pandas as pd

DDIR = "data/intraday_1m"
PART = 0.10            # max fraction of a bar's volume a resting limit can capture
N_LADDER = 5
BAND = 0.004          # ladder band: 0.4% below arrival (buy)
K_TWAP = 8
SAMPLE_EVERY = 3      # sample every 3rd day (speed)

# Liquidity tier by median daily turnover (VND): crude large/mid split
LIQ = {}

def day_bars(df, d):
    return df[df["date"] == d]

HALF_SPREAD_BPS = 6.0     # VN liquid-name half-spread captured by a resting limit fill (favorable)

def sim_passive(bars, arrival, Q):
    """Single limit at arrival; fill when low<=arrival (capture half-spread), capped by participation;
    unfilled -> forced ATC cross at last close. Returns (avg_price, passive_fill_rate)."""
    filled = 0.0; cost = 0.0
    fill_px = arrival * (1 - HALF_SPREAD_BPS / 1e4)   # resting buy fills better than the touch
    for _, b in bars.iterrows():
        if filled >= Q: break
        if b["low"] <= arrival:
            take = min(Q - filled, PART * b["volume"])
            filled += take; cost += take * fill_px
    pr = filled / Q
    if filled < Q:
        take = Q - filled; cost += take * bars["close"].iloc[-1]; filled = Q
    return cost / Q, pr

def sim_ladder(bars, arrival, Q):
    levels = [arrival * (1 - BAND * k / N_LADDER) for k in range(1, N_LADDER + 1)]
    qper = Q / N_LADDER
    fq = [0.0] * N_LADDER; cost = 0.0
    for _, b in bars.iterrows():
        for i, L in enumerate(levels):
            if fq[i] >= qper: continue
            if b["low"] <= L:
                take = min(qper - fq[i], PART * b["volume"])
                fq[i] += take; cost += take * L * (1 - HALF_SPREAD_BPS / 1e4)
    filled = sum(fq); pr = filled / Q
    if filled < Q:
        take = Q - filled; cost += take * bars["close"].iloc[-1]; filled = Q
    return cost / Q, pr

def sim_twap(bars, arrival, Q):
    """K marketable slices; each at slice VWAP, + sqrt market impact growing with order size (pays spread)."""
    n = len(bars)
    if n == 0: return arrival, 1.0
    idx = np.array_split(np.arange(n), K_TWAP)
    qper = Q / K_TWAP; cost = 0.0
    pct = Q / max(bars["volume"].sum(), 1)
    impact = 1 + (8.0 * (pct / 0.05) ** 0.5) / 1e4     # ~8bps at 5% ADV, sqrt-scaled; pays spread+impact
    for grp in idx:
        if len(grp) == 0: continue
        seg = bars.iloc[grp]
        vp = ((seg["high"] + seg["low"] + seg["close"]) / 3)
        px = (vp * seg["volume"]).sum() / max(seg["volume"].sum(), 1)
        cost += qper * px * impact
    return cost / Q, 1.0

rows = []
for f in sorted(glob.glob(f"{DDIR}/*.csv")):
    tk = os.path.basename(f)[:-4]
    df = pd.read_csv(f); df["time"] = pd.to_datetime(df["time"]); df["date"] = df["time"].dt.date
    days = sorted(df["date"].unique())[::SAMPLE_EVERY]
    med_turn = df.groupby("date").apply(lambda x: (x["close"] * x["volume"]).sum()).median()
    tier = "large" if med_turn > 50e9 else "mid"   # >50B/day = large
    for d in days:
        bars = day_bars(df, d)
        if len(bars) < 50: continue
        arrival = bars["open"].iloc[0]
        dayvol = bars["volume"].sum()
        if arrival <= 0 or dayvol <= 0: continue
        vwap = (((bars["high"] + bars["low"] + bars["close"]) / 3) * bars["volume"]).sum() / dayvol
        for pct in (0.01, 0.05, 0.15):
            Q = pct * dayvol
            for algo, fn in (("PASSIVE", sim_passive), ("LADDER", sim_ladder), ("TWAP", sim_twap)):
                avg, fr = fn(bars, arrival, Q)
                rows.append({"ticker": tk, "tier": tier, "pct_adv": pct, "algo": algo,
                             "is_bps": (avg / arrival - 1) * 1e4,           # vs arrival (buy: + = worse), spread+impact incl
                             "fill_rate": fr,
                             "vs_vwap_bps": (avg / vwap - 1) * 1e4})

R = pd.DataFrame(rows)
print(f"=== Execution backtest: {R['ticker'].nunique()} names, {len(R)//9} order-days, BUY side ===")
print(f"(IS = avg fill vs arrival price, bps. Lower = better. PASSIVE/LADDER capture spread on top; TWAP pays it.)\n")
print("--- mean implementation shortfall (bps vs arrival; spread+impact included; lower=better) by order-size ---")
print(R.groupby(["pct_adv", "algo"])["is_bps"].mean().unstack().round(1).to_string())
print("\n--- passive/ladder FILL RATE (before forced ATC) — the non-fill risk ---")
print(R[R.algo != "TWAP"].groupby(["pct_adv", "algo"])["fill_rate"].mean().unstack().round(3).to_string())
print("\n--- IS variability (std bps) — execution RISK, lower=more predictable ---")
print(R.groupby(["pct_adv", "algo"])["is_bps"].std().unstack().round(1).to_string())
print("\nNOTES: PASSIVE/LADDER credited 6bps half-spread on fills; TWAP pays sqrt-impact (~8bps@5%ADV).")
print("All 16 names are liquid VN (tier split disabled — turnover scale). BUY side; sells symmetric.")
