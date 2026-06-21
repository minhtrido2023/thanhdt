# -*- coding: utf-8 -*-
"""Part D — Kelly Q3 v2: FLAT 10% vs PROPOSED tier weights (no rescale collapse).

The v1 script renormalized proposed weights back to flat 10% (the clip+rescale
loop neutralized everything). v2 uses a tighter clip band [6%, 14%] and DOES
NOT rescale at the end — let proposed weights diverge genuinely.

Per spec:
  - w_tier = 0.10 × (Kelly_c / mean(Kelly_c)) × 0.25  (quarter-Kelly relative to avg)
  - clip [0.06, 0.14]  (±40% band around 10%)
  - tiers with n < 30 → forced flat 10%
  - NO final rescale

Reuses `ba_trades_v11_tier_labels.csv` and `kelly_q3_tier_stats.csv` from v1
(537 trades, 6 tiers). Runs side-by-side FLAT vs PROPOSED on canonical 12y
config — same simulator call pattern as sim_v11_transparent.py (only tier_weights
differs).

Outputs:
  kelly_q3_v2_out/<arm>_logs.csv, <arm>_transactions.csv, <arm>_open_positions.csv
  kelly_q3_v2_tier_weights.csv
  kelly_q3_v2_results.md
"""
import os, sys, io, pickle
from datetime import datetime
import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
OUTDIR  = os.path.join(WORKDIR, "kelly_q3_v2_out")
os.makedirs(OUTDIR, exist_ok=True)

from simulate_holistic_nav import simulate

# --- Canonical V11 config (matches sim_v11_transparent.py) -------------------
START_DATE = "2014-01-02"
END_DATE   = "2026-04-03"
TOTAL_NAV  = 50e9
BOOK_NAV   = 25e9
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY",
            "RE_BACKLOG_BUY"]
SECTOR_CAP_EXEMPT = {"RE_BACKLOG_BUY"}
MAX_POS_V11 = 12
FLAT = 0.10

SIG_PKL = os.path.join(WORKDIR, "kelly_q3_out", "_signals_v11_12y.pkl")
ALT_PKL = os.path.join(WORKDIR, "kelly_q3_out", "_alt_hybrid.pkl")
TIER_STATS_CSV = os.path.join(WORKDIR, "data/kelly_q3_tier_stats.csv")
TRADES_CSV = os.path.join(WORKDIR, "data/ba_trades_v11_tier_labels.csv")

PERIODS = [
    ("FULL 2014-2026",  "2014-01-02", "2026-04-03"),
    ("Pre-OOS 2014-19", "2014-01-02", "2019-12-31"),
    ("OOS 2024-2026",   "2024-01-01", "2026-04-03"),
    ("Y2022",           "2022-01-01", "2022-12-31"),
    ("Y2024",           "2024-01-01", "2024-12-31"),
    ("Y2025",           "2025-01-01", "2025-12-31"),
]

LOW_N = 30
CLIP_LO, CLIP_HI = 0.06, 0.14

print("=" * 100)
print("  KELLY Q3 v2 — FLAT 10% vs PROPOSED tier weights (no rescale collapse)")
print(f"  Period: {START_DATE} -> {END_DATE} | init NAV {TOTAL_NAV/1e9:.0f}B")
print(f"  Cost model: deposit=0.0, borrow=0.10 (NEW defaults)")
print(f"  Norm: w = 0.10 × (Kelly_c/mean_Kelly_c) × 0.25, clip [{CLIP_LO}, {CLIP_HI}], no rescale")
print("=" * 100)

# --- Stage A: load or recompute per-tier stats -------------------------------
print("\n[A] Loading per-tier stats...")
if os.path.exists(TIER_STATS_CSV):
    stats = pd.read_csv(TIER_STATS_CSV)
    print(f"  Loaded {TIER_STATS_CSV} ({len(stats)} tiers)")
else:
    print(f"  {TIER_STATS_CSV} missing — recomputing from {TRADES_CSV}")
    tlog = pd.read_csv(TRADES_CSV)
    rows = []
    for tier, sub in tlog.groupby("play_type"):
        rets = sub["net_return_pct"] / 100.0
        mu, sd = rets.mean(), rets.std()
        sharpe = mu/sd if sd > 0 else 0
        kelly_c = mu/(sd*sd) if sd > 0 else 0
        wr = (rets > 0).mean()
        rows.append({"play_type": tier, "n": len(sub), "WR_pct": wr*100,
                     "avg_win_pct": rets[rets>0].mean()*100 if (rets>0).any() else 0,
                     "avg_loss_pct": -rets[rets<0].mean()*100 if (rets<0).any() else 0,
                     "mean_ret_pct": mu*100, "sd_ret_pct": sd*100,
                     "sharpe_per_trade": sharpe, "kelly_continuous": kelly_c})
    stats = pd.DataFrame(rows).sort_values("n", ascending=False).reset_index(drop=True)

print(stats.to_string(index=False, float_format=lambda x: f"{x:.3f}"))

# --- Stage B: compute proposed weights (no rescale) --------------------------
print("\n[B] Computing proposed weights (no rescale, clip [6%, 14%], n<30 -> flat 10%)...")
fit = stats[stats["n"] >= LOW_N].copy()
small_n = stats[stats["n"] < LOW_N]["play_type"].tolist()

if len(fit) > 0 and fit["kelly_continuous"].mean() > 0:
    mean_k = fit["kelly_continuous"].mean()
    fit["raw_w"] = FLAT * (fit["kelly_continuous"] / mean_k) * 0.25
    fit["proposed_weight"] = fit["raw_w"].clip(lower=CLIP_LO, upper=CLIP_HI)
else:
    fit["proposed_weight"] = FLAT

proposed = {t: FLAT for t in TIER_BAL}
for _, r in fit.iterrows():
    if r["play_type"] in TIER_BAL:
        proposed[r["play_type"]] = float(r["proposed_weight"])

# Build display table
disp_rows = []
for _, r in stats.iterrows():
    pt = r["play_type"]
    w = proposed.get(pt, FLAT) if pt in TIER_BAL else FLAT
    note = ""
    if r["n"] < LOW_N: note = f"small_n_keep_flat (n<{LOW_N})"
    if pt not in TIER_BAL: note = (note + ";" if note else "") + "not in TIER_BAL"
    disp_rows.append({"play_type": pt, "n_trades": int(r["n"]),
                      "mean_ret_pct": r["mean_ret_pct"],
                      "kelly_continuous": r["kelly_continuous"],
                      "current_weight": FLAT,
                      "proposed_weight": w,
                      "delta_pp": (w - FLAT) * 100,
                      "note": note})
disp = pd.DataFrame(disp_rows).sort_values("kelly_continuous", ascending=False).reset_index(drop=True)
disp.to_csv(os.path.join(WORKDIR, "data/kelly_q3_v2_tier_weights.csv"), index=False)
print(disp.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
print(f"\n  Verify divergence:")
for k, v in proposed.items():
    print(f"    {k:<25} {v*100:>5.2f}%   ({(v-FLAT)*100:+.2f}pp vs 10%)")
n_diverge = sum(1 for v in proposed.values() if abs(v - FLAT) > 1e-4)
print(f"  Tiers diverging from flat 10%: {n_diverge}/{len(proposed)}")
if n_diverge == 0:
    print("  !! WARNING !! All tiers collapsed to flat 10% — proposed identical to baseline.")

# --- Stage C: load signals + run both sims -----------------------------------
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
        **LIQ_FULL, name=f"Q3v2_{arm_label}_BAL")

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
        **LIQ_V30, name=f"Q3v2_{arm_label}_VN30")

    nav_b["time"] = pd.to_datetime(nav_b["time"])
    nav_v["time"] = pd.to_datetime(nav_v["time"])
    nb = nav_b.set_index("time"); nv = nav_v.set_index("time")
    common = nb.index.intersection(nv.index)
    combined = (nb.loc[common,"nav"] + nv.loc[common,"nav"]).rename("nav")

    logs = pd.DataFrame({
        "ymd": common,
        "nav": combined.values,
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
    etf_all = pd.concat([annot(etf_bal,"BAL"), annot(etf_v30,"VN30")],
                        ignore_index=True)
    if not etf_all.empty:
        etf_tx = pd.DataFrame({
            "ymd": pd.to_datetime(etf_all["ymd"]),
            "ticker": "E1VFVN30",
            "action": etf_all["action"].apply(lambda a: "buy" if a=="buy_etf" else "sell"),
            "buy_amount":  np.where(etf_all["action"]=="buy_etf",  etf_all["amount_vnd"], 0.0),
            "sell_amount": np.where(etf_all["action"]=="sell_etf", etf_all["amount_vnd"], 0.0),
            "fee": etf_all["friction_cost"], "adj_price": etf_all["price_vn30"],
            "shares": etf_all["shares"], "holding_id": etf_all["holding_id"],
            "play_type": "ETF_PARK", "cash_after": etf_all["cash_after"],
            "reason": "ETF_REBAL_state" + etf_all["state"].astype(str),
            "book": etf_all["book"],
        })
    else:
        etf_tx = pd.DataFrame()
    if not tx_stock.empty:
        tx_stock["ymd"] = pd.to_datetime(tx_stock["ymd"])
    all_tx = pd.concat([tx_stock, etf_tx], ignore_index=True)
    if not all_tx.empty:
        all_tx = all_tx.sort_values(["ymd","book","action","ticker"]).reset_index(drop=True)

    open_b = nav_b.attrs.get("open_positions_final") if hasattr(nav_b,"attrs") else None
    open_v = nav_v.attrs.get("open_positions_final") if hasattr(nav_v,"attrs") else None
    open_df = pd.concat([
        open_b.assign(book="BAL") if open_b is not None and not open_b.empty else pd.DataFrame(),
        open_v.assign(book="VN30") if open_v is not None and not open_v.empty else pd.DataFrame(),
    ], ignore_index=True)

    logs.to_csv(os.path.join(OUTDIR, f"{arm_label}_logs.csv"), index=False)
    all_tx.to_csv(os.path.join(OUTDIR, f"{arm_label}_transactions.csv"), index=False)
    open_df.to_csv(os.path.join(OUTDIR, f"{arm_label}_open_positions.csv"), index=False)
    return combined, all_tx, open_df


print("\n[D] Running FLAT arm...")
weights_flat = {t: FLAT for t in TIER_BAL}
nav_flat, tx_flat, _ = run_arm("flat", weights_flat)
print(f"   end NAV {nav_flat.iloc[-1]/1e9:.2f}B  trades {len(tx_flat):,}")

print("\n[E] Running PROPOSED arm...")
nav_prop, tx_prop, _ = run_arm("proposed", proposed)
print(f"   end NAV {nav_prop.iloc[-1]/1e9:.2f}B  trades {len(tx_prop):,}")


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
    real = tx[tx["reason"].astype(str) != "MTM_UNREALIZED"]
    real = real[(real["ymd"] >= pd.Timestamp(ps)) & (real["ymd"] <= pd.Timestamp(pe))]
    return len(real)


print("\n[F] Computing windowed metrics + verdict...")
rows = []
for label, ps, pe in PERIODS:
    ps_ts = pd.Timestamp(ps); pe_ts = pd.Timestamp(pe)
    sub_f = nav_flat[(nav_flat.index >= ps_ts) & (nav_flat.index <= pe_ts)]
    sub_p = nav_prop[(nav_prop.index >= ps_ts) & (nav_prop.index <= pe_ts)]
    if len(sub_f) < 30 or len(sub_p) < 30:
        continue
    mF = window_metrics(sub_f); mP = window_metrics(sub_p)
    mF["n_trades"] = count_trades(tx_flat, ps, pe)
    mP["n_trades"] = count_trades(tx_prop, ps, pe)
    rows.append({"period": label, "F": mF, "P": mP})

oos = next((r for r in rows if r["period"] == "OOS 2024-2026"), None)
verdict, reason = "RED", "no OOS window"
if oos:
    dC = oos["P"]["cagr_pct"] - oos["F"]["cagr_pct"]
    dS = oos["P"]["sharpe"] - oos["F"]["sharpe"]
    dD = oos["P"]["max_dd_pct"] - oos["F"]["max_dd_pct"]   # negative = DD worsened
    cond_cagr = dC >= 0.5
    cond_shar = dS >= 0.05
    cond_dd   = dD >= -1.5
    if cond_cagr and cond_shar and cond_dd:
        verdict, reason = "GREEN", (f"ΔCAGR={dC:+.2f}pp / ΔSharpe={dS:+.2f} / "
                                    f"ΔMaxDD={dD:+.2f}pp — all gates pass")
    elif (cond_cagr or cond_shar) and cond_dd:
        verdict, reason = "YELLOW", (f"ΔCAGR={dC:+.2f}pp / ΔSharpe={dS:+.2f} / "
                                     f"ΔMaxDD={dD:+.2f}pp — partial pass")
    else:
        verdict, reason = "RED", (f"ΔCAGR={dC:+.2f}pp / ΔSharpe={dS:+.2f} / "
                                  f"ΔMaxDD={dD:+.2f}pp — fails gate")

print("\n" + "="*100)
print("  KELLY Q3 v2 — RESULTS")
print("="*100)
print(f"\n  {'Period':<22} {'Arm':<10} {'CAGR':>8} {'Sharpe':>7} {'MaxDD':>8} "
      f"{'Calmar':>7} {'NAV_B':>8} {'Trades':>7}")
print("-"*100)
for r in rows:
    p = r["period"]; F = r["F"]; P = r["P"]
    print(f"  {p:<22} {'FLAT':<10} {F['cagr_pct']:>+7.2f}% {F['sharpe']:>+7.2f} "
          f"{F['max_dd_pct']:>+7.2f}% {F['calmar']:>+7.2f} "
          f"{F.get('wealth_x',0)*25:>+7.2f}B {F['n_trades']:>7d}")
    print(f"  {'':<22} {'PROPOSED':<10} {P['cagr_pct']:>+7.2f}% {P['sharpe']:>+7.2f} "
          f"{P['max_dd_pct']:>+7.2f}% {P['calmar']:>+7.2f} "
          f"{P.get('wealth_x',0)*25:>+7.2f}B {P['n_trades']:>7d}")
    dC = P['cagr_pct']-F['cagr_pct']; dS = P['sharpe']-F['sharpe']
    dD = P['max_dd_pct']-F['max_dd_pct']; dCal = P['calmar']-F['calmar']
    print(f"  {'':<22} {'Δ P-F':<10} {dC:>+7.2f}pp {dS:>+7.2f}  {dD:>+7.2f}pp "
          f"{dCal:>+7.2f}")
    print()

print(f"  VERDICT: {verdict} — {reason}")

# --- Write markdown -----------------------------------------------------------
print("\n  Writing kelly_q3_v2_results.md...")
md = []
md.append("# Kelly Q3 v2 — FLAT 10% vs PROPOSED tier weights (no rescale collapse)\n")
md.append(f"**Date**: {datetime.now().strftime('%Y-%m-%d')}")
md.append(f"**Stack**: BA v11 full | 50/50 BAL+VN30 | V6 ETF (NEUTRAL 70%)")
md.append(f"**Period**: {START_DATE} → {END_DATE}")
md.append(f"**Init NAV**: {TOTAL_NAV/1e9:.0f}B")
md.append(f"**Cost (NEW)**: deposit_annual=0% (default), borrow_annual=10% (default), TC=0.1%/side, ETF friction=0.15%/side\n")
md.append("## Normalization (fixed from v1)\n")
md.append(f"- `w = 0.10 × (Kelly_c / mean(Kelly_c)) × 0.25`  (quarter-Kelly, relative to mean)")
md.append(f"- Clip to **[{CLIP_LO}, {CLIP_HI}]**  (±40% band around 10%)")
md.append(f"- Tiers with `n < {LOW_N}` forced to flat 10%")
md.append(f"- **No final rescale** — let proposed weights diverge genuinely from flat 10%\n")
md.append("## Proposed weights\n")
md.append("| tier | n | mean_ret % | Kelly_c | current | proposed | Δpp | note |")
md.append("|---|---:|---:|---:|---:|---:|---:|---|")
for _, r in disp.iterrows():
    md.append(f"| {r['play_type']} | {r['n_trades']} | {r['mean_ret_pct']:+.2f} | "
              f"{r['kelly_continuous']:+.3f} | {r['current_weight']*100:.2f}% | "
              f"**{r['proposed_weight']*100:.2f}%** | {r['delta_pp']:+.2f} | {r['note']} |")
n_div = sum(1 for v in proposed.values() if abs(v - FLAT) > 1e-4)
md.append(f"\nTiers diverging from flat 10%: **{n_div}/{len(proposed)}**\n")
md.append("## Verdict\n")
md.append(f"### **{verdict}** — {reason}\n")
md.append("Gate: OOS 2024-2026 ΔCAGR ≥ +0.5pp AND ΔSharpe ≥ +0.05 AND ΔMaxDD ≥ -1.5pp.\n")
md.append("## Results — all windows\n")
md.append("| Period | Arm | CAGR | Sharpe | MaxDD | Calmar | Trades |")
md.append("|---|---|---:|---:|---:|---:|---:|")
for r in rows:
    p = r["period"]; F = r["F"]; P = r["P"]
    md.append(f"| **{p}** | FLAT | {F['cagr_pct']:+.2f}% | {F['sharpe']:+.2f} | "
              f"{F['max_dd_pct']:+.2f}% | {F['calmar']:+.2f} | {F['n_trades']} |")
    md.append(f"|        | PROPOSED | {P['cagr_pct']:+.2f}% | {P['sharpe']:+.2f} | "
              f"{P['max_dd_pct']:+.2f}% | {P['calmar']:+.2f} | {P['n_trades']} |")
    dC = P['cagr_pct']-F['cagr_pct']; dS = P['sharpe']-F['sharpe']
    dD = P['max_dd_pct']-F['max_dd_pct']; dCal = P['calmar']-F['calmar']
    md.append(f"|        | **Δ P-F** | **{dC:+.2f}pp** | **{dS:+.2f}** | "
              f"**{dD:+.2f}pp** | **{dCal:+.2f}** | — |")
md.append("\n## Files\n")
md.append("- `kelly_q3_v2_tier_weights.csv` — proposed weights table")
md.append("- `kelly_q3_v2_out/flat_*.csv` — FLAT 10% arm logs/transactions/open positions")
md.append("- `kelly_q3_v2_out/proposed_*.csv` — PROPOSED arm logs/transactions/open positions")
md.append("\n## Notes vs v1\n")
md.append("- v1 (`test_kelly_q3_tier_weights.py`) had a rescale loop that collapsed proposed weights")
md.append("  back to flat 10% — Δ was identically zero. v2 drops the rescale and uses a tighter [6%, 14%] clip.")
md.append("- Uses same cached signal pkl as Part B + Q2 v2 for identical signal stream.")
md.append("- Built directly on sim_v11_transparent.py canonical pattern — only `tier_weights` differs.")

with open(os.path.join(WORKDIR, "kelly_q3_v2_results.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md))
print(f"  Wrote: kelly_q3_v2_results.md")
print("\nDONE.")
