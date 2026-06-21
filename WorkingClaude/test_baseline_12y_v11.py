# -*- coding: utf-8 -*-
"""Part B baseline validation — run the EXACT sim_v11_transparent.py V11 stack
over the full 12y window 2014-01-02 -> 2026-04-03 with 50B init, to verify
the cost-model change (deposit_annual=0 default + borrow_annual=0.10 default)
has not drifted the production baseline outside the 17-21% CAGR band.

Re-uses the cached `kelly_q3_out/_signals_v11_12y.pkl` + `_alt_hybrid.pkl`
so this is fast and matches the EXACT same data the Kelly Q2/Q3 v2 runs use
(same signal stream, same intraday alt-fill).

Outputs only stdout. Pass/fail is reported in the last line.
"""
import os, sys, io, pickle
import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate

# --- canonical config (matches sim_v11_transparent.py) -------------------------
START_DATE = "2014-01-02"
END_DATE   = "2026-04-03"
TOTAL_NAV  = 50e9
BOOK_NAV   = 25e9
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY",
            "RE_BACKLOG_BUY"]
SECTOR_CAP_EXEMPT = {"RE_BACKLOG_BUY"}
MAX_POS_V11 = 12
TIER_WEIGHTS_V11 = {t: 0.10 for t in TIER_BAL}

SIG_PKL = os.path.join(WORKDIR, "kelly_q3_out", "_signals_v11_12y.pkl")
ALT_PKL = os.path.join(WORKDIR, "kelly_q3_out", "_alt_hybrid.pkl")

print("=" * 100)
print("  PART B — 12y V11 BASELINE VALIDATION (post cost-model update)")
print(f"  Period: {START_DATE} -> {END_DATE} | init NAV {TOTAL_NAV/1e9:.0f}B")
print(f"  Cost model: deposit_annual=0.0 (default), borrow_annual=0.10 (default)")
print("=" * 100)

assert os.path.exists(SIG_PKL), f"Missing cache {SIG_PKL}"
assert os.path.exists(ALT_PKL), f"Missing cache {ALT_PKL}"
print("\n[1/3] Loading cached V11 12y signals + alt-fill...")
with open(SIG_PKL, "rb") as f:
    ctx = pickle.load(f)
with open(ALT_PKL, "rb") as f:
    alt_hybrid = pickle.load(f)
print(f"  Signals: {len(ctx['sig_f']):,} rows, {len(ctx['vni_dates'])} trading days")
print(f"  Alt-fill: {len(alt_hybrid):,} tickers with intraday")

sig_f = ctx["sig_f"]; prices = ctx["prices"]; liq_map = ctx["liq_map"]
vni_dates = ctx["vni_dates"]; open_prices = ctx["open_prices"]
vn30_underlying = ctx["vn30_underlying"]; sec_map = ctx["sec_map"]
top30 = ctx["top30"]; state_ff = ctx["state_ff"]

LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
            "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

# --- Run BAL + VN30 books, EXACT params from sim_v11_transparent.py ----------
print("\n[2/3] Running BAL book (50% of NAV)...")
nav_b, _ = simulate(sig_f, prices, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=MAX_POS_V11, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.0, init_nav=BOOK_NAV,
    sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
    sector_cap_exempt_tiers=SECTOR_CAP_EXEMPT,
    tier_weights=TIER_WEIGHTS_V11,
    deposit_annual=0.0, state_by_date=state_ff,
    cash_etf_states={3: 0.7}, vn30_underlying=vn30_underlying,
    etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
    etf_rebalance_friction=0.0015,
    open_prices=open_prices, t1_open_exec=True,
    entry_alt_prices=alt_hybrid, entry_fill_mode="v4_hybrid",
    force_close_eod=False,
    **LIQ_FULL, name="BASELINE_BAL")

print("\n   Running VN30 book (50% of NAV, top30 universe)...")
sig_vn30 = sig_f[sig_f["ticker"].isin(top30)].copy()
prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
LIQ_V30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
nav_v, _ = simulate(sig_vn30, prices_vn30, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=MAX_POS_V11, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.0, init_nav=BOOK_NAV,
    ticker_sector_map=sec_map,
    tier_weights=TIER_WEIGHTS_V11,
    deposit_annual=0.0, state_by_date=state_ff,
    cash_etf_states={3: 0.7}, vn30_underlying=vn30_underlying,
    etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
    etf_rebalance_friction=0.0015,
    open_prices=open_prices, t1_open_exec=True,
    entry_alt_prices=alt_hybrid, entry_fill_mode="v4_hybrid",
    force_close_eod=False,
    **LIQ_V30, name="BASELINE_VN30")

# --- Combine and compute window metrics --------------------------------------
print("\n[3/3] Computing metrics...")
nav_b["time"] = pd.to_datetime(nav_b["time"])
nav_v["time"] = pd.to_datetime(nav_v["time"])
nb = nav_b.set_index("time")["nav"]
nv = nav_v.set_index("time")["nav"]
common = nb.index.intersection(nv.index)
combined = nb.loc[common] + nv.loc[common]

def window_metrics(nav):
    rets = nav.pct_change().dropna()
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    spy = len(rets)/yrs if yrs > 0 else 252
    cagr = (nav.iloc[-1]/nav.iloc[0])**(1/yrs) - 1 if yrs > 0 else 0
    sh = rets.mean()/rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    dd = ((nav - nav.cummax())/nav.cummax()).min()
    cal = cagr/abs(dd) if dd < 0 else 0
    return cagr*100, sh, dd*100, cal, nav.iloc[-1]/nav.iloc[0]

PERIODS = [
    ("FULL 2014-2026",  "2014-01-02", "2026-04-03"),
    ("Pre-OOS 2014-19", "2014-01-02", "2019-12-31"),
    ("Mid 2018-2023",   "2018-01-01", "2023-12-31"),
    ("OOS 2024-2026",   "2024-01-01", "2026-04-03"),
]
print("\n" + "="*100)
print("  12y V11 BASELINE — windowed metrics")
print("="*100)
print(f"  {'Period':<22} {'CAGR':>8} {'Sharpe':>7} {'MaxDD':>8} {'Calmar':>7} {'Wealth':>8}")
print(f"  {'-'*22} {'-'*8} {'-'*7} {'-'*8} {'-'*7} {'-'*8}")
full_cagr = None
for label, ps, pe in PERIODS:
    ps_ts = pd.Timestamp(ps); pe_ts = pd.Timestamp(pe)
    sub = combined[(combined.index >= ps_ts) & (combined.index <= pe_ts)]
    if len(sub) < 30:
        continue
    cagr, sh, dd, cal, wx = window_metrics(sub)
    if label.startswith("FULL"):
        full_cagr = cagr
        full_sh, full_dd = sh, dd
    print(f"  {label:<22} {cagr:>+7.2f}% {sh:>+7.2f} {dd:>+7.2f}% {cal:>+7.2f} {wx:>+7.2f}x")

# --- Validation gate ----------------------------------------------------------
print("\n" + "="*100)
print("  BASELINE VALIDATION GATE: FULL CAGR should be in 17-21% band")
print("="*100)
if full_cagr is None:
    print("  FAIL: could not compute FULL CAGR")
    sys.exit(1)
print(f"  Measured FULL CAGR: {full_cagr:.2f}%")
print(f"  Measured FULL Sharpe: {full_sh:.2f}  |  MaxDD: {full_dd:.2f}%")
if 17.0 <= full_cagr <= 21.0:
    print(f"  *** OK *** CAGR={full_cagr:.2f}% within 17-21% band — proceed to Parts C/D/E")
elif 16.0 <= full_cagr <= 22.0:
    print(f"  !! WARN !! CAGR={full_cagr:.2f}% close-but-outside 17-21% band — note in report and continue cautiously")
else:
    print(f"  !! DRIFT DETECTED !! CAGR={full_cagr:.2f}% outside 17-21% band (>1pp from 19.4% target)")
    print(f"     STOP and inspect cost-model changes (borrow_annual=0.10 may be over-charging).")
    sys.exit(2)
