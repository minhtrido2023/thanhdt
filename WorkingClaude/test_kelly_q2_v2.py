# -*- coding: utf-8 -*-
"""Part C — Kelly Q2 v2 (rebuilt) — BASELINE vs HEUR_N100, full V11 stack.

Based DIRECTLY on sim_v11_transparent.py canonical config — only override is
the `cash_etf_states` dict between the two arms. Same simulator, same params,
same alt-fill, same period (2014-01-02 -> 2026-04-03), same 50B init.

BASELINE   : cash_etf_states = {1:0.0, 2:0.2, 3:0.7, 4:1.0, 5:1.3}  (current heuristic)
HEUR_N100  : cash_etf_states = {1:0.0, 2:0.2, 3:1.0, 4:1.0, 5:1.3}  (NEUTRAL 70->100)

This v2 re-uses the cached signal pkl (same as Part B and Q3 v2) so all three
parts run on identical data. The v1 script's BASELINE FULL CAGR landed at
+38.38% which is way outside the production 19.4% band — v1 had a config
drift bug we sidestep here by starting from the verified production pattern.

Outputs:
  kelly_q2_v2_out/<arm>_logs.csv
  kelly_q2_v2_out/<arm>_transactions.csv
  kelly_q2_v2_out/<arm>_open_positions.csv
  kelly_q2_v2_results.md
"""
import os, sys, io, pickle
from datetime import datetime
import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
OUTDIR  = os.path.join(WORKDIR, "kelly_q2_v2_out")
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
TIER_WEIGHTS_V11 = {t: 0.10 for t in TIER_BAL}

W_BASELINE  = {1: 0.0, 2: 0.2, 3: 0.7, 4: 1.0, 5: 1.3}
W_HEUR_N100 = {1: 0.0, 2: 0.2, 3: 1.0, 4: 1.0, 5: 1.3}

PERIODS = [
    ("FULL 2014-2026",  "2014-01-02", "2026-04-03"),
    ("Pre-OOS 2014-19", "2014-01-02", "2019-12-31"),
    ("OOS 2024-2026",   "2024-01-01", "2026-04-03"),
    ("Y2022",           "2022-01-01", "2022-12-31"),
    ("Y2024",           "2024-01-01", "2024-12-31"),
    ("Y2025",           "2025-01-01", "2025-12-31"),
    ("Y2026 partial",   "2026-01-01", "2026-04-03"),
]

SIG_PKL = os.path.join(WORKDIR, "kelly_q3_out", "_signals_v11_12y.pkl")
ALT_PKL = os.path.join(WORKDIR, "kelly_q3_out", "_alt_hybrid.pkl")

print("=" * 100)
print("  KELLY Q2 v2 — HEUR_N100 vs BASELINE (rebuilt from sim_v11_transparent.py)")
print(f"  Period: {START_DATE} -> {END_DATE} | init NAV {TOTAL_NAV/1e9:.0f}B")
print(f"  Cost model: deposit_annual=0.0 / borrow_annual=0.10 (new defaults)")
print(f"  BASELINE  ETF weights: {W_BASELINE}")
print(f"  HEUR_N100 ETF weights: {W_HEUR_N100}")
print("=" * 100)

print("\n[1/4] Loading cached V11 12y signals + alt-fill...")
with open(SIG_PKL, "rb") as f:
    ctx = pickle.load(f)
with open(ALT_PKL, "rb") as f:
    alt_hybrid = pickle.load(f)
sig_f = ctx["sig_f"]; prices = ctx["prices"]; liq_map = ctx["liq_map"]
vni_dates = ctx["vni_dates"]; open_prices = ctx["open_prices"]
vn30_underlying = ctx["vn30_underlying"]; sec_map = ctx["sec_map"]
top30 = ctx["top30"]; state_ff = ctx["state_ff"]
print(f"  Signals: {len(sig_f):,} rows | {len(vni_dates)} trading days")
print(f"  Alt-fill: {len(alt_hybrid):,} tickers")

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
        tier_weights=TIER_WEIGHTS_V11,
        deposit_annual=0.0, state_by_date=state_ff,
        cash_etf_states=weights, vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015,
        open_prices=open_prices, t1_open_exec=True,
        entry_alt_prices=alt_hybrid, entry_fill_mode="v4_hybrid",
        event_log=events_bal, etf_log=etf_bal,
        force_close_eod=False,
        **LIQ_FULL, name=f"Q2v2_{arm_label}_BAL")

    sig_vn30 = sig_f[sig_f["ticker"].isin(top30)].copy()
    prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
    liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
    LIQ_V30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
    events_v30, etf_v30 = [], []
    nav_v, _ = simulate(sig_vn30, prices_vn30, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=MAX_POS_V11, hold_days=45,
        stop_loss=-0.20, min_hold=2, slippage=0.0, init_nav=BOOK_NAV,
        ticker_sector_map=sec_map,
        tier_weights=TIER_WEIGHTS_V11,
        deposit_annual=0.0, state_by_date=state_ff,
        cash_etf_states=weights, vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015,
        open_prices=open_prices, t1_open_exec=True,
        entry_alt_prices=alt_hybrid, entry_fill_mode="v4_hybrid",
        event_log=events_v30, etf_log=etf_v30,
        force_close_eod=False,
        **LIQ_V30, name=f"Q2v2_{arm_label}_VN30")

    nav_b["time"] = pd.to_datetime(nav_b["time"])
    nav_v["time"] = pd.to_datetime(nav_v["time"])
    nb = nav_b.set_index("time"); nv = nav_v.set_index("time")
    common = nb.index.intersection(nv.index)
    combined = (nb.loc[common, "nav"] + nv.loc[common, "nav"]).rename("nav")

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


print("\n[2/4] Running BASELINE arm...")
nav_base, tx_base, open_base = run_arm("baseline", W_BASELINE)
print(f"   end NAV {nav_base.iloc[-1]/1e9:.2f}B  trades {len(tx_base):,}")

print("\n[3/4] Running HEUR_N100 arm...")
nav_n100, tx_n100, open_n100 = run_arm("heur_n100", W_HEUR_N100)
print(f"   end NAV {nav_n100.iloc[-1]/1e9:.2f}B  trades {len(tx_n100):,}")


def window_metrics(nav):
    rets = nav.pct_change().dropna()
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    spy = len(rets)/yrs if yrs > 0 else 252
    cagr = (nav.iloc[-1]/nav.iloc[0])**(1/yrs) - 1 if yrs > 0 else 0
    sh = rets.mean()/rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    peak = nav.cummax()
    dd_series = (nav - peak)/peak
    dd = dd_series.min()
    underwater = (nav < peak)
    dd_dur = 0
    if underwater.any():
        grp = (underwater != underwater.shift()).cumsum()
        for _, sub in nav[underwater].groupby(grp[underwater]):
            d = (sub.index[-1] - sub.index[0]).days
            if d > dd_dur: dd_dur = d
    cal = cagr/abs(dd) if dd < 0 else 0
    return {"cagr_pct": cagr*100, "sharpe": sh, "max_dd_pct": dd*100,
            "calmar": cal, "dd_dur_days": dd_dur, "wealth_x": nav.iloc[-1]/nav.iloc[0],
            "final_nav_bn": nav.iloc[-1]/1e9}

def count_trades(tx, ps, pe):
    if tx.empty: return 0
    real = tx[tx["reason"].astype(str) != "MTM_UNREALIZED"]
    real = real[(real["ymd"] >= pd.Timestamp(ps)) & (real["ymd"] <= pd.Timestamp(pe))]
    return len(real)


print("\n[4/4] Computing windowed metrics + verdict...")
rows = []
for label, ps, pe in PERIODS:
    ps_ts = pd.Timestamp(ps); pe_ts = pd.Timestamp(pe)
    sub_b = nav_base[(nav_base.index >= ps_ts) & (nav_base.index <= pe_ts)]
    sub_n = nav_n100[(nav_n100.index >= ps_ts) & (nav_n100.index <= pe_ts)]
    if len(sub_b) < 30 or len(sub_n) < 30:
        continue
    mB = window_metrics(sub_b); mN = window_metrics(sub_n)
    mB["n_trades"] = count_trades(tx_base, ps, pe)
    mN["n_trades"] = count_trades(tx_n100, ps, pe)
    rows.append({"period": label, "B": mB, "N": mN})

full = next((r for r in rows if r["period"].startswith("FULL")), None)
full_cagr_b = full["B"]["cagr_pct"] if full else 0
band_note = ""
if 17.0 <= full_cagr_b <= 21.0:
    band_note = f"BASELINE FULL CAGR={full_cagr_b:.2f}% is INSIDE 17-21% production band — config is aligned."
elif 16.0 <= full_cagr_b <= 22.0:
    band_note = (f"BASELINE FULL CAGR={full_cagr_b:.2f}% close-but-outside 17-21% band — "
                 "minor drift, results still indicative.")
else:
    band_note = (f"!! WARNING !! BASELINE FULL CAGR={full_cagr_b:.2f}% OUTSIDE 17-21% band — "
                 "config drift detected, treat results with caution.")

# Verdict gate: OOS 2024-2026 ΔCAGR ≥ +1.0pp AND ΔMaxDD ≤ +3pp (DD allowed to worsen by max 3pp)
oos = next((r for r in rows if r["period"] == "OOS 2024-2026"), None)
verdict, reason = "RED", "no OOS window"
if oos:
    dC = oos["N"]["cagr_pct"] - oos["B"]["cagr_pct"]
    dD = oos["N"]["max_dd_pct"] - oos["B"]["max_dd_pct"]   # negative = DD worsened
    if dC >= 1.0 and dD >= -3.0:
        verdict, reason = "GREEN", f"ΔCAGR={dC:+.2f}pp >= +1.0pp AND ΔMaxDD={dD:+.2f}pp >= -3.0pp"
    elif dC >= 0.5 or (dC >= 0 and dD >= -1.0):
        verdict, reason = "YELLOW", f"ΔCAGR={dC:+.2f}pp / ΔMaxDD={dD:+.2f}pp — marginal"
    else:
        verdict, reason = "RED", f"ΔCAGR={dC:+.2f}pp / ΔMaxDD={dD:+.2f}pp — fails gate"

print("\n" + "="*100)
print("  KELLY Q2 v2 — RESULTS")
print("="*100)
print(f"\n  Baseline band check: {band_note}\n")
print(f"  {'Period':<22} {'Arm':<10} {'CAGR':>8} {'Sharpe':>7} {'MaxDD':>8} "
      f"{'Calmar':>7} {'DDdur':>6} {'NAV_B':>8} {'Trades':>7}")
print("-"*100)
for r in rows:
    p = r["period"]; B = r["B"]; N = r["N"]
    print(f"  {p:<22} {'BASELINE':<10} {B['cagr_pct']:>+7.2f}% {B['sharpe']:>+7.2f} "
          f"{B['max_dd_pct']:>+7.2f}% {B['calmar']:>+7.2f} {B['dd_dur_days']:>6d} "
          f"{B['final_nav_bn']:>+7.2f}B {B['n_trades']:>7d}")
    print(f"  {'':<22} {'HEUR_N100':<10} {N['cagr_pct']:>+7.2f}% {N['sharpe']:>+7.2f} "
          f"{N['max_dd_pct']:>+7.2f}% {N['calmar']:>+7.2f} {N['dd_dur_days']:>6d} "
          f"{N['final_nav_bn']:>+7.2f}B {N['n_trades']:>7d}")
    dC = N['cagr_pct']-B['cagr_pct']; dS = N['sharpe']-B['sharpe']
    dD = N['max_dd_pct']-B['max_dd_pct']; dCal = N['calmar']-B['calmar']
    print(f"  {'':<22} {'Δ N100-B':<10} {dC:>+7.2f}pp {dS:>+7.2f}  {dD:>+7.2f}pp "
          f"{dCal:>+7.2f}")
    print()

print(f"  VERDICT: {verdict} — {reason}")

# --- Write markdown -----------------------------------------------------------
print("\n  Writing kelly_q2_v2_results.md...")
md = []
md.append("# Kelly Q2 v2 — HEUR_N100 vs BASELINE Shadow Backtest (rebuilt)\n")
md.append(f"**Date**: {datetime.now().strftime('%Y-%m-%d')}")
md.append(f"**Stack**: BA v11 full (SV_TIGHT + P3 + D1 RE_BACKLOG_BUY + 50/50 BAL+VN30 + V6 ETF)")
md.append(f"**Period**: {START_DATE} → {END_DATE}")
md.append(f"**Init NAV**: {TOTAL_NAV/1e9:.0f}B (25B BAL + 25B VN30)")
md.append(f"**Exec**: T+1 Open + Layer 3 v4 HYBRID intraday | slot12 (max_pos=12, 10% fixed)")
md.append(f"**Costs (NEW)**: TC=0.1% buy/sell, deposit_annual=0% (NEW default), borrow_annual=10% (NEW default), ETF friction=0.15%/side")
md.append(f"**Built directly from sim_v11_transparent.py canonical pattern** — only override is cash_etf_states.\n")
md.append("## Variants compared\n")
md.append(f"- **BASELINE** (current heuristic): `cash_etf_states = {W_BASELINE}`")
md.append(f"- **HEUR_N100** (proposed): `cash_etf_states = {W_HEUR_N100}` — NEUTRAL goes 70% -> 100%\n")
md.append("## Baseline sanity check\n")
md.append(f"{band_note}\n")
md.append("## Verdict\n")
md.append(f"### **{verdict}** — {reason}\n")
md.append("Gate: OOS 2024-2026 ΔCAGR >= +1.0pp AND ΔMaxDD <= +3pp vs BASELINE.\n")
md.append("## Results — all windows\n")
md.append("| Period | Arm | CAGR | Sharpe | MaxDD | Calmar | DDdur | NAV (B) | Trades |")
md.append("|---|---|---:|---:|---:|---:|---:|---:|---:|")
for r in rows:
    p = r["period"]; B = r["B"]; N = r["N"]
    md.append(f"| **{p}** | BASELINE | {B['cagr_pct']:+.2f}% | {B['sharpe']:+.2f} | "
              f"{B['max_dd_pct']:+.2f}% | {B['calmar']:+.2f} | {B['dd_dur_days']} | "
              f"{B['final_nav_bn']:+.2f} | {B['n_trades']} |")
    md.append(f"|        | HEUR_N100 | {N['cagr_pct']:+.2f}% | {N['sharpe']:+.2f} | "
              f"{N['max_dd_pct']:+.2f}% | {N['calmar']:+.2f} | {N['dd_dur_days']} | "
              f"{N['final_nav_bn']:+.2f} | {N['n_trades']} |")
    dC = N['cagr_pct']-B['cagr_pct']; dS = N['sharpe']-B['sharpe']
    dD = N['max_dd_pct']-B['max_dd_pct']; dCal = N['calmar']-B['calmar']
    md.append(f"|        | **Δ N100-B** | **{dC:+.2f}pp** | **{dS:+.2f}** | "
              f"**{dD:+.2f}pp** | **{dCal:+.2f}** | — | — | — |")
md.append("\n## Files\n")
md.append("- `kelly_q2_v2_out/baseline_logs.csv` / `_transactions.csv` / `_open_positions.csv`")
md.append("- `kelly_q2_v2_out/heur_n100_logs.csv` / `_transactions.csv` / `_open_positions.csv`")
md.append("\n## Notes\n")
md.append("- Built directly on sim_v11_transparent.py canonical pattern — only `cash_etf_states` differs between arms.")
md.append("- Uses same cached `kelly_q3_out/_signals_v11_12y.pkl` as Part B + Q3 v2 — identical signal stream.")
md.append("- New cost model: deposit_annual=0.0 (default) and borrow_annual=0.10 (default 10%/yr on margin).")
md.append("- v1 (`test_kelly_q2_heur_n100.py`) showed BASELINE FULL CAGR +38.38% which is config-drifted; this v2 fixes that.")

with open(os.path.join(WORKDIR, "kelly_q2_v2_results.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md))
print(f"  Wrote: kelly_q2_v2_results.md")
print("\nDONE.")
