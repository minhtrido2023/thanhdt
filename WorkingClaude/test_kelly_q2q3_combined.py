# -*- coding: utf-8 -*-
"""Kelly Q2 + Q3 combined verification.

Tests additivity of two GREEN changes:
  - Q2 HEUR_N100  : cash_etf_states[3] = 1.0 (was 0.7) -- NEUTRAL ETF deployment 70%->100%
  - Q3 BOOST_ONLY : MOMENTUM_S/N -> 14%, rest 10%
  - Q3 SHARPE_PROP: MOMENTUM_S/N -> 13%, DVR/RE -> 7%, rest 10%

4 arms:
  - BASELINE     : ETF heuristic {3:0.7} + flat 10% tier
  - Q2_ONLY      : ETF HEUR_N100 {3:1.0} + flat 10% tier
  - COMBO_BOOST  : ETF HEUR_N100 + BOOST_ONLY tier
  - COMBO_SHARPE : ETF HEUR_N100 + SHARPE_PROP tier

Compare combined gains to sum of individual gains to detect interaction effects.
"""
import os, sys, io, pickle
from datetime import datetime
import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
OUTDIR  = os.path.join(WORKDIR, "kelly_combo_out")
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

W_FLAT = {t: FLAT for t in TIER_BAL}
W_BOOST = {"MOMENTUM_S": 0.14, "MOMENTUM_N": 0.14,
           "MOMENTUM": 0.10, "DEEP_VALUE_RECOVERY": 0.10,
           "RE_BACKLOG_BUY": 0.10, "MEGA": 0.10}
W_SHARPE = {"MOMENTUM_S": 0.13, "MOMENTUM_N": 0.13,
            "MOMENTUM": 0.10, "DEEP_VALUE_RECOVERY": 0.07,
            "RE_BACKLOG_BUY": 0.07, "MEGA": 0.10}

ETF_HEUR = {1: 0.0, 2: 0.2, 3: 0.7, 4: 1.0, 5: 1.3}
ETF_N100 = {1: 0.0, 2: 0.2, 3: 1.0, 4: 1.0, 5: 1.3}

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

print("=" * 110)
print("  KELLY Q2+Q3 COMBINED VERIFICATION -- additivity check")
print(f"  Period: {START_DATE} -> {END_DATE} | init NAV {TOTAL_NAV/1e9:.0f}B")
print(f"  Cost: deposit=0.0, borrow=0.10 (new defaults)")
print("=" * 110)

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


def run_arm(arm_label, tier_w, etf_states):
    print(f"\n[RUN {arm_label}]  etf={etf_states} | tier sample MOMENTUM_S={tier_w.get('MOMENTUM_S')}")
    events_bal, etf_bal = [], []
    nav_b, _ = simulate(sig_f, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=MAX_POS_V11, hold_days=45,
        stop_loss=-0.20, min_hold=2, slippage=0.0, init_nav=BOOK_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        sector_cap_exempt_tiers=SECTOR_CAP_EXEMPT,
        tier_weights=tier_w,
        deposit_annual=0.0, state_by_date=state_ff,
        cash_etf_states=etf_states, vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015,
        open_prices=open_prices, t1_open_exec=True,
        entry_alt_prices=alt_hybrid, entry_fill_mode="v4_hybrid",
        event_log=events_bal, etf_log=etf_bal,
        force_close_eod=False,
        **LIQ_FULL, name=f"Combo_{arm_label}_BAL")

    sig_vn30 = sig_f[sig_f["ticker"].isin(top30)].copy()
    prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
    liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
    LIQ_V30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
    events_v30, etf_v30 = [], []
    nav_v, _ = simulate(sig_vn30, prices_vn30, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=MAX_POS_V11, hold_days=45,
        stop_loss=-0.20, min_hold=2, slippage=0.0, init_nav=BOOK_NAV,
        ticker_sector_map=sec_map,
        tier_weights=tier_w,
        deposit_annual=0.0, state_by_date=state_ff,
        cash_etf_states=etf_states, vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015,
        open_prices=open_prices, t1_open_exec=True,
        entry_alt_prices=alt_hybrid, entry_fill_mode="v4_hybrid",
        event_log=events_v30, etf_log=etf_v30,
        force_close_eod=False,
        **LIQ_V30, name=f"Combo_{arm_label}_VN30")

    nav_b["time"] = pd.to_datetime(nav_b["time"])
    nav_v["time"] = pd.to_datetime(nav_v["time"])
    nb = nav_b.set_index("time"); nv = nav_v.set_index("time")
    common = nb.index.intersection(nv.index)
    combined = (nb.loc[common,"nav"] + nv.loc[common,"nav"]).rename("nav")

    logs = pd.DataFrame({"ymd": common, "nav": combined.values,
                         "state": pd.Series(common).map(state_ff).values})

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
nav_base,  tx_base  = run_arm("baseline",     W_FLAT,   ETF_HEUR)
print(f"   BASELINE      end NAV {nav_base.iloc[-1]/1e9:.2f}B  trades {len(tx_base):,}")
nav_q2,    tx_q2    = run_arm("q2_only",      W_FLAT,   ETF_N100)
print(f"   Q2_ONLY       end NAV {nav_q2.iloc[-1]/1e9:.2f}B  trades {len(tx_q2):,}")
nav_cb,    tx_cb    = run_arm("combo_boost",  W_BOOST,  ETF_N100)
print(f"   COMBO_BOOST   end NAV {nav_cb.iloc[-1]/1e9:.2f}B  trades {len(tx_cb):,}")
nav_cs,    tx_cs    = run_arm("combo_sharpe", W_SHARPE, ETF_N100)
print(f"   COMBO_SHARPE  end NAV {nav_cs.iloc[-1]/1e9:.2f}B  trades {len(tx_cs):,}")


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


print("\n[C] Computing windowed metrics + additivity check...")
arms = [("BASELINE", nav_base, tx_base), ("Q2_ONLY", nav_q2, tx_q2),
        ("COMBO_BOOST", nav_cb, tx_cb), ("COMBO_SHARPE", nav_cs, tx_cs)]
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


# Reference from Q3 v3 (Q3 alone, ETF heuristic):
# These are the "expected Q3-alone gains" from v3 results
Q3_BOOST_OOS_DCAGR_alone   = 21.01 - 18.29   # +2.73pp
Q3_SHARPE_OOS_DCAGR_alone  = 19.41 - 18.29   # +1.12pp

def verdict(combo_label, expected_q3_alone_dcagr):
    oos = next((r for r in rows if r["period"] == "OOS 2024-2026"), None)
    if not oos: return None
    if combo_label not in oos["arms"] or "BASELINE" not in oos["arms"] or "Q2_ONLY" not in oos["arms"]:
        return None
    B  = oos["arms"]["BASELINE"]
    Q2 = oos["arms"]["Q2_ONLY"]
    C  = oos["arms"][combo_label]
    q2_alone = Q2["cagr_pct"] - B["cagr_pct"]
    combo_total = C["cagr_pct"] - B["cagr_pct"]
    q3_alone = expected_q3_alone_dcagr  # from v3 reference
    expected_sum = q2_alone + q3_alone
    interaction = combo_total - expected_sum
    return {
        "q2_alone": q2_alone,
        "q3_alone_ref": q3_alone,
        "expected_sum": expected_sum,
        "combo_actual": combo_total,
        "interaction": interaction,
        "combo_cagr": C["cagr_pct"],
        "combo_sharpe": C["sharpe"],
        "combo_dd": C["max_dd_pct"],
        "combo_calmar": C["calmar"],
        "baseline_cagr": B["cagr_pct"],
    }

print("\n" + "="*110)
print("  KELLY Q2+Q3 COMBINED -- RESULTS")
print("="*110)
print(f"\n  {'Period':<22} {'Arm':<14} {'CAGR':>8} {'Sharpe':>7} {'MaxDD':>8} {'Calmar':>7} {'WealthX':>7} {'Trades':>7}")
print("-"*110)
for r in rows:
    p = r["period"]
    for arm_label in ["BASELINE","Q2_ONLY","COMBO_BOOST","COMBO_SHARPE"]:
        if arm_label not in r["arms"]: continue
        m = r["arms"][arm_label]
        first = (arm_label == "BASELINE")
        print(f"  {p if first else '':<22} {arm_label:<14} {m['cagr_pct']:>+7.2f}% "
              f"{m['sharpe']:>+7.2f} {m['max_dd_pct']:>+7.2f}% {m['calmar']:>+7.2f} "
              f"{m['wealth_x']:>+7.2f}x {m['n_trades']:>7d}")
    B = r["arms"].get("BASELINE")
    if B:
        for arm_label in ["Q2_ONLY","COMBO_BOOST","COMBO_SHARPE"]:
            if arm_label not in r["arms"]: continue
            A = r["arms"][arm_label]
            dC = A['cagr_pct']-B['cagr_pct']; dS = A['sharpe']-B['sharpe']
            dD = A['max_dd_pct']-B['max_dd_pct']
            print(f"  {'':<22} {'D '+arm_label[:10]+'-B':<14} {dC:>+7.2f}pp {dS:>+7.2f}  {dD:>+7.2f}pp")
    print()

print("\n" + "="*110)
print("  ADDITIVITY CHECK (OOS 2024-2026)")
print("="*110)
v_cb = verdict("COMBO_BOOST",  Q3_BOOST_OOS_DCAGR_alone)
v_cs = verdict("COMBO_SHARPE", Q3_SHARPE_OOS_DCAGR_alone)
for label, v in [("COMBO_BOOST", v_cb), ("COMBO_SHARPE", v_cs)]:
    if v is None: continue
    print(f"\n  {label}:")
    print(f"    Q2 alone (this run, dCAGR vs BASELINE): {v['q2_alone']:+.2f}pp")
    print(f"    Q3 alone (from v3 reference):           {v['q3_alone_ref']:+.2f}pp")
    print(f"    Expected sum (if perfectly additive):   {v['expected_sum']:+.2f}pp")
    print(f"    COMBO actual:                           {v['combo_actual']:+.2f}pp")
    print(f"    Interaction (actual - expected):        {v['interaction']:+.2f}pp")
    print(f"    Final COMBO CAGR={v['combo_cagr']:+.2f}% Sharpe={v['combo_sharpe']:+.2f} "
          f"DD={v['combo_dd']:+.2f}% Calmar={v['combo_calmar']:+.2f}")
    if v['interaction'] > 1.0:
        print(f"    >>> POSITIVE interaction (>+1pp) -- combo wins more than sum")
    elif v['interaction'] < -1.0:
        print(f"    >>> NEGATIVE interaction (<-1pp) -- combo cancels some gains")
    else:
        print(f"    >>> NEAR-ADDITIVE (interaction in [-1, +1]pp band)")

# Write markdown
md = []
md.append("# Kelly Q2+Q3 Combined Verification\n")
md.append(f"**Date**: {datetime.now().strftime('%Y-%m-%d')}")
md.append(f"**Stack**: BA v11 full | 50/50 BAL+VN30 | V6 ETF")
md.append(f"**Period**: {START_DATE} -> {END_DATE} | Init NAV: {TOTAL_NAV/1e9:.0f}B")
md.append(f"**Cost**: deposit=0%, borrow=10% (new defaults)\n")
md.append("## Arms\n")
md.append("- **BASELINE**     : ETF heuristic {3:0.7} + flat 10% tier  (current production)")
md.append("- **Q2_ONLY**      : ETF HEUR_N100 {3:1.0} + flat 10% tier")
md.append("- **COMBO_BOOST**  : ETF HEUR_N100 + BOOST_ONLY tier (MOMENTUM_S/N -> 14%)")
md.append("- **COMBO_SHARPE** : ETF HEUR_N100 + SHARPE_PROP tier (M_S/N -> 13%, DVR/RE -> 7%)\n")
md.append("## Additivity check (OOS 2024-2026)\n")
md.append("| Combo | Q2 alone | Q3 alone (v3 ref) | Expected sum | Actual | Interaction |")
md.append("|---|---:|---:|---:|---:|---:|")
for label, v in [("COMBO_BOOST", v_cb), ("COMBO_SHARPE", v_cs)]:
    if v is None: continue
    md.append(f"| {label} | {v['q2_alone']:+.2f}pp | {v['q3_alone_ref']:+.2f}pp | "
              f"{v['expected_sum']:+.2f}pp | **{v['combo_actual']:+.2f}pp** | "
              f"**{v['interaction']:+.2f}pp** |")
md.append("\n## Results -- all windows\n")
md.append("| Period | Arm | CAGR | Sharpe | MaxDD | Calmar | Wealth | Trades |")
md.append("|---|---|---:|---:|---:|---:|---:|---:|")
for r in rows:
    p = r["period"]
    for arm_label in ["BASELINE","Q2_ONLY","COMBO_BOOST","COMBO_SHARPE"]:
        if arm_label not in r["arms"]: continue
        m = r["arms"][arm_label]
        first = (arm_label == "BASELINE")
        md.append(f"| **{p if first else ''}** | {arm_label} | {m['cagr_pct']:+.2f}% | {m['sharpe']:+.2f} | "
                  f"{m['max_dd_pct']:+.2f}% | {m['calmar']:+.2f} | {m['wealth_x']:.2f}x | {m['n_trades']} |")
    B = r["arms"].get("BASELINE")
    if B:
        for arm_label in ["Q2_ONLY","COMBO_BOOST","COMBO_SHARPE"]:
            if arm_label not in r["arms"]: continue
            A = r["arms"][arm_label]
            dC = A['cagr_pct']-B['cagr_pct']; dS = A['sharpe']-B['sharpe']
            dD = A['max_dd_pct']-B['max_dd_pct']; dCal = A['calmar']-B['calmar']
            md.append(f"|        | **D {arm_label}-B** | **{dC:+.2f}pp** | **{dS:+.2f}** | "
                      f"**{dD:+.2f}pp** | **{dCal:+.2f}** | -- | -- |")
md.append("\n## Files\n")
md.append("- `kelly_combo_out/{baseline,q2_only,combo_boost,combo_sharpe}_*.csv`")

with open(os.path.join(WORKDIR, "kelly_q2q3_combined_results.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md))
print(f"\n  Wrote: kelly_q2q3_combined_results.md")
print("\nDONE.")
