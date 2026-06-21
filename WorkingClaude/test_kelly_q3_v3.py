# -*- coding: utf-8 -*-
"""Part D — Kelly Q3 v3: FLAT vs BOOST_ONLY vs SHARPE_PROP tier weights.

v2 used quarter-Kelly normalized to flat 10% which cut ALL non-small-n tiers to
floor 6% (cash drag -> -6.15pp OOS CAGR, RED). v3 tries two alternative shaping
strategies that don't reduce capital deployed:

  - BOOST_ONLY: only raise MOMENTUM_S, MOMENTUM_N to 14% (high-Sharpe tiers),
    keep all others at 10%. Net effect: more capital to high-edge tiers when
    they fire, no cash drag on the rest.
  - SHARPE_PROP: w_i = 0.10 x Sharpe_i / mean(Sharpe_eligible), clip [7%, 13%].
    Tighter band, anchored to mean-Sharpe rather than mean-Kelly_c. Lets DVR/RE
    drift slightly down to floor 7% but boosts MOMENTUM_S/N up to 13%.

Both arms keep small-n tiers (MOMENTUM n=14, MEGA n=2) at flat 10%.

Reuses cached signals + alt-fill from Q2/Q3 v2 (same signal stream).
"""
import os, sys, io, pickle
from datetime import datetime
import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
OUTDIR  = os.path.join(WORKDIR, "kelly_q3_v3_out")
os.makedirs(OUTDIR, exist_ok=True)

from simulate_holistic_nav import simulate

# --- Canonical V11 config -----------------------------------------------------
START_DATE = "2014-01-02"
END_DATE   = "2026-04-03"
TOTAL_NAV  = 50e9
BOOK_NAV   = 25e9
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY",
            "RE_BACKLOG_BUY"]
SECTOR_CAP_EXEMPT = {"RE_BACKLOG_BUY"}
MAX_POS_V11 = 12
FLAT = 0.10
LOW_N = 30

SIG_PKL = os.path.join(WORKDIR, "kelly_q3_out", "_signals_v11_12y.pkl")
ALT_PKL = os.path.join(WORKDIR, "kelly_q3_out", "_alt_hybrid.pkl")
TIER_STATS_CSV = os.path.join(WORKDIR, "kelly_q3_tier_stats.csv")

PERIODS = [
    ("FULL 2014-2026",  "2014-01-02", "2026-04-03"),
    ("Pre-OOS 2014-19", "2014-01-02", "2019-12-31"),
    ("OOS 2024-2026",   "2024-01-01", "2026-04-03"),
    ("Y2022",           "2022-01-01", "2022-12-31"),
    ("Y2024",           "2024-01-01", "2024-12-31"),
    ("Y2025",           "2025-01-01", "2025-12-31"),
]

# BOOST_ONLY weights
BOOST_ONLY = {
    "MOMENTUM_S": 0.14, "MOMENTUM_N": 0.14,
    "MOMENTUM": 0.10, "DEEP_VALUE_RECOVERY": 0.10,
    "RE_BACKLOG_BUY": 0.10, "MEGA": 0.10,
}

print("=" * 100)
print("  KELLY Q3 v3 — FLAT vs BOOST_ONLY vs SHARPE_PROP")
print(f"  Period: {START_DATE} -> {END_DATE} | init NAV {TOTAL_NAV/1e9:.0f}B")
print(f"  Cost: deposit=0.0, borrow=0.10 (new defaults)")
print("=" * 100)

# --- Stage A: load per-tier stats --------------------------------------------
print("\n[A] Loading per-tier stats...")
stats = pd.read_csv(TIER_STATS_CSV)
print(stats.to_string(index=False, float_format=lambda x: f"{x:.3f}"))

# --- Stage B: build SHARPE_PROP weights --------------------------------------
print("\n[B] Computing SHARPE_PROP weights...")
SP_LO, SP_HI = 0.07, 0.13
fit = stats[stats["n"] >= LOW_N].copy()
mean_sh = fit["sharpe_per_trade"].mean()
fit["raw_w"] = FLAT * fit["sharpe_per_trade"] / mean_sh
fit["proposed_weight"] = fit["raw_w"].clip(lower=SP_LO, upper=SP_HI)

SHARPE_PROP = {t: FLAT for t in TIER_BAL}
for _, r in fit.iterrows():
    if r["play_type"] in TIER_BAL:
        SHARPE_PROP[r["play_type"]] = float(r["proposed_weight"])

# Display table
rows_disp = []
for _, r in stats.iterrows():
    pt = r["play_type"]
    rows_disp.append({
        "tier": pt, "n": int(r["n"]),
        "sharpe_per_trade": r["sharpe_per_trade"],
        "kelly_c": r["kelly_continuous"],
        "FLAT": FLAT,
        "BOOST_ONLY": BOOST_ONLY.get(pt, FLAT),
        "SHARPE_PROP": SHARPE_PROP.get(pt, FLAT),
        "note": f"small_n_keep_flat (n<{LOW_N})" if r["n"] < LOW_N else "",
    })
disp = pd.DataFrame(rows_disp).sort_values("sharpe_per_trade", ascending=False).reset_index(drop=True)
disp.to_csv(os.path.join(WORKDIR, "kelly_q3_v3_tier_weights.csv"), index=False)
print("\nWeights table:")
print(disp.to_string(index=False, float_format=lambda x: f"{x:.3f}"))

# --- Stage C: load signals ---------------------------------------------------
print("\n[C] Loading cached signals + alt-fill...")
with open(SIG_PKL, "rb") as f:
    ctx = pickle.load(f)
with open(ALT_PKL, "rb") as f:
    alt_hybrid = pickle.load(f)
sig_f = ctx["sig_f"]; prices = ctx["prices"]; liq_map = ctx["liq_map"]
vni_dates = ctx["vni_dates"]; open_prices = ctx["open_prices"]
vn30_underlying = ctx["vn30_underlying"]; sec_map = ctx["sec_map"]
top30 = ctx["top30"]; state_ff = ctx["state_ff"]

LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
            "liquidity_lookup": liq_map, "exit_slippage_tiered": True}


def run_arm(arm_label, weights):
    print(f"\n[RUN {arm_label}]  weights={weights}")
    events_bal, etf_bal = [], []
    nav_b, _ = simulate(sig_f, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=MAX_POS_V11, hold_days=45,
        stop_loss=-0.20, min_hold=2, slippage=0.0, init_nav=BOOK_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        sector_cap_exempt_tiers=SECTOR_CAP_EXEMPT,
        tier_weights=weights,
        deposit_annual=0.0, state_by_date=state_ff,
        cash_etf_states={3: 0.7}, vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015,
        open_prices=open_prices, t1_open_exec=True,
        entry_alt_prices=alt_hybrid, entry_fill_mode="v4_hybrid",
        event_log=events_bal, etf_log=etf_bal,
        force_close_eod=False,
        **LIQ_FULL, name=f"Q3v3_{arm_label}_BAL")

    sig_vn30 = sig_f[sig_f["ticker"].isin(top30)].copy()
    prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
    liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
    LIQ_V30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
    events_v30, etf_v30 = [], []
    nav_v, _ = simulate(sig_vn30, prices_vn30, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=MAX_POS_V11, hold_days=45,
        stop_loss=-0.20, min_hold=2, slippage=0.0, init_nav=BOOK_NAV,
        ticker_sector_map=sec_map,
        tier_weights=weights,
        deposit_annual=0.0, state_by_date=state_ff,
        cash_etf_states={3: 0.7}, vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015,
        open_prices=open_prices, t1_open_exec=True,
        entry_alt_prices=alt_hybrid, entry_fill_mode="v4_hybrid",
        event_log=events_v30, etf_log=etf_v30,
        force_close_eod=False,
        **LIQ_V30, name=f"Q3v3_{arm_label}_VN30")

    nav_b["time"] = pd.to_datetime(nav_b["time"])
    nav_v["time"] = pd.to_datetime(nav_v["time"])
    nb = nav_b.set_index("time"); nv = nav_v.set_index("time")
    common = nb.index.intersection(nv.index)
    combined = (nb.loc[common,"nav"] + nv.loc[common,"nav"]).rename("nav")

    logs = pd.DataFrame({
        "ymd": common, "nav": combined.values,
        "BAL_cash":   nb.loc[common,"cash"].values,
        "BAL_stocks": (nb.loc[common,"positions_mv"] + nb.loc[common,"pending_mv"]).values,
        "BAL_etf":    nb.loc[common,"cash_etf"].values,
        "VN30_cash":   nv.loc[common,"cash"].values,
        "VN30_stocks": (nv.loc[common,"positions_mv"] + nv.loc[common,"pending_mv"]).values,
        "VN30_etf":    nv.loc[common,"cash_etf"].values,
        "n_pos":      (nb.loc[common,"n_pos"] + nv.loc[common,"n_pos"]).values,
        "state":      pd.Series(common).map(state_ff).values,
    })

    def annot(evs, book):
        if not evs: return pd.DataFrame()
        d = pd.DataFrame(evs); d["book"] = book; return d
    tx_stock = pd.concat([annot(events_bal,"BAL"), annot(events_v30,"VN30")],
                         ignore_index=True)
    if not tx_stock.empty:
        tx_stock["ymd"] = pd.to_datetime(tx_stock["ymd"])

    logs.to_csv(os.path.join(OUTDIR, f"{arm_label}_logs.csv"), index=False)
    tx_stock.to_csv(os.path.join(OUTDIR, f"{arm_label}_transactions.csv"), index=False)
    return combined, tx_stock


print("\n[D] Running 3 arms...")
weights_flat = {t: FLAT for t in TIER_BAL}
nav_flat,  tx_flat  = run_arm("flat",        weights_flat)
print(f"   FLAT        end NAV {nav_flat.iloc[-1]/1e9:.2f}B  trades {len(tx_flat):,}")
nav_boost, tx_boost = run_arm("boost_only",  BOOST_ONLY)
print(f"   BOOST_ONLY  end NAV {nav_boost.iloc[-1]/1e9:.2f}B  trades {len(tx_boost):,}")
nav_sp,    tx_sp    = run_arm("sharpe_prop", SHARPE_PROP)
print(f"   SHARPE_PROP end NAV {nav_sp.iloc[-1]/1e9:.2f}B  trades {len(tx_sp):,}")


def window_metrics(nav):
    rets = nav.pct_change().dropna()
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    spy = len(rets)/yrs if yrs > 0 else 252
    cagr = (nav.iloc[-1]/nav.iloc[0])**(1/yrs) - 1 if yrs > 0 else 0
    sh = rets.mean()/rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    peak = nav.cummax(); dd_s = (nav - peak)/peak
    dd = dd_s.min()
    cal = cagr/abs(dd) if dd < 0 else 0
    return {"cagr_pct": cagr*100, "sharpe": sh, "max_dd_pct": dd*100,
            "calmar": cal, "wealth_x": nav.iloc[-1]/nav.iloc[0]}

def count_trades(tx, ps, pe):
    if tx.empty: return 0
    real = tx[tx["reason"].astype(str) != "MTM_UNREALIZED"] if "reason" in tx.columns else tx
    real = real[(real["ymd"] >= pd.Timestamp(ps)) & (real["ymd"] <= pd.Timestamp(pe))]
    return len(real)


print("\n[E] Computing windowed metrics + verdict...")
rows = []
for label, ps, pe in PERIODS:
    ps_ts = pd.Timestamp(ps); pe_ts = pd.Timestamp(pe)
    sub_f = nav_flat[(nav_flat.index >= ps_ts) & (nav_flat.index <= pe_ts)]
    sub_b = nav_boost[(nav_boost.index >= ps_ts) & (nav_boost.index <= pe_ts)]
    sub_s = nav_sp[(nav_sp.index >= ps_ts) & (nav_sp.index <= pe_ts)]
    if min(len(sub_f), len(sub_b), len(sub_s)) < 30:
        continue
    mF = window_metrics(sub_f); mB = window_metrics(sub_b); mS = window_metrics(sub_s)
    mF["n_trades"] = count_trades(tx_flat,  ps, pe)
    mB["n_trades"] = count_trades(tx_boost, ps, pe)
    mS["n_trades"] = count_trades(tx_sp,    ps, pe)
    rows.append({"period": label, "F": mF, "B": mB, "S": mS})


def verdict_for(arm_label, arm_key):
    oos = next((r for r in rows if r["period"] == "OOS 2024-2026"), None)
    if not oos: return ("RED", "no OOS")
    A = oos[arm_key]; F = oos["F"]
    dC = A["cagr_pct"] - F["cagr_pct"]
    dS = A["sharpe"] - F["sharpe"]
    dD = A["max_dd_pct"] - F["max_dd_pct"]
    cond_cagr = dC >= 0.5
    cond_shar = dS >= 0.05
    cond_dd   = dD >= -1.5
    if cond_cagr and cond_shar and cond_dd:
        return ("GREEN", f"dCAGR={dC:+.2f}pp / dSharpe={dS:+.2f} / dMaxDD={dD:+.2f}pp")
    elif (cond_cagr or cond_shar) and cond_dd:
        return ("YELLOW", f"dCAGR={dC:+.2f}pp / dSharpe={dS:+.2f} / dMaxDD={dD:+.2f}pp")
    else:
        return ("RED", f"dCAGR={dC:+.2f}pp / dSharpe={dS:+.2f} / dMaxDD={dD:+.2f}pp")

v_boost = verdict_for("BOOST_ONLY",  "B")
v_sp    = verdict_for("SHARPE_PROP", "S")

print("\n" + "="*100)
print("  KELLY Q3 v3 — RESULTS")
print("="*100)
print(f"\n  {'Period':<22} {'Arm':<14} {'CAGR':>8} {'Sharpe':>7} {'MaxDD':>8} "
      f"{'Calmar':>7} {'WealthX':>7} {'Trades':>7}")
print("-"*100)
for r in rows:
    p = r["period"]
    for arm_key, arm_label in [("F","FLAT"), ("B","BOOST_ONLY"), ("S","SHARPE_PROP")]:
        m = r[arm_key]
        print(f"  {p if arm_key=='F' else '':<22} {arm_label:<14} {m['cagr_pct']:>+7.2f}% "
              f"{m['sharpe']:>+7.2f} {m['max_dd_pct']:>+7.2f}% {m['calmar']:>+7.2f} "
              f"{m['wealth_x']:>+7.2f}x {m['n_trades']:>7d}")
    F = r["F"]
    for arm_key, lbl in [("B","B-F"), ("S","S-F")]:
        A = r[arm_key]
        dC = A['cagr_pct']-F['cagr_pct']; dS = A['sharpe']-F['sharpe']
        dD = A['max_dd_pct']-F['max_dd_pct']
        print(f"  {'':<22} {'D '+lbl:<14} {dC:>+7.2f}pp {dS:>+7.2f}  {dD:>+7.2f}pp")
    print()

print(f"  BOOST_ONLY  verdict: {v_boost[0]} -- {v_boost[1]}")
print(f"  SHARPE_PROP verdict: {v_sp[0]} -- {v_sp[1]}")

# --- Write markdown ----------------------------------------------------------
md = []
md.append("# Kelly Q3 v3 -- FLAT vs BOOST_ONLY vs SHARPE_PROP\n")
md.append(f"**Date**: {datetime.now().strftime('%Y-%m-%d')}")
md.append(f"**Stack**: BA v11 full | 50/50 BAL+VN30 | V6 ETF (NEUTRAL 70%)")
md.append(f"**Period**: {START_DATE} -> {END_DATE} | Init NAV: {TOTAL_NAV/1e9:.0f}B")
md.append(f"**Cost (NEW)**: deposit_annual=0% (default), borrow_annual=10% (default)\n")

md.append("## Weights compared\n")
md.append("| tier | n | Sharpe/tr | Kelly_c | FLAT | BOOST_ONLY | SHARPE_PROP | note |")
md.append("|---|---:|---:|---:|---:|---:|---:|---|")
for _, r in disp.iterrows():
    md.append(f"| {r['tier']} | {r['n']} | {r['sharpe_per_trade']:.3f} | "
              f"{r['kelly_c']:.3f} | {r['FLAT']*100:.1f}% | "
              f"{r['BOOST_ONLY']*100:.1f}% | {r['SHARPE_PROP']*100:.1f}% | {r['note']} |")

md.append("\n## Results -- all windows\n")
md.append("| Period | Arm | CAGR | Sharpe | MaxDD | Calmar | Wealth | Trades |")
md.append("|---|---|---:|---:|---:|---:|---:|---:|")
for r in rows:
    p = r["period"]
    for arm_key, arm_label in [("F","FLAT"), ("B","BOOST_ONLY"), ("S","SHARPE_PROP")]:
        m = r[arm_key]
        md.append(f"| **{p}** | {arm_label} | {m['cagr_pct']:+.2f}% | {m['sharpe']:+.2f} | "
                  f"{m['max_dd_pct']:+.2f}% | {m['calmar']:+.2f} | {m['wealth_x']:.2f}x | "
                  f"{m['n_trades']} |")
    F = r["F"]
    for arm_key, lbl in [("B","B-F"), ("S","S-F")]:
        A = r[arm_key]
        dC = A['cagr_pct']-F['cagr_pct']; dS = A['sharpe']-F['sharpe']
        dD = A['max_dd_pct']-F['max_dd_pct']; dCal = A['calmar']-F['calmar']
        md.append(f"|        | **{lbl}** | **{dC:+.2f}pp** | **{dS:+.2f}** | "
                  f"**{dD:+.2f}pp** | **{dCal:+.2f}** | -- | -- |")

md.append("\n## Verdict\n")
md.append(f"### BOOST_ONLY: **{v_boost[0]}** -- {v_boost[1]}")
md.append(f"### SHARPE_PROP: **{v_sp[0]}** -- {v_sp[1]}\n")
md.append("Gate: OOS 2024-2026 dCAGR >= +0.5pp AND dSharpe >= +0.05 AND dMaxDD >= -1.5pp.\n")
md.append("## Files\n")
md.append("- `kelly_q3_v3_tier_weights.csv` -- weights table")
md.append("- `kelly_q3_v3_out/{flat,boost_only,sharpe_prop}_*.csv` -- per-arm logs/transactions\n")
md.append("## Design vs v2\n")
md.append("- v2 PROPOSED cut all tiers to floor 6% -> cash drag -> RED")
md.append("- v3 BOOST_ONLY: only raise high-Sharpe tiers, no cuts -> tests if extra capital to high-edge tiers wins")
md.append("- v3 SHARPE_PROP: w_i = 0.10 x Sharpe_i/mean(Sharpe), clip [7%, 13%] -> tighter band, anchored to Sharpe (not Kelly_c)")

with open(os.path.join(WORKDIR, "kelly_q3_v3_results.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md))
print(f"\n  Wrote: kelly_q3_v3_results.md")
print("\nDONE.")
