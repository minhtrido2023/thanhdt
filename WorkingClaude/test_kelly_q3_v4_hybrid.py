# -*- coding: utf-8 -*-
"""Kelly Q3 v4 — HYBRID state-conditional tier weights.

v3 found:
  - BOOST_ONLY  wins FULL CAGR + OOS CAGR + Y2025 BULL (+2.94pp)
  - SHARPE_PROP wins FULL Sharpe + OOS Calmar (1.30!) + Y2022 CRISIS (+2.14pp)

Hypothesis: combine both -- use BOOST_ONLY when state in {BULL=4, EX-BULL=5}
to capture upside, SHARPE_PROP when state in {CRISIS=1, BEAR=2, NEUTRAL=3}
for defense. New simulate() param `tier_weights_by_state` enables this.

Arms compared:
  - FLAT          : 10% all tiers (baseline)
  - BOOST_ONLY    : MOMENTUM_S/N -> 14%, rest 10% (v3 winner)
  - SHARPE_PROP   : MOMENTUM_S/N -> 13%, DVR/RE -> 7% (v3 risk-adjusted)
  - HYBRID        : BOOST_ONLY @ state 4-5, SHARPE_PROP @ state 1-3

Outputs:
  kelly_q3_v4_out/<arm>_logs.csv, <arm>_transactions.csv
  kelly_q3_v4_results.md
"""
import os, sys, io, pickle
from datetime import datetime
import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
OUTDIR  = os.path.join(WORKDIR, "kelly_q3_v4_out")
os.makedirs(OUTDIR, exist_ok=True)

from simulate_holistic_nav import simulate

START_DATE = "2014-01-02"
END_DATE   = "2026-04-03"
TOTAL_NAV  = 50e9
BOOK_NAV   = 25e9
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY",
            "RE_BACKLOG_BUY"]
SECTOR_CAP_EXEMPT = {"RE_BACKLOG_BUY"}
MAX_POS_V11 = 12
FLAT = 0.10

# Weight presets
W_FLAT = {t: FLAT for t in TIER_BAL}
W_BOOST = {
    "MOMENTUM_S": 0.14, "MOMENTUM_N": 0.14,
    "MOMENTUM": 0.10, "DEEP_VALUE_RECOVERY": 0.10,
    "RE_BACKLOG_BUY": 0.10, "MEGA": 0.10,
}
W_SHARPE = {
    "MOMENTUM_S": 0.13, "MOMENTUM_N": 0.13,
    "MOMENTUM": 0.10, "DEEP_VALUE_RECOVERY": 0.07,
    "RE_BACKLOG_BUY": 0.07, "MEGA": 0.10,
}
# HYBRID state-conditional map:
#   state 4 (BULL), 5 (EX-BULL): use BOOST_ONLY
#   state 1 (CRISIS), 2 (BEAR), 3 (NEUTRAL): use SHARPE_PROP
HYBRID_BY_STATE = {1: W_SHARPE, 2: W_SHARPE, 3: W_SHARPE, 4: W_BOOST, 5: W_BOOST}

SIG_PKL = os.path.join(WORKDIR, "kelly_q3_out", "_signals_v11_12y.pkl")
ALT_PKL = os.path.join(WORKDIR, "kelly_q3_out", "_alt_hybrid.pkl")

PERIODS = [
    ("FULL 2014-2026",  "2014-01-02", "2026-04-03"),
    ("Pre-OOS 2014-19", "2014-01-02", "2019-12-31"),
    ("OOS 2024-2026",   "2024-01-01", "2026-04-03"),
    ("Y2022",           "2022-01-01", "2022-12-31"),
    ("Y2024",           "2024-01-01", "2024-12-31"),
    ("Y2025",           "2025-01-01", "2025-12-31"),
]

print("=" * 100)
print("  KELLY Q3 v4 -- FLAT vs BOOST_ONLY vs SHARPE_PROP vs HYBRID (state-conditional)")
print(f"  Period: {START_DATE} -> {END_DATE} | init NAV {TOTAL_NAV/1e9:.0f}B")
print(f"  HYBRID: state 4,5 -> BOOST_ONLY ; state 1,2,3 -> SHARPE_PROP")
print("=" * 100)

print("\n[A] Loading cached signals + alt-fill...")
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


def run_arm(arm_label, weights=None, weights_by_state=None):
    print(f"\n[RUN {arm_label}]")
    if weights_by_state is not None:
        print(f"   state-conditional: {[(s, sum(w.values())/len(w)) for s,w in weights_by_state.items()]}")
    else:
        print(f"   static: {weights}")
    events_bal, etf_bal = [], []
    nav_b, _ = simulate(sig_f, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=MAX_POS_V11, hold_days=45,
        stop_loss=-0.20, min_hold=2, slippage=0.0, init_nav=BOOK_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        sector_cap_exempt_tiers=SECTOR_CAP_EXEMPT,
        tier_weights=weights, tier_weights_by_state=weights_by_state,
        deposit_annual=0.0, state_by_date=state_ff,
        cash_etf_states={3: 0.7}, vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015,
        open_prices=open_prices, t1_open_exec=True,
        entry_alt_prices=alt_hybrid, entry_fill_mode="v4_hybrid",
        event_log=events_bal, etf_log=etf_bal,
        force_close_eod=False,
        **LIQ_FULL, name=f"Q3v4_{arm_label}_BAL")

    sig_vn30 = sig_f[sig_f["ticker"].isin(top30)].copy()
    prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
    liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
    LIQ_V30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
    events_v30, etf_v30 = [], []
    nav_v, _ = simulate(sig_vn30, prices_vn30, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=MAX_POS_V11, hold_days=45,
        stop_loss=-0.20, min_hold=2, slippage=0.0, init_nav=BOOK_NAV,
        ticker_sector_map=sec_map,
        tier_weights=weights, tier_weights_by_state=weights_by_state,
        deposit_annual=0.0, state_by_date=state_ff,
        cash_etf_states={3: 0.7}, vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015,
        open_prices=open_prices, t1_open_exec=True,
        entry_alt_prices=alt_hybrid, entry_fill_mode="v4_hybrid",
        event_log=events_v30, etf_log=etf_v30,
        force_close_eod=False,
        **LIQ_V30, name=f"Q3v4_{arm_label}_VN30")

    nav_b["time"] = pd.to_datetime(nav_b["time"])
    nav_v["time"] = pd.to_datetime(nav_v["time"])
    nb = nav_b.set_index("time"); nv = nav_v.set_index("time")
    common = nb.index.intersection(nv.index)
    combined = (nb.loc[common,"nav"] + nv.loc[common,"nav"]).rename("nav")

    logs = pd.DataFrame({
        "ymd": common, "nav": combined.values,
        "state": pd.Series(common).map(state_ff).values,
    })

    def annot(evs, book):
        if not evs: return pd.DataFrame()
        d = pd.DataFrame(evs); d["book"] = book; return d
    tx = pd.concat([annot(events_bal,"BAL"), annot(events_v30,"VN30")], ignore_index=True)
    if not tx.empty:
        tx["ymd"] = pd.to_datetime(tx["ymd"])

    logs.to_csv(os.path.join(OUTDIR, f"{arm_label}_logs.csv"), index=False)
    tx.to_csv(os.path.join(OUTDIR, f"{arm_label}_transactions.csv"), index=False)
    return combined, tx


print("\n[B] Running 4 arms...")
nav_flat,   tx_flat   = run_arm("flat",        weights=W_FLAT)
print(f"   FLAT        end NAV {nav_flat.iloc[-1]/1e9:.2f}B  trades {len(tx_flat):,}")
nav_boost,  tx_boost  = run_arm("boost_only",  weights=W_BOOST)
print(f"   BOOST_ONLY  end NAV {nav_boost.iloc[-1]/1e9:.2f}B  trades {len(tx_boost):,}")
nav_sp,     tx_sp     = run_arm("sharpe_prop", weights=W_SHARPE)
print(f"   SHARPE_PROP end NAV {nav_sp.iloc[-1]/1e9:.2f}B  trades {len(tx_sp):,}")
nav_hy,     tx_hy     = run_arm("hybrid",      weights_by_state=HYBRID_BY_STATE)
print(f"   HYBRID      end NAV {nav_hy.iloc[-1]/1e9:.2f}B  trades {len(tx_hy):,}")


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


print("\n[C] Computing windowed metrics + verdict...")
arms = [("FLAT", nav_flat, tx_flat), ("BOOST_ONLY", nav_boost, tx_boost),
        ("SHARPE_PROP", nav_sp, tx_sp), ("HYBRID", nav_hy, tx_hy)]
rows = []
for label, ps, pe in PERIODS:
    ps_ts = pd.Timestamp(ps); pe_ts = pd.Timestamp(pe)
    row = {"period": label, "arms": {}}
    for arm_label, nav, tx in arms:
        sub = nav[(nav.index >= ps_ts) & (nav.index <= pe_ts)]
        if len(sub) < 30:
            continue
        m = window_metrics(sub)
        m["n_trades"] = count_trades(tx, ps, pe)
        row["arms"][arm_label] = m
    rows.append(row)


def verdict_for(arm_label):
    oos = next((r for r in rows if r["period"] == "OOS 2024-2026"), None)
    if not oos or arm_label not in oos["arms"] or "FLAT" not in oos["arms"]:
        return ("RED", "no OOS")
    A = oos["arms"][arm_label]; F = oos["arms"]["FLAT"]
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

v_boost = verdict_for("BOOST_ONLY")
v_sp    = verdict_for("SHARPE_PROP")
v_hy    = verdict_for("HYBRID")

print("\n" + "="*110)
print("  KELLY Q3 v4 -- RESULTS")
print("="*110)
hdr = f"\n  {'Period':<22} {'Arm':<14} {'CAGR':>8} {'Sharpe':>7} {'MaxDD':>8} {'Calmar':>7} {'WealthX':>7} {'Trades':>7}"
print(hdr); print("-"*110)
for r in rows:
    p = r["period"]
    for arm_label in ["FLAT","BOOST_ONLY","SHARPE_PROP","HYBRID"]:
        if arm_label not in r["arms"]: continue
        m = r["arms"][arm_label]
        first = (arm_label == "FLAT")
        print(f"  {p if first else '':<22} {arm_label:<14} {m['cagr_pct']:>+7.2f}% "
              f"{m['sharpe']:>+7.2f} {m['max_dd_pct']:>+7.2f}% {m['calmar']:>+7.2f} "
              f"{m['wealth_x']:>+7.2f}x {m['n_trades']:>7d}")
    F = r["arms"].get("FLAT")
    if F:
        for arm_label in ["BOOST_ONLY","SHARPE_PROP","HYBRID"]:
            if arm_label not in r["arms"]: continue
            A = r["arms"][arm_label]
            dC = A['cagr_pct']-F['cagr_pct']; dS = A['sharpe']-F['sharpe']
            dD = A['max_dd_pct']-F['max_dd_pct']
            print(f"  {'':<22} {'D '+arm_label[:8]+'-F':<14} {dC:>+7.2f}pp {dS:>+7.2f}  {dD:>+7.2f}pp")
    print()

print(f"  BOOST_ONLY  verdict: {v_boost[0]} -- {v_boost[1]}")
print(f"  SHARPE_PROP verdict: {v_sp[0]} -- {v_sp[1]}")
print(f"  HYBRID      verdict: {v_hy[0]} -- {v_hy[1]}")

# --- markdown ---
md = []
md.append("# Kelly Q3 v4 -- HYBRID state-conditional vs static arms\n")
md.append(f"**Date**: {datetime.now().strftime('%Y-%m-%d')}")
md.append(f"**Stack**: BA v11 full | 50/50 BAL+VN30 | V6 ETF (NEUTRAL 70%)")
md.append(f"**Period**: {START_DATE} -> {END_DATE} | Init NAV: {TOTAL_NAV/1e9:.0f}B")
md.append(f"**Cost**: deposit_annual=0%, borrow_annual=10% (new defaults)\n")
md.append("## HYBRID design\n")
md.append("- State **4 (BULL)** + **5 (EX-BULL)**: use BOOST_ONLY weights (MOMENTUM_S/N = 14%, rest = 10%)")
md.append("- State **1 (CRISIS)** + **2 (BEAR)** + **3 (NEUTRAL)**: use SHARPE_PROP weights (MOMENTUM_S/N = 13%, DVR/RE = 7%, rest = 10%)")
md.append("\nRationale: capture upside in bull states via BOOST, reduce volatility in non-bull via SHARPE_PROP cuts.\n")
md.append("## Verdicts\n")
md.append(f"- BOOST_ONLY:  **{v_boost[0]}** -- {v_boost[1]}")
md.append(f"- SHARPE_PROP: **{v_sp[0]}** -- {v_sp[1]}")
md.append(f"- HYBRID:      **{v_hy[0]}** -- {v_hy[1]}\n")
md.append("Gate: OOS 2024-2026 dCAGR >= +0.5pp AND dSharpe >= +0.05 AND dMaxDD >= -1.5pp.\n")
md.append("## Results -- all windows\n")
md.append("| Period | Arm | CAGR | Sharpe | MaxDD | Calmar | Wealth | Trades |")
md.append("|---|---|---:|---:|---:|---:|---:|---:|")
for r in rows:
    p = r["period"]
    for arm_label in ["FLAT","BOOST_ONLY","SHARPE_PROP","HYBRID"]:
        if arm_label not in r["arms"]: continue
        m = r["arms"][arm_label]
        first = (arm_label == "FLAT")
        md.append(f"| **{p if first else ''}** | {arm_label} | {m['cagr_pct']:+.2f}% | {m['sharpe']:+.2f} | "
                  f"{m['max_dd_pct']:+.2f}% | {m['calmar']:+.2f} | {m['wealth_x']:.2f}x | {m['n_trades']} |")
    F = r["arms"].get("FLAT")
    if F:
        for arm_label in ["BOOST_ONLY","SHARPE_PROP","HYBRID"]:
            if arm_label not in r["arms"]: continue
            A = r["arms"][arm_label]
            dC = A['cagr_pct']-F['cagr_pct']; dS = A['sharpe']-F['sharpe']
            dD = A['max_dd_pct']-F['max_dd_pct']; dCal = A['calmar']-F['calmar']
            md.append(f"|        | **D {arm_label}-F** | **{dC:+.2f}pp** | **{dS:+.2f}** | "
                      f"**{dD:+.2f}pp** | **{dCal:+.2f}** | -- | -- |")
md.append("\n## Files\n")
md.append("- `kelly_q3_v4_out/{flat,boost_only,sharpe_prop,hybrid}_*.csv` -- per-arm logs/transactions")

with open(os.path.join(WORKDIR, "kelly_q3_v4_results.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md))
print(f"\n  Wrote: kelly_q3_v4_results.md")
print("\nDONE.")
